from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.auth.models import T_User
from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateReadResult,
    ResolveDecisionGateCommand,
    resolve_decision_gate,
)
from app.modules.system.models import GrantEvidenceSourceConfig, GrantEvidenceSourceRecord


class GrantEvidenceScope(str, Enum):
    GRANT_ANNOUNCEMENT = "GRANT_ANNOUNCEMENT"
    PATENT_REGISTER = "PATENT_REGISTER"


class GrantEvidenceSourceReferenceKind(str, Enum):
    DATA = "DATA"
    QUERY_CHANNEL = "QUERY_CHANNEL"
    FILE = "FILE"


class GrantEvidenceSourceReviewDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class GrantEvidenceSourceDisposition(str, Enum):
    CREATED = "CREATED"
    CHANGED = "CHANGED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterGrantEvidenceSourceCommand:
    source_code: str
    source_version: str
    evidence_scope: GrantEvidenceScope
    source_reference_kind: GrantEvidenceSourceReferenceKind
    source_reference_value: str
    acquisition_method: str
    effective_from: datetime
    effective_to: datetime | None
    supersedes_source_id: str | None
    actor_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewGrantEvidenceSourceCommand:
    source_record_id: str
    decision: GrantEvidenceSourceReviewDecision
    reviewer_id: str
    reviewed_at: datetime
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivateGrantEvidenceSourceCommand:
    source_record_id: str
    actor_id: str
    activated_at: datetime
    expected_current_source_id: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RetireGrantEvidenceSourceCommand:
    source_record_id: str
    actor_id: str
    retired_at: datetime
    expected_current_source_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishGrantEvidenceSourceConfigCommand:
    evidence_scope: GrantEvidenceScope
    source_record_id: str
    config_version: str
    effective_from: datetime
    effective_to: datetime | None
    selected_by: str
    published_at: datetime
    selection_reason: str
    expected_current_config_id: str | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RevokeGrantEvidenceSourceConfigCommand:
    evidence_scope: GrantEvidenceScope
    config_version: str
    effective_from: datetime
    selected_by: str
    published_at: datetime
    selection_reason: str
    expected_current_config_id: str
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveGrantEvidenceSourceCommand:
    evidence_scope: GrantEvidenceScope
    as_of: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceSourceRecordResult:
    source_record_id: str
    review_status: str
    activation_status: str
    source_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantEvidenceSourceDisposition


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceSourceConfigResult:
    config_id: str
    config_status: str
    config_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantEvidenceSourceDisposition


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceSourceResolution:
    gate_id: str
    config_id: str
    config_snapshot_hash: str
    source_record_id: str
    evidence_scope: GrantEvidenceScope
    source_code: str
    source_version: str
    source_snapshot_hash: str
    source_reference_kind: GrantEvidenceSourceReferenceKind
    source_reference_value: str
    acquisition_method: str
    effective_from: datetime
    effective_to: datetime | None


_GATE_CODE = "DG-GRANT-EVIDENCE-SOURCE"
_SCOPE_KEY = "GLOBAL"
_DECISION_VALUE = "APPROVED_POLICY"
_DECISION_SOURCE = "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
_DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
_SOURCE_SCHEMA = "CNIPA_GRANT_EVIDENCE_SOURCE_V1"
_CONFIG_SCHEMA = "CNIPA_GRANT_EVIDENCE_CONFIG_V1"


def _invalid(field: str) -> None:
    raise_business_error(
        "GRANT_EVIDENCE_SOURCE_INPUT_INVALID",
        "Invalid grant evidence source input",
        details={"field": field},
        status_code=400,
    )


def _conflict() -> None:
    raise_business_error(
        "GRANT_EVIDENCE_SOURCE_CONFLICT",
        "Grant evidence source conflict",
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


def _validate_uuid(value: object, field: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
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


def _validate_interval(start: datetime, end: datetime | None) -> None:
    if end is not None:
        _validate_datetime(end, "effective_to")
        if end <= start:
            _invalid("effective_to")


def _validate_transaction(transaction: object) -> Session:
    if not isinstance(transaction, Session):
        _invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        raise_business_error(
            "GRANT_EVIDENCE_SOURCE_TRANSACTION_DIRTY",
            "Grant evidence source transaction is dirty",
            status_code=409,
        )
    return transaction


def _validate_register(command: object) -> RegisterGrantEvidenceSourceCommand:
    if type(command) is not RegisterGrantEvidenceSourceCommand:
        _invalid("command")
    _validate_string(command.source_code, "source_code", 64)
    _validate_string(command.source_version, "source_version", 128)
    if type(command.evidence_scope) is not GrantEvidenceScope:
        _invalid("evidence_scope")
    if type(command.source_reference_kind) is not GrantEvidenceSourceReferenceKind:
        _invalid("source_reference_kind")
    _validate_string(command.source_reference_value, "source_reference_value", 512)
    _validate_string(command.acquisition_method, "acquisition_method", 64)
    start = _validate_datetime(command.effective_from, "effective_from")
    _validate_interval(start, command.effective_to)
    _validate_uuid(command.supersedes_source_id, "supersedes_source_id", optional=True)
    _validate_uuid(command.actor_id, "actor_id")
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    return command


def _validate_review(command: object) -> ReviewGrantEvidenceSourceCommand:
    if type(command) is not ReviewGrantEvidenceSourceCommand:
        _invalid("command")
    _validate_uuid(command.source_record_id, "source_record_id")
    if type(command.decision) is not GrantEvidenceSourceReviewDecision:
        _invalid("decision")
    _validate_uuid(command.reviewer_id, "reviewer_id")
    _validate_datetime(command.reviewed_at, "reviewed_at")
    _validate_string(command.reason, "reason", 4096)
    return command


def _validate_activate(command: object) -> ActivateGrantEvidenceSourceCommand:
    if type(command) is not ActivateGrantEvidenceSourceCommand:
        _invalid("command")
    _validate_uuid(command.source_record_id, "source_record_id")
    _validate_uuid(command.actor_id, "actor_id")
    _validate_datetime(command.activated_at, "activated_at")
    _validate_uuid(
        command.expected_current_source_id,
        "expected_current_source_id",
        optional=True,
    )
    return command


def _validate_retire(command: object) -> RetireGrantEvidenceSourceCommand:
    if type(command) is not RetireGrantEvidenceSourceCommand:
        _invalid("command")
    _validate_uuid(command.source_record_id, "source_record_id")
    _validate_uuid(command.actor_id, "actor_id")
    _validate_datetime(command.retired_at, "retired_at")
    _validate_uuid(command.expected_current_source_id, "expected_current_source_id")
    return command


def _validate_publish(command: object) -> PublishGrantEvidenceSourceConfigCommand:
    if type(command) is not PublishGrantEvidenceSourceConfigCommand:
        _invalid("command")
    if type(command.evidence_scope) is not GrantEvidenceScope:
        _invalid("evidence_scope")
    _validate_uuid(command.source_record_id, "source_record_id")
    _validate_string(command.config_version, "config_version", 128)
    start = _validate_datetime(command.effective_from, "effective_from")
    _validate_interval(start, command.effective_to)
    _validate_uuid(command.selected_by, "selected_by")
    _validate_datetime(command.published_at, "published_at")
    _validate_string(command.selection_reason, "selection_reason", 4096)
    _validate_uuid(
        command.expected_current_config_id,
        "expected_current_config_id",
        optional=True,
    )
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    return command


def _validate_revoke(command: object) -> RevokeGrantEvidenceSourceConfigCommand:
    if type(command) is not RevokeGrantEvidenceSourceConfigCommand:
        _invalid("command")
    if type(command.evidence_scope) is not GrantEvidenceScope:
        _invalid("evidence_scope")
    _validate_string(command.config_version, "config_version", 128)
    _validate_datetime(command.effective_from, "effective_from")
    _validate_uuid(command.selected_by, "selected_by")
    _validate_datetime(command.published_at, "published_at")
    _validate_string(command.selection_reason, "selection_reason", 4096)
    _validate_uuid(command.expected_current_config_id, "expected_current_config_id")
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    return command


def _validate_resolve(command: object) -> ResolveGrantEvidenceSourceCommand:
    if type(command) is not ResolveGrantEvidenceSourceCommand:
        _invalid("command")
    if type(command.evidence_scope) is not GrantEvidenceScope:
        _invalid("evidence_scope")
    _validate_datetime(command.as_of, "as_of")
    return command


def _canonical_json(value: dict[str, object]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _source_snapshot(command: RegisterGrantEvidenceSourceCommand) -> str:
    return _canonical_json(
        {
            "acquisition_method": command.acquisition_method,
            "effective_from": command.effective_from.isoformat(timespec="microseconds"),
            "effective_to": (
                command.effective_to.isoformat(timespec="microseconds")
                if command.effective_to is not None
                else None
            ),
            "evidence_scope": command.evidence_scope.value,
            "schema_version": _SOURCE_SCHEMA,
            "source_authority": "CNIPA",
            "source_code": command.source_code,
            "source_reference_kind": command.source_reference_kind.value,
            "source_reference_value": command.source_reference_value,
            "source_version": command.source_version,
        }
    )


def _expected_source_snapshot(row: GrantEvidenceSourceRecord) -> str:
    if type(row.effective_from) is not datetime or row.effective_from.utcoffset() is not None:
        _conflict()
    if row.effective_to is not None and (
        type(row.effective_to) is not datetime
        or row.effective_to.utcoffset() is not None
        or row.effective_to <= row.effective_from
    ):
        _conflict()
    return _canonical_json(
        {
            "acquisition_method": row.acquisition_method,
            "effective_from": row.effective_from.isoformat(timespec="microseconds"),
            "effective_to": (
                row.effective_to.isoformat(timespec="microseconds")
                if row.effective_to is not None
                else None
            ),
            "evidence_scope": row.evidence_scope,
            "schema_version": _SOURCE_SCHEMA,
            "source_authority": row.source_authority,
            "source_code": row.source_code,
            "source_reference_kind": row.source_reference_kind,
            "source_reference_value": row.source_reference_value,
            "source_version": row.source_version,
        }
    )


def _validate_source_canonical(row: GrantEvidenceSourceRecord) -> None:
    expected = _expected_source_snapshot(row)
    if (
        row.source_authority != "CNIPA"
        or row.evidence_scope not in {item.value for item in GrantEvidenceScope}
        or row.source_reference_kind
        not in {item.value for item in GrantEvidenceSourceReferenceKind}
        or row.source_snapshot != expected
        or row.source_snapshot_hash != _hash(expected)
    ):
        _conflict()


def _config_snapshot(
    *,
    evidence_scope: str,
    source_record_id: str,
    source_version: str,
    source_snapshot_hash: str,
    config_version: str,
    config_status: str,
    effective_from: datetime,
    effective_to: datetime | None,
    selected_by: str,
    published_at: datetime,
    selection_reason: str,
    expected_current_config_id: str | None,
) -> str:
    return _canonical_json(
        {
            "config_status": config_status,
            "config_version": config_version,
            "effective_from": effective_from.isoformat(timespec="microseconds"),
            "effective_to": (
                effective_to.isoformat(timespec="microseconds")
                if effective_to is not None
                else None
            ),
            "evidence_scope": evidence_scope,
            "expected_current_config_id": expected_current_config_id,
            "gate_code": _GATE_CODE,
            "published_at": published_at.isoformat(timespec="microseconds"),
            "schema_version": _CONFIG_SCHEMA,
            "scope_key": _SCOPE_KEY,
            "selected_by": selected_by,
            "selection_reason": selection_reason,
            "source_record_id": source_record_id,
            "source_snapshot_hash": source_snapshot_hash,
            "source_version": source_version,
        }
    )


def _expected_config_snapshot(row: GrantEvidenceSourceConfig) -> str:
    if (
        type(row.effective_from) is not datetime
        or row.effective_from.utcoffset() is not None
        or type(row.published_at) is not datetime
        or row.published_at.utcoffset() is not None
        or (
            row.effective_to is not None
            and (
                type(row.effective_to) is not datetime
                or row.effective_to.utcoffset() is not None
                or row.effective_to <= row.effective_from
            )
        )
    ):
        _conflict()
    try:
        snapshot = json.loads(row.config_snapshot)
        source_version = snapshot["source_version"]
        source_snapshot_hash = snapshot["source_snapshot_hash"]
    except (TypeError, ValueError, KeyError):
        _conflict()
    if type(source_version) is not str or type(source_snapshot_hash) is not str:
        _conflict()
    return _config_snapshot(
        evidence_scope=row.evidence_scope,
        source_record_id=row.source_record_id,
        source_version=source_version,
        source_snapshot_hash=source_snapshot_hash,
        config_version=row.config_version,
        config_status=row.config_status,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        selected_by=row.selected_by,
        published_at=row.published_at,
        selection_reason=row.selection_reason,
        expected_current_config_id=row.supersedes_config_id,
    )


def _validate_config_canonical(row: GrantEvidenceSourceConfig) -> None:
    expected = _expected_config_snapshot(row)
    if (
        row.gate_code != _GATE_CODE
        or row.scope_key != _SCOPE_KEY
        or row.evidence_scope not in {item.value for item in GrantEvidenceScope}
        or row.config_status not in {"ACTIVE", "REVOKED"}
        or row.config_snapshot != expected
        or row.config_snapshot_hash != _hash(expected)
    ):
        _conflict()


def _source_result(
    row: GrantEvidenceSourceRecord,
    disposition: GrantEvidenceSourceDisposition,
) -> GrantEvidenceSourceRecordResult:
    return GrantEvidenceSourceRecordResult(
        source_record_id=row.id,
        review_status=row.review_status,
        activation_status=row.activation_status,
        source_snapshot_hash=row.source_snapshot_hash,
        current_identity_key=row.current_identity_key,
        disposition=disposition,
    )


def _config_result(
    row: GrantEvidenceSourceConfig,
    disposition: GrantEvidenceSourceDisposition,
) -> GrantEvidenceSourceConfigResult:
    return GrantEvidenceSourceConfigResult(
        config_id=row.id,
        config_status=row.config_status,
        config_snapshot_hash=row.config_snapshot_hash,
        current_identity_key=row.current_identity_key,
        disposition=disposition,
    )


def _one_or_none(rows: list[object]) -> object | None:
    if len(rows) > 1:
        _conflict()
    return rows[0] if rows else None


def _user_exists(transaction: Session, user_id: str) -> None:
    if transaction.scalar(select(T_User.id).where(T_User.id == user_id)) is None:
        _conflict()


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    if not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def _gate(transaction: Session, as_of: datetime) -> DecisionGateReadResult:
    result = resolve_decision_gate(
        ResolveDecisionGateCommand(
            gate_code=DecisionGateCode.GRANT_EVIDENCE_SOURCE,
            scope_key=_SCOPE_KEY,
            as_of=as_of,
        ),
        transaction,
    )
    if (
        result.gate_code is not DecisionGateCode.GRANT_EVIDENCE_SOURCE
        or result.resolved_scope_key != _SCOPE_KEY
        or result.decision_value != _DECISION_VALUE
        or result.source_reference != _DECISION_SOURCE
        or result.source_version != _DECISION_VERSION
    ):
        _conflict()
    return result


def _registration_replay(
    row: GrantEvidenceSourceRecord,
    command: RegisterGrantEvidenceSourceCommand,
    snapshot: str,
) -> GrantEvidenceSourceRecordResult:
    _validate_source_canonical(row)
    if (
        row.source_snapshot != snapshot
        or row.supersedes_source_id != command.supersedes_source_id
        or row.created_by != command.actor_id
    ):
        _conflict()
    return _source_result(row, GrantEvidenceSourceDisposition.REUSED)


def register_grant_evidence_source(
    command: RegisterGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult:
    command = _validate_register(command)
    transaction = _validate_transaction(transaction)
    snapshot = _source_snapshot(command)
    with transaction.no_autoflush:
        _user_exists(transaction, command.actor_id)
        replay = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantEvidenceSourceRecord).where(
                        GrantEvidenceSourceRecord.idempotency_key == command.idempotency_key
                    )
                )
            )
        )
        if replay is not None:
            return _registration_replay(replay, command, snapshot)
        if command.supersedes_source_id is not None:
            predecessor = transaction.get(GrantEvidenceSourceRecord, command.supersedes_source_id)
            if (
                predecessor is None
                or predecessor.source_authority != "CNIPA"
                or predecessor.evidence_scope != command.evidence_scope.value
                or predecessor.source_code != command.source_code
            ):
                _conflict()
            _validate_source_canonical(predecessor)

    row = GrantEvidenceSourceRecord(
        id=str(uuid4()),
        source_authority="CNIPA",
        source_code=command.source_code,
        source_version=command.source_version,
        evidence_scope=command.evidence_scope.value,
        source_reference_kind=command.source_reference_kind.value,
        source_reference_value=command.source_reference_value,
        acquisition_method=command.acquisition_method,
        effective_from=command.effective_from,
        effective_to=command.effective_to,
        source_snapshot=snapshot,
        source_snapshot_hash=_hash(snapshot),
        review_status="PENDING",
        reviewed_by=None,
        reviewed_at=None,
        review_reason=None,
        activation_status="INACTIVE",
        activated_by=None,
        activated_at=None,
        supersedes_source_id=command.supersedes_source_id,
        current_identity_key=None,
        idempotency_key=command.idempotency_key,
        created_by=command.actor_id,
        updated_by=command.actor_id,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            transaction.add(row)
            transaction.flush([row])
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            replay = _one_or_none(
                list(
                    transaction.scalars(
                        select(GrantEvidenceSourceRecord).where(
                            GrantEvidenceSourceRecord.idempotency_key == command.idempotency_key
                        )
                    )
                )
            )
            if replay is not None:
                return _registration_replay(replay, command, snapshot)
        _conflict()
    return _source_result(row, GrantEvidenceSourceDisposition.CREATED)


def review_grant_evidence_source(
    command: ReviewGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult:
    command = _validate_review(command)
    transaction = _validate_transaction(transaction)
    with transaction.no_autoflush:
        row = transaction.get(GrantEvidenceSourceRecord, command.source_record_id)
        if row is None:
            _conflict()
        _validate_source_canonical(row)
        _user_exists(transaction, command.reviewer_id)
        if row.review_status in {"APPROVED", "REJECTED"}:
            if (
                row.review_status == command.decision.value
                and row.reviewed_by == command.reviewer_id
                and row.reviewed_at == command.reviewed_at
                and row.review_reason == command.reason
            ):
                return _source_result(row, GrantEvidenceSourceDisposition.REUSED)
            _conflict()
        if (
            row.review_status != "PENDING"
            or row.reviewed_by is not None
            or row.reviewed_at is not None
            or row.review_reason is not None
            or row.activation_status != "INACTIVE"
            or row.created_by == command.reviewer_id
        ):
            _conflict()

    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            result = transaction.execute(
                update(GrantEvidenceSourceRecord)
                .where(
                    GrantEvidenceSourceRecord.id == row.id,
                    GrantEvidenceSourceRecord.review_status == "PENDING",
                    GrantEvidenceSourceRecord.reviewed_by.is_(None),
                    GrantEvidenceSourceRecord.reviewed_at.is_(None),
                    GrantEvidenceSourceRecord.review_reason.is_(None),
                    GrantEvidenceSourceRecord.activation_status == "INACTIVE",
                )
                .values(
                    review_status=command.decision.value,
                    reviewed_by=command.reviewer_id,
                    reviewed_at=command.reviewed_at,
                    review_reason=command.reason,
                    updated_by=command.reviewer_id,
                    updated_at=command.reviewed_at,
                )
            )
            if result.rowcount != 1:
                _conflict()
            transaction.flush()
    except IntegrityError:
        transaction.expire_all()
        _conflict()
    transaction.expire(row)
    return _source_result(row, GrantEvidenceSourceDisposition.CHANGED)


def _source_current_identity(row: GrantEvidenceSourceRecord) -> str:
    return f"CNIPA|{row.evidence_scope}|{row.source_code}"


def _activation_replay(
    row: GrantEvidenceSourceRecord,
    command: ActivateGrantEvidenceSourceCommand,
    transaction: Session,
) -> GrantEvidenceSourceRecordResult:
    identity = _source_current_identity(row)
    if (
        row.activation_status not in {"ACTIVE", "RETIRED"}
        or row.review_status != "APPROVED"
        or row.reviewed_by is None
        or row.reviewed_by == row.created_by
        or type(row.reviewed_at) is not datetime
        or row.reviewed_at.utcoffset() is not None
        or not row.review_reason
        or row.activated_by != command.actor_id
        or row.activated_at != command.activated_at
        or row.supersedes_source_id != command.expected_current_source_id
        or (row.activation_status == "ACTIVE" and row.current_identity_key != identity)
        or (row.activation_status == "RETIRED" and row.current_identity_key is not None)
    ):
        _conflict()
    _validate_source_canonical(row)
    if row.supersedes_source_id is not None:
        predecessor = transaction.get(GrantEvidenceSourceRecord, row.supersedes_source_id)
        if (
            predecessor is None
            or predecessor.source_authority != row.source_authority
            or predecessor.evidence_scope != row.evidence_scope
            or predecessor.source_code != row.source_code
            or predecessor.review_status != "APPROVED"
            or predecessor.activation_status != "RETIRED"
            or predecessor.current_identity_key is not None
        ):
            _conflict()
        _validate_source_canonical(predecessor)
    return _source_result(row, GrantEvidenceSourceDisposition.REUSED)


def activate_grant_evidence_source(
    command: ActivateGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult:
    command = _validate_activate(command)
    transaction = _validate_transaction(transaction)
    with transaction.no_autoflush:
        row = transaction.get(GrantEvidenceSourceRecord, command.source_record_id)
        if row is None:
            _conflict()
        _user_exists(transaction, command.actor_id)
        if row.activation_status in {"ACTIVE", "RETIRED"}:
            return _activation_replay(row, command, transaction)
        _validate_source_canonical(row)
        if (
            row.review_status != "APPROVED"
            or row.reviewed_by is None
            or row.reviewed_at is None
            or not row.review_reason
            or row.activation_status != "INACTIVE"
            or row.activated_by is not None
            or row.activated_at is not None
            or row.current_identity_key is not None
            or row.supersedes_source_id != command.expected_current_source_id
        ):
            _conflict()
        identity = _source_current_identity(row)
        current = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantEvidenceSourceRecord).where(
                        GrantEvidenceSourceRecord.current_identity_key == identity
                    )
                )
            )
        )
        actual_current_id = current.id if current is not None else None
        if actual_current_id != command.expected_current_source_id:
            _conflict()
        if current is not None:
            _validate_source_canonical(current)
            if (
                current.id != row.supersedes_source_id
                or current.source_authority != row.source_authority
                or current.evidence_scope != row.evidence_scope
                or current.source_code != row.source_code
                or current.review_status != "APPROVED"
                or current.activation_status != "ACTIVE"
                or current.current_identity_key != identity
            ):
                _conflict()

    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            if current is not None:
                predecessor_result = transaction.execute(
                    update(GrantEvidenceSourceRecord)
                    .where(
                        GrantEvidenceSourceRecord.id == current.id,
                        GrantEvidenceSourceRecord.activation_status == "ACTIVE",
                        GrantEvidenceSourceRecord.current_identity_key == identity,
                    )
                    .values(
                        activation_status="RETIRED",
                        current_identity_key=None,
                        updated_by=command.actor_id,
                        updated_at=command.activated_at,
                    )
                )
                if predecessor_result.rowcount != 1:
                    _conflict()
            target_result = transaction.execute(
                update(GrantEvidenceSourceRecord)
                .where(
                    GrantEvidenceSourceRecord.id == row.id,
                    GrantEvidenceSourceRecord.review_status == "APPROVED",
                    GrantEvidenceSourceRecord.activation_status == "INACTIVE",
                    GrantEvidenceSourceRecord.current_identity_key.is_(None),
                )
                .values(
                    activation_status="ACTIVE",
                    activated_by=command.actor_id,
                    activated_at=command.activated_at,
                    current_identity_key=identity,
                    updated_by=command.actor_id,
                    updated_at=command.activated_at,
                )
            )
            if target_result.rowcount != 1:
                _conflict()
            transaction.flush()
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            winner = transaction.get(GrantEvidenceSourceRecord, command.source_record_id)
            if winner is not None:
                return _activation_replay(winner, command, transaction)
        _conflict()
    transaction.expire_all()
    row = transaction.get(GrantEvidenceSourceRecord, command.source_record_id)
    if row is None:
        _conflict()
    return _source_result(row, GrantEvidenceSourceDisposition.CHANGED)


def retire_grant_evidence_source(
    command: RetireGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceRecordResult:
    command = _validate_retire(command)
    transaction = _validate_transaction(transaction)
    if command.expected_current_source_id != command.source_record_id:
        _conflict()
    with transaction.no_autoflush:
        row = transaction.get(GrantEvidenceSourceRecord, command.source_record_id)
        if row is None:
            _conflict()
        _validate_source_canonical(row)
        identity = _source_current_identity(row)
        if (
            row.review_status != "APPROVED"
            or row.activation_status != "ACTIVE"
            or row.current_identity_key != identity
            or row.activated_by is None
            or row.activated_at is None
        ):
            _conflict()
        _user_exists(transaction, command.actor_id)

    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            result = transaction.execute(
                update(GrantEvidenceSourceRecord)
                .where(
                    GrantEvidenceSourceRecord.id == command.expected_current_source_id,
                    GrantEvidenceSourceRecord.activation_status == "ACTIVE",
                    GrantEvidenceSourceRecord.current_identity_key == identity,
                )
                .values(
                    activation_status="RETIRED",
                    current_identity_key=None,
                    updated_by=command.actor_id,
                    updated_at=command.retired_at,
                )
            )
            if result.rowcount != 1:
                _conflict()
            transaction.flush()
    except IntegrityError:
        transaction.expire_all()
        _conflict()
    transaction.expire(row)
    return _source_result(row, GrantEvidenceSourceDisposition.CHANGED)


def _config_replay(
    row: GrantEvidenceSourceConfig,
    expected_snapshot: str,
) -> GrantEvidenceSourceConfigResult:
    _validate_config_canonical(row)
    if row.config_snapshot != expected_snapshot:
        _conflict()
    return _config_result(row, GrantEvidenceSourceDisposition.REUSED)


def _current_config(transaction: Session, identity: str) -> GrantEvidenceSourceConfig | None:
    return _one_or_none(
        list(
            transaction.scalars(
                select(GrantEvidenceSourceConfig).where(
                    GrantEvidenceSourceConfig.current_identity_key == identity
                )
            )
        )
    )


def _validate_actionable_source(
    source: GrantEvidenceSourceRecord,
    evidence_scope: GrantEvidenceScope,
    as_of: datetime,
) -> None:
    _validate_source_canonical(source)
    identity = _source_current_identity(source)
    if (
        source.evidence_scope != evidence_scope.value
        or source.review_status != "APPROVED"
        or source.reviewed_by is None
        or source.reviewed_by == source.created_by
        or type(source.reviewed_at) is not datetime
        or source.reviewed_at.utcoffset() is not None
        or not source.review_reason
        or source.activation_status != "ACTIVE"
        or source.activated_by is None
        or type(source.activated_at) is not datetime
        or source.activated_at.utcoffset() is not None
        or source.current_identity_key != identity
        or not _applicable(source.effective_from, source.effective_to, as_of)
    ):
        _conflict()


def publish_grant_evidence_source_config(
    command: PublishGrantEvidenceSourceConfigCommand, transaction: Session
) -> GrantEvidenceSourceConfigResult:
    command = _validate_publish(command)
    transaction = _validate_transaction(transaction)
    _gate(transaction, command.published_at)
    with transaction.no_autoflush:
        _user_exists(transaction, command.selected_by)
        source = transaction.get(GrantEvidenceSourceRecord, command.source_record_id)
        if source is None:
            _conflict()
        _validate_source_canonical(source)
        snapshot = _config_snapshot(
            evidence_scope=command.evidence_scope.value,
            source_record_id=source.id,
            source_version=source.source_version,
            source_snapshot_hash=source.source_snapshot_hash,
            config_version=command.config_version,
            config_status="ACTIVE",
            effective_from=command.effective_from,
            effective_to=command.effective_to,
            selected_by=command.selected_by,
            published_at=command.published_at,
            selection_reason=command.selection_reason,
            expected_current_config_id=command.expected_current_config_id,
        )
        replay = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantEvidenceSourceConfig).where(
                        GrantEvidenceSourceConfig.idempotency_key == command.idempotency_key
                    )
                )
            )
        )
        if replay is not None:
            return _config_replay(replay, snapshot)
        _validate_actionable_source(source, command.evidence_scope, command.effective_from)
        if source.effective_from > command.effective_from or (
            source.effective_to is not None
            and (command.effective_to is None or source.effective_to < command.effective_to)
        ):
            _conflict()
        identity = f"{_GATE_CODE}|{_SCOPE_KEY}|{command.evidence_scope.value}"
        current = _current_config(transaction, identity)
        actual_current_id = current.id if current is not None else None
        if actual_current_id != command.expected_current_config_id:
            _conflict()
        if current is not None:
            _validate_config_canonical(current)

    row = GrantEvidenceSourceConfig(
        id=str(uuid4()),
        gate_code=_GATE_CODE,
        scope_key=_SCOPE_KEY,
        evidence_scope=command.evidence_scope.value,
        source_record_id=source.id,
        config_version=command.config_version,
        config_status="ACTIVE",
        effective_from=command.effective_from,
        effective_to=command.effective_to,
        selected_by=command.selected_by,
        published_at=command.published_at,
        selection_reason=command.selection_reason,
        supersedes_config_id=command.expected_current_config_id,
        config_snapshot=snapshot,
        config_snapshot_hash=_hash(snapshot),
        idempotency_key=command.idempotency_key,
        current_identity_key=identity,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            if current is not None:
                result = transaction.execute(
                    update(GrantEvidenceSourceConfig)
                    .where(
                        GrantEvidenceSourceConfig.id == command.expected_current_config_id,
                        GrantEvidenceSourceConfig.current_identity_key == identity,
                    )
                    .values(current_identity_key=None)
                )
                if result.rowcount != 1:
                    _conflict()
            transaction.add(row)
            transaction.flush([row])
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            replay = _one_or_none(
                list(
                    transaction.scalars(
                        select(GrantEvidenceSourceConfig).where(
                            GrantEvidenceSourceConfig.idempotency_key == command.idempotency_key
                        )
                    )
                )
            )
            if replay is not None:
                return _config_replay(replay, snapshot)
        _conflict()
    return _config_result(row, GrantEvidenceSourceDisposition.CREATED)


def revoke_grant_evidence_source_config(
    command: RevokeGrantEvidenceSourceConfigCommand, transaction: Session
) -> GrantEvidenceSourceConfigResult:
    command = _validate_revoke(command)
    transaction = _validate_transaction(transaction)
    _gate(transaction, command.published_at)
    with transaction.no_autoflush:
        _user_exists(transaction, command.selected_by)
        replay = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantEvidenceSourceConfig).where(
                        GrantEvidenceSourceConfig.idempotency_key == command.idempotency_key
                    )
                )
            )
        )
        if replay is not None:
            _validate_config_canonical(replay)
            try:
                replay_snapshot = json.loads(replay.config_snapshot)
                expected = _config_snapshot(
                    evidence_scope=command.evidence_scope.value,
                    source_record_id=replay.source_record_id,
                    source_version=replay_snapshot["source_version"],
                    source_snapshot_hash=replay_snapshot["source_snapshot_hash"],
                    config_version=command.config_version,
                    config_status="REVOKED",
                    effective_from=command.effective_from,
                    effective_to=None,
                    selected_by=command.selected_by,
                    published_at=command.published_at,
                    selection_reason=command.selection_reason,
                    expected_current_config_id=command.expected_current_config_id,
                )
            except (TypeError, KeyError):
                _conflict()
            return _config_replay(replay, expected)
        identity = f"{_GATE_CODE}|{_SCOPE_KEY}|{command.evidence_scope.value}"
        current = _current_config(transaction, identity)
        if (
            current is None
            or current.id != command.expected_current_config_id
            or current.config_status != "ACTIVE"
            or current.evidence_scope != command.evidence_scope.value
        ):
            _conflict()
        _validate_config_canonical(current)
        try:
            current_snapshot = json.loads(current.config_snapshot)
            source_version = current_snapshot["source_version"]
            source_snapshot_hash = current_snapshot["source_snapshot_hash"]
        except (TypeError, ValueError, KeyError):
            _conflict()
        source = transaction.get(GrantEvidenceSourceRecord, current.source_record_id)
        if source is None:
            _conflict()
        _validate_actionable_source(source, command.evidence_scope, command.effective_from)
        if (
            source.source_version != source_version
            or source.source_snapshot_hash != source_snapshot_hash
        ):
            _conflict()
        snapshot = _config_snapshot(
            evidence_scope=command.evidence_scope.value,
            source_record_id=current.source_record_id,
            source_version=source_version,
            source_snapshot_hash=source_snapshot_hash,
            config_version=command.config_version,
            config_status="REVOKED",
            effective_from=command.effective_from,
            effective_to=None,
            selected_by=command.selected_by,
            published_at=command.published_at,
            selection_reason=command.selection_reason,
            expected_current_config_id=command.expected_current_config_id,
        )

    row = GrantEvidenceSourceConfig(
        id=str(uuid4()),
        gate_code=_GATE_CODE,
        scope_key=_SCOPE_KEY,
        evidence_scope=command.evidence_scope.value,
        source_record_id=current.source_record_id,
        config_version=command.config_version,
        config_status="REVOKED",
        effective_from=command.effective_from,
        effective_to=None,
        selected_by=command.selected_by,
        published_at=command.published_at,
        selection_reason=command.selection_reason,
        supersedes_config_id=current.id,
        config_snapshot=snapshot,
        config_snapshot_hash=_hash(snapshot),
        idempotency_key=command.idempotency_key,
        current_identity_key=identity,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            result = transaction.execute(
                update(GrantEvidenceSourceConfig)
                .where(
                    GrantEvidenceSourceConfig.id == command.expected_current_config_id,
                    GrantEvidenceSourceConfig.config_status == "ACTIVE",
                    GrantEvidenceSourceConfig.current_identity_key == identity,
                )
                .values(current_identity_key=None)
            )
            if result.rowcount != 1:
                _conflict()
            transaction.add(row)
            transaction.flush([row])
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            replay = _one_or_none(
                list(
                    transaction.scalars(
                        select(GrantEvidenceSourceConfig).where(
                            GrantEvidenceSourceConfig.idempotency_key == command.idempotency_key
                        )
                    )
                )
            )
            if replay is not None:
                return _config_replay(replay, snapshot)
        _conflict()
    return _config_result(row, GrantEvidenceSourceDisposition.CREATED)


def _applicable(start: datetime, end: datetime | None, as_of: datetime) -> bool:
    return start <= as_of and (end is None or as_of < end)


def resolve_grant_evidence_source(
    command: ResolveGrantEvidenceSourceCommand, transaction: Session
) -> GrantEvidenceSourceResolution:
    command = _validate_resolve(command)
    transaction = _validate_transaction(transaction)
    gate = _gate(transaction, command.as_of)
    config_identity = f"{_GATE_CODE}|{_SCOPE_KEY}|{command.evidence_scope.value}"
    with transaction.no_autoflush:
        configs = list(
            transaction.scalars(
                select(GrantEvidenceSourceConfig).where(
                    GrantEvidenceSourceConfig.current_identity_key == config_identity
                )
            )
        )
        if len(configs) != 1:
            _conflict()
        config = configs[0]
        _validate_config_canonical(config)
        if (
            config.config_status != "ACTIVE"
            or config.evidence_scope != command.evidence_scope.value
            or config.current_identity_key != config_identity
            or not _applicable(config.effective_from, config.effective_to, command.as_of)
        ):
            _conflict()
        source = transaction.get(GrantEvidenceSourceRecord, config.source_record_id)
        if source is None:
            _conflict()
        _validate_source_canonical(source)
        source_identity = _source_current_identity(source)
        try:
            config_snapshot = json.loads(config.config_snapshot)
        except (TypeError, ValueError):
            _conflict()
        if (
            source.evidence_scope != command.evidence_scope.value
            or source.review_status != "APPROVED"
            or source.reviewed_by is None
            or source.reviewed_by == source.created_by
            or type(source.reviewed_at) is not datetime
            or not source.review_reason
            or source.activation_status != "ACTIVE"
            or source.activated_by is None
            or type(source.activated_at) is not datetime
            or source.current_identity_key != source_identity
            or config_snapshot.get("source_record_id") != source.id
            or config_snapshot.get("source_version") != source.source_version
            or config_snapshot.get("source_snapshot_hash") != source.source_snapshot_hash
            or not _applicable(source.effective_from, source.effective_to, command.as_of)
        ):
            _conflict()
    return GrantEvidenceSourceResolution(
        gate_id=gate.gate_id,
        config_id=config.id,
        config_snapshot_hash=config.config_snapshot_hash,
        source_record_id=source.id,
        evidence_scope=command.evidence_scope,
        source_code=source.source_code,
        source_version=source.source_version,
        source_snapshot_hash=source.source_snapshot_hash,
        source_reference_kind=GrantEvidenceSourceReferenceKind(source.source_reference_kind),
        source_reference_value=source.source_reference_value,
        acquisition_method=source.acquisition_method,
        effective_from=source.effective_from,
        effective_to=source.effective_to,
    )
