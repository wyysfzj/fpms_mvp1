from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.cases.lifecycle_activity_service import append_case_activity
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    LifecycleProjection,
    OfficialProcedureStage,
)
from app.modules.cases.models import Case, CaseActivityEvent
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationResult,
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
    RegisterEvidenceDerivationCommand,
    RegisterEvidenceVersionCommand,
)
from app.modules.documents.models import (
    DocAttachment,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)

_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_REGISTERABLE_EVIDENCE_ROLE_VALUES = frozenset(
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
        "RAW_ATTACHMENT",
        "GENERATED_ATTACHMENT",
        "OA_STRUCTURED_ATTACHMENT",
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SwitchCurrentEvidenceVersionCommand:
    case_id: str
    expected_current_evidence_version_id: str
    target_evidence_version_id: str
    actor_id: str
    switched_at: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SwitchCurrentEvidenceVersionResult:
    case_id: str
    lineage_key: str
    previous_current_evidence_version_id: str
    current_evidence_version_id: str
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    switched_at: datetime
    idempotency_key: str
    reused: bool


class EvidenceReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewEvidenceVersionCommand:
    case_id: str
    evidence_version_id: str
    reviewer_id: str
    decision: EvidenceReviewDecision
    reviewed_at: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewEvidenceVersionResult:
    case_id: str
    evidence_version_id: str
    creator_id: str
    reviewer_id: str
    decision: EvidenceReviewDecision
    review_state: EvidenceReviewState
    reviewed_at: datetime
    activity_id: str
    activity_sequence: int
    lifecycle_revision: int
    idempotency_key: str
    reused: bool


def _require_text(value: object, *, field: str, max_length: int) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise_business_error(
            "EVIDENCE_VERSION_INVALID",
            f"{field} must be non-empty and at most {max_length} characters",
            details={"field": field},
            status_code=400,
        )


def _validate_register_command(command: RegisterEvidenceVersionCommand) -> None:
    if type(command) is not RegisterEvidenceVersionCommand:
        raise_business_error(
            "EVIDENCE_VERSION_INVALID",
            "command must be a RegisterEvidenceVersionCommand",
            details={"field": "command"},
            status_code=400,
        )
    _require_text(command.case_id, field="case_id", max_length=36)
    _require_text(command.document_id, field="document_id", max_length=36)
    _require_text(command.attachment_id, field="attachment_id", max_length=36)
    _require_text(command.lineage_key, field="lineage_key", max_length=128)
    _require_text(command.creator_id, field="creator_id", max_length=36)
    if type(command.role) is not EvidenceRole:
        raise_business_error(
            "EVIDENCE_VERSION_INVALID",
            "role must be an EvidenceRole",
            details={"field": "role"},
            status_code=400,
        )
    if type(command.state) is not EvidenceVersionState:
        raise_business_error(
            "EVIDENCE_VERSION_INVALID",
            "state must be an EvidenceVersionState",
            details={"field": "state"},
            status_code=400,
        )
    if not isinstance(command.content_hash, str) or not _CONTENT_HASH_PATTERN.fullmatch(
        command.content_hash
    ):
        raise_business_error(
            "EVIDENCE_VERSION_INVALID",
            "content_hash must use lowercase SHA-256 wire format",
            details={"field": "content_hash"},
            status_code=400,
        )


def _validate_register_role_state(command: RegisterEvidenceVersionCommand) -> None:
    role_value = command.role.value
    if role_value not in _REGISTERABLE_EVIDENCE_ROLE_VALUES:
        raise_business_error(
            "EVIDENCE_VERSION_INVALID",
            "role is not allowed for evidence version registration",
            details={"field": "role"},
            status_code=400,
        )
    if (
        role_value
        in {
            "RAW_ATTACHMENT",
            "GENERATED_ATTACHMENT",
        }
        and command.state is not EvidenceVersionState.DRAFT
    ):
        raise_business_error(
            "EVIDENCE_VERSION_INVALID",
            "RAW_ATTACHMENT evidence versions must be registered as DRAFT",
            details={"field": "state"},
            status_code=400,
        )


def _capture_lifecycle_projection(case: Case) -> LifecycleProjection:
    try:
        return LifecycleProjection(
            business_stage=(
                BusinessStage(case.business_stage) if case.business_stage is not None else None
            ),
            official_procedure_stage=(
                OfficialProcedureStage(case.official_procedure_stage)
                if case.official_procedure_stage is not None
                else None
            ),
            legal_status=LegalStatus(case.legal_status) if case.legal_status is not None else None,
            lifecycle_verification_status=(
                ConfirmationStatus(case.lifecycle_verification_status)
                if case.lifecycle_verification_status is not None
                else None
            ),
        )
    except ValueError:
        raise_business_error(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "Stored lifecycle projection is invalid",
            status_code=409,
        )


def register_evidence_version(
    command: RegisterEvidenceVersionCommand,
    transaction: Session,
) -> EvidenceVersionResult:
    _validate_register_command(command)
    _validate_register_role_state(command)

    case = transaction.get(Case, command.case_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    document = transaction.get(Document, command.document_id)
    if document is None:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)
    if document.case_id != command.case_id:
        raise_business_error(
            "DOCUMENT_CASE_MISMATCH",
            "Document does not belong to the requested case",
            status_code=400,
        )

    attachment = transaction.get(DocAttachment, command.attachment_id)
    if attachment is None:
        raise_business_error("ATTACHMENT_NOT_FOUND", "Attachment not found", status_code=404)
    if attachment.document_id != command.document_id:
        raise_business_error(
            "ATTACHMENT_DOCUMENT_MISMATCH",
            "Attachment does not belong to the requested document",
            status_code=400,
        )

    projection = _capture_lifecycle_projection(case)
    legacy_case_status = case.status

    largest_version = transaction.scalar(
        select(func.max(DocumentEvidenceVersion.version_number)).where(
            DocumentEvidenceVersion.case_id == command.case_id,
            DocumentEvidenceVersion.lineage_key == command.lineage_key,
        )
    )
    version_number = max(largest_version or 0, 0) + 1

    current_identity = f"{command.case_id}|{command.lineage_key}"
    current_exists = transaction.scalar(
        select(DocumentEvidenceVersion.id)
        .where(DocumentEvidenceVersion.current_identity_key == current_identity)
        .limit(1)
    )
    stored_current_identity = None if current_exists is not None else current_identity

    version = DocumentEvidenceVersion(
        id=str(uuid4()),
        case_id=command.case_id,
        document_id=command.document_id,
        attachment_id=command.attachment_id,
        lineage_key=command.lineage_key,
        role=command.role.value,
        version_number=version_number,
        state=command.state.value,
        creator_id=command.creator_id,
        review_state=EvidenceReviewState.PENDING.value,
        reviewer_id=None,
        reviewed_at=None,
        final_submitted_at=None,
        content_hash=command.content_hash,
        current_identity_key=stored_current_identity,
    )
    transaction.add(version)
    transaction.flush()
    if version.created_at is None:
        transaction.refresh(version, attribute_names=["created_at"])

    append_case_activity(
        LifecycleEventCommand(
            case_id=version.case_id,
            event_type="DOCUMENT_EVIDENCE_VERSION_REGISTERED",
            lane=ActivityLane.DOCUMENT,
            effective_at=version.created_at,
            occurred_at=version.created_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=version.case_id,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=version.id,
                    content_hash=version.content_hash,
                    captured_at=version.created_at,
                ),
            ),
            actor_id=version.creator_id,
            reviewer_id=None,
            idempotency_key=f"document-evidence-version:{version.id}",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "evidence_version_id": version.id,
                "document_id": version.document_id,
                "attachment_id": version.attachment_id,
                "lineage_key": version.lineage_key,
                "role": version.role,
                "version_number": version.version_number,
                "state": version.state,
                "review_state": version.review_state,
            },
        ),
        transaction,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=legacy_case_status,
        conflict_codes=(),
    )

    return EvidenceVersionResult(
        evidence_version_id=version.id,
        case_id=version.case_id,
        document_id=version.document_id,
        attachment_id=version.attachment_id,
        lineage_key=version.lineage_key,
        role=EvidenceRole(version.role),
        version_number=version.version_number,
        state=EvidenceVersionState(version.state),
        creator_id=version.creator_id,
        review_state=EvidenceReviewState(version.review_state),
        reviewer_id=version.reviewer_id,
        reviewed_at=version.reviewed_at,
        final_submitted_at=version.final_submitted_at,
        content_hash=version.content_hash,
        is_current=version.current_identity_key is not None,
        is_final=command.state is EvidenceVersionState.FINAL,
    )


def _require_derivation_text(value: object, *, field: str, max_length: int) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise_business_error(
            "EVIDENCE_DERIVATION_INVALID",
            f"{field} must be non-empty and at most {max_length} characters",
            details={"field": field},
            status_code=400,
        )


def _reject_nonfinite_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _validate_derivation_command(command: RegisterEvidenceDerivationCommand) -> None:
    _require_derivation_text(command.case_id, field="case_id", max_length=36)
    _require_derivation_text(
        command.parent_evidence_version_id,
        field="parent_evidence_version_id",
        max_length=36,
    )
    _require_derivation_text(
        command.child_evidence_version_id,
        field="child_evidence_version_id",
        max_length=36,
    )
    _require_derivation_text(command.actor_id, field="actor_id", max_length=36)
    if type(command.derivation_type) is not EvidenceDerivationType:
        raise_business_error(
            "EVIDENCE_DERIVATION_INVALID",
            "derivation_type must be an EvidenceDerivationType",
            details={"field": "derivation_type"},
            status_code=400,
        )
    if not isinstance(command.derived_at, datetime) or command.derived_at.tzinfo is not None:
        raise_business_error(
            "EVIDENCE_DERIVATION_INVALID",
            "derived_at must be a timezone-naive datetime",
            details={"field": "derived_at"},
            status_code=400,
        )
    if not isinstance(command.source_snapshot, str):
        raise_business_error(
            "EVIDENCE_DERIVATION_INVALID",
            "source_snapshot must be canonical JSON object text",
            details={"field": "source_snapshot"},
            status_code=400,
        )
    try:
        snapshot = json.loads(
            command.source_snapshot,
            parse_constant=_reject_nonfinite_json_constant,
        )
        canonical_snapshot = json.dumps(
            snapshot,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        raise_business_error(
            "EVIDENCE_DERIVATION_INVALID",
            "source_snapshot must be canonical JSON object text",
            details={"field": "source_snapshot"},
            status_code=400,
        )
    if not isinstance(snapshot, dict) or command.source_snapshot != canonical_snapshot:
        raise_business_error(
            "EVIDENCE_DERIVATION_INVALID",
            "source_snapshot must be canonical JSON object text",
            details={"field": "source_snapshot"},
            status_code=400,
        )


def register_evidence_derivation(
    command: RegisterEvidenceDerivationCommand,
    transaction: Session,
) -> EvidenceDerivationResult:
    _validate_derivation_command(command)

    if command.parent_evidence_version_id == command.child_evidence_version_id:
        raise_business_error(
            "EVIDENCE_DERIVATION_SELF_REFERENCE",
            "Parent and child evidence versions must differ",
            status_code=400,
        )

    parent = transaction.get(
        DocumentEvidenceVersion,
        command.parent_evidence_version_id,
    )
    if parent is None:
        raise_business_error(
            "PARENT_EVIDENCE_VERSION_NOT_FOUND",
            "Parent evidence version not found",
            status_code=404,
        )

    child = transaction.get(
        DocumentEvidenceVersion,
        command.child_evidence_version_id,
    )
    if child is None:
        raise_business_error(
            "CHILD_EVIDENCE_VERSION_NOT_FOUND",
            "Child evidence version not found",
            status_code=404,
        )

    if parent.case_id != child.case_id or parent.case_id != command.case_id:
        raise_business_error(
            "EVIDENCE_DERIVATION_CASE_MISMATCH",
            "Parent and child evidence versions must belong to the requested case",
            status_code=400,
        )

    case = transaction.get(Case, command.case_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    projection = _capture_lifecycle_projection(case)
    legacy_case_status = case.status
    derivation_id = str(uuid4())
    derivation = DocumentEvidenceDerivation(
        id=derivation_id,
        case_id=command.case_id,
        parent_evidence_version_id=command.parent_evidence_version_id,
        child_evidence_version_id=command.child_evidence_version_id,
        derivation_type=command.derivation_type.value,
        actor_id=command.actor_id,
        derived_at=command.derived_at,
        source_snapshot=command.source_snapshot,
    )
    transaction.add(derivation)
    transaction.flush()

    append_case_activity(
        LifecycleEventCommand(
            case_id=command.case_id,
            event_type="DOCUMENT_EVIDENCE_DERIVATION_REGISTERED",
            lane=ActivityLane.DOCUMENT,
            effective_at=command.derived_at,
            occurred_at=command.derived_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=command.case_id,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=parent.id,
                    content_hash=parent.content_hash,
                    captured_at=command.derived_at,
                ),
                EvidenceReference(
                    case_id=command.case_id,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=child.id,
                    content_hash=child.content_hash,
                    captured_at=command.derived_at,
                ),
            ),
            actor_id=command.actor_id,
            reviewer_id=None,
            idempotency_key=f"document-derivation:{derivation_id}",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "evidence_derivation_id": derivation_id,
                "parent_evidence_version_id": command.parent_evidence_version_id,
                "child_evidence_version_id": command.child_evidence_version_id,
                "derivation_type": command.derivation_type.value,
                "source_snapshot": command.source_snapshot,
            },
        ),
        transaction,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=legacy_case_status,
        conflict_codes=(),
    )

    return EvidenceDerivationResult(
        evidence_derivation_id=derivation.id,
        case_id=derivation.case_id,
        parent_evidence_version_id=derivation.parent_evidence_version_id,
        child_evidence_version_id=derivation.child_evidence_version_id,
        derivation_type=EvidenceDerivationType(derivation.derivation_type),
        actor_id=derivation.actor_id,
        derived_at=derivation.derived_at,
        source_snapshot=derivation.source_snapshot,
    )


def _current_invalid(field: str) -> None:
    raise_business_error(
        "EVIDENCE_CURRENT_INVALID",
        f"Invalid current-version switch field: {field}",
        details={"field": field},
        status_code=400,
    )


def _require_current_text(value: object, *, field: str, max_length: int) -> None:
    if type(value) is not str or not value.strip() or len(value) > max_length:
        _current_invalid(field)


def _validate_switch_current_command(command: SwitchCurrentEvidenceVersionCommand) -> None:
    if type(command) is not SwitchCurrentEvidenceVersionCommand:
        _current_invalid("command")
    _require_current_text(command.case_id, field="case_id", max_length=36)
    _require_current_text(
        command.expected_current_evidence_version_id,
        field="expected_current_evidence_version_id",
        max_length=36,
    )
    _require_current_text(
        command.target_evidence_version_id,
        field="target_evidence_version_id",
        max_length=36,
    )
    _require_current_text(command.actor_id, field="actor_id", max_length=36)
    if type(command.switched_at) is not datetime or command.switched_at.tzinfo is not None:
        _current_invalid("switched_at")
    _require_current_text(command.idempotency_key, field="idempotency_key", max_length=100)
    if command.expected_current_evidence_version_id == command.target_evidence_version_id:
        _current_invalid("target_evidence_version_id")


def _current_evidence_references(
    command: SwitchCurrentEvidenceVersionCommand,
    expected: DocumentEvidenceVersion,
    target: DocumentEvidenceVersion,
) -> tuple[EvidenceReference, EvidenceReference]:
    return (
        EvidenceReference(
            case_id=command.case_id,
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id=expected.id,
            content_hash=expected.content_hash,
            captured_at=command.switched_at,
        ),
        EvidenceReference(
            case_id=command.case_id,
            evidence_kind="DOCUMENT_EVIDENCE_VERSION",
            object_type="DocumentEvidenceVersion",
            object_id=target.id,
            content_hash=target.content_hash,
            captured_at=command.switched_at,
        ),
    )


def _current_switch_activity_command(
    command: SwitchCurrentEvidenceVersionCommand,
    expected: DocumentEvidenceVersion,
    target: DocumentEvidenceVersion,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=command.case_id,
        event_type="DOCUMENT_EVIDENCE_CURRENT_VERSION_SWITCHED",
        lane=ActivityLane.DOCUMENT,
        effective_at=command.switched_at,
        occurred_at=command.switched_at,
        evidence_refs=_current_evidence_references(command, expected, target),
        actor_id=command.actor_id,
        reviewer_id=None,
        idempotency_key=f"document-current-version:{command.idempotency_key}",
        source_activity_id=None,
        supersedes_event_id=None,
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={
            "current_evidence_version_id": target.id,
            "lineage_key": target.lineage_key,
            "previous_current_evidence_version_id": expected.id,
        },
    )


def _stored_activity_projection(
    activity: CaseActivityEvent,
    *,
    old: bool,
    verification_status: ConfirmationStatus | None,
) -> LifecycleProjection:
    try:
        return LifecycleProjection(
            business_stage=(
                BusinessStage(activity.old_business_stage)
                if old and activity.old_business_stage is not None
                else BusinessStage(activity.new_business_stage)
                if not old and activity.new_business_stage is not None
                else None
            ),
            official_procedure_stage=(
                OfficialProcedureStage(activity.old_official_procedure_stage)
                if old and activity.old_official_procedure_stage is not None
                else OfficialProcedureStage(activity.new_official_procedure_stage)
                if not old and activity.new_official_procedure_stage is not None
                else None
            ),
            legal_status=(
                LegalStatus(activity.old_legal_status)
                if old and activity.old_legal_status is not None
                else LegalStatus(activity.new_legal_status)
                if not old and activity.new_legal_status is not None
                else None
            ),
            lifecycle_verification_status=verification_status,
        )
    except ValueError:
        raise_business_error(
            "LIFECYCLE_PROJECTION_CONFLICT",
            "Stored lifecycle activity projection is invalid",
            status_code=409,
        )


def _current_switch_result(
    command: SwitchCurrentEvidenceVersionCommand,
    *,
    lineage_key: str,
    activity_id: str,
    sequence: int,
    lifecycle_revision: int,
    reused: bool,
) -> SwitchCurrentEvidenceVersionResult:
    return SwitchCurrentEvidenceVersionResult(
        case_id=command.case_id,
        lineage_key=lineage_key,
        previous_current_evidence_version_id=(command.expected_current_evidence_version_id),
        current_evidence_version_id=command.target_evidence_version_id,
        activity_id=activity_id,
        activity_sequence=sequence,
        lifecycle_revision=lifecycle_revision,
        switched_at=command.switched_at,
        idempotency_key=command.idempotency_key,
        reused=reused,
    )


def switch_current_evidence_version(
    command: SwitchCurrentEvidenceVersionCommand,
    transaction: Session,
) -> SwitchCurrentEvidenceVersionResult:
    _validate_switch_current_command(command)

    case = transaction.get(Case, command.case_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    expected = transaction.get(
        DocumentEvidenceVersion,
        command.expected_current_evidence_version_id,
    )
    if expected is None:
        raise_business_error(
            "EXPECTED_EVIDENCE_VERSION_NOT_FOUND",
            "Expected current evidence version not found",
            status_code=404,
        )
    target = transaction.get(
        DocumentEvidenceVersion,
        command.target_evidence_version_id,
    )
    if target is None:
        raise_business_error(
            "TARGET_EVIDENCE_VERSION_NOT_FOUND",
            "Target evidence version not found",
            status_code=404,
        )

    if expected.case_id != command.case_id or target.case_id != command.case_id:
        raise_business_error(
            "EVIDENCE_CURRENT_CASE_MISMATCH",
            "Evidence versions do not belong to the requested case",
            status_code=400,
        )
    if (
        type(expected.lineage_key) is not str
        or not expected.lineage_key.strip()
        or type(target.lineage_key) is not str
        or not target.lineage_key.strip()
        or expected.lineage_key != target.lineage_key
    ):
        raise_business_error(
            "EVIDENCE_CURRENT_LINEAGE_MISMATCH",
            "Evidence versions do not share a lineage",
            status_code=409,
        )

    current_projection = _capture_lifecycle_projection(case)
    legacy_case_status = case.status
    activity_key = f"document-current-version:{command.idempotency_key}"
    existing_activity = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == command.case_id,
            CaseActivityEvent.idempotency_key == activity_key,
        )
    )
    activity_command = _current_switch_activity_command(command, expected, target)
    if existing_activity is not None:
        activity_result = append_case_activity(
            activity_command,
            transaction,
            previous_projection=_stored_activity_projection(
                existing_activity,
                old=True,
                verification_status=(current_projection.lifecycle_verification_status),
            ),
            current_projection=_stored_activity_projection(
                existing_activity,
                old=False,
                verification_status=(current_projection.lifecycle_verification_status),
            ),
            legacy_case_status=legacy_case_status,
            conflict_codes=(),
        )
        return _current_switch_result(
            command,
            lineage_key=target.lineage_key,
            activity_id=activity_result.activity_id,
            sequence=activity_result.sequence,
            lifecycle_revision=activity_result.lifecycle_revision,
            reused=activity_result.reused,
        )

    try:
        EvidenceVersionState(expected.state)
        EvidenceReviewState(expected.review_state)
        EvidenceVersionState(target.state)
        target_review_state = EvidenceReviewState(target.review_state)
    except (TypeError, ValueError):
        raise_business_error(
            "EVIDENCE_CURRENT_STATE_CONFLICT",
            "Stored evidence version state is invalid",
            status_code=409,
        )
    if target_review_state is EvidenceReviewState.REJECTED:
        raise_business_error(
            "EVIDENCE_CURRENT_REJECTED",
            "A rejected evidence version cannot become current",
            status_code=409,
        )

    current_identity = f"{command.case_id}|{expected.lineage_key}"
    holder_ids = transaction.scalars(
        select(DocumentEvidenceVersion.id).where(
            DocumentEvidenceVersion.current_identity_key == current_identity
        )
    ).all()
    if not holder_ids:
        raise_business_error(
            "EVIDENCE_CURRENT_NOT_FOUND",
            "Current evidence version is not set",
            status_code=409,
        )
    if holder_ids != [expected.id] or target.current_identity_key is not None:
        raise_business_error(
            "EVIDENCE_CURRENT_CONFLICT",
            "Current evidence version does not match the expected identity",
            status_code=409,
        )

    receipt_link_exists = transaction.scalar(
        select(DocumentEvidenceDerivation.id)
        .where(
            DocumentEvidenceDerivation.case_id == command.case_id,
            DocumentEvidenceDerivation.parent_evidence_version_id == expected.id,
            DocumentEvidenceDerivation.derivation_type == EvidenceDerivationType.RECEIPT_LINK.value,
        )
        .limit(1)
    )
    if expected.state == EvidenceVersionState.FINAL.value and receipt_link_exists is not None:
        raise_business_error(
            "EVIDENCE_CURRENT_RECEIPT_LOCKED",
            "A receipt-linked final evidence version cannot be replaced",
            status_code=409,
        )

    cleared = transaction.execute(
        update(DocumentEvidenceVersion)
        .where(
            DocumentEvidenceVersion.id == expected.id,
            DocumentEvidenceVersion.current_identity_key == current_identity,
        )
        .values(current_identity_key=None)
        .execution_options(synchronize_session=False)
    )
    if cleared.rowcount != 1:
        raise_business_error(
            "EVIDENCE_CURRENT_CONCURRENCY_CONFLICT",
            "Current evidence version changed concurrently",
            status_code=409,
        )
    transaction.flush()

    assigned = transaction.execute(
        update(DocumentEvidenceVersion)
        .where(
            DocumentEvidenceVersion.id == target.id,
            DocumentEvidenceVersion.current_identity_key.is_(None),
        )
        .values(current_identity_key=current_identity)
        .execution_options(synchronize_session=False)
    )
    if assigned.rowcount != 1:
        raise_business_error(
            "EVIDENCE_CURRENT_CONCURRENCY_CONFLICT",
            "Target evidence version changed concurrently",
            status_code=409,
        )
    transaction.expire(expected, ["current_identity_key"])
    transaction.expire(target, ["current_identity_key"])

    activity_result = append_case_activity(
        activity_command,
        transaction,
        previous_projection=current_projection,
        current_projection=current_projection,
        legacy_case_status=legacy_case_status,
        conflict_codes=(),
    )
    return _current_switch_result(
        command,
        lineage_key=target.lineage_key,
        activity_id=activity_result.activity_id,
        sequence=activity_result.sequence,
        lifecycle_revision=activity_result.lifecycle_revision,
        reused=activity_result.reused,
    )


def _review_invalid(field: str) -> None:
    raise_business_error(
        "EVIDENCE_REVIEW_INVALID",
        f"Invalid evidence review field: {field}",
        details={"field": field},
        status_code=400,
    )


def _require_review_text(value: object, *, field: str, max_length: int) -> None:
    if type(value) is not str or not value.strip() or len(value) > max_length:
        _review_invalid(field)


def _validate_review_command(command: ReviewEvidenceVersionCommand) -> None:
    if type(command) is not ReviewEvidenceVersionCommand:
        _review_invalid("command")
    _require_review_text(command.case_id, field="case_id", max_length=36)
    _require_review_text(
        command.evidence_version_id,
        field="evidence_version_id",
        max_length=36,
    )
    _require_review_text(command.reviewer_id, field="reviewer_id", max_length=36)
    if type(command.decision) is not EvidenceReviewDecision:
        _review_invalid("decision")
    if type(command.reviewed_at) is not datetime or command.reviewed_at.tzinfo is not None:
        _review_invalid("reviewed_at")
    _require_review_text(command.idempotency_key, field="idempotency_key", max_length=103)


def _review_state_conflict() -> None:
    raise_business_error(
        "EVIDENCE_REVIEW_STATE_CONFLICT",
        "Stored evidence review state is invalid",
        status_code=409,
    )


def _validate_review_version_carrier(version: DocumentEvidenceVersion) -> None:
    if (
        type(version.creator_id) is not str
        or not version.creator_id.strip()
        or len(version.creator_id) > 36
        or type(version.content_hash) is not str
        or _CONTENT_HASH_PATTERN.fullmatch(version.content_hash) is None
        or type(version.state) is not str
    ):
        _review_state_conflict()
    try:
        EvidenceVersionState(version.state)
    except ValueError:
        _review_state_conflict()


def _review_activity_command(
    command: ReviewEvidenceVersionCommand,
    version: DocumentEvidenceVersion,
    review_state: EvidenceReviewState,
) -> LifecycleEventCommand:
    return LifecycleEventCommand(
        case_id=command.case_id,
        event_type="DOCUMENT_EVIDENCE_REVIEW_DECIDED",
        lane=ActivityLane.DOCUMENT,
        effective_at=command.reviewed_at,
        occurred_at=command.reviewed_at,
        evidence_refs=(
            EvidenceReference(
                case_id=command.case_id,
                evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                object_type="DocumentEvidenceVersion",
                object_id=version.id,
                content_hash=version.content_hash,
                captured_at=command.reviewed_at,
            ),
        ),
        actor_id=command.reviewer_id,
        reviewer_id=command.reviewer_id,
        idempotency_key=f"document-evidence-review:{command.idempotency_key}",
        source_activity_id=None,
        supersedes_event_id=None,
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload={
            "creator_id": version.creator_id,
            "decision": command.decision.value,
            "evidence_version_id": version.id,
            "previous_review_state": EvidenceReviewState.PENDING.value,
            "review_state": review_state.value,
            "reviewer_id": command.reviewer_id,
        },
    )


def _review_result(
    command: ReviewEvidenceVersionCommand,
    version: DocumentEvidenceVersion,
    *,
    review_state: EvidenceReviewState,
    activity_id: str,
    sequence: int,
    lifecycle_revision: int,
    reused: bool,
) -> ReviewEvidenceVersionResult:
    return ReviewEvidenceVersionResult(
        case_id=command.case_id,
        evidence_version_id=version.id,
        creator_id=version.creator_id,
        reviewer_id=command.reviewer_id,
        decision=command.decision,
        review_state=review_state,
        reviewed_at=command.reviewed_at,
        activity_id=activity_id,
        activity_sequence=sequence,
        lifecycle_revision=lifecycle_revision,
        idempotency_key=command.idempotency_key,
        reused=reused,
    )


def _review_tuple_is_consistent(
    version: DocumentEvidenceVersion,
    review_state: EvidenceReviewState,
) -> bool:
    if review_state is EvidenceReviewState.PENDING:
        return version.reviewer_id is None and version.reviewed_at is None
    return (
        type(version.reviewer_id) is str
        and bool(version.reviewer_id.strip())
        and len(version.reviewer_id) <= 36
        and type(version.reviewed_at) is datetime
        and version.reviewed_at.tzinfo is None
    )


def review_evidence_version(
    command: ReviewEvidenceVersionCommand,
    transaction: Session,
) -> ReviewEvidenceVersionResult:
    _validate_review_command(command)

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
            "EVIDENCE_REVIEW_CASE_MISMATCH",
            "Evidence version does not belong to the requested case",
            status_code=400,
        )

    _validate_review_version_carrier(version)
    if command.reviewer_id == version.creator_id:
        raise_business_error(
            "EVIDENCE_REVIEW_SELF_REVIEW",
            "Evidence creator cannot review the same version",
            status_code=409,
        )

    current_projection = _capture_lifecycle_projection(case)
    legacy_case_status = case.status
    review_state = (
        EvidenceReviewState.APPROVED
        if command.decision is EvidenceReviewDecision.APPROVE
        else EvidenceReviewState.REJECTED
    )
    activity_key = f"document-evidence-review:{command.idempotency_key}"
    existing_activity = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == command.case_id,
            CaseActivityEvent.idempotency_key == activity_key,
        )
    )
    activity_command = _review_activity_command(command, version, review_state)
    if existing_activity is not None:
        previous_projection = _stored_activity_projection(
            existing_activity,
            old=True,
            verification_status=current_projection.lifecycle_verification_status,
        )
        stored_current_projection = _stored_activity_projection(
            existing_activity,
            old=False,
            verification_status=current_projection.lifecycle_verification_status,
        )
        if previous_projection != stored_current_projection:
            raise_business_error(
                "EVIDENCE_REVIEW_HISTORY_CONFLICT",
                "Stored review activity changed the central lifecycle projection",
                status_code=409,
            )
        activity_result = append_case_activity(
            activity_command,
            transaction,
            previous_projection=previous_projection,
            current_projection=stored_current_projection,
            legacy_case_status=legacy_case_status,
            conflict_codes=(),
        )
        if (
            version.review_state != review_state.value
            or version.reviewer_id != command.reviewer_id
            or version.reviewed_at != command.reviewed_at
        ):
            raise_business_error(
                "EVIDENCE_REVIEW_HISTORY_CONFLICT",
                "Evidence review carrier disagrees with its activity",
                status_code=409,
            )
        return _review_result(
            command,
            version,
            review_state=review_state,
            activity_id=activity_result.activity_id,
            sequence=activity_result.sequence,
            lifecycle_revision=activity_result.lifecycle_revision,
            reused=True,
        )

    if type(version.review_state) is not str:
        _review_state_conflict()
    try:
        stored_review_state = EvidenceReviewState(version.review_state)
    except ValueError:
        _review_state_conflict()
    if not _review_tuple_is_consistent(version, stored_review_state):
        _review_state_conflict()
    if stored_review_state is not EvidenceReviewState.PENDING:
        raise_business_error(
            "EVIDENCE_REVIEW_ALREADY_DECIDED",
            "Evidence review decision is already terminal",
            status_code=409,
        )

    changed = transaction.execute(
        update(DocumentEvidenceVersion)
        .where(
            DocumentEvidenceVersion.id == version.id,
            DocumentEvidenceVersion.case_id == command.case_id,
            DocumentEvidenceVersion.review_state == EvidenceReviewState.PENDING.value,
            DocumentEvidenceVersion.reviewer_id.is_(None),
            DocumentEvidenceVersion.reviewed_at.is_(None),
        )
        .values(
            review_state=review_state.value,
            reviewer_id=command.reviewer_id,
            reviewed_at=command.reviewed_at,
            updated_at=command.reviewed_at,
        )
        .execution_options(synchronize_session=False)
    )
    if changed.rowcount != 1:
        raise_business_error(
            "EVIDENCE_REVIEW_CONCURRENCY_CONFLICT",
            "Evidence review state changed concurrently",
            status_code=409,
        )
    transaction.expire(
        version,
        ["review_state", "reviewer_id", "reviewed_at", "updated_at"],
    )

    activity_result = append_case_activity(
        activity_command,
        transaction,
        previous_projection=current_projection,
        current_projection=current_projection,
        legacy_case_status=legacy_case_status,
        conflict_codes=(),
    )
    return _review_result(
        command,
        version,
        review_state=review_state,
        activity_id=activity_result.activity_id,
        sequence=activity_result.sequence,
        lifecycle_revision=activity_result.lifecycle_revision,
        reused=False,
    )
