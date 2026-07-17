from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
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
from app.modules.cases.models import Case, CaseActivityEvent, CaseActivityEventEvidence
from app.modules.documents.evidence_contracts import (
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionState,
    RegisterEvidenceDerivationCommand,
    RegisterEvidenceVersionCommand,
)
from app.modules.documents.evidence_service import (
    register_evidence_derivation,
    register_evidence_version,
)
from app.modules.documents.models import (
    DocAttachment,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)

_PERMITTED_MANIFEST_ROLES = frozenset(
    {
        "OA_STATEMENT_WORD",
        "OA_MODIFIED_CLAIMS",
        "OA_AMENDMENT_COMPARISON",
        "OA_OTHER_PROOF",
        "OA_ADDITIONAL_FILE",
    }
)
_CARRIER_KEYS = frozenset(
    {
        "actor_id",
        "case_id",
        "command_idempotency_key",
        "manifest_id",
        "manifest_role",
        "package_id",
        "promoted_at",
        "promotion_identity_key",
        "raw_content_hash",
        "raw_evidence_version_id",
        "schema",
        "target_state",
        "typed_content_hash",
        "typed_evidence_version_id",
    }
)
_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")


@dataclass(frozen=True, slots=True, kw_only=True)
class PromoteOaStructuredAttachmentCommand:
    case_id: str
    package_id: str
    manifest_id: str
    raw_evidence_version_id: str
    target_state: EvidenceVersionState
    actor_id: str
    promoted_at: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class PromoteOaStructuredAttachmentResult:
    typed_evidence_version_id: str
    evidence_derivation_id: str
    activity_id: str
    promotion_identity_key: str
    reused: bool


def _invalid(field: str) -> None:
    raise_business_error(
        "OA_ATTACHMENT_PROMOTION_INVALID",
        f"Invalid OA attachment promotion field: {field}",
        details={"field": field},
        status_code=400,
    )


def _conflict(message: str) -> None:
    raise_business_error(
        "OA_ATTACHMENT_PROMOTION_CONFLICT",
        message,
        status_code=409,
    )


def _validate_command(command: PromoteOaStructuredAttachmentCommand) -> None:
    if type(command) is not PromoteOaStructuredAttachmentCommand:
        _invalid("command")
    for field in (
        "case_id",
        "package_id",
        "manifest_id",
        "raw_evidence_version_id",
        "actor_id",
    ):
        value = getattr(command, field)
        if type(value) is not str or not value.strip() or len(value) > 36:
            _invalid(field)
    if type(command.target_state) is not EvidenceVersionState:
        _invalid("target_state")
    if command.target_state not in {
        EvidenceVersionState.DRAFT,
        EvidenceVersionState.FINAL,
    }:
        _invalid("target_state")
    if type(command.promoted_at) is not datetime or command.promoted_at.tzinfo is not None:
        _invalid("promoted_at")
    if (
        type(command.idempotency_key) is not str
        or not command.idempotency_key.strip()
        or len(command.idempotency_key) > 103
    ):
        _invalid("idempotency_key")


def _validate_lookup_identity(command: PromoteOaStructuredAttachmentCommand) -> None:
    if type(command) is not PromoteOaStructuredAttachmentCommand:
        _invalid("command")
    if type(command.case_id) is not str or not command.case_id.strip() or len(command.case_id) > 36:
        _invalid("case_id")
    if (
        type(command.idempotency_key) is not str
        or not command.idempotency_key.strip()
        or len(command.idempotency_key) > 103
    ):
        _invalid("idempotency_key")


def _validate_replay_command_shape(command: PromoteOaStructuredAttachmentCommand) -> None:
    text_fields = (
        command.package_id,
        command.manifest_id,
        command.raw_evidence_version_id,
        command.actor_id,
    )
    if any(type(value) is not str or not value.strip() or len(value) > 36 for value in text_fields):
        _conflict("Promotion replay command identity is invalid")
    if type(command.target_state) is not EvidenceVersionState:
        _conflict("Promotion replay target state is invalid")
    if type(command.promoted_at) is not datetime or command.promoted_at.tzinfo is not None:
        _conflict("Promotion replay promoted time is invalid")


def _canonical_json(value: dict[str, str]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _projection(case: Case) -> LifecycleProjection:
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
        _conflict("Stored lifecycle projection is invalid")


def _load_fresh_carriers(
    command: PromoteOaStructuredAttachmentCommand,
    transaction: Session,
) -> tuple[
    Case,
    OfficialWorkPackageManifest,
    DocumentEvidenceVersion,
    DocAttachment,
    str,
]:
    case = transaction.get(Case, command.case_id)
    package = transaction.get(OfficialWorkPackage, command.package_id)
    manifest = transaction.get(OfficialWorkPackageManifest, command.manifest_id)
    parent = transaction.get(DocumentEvidenceVersion, command.raw_evidence_version_id)
    if case is None or package is None or manifest is None or parent is None:
        _conflict("Required OA promotion carrier is missing")
    if package.case_id != command.case_id or package.package_kind != "OA_REPLY":
        _conflict("Package is not the exact same-case OA_REPLY package")
    if manifest.package_id != package.id or manifest.present is not True:
        _conflict("Manifest is not present in the requested package")
    role = manifest.official_file_role
    if type(role) is not str or role not in _PERMITTED_MANIFEST_ROLES:
        _conflict("Manifest does not carry one permitted OA role")
    if (
        parent.case_id != command.case_id
        or parent.role != EvidenceRole.RAW_ATTACHMENT.value
        or parent.state != EvidenceVersionState.DRAFT.value
        or manifest.evidence_version_id != parent.id
        or manifest.attachment_id != parent.attachment_id
    ):
        _conflict("Manifest does not link the requested RAW_ATTACHMENT DRAFT parent")
    if type(parent.lineage_key) is not str or not parent.lineage_key.strip():
        _conflict("Raw parent lineage is invalid")
    if (
        type(parent.content_hash) is not str
        or _CONTENT_HASH_PATTERN.fullmatch(parent.content_hash) is None
    ):
        _conflict("Raw parent content hash is invalid")
    current_identity = f"{command.case_id}|{parent.lineage_key}"
    current_ids = transaction.scalars(
        select(DocumentEvidenceVersion.id).where(
            DocumentEvidenceVersion.current_identity_key == current_identity
        )
    ).all()
    if current_ids != [parent.id]:
        _conflict("Requested raw parent is not the unique current version")
    attachment = transaction.get(DocAttachment, parent.attachment_id)
    if attachment is None or attachment.document_id != parent.document_id:
        _conflict("Raw attachment carrier is missing or mismatched")
    if (
        parent.content_hash != manifest.content_hash
        or parent.content_hash != attachment.content_hash
    ):
        _conflict("Raw parent, manifest, and attachment hashes do not match")
    existing_derivation = transaction.scalar(
        select(DocumentEvidenceDerivation.id)
        .where(
            DocumentEvidenceDerivation.case_id == command.case_id,
            DocumentEvidenceDerivation.parent_evidence_version_id == parent.id,
            DocumentEvidenceDerivation.derivation_type
            == EvidenceDerivationType.OFFICIAL_RECOGNITION.value,
        )
        .limit(1)
    )
    if existing_derivation is not None:
        _conflict("A partial OFFICIAL_RECOGNITION derivation carrier already exists")
    return case, manifest, parent, attachment, role


def _create_or_reuse_child(
    command: PromoteOaStructuredAttachmentCommand,
    transaction: Session,
    *,
    parent: DocumentEvidenceVersion,
    manifest_role: str,
) -> DocumentEvidenceVersion:
    lineage_key = f"{parent.lineage_key}|OA|{manifest_role}"
    candidates = transaction.scalars(
        select(DocumentEvidenceVersion).where(
            DocumentEvidenceVersion.case_id == command.case_id,
            DocumentEvidenceVersion.lineage_key == lineage_key,
        )
    ).all()
    if len(candidates) > 1:
        _conflict("Multiple typed child carriers exist")
    if candidates:
        child = candidates[0]
        if (
            child.document_id != parent.document_id
            or child.attachment_id != parent.attachment_id
            or child.role != EvidenceRole.OA_STRUCTURED_ATTACHMENT.value
            or child.state != command.target_state.value
            or child.content_hash != parent.content_hash
            or child.review_state != EvidenceReviewState.PENDING.value
            or child.reviewer_id is not None
            or child.reviewed_at is not None
            or child.final_submitted_at is not None
        ):
            _conflict("Existing typed child carrier conflicts with the promotion")
        return child
    result = register_evidence_version(
        RegisterEvidenceVersionCommand(
            case_id=command.case_id,
            document_id=parent.document_id,
            attachment_id=parent.attachment_id,
            lineage_key=lineage_key,
            role=EvidenceRole.OA_STRUCTURED_ATTACHMENT,
            state=command.target_state,
            creator_id=command.actor_id,
            content_hash=parent.content_hash,
        ),
        transaction,
    )
    child = transaction.get(DocumentEvidenceVersion, result.evidence_version_id)
    if child is None:
        _conflict("Typed child carrier was not persisted")
    return child


def _replay_result(
    command: PromoteOaStructuredAttachmentCommand,
    transaction: Session,
    *,
    activity: CaseActivityEvent,
) -> PromoteOaStructuredAttachmentResult:
    try:
        payload = json.loads(activity.payload_json)
    except (TypeError, ValueError):
        _conflict("Promotion activity payload is malformed")
    if (
        type(payload) is not dict
        or frozenset(payload) != _CARRIER_KEYS
        or any(type(value) is not str for value in payload.values())
        or activity.payload_json != _canonical_json(payload)
    ):
        _conflict("Promotion activity payload is not the exact canonical carrier")
    expected_command_values = {
        "actor_id": command.actor_id,
        "case_id": command.case_id,
        "command_idempotency_key": command.idempotency_key,
        "manifest_id": command.manifest_id,
        "package_id": command.package_id,
        "promoted_at": command.promoted_at.isoformat(),
        "raw_evidence_version_id": command.raw_evidence_version_id,
        "schema": "FPMS_OA_STRUCTURED_ATTACHMENT_PROMOTION_V1",
        "target_state": command.target_state.value,
    }
    if any(payload[key] != value for key, value in expected_command_values.items()):
        _conflict("Promotion replay command identity differs")
    manifest_role = payload["manifest_role"]
    if manifest_role not in _PERMITTED_MANIFEST_ROLES:
        _conflict("Promotion replay manifest role is invalid")
    identity_source = {
        "actor_id": command.actor_id,
        "case_id": command.case_id,
        "command_idempotency_key": command.idempotency_key,
        "manifest_id": command.manifest_id,
        "manifest_role": manifest_role,
        "package_id": command.package_id,
        "promoted_at": command.promoted_at.isoformat(),
        "raw_content_hash": payload["raw_content_hash"],
        "raw_evidence_version_id": command.raw_evidence_version_id,
        "target_state": command.target_state.value,
    }
    expected_identity = (
        "sha256:" + hashlib.sha256(_canonical_json(identity_source).encode("utf-8")).hexdigest()
    )
    if payload["promotion_identity_key"] != expected_identity:
        _conflict("Promotion identity key is invalid")

    package = transaction.get(OfficialWorkPackage, command.package_id)
    manifest = transaction.get(OfficialWorkPackageManifest, command.manifest_id)
    parent = transaction.get(DocumentEvidenceVersion, command.raw_evidence_version_id)
    child = transaction.get(
        DocumentEvidenceVersion,
        payload["typed_evidence_version_id"],
    )
    if package is None or manifest is None or parent is None or child is None:
        _conflict("Promotion replay carrier is missing")
    if package.case_id != command.case_id or package.package_kind != "OA_REPLY":
        _conflict("Promotion replay package conflicts")
    if (
        manifest.package_id != command.package_id
        or manifest.evidence_version_id != child.id
        or manifest.content_hash != child.content_hash
        or manifest.official_file_role != manifest_role
    ):
        _conflict("Promotion replay manifest conflicts")
    if (
        parent.case_id != command.case_id
        or parent.content_hash != payload["raw_content_hash"]
        or child.case_id != command.case_id
        or child.document_id != parent.document_id
        or child.attachment_id != parent.attachment_id
        or child.lineage_key != f"{parent.lineage_key}|OA|{manifest_role}"
        or child.role != EvidenceRole.OA_STRUCTURED_ATTACHMENT.value
        or child.state != command.target_state.value
        or child.creator_id != command.actor_id
        or child.review_state != EvidenceReviewState.PENDING.value
        or child.reviewer_id is not None
        or child.reviewed_at is not None
        or child.content_hash != payload["typed_content_hash"]
        or child.content_hash != parent.content_hash
    ):
        _conflict("Promotion replay evidence version conflicts")

    derivations = transaction.scalars(
        select(DocumentEvidenceDerivation).where(
            DocumentEvidenceDerivation.case_id == command.case_id,
            DocumentEvidenceDerivation.parent_evidence_version_id == parent.id,
            DocumentEvidenceDerivation.child_evidence_version_id == child.id,
            DocumentEvidenceDerivation.derivation_type
            == EvidenceDerivationType.OFFICIAL_RECOGNITION.value,
        )
    ).all()
    if len(derivations) != 1:
        _conflict("Promotion replay derivation cardinality conflicts")
    derivation = derivations[0]
    if (
        derivation.actor_id != command.actor_id
        or derivation.derived_at != command.promoted_at
        or derivation.source_snapshot != activity.payload_json
    ):
        _conflict("Promotion replay derivation conflicts")

    if (
        activity.lane != ActivityLane.DOCUMENT.value
        or activity.activity_type != "OA_STRUCTURED_ATTACHMENT_PROMOTED"
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or activity.actor_id != command.actor_id
        or activity.reviewer_id is not None
        or activity.effective_at != command.promoted_at
        or activity.occurred_at != command.promoted_at
        or activity.old_business_stage != activity.new_business_stage
        or activity.old_official_procedure_stage != activity.new_official_procedure_stage
        or activity.old_legal_status != activity.new_legal_status
    ):
        _conflict("Promotion replay activity conflicts")
    references = transaction.scalars(
        select(CaseActivityEventEvidence).where(
            CaseActivityEventEvidence.case_id == command.case_id,
            CaseActivityEventEvidence.activity_id == activity.id,
        )
    ).all()
    actual_references = {
        (
            reference.evidence_kind,
            reference.object_type,
            reference.object_id,
            reference.content_hash,
            reference.captured_at,
        )
        for reference in references
    }
    expected_references = {
        (
            "RAW_ATTACHMENT_VERSION",
            "DocumentEvidenceVersion",
            parent.id,
            parent.content_hash,
            command.promoted_at,
        ),
        (
            "OA_STRUCTURED_ATTACHMENT_VERSION",
            "DocumentEvidenceVersion",
            child.id,
            child.content_hash,
            command.promoted_at,
        ),
    }
    if len(references) != 2 or actual_references != expected_references:
        _conflict("Promotion replay references conflict")
    return PromoteOaStructuredAttachmentResult(
        typed_evidence_version_id=child.id,
        evidence_derivation_id=derivation.id,
        activity_id=activity.id,
        promotion_identity_key=expected_identity,
        reused=True,
    )


def promote_oa_structured_attachment(
    command: PromoteOaStructuredAttachmentCommand,
    transaction: Session,
) -> PromoteOaStructuredAttachmentResult:
    _validate_lookup_identity(command)
    activity_key = f"oa-structured-promotion:{command.idempotency_key}"
    existing_activities = transaction.scalars(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == command.case_id,
            CaseActivityEvent.idempotency_key == activity_key,
        )
    ).all()
    if len(existing_activities) > 1:
        _conflict("Multiple promotion activity carriers exist")
    if existing_activities:
        _validate_replay_command_shape(command)
        return _replay_result(
            command,
            transaction,
            activity=existing_activities[0],
        )
    _validate_command(command)

    case, manifest, parent, _attachment, manifest_role = _load_fresh_carriers(
        command,
        transaction,
    )
    identity_source = {
        "actor_id": command.actor_id,
        "case_id": command.case_id,
        "command_idempotency_key": command.idempotency_key,
        "manifest_id": command.manifest_id,
        "manifest_role": manifest_role,
        "package_id": command.package_id,
        "promoted_at": command.promoted_at.isoformat(),
        "raw_content_hash": parent.content_hash,
        "raw_evidence_version_id": parent.id,
        "target_state": command.target_state.value,
    }
    promotion_identity_key = (
        "sha256:" + hashlib.sha256(_canonical_json(identity_source).encode("utf-8")).hexdigest()
    )
    child = _create_or_reuse_child(
        command,
        transaction,
        parent=parent,
        manifest_role=manifest_role,
    )
    carrier = {
        **identity_source,
        "promotion_identity_key": promotion_identity_key,
        "schema": "FPMS_OA_STRUCTURED_ATTACHMENT_PROMOTION_V1",
        "typed_content_hash": child.content_hash,
        "typed_evidence_version_id": child.id,
    }
    carrier_json = _canonical_json(carrier)
    derivation_result = register_evidence_derivation(
        RegisterEvidenceDerivationCommand(
            case_id=command.case_id,
            parent_evidence_version_id=parent.id,
            child_evidence_version_id=child.id,
            derivation_type=EvidenceDerivationType.OFFICIAL_RECOGNITION,
            actor_id=command.actor_id,
            derived_at=command.promoted_at,
            source_snapshot=carrier_json,
        ),
        transaction,
    )
    projection = _projection(case)
    activity_result = append_case_activity(
        LifecycleEventCommand(
            case_id=command.case_id,
            event_type="OA_STRUCTURED_ATTACHMENT_PROMOTED",
            lane=ActivityLane.DOCUMENT,
            effective_at=command.promoted_at,
            occurred_at=command.promoted_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=command.case_id,
                    evidence_kind="RAW_ATTACHMENT_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=parent.id,
                    content_hash=parent.content_hash,
                    captured_at=command.promoted_at,
                ),
                EvidenceReference(
                    case_id=command.case_id,
                    evidence_kind="OA_STRUCTURED_ATTACHMENT_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=child.id,
                    content_hash=child.content_hash,
                    captured_at=command.promoted_at,
                ),
            ),
            actor_id=command.actor_id,
            reviewer_id=None,
            idempotency_key=activity_key,
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload=carrier,
        ),
        transaction,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=case.status,
        conflict_codes=(),
    )
    manifest.evidence_version_id = child.id
    manifest.content_hash = child.content_hash
    transaction.flush()
    return PromoteOaStructuredAttachmentResult(
        typed_evidence_version_id=child.id,
        evidence_derivation_id=derivation_result.evidence_derivation_id,
        activity_id=activity_result.activity_id,
        promotion_identity_key=promotion_identity_key,
        reused=False,
    )


__all__ = [
    "PromoteOaStructuredAttachmentCommand",
    "PromoteOaStructuredAttachmentResult",
    "promote_oa_structured_attachment",
]
