from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, MultipleResultsFound
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.auth.models import T_User
from app.modules.system.models import CustomerDecisionGate


class DecisionGateCode(str, Enum):
    FEE_APPLICATION_DRAFT = "DG-FEE-APPLICATION-DRAFT"
    FEE_GRANT_YEAR_DRAFT = "DG-FEE-GRANT-YEAR-DRAFT"
    FEE_FUTURE_ANNUITY = "DG-FEE-FUTURE-ANNUITY"
    GRANT_EVIDENCE_SOURCE = "DG-GRANT-EVIDENCE-SOURCE"
    GRANT_MANUAL_REVIEW = "DG-GRANT-MANUAL-REVIEW"
    PAYMENT_WORKBOOK = "DG-PAYMENT-WORKBOOK"
    SERVICE_RATE_VERSION = "DG-SERVICE-RATE-VERSION"
    LEGACY_FORM_CLASS = "DG-LEGACY-FORM-CLASS"


class DecisionGateStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    REVOKED = "REVOKED"


class DecisionGateRecordDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True)
class RecordDecisionGateCommand:
    gate_code: DecisionGateCode
    scope_key: str
    decision_value: str | None
    decision_status: DecisionGateStatus
    source_reference: str
    source_version: str
    confirmed_by: str
    effective_at: datetime
    idempotency_key: str
    expected_current_gate_id: str | None


@dataclass(frozen=True)
class DecisionGateRecordResult:
    gate_id: str
    gate_code: DecisionGateCode
    scope_key: str
    decision_value: str | None
    decision_status: DecisionGateStatus
    source_reference: str
    source_version: str
    confirmed_by: str
    effective_at: datetime
    supersedes_gate_id: str | None
    decision_snapshot: str
    idempotency_key: str
    current_identity_key: str | None
    disposition: DecisionGateRecordDisposition


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveDecisionGateCommand:
    gate_code: DecisionGateCode
    scope_key: str
    as_of: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class DecisionGateReadResult:
    gate_id: str
    gate_code: DecisionGateCode
    requested_scope_key: str
    resolved_scope_key: str
    decision_value: str
    source_reference: str
    source_version: str
    confirmed_by: str
    effective_at: datetime


_LEGACY_CLASSIFICATIONS = {"CURRENT_OFFICIAL", "HISTORICAL", "INTERNAL_ONLY"}
_LEGACY_FORM_KEYS = {f"form-{number:03d}" for number in range(1, 23)}


def _invalid(field: str) -> None:
    raise_business_error(
        "DECISION_GATE_INVALID",
        "Invalid decision gate input",
        details={"field": field},
        status_code=400,
    )


def _validate_string(value: object, field: str, limit: int) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or len(value) > limit
    ):
        _invalid(field)
    return value


def _validate_expected_gate_id(value: str | None) -> None:
    if value is None:
        return
    try:
        parsed = UUID(value)
    except (TypeError, ValueError, AttributeError):
        _invalid("expected_current_gate_id")
    if str(parsed) != value:
        _invalid("expected_current_gate_id")


def _validate_scope(command: RecordDecisionGateCommand) -> None:
    if command.gate_code is DecisionGateCode.LEGACY_FORM_CLASS:
        if command.scope_key == "ALL-22":
            return
        if command.scope_key not in _LEGACY_FORM_KEYS:
            _invalid("scope_key")
        return

    if command.scope_key == "GLOBAL":
        return
    if not command.scope_key.startswith("case:"):
        _invalid("scope_key")
    case_id = command.scope_key[5:]
    if (
        not 1 <= len(case_id) <= 36
        or "|" in case_id
        or any(character.isspace() for character in case_id)
    ):
        _invalid("scope_key")


def _validate_decision_value(command: RecordDecisionGateCommand) -> None:
    if command.decision_status is DecisionGateStatus.REVOKED:
        if command.decision_value is not None:
            _invalid("decision_value")
        return

    value = command.decision_value
    if type(value) is not str or not value or value != value.strip() or "\x00" in value:
        _invalid("decision_value")
    if command.gate_code is not DecisionGateCode.LEGACY_FORM_CLASS:
        return
    if command.scope_key != "ALL-22":
        if value not in _LEGACY_CLASSIFICATIONS:
            _invalid("decision_value")
        return
    try:
        parsed = json.loads(value)
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        _invalid("decision_value")
    if (
        type(parsed) is not dict
        or set(parsed) != _LEGACY_FORM_KEYS
        or any(
            type(classification) is not str or classification not in _LEGACY_CLASSIFICATIONS
            for classification in parsed.values()
        )
        or canonical != value
    ):
        _invalid("decision_value")


def _snapshot(command: RecordDecisionGateCommand) -> str:
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


def _validate_command(command: object) -> tuple[RecordDecisionGateCommand, str, str]:
    if type(command) is not RecordDecisionGateCommand:
        _invalid("command")
    if type(command.gate_code) is not DecisionGateCode:
        _invalid("gate_code")
    if type(command.decision_status) is not DecisionGateStatus:
        _invalid("decision_status")

    _validate_string(command.scope_key, "scope_key", 256)
    _validate_string(command.source_reference, "source_reference", 512)
    _validate_string(command.source_version, "source_version", 128)
    _validate_string(command.confirmed_by, "confirmed_by", 36)
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    if command.expected_current_gate_id is not None:
        _validate_string(command.expected_current_gate_id, "expected_current_gate_id", 36)
    _validate_expected_gate_id(command.expected_current_gate_id)

    if (
        not isinstance(command.effective_at, datetime)
        or command.effective_at.utcoffset() is not None
    ):
        _invalid("effective_at")
    _validate_scope(command)
    _validate_decision_value(command)
    snapshot = _snapshot(command)
    current_identity = f"{command.gate_code.value}|{command.scope_key}"
    return command, snapshot, current_identity


def _idempotency_row(
    transaction: Session,
    idempotency_key: str,
) -> CustomerDecisionGate | None:
    return transaction.execute(
        select(CustomerDecisionGate).where(CustomerDecisionGate.idempotency_key == idempotency_key)
    ).scalar_one_or_none()


def _raise_current_conflict(
    current_identity: str,
    expected_current_gate_id: str | None,
    actual_current_gate_id: str | None,
) -> None:
    raise_business_error(
        "DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
        "Decision gate current identity conflict",
        details={
            "current_identity_key": current_identity,
            "expected_current_gate_id": expected_current_gate_id,
            "actual_current_gate_id": actual_current_gate_id,
        },
        status_code=409,
    )


def _current_row(
    transaction: Session,
    current_identity: str,
    expected_current_gate_id: str | None,
) -> CustomerDecisionGate | None:
    try:
        return transaction.execute(
            select(CustomerDecisionGate).where(
                CustomerDecisionGate.current_identity_key == current_identity
            )
        ).scalar_one_or_none()
    except MultipleResultsFound:
        _raise_current_conflict(current_identity, expected_current_gate_id, None)


def _result(
    row: CustomerDecisionGate,
    disposition: DecisionGateRecordDisposition,
) -> DecisionGateRecordResult:
    return DecisionGateRecordResult(
        gate_id=row.id,
        gate_code=DecisionGateCode(row.gate_code),
        scope_key=row.scope_key,
        decision_value=row.decision_value,
        decision_status=DecisionGateStatus(row.decision_status),
        source_reference=row.source_reference,
        source_version=row.source_version,
        confirmed_by=row.confirmed_by,
        effective_at=row.effective_at,
        supersedes_gate_id=row.supersedes_gate_id,
        decision_snapshot=row.decision_snapshot,
        idempotency_key=row.idempotency_key,
        current_identity_key=row.current_identity_key,
        disposition=disposition,
    )


def _reuse_or_conflict(
    row: CustomerDecisionGate,
    snapshot: str,
    idempotency_key: str,
) -> DecisionGateRecordResult:
    if row.decision_snapshot == snapshot:
        return _result(row, DecisionGateRecordDisposition.REUSED)
    raise_business_error(
        "DECISION_GATE_IDEMPOTENCY_PAYLOAD_CONFLICT",
        "Decision gate idempotency payload conflict",
        details={"idempotency_key": idempotency_key, "existing_gate_id": row.id},
        status_code=409,
    )


def record_decision_gate(
    command: RecordDecisionGateCommand,
    transaction: Session,
) -> DecisionGateRecordResult:
    command, snapshot, current_identity = _validate_command(command)

    existing = _idempotency_row(transaction, command.idempotency_key)
    if existing is not None:
        return _reuse_or_conflict(existing, snapshot, command.idempotency_key)

    actor_exists = transaction.execute(
        select(T_User.id).where(T_User.id == command.confirmed_by)
    ).scalar_one_or_none()
    if actor_exists is None:
        raise_business_error(
            "DECISION_GATE_ACTOR_NOT_FOUND",
            "Decision gate actor not found",
            details={"confirmed_by": command.confirmed_by},
            status_code=404,
        )

    current = _current_row(transaction, current_identity, command.expected_current_gate_id)
    if current is None:
        if command.decision_status is DecisionGateStatus.REVOKED:
            raise_business_error(
                "DECISION_GATE_CURRENT_NOT_FOUND",
                "Decision gate current row not found",
                details={"current_identity_key": current_identity},
                status_code=409,
            )
        if command.expected_current_gate_id is not None:
            _raise_current_conflict(
                current_identity,
                command.expected_current_gate_id,
                None,
            )
    elif current.id != command.expected_current_gate_id:
        _raise_current_conflict(
            current_identity,
            command.expected_current_gate_id,
            current.id,
        )
    elif (
        current.decision_status == DecisionGateStatus.REVOKED.value
        and command.decision_status is DecisionGateStatus.REVOKED
    ):
        raise_business_error(
            "DECISION_GATE_ALREADY_REVOKED",
            "Decision gate is already revoked",
            details={"current_gate_id": current.id},
            status_code=409,
        )

    row = CustomerDecisionGate(
        id=str(uuid4()),
        gate_code=command.gate_code.value,
        scope_key=command.scope_key,
        decision_value=command.decision_value,
        decision_status=command.decision_status.value,
        source_reference=command.source_reference,
        source_version=command.source_version,
        confirmed_by=command.confirmed_by,
        effective_at=command.effective_at,
        supersedes_gate_id=current.id if current is not None else None,
        decision_snapshot=snapshot,
        idempotency_key=command.idempotency_key,
        current_identity_key=current_identity,
    )
    nested_transaction = transaction.begin_nested()
    try:
        with nested_transaction:
            if current is not None:
                current.current_identity_key = None
                transaction.flush()
            transaction.add(row)
            transaction.flush()
    except IntegrityError:
        winner = _idempotency_row(transaction, command.idempotency_key)
        if winner is not None:
            return _reuse_or_conflict(winner, snapshot, command.idempotency_key)
        current_winner = _current_row(
            transaction,
            current_identity,
            command.expected_current_gate_id,
        )
        if current_winner is not None and current_winner.id != command.expected_current_gate_id:
            _raise_current_conflict(
                current_identity,
                command.expected_current_gate_id,
                current_winner.id,
            )
        raise_business_error(
            "DECISION_GATE_WRITE_CONFLICT",
            "Decision gate write conflict",
            details={
                "idempotency_key": command.idempotency_key,
                "current_identity_key": current_identity,
            },
            status_code=409,
        )

    return _result(row, DecisionGateRecordDisposition.CREATED)


def _read_invalid(field: str) -> None:
    raise_business_error(
        "DECISION_GATE_INVALID",
        "Invalid decision gate read input",
        details={"field": field},
        status_code=400,
    )


def _read_candidates(command: ResolveDecisionGateCommand) -> tuple[str, ...]:
    gate_code = command.gate_code.value
    if command.gate_code is DecisionGateCode.LEGACY_FORM_CLASS:
        return (
            f"{gate_code}|{command.scope_key}",
            f"{gate_code}|ALL-22",
        )
    if command.scope_key == "GLOBAL":
        return (f"{gate_code}|GLOBAL",)
    return (
        f"{gate_code}|{command.scope_key}",
        f"{gate_code}|GLOBAL",
    )


def _validate_read_command(command: object) -> tuple[ResolveDecisionGateCommand, tuple[str, ...]]:
    if type(command) is not ResolveDecisionGateCommand:
        _read_invalid("command")
    if type(command.gate_code) is not DecisionGateCode:
        _read_invalid("gate_code")

    scope_key = command.scope_key
    if (
        type(scope_key) is not str
        or not scope_key
        or scope_key != scope_key.strip()
        or "\x00" in scope_key
    ):
        _read_invalid("scope_key")
    if command.gate_code is DecisionGateCode.LEGACY_FORM_CLASS:
        if scope_key not in _LEGACY_FORM_KEYS:
            _read_invalid("scope_key")
    elif scope_key != "GLOBAL":
        if not scope_key.startswith("case:"):
            _read_invalid("scope_key")
        case_id = scope_key[5:]
        if (
            not 1 <= len(case_id) <= 36
            or "|" in case_id
            or any(character.isspace() for character in case_id)
        ):
            _read_invalid("scope_key")

    if type(command.as_of) is not datetime or command.as_of.utcoffset() is not None:
        _read_invalid("as_of")
    return command, _read_candidates(command)


def _read_error(code: str, message: str, details: dict[str, object]) -> None:
    raise_business_error(code, message, details=details, status_code=409)


def _selected_read_row(
    rows: list[CustomerDecisionGate],
    candidate_identities: tuple[str, ...],
    command: ResolveDecisionGateCommand,
) -> tuple[CustomerDecisionGate, str]:
    for candidate_identity in candidate_identities:
        candidate_rows = [row for row in rows if row.current_identity_key == candidate_identity]
        if len(candidate_rows) > 1:
            _read_error(
                "DECISION_GATE_CANDIDATE_MULTIPLICITY",
                "Decision gate candidate multiplicity",
                {
                    "current_identity_key": candidate_identity,
                    "candidate_count": len(candidate_rows),
                },
            )
    for candidate_identity in candidate_identities:
        candidate_rows = [row for row in rows if row.current_identity_key == candidate_identity]
        if candidate_rows:
            return candidate_rows[0], candidate_identity
    if rows:
        return rows[0], candidate_identities[0]
    _read_error(
        "DECISION_GATE_NOT_FOUND",
        "Decision gate current row not found",
        {"gate_code": command.gate_code.value, "scope_key": command.scope_key},
    )


def _validate_read_identity(
    row: CustomerDecisionGate,
    command: ResolveDecisionGateCommand,
    candidate_identity: str,
) -> str:
    resolved_scope_key = candidate_identity.partition("|")[2]
    if (
        row.gate_code != command.gate_code.value
        or row.scope_key != resolved_scope_key
        or row.current_identity_key != candidate_identity
    ):
        _read_error(
            "DECISION_GATE_CURRENT_IDENTITY_CONFLICT",
            "Decision gate current identity conflict",
            {
                "gate_id": row.id,
                "expected_current_identity_key": candidate_identity,
                "actual_current_identity_key": row.current_identity_key,
                "actual_gate_code": row.gate_code,
                "actual_scope_key": row.scope_key,
            },
        )
    return resolved_scope_key


def _read_decision_value(
    row: CustomerDecisionGate,
    command: ResolveDecisionGateCommand,
    resolved_scope_key: str,
) -> str:
    value = row.decision_value
    if command.gate_code is not DecisionGateCode.LEGACY_FORM_CLASS:
        if type(value) is not str or not value or value != value.strip() or "\x00" in value:
            _read_error(
                "DECISION_GATE_CURRENT_ROW_CORRUPT",
                "Decision gate current row is corrupt",
                {"gate_id": row.id, "field": "decision_value"},
            )
        return value
    if resolved_scope_key != "ALL-22":
        if type(value) is not str or value not in _LEGACY_CLASSIFICATIONS:
            _read_error(
                "DECISION_GATE_CURRENT_ROW_CORRUPT",
                "Decision gate current row is corrupt",
                {"gate_id": row.id, "field": "decision_value"},
            )
        return value

    try:
        parsed = json.loads(value) if type(value) is str else None
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        parsed = None
        canonical = None
    if (
        type(parsed) is not dict
        or set(parsed) != _LEGACY_FORM_KEYS
        or any(
            type(classification) is not str or classification not in _LEGACY_CLASSIFICATIONS
            for classification in parsed.values()
        )
        or canonical != value
    ):
        _read_error(
            "DECISION_GATE_LEGACY_MAP_CORRUPT",
            "Decision gate legacy map is corrupt",
            {"gate_id": row.id, "scope_key": "ALL-22"},
        )
    return parsed[command.scope_key]


def resolve_decision_gate(
    command: ResolveDecisionGateCommand,
    transaction: Session,
) -> DecisionGateReadResult:
    command, candidate_identities = _validate_read_command(command)
    with transaction.no_autoflush:
        rows = list(
            transaction.execute(
                select(CustomerDecisionGate).where(
                    CustomerDecisionGate.current_identity_key.in_(candidate_identities)
                )
            )
            .scalars()
            .all()
        )
    row, selected_identity = _selected_read_row(rows, candidate_identities, command)
    resolved_scope_key = _validate_read_identity(row, command, selected_identity)

    if row.decision_status == DecisionGateStatus.REVOKED.value:
        _read_error(
            "DECISION_GATE_REVOKED",
            "Decision gate is revoked",
            {"gate_id": row.id, "resolved_scope_key": resolved_scope_key},
        )
    if row.decision_status != DecisionGateStatus.CONFIRMED.value:
        _read_error(
            "DECISION_GATE_CURRENT_ROW_CORRUPT",
            "Decision gate current row is corrupt",
            {"gate_id": row.id, "field": "decision_status"},
        )
    if type(row.effective_at) is not datetime or row.effective_at.utcoffset() is not None:
        _read_error(
            "DECISION_GATE_CURRENT_ROW_CORRUPT",
            "Decision gate current row is corrupt",
            {"gate_id": row.id, "field": "effective_at"},
        )
    if row.effective_at > command.as_of:
        _read_error(
            "DECISION_GATE_NOT_EFFECTIVE",
            "Decision gate is not effective",
            {
                "gate_id": row.id,
                "effective_at": row.effective_at.isoformat(timespec="microseconds"),
                "as_of": command.as_of.isoformat(timespec="microseconds"),
            },
        )

    decision_value = _read_decision_value(row, command, resolved_scope_key)
    return DecisionGateReadResult(
        gate_id=row.id,
        gate_code=command.gate_code,
        requested_scope_key=command.scope_key,
        resolved_scope_key=resolved_scope_key,
        decision_value=decision_value,
        source_reference=row.source_reference,
        source_version=row.source_version,
        confirmed_by=row.confirmed_by,
        effective_at=row.effective_at,
    )
