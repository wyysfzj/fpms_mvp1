from __future__ import annotations

import inspect
import json
from contextlib import nullcontext
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from types import SimpleNamespace
from typing import get_type_hints

import pytest
from sqlalchemy import event, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import BusinessError
from app.modules.auth.models import T_User
from app.modules.system import decision_gate_service as service
from app.modules.system.models import CustomerDecisionGate

AS_OF = datetime(2026, 7, 13, 12, 0, 0, 123456)
FORM_KEYS = {f"form-{number:03d}" for number in range(1, 23)}


class _Result:
    def __init__(self, rows: list[object]) -> None:
        self._rows = rows

    def scalars(self) -> _Result:
        return self

    def all(self) -> list[object]:
        return self._rows


class TransactionSpy:
    def __init__(self, rows: list[object] | None = None) -> None:
        self.rows = rows or []
        self.execute_calls = 0
        self.statement = None
        self.prohibited_calls: list[str] = []
        self.no_autoflush = nullcontext()

    def execute(self, statement):
        self.execute_calls += 1
        self.statement = statement
        return _Result(self.rows)

    def _prohibited(self, name: str):
        self.prohibited_calls.append(name)
        raise AssertionError(f"read service called prohibited method: {name}")

    def add(self, *args, **kwargs):
        self._prohibited("add")

    def flush(self, *args, **kwargs):
        self._prohibited("flush")

    def commit(self, *args, **kwargs):
        self._prohibited("commit")

    def rollback(self, *args, **kwargs):
        self._prohibited("rollback")

    def begin_nested(self, *args, **kwargs):
        self._prohibited("begin_nested")

    def refresh(self, *args, **kwargs):
        self._prohibited("refresh")

    def close(self, *args, **kwargs):
        self._prohibited("close")


def _command(**changes):
    values = {
        "gate_code": service.DecisionGateCode.FEE_APPLICATION_DRAFT,
        "scope_key": "GLOBAL",
        "as_of": AS_OF,
    }
    values.update(changes)
    return service.ResolveDecisionGateCommand(**values)


def _row(
    *,
    gate_code: str = "DG-FEE-APPLICATION-DRAFT",
    scope_key: str = "GLOBAL",
    current_identity_key: str | None = "DG-FEE-APPLICATION-DRAFT|GLOBAL",
    decision_value: object = "CUSTOMER_APPROVED",
    decision_status: object = "CONFIRMED",
    effective_at: object = AS_OF,
    gate_id: str = "gate-001",
):
    return SimpleNamespace(
        id=gate_id,
        gate_code=gate_code,
        scope_key=scope_key,
        current_identity_key=current_identity_key,
        decision_value=decision_value,
        decision_status=decision_status,
        source_reference="customer-answer:2026-07-13",
        source_version="v1",
        confirmed_by="actor-001",
        effective_at=effective_at,
    )


def _canonical_map(**changes: str) -> str:
    values = {key: "CURRENT_OFFICIAL" for key in FORM_KEYS}
    values.update(changes)
    return json.dumps(
        values,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _assert_error(
    transaction: TransactionSpy,
    command,
    *,
    code: str,
    details: dict,
    select_count: int = 1,
) -> None:
    with pytest.raises(BusinessError) as caught:
        service.resolve_decision_gate(command, transaction)
    assert caught.value.code == code
    assert caught.value.status_code == (400 if code == "DECISION_GATE_INVALID" else 409)
    assert caught.value.details == details
    assert transaction.execute_calls == select_count
    assert transaction.prohibited_calls == []


def _query_values(transaction: TransactionSpy) -> set[str]:
    assert transaction.statement is not None
    assert transaction.statement.is_select is True
    values: set[str] = set()
    for value in transaction.statement.compile().params.values():
        if isinstance(value, list):
            values.update(value)
        elif isinstance(value, str):
            values.add(value)
    return values


def test_public_read_contract_is_exact_reuses_enum_and_is_synchronous() -> None:
    assert service.ResolveDecisionGateCommand.__dataclass_params__.frozen is True
    assert service.DecisionGateReadResult.__dataclass_params__.frozen is True
    assert is_dataclass(service.ResolveDecisionGateCommand)
    assert is_dataclass(service.DecisionGateReadResult)
    assert service.ResolveDecisionGateCommand.__slots__ == ("gate_code", "scope_key", "as_of")
    assert service.DecisionGateReadResult.__slots__ == (
        "gate_id",
        "gate_code",
        "requested_scope_key",
        "resolved_scope_key",
        "decision_value",
        "source_reference",
        "source_version",
        "confirmed_by",
        "effective_at",
    )
    assert tuple(field.name for field in fields(service.ResolveDecisionGateCommand)) == (
        "gate_code",
        "scope_key",
        "as_of",
    )
    assert get_type_hints(service.ResolveDecisionGateCommand) == {
        "gate_code": service.DecisionGateCode,
        "scope_key": str,
        "as_of": datetime,
    }
    assert tuple(field.name for field in fields(service.DecisionGateReadResult)) == (
        "gate_id",
        "gate_code",
        "requested_scope_key",
        "resolved_scope_key",
        "decision_value",
        "source_reference",
        "source_version",
        "confirmed_by",
        "effective_at",
    )
    assert get_type_hints(service.DecisionGateReadResult) == {
        "gate_id": str,
        "gate_code": service.DecisionGateCode,
        "requested_scope_key": str,
        "resolved_scope_key": str,
        "decision_value": str,
        "source_reference": str,
        "source_version": str,
        "confirmed_by": str,
        "effective_at": datetime,
    }
    signature = inspect.signature(service.resolve_decision_gate)
    assert tuple(signature.parameters) == ("command", "transaction")
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in inspect.signature(service.ResolveDecisionGateCommand).parameters.values()
    )
    assert get_type_hints(service.resolve_decision_gate) == {
        "command": service.ResolveDecisionGateCommand,
        "transaction": Session,
        "return": service.DecisionGateReadResult,
    }
    assert inspect.iscoroutinefunction(service.resolve_decision_gate) is False
    command = _command()
    with pytest.raises(FrozenInstanceError):
        command.scope_key = "case:changed"


class _GateLookalike(str, Enum):
    FEE_APPLICATION_DRAFT = "DG-FEE-APPLICATION-DRAFT"


@pytest.mark.parametrize(
    ("command", "field"),
    [
        (object(), "command"),
        (lambda: _command(gate_code="DG-FEE-APPLICATION-DRAFT"), "gate_code"),
        (lambda: _command(gate_code=_GateLookalike.FEE_APPLICATION_DRAFT), "gate_code"),
        (lambda: _command(scope_key=123), "scope_key"),
        (lambda: _command(scope_key=" GLOBAL"), "scope_key"),
        (lambda: _command(scope_key="GLOBAL "), "scope_key"),
        (lambda: _command(scope_key="G\x00LOBAL"), "scope_key"),
        (lambda: _command(scope_key="global"), "scope_key"),
        (lambda: _command(scope_key="case:"), "scope_key"),
        (lambda: _command(scope_key="case:a b"), "scope_key"),
        (lambda: _command(scope_key="case:a|b"), "scope_key"),
        (lambda: _command(scope_key=f"case:{'a' * 37}"), "scope_key"),
        (lambda: _command(as_of="2026-07-13"), "as_of"),
        (lambda: _command(as_of=timezone.utc), "as_of"),
        (lambda: _command(as_of=datetime.now(timezone.utc)), "as_of"),
    ],
)
def test_invalid_non_legacy_commands_fail_before_select(command, field: str) -> None:
    transaction = TransactionSpy()
    value = command() if callable(command) else command
    _assert_error(
        transaction,
        value,
        code="DECISION_GATE_INVALID",
        details={"field": field},
        select_count=0,
    )


@pytest.mark.parametrize(
    "scope_key",
    ["ALL-22", "GLOBAL", "case:1", "FORM-001", "form-000", "form-023", "form-01"],
)
def test_invalid_legacy_public_scopes_fail_before_select(scope_key: str) -> None:
    transaction = TransactionSpy()
    _assert_error(
        transaction,
        _command(gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS, scope_key=scope_key),
        code="DECISION_GATE_INVALID",
        details={"field": "scope_key"},
        select_count=0,
    )


def test_global_request_projects_exact_row_and_queries_only_global_identity() -> None:
    row = _row()
    transaction = TransactionSpy([row])
    result = service.resolve_decision_gate(_command(), transaction)
    assert result == service.DecisionGateReadResult(
        gate_id="gate-001",
        gate_code=service.DecisionGateCode.FEE_APPLICATION_DRAFT,
        requested_scope_key="GLOBAL",
        resolved_scope_key="GLOBAL",
        decision_value="CUSTOMER_APPROVED",
        source_reference="customer-answer:2026-07-13",
        source_version="v1",
        confirmed_by="actor-001",
        effective_at=AS_OF,
    )
    assert transaction.execute_calls == 1
    assert _query_values(transaction) == {"DG-FEE-APPLICATION-DRAFT|GLOBAL"}
    assert transaction.prohibited_calls == []


def test_case_request_prefers_case_and_falls_back_to_global_only_when_case_absent() -> None:
    case = _row(
        scope_key="case:C-1",
        current_identity_key="DG-FEE-APPLICATION-DRAFT|case:C-1",
        gate_id="case-gate",
    )
    global_row = _row(gate_id="global-gate")
    transaction = TransactionSpy([global_row, case])
    result = service.resolve_decision_gate(_command(scope_key="case:C-1"), transaction)
    assert result.gate_id == "case-gate"
    assert result.requested_scope_key == "case:C-1"
    assert result.resolved_scope_key == "case:C-1"
    assert _query_values(transaction) == {
        "DG-FEE-APPLICATION-DRAFT|case:C-1",
        "DG-FEE-APPLICATION-DRAFT|GLOBAL",
    }

    fallback_transaction = TransactionSpy([global_row])
    fallback = service.resolve_decision_gate(_command(scope_key="case:C-1"), fallback_transaction)
    assert fallback.gate_id == "global-gate"
    assert fallback.requested_scope_key == "case:C-1"
    assert fallback.resolved_scope_key == "GLOBAL"


@pytest.mark.parametrize(
    ("changes", "code", "details"),
    [
        (
            {"decision_status": "REVOKED"},
            "DECISION_GATE_REVOKED",
            {"gate_id": "case-gate", "resolved_scope_key": "case:C-1"},
        ),
        (
            {"effective_at": AS_OF + timedelta(microseconds=1)},
            "DECISION_GATE_NOT_EFFECTIVE",
            {
                "gate_id": "case-gate",
                "effective_at": "2026-07-13T12:00:00.123457",
                "as_of": "2026-07-13T12:00:00.123456",
            },
        ),
        (
            {"decision_value": " corrupt "},
            "DECISION_GATE_CURRENT_ROW_CORRUPT",
            {"gate_id": "case-gate", "field": "decision_value"},
        ),
    ],
)
def test_invalid_case_row_shadows_valid_global_fallback(changes, code: str, details: dict) -> None:
    case = _row(
        scope_key="case:C-1",
        current_identity_key="DG-FEE-APPLICATION-DRAFT|case:C-1",
        gate_id="case-gate",
        **changes,
    )
    transaction = TransactionSpy([_row(gate_id="global-gate"), case])
    _assert_error(
        transaction,
        _command(scope_key="case:C-1"),
        code=code,
        details=details,
    )


@pytest.mark.parametrize("form", ["form-001", "form-022"])
def test_legacy_form_resolves_direct_and_canonical_all_22_fallback(form: str) -> None:
    direct_identity = f"DG-LEGACY-FORM-CLASS|{form}"
    direct = _row(
        gate_code="DG-LEGACY-FORM-CLASS",
        scope_key=form,
        current_identity_key=direct_identity,
        decision_value="HISTORICAL",
        gate_id="direct-gate",
    )
    command = _command(gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS, scope_key=form)
    direct_result = service.resolve_decision_gate(command, TransactionSpy([direct]))
    assert direct_result.decision_value == "HISTORICAL"
    assert direct_result.requested_scope_key == form
    assert direct_result.resolved_scope_key == form

    carrier = _row(
        gate_code="DG-LEGACY-FORM-CLASS",
        scope_key="ALL-22",
        current_identity_key="DG-LEGACY-FORM-CLASS|ALL-22",
        decision_value=_canonical_map(**{form: "INTERNAL_ONLY"}),
        gate_id="map-gate",
    )
    fallback_transaction = TransactionSpy([carrier])
    fallback_result = service.resolve_decision_gate(command, fallback_transaction)
    assert fallback_result.decision_value == "INTERNAL_ONLY"
    assert fallback_result.requested_scope_key == form
    assert fallback_result.resolved_scope_key == "ALL-22"
    assert _query_values(fallback_transaction) == {
        direct_identity,
        "DG-LEGACY-FORM-CLASS|ALL-22",
    }


@pytest.mark.parametrize(
    ("changes", "code", "details"),
    [
        (
            {"decision_status": "REVOKED"},
            "DECISION_GATE_REVOKED",
            {"gate_id": "direct-gate", "resolved_scope_key": "form-001"},
        ),
        (
            {"effective_at": AS_OF + timedelta(microseconds=1)},
            "DECISION_GATE_NOT_EFFECTIVE",
            {
                "gate_id": "direct-gate",
                "effective_at": "2026-07-13T12:00:00.123457",
                "as_of": "2026-07-13T12:00:00.123456",
            },
        ),
        (
            {"decision_value": "BLANKET"},
            "DECISION_GATE_CURRENT_ROW_CORRUPT",
            {"gate_id": "direct-gate", "field": "decision_value"},
        ),
    ],
)
def test_invalid_direct_form_shadows_valid_all_22(changes, code: str, details: dict) -> None:
    direct = _row(
        gate_code="DG-LEGACY-FORM-CLASS",
        scope_key="form-001",
        current_identity_key="DG-LEGACY-FORM-CLASS|form-001",
        gate_id="direct-gate",
        **changes,
    )
    carrier = _row(
        gate_code="DG-LEGACY-FORM-CLASS",
        scope_key="ALL-22",
        current_identity_key="DG-LEGACY-FORM-CLASS|ALL-22",
        decision_value=_canonical_map(),
        gate_id="map-gate",
    )
    transaction = TransactionSpy([carrier, direct])
    _assert_error(
        transaction,
        _command(
            gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS,
            scope_key="form-001",
        ),
        code=code,
        details=details,
    )


def test_missing_identity_mismatch_and_candidate_multiplicity_fail_closed() -> None:
    command = _command(scope_key="case:C-1")
    _assert_error(
        TransactionSpy(),
        command,
        code="DECISION_GATE_NOT_FOUND",
        details={"gate_code": "DG-FEE-APPLICATION-DRAFT", "scope_key": "case:C-1"},
    )

    mismatch = _row(
        gate_code="DG-FEE-APPLICATION-DRAFT",
        scope_key="case:C-2",
        current_identity_key="DG-FEE-APPLICATION-DRAFT|case:C-1",
        gate_id="mismatch",
    )
    _assert_error(
        TransactionSpy([mismatch]),
        command,
        code="DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
        details={
            "gate_id": "mismatch",
            "expected_current_identity_key": "DG-FEE-APPLICATION-DRAFT|case:C-1",
            "actual_current_identity_key": "DG-FEE-APPLICATION-DRAFT|case:C-1",
            "actual_gate_code": "DG-FEE-APPLICATION-DRAFT",
            "actual_scope_key": "case:C-2",
        },
    )

    null_identity = _row(current_identity_key=None, gate_id="null-identity")
    _assert_error(
        TransactionSpy([null_identity]),
        _command(),
        code="DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
        details={
            "gate_id": "null-identity",
            "expected_current_identity_key": "DG-FEE-APPLICATION-DRAFT|GLOBAL",
            "actual_current_identity_key": None,
            "actual_gate_code": "DG-FEE-APPLICATION-DRAFT",
            "actual_scope_key": "GLOBAL",
        },
    )

    duplicate_case = [
        _row(
            scope_key="case:C-1",
            current_identity_key="DG-FEE-APPLICATION-DRAFT|case:C-1",
            gate_id=f"case-{number}",
        )
        for number in (1, 2)
    ]
    _assert_error(
        TransactionSpy([*duplicate_case, _row(gate_id="global")]),
        command,
        code="DECISION_GATE_CANDIDATE_MULTIPLICITY",
        details={
            "current_identity_key": "DG-FEE-APPLICATION-DRAFT|case:C-1",
            "candidate_count": 2,
        },
    )

    duplicate_global = [_row(gate_id=f"global-{number}") for number in (1, 2)]
    _assert_error(
        TransactionSpy(duplicate_global),
        command,
        code="DECISION_GATE_CANDIDATE_MULTIPLICITY",
        details={
            "current_identity_key": "DG-FEE-APPLICATION-DRAFT|GLOBAL",
            "candidate_count": 2,
        },
    )


@pytest.mark.parametrize(
    "value",
    [
        "not-json",
        json.dumps({key: "CURRENT_OFFICIAL" for key in FORM_KEYS}),
        _canonical_map()[:-1],
        json.dumps(
            {**{key: "CURRENT_OFFICIAL" for key in FORM_KEYS}, "form-023": "HISTORICAL"},
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps(
            {key: "CURRENT_OFFICIAL" for key in FORM_KEYS if key != "form-022"},
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps({key: "BLANKET" for key in FORM_KEYS}, sort_keys=True, separators=(",", ":")),
        json.dumps({key: 1 for key in FORM_KEYS}, sort_keys=True, separators=(",", ":")),
        json.dumps(
            {**{key: "CURRENT_OFFICIAL" for key in FORM_KEYS}, "form-001": "INVALID"},
            sort_keys=True,
            separators=(",", ":"),
        ),
        json.dumps("CURRENT_OFFICIAL"),
    ],
)
def test_corrupt_legacy_map_fails_closed(value: str) -> None:
    carrier = _row(
        gate_code="DG-LEGACY-FORM-CLASS",
        scope_key="ALL-22",
        current_identity_key="DG-LEGACY-FORM-CLASS|ALL-22",
        decision_value=value,
        gate_id="map-gate",
    )
    _assert_error(
        TransactionSpy([carrier]),
        _command(
            gate_code=service.DecisionGateCode.LEGACY_FORM_CLASS,
            scope_key="form-001",
        ),
        code="DECISION_GATE_LEGACY_MAP_CORRUPT",
        details={"gate_id": "map-gate", "scope_key": "ALL-22"},
    )


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"decision_status": "UNKNOWN"}, "decision_status"),
        ({"effective_at": "2026-07-13"}, "effective_at"),
        ({"effective_at": datetime.now(timezone.utc)}, "effective_at"),
        ({"decision_value": ""}, "decision_value"),
        ({"decision_value": None}, "decision_value"),
        ({"decision_value": "VALUE\x00"}, "decision_value"),
    ],
)
def test_selected_current_row_corruption_has_exact_field(changes, field: str) -> None:
    row = _row(**changes)
    _assert_error(
        TransactionSpy([row]),
        _command(),
        code="DECISION_GATE_CURRENT_ROW_CORRUPT",
        details={"gate_id": "gate-001", "field": field},
    )


def test_effective_boundary_and_future_current_never_revives_superseded_row() -> None:
    equality = service.resolve_decision_gate(_command(), TransactionSpy([_row()]))
    assert equality.effective_at == AS_OF

    future = _row(effective_at=AS_OF + timedelta(microseconds=1), gate_id="future")
    superseded = _row(current_identity_key=None, gate_id="old")
    transaction = TransactionSpy([future])
    _assert_error(
        transaction,
        _command(),
        code="DECISION_GATE_NOT_EFFECTIVE",
        details={
            "gate_id": "future",
            "effective_at": "2026-07-13T12:00:00.123457",
            "as_of": "2026-07-13T12:00:00.123456",
        },
    )
    assert superseded not in transaction.rows


def test_real_session_read_does_not_autoflush_or_select_pending_gate(
    session_factory: sessionmaker[Session],
) -> None:
    autoflush_factory = sessionmaker(
        bind=session_factory.kw["bind"],
        autoflush=True,
        expire_on_commit=False,
    )
    with autoflush_factory() as transaction:
        actor_id = transaction.scalar(select(T_User.id).where(T_User.username == "admin"))
        identity = "DG-PAYMENT-WORKBOOK|case:pending-real-session"
        pending = CustomerDecisionGate(
            id="pending-gate",
            gate_code="DG-PAYMENT-WORKBOOK",
            scope_key="case:pending-real-session",
            decision_value="CUSTOMER_APPROVED",
            decision_status="CONFIRMED",
            source_reference="pending-caller-state",
            source_version="v1",
            confirmed_by=actor_id,
            effective_at=AS_OF,
            supersedes_gate_id=None,
            decision_snapshot="{}",
            idempotency_key="pending-real-session",
            current_identity_key=identity,
        )
        transaction.add(pending)
        connection = transaction.connection()

        transaction_before = transaction.get_transaction()
        new_before = tuple(transaction.new)
        dirty_before = tuple(transaction.dirty)
        identity_map_before = tuple(transaction.identity_map.keys())
        pending_identity_before = sa_inspect(pending).identity_key
        current_identity_before = pending.current_identity_key
        in_transaction_before = transaction.in_transaction()
        in_nested_transaction_before = transaction.in_nested_transaction()
        is_active_before = transaction.is_active
        statements: list[str] = []

        def trace_statement(
            _connection,
            _cursor,
            statement: str,
            _parameters,
            _context,
            _executemany,
        ) -> None:
            statements.append(statement.lstrip().partition(" ")[0].upper())

        error: BusinessError | None = None
        result = None
        event.listen(connection, "before_cursor_execute", trace_statement)
        try:
            try:
                result = service.resolve_decision_gate(
                    _command(
                        gate_code=service.DecisionGateCode.PAYMENT_WORKBOOK,
                        scope_key="case:pending-real-session",
                    ),
                    transaction,
                )
            except BusinessError as caught:
                error = caught
        finally:
            event.remove(connection, "before_cursor_execute", trace_statement)

        assert statements == ["SELECT"]
        assert result is None
        assert error is not None
        assert error.code == "DECISION_GATE_NOT_FOUND"
        assert error.status_code == 409
        assert error.details == {
            "gate_code": "DG-PAYMENT-WORKBOOK",
            "scope_key": "case:pending-real-session",
        }
        assert tuple(transaction.new) == new_before == (pending,)
        assert tuple(transaction.dirty) == dirty_before == ()
        assert tuple(transaction.identity_map.keys()) == identity_map_before
        assert sa_inspect(pending).pending is True
        assert sa_inspect(pending).persistent is False
        assert sa_inspect(pending).identity_key == pending_identity_before is None
        assert pending.current_identity_key == current_identity_before == identity
        assert transaction.get_transaction() is transaction_before
        assert transaction.in_transaction() is in_transaction_before is True
        assert transaction.in_nested_transaction() is in_nested_transaction_before is False
        assert transaction.is_active is is_active_before is True
