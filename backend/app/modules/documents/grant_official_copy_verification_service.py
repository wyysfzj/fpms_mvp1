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

from app.core.errors import BusinessError, raise_business_error
from app.modules.auth.models import T_User, T_UserRole
from app.modules.documents.models import (
    DocAttachment,
    DocumentEvidenceVersion,
    GrantOfficialCopyVerificationEvent,
)
from app.modules.system.grant_evidence_source_service import (
    GrantEvidenceScope,
    GrantEvidenceSourceResolution,
    ResolveGrantEvidenceSourceCommand,
    resolve_grant_evidence_source,
)
from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleResolution,
    ResolveGrantManualReviewRoleConfigCommand,
    resolve_grant_manual_review_role_config,
)


class GrantOfficialCopyEventType(str, Enum):
    ACQUIRED = "ACQUIRED"
    FIRST_VERIFIED = "FIRST_VERIFIED"
    SECOND_VERIFIED = "SECOND_VERIFIED"


class GrantOfficialCopyDisposition(str, Enum):
    CREATED = "CREATED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordGrantOfficialCopyEventCommand:
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    actor_id: str
    action_at: datetime
    reason: str
    original_reference: str | None
    expected_current_event_id: str | None
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantOfficialCopyEventResult:
    event_id: str
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    source_config_id: str
    source_record_id: str
    role_config_id: str
    event_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantOfficialCopyDisposition


_SCHEMA = "CNIPA_GRANT_OFFICIAL_COPY_VERIFICATION_EVENT_V1"
_CURRENT_PREFIX = "GRANT_OFFICIAL_COPY|"
_PREDECESSOR = {
    GrantOfficialCopyEventType.FIRST_VERIFIED: GrantOfficialCopyEventType.ACQUIRED,
    GrantOfficialCopyEventType.SECOND_VERIFIED: GrantOfficialCopyEventType.FIRST_VERIFIED,
}


def _invalid(field: str) -> None:
    raise_business_error(
        "GRANT_OFFICIAL_COPY_EVENT_INPUT_INVALID",
        "Invalid grant official-copy event input",
        details={"field": field},
        status_code=400,
    )


def _conflict() -> None:
    raise_business_error(
        "GRANT_OFFICIAL_COPY_EVENT_CONFLICT",
        "Grant official-copy event conflict",
        status_code=409,
    )


def _validate_uuid(value: object, field: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if type(value) is not str:
        _invalid(field)
    try:
        parsed = UUID(value)
    except (AttributeError, TypeError, ValueError):
        _invalid(field)
    if str(parsed) != value:
        _invalid(field)
    return value


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


def _validate_hash(value: object, field: str, *, length: int = 64) -> str:
    if (
        type(value) is not str
        or len(value) != length
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _conflict()
    return value


def _validate_content_hash(value: object) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or len(value) > 128
    ):
        _conflict()
    return value


def _validate_command(
    command: object,
) -> RecordGrantOfficialCopyEventCommand:
    if type(command) is not RecordGrantOfficialCopyEventCommand:
        _invalid("command")
    _validate_uuid(command.evidence_version_id, "evidence_version_id")
    if type(command.evidence_scope) is not GrantEvidenceScope:
        _invalid("evidence_scope")
    if type(command.event_type) is not GrantOfficialCopyEventType:
        _invalid("event_type")
    _validate_uuid(command.actor_id, "actor_id")
    if type(command.action_at) is not datetime or command.action_at.utcoffset() is not None:
        _invalid("action_at")
    _validate_string(command.reason, "reason", 4096)
    _validate_string(command.idempotency_key, "idempotency_key", 128)
    if command.event_type is GrantOfficialCopyEventType.ACQUIRED:
        _validate_string(command.original_reference, "original_reference", 512)
        if command.expected_current_event_id is not None:
            _invalid("expected_current_event_id")
    else:
        if command.original_reference is not None:
            _invalid("original_reference")
        _validate_uuid(command.expected_current_event_id, "expected_current_event_id")
    return command


def _validate_transaction(transaction: object) -> Session:
    if not isinstance(transaction, Session):
        _invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _conflict()
    return transaction


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


def _event_snapshot(
    *,
    evidence_version_id: str,
    source_config_id: str,
    source_record_id: str,
    role_config_id: str,
    evidence_scope: str,
    event_type: str,
    actor_id: str,
    action_at: datetime,
    reason: str,
    original_reference: str,
    acquisition_method_snapshot: str,
    evidence_content_hash: str,
    source_config_snapshot_hash: str,
    source_snapshot_hash: str,
    role_config_snapshot_hash: str,
    predecessor_event_id: str | None,
) -> str:
    return _canonical_json(
        {
            "acquisition_method_snapshot": acquisition_method_snapshot,
            "action_at": action_at.isoformat(timespec="microseconds"),
            "actor_id": actor_id,
            "event_type": event_type,
            "evidence_content_hash": evidence_content_hash,
            "evidence_scope": evidence_scope,
            "evidence_version_id": evidence_version_id,
            "original_reference": original_reference,
            "predecessor_event_id": predecessor_event_id,
            "reason": reason,
            "role_config_id": role_config_id,
            "role_config_snapshot_hash": role_config_snapshot_hash,
            "schema": _SCHEMA,
            "source_config_id": source_config_id,
            "source_config_snapshot_hash": source_config_snapshot_hash,
            "source_record_id": source_record_id,
            "source_snapshot_hash": source_snapshot_hash,
        }
    )


def _validate_evidence(
    transaction: Session,
    evidence_version_id: str,
) -> DocumentEvidenceVersion:
    evidence = transaction.get(DocumentEvidenceVersion, evidence_version_id)
    if evidence is None:
        _conflict()
    expected_current = f"{evidence.case_id}|{evidence.lineage_key}"
    if (
        evidence.current_identity_key != expected_current
        or evidence.role != "RAW_ATTACHMENT"
        or evidence.state != "FINAL"
        or evidence.review_state != "PENDING"
        or evidence.reviewer_id is not None
        or evidence.reviewed_at is not None
        or evidence.final_submitted_at is not None
    ):
        _conflict()
    content_hash = _validate_content_hash(evidence.content_hash)
    attachment = transaction.get(DocAttachment, evidence.attachment_id)
    if (
        attachment is None
        or attachment.document_id != evidence.document_id
        or attachment.content_hash != content_hash
    ):
        _conflict()
    return evidence


def _resolve_authority(
    command: RecordGrantOfficialCopyEventCommand,
    transaction: Session,
) -> tuple[GrantEvidenceSourceResolution, GrantManualReviewRoleResolution]:
    try:
        source = resolve_grant_evidence_source(
            ResolveGrantEvidenceSourceCommand(
                evidence_scope=command.evidence_scope,
                as_of=command.action_at,
            ),
            transaction,
        )
        roles = resolve_grant_manual_review_role_config(
            ResolveGrantManualReviewRoleConfigCommand(as_of=command.action_at),
            transaction,
        )
    except BusinessError:
        _conflict()
    if (
        type(source) is not GrantEvidenceSourceResolution
        or source.evidence_scope is not command.evidence_scope
        or type(roles) is not GrantManualReviewRoleResolution
    ):
        _conflict()
    for value in (
        source.config_id,
        source.source_record_id,
        roles.config_id,
    ):
        try:
            parsed = UUID(value)
        except (AttributeError, TypeError, ValueError):
            _conflict()
        if str(parsed) != value:
            _conflict()
    _validate_hash(source.config_snapshot_hash, "source_config_snapshot_hash")
    _validate_hash(source.source_snapshot_hash, "source_snapshot_hash")
    _validate_hash(roles.config_snapshot_hash, "role_config_snapshot_hash")
    if (
        type(source.acquisition_method) is not str
        or not source.acquisition_method
        or source.acquisition_method != source.acquisition_method.strip()
        or "\x00" in source.acquisition_method
        or len(source.acquisition_method) > 64
    ):
        _conflict()
    return source, roles


def _required_role_id(
    event_type: GrantOfficialCopyEventType,
    roles: GrantManualReviewRoleResolution,
) -> str:
    if event_type is GrantOfficialCopyEventType.ACQUIRED:
        return roles.official_copy_acquirer_role_id
    if event_type is GrantOfficialCopyEventType.FIRST_VERIFIED:
        return roles.first_verifier_role_id
    return roles.second_verifier_role_id


def _validate_actor(
    transaction: Session,
    actor_id: str,
    role_id: str,
) -> None:
    membership = transaction.scalar(
        select(T_UserRole.user_id)
        .join(T_User, T_User.id == T_UserRole.user_id)
        .where(
            T_UserRole.user_id == actor_id,
            T_UserRole.role_id == role_id,
            T_User.is_active.is_(True),
        )
    )
    if membership != actor_id:
        _conflict()


def _stored_event_type(row: GrantOfficialCopyVerificationEvent) -> GrantOfficialCopyEventType:
    try:
        return GrantOfficialCopyEventType(row.event_type)
    except (TypeError, ValueError):
        _conflict()


def _validate_stored(row: GrantOfficialCopyVerificationEvent) -> None:
    event_type = _stored_event_type(row)
    if (
        row.evidence_scope not in {item.value for item in GrantEvidenceScope}
        or type(row.action_at) is not datetime
        or row.action_at.utcoffset() is not None
        or row.current_identity_key
        not in {None, f"{_CURRENT_PREFIX}{row.evidence_version_id}"}
    ):
        _conflict()
    required_ids = (
        row.id,
        row.evidence_version_id,
        row.source_config_id,
        row.source_record_id,
        row.role_config_id,
        row.actor_id,
    )
    if row.predecessor_event_id is not None:
        required_ids += (row.predecessor_event_id,)
    for value in required_ids:
        try:
            parsed = UUID(value)
        except (AttributeError, TypeError, ValueError):
            _conflict()
        if str(parsed) != value:
            _conflict()
    for value, limit in (
        (row.reason, 4096),
        (row.original_reference, 512),
        (row.acquisition_method_snapshot, 64),
        (row.idempotency_key, 128),
    ):
        if (
            type(value) is not str
            or not value
            or value != value.strip()
            or "\x00" in value
            or len(value) > limit
        ):
            _conflict()
    if event_type is GrantOfficialCopyEventType.ACQUIRED:
        if row.predecessor_event_id is not None:
            _conflict()
    elif row.predecessor_event_id is None:
        _conflict()
    for value, field in (
        (row.source_config_snapshot_hash, "source_config_snapshot_hash"),
        (row.source_snapshot_hash, "source_snapshot_hash"),
        (row.role_config_snapshot_hash, "role_config_snapshot_hash"),
        (row.event_snapshot_hash, "event_snapshot_hash"),
    ):
        _validate_hash(value, field)
    _validate_content_hash(row.evidence_content_hash)
    expected = _event_snapshot(
        evidence_version_id=row.evidence_version_id,
        source_config_id=row.source_config_id,
        source_record_id=row.source_record_id,
        role_config_id=row.role_config_id,
        evidence_scope=row.evidence_scope,
        event_type=row.event_type,
        actor_id=row.actor_id,
        action_at=row.action_at,
        reason=row.reason,
        original_reference=row.original_reference,
        acquisition_method_snapshot=row.acquisition_method_snapshot,
        evidence_content_hash=row.evidence_content_hash,
        source_config_snapshot_hash=row.source_config_snapshot_hash,
        source_snapshot_hash=row.source_snapshot_hash,
        role_config_snapshot_hash=row.role_config_snapshot_hash,
        predecessor_event_id=row.predecessor_event_id,
    )
    if row.event_snapshot != expected or row.event_snapshot_hash != _hash(expected):
        _conflict()


def _validate_chain(
    transaction: Session,
    row: GrantOfficialCopyVerificationEvent,
) -> None:
    seen: set[str] = set()
    current = row
    expected = _stored_event_type(current)
    while True:
        _validate_stored(current)
        if current.id in seen or _stored_event_type(current) is not expected:
            _conflict()
        seen.add(current.id)
        if expected is GrantOfficialCopyEventType.ACQUIRED:
            return
        predecessor = transaction.get(
            GrantOfficialCopyVerificationEvent,
            current.predecessor_event_id,
        )
        expected = _PREDECESSOR[expected]
        if (
            predecessor is None
            or predecessor.evidence_version_id != row.evidence_version_id
            or predecessor.evidence_scope != row.evidence_scope
            or predecessor.source_config_id != row.source_config_id
            or predecessor.source_record_id != row.source_record_id
            or predecessor.source_config_snapshot_hash
            != row.source_config_snapshot_hash
            or predecessor.source_snapshot_hash != row.source_snapshot_hash
            or predecessor.acquisition_method_snapshot
            != row.acquisition_method_snapshot
            or predecessor.evidence_content_hash != row.evidence_content_hash
            or predecessor.original_reference != row.original_reference
        ):
            _conflict()
        current = predecessor


def _validate_source_lineage(
    row: GrantOfficialCopyVerificationEvent,
    source: GrantEvidenceSourceResolution,
) -> None:
    if (
        row.source_config_id != source.config_id
        or row.source_record_id != source.source_record_id
        or row.source_config_snapshot_hash != source.config_snapshot_hash
        or row.source_snapshot_hash != source.source_snapshot_hash
        or row.acquisition_method_snapshot != source.acquisition_method
    ):
        _conflict()


def _one_or_none(rows: list[GrantOfficialCopyVerificationEvent]):
    if len(rows) > 1:
        _conflict()
    return rows[0] if rows else None


def _result(
    row: GrantOfficialCopyVerificationEvent,
    disposition: GrantOfficialCopyDisposition,
) -> GrantOfficialCopyEventResult:
    return GrantOfficialCopyEventResult(
        event_id=row.id,
        evidence_version_id=row.evidence_version_id,
        evidence_scope=GrantEvidenceScope(row.evidence_scope),
        event_type=GrantOfficialCopyEventType(row.event_type),
        source_config_id=row.source_config_id,
        source_record_id=row.source_record_id,
        role_config_id=row.role_config_id,
        event_snapshot_hash=row.event_snapshot_hash,
        current_identity_key=row.current_identity_key,
        disposition=disposition,
    )


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    if not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def record_grant_official_copy_event(
    command: RecordGrantOfficialCopyEventCommand,
    transaction: Session,
) -> GrantOfficialCopyEventResult:
    command = _validate_command(command)
    transaction = _validate_transaction(transaction)
    with transaction.no_autoflush:
        evidence = _validate_evidence(transaction, command.evidence_version_id)
        source, roles = _resolve_authority(command, transaction)
        _validate_actor(
            transaction,
            command.actor_id,
            _required_role_id(command.event_type, roles),
        )
        predecessor = None
        original_reference = command.original_reference
        if command.event_type is not GrantOfficialCopyEventType.ACQUIRED:
            predecessor = transaction.get(
                GrantOfficialCopyVerificationEvent,
                command.expected_current_event_id,
            )
            if (
                predecessor is None
                or predecessor.evidence_version_id != evidence.id
                or predecessor.evidence_scope != command.evidence_scope.value
                or _stored_event_type(predecessor) is not _PREDECESSOR[command.event_type]
            ):
                _conflict()
            _validate_chain(transaction, predecessor)
            _validate_source_lineage(predecessor, source)
            original_reference = predecessor.original_reference
            if (
                predecessor.evidence_content_hash != evidence.content_hash
                or (
                    command.event_type is GrantOfficialCopyEventType.SECOND_VERIFIED
                    and predecessor.actor_id == command.actor_id
                )
            ):
                _conflict()
        snapshot = _event_snapshot(
            evidence_version_id=evidence.id,
            source_config_id=source.config_id,
            source_record_id=source.source_record_id,
            role_config_id=roles.config_id,
            evidence_scope=command.evidence_scope.value,
            event_type=command.event_type.value,
            actor_id=command.actor_id,
            action_at=command.action_at,
            reason=command.reason,
            original_reference=original_reference,
            acquisition_method_snapshot=source.acquisition_method,
            evidence_content_hash=evidence.content_hash,
            source_config_snapshot_hash=source.config_snapshot_hash,
            source_snapshot_hash=source.source_snapshot_hash,
            role_config_snapshot_hash=roles.config_snapshot_hash,
            predecessor_event_id=(predecessor.id if predecessor is not None else None),
        )
        replay = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantOfficialCopyVerificationEvent).where(
                        GrantOfficialCopyVerificationEvent.idempotency_key
                        == command.idempotency_key
                    )
                )
            )
        )
        if replay is not None:
            _validate_stored(replay)
            if replay.event_snapshot != snapshot:
                _conflict()
            return _result(replay, GrantOfficialCopyDisposition.REUSED)
        same_stage = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantOfficialCopyVerificationEvent).where(
                        GrantOfficialCopyVerificationEvent.evidence_version_id == evidence.id,
                        GrantOfficialCopyVerificationEvent.event_type == command.event_type.value,
                    )
                )
            )
        )
        if same_stage is not None:
            _conflict()
        current_key = f"{_CURRENT_PREFIX}{evidence.id}"
        current = _one_or_none(
            list(
                transaction.scalars(
                    select(GrantOfficialCopyVerificationEvent).where(
                        GrantOfficialCopyVerificationEvent.current_identity_key == current_key
                    )
                )
            )
        )
        if command.event_type is GrantOfficialCopyEventType.ACQUIRED:
            if current is not None:
                _conflict()
        elif current is None or current.id != predecessor.id:
            _conflict()

    row = GrantOfficialCopyVerificationEvent(
        id=str(uuid4()),
        evidence_version_id=evidence.id,
        source_config_id=source.config_id,
        source_record_id=source.source_record_id,
        role_config_id=roles.config_id,
        evidence_scope=command.evidence_scope.value,
        event_type=command.event_type.value,
        actor_id=command.actor_id,
        action_at=command.action_at,
        reason=command.reason,
        original_reference=original_reference,
        acquisition_method_snapshot=source.acquisition_method,
        evidence_content_hash=evidence.content_hash,
        source_config_snapshot_hash=source.config_snapshot_hash,
        source_snapshot_hash=source.source_snapshot_hash,
        role_config_snapshot_hash=roles.config_snapshot_hash,
        predecessor_event_id=predecessor.id if predecessor is not None else None,
        event_snapshot=snapshot,
        event_snapshot_hash=_hash(snapshot),
        idempotency_key=command.idempotency_key,
        current_identity_key=current_key,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            if predecessor is not None:
                moved = transaction.execute(
                    update(GrantOfficialCopyVerificationEvent)
                    .where(
                        GrantOfficialCopyVerificationEvent.id == predecessor.id,
                        GrantOfficialCopyVerificationEvent.current_identity_key == current_key,
                    )
                    .values(current_identity_key=None)
                )
                if moved.rowcount != 1:
                    _conflict()
            transaction.add(row)
            transaction.flush([row])
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            replay = _one_or_none(
                list(
                    transaction.scalars(
                        select(GrantOfficialCopyVerificationEvent).where(
                            GrantOfficialCopyVerificationEvent.idempotency_key
                            == command.idempotency_key
                        )
                    )
                )
            )
            if replay is not None:
                _validate_stored(replay)
                if replay.event_snapshot == snapshot:
                    return _result(replay, GrantOfficialCopyDisposition.REUSED)
        _conflict()
    return _result(row, GrantOfficialCopyDisposition.CREATED)
