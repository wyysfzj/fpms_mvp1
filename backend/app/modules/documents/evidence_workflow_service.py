from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

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
    EvidenceDerivationType,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.evidence_policy import (
    CopyableOaAttachmentEvidence,
    CopyableOaAttachmentPolicyError,
    NoncopyableOaAppendixPolicyError,
    require_copyable_oa_attachment_combination,
    require_noncopyable_oa_appendix_derivation,
)
from app.modules.documents.evidence_service import (
    _capture_lifecycle_projection,
    _stored_activity_projection,
)
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceDerivation,
    DocumentEvidenceVersion,
)
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageManifest,
)

_CONTENT_HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_OA_PREPARATION_SCHEMA = "FPMS_OA_REPLY_PREPARATION_V1"
_OA_PREPARATION_TYPE = EvidenceDerivationType.OA_REPLY_PREPARATION.value
_OA_ATTACHMENT_ROLE_RANK = {
    role: rank
    for rank, role in enumerate(
        (
            "OA_STATEMENT_WORD",
            "OA_MODIFIED_CLAIMS",
            "OA_AMENDMENT_COMPARISON",
            "OA_OTHER_PROOF",
            "OA_ADDITIONAL_FILE",
        )
    )
}
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


@dataclass(frozen=True, slots=True, kw_only=True)
class PrepareOaReplyCommand:
    case_id: str
    source_document_id: str
    source_evidence_version_id: str
    package_id: str
    reply_document_id: str
    reply_attachment_id: str
    reply_content_hash: str
    actor_id: str
    attachments: tuple[CopyableOaAttachmentEvidence, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class OaReplyPackageResult:
    case_id: str
    source_document_id: str
    source_evidence_version_id: str
    reply_document_id: str
    reply_evidence_version_id: str
    package_id: str
    content_hash: str
    reused: bool


@dataclass(frozen=True, slots=True)
class _OaTypedAttachmentCarrier:
    version: DocumentEvidenceVersion
    attachment: DocAttachment
    manifest: OfficialWorkPackageManifest


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


def _oa_invalid(field: str) -> None:
    raise_business_error(
        "OA_REPLY_PREPARATION_INVALID",
        f"Invalid OA reply preparation field: {field}",
        details={"field": field},
        status_code=400,
    )


def _oa_conflict(message: str) -> None:
    raise_business_error(
        "OA_REPLY_IDENTITY_CONFLICT",
        message,
        status_code=409,
    )


def _validate_oa_command(command: PrepareOaReplyCommand) -> None:
    if type(command) is not PrepareOaReplyCommand:
        _oa_invalid("command")
    for field in (
        "case_id",
        "source_document_id",
        "source_evidence_version_id",
        "package_id",
        "reply_document_id",
        "reply_attachment_id",
        "reply_content_hash",
        "actor_id",
    ):
        value = getattr(command, field)
        max_length = 128 if field == "reply_content_hash" else 36
        if type(value) is not str or not value.strip() or len(value) > max_length:
            _oa_invalid(field)
    if _CONTENT_HASH_PATTERN.fullmatch(command.reply_content_hash) is None:
        _oa_invalid("reply_content_hash")
    if type(command.attachments) is not tuple:
        _oa_invalid("attachments")


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


def _stored_evidence_result(version: DocumentEvidenceVersion) -> EvidenceVersionResult:
    try:
        role = EvidenceRole(version.role)
        state = EvidenceVersionState(version.state)
        review_state = EvidenceReviewState(version.review_state)
    except ValueError:
        _oa_conflict("Stored OA attachment evidence has an invalid enum value")
    return EvidenceVersionResult(
        evidence_version_id=version.id,
        case_id=version.case_id,
        document_id=version.document_id,
        attachment_id=version.attachment_id,
        lineage_key=version.lineage_key,
        role=role,
        version_number=version.version_number,
        state=state,
        creator_id=version.creator_id,
        review_state=review_state,
        reviewer_id=version.reviewer_id,
        reviewed_at=version.reviewed_at,
        final_submitted_at=version.final_submitted_at,
        content_hash=version.content_hash,
        is_current=version.current_identity_key is not None,
        is_final=state is EvidenceVersionState.FINAL,
    )


def _require_source_oa_notice(
    command: PrepareOaReplyCommand,
    transaction: Session,
) -> tuple[Document, DocumentEvidenceVersion, DocAttachment]:
    source = transaction.get(Document, command.source_document_id)
    if source is None:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)
    if source.case_id != command.case_id:
        raise_business_error(
            "OA_REPLY_DOCUMENT_CASE_MISMATCH",
            "Source document does not belong to the requested case",
            status_code=400,
        )
    if source.direction != "IN":
        raise_business_error(
            "OA_REPLY_SOURCE_DIRECTION_INVALID",
            "OA reply source must be an incoming document",
            status_code=400,
        )
    template = (
        transaction.get(DocTemplate, source.doc_template_id) if source.doc_template_id else None
    )
    semantics = resolve_document_semantics(template)
    if semantics.catalog_status != "EXECUTABLE" or semantics.execution_behavior != "OA_REPLY":
        raise_business_error(
            "OA_REPLY_SOURCE_SEMANTICS_INVALID",
            "Document does not have executable OA reply semantics",
            status_code=409,
        )

    version = transaction.get(DocumentEvidenceVersion, command.source_evidence_version_id)
    if version is None:
        raise_business_error(
            "EVIDENCE_VERSION_NOT_FOUND",
            "Evidence version not found",
            status_code=404,
        )
    source_attachment = transaction.get(DocAttachment, version.attachment_id)
    if (
        version.case_id != command.case_id
        or version.document_id != source.id
        or source_attachment is None
        or source_attachment.document_id != source.id
        or source_attachment.content_hash != version.content_hash
        or version.current_identity_key != f"{command.case_id}|{version.lineage_key}"
    ):
        _oa_conflict("Source OA notice evidence identity is inconsistent")
    return source, version, source_attachment


def _require_oa_package(
    command: PrepareOaReplyCommand,
    source: Document,
    transaction: Session,
) -> OfficialWorkPackage:
    packages = transaction.scalars(
        select(OfficialWorkPackage).where(
            OfficialWorkPackage.source_document_id == source.id,
            OfficialWorkPackage.package_kind == "OA_REPLY",
        )
    ).all()
    if len(packages) != 1:
        _oa_conflict("OA reply package identity is not unique")
    package = packages[0]
    if (
        package.id != command.package_id
        or package.case_id != command.case_id
        or package.resolve_key != f"OA_REPLY:{source.id}"
    ):
        _oa_conflict("OA reply package identity is inconsistent")
    return package


def _require_reply_carriers(
    command: PrepareOaReplyCommand,
    source: Document,
    transaction: Session,
) -> tuple[Document, DocAttachment]:
    reply = transaction.get(Document, command.reply_document_id)
    if reply is None:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)
    if reply.case_id != command.case_id:
        raise_business_error(
            "OA_REPLY_DOCUMENT_CASE_MISMATCH",
            "Reply document does not belong to the requested case",
            status_code=400,
        )
    template = (
        transaction.get(DocTemplate, reply.doc_template_id) if reply.doc_template_id else None
    )
    if (
        template is None
        or template.code != "OA_OUT"
        or reply.direction != "OUT"
        or reply.reply_to_id != source.id
    ):
        _oa_conflict("Reply document is not the exact OA_OUT for its source")

    attachment = transaction.get(DocAttachment, command.reply_attachment_id)
    if (
        attachment is None
        or attachment.document_id != reply.id
        or attachment.content_hash != command.reply_content_hash
    ):
        _oa_conflict("Reply attachment identity or content hash is inconsistent")
    return reply, attachment


def _require_typed_attachments(
    command: PrepareOaReplyCommand,
    package: OfficialWorkPackage,
    transaction: Session,
) -> tuple[_OaTypedAttachmentCarrier, ...]:
    try:
        require_copyable_oa_attachment_combination(
            case_id=command.case_id,
            package_id=package.id,
            attachments=command.attachments,
        )
    except CopyableOaAttachmentPolicyError as exc:
        raise_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            "Selected OA attachment policy rejected the typed identity",
            details={"policy_code": exc.code.value},
            status_code=409,
        )

    stored_manifests = transaction.scalars(
        select(OfficialWorkPackageManifest).where(
            OfficialWorkPackageManifest.package_id == package.id,
            OfficialWorkPackageManifest.official_file_role.in_(_OA_ATTACHMENT_ROLE_RANK),
            OfficialWorkPackageManifest.present.is_(True),
        )
    ).all()
    if {manifest.id for manifest in stored_manifests} != {
        attachment.manifest_id for attachment in command.attachments
    }:
        _oa_conflict("Selected OA attachment manifest set is stale or incomplete")

    carriers: list[_OaTypedAttachmentCarrier] = []
    for selected in command.attachments:
        version = transaction.get(
            DocumentEvidenceVersion,
            selected.evidence_version.evidence_version_id,
        )
        manifest = transaction.get(OfficialWorkPackageManifest, selected.manifest_id)
        stored_attachment = (
            transaction.get(DocAttachment, version.attachment_id) if version is not None else None
        )
        if (
            version is None
            or manifest is None
            or stored_attachment is None
            or _stored_evidence_result(version) != selected.evidence_version
            or version.current_identity_key != f"{command.case_id}|{version.lineage_key}"
            or manifest.package_id != package.id
            or manifest.evidence_version_id != version.id
            or manifest.attachment_id != version.attachment_id
            or version.attachment_id != stored_attachment.id
            or stored_attachment.document_id != version.document_id
            or stored_attachment.content_hash != version.content_hash
            or manifest.official_file_role != selected.manifest_role
            or manifest.content_hash != selected.manifest_content_hash
            or manifest.content_hash != version.content_hash
            or manifest.present is not True
        ):
            _oa_conflict("Selected OA attachment identity changed after policy validation")
        manifest_is_appendix = manifest.source_role_alias == "OA_STATEMENT_APPENDIX"
        attachment_is_appendix = stored_attachment.source_role_alias == "OA_STATEMENT_APPENDIX"
        if manifest_is_appendix != attachment_is_appendix:
            _oa_conflict("OA appendix alias identity is one-sided")
        carriers.append(
            _OaTypedAttachmentCarrier(
                version=version,
                attachment=stored_attachment,
                manifest=manifest,
            )
        )

    appendix_carriers = [
        carrier
        for carrier in carriers
        if carrier.manifest.source_role_alias == "OA_STATEMENT_APPENDIX"
        and carrier.attachment.source_role_alias == "OA_STATEMENT_APPENDIX"
    ]
    if appendix_carriers:
        full_reply_manifests = transaction.scalars(
            select(OfficialWorkPackageManifest).where(
                OfficialWorkPackageManifest.package_id == package.id,
                OfficialWorkPackageManifest.official_file_role == "OA_STATEMENT_PDF",
                OfficialWorkPackageManifest.present.is_(True),
            )
        ).all()
        if len(full_reply_manifests) != 1:
            _oa_conflict("OA noncopyable appendix parent identity is not unique")
        full_reply_manifest = full_reply_manifests[0]
        full_reply_pdf = transaction.get(
            DocumentEvidenceVersion,
            full_reply_manifest.evidence_version_id,
        )
        full_reply_attachment = transaction.get(
            DocAttachment,
            full_reply_manifest.attachment_id,
        )
        if full_reply_pdf is None or full_reply_attachment is None:
            _oa_conflict("OA noncopyable appendix parent carrier is missing")

        for carrier in appendix_carriers:
            derivations = transaction.scalars(
                select(DocumentEvidenceDerivation).where(
                    DocumentEvidenceDerivation.parent_evidence_version_id == full_reply_pdf.id,
                    DocumentEvidenceDerivation.child_evidence_version_id == carrier.version.id,
                )
            ).all()
            if len(derivations) != 1:
                _oa_conflict("OA noncopyable appendix derivation carrier is incomplete")
            try:
                require_noncopyable_oa_appendix_derivation(
                    case_id=command.case_id,
                    package=package,
                    full_reply_pdf=full_reply_pdf,
                    full_reply_attachment=full_reply_attachment,
                    full_reply_manifest=full_reply_manifest,
                    extracted_appendix=carrier.version,
                    appendix_attachment=carrier.attachment,
                    appendix_manifest=carrier.manifest,
                    derivation=derivations[0],
                    other_proof_evidence_version_id=carrier.version.id,
                )
            except NoncopyableOaAppendixPolicyError as exc:
                raise_business_error(
                    "OA_REPLY_IDENTITY_CONFLICT",
                    "Selected OA noncopyable appendix policy rejected the derivation",
                    details={"policy_code": exc.code.value},
                    status_code=409,
                )
    return tuple(carriers)


def _oa_preparation_snapshot(
    command: PrepareOaReplyCommand,
    *,
    source: Document,
    source_version: DocumentEvidenceVersion,
    source_attachment: DocAttachment,
    reply: Document,
    reply_version: DocumentEvidenceVersion,
    reply_attachment: DocAttachment,
    typed_carriers: tuple[_OaTypedAttachmentCarrier, ...],
    prepared_at: datetime,
) -> str:
    attachments = [
        {
            "attachment_content_hash": carrier.attachment.content_hash,
            "attachment_document_id": carrier.attachment.document_id,
            "attachment_id": carrier.attachment.id,
            "attachment_source_role_alias": carrier.attachment.source_role_alias,
            "evidence_content_hash": carrier.version.content_hash,
            "evidence_document_id": carrier.version.document_id,
            "evidence_lineage_key": carrier.version.lineage_key,
            "evidence_role": carrier.version.role,
            "evidence_version_id": carrier.version.id,
            "evidence_version_number": carrier.version.version_number,
            "manifest_attachment_id": carrier.manifest.attachment_id,
            "manifest_content_hash": carrier.manifest.content_hash,
            "manifest_evidence_version_id": carrier.manifest.evidence_version_id,
            "manifest_id": carrier.manifest.id,
            "manifest_role": carrier.manifest.official_file_role,
            "manifest_source_role_alias": carrier.manifest.source_role_alias,
        }
        for carrier in typed_carriers
    ]
    attachments.sort(
        key=lambda item: (
            _OA_ATTACHMENT_ROLE_RANK[item["manifest_role"]],
            item["manifest_id"],
            item["evidence_version_id"],
        )
    )
    snapshot = {
        "actor_id": command.actor_id,
        "attachments": attachments,
        "case_id": command.case_id,
        "package_id": command.package_id,
        "prepared_at": prepared_at.isoformat(timespec="microseconds"),
        "reply": {
            "attachment_id": reply_attachment.id,
            "content_hash": reply_version.content_hash,
            "document_id": reply.id,
            "evidence_version_id": reply_version.id,
            "lineage_key": reply_version.lineage_key,
        },
        "schema": _OA_PREPARATION_SCHEMA,
        "source": {
            "attachment_id": source_attachment.id,
            "content_hash": source_version.content_hash,
            "document_id": source.id,
            "evidence_version_id": source_version.id,
            "lineage_key": source_version.lineage_key,
        },
    }
    return json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _oa_replay_prepared_at(derivation: DocumentEvidenceDerivation) -> datetime:
    if (
        type(derivation.derived_at) is not datetime
        or derivation.derived_at.tzinfo is not None
        or type(derivation.source_snapshot) is not str
    ):
        _oa_conflict("Persisted OA preparation receipt has invalid time or bytes")
    try:
        snapshot = json.loads(derivation.source_snapshot)
        canonical_snapshot = json.dumps(
            snapshot,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        _oa_conflict("Persisted OA preparation receipt is malformed")
    if (
        type(snapshot) is not dict
        or set(snapshot)
        != {
            "actor_id",
            "attachments",
            "case_id",
            "package_id",
            "prepared_at",
            "reply",
            "schema",
            "source",
        }
        or canonical_snapshot != derivation.source_snapshot
        or type(snapshot["prepared_at"]) is not str
    ):
        _oa_conflict("Persisted OA preparation receipt is not canonical")
    try:
        prepared_at = datetime.fromisoformat(snapshot["prepared_at"])
    except ValueError:
        _oa_conflict("Persisted OA preparation time is malformed")
    if (
        prepared_at.tzinfo is not None
        or prepared_at != derivation.derived_at
        or snapshot["prepared_at"] != prepared_at.isoformat(timespec="microseconds")
    ):
        _oa_conflict("Persisted OA preparation time contradicts the derivation")
    return prepared_at


def _oa_result(
    command: PrepareOaReplyCommand,
    version: DocumentEvidenceVersion,
    *,
    reused: bool,
) -> OaReplyPackageResult:
    return OaReplyPackageResult(
        case_id=command.case_id,
        source_document_id=command.source_document_id,
        source_evidence_version_id=command.source_evidence_version_id,
        reply_document_id=command.reply_document_id,
        reply_evidence_version_id=version.id,
        package_id=command.package_id,
        content_hash=version.content_hash,
        reused=reused,
    )


def prepare_oa_reply(
    command: PrepareOaReplyCommand,
    transaction: Session,
) -> OaReplyPackageResult:
    _validate_oa_command(command)
    if transaction.get(Case, command.case_id) is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    source, source_version, source_attachment = _require_source_oa_notice(
        command,
        transaction,
    )
    package = _require_oa_package(command, source, transaction)
    reply, reply_attachment = _require_reply_carriers(command, source, transaction)
    typed_carriers = _require_typed_attachments(command, package, transaction)

    linked_packages = transaction.scalars(
        select(OfficialWorkPackage).where(
            OfficialWorkPackage.reply_document_id == reply.id,
        )
    ).all()
    if any(linked.id != package.id for linked in linked_packages):
        _oa_conflict("Reply document is linked to another work package")

    lineage_key = f"oa-reply:{source.id}"
    versions = transaction.scalars(
        select(DocumentEvidenceVersion).where(
            DocumentEvidenceVersion.lineage_key == lineage_key,
        )
    ).all()
    if any(version.case_id != command.case_id for version in versions):
        _oa_conflict("OA reply lineage crosses cases")
    if len(versions) > 1:
        _oa_conflict("OA reply lineage has multiple persisted evidence closures")
    if versions:
        version = versions[0]
        if (
            package.reply_document_id != reply.id
            or len(linked_packages) != 1
            or version.case_id != command.case_id
            or version.document_id != reply.id
            or version.attachment_id != reply_attachment.id
            or version.lineage_key != lineage_key
            or version.role != EvidenceRole.GENERATED_ATTACHMENT.value
            or version.version_number != 1
            or version.state != EvidenceVersionState.DRAFT.value
            or version.creator_id != command.actor_id
            or version.review_state != EvidenceReviewState.PENDING.value
            or version.reviewer_id is not None
            or version.reviewed_at is not None
            or version.final_submitted_at is not None
            or version.content_hash != command.reply_content_hash
            or version.current_identity_key != f"{command.case_id}|{lineage_key}"
        ):
            _oa_conflict("Persisted OA reply closure contradicts the requested replay")
        source_derivations = transaction.scalars(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.parent_evidence_version_id == source_version.id,
                DocumentEvidenceDerivation.derivation_type == _OA_PREPARATION_TYPE,
            )
        ).all()
        reply_derivations = transaction.scalars(
            select(DocumentEvidenceDerivation).where(
                DocumentEvidenceDerivation.child_evidence_version_id == version.id,
                DocumentEvidenceDerivation.derivation_type == _OA_PREPARATION_TYPE,
            )
        ).all()
        if any(row.case_id != command.case_id for row in (*source_derivations, *reply_derivations)):
            _oa_conflict("Persisted OA preparation derivation crosses cases")
        if (
            len(source_derivations) != 1
            or len(reply_derivations) != 1
            or source_derivations[0].id != reply_derivations[0].id
        ):
            _oa_conflict("Persisted OA preparation derivation cardinality is inconsistent")
        derivation = source_derivations[0]
        if (
            derivation.case_id != command.case_id
            or derivation.parent_evidence_version_id != source_version.id
            or derivation.child_evidence_version_id != version.id
            or derivation.derivation_type != _OA_PREPARATION_TYPE
            or derivation.actor_id != command.actor_id
        ):
            _oa_conflict("Persisted OA preparation derivation identity is inconsistent")
        prepared_at = _oa_replay_prepared_at(derivation)
        rebuilt_snapshot = _oa_preparation_snapshot(
            command,
            source=source,
            source_version=source_version,
            source_attachment=source_attachment,
            reply=reply,
            reply_version=version,
            reply_attachment=reply_attachment,
            typed_carriers=typed_carriers,
            prepared_at=prepared_at,
        )
        if rebuilt_snapshot != derivation.source_snapshot:
            _oa_conflict("Persisted OA preparation receipt contradicts current identity")
        return _oa_result(command, version, reused=True)

    if package.reply_document_id is not None or linked_packages:
        _oa_conflict("OA reply package link exists without its evidence closure")
    source_derivations = transaction.scalars(
        select(DocumentEvidenceDerivation).where(
            DocumentEvidenceDerivation.parent_evidence_version_id == source_version.id,
            DocumentEvidenceDerivation.derivation_type == _OA_PREPARATION_TYPE,
        )
    ).all()
    if any(row.case_id != command.case_id for row in source_derivations):
        _oa_conflict("Source OA notice preparation derivation crosses cases")
    if source_derivations:
        _oa_conflict("Source OA notice already has a preparation derivation")

    version = DocumentEvidenceVersion(
        id=str(uuid4()),
        case_id=command.case_id,
        document_id=reply.id,
        attachment_id=reply_attachment.id,
        lineage_key=lineage_key,
        role=EvidenceRole.GENERATED_ATTACHMENT.value,
        version_number=1,
        state=EvidenceVersionState.DRAFT.value,
        creator_id=command.actor_id,
        review_state=EvidenceReviewState.PENDING.value,
        reviewer_id=None,
        reviewed_at=None,
        final_submitted_at=None,
        content_hash=command.reply_content_hash,
        current_identity_key=f"{command.case_id}|{lineage_key}",
    )
    transaction.add(version)
    transaction.flush([version])

    prepared_at = datetime.now(timezone.utc).replace(tzinfo=None)
    derivation = DocumentEvidenceDerivation(
        id=str(uuid4()),
        case_id=command.case_id,
        parent_evidence_version_id=source_version.id,
        child_evidence_version_id=version.id,
        derivation_type=_OA_PREPARATION_TYPE,
        actor_id=command.actor_id,
        derived_at=prepared_at,
        source_snapshot=_oa_preparation_snapshot(
            command,
            source=source,
            source_version=source_version,
            source_attachment=source_attachment,
            reply=reply,
            reply_version=version,
            reply_attachment=reply_attachment,
            typed_carriers=typed_carriers,
            prepared_at=prepared_at,
        ),
    )
    package.reply_document_id = reply.id
    transaction.add(derivation)
    transaction.flush()
    return _oa_result(command, version, reused=False)


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
    "OaReplyPackageResult",
    "PrepareOaReplyCommand",
    "SubmissionEvidenceResult",
    "finalize_external_submission",
    "prepare_oa_reply",
)
