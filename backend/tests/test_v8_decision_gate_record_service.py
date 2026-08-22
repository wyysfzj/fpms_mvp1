from __future__ import annotations

import importlib
import inspect
import json
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from types import ModuleType
from typing import get_type_hints
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.system.models import CustomerDecisionGate

MODULE = "app.modules.system.decision_gate_service"

GATE_VALUES = (
    "DG-FEE-APPLICATION-DRAFT",
    "DG-FEE-GRANT-YEAR-DRAFT",
    "DG-FEE-FUTURE-ANNUITY",
    "DG-GRANT-EVIDENCE-SOURCE",
    "DG-GRANT-MANUAL-REVIEW",
    "DG-PAYMENT-WORKBOOK",
    "DG-SERVICE-RATE-VERSION",
    "DG-LEGACY-FORM-CLASS",
)
STATUS_VALUES = ("CONFIRMED", "REVOKED")
DISPOSITION_VALUES = ("CREATED", "REUSED")

COMMAND_FIELDS = (
    "gate_code",
    "scope_key",
    "decision_value",
    "decision_status",
    "source_reference",
    "source_version",
    "confirmed_by",
    "effective_at",
    "idempotency_key",
    "expected_current_gate_id",
)
RESULT_FIELDS = (
    "gate_id",
    "gate_code",
    "scope_key",
    "decision_value",
    "decision_status",
    "source_reference",
    "source_version",
    "confirmed_by",
    "effective_at",
    "supersedes_gate_id",
    "decision_snapshot",
    "idempotency_key",
    "current_identity_key",
    "disposition",
)

EFFECTIVE_AT = datetime(2026, 7, 13, 9, 8, 7, 654321)


def _service_module() -> ModuleType | None:
    try:
        return importlib.import_module(MODULE)
    except ModuleNotFoundError as exc:
        if exc.name != MODULE:
            raise
        return None


@pytest.fixture
def service() -> ModuleType:
    module = _service_module()
    if module is None:
        pytest.skip("missing service is asserted by the public-contract RED")
    return module


@pytest.fixture
def db(session_factory: sessionmaker) -> Session:
    with session_factory() as transaction:
        yield transaction


def _actor_id(transaction: Session) -> str:
    return transaction.execute(select(T_User.id).where(T_User.username == "admin")).scalar_one()


def _command(service: ModuleType, actor_id: str, **changes):
    values = {
        "gate_code": service.DecisionGateCode.FEE_APPLICATION_DRAFT,
        "scope_key": "GLOBAL",
        "decision_value": "CUSTOMER_APPROVED",
        "decision_status": service.DecisionGateStatus.CONFIRMED,
        "source_reference": "customer-answer:2026-07-13",
        "source_version": "v1",
        "confirmed_by": actor_id,
        "effective_at": EFFECTIVE_AT,
        "idempotency_key": "decision-request-001",
        "expected_current_gate_id": None,
    }
    values.update(changes)
    return service.RecordDecisionGateCommand(**values)


def _canonical_snapshot(command) -> str:
    return json.dumps(
        {
            "confirmed_by": command.confirmed_by,
            "decision_status": command.decision_status.value,
            "decision_value": command.decision_value,
            "effective_at": command.effective_at.isoformat(timespec="microseconds"),
            "expected_current_gate_id": command.expected_current_gate_id,
            "gate_code": command.gate_code.value,
            "scope_key": command.scope_key,
            "source_reference": command.source_reference,
            "source_version": command.source_version,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _rows(transaction: Session) -> list[CustomerDecisionGate]:
    return list(
        transaction.execute(
            select(CustomerDecisionGate).order_by(CustomerDecisionGate.recorded_at)
        ).scalars()
    )


def _assert_error(
    error: BusinessError,
    *,
    code: str,
    status_code: int,
    details: dict,
) -> None:
    assert error.code == code
    assert error.status_code == status_code
    assert error.details == details


def _assert_invalid(service: ModuleType, transaction: Session, command, field: str) -> None:
    before = list(
        transaction.execute(
            select(CustomerDecisionGate.id, CustomerDecisionGate.current_identity_key)
        )
    )
    with pytest.raises(BusinessError) as caught:
        service.record_decision_gate(command, transaction)
    _assert_error(
        caught.value,
        code="DECISION_GATE_INVALID",
        status_code=400,
        details={"field": field},
    )
    after = list(
        transaction.execute(
            select(CustomerDecisionGate.id, CustomerDecisionGate.current_identity_key)
        )
    )
    assert after == before


def _insert_winner(
    transaction: Session,
    command,
    *,
    gate_id: str | None = None,
    decision_snapshot: str | None = None,
    idempotency_key: str | None = None,
    current_identity_key: str | None = None,
) -> CustomerDecisionGate:
    row = CustomerDecisionGate(
        id=gate_id or str(uuid4()),
        gate_code=command.gate_code.value,
        scope_key=command.scope_key,
        decision_value=command.decision_value,
        decision_status=command.decision_status.value,
        source_reference=command.source_reference,
        source_version=command.source_version,
        confirmed_by=command.confirmed_by,
        effective_at=command.effective_at,
        supersedes_gate_id=None,
        decision_snapshot=decision_snapshot or _canonical_snapshot(command),
        idempotency_key=idempotency_key or command.idempotency_key,
        current_identity_key=current_identity_key,
    )
    transaction.add(row)
    transaction.commit()
    return row


def _hide_first_gate_query(monkeypatch, transaction: Session, marker: str) -> None:
    original_execute = transaction.execute
    hidden = False

    def execute(statement, *args, **kwargs):
        nonlocal hidden
        rendered = str(statement)
        where_clause = rendered.partition("WHERE")[2]
        if not hidden and "t_customer_decision_gate" in rendered and marker in where_clause:
            hidden = True

            class EmptyResult:
                @staticmethod
                def scalar_one_or_none():
                    return None

            return EmptyResult()
        return original_execute(statement, *args, **kwargs)

    monkeypatch.setattr(transaction, "execute", execute)


def _raise_task_flush(monkeypatch, transaction: Session) -> None:
    original_flush = transaction.flush
    flush_calls = 0

    def flush(*args, **kwargs):
        nonlocal flush_calls
        flush_calls += 1
        if flush_calls == 2:
            raise IntegrityError("simulated unique winner", {}, Exception())
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(transaction, "flush", flush)


def test_public_contract_is_exact_and_synchronous() -> None:
    service = _service_module()
    assert service is not None, f"{MODULE} is absent"

    assert tuple(member.value for member in service.DecisionGateCode) == GATE_VALUES
    assert tuple(member.value for member in service.DecisionGateStatus) == STATUS_VALUES
    assert tuple(member.value for member in service.DecisionGateRecordDisposition) == (
        DISPOSITION_VALUES
    )
    assert issubclass(service.DecisionGateCode, str)
    assert issubclass(service.DecisionGateStatus, str)
    assert issubclass(service.DecisionGateRecordDisposition, str)

    assert is_dataclass(service.RecordDecisionGateCommand)
    assert service.RecordDecisionGateCommand.__dataclass_params__.frozen is True
    assert tuple(field.name for field in fields(service.RecordDecisionGateCommand)) == (
        COMMAND_FIELDS
    )
    command_hints = get_type_hints(service.RecordDecisionGateCommand)
    assert tuple(command_hints) == COMMAND_FIELDS
    assert command_hints == {
        "gate_code": service.DecisionGateCode,
        "scope_key": str,
        "decision_value": str | None,
        "decision_status": service.DecisionGateStatus,
        "source_reference": str,
        "source_version": str,
        "confirmed_by": str,
        "effective_at": datetime,
        "idempotency_key": str,
        "expected_current_gate_id": str | None,
    }

    assert is_dataclass(service.DecisionGateRecordResult)
    assert service.DecisionGateRecordResult.__dataclass_params__.frozen is True
    assert tuple(field.name for field in fields(service.DecisionGateRecordResult)) == RESULT_FIELDS
    result_hints = get_type_hints(service.DecisionGateRecordResult)
    assert tuple(result_hints) == RESULT_FIELDS
    assert result_hints == {
        "gate_id": str,
        "gate_code": service.DecisionGateCode,
        "scope_key": str,
        "decision_value": str | None,
        "decision_status": service.DecisionGateStatus,
        "source_reference": str,
        "source_version": str,
        "confirmed_by": str,
        "effective_at": datetime,
        "supersedes_gate_id": str | None,
        "decision_snapshot": str,
        "idempotency_key": str,
        "current_identity_key": str | None,
        "disposition": service.DecisionGateRecordDisposition,
    }

    signature = inspect.signature(service.record_decision_gate)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert get_type_hints(service.record_decision_gate) == {
        "command": service.RecordDecisionGateCommand,
        "transaction": Session,
        "return": service.DecisionGateRecordResult,
    }
    assert inspect.iscoroutinefunction(service.record_decision_gate) is False

    sample = service.RecordDecisionGateCommand(
        service.DecisionGateCode.FEE_APPLICATION_DRAFT,
        "GLOBAL",
        "VALUE",
        service.DecisionGateStatus.CONFIRMED,
        "source",
        "v1",
        str(uuid4()),
        EFFECTIVE_AT,
        "request",
        None,
    )
    with pytest.raises(FrozenInstanceError):
        sample.scope_key = "case:changed"


def test_first_confirmation_persists_canonical_current_row_without_commit_or_rollback(
    service: ModuleType,
    db: Session,
    monkeypatch,
) -> None:
    command = _command(service, _actor_id(db))
    commit_calls = 0
    rollback_calls = 0

    def commit() -> None:
        nonlocal commit_calls
        commit_calls += 1

    def rollback() -> None:
        nonlocal rollback_calls
        rollback_calls += 1

    monkeypatch.setattr(db, "commit", commit)
    monkeypatch.setattr(db, "rollback", rollback)

    result = service.record_decision_gate(command, db)

    assert result.disposition is service.DecisionGateRecordDisposition.CREATED
    assert str(UUID(result.gate_id)) == result.gate_id
    assert result.gate_code is command.gate_code
    assert result.scope_key == "GLOBAL"
    assert result.decision_value == "CUSTOMER_APPROVED"
    assert result.decision_status is service.DecisionGateStatus.CONFIRMED
    assert result.source_reference == command.source_reference
    assert result.source_version == command.source_version
    assert result.confirmed_by == command.confirmed_by
    assert result.effective_at == EFFECTIVE_AT
    assert result.supersedes_gate_id is None
    assert result.decision_snapshot == _canonical_snapshot(command)
    assert result.idempotency_key == command.idempotency_key
    assert result.current_identity_key == "DG-FEE-APPLICATION-DRAFT|GLOBAL"
    assert commit_calls == 0
    assert rollback_calls == 0

    rows = _rows(db)
    assert len(rows) == 1
    assert rows[0].id == result.gate_id
    assert rows[0].decision_snapshot == result.decision_snapshot
    assert rows[0].current_identity_key == result.current_identity_key


def test_exact_replay_reuses_same_row_while_current_and_after_supersession(
    service: ModuleType,
    db: Session,
) -> None:
    first_command = _command(service, _actor_id(db))
    first = service.record_decision_gate(first_command, db)

    replay = service.record_decision_gate(first_command, db)
    assert replay.gate_id == first.gate_id
    assert replay.disposition is service.DecisionGateRecordDisposition.REUSED
    assert len(_rows(db)) == 1

    second_command = replace(
        first_command,
        decision_value="CUSTOMER_CHANGED",
        idempotency_key="decision-request-002",
        expected_current_gate_id=first.gate_id,
    )
    second = service.record_decision_gate(second_command, db)
    assert second.disposition is service.DecisionGateRecordDisposition.CREATED

    rows_before_replay = [(row.id, row.current_identity_key) for row in _rows(db)]
    superseded_replay = service.record_decision_gate(first_command, db)
    rows_after_replay = [(row.id, row.current_identity_key) for row in _rows(db)]

    assert superseded_replay.gate_id == first.gate_id
    assert superseded_replay.current_identity_key is None
    assert superseded_replay.disposition is service.DecisionGateRecordDisposition.REUSED
    assert rows_after_replay == rows_before_replay
    assert rows_after_replay == [
        (first.gate_id, None),
        (second.gate_id, second.current_identity_key),
    ]


@pytest.mark.parametrize(
    ("changed_field", "changed_value"),
    [
        ("gate_code", "FEE_GRANT_YEAR_DRAFT"),
        ("scope_key", "case:case-001"),
        ("decision_value", "DIFFERENT"),
        ("decision_status", "REVOKED"),
        ("source_reference", "different-source"),
        ("source_version", "v2"),
        ("confirmed_by", "missing-actor"),
        ("effective_at", datetime(2026, 7, 14)),
        ("expected_current_gate_id", "00000000-0000-0000-0000-000000000001"),
    ],
)
def test_idempotency_payload_conflict_precedes_actor_and_current_checks(
    service: ModuleType,
    db: Session,
    changed_field: str,
    changed_value,
) -> None:
    first_command = _command(service, _actor_id(db))
    first = service.record_decision_gate(first_command, db)
    changes = {changed_field: changed_value}
    if changed_field == "gate_code":
        changes[changed_field] = service.DecisionGateCode.FEE_GRANT_YEAR_DRAFT
    elif changed_field == "decision_status":
        changes[changed_field] = service.DecisionGateStatus.REVOKED
        changes["decision_value"] = None
    conflict_command = replace(first_command, **changes)

    with pytest.raises(BusinessError) as caught:
        service.record_decision_gate(conflict_command, db)

    _assert_error(
        caught.value,
        code="DECISION_GATE_IDEMPOTENCY_PAYLOAD_CONFLICT",
        status_code=409,
        details={
            "idempotency_key": first_command.idempotency_key,
            "existing_gate_id": first.gate_id,
        },
    )
    rows = _rows(db)
    assert [(row.id, row.current_identity_key) for row in rows] == [
        (first.gate_id, first.current_identity_key)
    ]


def test_confirm_revoke_and_reconfirm_preserve_exact_supersession_chain(
    service: ModuleType,
    db: Session,
) -> None:
    actor_id = _actor_id(db)
    confirmed = service.record_decision_gate(_command(service, actor_id), db)
    revoked_command = _command(
        service,
        actor_id,
        decision_value=None,
        decision_status=service.DecisionGateStatus.REVOKED,
        idempotency_key="decision-request-002",
        expected_current_gate_id=confirmed.gate_id,
    )
    revoked = service.record_decision_gate(revoked_command, db)
    reconfirmed_command = _command(
        service,
        actor_id,
        decision_value="CUSTOMER_REAPPROVED",
        idempotency_key="decision-request-003",
        expected_current_gate_id=revoked.gate_id,
    )
    reconfirmed = service.record_decision_gate(reconfirmed_command, db)

    rows = _rows(db)
    assert [row.id for row in rows] == [confirmed.gate_id, revoked.gate_id, reconfirmed.gate_id]
    assert [row.decision_status for row in rows] == ["CONFIRMED", "REVOKED", "CONFIRMED"]
    assert [row.supersedes_gate_id for row in rows] == [
        None,
        confirmed.gate_id,
        revoked.gate_id,
    ]
    assert [row.current_identity_key for row in rows] == [
        None,
        None,
        "DG-FEE-APPLICATION-DRAFT|GLOBAL",
    ]


def test_repeated_confirmation_value_with_new_key_is_a_new_decision(
    service: ModuleType,
    db: Session,
) -> None:
    actor_id = _actor_id(db)
    first_command = _command(service, actor_id)
    first = service.record_decision_gate(first_command, db)
    second = service.record_decision_gate(
        replace(
            first_command,
            idempotency_key="decision-request-002",
            expected_current_gate_id=first.gate_id,
        ),
        db,
    )

    assert second.disposition is service.DecisionGateRecordDisposition.CREATED
    assert second.gate_id != first.gate_id
    assert second.supersedes_gate_id == first.gate_id


def test_transition_conflicts_have_exact_contract_and_do_not_write(
    service: ModuleType,
    db: Session,
) -> None:
    actor_id = _actor_id(db)
    identity = "DG-FEE-APPLICATION-DRAFT|GLOBAL"

    first_revocation = _command(
        service,
        actor_id,
        decision_value=None,
        decision_status=service.DecisionGateStatus.REVOKED,
    )
    with pytest.raises(BusinessError) as caught:
        service.record_decision_gate(first_revocation, db)
    _assert_error(
        caught.value,
        code="DECISION_GATE_CURRENT_NOT_FOUND",
        status_code=409,
        details={"current_identity_key": identity},
    )
    assert _rows(db) == []

    with pytest.raises(BusinessError) as caught:
        service.record_decision_gate(
            _command(
                service,
                actor_id,
                expected_current_gate_id="00000000-0000-0000-0000-000000000001",
            ),
            db,
        )
    _assert_error(
        caught.value,
        code="DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
        status_code=409,
        details={
            "current_identity_key": identity,
            "expected_current_gate_id": "00000000-0000-0000-0000-000000000001",
            "actual_current_gate_id": None,
        },
    )
    assert _rows(db) == []

    confirmed = service.record_decision_gate(
        _command(service, actor_id, idempotency_key="decision-request-003"),
        db,
    )
    for key, expected in [
        ("decision-request-004", None),
        ("decision-request-005", "00000000-0000-0000-0000-000000000002"),
    ]:
        with pytest.raises(BusinessError) as caught:
            service.record_decision_gate(
                _command(
                    service,
                    actor_id,
                    idempotency_key=key,
                    expected_current_gate_id=expected,
                ),
                db,
            )
        _assert_error(
            caught.value,
            code="DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
            status_code=409,
            details={
                "current_identity_key": identity,
                "expected_current_gate_id": expected,
                "actual_current_gate_id": confirmed.gate_id,
            },
        )

    revoked = service.record_decision_gate(
        _command(
            service,
            actor_id,
            decision_value=None,
            decision_status=service.DecisionGateStatus.REVOKED,
            idempotency_key="decision-request-006",
            expected_current_gate_id=confirmed.gate_id,
        ),
        db,
    )
    with pytest.raises(BusinessError) as caught:
        service.record_decision_gate(
            _command(
                service,
                actor_id,
                decision_value=None,
                decision_status=service.DecisionGateStatus.REVOKED,
                idempotency_key="decision-request-007",
                expected_current_gate_id=revoked.gate_id,
            ),
            db,
        )
    _assert_error(
        caught.value,
        code="DECISION_GATE_ALREADY_REVOKED",
        status_code=409,
        details={"current_gate_id": revoked.gate_id},
    )
    assert len(_rows(db)) == 2


class GateCodeLookalike(str, Enum):
    VALUE = "DG-FEE-APPLICATION-DRAFT"


class StatusLookalike(str, Enum):
    VALUE = "CONFIRMED"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("gate_code", "DG-FEE-APPLICATION-DRAFT"),
        ("gate_code", GateCodeLookalike.VALUE),
        ("scope_key", ""),
        ("scope_key", " GLOBAL"),
        ("scope_key", "GLOBAL\x00"),
        ("scope_key", "x" * 257),
        ("source_reference", ""),
        ("source_reference", "source "),
        ("source_reference", "source\x00"),
        ("source_reference", "x" * 513),
        ("source_version", ""),
        ("source_version", " v1"),
        ("source_version", "v1\x00"),
        ("source_version", "x" * 129),
        ("confirmed_by", ""),
        ("confirmed_by", " actor"),
        ("confirmed_by", "actor\x00"),
        ("confirmed_by", "x" * 37),
        ("idempotency_key", ""),
        ("idempotency_key", "key "),
        ("idempotency_key", "key\x00"),
        ("idempotency_key", "x" * 129),
        ("expected_current_gate_id", "not-a-uuid"),
        ("expected_current_gate_id", "00000000-0000-0000-0000-000000000001 "),
        ("expected_current_gate_id", "00000000000000000000000000000001"),
        ("expected_current_gate_id", "00000000-0000-0000-0000-00000000000A"),
        ("expected_current_gate_id", "x" * 37),
        ("effective_at", "2026-07-13T09:08:07"),
        ("effective_at", datetime(2026, 7, 13, tzinfo=timezone.utc)),
        ("decision_status", "CONFIRMED"),
        ("decision_status", StatusLookalike.VALUE),
        ("decision_value", ""),
        ("decision_value", " VALUE"),
        ("decision_value", "VALUE\x00"),
    ],
)
def test_invalid_runtime_and_canonical_inputs_fail_in_the_named_field(
    service: ModuleType,
    db: Session,
    field: str,
    value,
) -> None:
    command = _command(service, _actor_id(db))
    _assert_invalid(service, db, replace(command, **{field: value}), field)


def test_invalid_command_instance_fails_before_field_access(
    service: ModuleType,
    db: Session,
) -> None:
    _assert_invalid(service, db, object(), "command")


@pytest.mark.parametrize(
    ("gate_name", "scope_key"),
    [
        ("FEE_APPLICATION_DRAFT", "global"),
        ("FEE_GRANT_YEAR_DRAFT", "case:"),
        ("FEE_FUTURE_ANNUITY", "case:a b"),
        ("GRANT_EVIDENCE_SOURCE", "case:a|b"),
        ("GRANT_MANUAL_REVIEW", f"case:{'x' * 37}"),
        ("PAYMENT_WORKBOOK", "form-001"),
        ("SERVICE_RATE_VERSION", "ALL-22"),
        ("LEGACY_FORM_CLASS", "GLOBAL"),
        ("LEGACY_FORM_CLASS", "case:case-001"),
        ("LEGACY_FORM_CLASS", "form-000"),
        ("LEGACY_FORM_CLASS", "form-023"),
        ("LEGACY_FORM_CLASS", "FORM-001"),
        ("LEGACY_FORM_CLASS", "all-22"),
    ],
)
def test_gate_scope_grammar_rejects_noncanonical_or_incompatible_scope(
    service: ModuleType,
    db: Session,
    gate_name: str,
    scope_key: str,
) -> None:
    command = _command(
        service,
        _actor_id(db),
        gate_code=getattr(service.DecisionGateCode, gate_name),
        scope_key=scope_key,
    )
    _assert_invalid(service, db, command, "scope_key")


@pytest.mark.parametrize(
    ("status_name", "decision_value"),
    [
        ("CONFIRMED", None),
        ("REVOKED", "VALUE"),
    ],
)
def test_status_value_combinations_are_exact(
    service: ModuleType,
    db: Session,
    status_name: str,
    decision_value: str | None,
) -> None:
    command = _command(
        service,
        _actor_id(db),
        decision_status=getattr(service.DecisionGateStatus, status_name),
        decision_value=decision_value,
    )
    _assert_invalid(service, db, command, "decision_value")


def _all_22_map(**changes: str) -> dict[str, str]:
    values = {f"form-{number:03d}": "HISTORICAL" for number in range(1, 23)}
    values.update(changes)
    return values


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


@pytest.mark.parametrize("scope_key", ["form-001", "form-022"])
@pytest.mark.parametrize(
    "decision_value",
    ["CURRENT_OFFICIAL", "HISTORICAL", "INTERNAL_ONLY"],
)
def test_scoped_legacy_classifications_pass(
    service: ModuleType,
    db: Session,
    scope_key: str,
    decision_value: str,
) -> None:
    result = service.record_decision_gate(
        _command(
            service,
            _actor_id(db),
            gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS,
            scope_key=scope_key,
            decision_value=decision_value,
            idempotency_key=f"legacy:{scope_key}:{decision_value}",
        ),
        db,
    )
    assert result.disposition is service.DecisionGateRecordDisposition.CREATED
    assert result.current_identity_key == f"DG-LEGACY-FORM-CLASS|{scope_key}"


def test_complete_canonical_all_22_map_passes(service: ModuleType, db: Session) -> None:
    value = _canonical_json(
        _all_22_map(
            **{
                "form-001": "CURRENT_OFFICIAL",
                "form-022": "INTERNAL_ONLY",
            }
        )
    )
    result = service.record_decision_gate(
        _command(
            service,
            _actor_id(db),
            gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS,
            scope_key="ALL-22",
            decision_value=value,
            idempotency_key="legacy:all-22",
        ),
        db,
    )
    assert result.decision_value == value


@pytest.mark.parametrize(
    "decision_value",
    [
        "HISTORICAL",
        _canonical_json({key: value for key, value in _all_22_map().items() if key != "form-022"}),
        _canonical_json({**_all_22_map(), "form-023": "HISTORICAL"}),
        json.dumps(_all_22_map(), ensure_ascii=False, sort_keys=True),
        _canonical_json(_all_22_map(**{"form-022": "UNKNOWN"})),
        _canonical_json({**_all_22_map(), "form-022": ["HISTORICAL"]}),
        _canonical_json({**_all_22_map(), "form-022": {"value": "HISTORICAL"}}),
        "[]",
        "not-json",
    ],
)
def test_all_22_rejects_blanket_incomplete_extra_noncanonical_and_illegal_maps(
    service: ModuleType,
    db: Session,
    decision_value: str,
) -> None:
    command = _command(
        service,
        _actor_id(db),
        gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS,
        scope_key="ALL-22",
        decision_value=decision_value,
    )
    _assert_invalid(service, db, command, "decision_value")


@pytest.mark.parametrize("decision_value", ["CURRENT", "historical", "{}"])
def test_scoped_legacy_rejects_unknown_classification(
    service: ModuleType,
    db: Session,
    decision_value: str,
) -> None:
    command = _command(
        service,
        _actor_id(db),
        gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS,
        scope_key="form-001",
        decision_value=decision_value,
    )
    _assert_invalid(service, db, command, "decision_value")


def test_missing_actor_has_exact_contract_and_preserves_current_identity(
    service: ModuleType,
    db: Session,
) -> None:
    actor_id = _actor_id(db)
    first = service.record_decision_gate(_command(service, actor_id), db)
    before = [(row.id, row.current_identity_key) for row in _rows(db)]
    command = _command(
        service,
        "00000000-0000-0000-0000-000000000099",
        idempotency_key="decision-request-002",
        expected_current_gate_id=first.gate_id,
    )

    with pytest.raises(BusinessError) as caught:
        service.record_decision_gate(command, db)

    _assert_error(
        caught.value,
        code="DECISION_GATE_ACTOR_NOT_FOUND",
        status_code=404,
        details={"confirmed_by": command.confirmed_by},
    )
    assert [(row.id, row.current_identity_key) for row in _rows(db)] == before


@pytest.mark.parametrize("snapshot_matches", [True, False])
def test_unique_idempotency_race_rereads_winner_without_outer_transaction_control(
    service: ModuleType,
    session_factory: sessionmaker,
    monkeypatch,
    snapshot_matches: bool,
) -> None:
    with session_factory() as setup:
        actor_id = _actor_id(setup)
        command = _command(service, actor_id)
        winner = _insert_winner(
            setup,
            command,
            decision_snapshot=(
                _canonical_snapshot(command) if snapshot_matches else '{"different":true}'
            ),
            current_identity_key=None,
        )
        winner_id = winner.id

    with session_factory() as transaction:
        _hide_first_gate_query(monkeypatch, transaction, "idempotency_key")
        commit_calls = 0
        rollback_calls = 0

        def commit() -> None:
            nonlocal commit_calls
            commit_calls += 1

        def rollback() -> None:
            nonlocal rollback_calls
            rollback_calls += 1

        monkeypatch.setattr(transaction, "commit", commit)
        monkeypatch.setattr(transaction, "rollback", rollback)

        if snapshot_matches:
            result = service.record_decision_gate(command, transaction)
            assert result.gate_id == winner_id
            assert result.disposition is service.DecisionGateRecordDisposition.REUSED
        else:
            with pytest.raises(BusinessError) as caught:
                service.record_decision_gate(command, transaction)
            _assert_error(
                caught.value,
                code="DECISION_GATE_IDEMPOTENCY_PAYLOAD_CONFLICT",
                status_code=409,
                details={
                    "idempotency_key": command.idempotency_key,
                    "existing_gate_id": winner_id,
                },
            )
        assert commit_calls == 0
        assert rollback_calls == 0


def test_unique_current_identity_race_reports_exact_winner_conflict(
    service: ModuleType,
    session_factory: sessionmaker,
    monkeypatch,
) -> None:
    with session_factory() as setup:
        actor_id = _actor_id(setup)
        command = _command(service, actor_id)
        winner_command = replace(command, idempotency_key="winner-request")
        winner = _insert_winner(
            setup,
            winner_command,
            current_identity_key="DG-FEE-APPLICATION-DRAFT|GLOBAL",
        )
        winner_id = winner.id

    with session_factory() as transaction:
        _hide_first_gate_query(monkeypatch, transaction, "current_identity_key")

        with pytest.raises(BusinessError) as caught:
            service.record_decision_gate(command, transaction)

        _assert_error(
            caught.value,
            code="DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
            status_code=409,
            details={
                "current_identity_key": "DG-FEE-APPLICATION-DRAFT|GLOBAL",
                "expected_current_gate_id": None,
                "actual_current_gate_id": winner_id,
            },
        )


def test_integrity_race_without_readable_winner_is_generic_write_conflict(
    service: ModuleType,
    db: Session,
    monkeypatch,
) -> None:
    command = _command(service, _actor_id(db))
    _raise_task_flush(monkeypatch, db)

    with pytest.raises(BusinessError) as caught:
        service.record_decision_gate(command, db)

    _assert_error(
        caught.value,
        code="DECISION_GATE_WRITE_CONFLICT",
        status_code=409,
        details={
            "idempotency_key": command.idempotency_key,
            "current_identity_key": "DG-FEE-APPLICATION-DRAFT|GLOBAL",
        },
    )
    assert _rows(db) == []


def test_unrelated_begin_nested_preflush_integrity_error_propagates_and_preserves_caller_state(
    service: ModuleType,
    db: Session,
    monkeypatch,
) -> None:
    command = _command(service, _actor_id(db))
    caller_pending_user = T_User(
        id=str(uuid4()),
        username="caller-pending-user",
        password_hash="not-used",
    )
    db.add(caller_pending_user)
    unrelated_error = IntegrityError("unrelated caller pending failure", {}, Exception())

    def fail_preflush(*_args, **_kwargs) -> None:
        raise unrelated_error

    monkeypatch.setattr(db, "flush", fail_preflush)

    with pytest.raises(IntegrityError) as caught:
        service.record_decision_gate(command, db)

    assert caught.value is unrelated_error
    assert db.is_active is True
    assert caller_pending_user in db.new
    assert not any(isinstance(value, CustomerDecisionGate) for value in db.new)
