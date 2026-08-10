from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.auth.models import T_User
from app.modules.cases.models import Case
from app.modules.masterdata.clients.models import Client
from app.modules.rbac.service import get_user_permissions
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateReadResult,
    ResolveDecisionGateCommand,
    resolve_decision_gate,
)
from app.modules.system.models import CustomerDecisionGate, FutureAnnuityDraftExceptionRecord


class FutureAnnuityExceptionScope(str, Enum):
    CLIENT = "CLIENT"
    CASE = "CASE"


class FutureAnnuityExceptionRecordType(str, Enum):
    PUBLISHED = "PUBLISHED"
    REVOKED = "REVOKED"


class FutureAnnuityExceptionDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishFutureAnnuityExceptionCommand:
    scope_type: FutureAnnuityExceptionScope
    scope_id: str
    effective_from: datetime
    effective_to: datetime
    record_version: str
    source_reference: str
    source_version: str
    reason: str
    confirmed_by: str
    published_at: datetime
    effective_at: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RevokeFutureAnnuityExceptionCommand:
    target_publication_id: str
    record_version: str
    reason: str
    confirmed_by: str
    published_at: datetime
    effective_at: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveFutureAnnuityExceptionCommand:
    client_id: str
    case_id: str
    as_of: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class FutureAnnuityExceptionRecordResult:
    record_id: str
    record_type: FutureAnnuityExceptionRecordType
    target_publication_id: str | None
    record_version: str
    record_snapshot_hash: str
    disposition: FutureAnnuityExceptionDisposition


@dataclass(frozen=True, slots=True, kw_only=True)
class FutureAnnuityExceptionUseAttestation:
    gate_id: str
    gate_source_reference: str
    gate_source_version: str
    publication_id: str
    publication_snapshot_hash: str
    scope_type: FutureAnnuityExceptionScope
    scope_id: str
    client_id: str
    case_id: str
    effective_from: datetime
    effective_to: datetime
    record_version: str
    source_reference: str
    source_version: str
    confirmed_by: str
    published_at: datetime
    effective_at: datetime
    as_of: datetime


_SCHEMA = "FPMS_FUTURE_ANNUITY_DRAFT_EXCEPTION_V1"
_GATE_SCOPE = "GLOBAL"
_GATE_VALUE = "APPROVED_POLICY"
_DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
_DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
_PERMISSION = "SystemParam.Edit"


def _invalid(field: str) -> None:
    raise_business_error(
        "FUTURE_ANNUITY_EXCEPTION_INPUT_INVALID",
        "后续年费例外输入无效",
        details={"field": field},
        status_code=400,
    )


def _not_found() -> None:
    raise_business_error(
        "FUTURE_ANNUITY_EXCEPTION_NOT_FOUND",
        "未找到后续年费例外",
        status_code=404,
    )


def _conflict() -> None:
    raise_business_error(
        "FUTURE_ANNUITY_EXCEPTION_CONFLICT",
        "后续年费例外冲突",
        status_code=409,
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


def _validate_uuid(value: object, field: str) -> str:
    if type(value) is not str:
        _invalid(field)
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError, TypeError):
        _invalid(field)
    if str(parsed) != value:
        _invalid(field)
    return value


def _validate_datetime(value: object, field: str) -> datetime:
    if type(value) is not datetime or value.utcoffset() is not None:
        _invalid(field)
    return value


def _validate_transaction(transaction: object) -> Session:
    if not isinstance(transaction, Session):
        _invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        raise_business_error(
            "FUTURE_ANNUITY_EXCEPTION_TRANSACTION_DIRTY",
            "后续年费例外事务包含未处理改动",
            status_code=409,
        )
    return transaction


def _validate_publish(command: object) -> PublishFutureAnnuityExceptionCommand:
    if type(command) is not PublishFutureAnnuityExceptionCommand:
        _invalid("command")
    if type(command.scope_type) is not FutureAnnuityExceptionScope:
        _invalid("scope_type")
    _validate_uuid(command.scope_id, "scope_id")
    start = _validate_datetime(command.effective_from, "effective_from")
    end = _validate_datetime(command.effective_to, "effective_to")
    if end <= start:
        _invalid("effective_to")
    _validate_string(command.record_version, "record_version", 128)
    _validate_string(command.source_reference, "source_reference", 512)
    _validate_string(command.source_version, "source_version", 128)
    _validate_string(command.reason, "reason", 4096)
    _validate_uuid(command.confirmed_by, "confirmed_by")
    published_at = _validate_datetime(command.published_at, "published_at")
    effective_at = _validate_datetime(command.effective_at, "effective_at")
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    if max(start, published_at, effective_at) >= end:
        _invalid("effective_to")
    return command


def _validate_revoke(command: object) -> RevokeFutureAnnuityExceptionCommand:
    if type(command) is not RevokeFutureAnnuityExceptionCommand:
        _invalid("command")
    _validate_uuid(command.target_publication_id, "target_publication_id")
    _validate_string(command.record_version, "record_version", 128)
    _validate_string(command.reason, "reason", 4096)
    _validate_uuid(command.confirmed_by, "confirmed_by")
    _validate_datetime(command.published_at, "published_at")
    _validate_datetime(command.effective_at, "effective_at")
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    return command


def _validate_resolve(command: object) -> ResolveFutureAnnuityExceptionCommand:
    if type(command) is not ResolveFutureAnnuityExceptionCommand:
        _invalid("command")
    _validate_uuid(command.client_id, "client_id")
    _validate_uuid(command.case_id, "case_id")
    _validate_datetime(command.as_of, "as_of")
    return command


def _resolve_gate(as_of: datetime, transaction: Session) -> DecisionGateReadResult:
    result = resolve_decision_gate(
        ResolveDecisionGateCommand(
            gate_code=DecisionGateCode.FEE_FUTURE_ANNUITY,
            scope_key=_GATE_SCOPE,
            as_of=as_of,
        ),
        transaction,
    )
    if (
        result.gate_code is not DecisionGateCode.FEE_FUTURE_ANNUITY
        or result.requested_scope_key != _GATE_SCOPE
        or result.resolved_scope_key != _GATE_SCOPE
        or result.decision_value != _GATE_VALUE
        or result.source_reference != _DECISION_SOURCE
        or result.source_version != _DECISION_VERSION
    ):
        _conflict()
    return result


def _require_permission(user_id: str, transaction: Session) -> None:
    user = transaction.get(T_User, user_id)
    if user is None:
        _not_found()
    if user.is_active is not True or _PERMISSION not in get_user_permissions(transaction, user_id):
        _conflict()


def _serialize_and_revalidate_gate(
    gate: DecisionGateReadResult,
    as_of: datetime,
    transaction: Session,
) -> None:
    connection = transaction.connection()
    try:
        if connection.dialect.name == "sqlite":
            driver = connection.connection.driver_connection
            if not driver.in_transaction:
                connection.exec_driver_sql("BEGIN IMMEDIATE")
            else:
                connection.exec_driver_sql(
                    "UPDATE t_future_annuity_draft_exception_record SET id = id WHERE 0"
                )
        else:
            locked_gate_id = transaction.scalar(
                select(CustomerDecisionGate.id)
                .where(CustomerDecisionGate.id == gate.gate_id)
                .with_for_update()
            )
            if locked_gate_id != gate.gate_id:
                _conflict()
    except OperationalError:
        _conflict()
    if _resolve_gate(as_of, transaction) != gate:
        _conflict()


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="microseconds")


def _canonical(payload: dict[str, object]) -> tuple[str, str]:
    snapshot = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return snapshot, hashlib.sha256(snapshot.encode("utf-8")).hexdigest()


def _published_payload(command: PublishFutureAnnuityExceptionCommand) -> dict[str, object]:
    return {
        "schema": _SCHEMA,
        "record_type": FutureAnnuityExceptionRecordType.PUBLISHED.value,
        "scope_type": command.scope_type.value,
        "scope_id": command.scope_id,
        "effective_from": _iso(command.effective_from),
        "effective_to": _iso(command.effective_to),
        "effective_at": _iso(command.effective_at),
        "record_version": command.record_version,
        "source_reference": command.source_reference,
        "source_version": command.source_version,
        "reason": command.reason,
        "confirmed_by": command.confirmed_by,
        "published_at": _iso(command.published_at),
    }


def _revoked_payload(
    command: RevokeFutureAnnuityExceptionCommand,
    target: FutureAnnuityDraftExceptionRecord,
) -> dict[str, object]:
    return {
        "schema": _SCHEMA,
        "record_type": FutureAnnuityExceptionRecordType.REVOKED.value,
        "target_publication_id": command.target_publication_id,
        "effective_at": _iso(command.effective_at),
        "record_version": command.record_version,
        "source_reference": target.source_reference,
        "source_version": target.source_version,
        "reason": command.reason,
        "confirmed_by": command.confirmed_by,
        "published_at": _iso(command.published_at),
    }


def _row_payload(row: FutureAnnuityDraftExceptionRecord) -> dict[str, object]:
    if row.record_type == FutureAnnuityExceptionRecordType.PUBLISHED.value:
        if row.scope_type == FutureAnnuityExceptionScope.CLIENT.value:
            scope_id = row.client_id
            if row.case_id is not None:
                _conflict()
        elif row.scope_type == FutureAnnuityExceptionScope.CASE.value:
            scope_id = row.case_id
            if row.client_id is not None:
                _conflict()
        else:
            _conflict()
        if (
            type(row.effective_from) is not datetime
            or type(row.effective_to) is not datetime
            or row.target_publication_id is not None
            or scope_id is None
        ):
            _conflict()
        return {
            "schema": _SCHEMA,
            "record_type": row.record_type,
            "scope_type": row.scope_type,
            "scope_id": scope_id,
            "effective_from": _iso(row.effective_from),
            "effective_to": _iso(row.effective_to),
            "effective_at": _iso(row.effective_at),
            "record_version": row.record_version,
            "source_reference": row.source_reference,
            "source_version": row.source_version,
            "reason": row.reason,
            "confirmed_by": row.confirmed_by,
            "published_at": _iso(row.published_at),
        }
    if row.record_type == FutureAnnuityExceptionRecordType.REVOKED.value:
        if (
            row.target_publication_id is None
            or row.scope_type is not None
            or row.client_id is not None
            or row.case_id is not None
            or row.effective_from is not None
            or row.effective_to is not None
        ):
            _conflict()
        return {
            "schema": _SCHEMA,
            "record_type": row.record_type,
            "target_publication_id": row.target_publication_id,
            "effective_at": _iso(row.effective_at),
            "record_version": row.record_version,
            "source_reference": row.source_reference,
            "source_version": row.source_version,
            "reason": row.reason,
            "confirmed_by": row.confirmed_by,
            "published_at": _iso(row.published_at),
        }
    _conflict()


def _validate_row(row: FutureAnnuityDraftExceptionRecord) -> None:
    try:
        _validate_uuid(row.id, "record_id")
        _validate_uuid(row.confirmed_by, "confirmed_by")
        _validate_datetime(row.published_at, "published_at")
        _validate_datetime(row.effective_at, "effective_at")
        _validate_string(row.record_version, "record_version", 128)
        _validate_string(row.source_reference, "source_reference", 512)
        _validate_string(row.source_version, "source_version", 128)
        _validate_string(row.reason, "reason", 4096)
        _validate_string(row.idempotency_key, "idempotency_key", 128)
        if row.record_type == FutureAnnuityExceptionRecordType.PUBLISHED.value:
            scope_id = row.client_id if row.client_id is not None else row.case_id
            _validate_uuid(scope_id, "scope_id")
            start = _validate_datetime(row.effective_from, "effective_from")
            end = _validate_datetime(row.effective_to, "effective_to")
            if end <= start or max(start, row.published_at, row.effective_at) >= end:
                _invalid("effective_to")
        elif row.record_type == FutureAnnuityExceptionRecordType.REVOKED.value:
            _validate_uuid(row.target_publication_id, "target_publication_id")
        payload = _row_payload(row)
        snapshot, digest = _canonical(payload)
    except Exception as error:
        if getattr(error, "code", None) == "FUTURE_ANNUITY_EXCEPTION_INPUT_INVALID":
            _conflict()
        raise
    if row.record_snapshot != snapshot or row.record_snapshot_hash != digest:
        _conflict()


def _result(
    row: FutureAnnuityDraftExceptionRecord,
    disposition: FutureAnnuityExceptionDisposition,
) -> FutureAnnuityExceptionRecordResult:
    _validate_row(row)
    return FutureAnnuityExceptionRecordResult(
        record_id=row.id,
        record_type=FutureAnnuityExceptionRecordType(row.record_type),
        target_publication_id=row.target_publication_id,
        record_version=row.record_version,
        record_snapshot_hash=row.record_snapshot_hash,
        disposition=disposition,
    )


def _one(rows: list[FutureAnnuityDraftExceptionRecord]) -> FutureAnnuityDraftExceptionRecord | None:
    if len(rows) > 1:
        _conflict()
    return rows[0] if rows else None


def _by_idempotency(
    transaction: Session, key: str
) -> FutureAnnuityDraftExceptionRecord | None:
    return _one(
        list(
            transaction.scalars(
                select(FutureAnnuityDraftExceptionRecord).where(
                    FutureAnnuityDraftExceptionRecord.idempotency_key == key
                )
            )
        )
    )


def _version_conflicts(transaction: Session, version: str) -> bool:
    return (
        transaction.scalar(
            select(FutureAnnuityDraftExceptionRecord.id).where(
                FutureAnnuityDraftExceptionRecord.record_version == version
            )
        )
        is not None
    )


def _same_snapshot_replay(
    row: FutureAnnuityDraftExceptionRecord | None,
    expected_snapshot: str,
) -> FutureAnnuityExceptionRecordResult | None:
    if row is None:
        return None
    _validate_row(row)
    if row.record_snapshot != expected_snapshot:
        _conflict()
    return _result(row, FutureAnnuityExceptionDisposition.REUSED)


def _scope_exists(
    command: PublishFutureAnnuityExceptionCommand, transaction: Session
) -> tuple[str | None, str | None, str]:
    if command.scope_type is FutureAnnuityExceptionScope.CLIENT:
        if transaction.get(Client, command.scope_id) is None:
            _not_found()
        return command.scope_id, None, command.scope_id
    case = transaction.get(Case, command.scope_id)
    if case is None:
        _not_found()
    if case.client_id is None:
        _conflict()
    return None, command.scope_id, case.client_id


def _revocations(
    publication_id: str, transaction: Session
) -> list[FutureAnnuityDraftExceptionRecord]:
    rows = list(
        transaction.scalars(
            select(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.target_publication_id == publication_id
            )
        )
    )
    if len(rows) > 1:
        _conflict()
    for row in rows:
        _validate_row(row)
    return rows


def _usable_segment_end(
    publication: FutureAnnuityDraftExceptionRecord,
    transaction: Session,
) -> datetime:
    if publication.effective_to is None:
        _conflict()
    revocations = _revocations(publication.id, transaction)
    if not revocations:
        return publication.effective_to
    revocation = revocations[0]
    if (
        revocation.record_type != FutureAnnuityExceptionRecordType.REVOKED.value
        or revocation.source_reference != publication.source_reference
        or revocation.source_version != publication.source_version
    ):
        _conflict()
    return min(publication.effective_to, max(revocation.published_at, revocation.effective_at))


def _overlaps(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    return max(left_start, right_start) < min(left_end, right_end)


def _reject_overlap(
    command: PublishFutureAnnuityExceptionCommand,
    client_id: str,
    transaction: Session,
) -> None:
    proposed_start = max(command.effective_from, command.published_at, command.effective_at)
    if command.scope_type is FutureAnnuityExceptionScope.CLIENT:
        related_case_ids = list(
            transaction.scalars(select(Case.id).where(Case.client_id == client_id))
        )
        relation_filter = (
            (FutureAnnuityDraftExceptionRecord.client_id == client_id)
            | (FutureAnnuityDraftExceptionRecord.case_id.in_(related_case_ids))
        )
    else:
        relation_filter = (
            (FutureAnnuityDraftExceptionRecord.client_id == client_id)
            | (FutureAnnuityDraftExceptionRecord.case_id == command.scope_id)
        )
    publications = list(
        transaction.scalars(
            select(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.record_type
                == FutureAnnuityExceptionRecordType.PUBLISHED.value,
                relation_filter,
            )
        )
    )
    for publication in publications:
        _validate_row(publication)
        existing_start = max(
            publication.effective_from,
            publication.published_at,
            publication.effective_at,
        )
        existing_end = _usable_segment_end(publication, transaction)
        if existing_start >= existing_end:
            continue
        related = False
        if publication.scope_type == FutureAnnuityExceptionScope.CLIENT.value:
            related = publication.client_id == client_id
        elif publication.scope_type == FutureAnnuityExceptionScope.CASE.value:
            case = transaction.get(Case, publication.case_id)
            if case is None or case.client_id is None:
                _conflict()
            related = (
                case.client_id == client_id
                if command.scope_type is FutureAnnuityExceptionScope.CLIENT
                else publication.case_id == command.scope_id
            )
        else:
            _conflict()
        if related and _overlaps(
            proposed_start,
            command.effective_to,
            existing_start,
            existing_end,
        ):
            _conflict()


def _insert(
    row: FutureAnnuityDraftExceptionRecord,
    expected_snapshot: str,
    transaction: Session,
) -> FutureAnnuityExceptionRecordResult:
    connection = transaction.connection()
    if (
        connection.dialect.name == "sqlite"
        and not connection.connection.driver_connection.in_transaction
    ):
        connection.exec_driver_sql("BEGIN")
    try:
        with transaction.begin_nested():
            transaction.add(row)
            transaction.flush()
    except IntegrityError:
        replay = _same_snapshot_replay(
            _by_idempotency(transaction, row.idempotency_key), expected_snapshot
        )
        if replay is not None:
            return replay
        _conflict()
    return _result(row, FutureAnnuityExceptionDisposition.CREATED)


def publish_future_annuity_exception(
    command: PublishFutureAnnuityExceptionCommand,
    transaction: Session,
) -> FutureAnnuityExceptionRecordResult:
    command = _validate_publish(command)
    transaction = _validate_transaction(transaction)
    gate = _resolve_gate(command.published_at, transaction)
    _serialize_and_revalidate_gate(gate, command.published_at, transaction)
    _require_permission(command.confirmed_by, transaction)
    client_id, case_id, related_client_id = _scope_exists(command, transaction)
    payload = _published_payload(command)
    snapshot, digest = _canonical(payload)
    replay = _same_snapshot_replay(
        _by_idempotency(transaction, command.idempotency_key), snapshot
    )
    if replay is not None:
        return replay
    if _version_conflicts(transaction, command.record_version):
        _conflict()
    _reject_overlap(command, related_client_id, transaction)
    row = FutureAnnuityDraftExceptionRecord(
        id=str(uuid4()),
        record_type=FutureAnnuityExceptionRecordType.PUBLISHED.value,
        scope_type=command.scope_type.value,
        client_id=client_id,
        case_id=case_id,
        effective_from=command.effective_from,
        effective_to=command.effective_to,
        target_publication_id=None,
        record_version=command.record_version,
        source_reference=command.source_reference,
        source_version=command.source_version,
        reason=command.reason,
        record_snapshot=snapshot,
        record_snapshot_hash=digest,
        confirmed_by=command.confirmed_by,
        published_at=command.published_at,
        effective_at=command.effective_at,
        idempotency_key=command.idempotency_key,
    )
    return _insert(row, snapshot, transaction)


def revoke_future_annuity_exception(
    command: RevokeFutureAnnuityExceptionCommand,
    transaction: Session,
) -> FutureAnnuityExceptionRecordResult:
    command = _validate_revoke(command)
    transaction = _validate_transaction(transaction)
    gate = _resolve_gate(command.published_at, transaction)
    _serialize_and_revalidate_gate(gate, command.published_at, transaction)
    _require_permission(command.confirmed_by, transaction)
    target = transaction.get(FutureAnnuityDraftExceptionRecord, command.target_publication_id)
    if target is None:
        _not_found()
    _validate_row(target)
    if target.record_type != FutureAnnuityExceptionRecordType.PUBLISHED.value:
        _conflict()
    payload = _revoked_payload(command, target)
    snapshot, digest = _canonical(payload)
    replay = _same_snapshot_replay(
        _by_idempotency(transaction, command.idempotency_key), snapshot
    )
    if replay is not None:
        return replay
    if _version_conflicts(transaction, command.record_version) or _revocations(
        target.id, transaction
    ):
        _conflict()
    row = FutureAnnuityDraftExceptionRecord(
        id=str(uuid4()),
        record_type=FutureAnnuityExceptionRecordType.REVOKED.value,
        scope_type=None,
        client_id=None,
        case_id=None,
        effective_from=None,
        effective_to=None,
        target_publication_id=target.id,
        record_version=command.record_version,
        source_reference=target.source_reference,
        source_version=target.source_version,
        reason=command.reason,
        record_snapshot=snapshot,
        record_snapshot_hash=digest,
        confirmed_by=command.confirmed_by,
        published_at=command.published_at,
        effective_at=command.effective_at,
        idempotency_key=command.idempotency_key,
    )
    return _insert(row, snapshot, transaction)


def resolve_future_annuity_exception(
    command: ResolveFutureAnnuityExceptionCommand,
    transaction: Session,
) -> FutureAnnuityExceptionUseAttestation:
    command = _validate_resolve(command)
    transaction = _validate_transaction(transaction)
    gate = _resolve_gate(command.as_of, transaction)
    if transaction.get(Client, command.client_id) is None:
        _not_found()
    case = transaction.get(Case, command.case_id)
    if case is None:
        _not_found()
    if case.client_id != command.client_id:
        _conflict()
    publications = list(
        transaction.scalars(
            select(FutureAnnuityDraftExceptionRecord).where(
                FutureAnnuityDraftExceptionRecord.record_type
                == FutureAnnuityExceptionRecordType.PUBLISHED.value,
                (
                    (FutureAnnuityDraftExceptionRecord.client_id == command.client_id)
                    | (FutureAnnuityDraftExceptionRecord.case_id == command.case_id)
                ),
            )
        )
    )
    candidates: list[FutureAnnuityDraftExceptionRecord] = []
    for publication in publications:
        _validate_row(publication)
        if publication.effective_from is None or publication.effective_to is None:
            _conflict()
        if not (
            publication.effective_from <= command.as_of < publication.effective_to
            and publication.published_at <= command.as_of
            and publication.effective_at <= command.as_of
        ):
            continue
        revocations = _revocations(publication.id, transaction)
        if revocations:
            revocation = revocations[0]
            if (
                revocation.source_reference != publication.source_reference
                or revocation.source_version != publication.source_version
            ):
                _conflict()
            if revocation.published_at <= command.as_of and revocation.effective_at <= command.as_of:
                continue
        candidates.append(publication)
    if not candidates:
        _not_found()
    if len(candidates) != 1:
        _conflict()
    publication = candidates[0]
    scope_type = FutureAnnuityExceptionScope(publication.scope_type)
    scope_id = publication.client_id if scope_type is FutureAnnuityExceptionScope.CLIENT else publication.case_id
    if scope_id is None:
        _conflict()
    return FutureAnnuityExceptionUseAttestation(
        gate_id=gate.gate_id,
        gate_source_reference=gate.source_reference,
        gate_source_version=gate.source_version,
        publication_id=publication.id,
        publication_snapshot_hash=publication.record_snapshot_hash,
        scope_type=scope_type,
        scope_id=scope_id,
        client_id=command.client_id,
        case_id=command.case_id,
        effective_from=publication.effective_from,
        effective_to=publication.effective_to,
        record_version=publication.record_version,
        source_reference=publication.source_reference,
        source_version=publication.source_version,
        confirmed_by=publication.confirmed_by,
        published_at=publication.published_at,
        effective_at=publication.effective_at,
        as_of=command.as_of,
    )
