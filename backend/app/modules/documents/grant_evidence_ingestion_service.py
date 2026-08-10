from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.auth.models import T_User, T_UserRole
from app.modules.documents.models import (
    DocAttachment,
    DocumentEvidenceVersion,
    GrantEvidenceCandidate,
    GrantOfficialCopyVerificationEvent,
)
from app.modules.system.grant_evidence_source_service import (
    GrantEvidenceScope,
    _validate_source_canonical,
)
from app.modules.system.grant_evidence_source_service import (
    _validate_config_canonical as _validate_source_config_canonical,
)
from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleResolution,
    ResolveGrantManualReviewRoleConfigCommand,
    resolve_grant_manual_review_role_config,
)
from app.modules.system.grant_manual_review_role_service import (
    _validate_canonical as _validate_role_config_canonical,
)
from app.modules.system.models import (
    GrantEvidenceSourceConfig,
    GrantEvidenceSourceRecord,
    GrantManualReviewRoleConfig,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceFact:
    name: str
    raw_value: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantEvidenceConflict:
    name: str
    raw_values: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class IngestGrantEvidenceCandidateCommand:
    case_id: str
    document_id: str
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    expected_terminal_event_id: str
    proposed_by: str
    proposed_at: datetime
    facts: tuple[GrantEvidenceFact, ...]
    conflicts: tuple[GrantEvidenceConflict, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class IngestGrantEvidenceCandidateResult:
    candidate_id: str
    evidence_version_id: str
    terminal_event_id: str
    source_config_id: str
    source_record_id: str
    proposal_role_config_id: str
    evidence_scope: GrantEvidenceScope
    acquisition_snapshot_hash: str
    candidate_snapshot_hash: str
    review_status: str
    disposition: str


_EVENT_SCHEMA = "CNIPA_GRANT_OFFICIAL_COPY_VERIFICATION_EVENT_V1"
_ACQUISITION_SCHEMA = "CNIPA_GRANT_EVIDENCE_ACQUISITION_V2"
_CANDIDATE_SCHEMA = "CNIPA_GRANT_EVIDENCE_CANDIDATE_V1"
_CURRENT_PREFIX = "GRANT_OFFICIAL_COPY|"


def _invalid(field: str) -> None:
    raise_business_error(
        "GRANT_EVIDENCE_CANDIDATE_INPUT_INVALID",
        "Invalid grant evidence candidate input",
        details={"field": field},
        status_code=400,
    )


def _conflict() -> None:
    raise_business_error(
        "GRANT_EVIDENCE_CANDIDATE_CONFLICT",
        "Grant evidence candidate conflict",
        status_code=409,
    )


def _uuid(value: object, field: str, *, input_error: bool = True) -> str:
    if type(value) is not str:
        _invalid(field) if input_error else _conflict()
    try:
        parsed = UUID(value)
    except (AttributeError, TypeError, ValueError):
        _invalid(field) if input_error else _conflict()
    if str(parsed) != value:
        _invalid(field) if input_error else _conflict()
    return value


def _string(value: object, field: str, limit: int, *, input_error: bool = True) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or len(value) > limit
    ):
        _invalid(field) if input_error else _conflict()
    return value


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash64(value: object) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _conflict()
    return value


def _canonical(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _validate_command(command: object) -> IngestGrantEvidenceCandidateCommand:
    if type(command) is not IngestGrantEvidenceCandidateCommand:
        _invalid("command")
    for field in (
        "case_id",
        "document_id",
        "evidence_version_id",
        "expected_terminal_event_id",
        "proposed_by",
    ):
        _uuid(getattr(command, field), field)
    if type(command.evidence_scope) is not GrantEvidenceScope:
        _invalid("evidence_scope")
    if type(command.proposed_at) is not datetime or command.proposed_at.utcoffset() is not None:
        _invalid("proposed_at")
    if type(command.facts) is not tuple or not command.facts:
        _invalid("facts")
    if type(command.conflicts) is not tuple:
        _invalid("conflicts")
    fact_pairs: list[tuple[str, str]] = []
    for fact in command.facts:
        if type(fact) is not GrantEvidenceFact:
            _invalid("facts")
        fact_pairs.append(
            (
                _string(fact.name, "facts.name", 4096),
                _string(fact.raw_value, "facts.raw_value", 4096),
            )
        )
    if len({name for name, _value in fact_pairs}) != len(fact_pairs) or tuple(fact_pairs) != tuple(
        sorted(fact_pairs)
    ):
        _invalid("facts")
    fact_names = {name for name, _value in fact_pairs}
    conflict_names: list[str] = []
    for conflict in command.conflicts:
        if type(conflict) is not GrantEvidenceConflict:
            _invalid("conflicts")
        name = _string(conflict.name, "conflicts.name", 4096)
        if type(conflict.raw_values) is not tuple or len(conflict.raw_values) < 2:
            _invalid("conflicts.raw_values")
        raw_values = tuple(
            _string(value, "conflicts.raw_values", 4096) for value in conflict.raw_values
        )
        if len(set(raw_values)) != len(raw_values) or raw_values != tuple(sorted(raw_values)):
            _invalid("conflicts.raw_values")
        if name not in fact_names:
            _invalid("conflicts.name")
        conflict_names.append(name)
    if len(set(conflict_names)) != len(conflict_names) or tuple(conflict_names) != tuple(
        sorted(conflict_names)
    ):
        _invalid("conflicts")
    return command


def _validate_transaction(transaction: object) -> Session:
    if not isinstance(transaction, Session):
        _invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _conflict()
    return transaction


def _validate_evidence(
    transaction: Session,
    command: IngestGrantEvidenceCandidateCommand,
) -> tuple[DocumentEvidenceVersion, DocAttachment]:
    evidence = transaction.get(DocumentEvidenceVersion, command.evidence_version_id)
    if evidence is None:
        _conflict()
    content_hash = _string(evidence.content_hash, "evidence.content_hash", 128, input_error=False)
    if (
        evidence.case_id != command.case_id
        or evidence.document_id != command.document_id
        or evidence.current_identity_key != f"{evidence.case_id}|{evidence.lineage_key}"
        or evidence.role != "RAW_ATTACHMENT"
        or evidence.state != "FINAL"
        or evidence.review_state != "PENDING"
        or evidence.reviewer_id is not None
        or evidence.reviewed_at is not None
        or evidence.final_submitted_at is not None
    ):
        _conflict()
    attachment = transaction.get(DocAttachment, evidence.attachment_id)
    if (
        attachment is None
        or attachment.document_id != command.document_id
        or attachment.content_hash != content_hash
    ):
        _conflict()
    return evidence, attachment


def _event_snapshot(row: GrantOfficialCopyVerificationEvent) -> str:
    return _canonical(
        {
            "acquisition_method_snapshot": row.acquisition_method_snapshot,
            "action_at": row.action_at.isoformat(timespec="microseconds"),
            "actor_id": row.actor_id,
            "event_type": row.event_type,
            "evidence_content_hash": row.evidence_content_hash,
            "evidence_scope": row.evidence_scope,
            "evidence_version_id": row.evidence_version_id,
            "original_reference": row.original_reference,
            "predecessor_event_id": row.predecessor_event_id,
            "reason": row.reason,
            "role_config_id": row.role_config_id,
            "role_config_snapshot_hash": row.role_config_snapshot_hash,
            "schema": _EVENT_SCHEMA,
            "source_config_id": row.source_config_id,
            "source_config_snapshot_hash": row.source_config_snapshot_hash,
            "source_record_id": row.source_record_id,
            "source_snapshot_hash": row.source_snapshot_hash,
        }
    )


def _validate_event(row: GrantOfficialCopyVerificationEvent) -> None:
    for field in (
        "id",
        "evidence_version_id",
        "source_config_id",
        "source_record_id",
        "role_config_id",
        "actor_id",
    ):
        _uuid(getattr(row, field), field, input_error=False)
    if row.predecessor_event_id is not None:
        _uuid(row.predecessor_event_id, "predecessor_event_id", input_error=False)
    if (
        row.event_type not in {"ACQUIRED", "FIRST_VERIFIED", "SECOND_VERIFIED"}
        or row.evidence_scope not in {item.value for item in GrantEvidenceScope}
        or type(row.action_at) is not datetime
        or row.action_at.utcoffset() is not None
        or row.current_identity_key not in {None, f"{_CURRENT_PREFIX}{row.evidence_version_id}"}
    ):
        _conflict()
    for value in (
        row.source_config_snapshot_hash,
        row.source_snapshot_hash,
        row.role_config_snapshot_hash,
        row.event_snapshot_hash,
    ):
        _hash64(value)
    for value, field, limit in (
        (row.reason, "reason", 4096),
        (row.original_reference, "original_reference", 512),
        (row.acquisition_method_snapshot, "acquisition_method_snapshot", 64),
        (row.evidence_content_hash, "evidence_content_hash", 128),
        (row.idempotency_key, "idempotency_key", 128),
    ):
        _string(value, field, limit, input_error=False)
    expected = _event_snapshot(row)
    if row.event_snapshot != expected or row.event_snapshot_hash != _hash_text(expected):
        _conflict()


def _role_config_at(
    transaction: Session,
    event: GrantOfficialCopyVerificationEvent,
) -> None:
    row = transaction.get(GrantManualReviewRoleConfig, event.role_config_id)
    if row is None:
        _conflict()
    try:
        _validate_role_config_canonical(row)
    except BusinessError:
        _conflict()
    if (
        row.config_status != "ACTIVE"
        or row.config_snapshot_hash != event.role_config_snapshot_hash
        or row.published_at > event.action_at
        or row.effective_from > event.action_at
        or (row.effective_to is not None and event.action_at >= row.effective_to)
    ):
        _conflict()


def _terminal_chain(
    transaction: Session,
    command: IngestGrantEvidenceCandidateCommand,
    evidence: DocumentEvidenceVersion,
) -> tuple[
    GrantOfficialCopyVerificationEvent,
    GrantOfficialCopyVerificationEvent,
    GrantOfficialCopyVerificationEvent,
]:
    current_key = f"{_CURRENT_PREFIX}{evidence.id}"
    current = list(
        transaction.scalars(
            select(GrantOfficialCopyVerificationEvent).where(
                GrantOfficialCopyVerificationEvent.current_identity_key == current_key
            )
        )
    )
    if len(current) != 1:
        _conflict()
    terminal = current[0]
    if (
        terminal.id != command.expected_terminal_event_id
        or terminal.event_type != "SECOND_VERIFIED"
    ):
        _conflict()
    first = transaction.get(GrantOfficialCopyVerificationEvent, terminal.predecessor_event_id)
    acquired = (
        transaction.get(GrantOfficialCopyVerificationEvent, first.predecessor_event_id)
        if first is not None
        else None
    )
    if (
        first is None
        or acquired is None
        or first.event_type != "FIRST_VERIFIED"
        or acquired.event_type != "ACQUIRED"
        or acquired.predecessor_event_id is not None
        or first.actor_id == terminal.actor_id
    ):
        _conflict()
    lineage = (acquired, first, terminal)
    for event in lineage:
        _validate_event(event)
        _role_config_at(transaction, event)
        if (
            event.evidence_version_id != evidence.id
            or event.evidence_scope != command.evidence_scope.value
            or event.evidence_content_hash != evidence.content_hash
            or event.source_config_id != acquired.source_config_id
            or event.source_record_id != acquired.source_record_id
            or event.source_config_snapshot_hash != acquired.source_config_snapshot_hash
            or event.source_snapshot_hash != acquired.source_snapshot_hash
            or event.original_reference != acquired.original_reference
            or event.acquisition_method_snapshot != acquired.acquisition_method_snapshot
        ):
            _conflict()
    return lineage


def _source_authority(
    transaction: Session,
    command: IngestGrantEvidenceCandidateCommand,
    acquired: GrantOfficialCopyVerificationEvent,
) -> GrantEvidenceSourceRecord:
    config = transaction.get(GrantEvidenceSourceConfig, acquired.source_config_id)
    source = transaction.get(GrantEvidenceSourceRecord, acquired.source_record_id)
    if config is None or source is None:
        _conflict()
    try:
        _validate_source_config_canonical(config)
        _validate_source_canonical(source)
        config_snapshot = json.loads(config.config_snapshot)
    except (BusinessError, TypeError, ValueError):
        _conflict()
    if (
        config.gate_code != "DG-GRANT-EVIDENCE-SOURCE"
        or config.scope_key != "GLOBAL"
        or config.evidence_scope != command.evidence_scope.value
        or config.source_record_id != source.id
        or config.config_status != "ACTIVE"
        or config.config_snapshot_hash != acquired.source_config_snapshot_hash
        or config_snapshot.get("source_record_id") != source.id
        or config_snapshot.get("source_version") != source.source_version
        or config_snapshot.get("source_snapshot_hash") != source.source_snapshot_hash
        or config.published_at > acquired.action_at
        or config.effective_from > acquired.action_at
        or (config.effective_to is not None and acquired.action_at >= config.effective_to)
        or source.source_authority != "CNIPA"
        or source.evidence_scope != command.evidence_scope.value
        or source.source_snapshot_hash != acquired.source_snapshot_hash
        or source.review_status != "APPROVED"
        or source.reviewed_by is None
        or source.reviewed_at is None
        or source.reviewed_at > acquired.action_at
        or source.activation_status not in {"ACTIVE", "RETIRED"}
        or source.activated_by is None
        or source.activated_at is None
        or source.activated_at > acquired.action_at
        or source.effective_from > acquired.action_at
        or (source.effective_to is not None and acquired.action_at >= source.effective_to)
        or source.acquisition_method != acquired.acquisition_method_snapshot
    ):
        _conflict()
    return source


def _proposal_authority(
    transaction: Session,
    command: IngestGrantEvidenceCandidateCommand,
) -> GrantManualReviewRoleResolution:
    try:
        roles = resolve_grant_manual_review_role_config(
            ResolveGrantManualReviewRoleConfigCommand(as_of=command.proposed_at),
            transaction,
        )
    except BusinessError:
        _conflict()
    if type(roles) is not GrantManualReviewRoleResolution:
        _conflict()
    _uuid(roles.config_id, "proposal_role_config_id", input_error=False)
    _hash64(roles.config_snapshot_hash)
    membership = transaction.scalar(
        select(T_UserRole.user_id)
        .join(T_User, T_User.id == T_UserRole.user_id)
        .where(
            T_UserRole.user_id == command.proposed_by,
            T_UserRole.role_id == roles.manual_review_proposer_role_id,
            T_User.is_active.is_(True),
        )
    )
    if membership != command.proposed_by:
        _conflict()
    return roles


def _candidate_snapshot(command: IngestGrantEvidenceCandidateCommand) -> str:
    return _canonical(
        {
            "conflicts": [
                {"name": conflict.name, "raw_values": list(conflict.raw_values)}
                for conflict in command.conflicts
            ],
            "evidence_scope": command.evidence_scope.value,
            "facts": [{"name": fact.name, "raw_value": fact.raw_value} for fact in command.facts],
            "schema_version": _CANDIDATE_SCHEMA,
        }
    )


def _acquisition_snapshot(
    *,
    command: IngestGrantEvidenceCandidateCommand,
    evidence: DocumentEvidenceVersion,
    attachment: DocAttachment,
    acquired: GrantOfficialCopyVerificationEvent,
    first: GrantOfficialCopyVerificationEvent,
    terminal: GrantOfficialCopyVerificationEvent,
    source: GrantEvidenceSourceRecord,
    roles: GrantManualReviewRoleResolution,
) -> str:
    return _canonical(
        {
            "acquired_at": acquired.action_at.isoformat(timespec="microseconds"),
            "acquired_by": acquired.actor_id,
            "acquisition_event_id": acquired.id,
            "acquisition_event_snapshot_hash": acquired.event_snapshot_hash,
            "acquisition_method": acquired.acquisition_method_snapshot,
            "acquisition_reason": acquired.reason,
            "attachment_id": attachment.id,
            "case_id": command.case_id,
            "document_id": command.document_id,
            "evidence_content_hash": evidence.content_hash,
            "evidence_scope": command.evidence_scope.value,
            "evidence_version_id": evidence.id,
            "first_verification_event_id": first.id,
            "first_verification_event_snapshot_hash": first.event_snapshot_hash,
            "first_verification_reason": first.reason,
            "first_verified_at": first.action_at.isoformat(timespec="microseconds"),
            "first_verified_by": first.actor_id,
            "original_reference": acquired.original_reference,
            "proposal_role_config_id": roles.config_id,
            "proposal_role_config_snapshot_hash": roles.config_snapshot_hash,
            "proposed_at": command.proposed_at.isoformat(timespec="microseconds"),
            "proposed_by": command.proposed_by,
            "schema_version": _ACQUISITION_SCHEMA,
            "second_verification_reason": terminal.reason,
            "second_verified_at": terminal.action_at.isoformat(timespec="microseconds"),
            "second_verified_by": terminal.actor_id,
            "source_config_id": acquired.source_config_id,
            "source_config_snapshot_hash": acquired.source_config_snapshot_hash,
            "source_record_id": source.id,
            "source_snapshot_hash": source.source_snapshot_hash,
            "source_version": source.source_version,
            "terminal_verification_event_id": terminal.id,
            "terminal_verification_event_snapshot_hash": terminal.event_snapshot_hash,
        }
    )


def _result(
    row: GrantEvidenceCandidate,
    *,
    terminal_event_id: str,
    proposal_role_config_id: str,
    disposition: str,
) -> IngestGrantEvidenceCandidateResult:
    return IngestGrantEvidenceCandidateResult(
        candidate_id=row.id,
        evidence_version_id=row.evidence_version_id,
        terminal_event_id=terminal_event_id,
        source_config_id=row.source_config_id,
        source_record_id=row.source_record_id,
        proposal_role_config_id=proposal_role_config_id,
        evidence_scope=GrantEvidenceScope(row.evidence_scope),
        acquisition_snapshot_hash=row.acquisition_snapshot_hash,
        candidate_snapshot_hash=row.candidate_snapshot_hash,
        review_status=row.review_status,
        disposition=disposition,
    )


def _replay(
    row: GrantEvidenceCandidate,
    *,
    command: IngestGrantEvidenceCandidateCommand,
    acquired: GrantOfficialCopyVerificationEvent,
    terminal: GrantOfficialCopyVerificationEvent,
    source: GrantEvidenceSourceRecord,
    roles: GrantManualReviewRoleResolution,
    acquisition_snapshot: str,
    candidate_snapshot: str,
    conflict_snapshot: str | None,
) -> IngestGrantEvidenceCandidateResult:
    if (
        row.case_id != command.case_id
        or row.document_id != command.document_id
        or row.evidence_version_id != command.evidence_version_id
        or row.source_config_id != acquired.source_config_id
        or row.source_record_id != source.id
        or row.evidence_scope != command.evidence_scope.value
        or row.source_version_snapshot != source.source_version
        or row.original_reference != acquired.original_reference
        or row.acquisition_method_snapshot != acquired.acquisition_method_snapshot
        or row.acquired_at != acquired.action_at
        or row.acquisition_snapshot != acquisition_snapshot
        or row.acquisition_snapshot_hash != _hash_text(acquisition_snapshot)
        or row.candidate_snapshot != candidate_snapshot
        or row.candidate_snapshot_hash != _hash_text(candidate_snapshot)
        or row.proposed_by != command.proposed_by
        or row.proposed_at != command.proposed_at
        or row.review_status != "PENDING"
        or row.reviewer_id is not None
        or row.reviewed_at is not None
        or row.review_reason is not None
        or row.conflict_snapshot != conflict_snapshot
    ):
        _conflict()
    return _result(
        row,
        terminal_event_id=terminal.id,
        proposal_role_config_id=roles.config_id,
        disposition="REUSED",
    )


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    if not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def ingest_grant_evidence_candidate(
    command: IngestGrantEvidenceCandidateCommand,
    transaction: Session,
) -> IngestGrantEvidenceCandidateResult:
    command = _validate_command(command)
    transaction = _validate_transaction(transaction)
    with transaction.no_autoflush:
        evidence, attachment = _validate_evidence(transaction, command)
        acquired, first, terminal = _terminal_chain(transaction, command, evidence)
        source = _source_authority(transaction, command, acquired)
        roles = _proposal_authority(transaction, command)
        candidate_snapshot = _candidate_snapshot(command)
        acquisition_snapshot = _acquisition_snapshot(
            command=command,
            evidence=evidence,
            attachment=attachment,
            acquired=acquired,
            first=first,
            terminal=terminal,
            source=source,
            roles=roles,
        )
        conflicts = json.loads(candidate_snapshot)["conflicts"]
        conflict_snapshot = _canonical(conflicts) if conflicts else None
        rows = list(
            transaction.scalars(
                select(GrantEvidenceCandidate).where(
                    GrantEvidenceCandidate.evidence_version_id == evidence.id
                )
            )
        )
        if len(rows) > 1:
            _conflict()
        if rows:
            return _replay(
                rows[0],
                command=command,
                acquired=acquired,
                terminal=terminal,
                source=source,
                roles=roles,
                acquisition_snapshot=acquisition_snapshot,
                candidate_snapshot=candidate_snapshot,
                conflict_snapshot=conflict_snapshot,
            )

    row = GrantEvidenceCandidate(
        id=str(uuid4()),
        case_id=command.case_id,
        document_id=command.document_id,
        evidence_version_id=evidence.id,
        source_config_id=acquired.source_config_id,
        source_record_id=source.id,
        evidence_scope=command.evidence_scope.value,
        source_version_snapshot=source.source_version,
        original_reference=acquired.original_reference,
        acquisition_method_snapshot=acquired.acquisition_method_snapshot,
        acquired_at=acquired.action_at,
        acquisition_snapshot=acquisition_snapshot,
        acquisition_snapshot_hash=_hash_text(acquisition_snapshot),
        candidate_snapshot=candidate_snapshot,
        candidate_snapshot_hash=_hash_text(candidate_snapshot),
        proposed_by=command.proposed_by,
        proposed_at=command.proposed_at,
        review_status="PENDING",
        reviewer_id=None,
        reviewed_at=None,
        review_reason=None,
        conflict_snapshot=conflict_snapshot,
    )
    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            transaction.add(row)
            transaction.flush([row])
    except IntegrityError:
        transaction.expire_all()
        with transaction.no_autoflush:
            rows = list(
                transaction.scalars(
                    select(GrantEvidenceCandidate).where(
                        GrantEvidenceCandidate.evidence_version_id == evidence.id
                    )
                )
            )
            if len(rows) == 1:
                return _replay(
                    rows[0],
                    command=command,
                    acquired=acquired,
                    terminal=terminal,
                    source=source,
                    roles=roles,
                    acquisition_snapshot=acquisition_snapshot,
                    candidate_snapshot=candidate_snapshot,
                    conflict_snapshot=conflict_snapshot,
                )
        _conflict()
    return _result(
        row,
        terminal_event_id=terminal.id,
        proposal_role_config_id=roles.config_id,
        disposition="CREATED",
    )
