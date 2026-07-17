from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    ConfirmationStatus,
    EvidenceReference,
    LifecycleEventCommand,
)
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
)
from app.modules.documents.evidence_service import (
    _capture_lifecycle_projection,
    _stored_activity_projection,
)
from app.modules.documents.models import DocumentEvidenceVersion

_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_EXTERNAL_SUBMISSION_ELIGIBLE_ROLES = frozenset(
    {
        "FILING_FULL_WORD",
        "TRACKED_REVISED_WORD",
        "FILING_COMPONENT",
        "EXTERNAL_XML_PACKAGE",
        "OFFICIAL_SUBMISSION_LIST",
        "OFFICIAL_FINAL_PDF",
        "SUBMITTED_XML",
        "OFFICIAL_RECEIPT",
        "CLIENT_LETTER_WORD",
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalizeExternalSubmissionCommand:
    case_id: str
    evidence_version_id: str
    actor_id: str
    submitted_at: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SubmissionEvidenceResult:
    case_id: str
    evidence_version_id: str
    content_hash: str
    submitted_at: datetime
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    idempotency_key: str
    reused: bool


def _invalid(field: str) -> None:
    raise_business_error(
        "EXTERNAL_SUBMISSION_INVALID",
        f"Invalid external-submission field: {field}",
        details={"field": field},
        status_code=400,
    )


def _require_text(value: object, *, field: str, max_length: int) -> None:
    if type(value) is not str or not value.strip() or len(value) > max_length:
        _invalid(field)


def _validate_command(command: FinalizeExternalSubmissionCommand) -> None:
    if type(command) is not FinalizeExternalSubmissionCommand:
        _invalid("command")
    _require_text(command.case_id, field="case_id", max_length=36)
    _require_text(
        command.evidence_version_id,
        field="evidence_version_id",
        max_length=36,
    )
    _require_text(command.actor_id, field="actor_id", max_length=36)
    if type(command.submitted_at) is not datetime or command.submitted_at.tzinfo is not None:
        _invalid("submitted_at")
    _require_text(command.idempotency_key, field="idempotency_key", max_length=99)


def _validate_stored_identity(version: DocumentEvidenceVersion) -> None:
    if (
        type(version.lineage_key) is not str
        or not version.lineage_key.strip()
        or len(version.lineage_key) > 128
        or type(version.role) is not str
        or type(version.creator_id) is not str
        or not version.creator_id.strip()
        or len(version.creator_id) > 36
        or type(version.content_hash) is not str
        or _CONTENT_HASH_PATTERN.fullmatch(version.content_hash) is None
    ):
        raise_business_error(
            "EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT",
            "Stored evidence identity is invalid",
            status_code=409,
        )
    try:
        EvidenceRole(version.role)
    except ValueError:
        raise_business_error(
            "EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT",
            "Stored evidence role is invalid",
            status_code=409,
        )


def _require_independent_approval(version: DocumentEvidenceVersion) -> None:
    if version.review_state != EvidenceReviewState.APPROVED.value:
        raise_business_error(
            "EXTERNAL_SUBMISSION_NOT_APPROVED",
            "Evidence version must be approved before external submission",
            status_code=409,
        )
    if (
        type(version.reviewer_id) is not str
        or not version.reviewer_id.strip()
        or len(version.reviewer_id) > 36
        or type(version.reviewed_at) is not datetime
        or version.reviewed_at.tzinfo is not None
    ):
        raise_business_error(
            "EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT",
            "Stored evidence review tuple is invalid",
            status_code=409,
        )
    if version.reviewer_id == version.creator_id:
        raise_business_error(
            "EXTERNAL_SUBMISSION_SELF_REVIEWED",
            "Evidence creator cannot independently approve the same version",
            status_code=409,
        )


def _activity_command(
    command: FinalizeExternalSubmissionCommand,
    version: DocumentEvidenceVersion,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=command.case_id,
        event_type="DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED",
        lane=ActivityLane.DOCUMENT,
        effective_at=command.submitted_at,
        occurred_at=command.submitted_at,
        evidence_refs=(
            EvidenceReference(
                case_id=command.case_id,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=version.id,
                content_hash=version.content_hash,
                captured_at=command.submitted_at,
            ),
        ),
        actor_id=command.actor_id,
        reviewer_id=version.reviewer_id,
        idempotency_key=f"document-external-submission:{command.idempotency_key}",
        source_activity_id=None,
        supersedes_event_id=None,
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={
            "evidence_version_id": version.id,
            "lineage_key": version.lineage_key,
            "role": version.role,
            "submitted_at": command.submitted_at.isoformat(),
        },
    )


def _result(
    command: FinalizeExternalSubmissionCommand,
    version: DocumentEvidenceVersion,
    *,
    activity_id: str,
    sequence: int,
    lifecycle_revision: int,
    reused: bool,
) -> SubmissionEvidenceResult:
    return SubmissionEvidenceResult(
        case_id=command.case_id,
        evidence_version_id=version.id,
        content_hash=version.content_hash,
        submitted_at=command.submitted_at,
        activity_id=activity_id,
        activity_sequence=sequence,
        lifecycle_revision=lifecycle_revision,
        idempotency_key=command.idempotency_key,
        reused=reused,
    )


def _require_replay_carrier_consistency(
    version: DocumentEvidenceVersion,
    activity: CaseActivityEvent,
) -> None:
    if (
        version.state != EvidenceVersionState.FINAL.value
        or version.review_state != EvidenceReviewState.APPROVED.value
        or type(version.reviewer_id) is not str
        or not version.reviewer_id.strip()
        or len(version.reviewer_id) > 36
        or type(version.reviewed_at) is not datetime
        or version.reviewed_at.tzinfo is not None
        or version.reviewer_id == version.creator_id
        or version.reviewer_id != activity.reviewer_id
        or version.final_submitted_at != activity.effective_at
    ):
        raise_business_error(
            "EXTERNAL_SUBMISSION_HISTORY_CONFLICT",
            "Evidence carrier disagrees with its submission activity",
            status_code=409,
        )


def finalize_external_submission(
    command: FinalizeExternalSubmissionCommand,
    transaction: Session,
) -> SubmissionEvidenceResult:
    _validate_command(command)

    case = transaction.get(Case, command.case_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    version = transaction.get(DocumentEvidenceVersion, command.evidence_version_id)
    if version is None:
        raise_business_error(
            "EVIDENCE_VERSION_NOT_FOUND",
            "Evidence version not found",
            status_code=404,
        )
    if version.case_id != command.case_id:
        raise_business_error(
            "EXTERNAL_SUBMISSION_CASE_MISMATCH",
            "Evidence version does not belong to the requested case",
            status_code=400,
        )
    _validate_stored_identity(version)
    if version.role not in _EXTERNAL_SUBMISSION_ELIGIBLE_ROLES:
        raise_business_error(
            "EXTERNAL_SUBMISSION_EVIDENCE_CONFLICT",
            "Stored evidence role is not eligible for external submission",
            status_code=409,
        )

    projection = _capture_lifecycle_projection(case)
    legacy_case_status = case.status
    activity_key = f"document-external-submission:{command.idempotency_key}"
    existing_activity = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == command.case_id,
            CaseActivityEvent.idempotency_key == activity_key,
        )
    )
    activity_command = _activity_command(command, version)
    if existing_activity is not None:
        previous_projection = _stored_activity_projection(
            existing_activity,
            old=True,
            verification_status=projection.lifecycle_verification_status,
        )
        stored_current_projection = _stored_activity_projection(
            existing_activity,
            old=False,
            verification_status=projection.lifecycle_verification_status,
        )
        if previous_projection != stored_current_projection:
            raise_business_error(
                "EXTERNAL_SUBMISSION_HISTORY_CONFLICT",
                "Stored submission activity changed the central lifecycle projection",
                status_code=409,
            )
        _require_replay_carrier_consistency(version, existing_activity)
        activity_result = append_case_activity(
            activity_command,
            transaction,
            previous_projection=previous_projection,
            current_projection=stored_current_projection,
            legacy_case_status=legacy_case_status,
            conflict_codes=(),
        )
        return _result(
            command,
            version,
            activity_id=activity_result.activity_id,
            sequence=activity_result.sequence,
            lifecycle_revision=activity_result.lifecycle_revision,
            reused=True,
        )

    if version.state != EvidenceVersionState.FINAL.value:
        raise_business_error(
            "EXTERNAL_SUBMISSION_NOT_FINAL",
            "Evidence version must be final before external submission",
            status_code=409,
        )
    _require_independent_approval(version)
    expected_current_identity = f"{command.case_id}|{version.lineage_key}"
    if version.current_identity_key != expected_current_identity:
        raise_business_error(
            "EXTERNAL_SUBMISSION_NOT_CURRENT",
            "Evidence version must be current before external submission",
            status_code=409,
        )
    if version.final_submitted_at is not None:
        raise_business_error(
            "EXTERNAL_SUBMISSION_ALREADY_FINALIZED",
            "Evidence version already has an external submission result",
            status_code=409,
        )

    changed = transaction.execute(
        update(DocumentEvidenceVersion)
        .where(
            DocumentEvidenceVersion.id == version.id,
            DocumentEvidenceVersion.case_id == command.case_id,
            DocumentEvidenceVersion.role == version.role,
            DocumentEvidenceVersion.state == EvidenceVersionState.FINAL.value,
            DocumentEvidenceVersion.review_state == EvidenceReviewState.APPROVED.value,
            DocumentEvidenceVersion.reviewer_id == version.reviewer_id,
            DocumentEvidenceVersion.reviewed_at == version.reviewed_at,
            DocumentEvidenceVersion.current_identity_key == expected_current_identity,
            DocumentEvidenceVersion.final_submitted_at.is_(None),
        )
        .values(
            final_submitted_at=command.submitted_at,
            updated_at=command.submitted_at,
        )
        .execution_options(synchronize_session=False)
    )
    if changed.rowcount != 1:
        raise_business_error(
            "EXTERNAL_SUBMISSION_CONCURRENCY_CONFLICT",
            "Evidence submission state changed concurrently",
            status_code=409,
        )
    transaction.expire(version, ["final_submitted_at", "updated_at"])

    activity_result = append_case_activity(
        activity_command,
        transaction,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=legacy_case_status,
        conflict_codes=(),
    )
    return _result(
        command,
        version,
        activity_id=activity_result.activity_id,
        sequence=activity_result.sequence,
        lifecycle_revision=activity_result.lifecycle_revision,
        reused=False,
    )


__all__ = (
    "FinalizeExternalSubmissionCommand",
    "SubmissionEvidenceResult",
    "finalize_external_submission",
)
