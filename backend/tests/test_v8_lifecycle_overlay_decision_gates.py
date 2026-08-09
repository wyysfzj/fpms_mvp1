from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.cases import lifecycle_overlay_service as overlay_service
from app.modules.cases.models import Case
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateReadResult,
    ResolveDecisionGateCommand,
)

AS_OF = datetime(2026, 8, 10, 12, 0, 0, 123456)
CASE_CODES = (
    DecisionGateCode.FEE_APPLICATION_DRAFT,
    DecisionGateCode.FEE_GRANT_YEAR_DRAFT,
    DecisionGateCode.FEE_FUTURE_ANNUITY,
    DecisionGateCode.GRANT_EVIDENCE_SOURCE,
    DecisionGateCode.GRANT_MANUAL_REVIEW,
    DecisionGateCode.PAYMENT_WORKBOOK,
    DecisionGateCode.SERVICE_RATE_VERSION,
)
UNRESOLVED_CODES = (
    "DECISION_GATE_NOT_FOUND",
    "DECISION_GATE_REVOKED",
    "DECISION_GATE_NOT_EFFECTIVE",
    "DECISION_GATE_CANDIDATE_MULTIPLICITY",
    "DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
    "DECISION_GATE_CURRENT_ROW_CORRUPT",
    "DECISION_GATE_LEGACY_MAP_CORRUPT",
)


def _case(transaction: Session) -> Case:
    case = Case(
        id=str(uuid4()),
        case_no=f"OVERLAY-GATE-{uuid4().hex}",
        status="NOT_FILED",
    )
    transaction.add(case)
    transaction.commit()
    return case


def _expected_commands(case_id: str) -> tuple[tuple[DecisionGateCode, str], ...]:
    return tuple((code, f"case:{case_id}") for code in CASE_CODES) + tuple(
        (DecisionGateCode.LEGACY_FORM_CLASS, f"form-{number:03d}") for number in range(1, 23)
    )


def _result(
    command: ResolveDecisionGateCommand,
    *,
    resolved_scope_key: str | None = None,
    decision_value: str | None = None,
) -> DecisionGateReadResult:
    return DecisionGateReadResult(
        gate_id=f"gate:{command.gate_code.value}:{command.scope_key}",
        gate_code=command.gate_code,
        requested_scope_key=command.scope_key,
        resolved_scope_key=resolved_scope_key or command.scope_key,
        decision_value=decision_value or "CURRENT_OFFICIAL",
        source_reference="customer-answer:2026-07-14",
        source_version="v2",
        confirmed_by="customer-actor",
        effective_at=datetime(2026, 8, 1, 9, 0),
    )


def _read(case: Case, transaction: Session):
    return overlay_service.read_lifecycle_overlay(
        case_id=case.id,
        after_sequence=0,
        limit=25,
        as_of_revision=None,
        transaction=transaction,
    )


def _assert_read_only(transaction: Session) -> None:
    assert not transaction.new
    assert not transaction.dirty
    assert not transaction.deleted


def test_overlay_resolves_exact_order_with_one_clock_and_lossless_fallback(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        commands: list[ResolveDecisionGateCommand] = []

        def resolver(
            command: ResolveDecisionGateCommand, actual: Session
        ) -> DecisionGateReadResult:
            assert actual is transaction
            commands.append(command)
            if command.scope_key == "form-001":
                return _result(
                    command,
                    resolved_scope_key="ALL-22",
                    decision_value="HISTORICAL",
                )
            if command.scope_key == "form-002":
                return _result(command, decision_value="INTERNAL_ONLY")
            return _result(command)

        monkeypatch.setattr(overlay_service, "_utc_now", lambda: AS_OF)
        monkeypatch.setattr(overlay_service, "resolve_decision_gate", resolver, raising=False)

        result = _read(case, transaction)

        expected = _expected_commands(case.id)
        assert result.generated_at is AS_OF
        assert [
            (item.gate_code, item.requested_scope_key) for item in result.decision_gates
        ] == list(expected)
        assert [(item.gate_code, item.scope_key) for item in commands] == list(expected)
        assert len(commands) == len(expected) == 29
        assert all(command.as_of is AS_OF for command in commands)
        assert all(command.scope_key != "ALL-22" for command in commands)
        assert all(item.resolution_status.value == "RESOLVED" for item in result.decision_gates)
        direct = result.decision_gates[0]
        assert (
            direct.gate_id,
            direct.gate_code,
            direct.requested_scope_key,
            direct.resolved_scope_key,
            direct.decision_value,
            direct.source_reference,
            direct.source_version,
            direct.confirmed_by,
            direct.effective_at,
            direct.unresolved_reason,
        ) == (
            f"gate:{CASE_CODES[0].value}:case:{case.id}",
            CASE_CODES[0],
            f"case:{case.id}",
            f"case:{case.id}",
            "CURRENT_OFFICIAL",
            "customer-answer:2026-07-14",
            "v2",
            "customer-actor",
            datetime(2026, 8, 1, 9, 0),
            None,
        )
        fallback = result.decision_gates[7]
        assert fallback.requested_scope_key == "form-001"
        assert fallback.resolved_scope_key == "ALL-22"
        assert fallback.decision_value == "HISTORICAL"
        assert fallback.source_reference == "customer-answer:2026-07-14"
        assert fallback.unresolved_reason is None
        assert result.decision_gates[8].decision_value == "INTERNAL_ONLY"
        _assert_read_only(transaction)


@pytest.mark.parametrize("error_code", UNRESOLVED_CODES)
@pytest.mark.parametrize("failure_index", (0, 14, 28))
def test_overlay_maps_each_known_409_at_every_position_and_completes_all_calls(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: sessionmaker,
    error_code: str,
    failure_index: int,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        commands: list[ResolveDecisionGateCommand] = []

        def resolver(
            command: ResolveDecisionGateCommand, actual: Session
        ) -> DecisionGateReadResult:
            assert actual is transaction
            commands.append(command)
            if len(commands) - 1 == failure_index:
                raise BusinessError(error_code, "unresolved", status_code=409)
            return _result(command)

        monkeypatch.setattr(overlay_service, "_utc_now", lambda: AS_OF)
        monkeypatch.setattr(overlay_service, "resolve_decision_gate", resolver, raising=False)

        result = _read(case, transaction)

        assert len(commands) == len(result.decision_gates) == 29
        unresolved = result.decision_gates[failure_index]
        assert unresolved.resolution_status.value == "UNRESOLVED"
        assert unresolved.unresolved_reason == error_code
        assert (
            unresolved.gate_id,
            unresolved.resolved_scope_key,
            unresolved.decision_value,
            unresolved.source_reference,
            unresolved.source_version,
            unresolved.confirmed_by,
            unresolved.effective_at,
        ) == (None, None, None, None, None, None, None)
        assert all(
            entry.resolution_status.value == "RESOLVED"
            for index, entry in enumerate(result.decision_gates)
            if index != failure_index
        )
        _assert_read_only(transaction)


def test_overlay_keeps_multiple_unresolved_composite_identities_independent(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: sessionmaker,
) -> None:
    failures = {1: UNRESOLVED_CODES[0], 8: UNRESOLVED_CODES[-1]}
    with session_factory() as transaction:
        case = _case(transaction)
        commands: list[ResolveDecisionGateCommand] = []

        def resolver(
            command: ResolveDecisionGateCommand, actual: Session
        ) -> DecisionGateReadResult:
            assert actual is transaction
            commands.append(command)
            if error_code := failures.get(len(commands) - 1):
                raise BusinessError(error_code, "unresolved", status_code=409)
            return _result(command)

        monkeypatch.setattr(overlay_service, "_utc_now", lambda: AS_OF)
        monkeypatch.setattr(overlay_service, "resolve_decision_gate", resolver, raising=False)

        result = _read(case, transaction)

        assert len(commands) == len(result.decision_gates) == 29
        assert [result.decision_gates[index].unresolved_reason for index in failures] == list(
            failures.values()
        )
        assert result.decision_gates[8].requested_scope_key == "form-002"
        _assert_read_only(transaction)


def test_overlay_converts_only_decision_gate_invalid_to_contract_conflict_and_stops(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: sessionmaker,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        calls = 0

        def resolver(
            _command: ResolveDecisionGateCommand, actual: Session
        ) -> DecisionGateReadResult:
            nonlocal calls
            assert actual is transaction
            calls += 1
            raise BusinessError("DECISION_GATE_INVALID", "invalid", status_code=400)

        monkeypatch.setattr(overlay_service, "_utc_now", lambda: AS_OF)
        monkeypatch.setattr(overlay_service, "resolve_decision_gate", resolver, raising=False)

        with pytest.raises(BusinessError) as caught:
            _read(case, transaction)

        assert caught.value.code == "LIFECYCLE_OVERLAY_DECISION_GATE_CONTRACT_INVALID"
        assert caught.value.status_code == 409
        assert calls == 1
        _assert_read_only(transaction)


@pytest.mark.parametrize(
    "error",
    (
        BusinessError("DECISION_GATE_NOT_FOUND", "wrong status", status_code=400),
        BusinessError("UNEXPECTED_GATE_ERROR", "unexpected", status_code=409),
        RuntimeError("unexpected resolver failure"),
    ),
)
def test_overlay_propagates_other_resolver_errors_without_retry(
    monkeypatch: pytest.MonkeyPatch,
    session_factory: sessionmaker,
    error: Exception,
) -> None:
    with session_factory() as transaction:
        case = _case(transaction)
        calls = 0

        def resolver(
            _command: ResolveDecisionGateCommand, actual: Session
        ) -> DecisionGateReadResult:
            nonlocal calls
            assert actual is transaction
            calls += 1
            raise error

        monkeypatch.setattr(overlay_service, "_utc_now", lambda: AS_OF)
        monkeypatch.setattr(overlay_service, "resolve_decision_gate", resolver, raising=False)

        with pytest.raises(type(error)) as caught:
            _read(case, transaction)

        assert caught.value is error
        assert calls == 1
        _assert_read_only(transaction)
