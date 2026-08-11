from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import BusinessError, raise_business_error
from app.modules.auth.models import T_User, T_UserRole
from app.modules.documents.models import GrantEvidenceCandidate
from app.modules.system.grant_manual_review_role_service import (
    GrantManualReviewRoleResolution,
    ResolveGrantManualReviewRoleConfigCommand,
    resolve_grant_manual_review_role_config,
)


class GrantEvidenceReviewDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class GrantEvidenceReviewDisposition(str, Enum):
    CHANGED = "CHANGED"
    REUSED = "REUSED"


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewGrantEvidenceCandidateCommand:
    candidate_id: str
    decision: GrantEvidenceReviewDecision
    reviewer_id: str
    reviewed_at: datetime
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewGrantEvidenceCandidateResult:
    candidate_id: str
    evidence_version_id: str
    review_status: str
    reviewer_id: str
    reviewed_at: datetime
    candidate_snapshot_hash: str
    review_role_config_id: str
    review_role_config_snapshot_hash: str
    disposition: GrantEvidenceReviewDisposition


_CANDIDATE_SCHEMA = "CNIPA_GRANT_EVIDENCE_CANDIDATE_V1"
_ACQUISITION_SCHEMA = "CNIPA_GRANT_EVIDENCE_ACQUISITION_V2"
_EVIDENCE_SCOPES = {"GRANT_ANNOUNCEMENT", "PATENT_REGISTER"}
_ACQUISITION_KEYS = {
    "acquired_at",
    "acquired_by",
    "acquisition_event_id",
    "acquisition_event_snapshot_hash",
    "acquisition_method",
    "acquisition_reason",
    "attachment_id",
    "case_id",
    "document_id",
    "evidence_content_hash",
    "evidence_scope",
    "evidence_version_id",
    "first_verification_event_id",
    "first_verification_event_snapshot_hash",
    "first_verification_reason",
    "first_verified_at",
    "first_verified_by",
    "original_reference",
    "proposal_role_config_id",
    "proposal_role_config_snapshot_hash",
    "proposed_at",
    "proposed_by",
    "schema_version",
    "second_verification_reason",
    "second_verified_at",
    "second_verified_by",
    "source_config_id",
    "source_config_snapshot_hash",
    "source_record_id",
    "source_snapshot_hash",
    "source_version",
    "terminal_verification_event_id",
    "terminal_verification_event_snapshot_hash",
}


def _invalid(field: str) -> None:
    raise_business_error(
        "GRANT_EVIDENCE_REVIEW_INPUT_INVALID",
        "Invalid grant evidence review input",
        details={"field": field},
        status_code=400,
    )


def _conflict() -> None:
    raise_business_error(
        "GRANT_EVIDENCE_REVIEW_CONFLICT",
        "Grant evidence review conflict",
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


def _text(value: object, field: str, limit: int, *, input_error: bool = True) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or "\x00" in value
        or len(value) > limit
    ):
        _invalid(field) if input_error else _conflict()
    return value


def _hash64(value: object) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        _conflict()
    return value


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical(value: object) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        _conflict()


def _canonical_payload(value: object) -> object:
    if type(value) is not str:
        _conflict()
    try:
        payload = json.loads(value)
    except (TypeError, ValueError):
        _conflict()
    if _canonical(payload) != value:
        _conflict()
    return payload


def _timestamp(value: object) -> datetime:
    if type(value) is not str:
        _conflict()
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        _conflict()
    if parsed.utcoffset() is not None or parsed.isoformat(timespec="microseconds") != value:
        _conflict()
    return parsed


def _validate_command(command: object) -> ReviewGrantEvidenceCandidateCommand:
    if type(command) is not ReviewGrantEvidenceCandidateCommand:
        _invalid("command")
    _uuid(command.candidate_id, "candidate_id")
    if type(command.decision) is not GrantEvidenceReviewDecision:
        _invalid("decision")
    _uuid(command.reviewer_id, "reviewer_id")
    if type(command.reviewed_at) is not datetime or command.reviewed_at.utcoffset() is not None:
        _invalid("reviewed_at")
    _text(command.reason, "reason", 4096)
    return command


def _validate_transaction(transaction: object) -> Session:
    if not isinstance(transaction, Session):
        _invalid("transaction")
    if transaction.new or transaction.dirty or transaction.deleted:
        _conflict()
    return transaction


def _validate_candidate_payload(row: GrantEvidenceCandidate) -> None:
    payload = _canonical_payload(row.candidate_snapshot)
    if type(payload) is not dict or set(payload) != {
        "schema_version",
        "evidence_scope",
        "facts",
        "conflicts",
    }:
        _conflict()
    if (
        payload["schema_version"] != _CANDIDATE_SCHEMA
        or payload["evidence_scope"] != row.evidence_scope
    ):
        _conflict()
    facts = payload["facts"]
    if type(facts) is not list or not facts:
        _conflict()
    fact_pairs: list[tuple[str, str]] = []
    for fact in facts:
        if type(fact) is not dict or set(fact) != {"name", "raw_value"}:
            _conflict()
        fact_pairs.append(
            (
                _text(fact["name"], "candidate.facts.name", 4096, input_error=False),
                _text(
                    fact["raw_value"],
                    "candidate.facts.raw_value",
                    4096,
                    input_error=False,
                ),
            )
        )
    if len({name for name, _value in fact_pairs}) != len(fact_pairs) or tuple(fact_pairs) != tuple(
        sorted(fact_pairs)
    ):
        _conflict()
    fact_names = {name for name, _value in fact_pairs}

    conflicts = payload["conflicts"]
    if type(conflicts) is not list:
        _conflict()
    conflict_names: list[str] = []
    for conflict in conflicts:
        if type(conflict) is not dict or set(conflict) != {"name", "raw_values"}:
            _conflict()
        name = _text(conflict["name"], "candidate.conflicts.name", 4096, input_error=False)
        raw_values = conflict["raw_values"]
        if type(raw_values) is not list or len(raw_values) < 2:
            _conflict()
        checked_values = tuple(
            _text(
                value,
                "candidate.conflicts.raw_values",
                4096,
                input_error=False,
            )
            for value in raw_values
        )
        if (
            len(set(checked_values)) != len(checked_values)
            or checked_values != tuple(sorted(checked_values))
            or name not in fact_names
        ):
            _conflict()
        conflict_names.append(name)
    if len(set(conflict_names)) != len(conflict_names) or tuple(conflict_names) != tuple(
        sorted(conflict_names)
    ):
        _conflict()
    expected_conflicts = _canonical(conflicts) if conflicts else None
    if (
        row.candidate_snapshot_hash != _hash(row.candidate_snapshot)
        or row.conflict_snapshot != expected_conflicts
    ):
        _conflict()


def _validate_acquisition_payload(row: GrantEvidenceCandidate) -> None:
    payload = _canonical_payload(row.acquisition_snapshot)
    if type(payload) is not dict or set(payload) != _ACQUISITION_KEYS:
        _conflict()
    if (
        payload["schema_version"] != _ACQUISITION_SCHEMA
        or payload["case_id"] != row.case_id
        or payload["document_id"] != row.document_id
        or payload["evidence_version_id"] != row.evidence_version_id
        or payload["evidence_scope"] != row.evidence_scope
        or payload["source_config_id"] != row.source_config_id
        or payload["source_record_id"] != row.source_record_id
        or payload["source_version"] != row.source_version_snapshot
        or payload["original_reference"] != row.original_reference
        or payload["acquisition_method"] != row.acquisition_method_snapshot
        or payload["proposed_by"] != row.proposed_by
        or _timestamp(payload["acquired_at"]) != row.acquired_at
        or _timestamp(payload["proposed_at"]) != row.proposed_at
        or row.acquisition_snapshot_hash != _hash(row.acquisition_snapshot)
    ):
        _conflict()
    for field in (
        "acquired_by",
        "acquisition_event_id",
        "attachment_id",
        "first_verification_event_id",
        "first_verified_by",
        "proposal_role_config_id",
        "second_verified_by",
        "terminal_verification_event_id",
    ):
        _uuid(payload[field], f"acquisition.{field}", input_error=False)
    for field in (
        "acquisition_event_snapshot_hash",
        "first_verification_event_snapshot_hash",
        "proposal_role_config_snapshot_hash",
        "source_config_snapshot_hash",
        "source_snapshot_hash",
        "terminal_verification_event_snapshot_hash",
    ):
        _hash64(payload[field])
    first_at = _timestamp(payload["first_verified_at"])
    second_at = _timestamp(payload["second_verified_at"])
    if (
        not row.acquired_at < first_at < second_at <= row.proposed_at
        or payload["first_verified_by"] == payload["second_verified_by"]
    ):
        _conflict()
    for field, limit in (
        ("acquisition_method", 64),
        ("acquisition_reason", 4096),
        ("evidence_content_hash", 128),
        ("first_verification_reason", 4096),
        ("original_reference", 512),
        ("second_verification_reason", 4096),
        ("source_version", 128),
    ):
        _text(payload[field], f"acquisition.{field}", limit, input_error=False)


def _validate_candidate(row: GrantEvidenceCandidate) -> None:
    for field in (
        "id",
        "case_id",
        "document_id",
        "evidence_version_id",
        "source_config_id",
        "source_record_id",
        "proposed_by",
    ):
        _uuid(getattr(row, field), f"candidate.{field}", input_error=False)
    if (
        row.evidence_scope not in _EVIDENCE_SCOPES
        or type(row.acquired_at) is not datetime
        or row.acquired_at.utcoffset() is not None
        or type(row.proposed_at) is not datetime
        or row.proposed_at.utcoffset() is not None
        or row.acquired_at > row.proposed_at
    ):
        _conflict()
    for field in ("created_at", "updated_at"):
        value = getattr(row, field)
        if type(value) is not datetime or value.utcoffset() is not None:
            _conflict()
    _text(row.source_version_snapshot, "candidate.source_version_snapshot", 128, input_error=False)
    _text(row.original_reference, "candidate.original_reference", 512, input_error=False)
    _text(
        row.acquisition_method_snapshot,
        "candidate.acquisition_method_snapshot",
        64,
        input_error=False,
    )
    _hash64(row.acquisition_snapshot_hash)
    _hash64(row.candidate_snapshot_hash)
    _validate_candidate_payload(row)
    _validate_acquisition_payload(row)
    pending = (
        row.review_status == "PENDING"
        and row.reviewer_id is None
        and row.reviewed_at is None
        and row.review_reason is None
    )
    terminal = row.review_status in {"APPROVED", "REJECTED"}
    if terminal:
        _uuid(row.reviewer_id, "candidate.reviewer_id", input_error=False)
        if (
            type(row.reviewed_at) is not datetime
            or row.reviewed_at.utcoffset() is not None
            or row.reviewed_at < row.proposed_at
            or row.reviewer_id == row.proposed_by
        ):
            _conflict()
        _text(row.review_reason, "candidate.review_reason", 4096, input_error=False)
    if not pending and not terminal:
        _conflict()


def _review_authority(
    transaction: Session,
    command: ReviewGrantEvidenceCandidateCommand,
) -> GrantManualReviewRoleResolution:
    try:
        roles = resolve_grant_manual_review_role_config(
            ResolveGrantManualReviewRoleConfigCommand(as_of=command.reviewed_at),
            transaction,
        )
    except BusinessError:
        _conflict()
    if type(roles) is not GrantManualReviewRoleResolution:
        _conflict()
    _uuid(roles.config_id, "review_role_config_id", input_error=False)
    _hash64(roles.config_snapshot_hash)
    _uuid(
        roles.manual_review_second_reviewer_role_id,
        "manual_review_second_reviewer_role_id",
        input_error=False,
    )
    membership = transaction.scalar(
        select(T_UserRole.user_id)
        .join(T_User, T_User.id == T_UserRole.user_id)
        .where(
            T_UserRole.user_id == command.reviewer_id,
            T_UserRole.role_id == roles.manual_review_second_reviewer_role_id,
            T_User.is_active.is_(True),
        )
    )
    if membership != command.reviewer_id:
        _conflict()
    return roles


def _result(
    row: GrantEvidenceCandidate,
    command: ReviewGrantEvidenceCandidateCommand,
    roles: GrantManualReviewRoleResolution,
    disposition: GrantEvidenceReviewDisposition,
) -> ReviewGrantEvidenceCandidateResult:
    return ReviewGrantEvidenceCandidateResult(
        candidate_id=row.id,
        evidence_version_id=row.evidence_version_id,
        review_status=command.decision.value,
        reviewer_id=command.reviewer_id,
        reviewed_at=command.reviewed_at,
        candidate_snapshot_hash=row.candidate_snapshot_hash,
        review_role_config_id=roles.config_id,
        review_role_config_snapshot_hash=roles.config_snapshot_hash,
        disposition=disposition,
    )


def _ensure_sqlite_outer_transaction(transaction: Session) -> None:
    connection = transaction.connection()
    if connection.dialect.name != "sqlite":
        return
    if not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")


def review_grant_evidence_candidate(
    command: ReviewGrantEvidenceCandidateCommand,
    transaction: Session,
) -> ReviewGrantEvidenceCandidateResult:
    command = _validate_command(command)
    transaction = _validate_transaction(transaction)
    with transaction.no_autoflush:
        row = transaction.get(GrantEvidenceCandidate, command.candidate_id)
        if row is None:
            _conflict()
        _validate_candidate(row)
        if command.reviewed_at < row.proposed_at or command.reviewer_id == row.proposed_by:
            _conflict()
        roles = _review_authority(transaction, command)
        if row.review_status != "PENDING":
            if (
                row.review_status != command.decision.value
                or row.reviewer_id != command.reviewer_id
                or row.reviewed_at != command.reviewed_at
                or row.review_reason != command.reason
            ):
                _conflict()
            return _result(row, command, roles, GrantEvidenceReviewDisposition.REUSED)

    _ensure_sqlite_outer_transaction(transaction)
    try:
        with transaction.begin_nested():
            changed = transaction.execute(
                update(GrantEvidenceCandidate)
                .where(
                    GrantEvidenceCandidate.id == command.candidate_id,
                    GrantEvidenceCandidate.review_status == "PENDING",
                    GrantEvidenceCandidate.reviewer_id.is_(None),
                    GrantEvidenceCandidate.reviewed_at.is_(None),
                    GrantEvidenceCandidate.review_reason.is_(None),
                )
                .values(
                    review_status=command.decision.value,
                    reviewer_id=command.reviewer_id,
                    reviewed_at=command.reviewed_at,
                    review_reason=command.reason,
                    updated_at=command.reviewed_at,
                )
            )
            if changed.rowcount != 1:
                _conflict()
    except IntegrityError:
        _conflict()
    if command.decision is GrantEvidenceReviewDecision.APPROVED and row.conflict_snapshot is None:
        from app.modules.documents import evidence_policy

        adapter = (
            evidence_policy.apply_grant_announcement_evidence
            if row.evidence_scope == "GRANT_ANNOUNCEMENT"
            else evidence_policy.apply_patent_register_evidence
        )
        adapter(
            row,
            review_role_config_id=roles.config_id,
            review_role_config_snapshot_hash=roles.config_snapshot_hash,
            transaction=transaction,
        )
    return _result(row, command, roles, GrantEvidenceReviewDisposition.CHANGED)
