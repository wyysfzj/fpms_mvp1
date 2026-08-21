from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import BusinessError, raise_business_error
from app.core.storage import ensure_dir, safe_join
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
from app.modules.cases.models import Case, T_CaseApplicant
from app.modules.documents.enums import DocumentDirection, DocumentDocType
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
    RegisterEvidenceVersionCommand,
)
from app.modules.documents.evidence_service import register_evidence_version
from app.modules.documents.extra_data import (
    DocumentExtraDataBusinessError,
    DocumentExtraDataShapeError,
    merge_document_extra_data,
    parse_document_extra_data,
)
from app.modules.documents.fee_linking_service import (
    create_fee_draft_from_wizard_row,
    maybe_create_fee_draft,
    parse_fee_item_list_candidates,
)
from app.modules.documents.models import (
    DocAttachment,
    DocDispatch,
    DocDispatchLine,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
)
from app.modules.documents.schemas import (
    AttachmentManifestItemOut,
    AttachmentManifestSummaryOut,
    DocTemplateCreateIn,
    DocTemplateUpdateIn,
    DocumentCreateIn,
    DocumentDispatchCreateIn,
    DocumentEnvelopePreviewOut,
    DocumentImpactItemOut,
    DocumentImpactPreviewIn,
    DocumentImpactPreviewOut,
    DocumentMailingBatchIn,
    DocumentUpdateIn,
    DocumentWizardAttachmentFinalRowIn,
    DocumentWizardAttachmentPreviewIn,
    DocumentWizardBatchCreateIn,
    DocumentWizardBatchRowIn,
    DocumentWizardFeeFinalRowIn,
    DocumentWizardFeePreviewIn,
    DocumentWizardTaskFinalRowIn,
)
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.masterdata.clients.models import Client, ClientAddress
from app.modules.tasks.enums import TaskAction, TaskStatus
from app.modules.tasks.models import Task, TaskTemplate
from app.modules.tasks.service import _create_task_log
from app.modules.tasks.task_generation_service import TaskGenerationService
from app.modules.templates.models import Template
from app.modules.templates.render import TemplateRenderer

logger = logging.getLogger(__name__)

ATTACHMENT_ROLE_CATEGORY_INTAKE = "INTAKE_GATE"
ATTACHMENT_ROLE_CATEGORY_FILING = "FILING"
ATTACHMENT_ROLE_CATEGORY_OA = "OA_REPLY"
ATTACHMENT_ROLE_CATEGORY_ARCHIVE = "ARCHIVE"

_ATTACHMENT_ROLE_DEFINITIONS: dict[str, dict[str, object]] = {
    "TECHNICAL_DISCLOSURE": {
        "category": ATTACHMENT_ROLE_CATEGORY_INTAKE,
        "package_usage_hint": "CASE_INTAKE",
    },
    "COMMISSION_INSTRUCTION": {
        "category": ATTACHMENT_ROLE_CATEGORY_INTAKE,
        "package_usage_hint": "CASE_INTAKE",
    },
    "FILING_FULL_WORD": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_SOURCE_WORD",
        "package_usage_hint": "FILING_PREP",
    },
    "FILING_ABSTRACT": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_XML_ZIP_AUTO_ASSIGN",
        "package_usage_hint": "FILING_PREP",
    },
    "CLAIMS": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_XML_ZIP_AUTO_ASSIGN",
        "package_usage_hint": "FILING_PREP",
    },
    "FILING_CLAIMS": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_XML_ZIP_AUTO_ASSIGN",
        "package_usage_hint": "FILING_PREP",
    },
    "FILING_DESCRIPTION": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_XML_ZIP_AUTO_ASSIGN",
        "package_usage_hint": "FILING_PREP",
    },
    "FILING_DRAWINGS": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_XML_ZIP_AUTO_ASSIGN",
        "package_usage_hint": "FILING_PREP",
    },
    "FILING_SEQUENCE_LISTING": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_XML_ZIP_AUTO_ASSIGN",
        "package_usage_hint": "FILING_PREP",
    },
    "FILING_XML_ZIP": {
        "category": ATTACHMENT_ROLE_CATEGORY_FILING,
        "external_upload_position": "FILING_XML_ZIP_UPLOAD",
        "package_usage_hint": "FILING_PREP",
    },
    "OA_STATEMENT_WORD": {
        "category": ATTACHMENT_ROLE_CATEGORY_OA,
        "external_upload_position": "OA_REPLY_STATEMENT_SOURCE",
        "package_usage_hint": "OA_REPLY",
    },
    "OA_STATEMENT_PDF": {
        "category": ATTACHMENT_ROLE_CATEGORY_OA,
        "external_upload_position": "OA_REPLY_OTHER_PROOF_FILES",
        "package_usage_hint": "OA_REPLY",
    },
    "OA_MODIFIED_CLAIMS": {
        "category": ATTACHMENT_ROLE_CATEGORY_OA,
        "external_upload_position": "OA_REPLY_CLAIMS",
        "package_usage_hint": "OA_REPLY",
    },
    "OA_AMENDMENT_COMPARISON": {
        "category": ATTACHMENT_ROLE_CATEGORY_OA,
        "external_upload_position": "OA_REPLY_COMPARISON_PAGE",
        "package_usage_hint": "OA_REPLY",
    },
    "OA_OTHER_PROOF": {
        "category": ATTACHMENT_ROLE_CATEGORY_OA,
        "external_upload_position": "OA_REPLY_OTHER_PROOF_FILES",
        "package_usage_hint": "OA_REPLY",
    },
    "OA_ADDITIONAL_FILE": {
        "category": ATTACHMENT_ROLE_CATEGORY_OA,
        "external_upload_position": "OA_REPLY_ADDITIONAL_FILES",
        "package_usage_hint": "OA_REPLY",
    },
    "FILING_MERGED_PDF": {
        "category": ATTACHMENT_ROLE_CATEGORY_ARCHIVE,
        "external_upload_position": "FILING_ARCHIVE",
        "package_usage_hint": "FILING_ARCHIVE",
        "is_archive_evidence": True,
    },
    "OFFICIAL_NOTICE_PDF": {
        "category": ATTACHMENT_ROLE_CATEGORY_ARCHIVE,
        "external_upload_position": "OFFICIAL_NOTICE_EVIDENCE",
        "package_usage_hint": "OFFICIAL_NOTICE_EVIDENCE",
        "is_archive_evidence": True,
    },
    "ELECTRONIC_RECEIPT": {
        "category": ATTACHMENT_ROLE_CATEGORY_ARCHIVE,
        "external_upload_position": "RECEIPT_ARCHIVE",
        "package_usage_hint": "RECEIPT_ARCHIVE",
        "is_archive_evidence": True,
        "is_receipt_evidence": True,
    },
}

_PDF_MIME_TYPES = {"application/pdf", "application/octet-stream"}
_WORD_MIME_TYPES = {
    "application/msword",
    "application/octet-stream",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
_ZIP_MIME_TYPES = {
    "application/octet-stream",
    "application/x-zip-compressed",
    "application/zip",
}
_IMAGE_MIME_TYPES = {"image/jpeg", "image/png"}
_SPREADSHEET_MIME_TYPES = {
    "application/octet-stream",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
_PROOF_MIME_TYPES = (
    _PDF_MIME_TYPES
    | _WORD_MIME_TYPES
    | _IMAGE_MIME_TYPES
    | _SPREADSHEET_MIME_TYPES
    | _ZIP_MIME_TYPES
)
_ATTACHMENT_ROLE_FILE_RULES: dict[str, dict[str, set[str]]] = {
    "FILING_FULL_WORD": {
        "exts": {".doc", ".docx"},
        "mimes": _WORD_MIME_TYPES,
    },
    "FILING_XML_ZIP": {
        "exts": {".zip"},
        "mimes": _ZIP_MIME_TYPES,
    },
    "FILING_MERGED_PDF": {
        "exts": {".pdf"},
        "mimes": _PDF_MIME_TYPES,
    },
    "OFFICIAL_NOTICE_PDF": {
        "exts": {".pdf"},
        "mimes": _PDF_MIME_TYPES,
    },
    "ELECTRONIC_RECEIPT": {
        "exts": {".pdf"},
        "mimes": _PDF_MIME_TYPES,
    },
    "OA_STATEMENT_WORD": {
        "exts": {".doc", ".docx"},
        "mimes": _WORD_MIME_TYPES,
    },
    "OA_STATEMENT_PDF": {
        "exts": {".pdf"},
        "mimes": _PDF_MIME_TYPES,
    },
    "OA_MODIFIED_CLAIMS": {
        "exts": {".doc", ".docx"},
        "mimes": _WORD_MIME_TYPES,
    },
    "OA_AMENDMENT_COMPARISON": {
        "exts": {".doc", ".docx", ".pdf"},
        "mimes": _WORD_MIME_TYPES | _PDF_MIME_TYPES,
    },
    "OA_OTHER_PROOF": {
        "exts": {".doc", ".docx", ".jpg", ".jpeg", ".pdf", ".png", ".xls", ".xlsx", ".zip"},
        "mimes": _PROOF_MIME_TYPES,
    },
    "OA_ADDITIONAL_FILE": {
        "exts": {".doc", ".docx", ".jpg", ".jpeg", ".pdf", ".png", ".xls", ".xlsx", ".zip"},
        "mimes": _PROOF_MIME_TYPES,
    },
}

_ATTACHMENT_ROLE_ALIASES = {
    "技术交底书": "TECHNICAL_DISCLOSURE",
    "委托指示": "COMMISSION_INSTRUCTION",
    "完整递交文件": "FILING_FULL_WORD",
    "摘要": "FILING_ABSTRACT",
    "权利要求书": "CLAIMS",
    "说明书": "FILING_DESCRIPTION",
    "说明书附图": "FILING_DRAWINGS",
    "序列表": "FILING_SEQUENCE_LISTING",
    "xml压缩包": "FILING_XML_ZIP",
    "XML压缩包": "FILING_XML_ZIP",
    "合并PDF": "FILING_MERGED_PDF",
    "合并 PDF": "FILING_MERGED_PDF",
    "电子申请回执": "ELECTRONIC_RECEIPT",
}

_HISTORICAL_ATTACHMENT_ALIASES = {
    "PCT 公开文本",
    "补正后的说明书",
    "补正后说明书",
    "递交电子申请文件",
    "递交的电子申请文件",
    "客户提供原始文件",
}


def _merge_document_create_extra_data(
    data: DocumentCreateIn | DocumentImpactPreviewIn,
) -> str | None:
    structured_fields = (
        "official_due_date",
        "official_due_date_source",
        "official_due_date_status",
        "description",
    )
    updates = {
        field: getattr(data, field) for field in structured_fields if field in data.model_fields_set
    }
    try:
        if not updates:
            parsed = parse_document_extra_data(data.extra_data)
            if parsed.official_due_date_status == "LEGACY_UNVERIFIED":
                raise DocumentExtraDataBusinessError(
                    "OfficialDueDate",
                    "writes require date, source, and write status together",
                )
            return data.extra_data
        return merge_document_extra_data(data.extra_data, **updates)
    except DocumentExtraDataShapeError as exc:
        raise_business_error(
            "DOCUMENT_EXTRA_DATA_INVALID",
            "Document extra data has an invalid shape",
            details={"field": exc.field, "reason": exc.reason},
            status_code=422,
        )
    except DocumentExtraDataBusinessError as exc:
        raise_business_error(
            "DOCUMENT_DEADLINE_INVALID",
            "Document deadline fields are incomplete or inconsistent",
            details={"field": exc.field, "reason": exc.reason},
            status_code=400,
        )


def _is_official_notice_catalog_template(template: DocTemplate) -> bool:
    template_code = (_normalize_text(template.code) or "").upper()
    if template_code.startswith("OFFICIAL_NOTICE_"):
        return True
    try:
        metadata = json.loads(template.input_fields or "null")
    except (json.JSONDecodeError, TypeError):
        return False
    return bool(
        isinstance(metadata, dict)
        and (_normalize_text(metadata.get("catalog_kind")) or "").upper() == "OFFICIAL_NOTICE"
    )


def _validate_document_template_execution_gate(template: DocTemplate) -> None:
    if not _is_official_notice_catalog_template(template):
        return
    semantics = resolve_document_semantics(template)
    if semantics.catalog_status == "EXECUTABLE":
        return
    raise_business_error(
        "DOCUMENT_TEMPLATE_REFERENCE_ONLY",
        "Official notice catalog template is reference-only",
        details={
            "template_id": template.id,
            "template_code": template.code,
            "catalog_status": semantics.catalog_status,
        },
        status_code=409,
    )


def _validate_document_create_deadline(template: DocTemplate | None, extra_data: str | None) -> None:
    if template is None:
        return
    semantics = resolve_document_semantics(template)
    if semantics.deadline_source_policy != "EXPLICIT_OFFICIAL_DUE_REQUIRED":
        return
    deadline = parse_document_extra_data(extra_data)
    if (
        deadline.official_due_date is not None
        and deadline.official_due_date_source
        in {"MANUAL_OFFICIAL_NOTICE", "IMPORTED_OFFICIAL_NOTICE"}
        and deadline.official_due_date_status == "CONFIRMED"
    ):
        return
    error_code = {
        "OA_REPLY": "OA_OFFICIAL_DUE_DATE_REQUIRED",
        "GRANT_NOTICE": "GRANT_OFFICIAL_DUE_DATE_REQUIRED",
    }.get(
        semantics.execution_behavior,
        "DOCUMENT_OFFICIAL_DUE_DATE_REQUIRED",
    )
    raise_business_error(
        error_code,
        "Executable notice creation requires a confirmed explicit official due date",
        details={"status": deadline.official_due_date_status},
        status_code=409,
    )


def _is_oa_out_template(template: DocTemplate | None) -> bool:
    return bool(template and (template.code or "").strip().upper() == "OA_OUT")


def _reply_source_waits_for_receipt_archive(
    db: Session,
    source_document: Document,
) -> bool:
    if not source_document.doc_template_id:
        return False
    source_template = db.execute(
        select(DocTemplate).where(DocTemplate.id == source_document.doc_template_id)
    ).scalar_one_or_none()
    if not source_template:
        return False
    semantics = resolve_document_semantics(source_template)
    return (
        semantics.execution_behavior == "OA_REPLY"
        and semantics.completion_event == "OFFICIAL_RECEIPT_ARCHIVED"
    )


def _apply_template_defaults(
    *,
    case: Case,
    document: Document,
    template: DocTemplate | None,
    need_reply_overridden: bool = False,
) -> None:
    if not template:
        return

    semantics = resolve_document_semantics(template)
    if not need_reply_overridden:
        document.need_reply = semantics.requires_reply


def _advance_grant_notice_case_after_attachment(db: Session, *, document: Document) -> None:
    if document.direction != DocumentDirection.IN or not document.doc_template_id:
        return

    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
    ).scalar_one_or_none()
    if not template or (template.code or "").strip().upper() != "GRANT_NOTICE":
        return

    from app.modules.grant_fees.service import ensure_grant_fee_task_for_notice_document

    ensure_grant_fee_task_for_notice_document(db, document=document, template=template)


def _is_patent_certificate_document(db: Session, document: Document) -> bool:
    if not document.doc_template_id:
        return False
    template = db.get(DocTemplate, document.doc_template_id)
    if template is None or (template.code or "").strip().upper() != "OFFICIAL_NOTICE_010":
        return False
    try:
        metadata = json.loads(template.input_fields or "null")
    except (json.JSONDecodeError, TypeError):
        return False
    return bool(
        isinstance(metadata, dict)
        and metadata.get("catalog_kind") == "OFFICIAL_NOTICE"
        and metadata.get("official_notice_name") == "专利证书"
    )


def _capture_document_activity_projection(case: Case) -> LifecycleProjection:
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


def _append_certificate_archived_activity(
    db: Session,
    *,
    document: Document,
    evidence_version: EvidenceVersionResult,
) -> None:
    if not _is_patent_certificate_document(db, document):
        return
    case = db.get(Case, document.case_id)
    version = db.get(DocumentEvidenceVersion, evidence_version.evidence_version_id)
    if case is None:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    if version is None:
        raise_business_error(
            "EVIDENCE_VERSION_NOT_FOUND",
            "Evidence version not found",
            status_code=404,
        )
    projection = _capture_document_activity_projection(case)
    append_case_activity(
        LifecycleEventCommand(
            case_id=case.id,
            event_type="CERTIFICATE_ARCHIVED",
            lane=ActivityLane.DOCUMENT,
            effective_at=version.created_at,
            occurred_at=version.created_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=case.id,
                    evidence_kind="DOCUMENT_EVIDENCE_VERSION",
                    object_type="DocumentEvidenceVersion",
                    object_id=version.id,
                    content_hash=version.content_hash,
                    captured_at=version.created_at,
                ),
            ),
            actor_id=evidence_version.creator_id,
            reviewer_id=None,
            idempotency_key=f"certificate-archived:{version.id}",
            source_activity_id=None,
            supersedes_event_id=None,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={
                "attachment_id": version.attachment_id,
                "document_id": version.document_id,
                "evidence_version_id": version.id,
            },
        ),
        db,
        previous_projection=projection,
        current_projection=projection,
        legacy_case_status=case.status,
        conflict_codes=(),
    )


def _apply_reply_chain(
    db: Session,
    *,
    document: Document,
    doc_date: date | None,
    template: DocTemplate | None,
) -> None:
    if not document.reply_to_id or document.direction != DocumentDirection.OUT:
        return

    original_doc = db.execute(
        select(Document).where(Document.id == document.reply_to_id)
    ).scalar_one_or_none()
    if not original_doc:
        raise_business_error(
            "REPLY_TO_DOC_NOT_FOUND", "Reply-to document not found", status_code=404
        )

    if not _is_oa_out_template(template):
        original_doc.reply_date = doc_date
    if _reply_source_waits_for_receipt_archive(db, original_doc):
        return

    open_tasks = (
        db.execute(
            select(Task).where(
                Task.document_id == document.reply_to_id,
                Task.status == TaskStatus.OPEN.value,
            )
        )
        .scalars()
        .all()
    )

    for task in open_tasks:
        task.status = TaskStatus.DONE.value
        task.done_at = datetime.utcnow()
        _create_task_log(
            db,
            task_id=task.id,
            action=TaskAction.AUTO_WRITEOFF,
            from_status=TaskStatus.OPEN.value,
            to_status=TaskStatus.DONE.value,
            remark=f"Auto write-off: reply document {document.id}",
        )


def _validate_reply_to_document(
    db: Session,
    *,
    case_id: str,
    reply_to_id: str | None,
    template: DocTemplate | None,
) -> None:
    if not reply_to_id:
        return

    original_doc = db.execute(
        select(Document).where(Document.id == reply_to_id)
    ).scalar_one_or_none()
    if not original_doc:
        raise_business_error(
            "REPLY_TO_DOC_NOT_FOUND", "Reply-to document not found", status_code=404
        )

    if original_doc.case_id != case_id:
        raise_business_error(
            "REPLY_TO_CASE_MISMATCH",
            "Reply-to document must belong to the same case",
            status_code=400,
        )

    expected_template_code = _normalize_text(getattr(template, "reply_to_template_code", None))
    if expected_template_code:
        original_template = None
        original_template_code = None
        if original_doc.doc_template_id:
            original_template = db.execute(
                select(DocTemplate).where(DocTemplate.id == original_doc.doc_template_id)
            ).scalar_one_or_none()
            original_template_code = _normalize_text(getattr(original_template, "code", None))
        matches_expected_template = original_template_code == expected_template_code
        if (
            not matches_expected_template
            and expected_template_code.upper() == "OA_IN"
            and original_template is not None
        ):
            original_semantics = resolve_document_semantics(original_template)
            matches_expected_template = (
                original_semantics.catalog_status == "EXECUTABLE"
                and original_semantics.execution_behavior == "OA_REPLY"
            )
        if not matches_expected_template:
            raise_business_error(
                "REPLY_TO_TEMPLATE_MISMATCH",
                "Reply-to document template does not match reply template rule",
                status_code=400,
            )


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _normalize_attachment_role(value: str | None) -> str | None:
    role = _normalize_text(value)
    if not role:
        return None
    return role.upper()


def _resolve_attachment_role_from_alias(source_role_alias: str | None) -> str | None:
    alias = _normalize_text(source_role_alias)
    if not alias:
        return None
    return _ATTACHMENT_ROLE_ALIASES.get(alias)


def _attachment_role_definition(role: str | None) -> dict[str, object] | None:
    if not role:
        return None
    return _ATTACHMENT_ROLE_DEFINITIONS.get(role)


def _validate_attachment_file_rule(
    *,
    official_file_role: str | None,
    file_name: str,
    content_type: str,
) -> None:
    if not official_file_role:
        return

    rule = _ATTACHMENT_ROLE_FILE_RULES.get(official_file_role)
    if not rule:
        return

    ext = Path(file_name).suffix.lower()
    allowed_exts = rule["exts"]
    if ext not in allowed_exts:
        raise_business_error(
            "ATTACHMENT_EXTENSION_NOT_ALLOWED",
            "Attachment extension not allowed for selected official file role",
            details={
                "official_file_role": official_file_role,
                "extension": ext,
                "allowed_extensions": sorted(allowed_exts),
            },
            status_code=400,
        )

    allowed_mime_types = rule["mimes"]
    normalized_content_type = content_type.split(";", 1)[0].strip().lower()
    if normalized_content_type not in allowed_mime_types:
        raise_business_error(
            "ATTACHMENT_MIME_NOT_ALLOWED",
            "Attachment mime type not allowed for selected official file role",
            details={
                "official_file_role": official_file_role,
                "mime_type": normalized_content_type,
                "allowed_mime_types": sorted(allowed_mime_types),
            },
            status_code=400,
        )


def _resolve_attachment_manifest_metadata(
    *,
    official_file_role: str | None = None,
    source_role_alias: str | None = None,
    external_upload_position: str | None = None,
    package_usage_hint: str | None = None,
    is_archive_evidence: bool | None = None,
    is_receipt_evidence: bool | None = None,
) -> dict[str, object | None]:
    role = _normalize_attachment_role(official_file_role)
    alias = _normalize_text(source_role_alias)
    if role is None:
        role = _resolve_attachment_role_from_alias(alias)

    definition = _attachment_role_definition(role)
    if role and not definition:
        raise_business_error(
            "ATTACHMENT_OFFICIAL_ROLE_INVALID",
            "Attachment official file role is invalid",
            details={"official_file_role": role},
            status_code=400,
        )

    archive_default = bool(definition and definition.get("is_archive_evidence"))
    receipt_default = bool(definition and definition.get("is_receipt_evidence"))
    return {
        "official_file_role": role,
        "source_role_alias": alias,
        "external_upload_position": _normalize_text(external_upload_position)
        or (
            str(definition["external_upload_position"])
            if definition and definition.get("external_upload_position")
            else None
        ),
        "package_usage_hint": _normalize_text(package_usage_hint)
        or (
            str(definition["package_usage_hint"])
            if definition and definition.get("package_usage_hint")
            else None
        ),
        "is_archive_evidence": archive_default
        if is_archive_evidence is None
        else is_archive_evidence,
        "is_receipt_evidence": receipt_default
        if is_receipt_evidence is None
        else is_receipt_evidence,
    }


def _attachment_manifest_item(attachment: DocAttachment) -> AttachmentManifestItemOut:
    metadata = _resolve_attachment_manifest_metadata(
        official_file_role=getattr(attachment, "official_file_role", None),
        source_role_alias=getattr(attachment, "source_role_alias", None),
        external_upload_position=getattr(attachment, "external_upload_position", None),
        package_usage_hint=getattr(attachment, "package_usage_hint", None),
        is_archive_evidence=getattr(attachment, "is_archive_evidence", None),
        is_receipt_evidence=getattr(attachment, "is_receipt_evidence", None),
    )
    return AttachmentManifestItemOut(
        attachment_id=attachment.id,
        document_id=attachment.document_id,
        file_name=attachment.file_name,
        official_file_role=metadata["official_file_role"],
        source_role_alias=metadata["source_role_alias"],
        external_upload_position=metadata["external_upload_position"],
        content_hash=attachment.content_hash,
        package_usage_hint=metadata["package_usage_hint"],
        is_archive_evidence=bool(metadata["is_archive_evidence"]),
        is_receipt_evidence=bool(metadata["is_receipt_evidence"]),
    )


def summarize_attachment_manifest(
    attachments: list[DocAttachment],
    *,
    require_commission_instruction: bool = False,
) -> AttachmentManifestSummaryOut:
    intake_gate_roles: list[AttachmentManifestItemOut] = []
    filing_roles: list[AttachmentManifestItemOut] = []
    oa_roles: list[AttachmentManifestItemOut] = []
    archive_roles: list[AttachmentManifestItemOut] = []
    historical_alias_roles: list[AttachmentManifestItemOut] = []

    for attachment in attachments:
        item = _attachment_manifest_item(attachment)
        definition = _attachment_role_definition(item.official_file_role)
        category = definition.get("category") if definition else None
        if category == ATTACHMENT_ROLE_CATEGORY_INTAKE:
            intake_gate_roles.append(item)
        elif category == ATTACHMENT_ROLE_CATEGORY_FILING:
            filing_roles.append(item)
        elif category == ATTACHMENT_ROLE_CATEGORY_OA:
            oa_roles.append(item)
        elif category == ATTACHMENT_ROLE_CATEGORY_ARCHIVE:
            archive_roles.append(item)
        elif item.source_role_alias in _HISTORICAL_ATTACHMENT_ALIASES:
            historical_alias_roles.append(item)

    present_intake_roles = {
        item.official_file_role for item in intake_gate_roles if item.official_file_role
    }
    missing_intake_gate_roles: list[str] = []
    if "TECHNICAL_DISCLOSURE" not in present_intake_roles:
        missing_intake_gate_roles.append("TECHNICAL_DISCLOSURE")
    if require_commission_instruction and "COMMISSION_INSTRUCTION" not in present_intake_roles:
        missing_intake_gate_roles.append("COMMISSION_INSTRUCTION")

    return AttachmentManifestSummaryOut(
        intake_gate_roles=intake_gate_roles,
        filing_roles=filing_roles,
        oa_roles=oa_roles,
        archive_roles=archive_roles,
        historical_alias_roles=historical_alias_roles,
        missing_intake_gate_roles=missing_intake_gate_roles,
    )


def _resolve_case_title(case: Case) -> str | None:
    return _normalize_text(getattr(case, "title_cn", None)) or _normalize_text(
        getattr(case, "title_en", None)
    )


def _format_mailing_address(address: ClientAddress) -> str | None:
    parts: list[str] = []
    for value in (
        address.address_line1,
        address.address_line2,
        address.city,
        address.province,
        address.postal_code,
        address.country_code,
    ):
        normalized = _normalize_text(value)
        if normalized:
            parts.append(normalized)
    if not parts:
        return None
    return ", ".join(parts)


def _format_applicant_address(applicant: T_CaseApplicant) -> str | None:
    parts: list[str] = []
    for value in (applicant.address_cn, applicant.address_en):
        normalized = _normalize_text(value)
        if normalized:
            parts.append(normalized)
    if not parts:
        return None
    return " / ".join(parts)


def _resolve_envelope_preview(
    db: Session,
    *,
    document: Document,
    case: Case,
) -> DocumentEnvelopePreviewOut:
    client = None
    if case.client_id:
        client = db.execute(select(Client).where(Client.id == case.client_id)).scalar_one_or_none()

    client_name = None
    if client:
        client_name = _normalize_text(client.name_cn) or _normalize_text(client.name_en)

    if case.doc_address_id:
        address = db.execute(
            select(ClientAddress).where(ClientAddress.id == case.doc_address_id)
        ).scalar_one_or_none()
        if address:
            recipient_address = _format_mailing_address(address)
            if recipient_address:
                return DocumentEnvelopePreviewOut(
                    document_id=document.id,
                    case_id=case.id,
                    case_no=case.case_no,
                    client_id=case.client_id,
                    client_name=client_name,
                    recipient_name=client_name,
                    recipient_address=recipient_address,
                    address_source="CASE_DOC_ADDRESS",
                )

    if case.client_id:
        default_address = db.execute(
            select(ClientAddress)
            .where(
                ClientAddress.client_id == case.client_id,
                ClientAddress.is_default.is_(True),
            )
            .order_by(ClientAddress.updated_at.desc(), ClientAddress.created_at.desc())
        ).scalar_one_or_none()
        if default_address:
            recipient_address = _format_mailing_address(default_address)
            if recipient_address:
                return DocumentEnvelopePreviewOut(
                    document_id=document.id,
                    case_id=case.id,
                    case_no=case.case_no,
                    client_id=case.client_id,
                    client_name=client_name,
                    recipient_name=client_name,
                    recipient_address=recipient_address,
                    address_source="CLIENT_DEFAULT_ADDRESS",
                )

    first_applicant = db.execute(
        select(T_CaseApplicant)
        .where(T_CaseApplicant.case_id == case.id)
        .order_by(T_CaseApplicant.is_first.desc(), T_CaseApplicant.seq.asc())
    ).scalar_one_or_none()
    if first_applicant:
        recipient_address = _format_applicant_address(first_applicant)
        if recipient_address:
            recipient_name = _normalize_text(first_applicant.name_cn) or _normalize_text(
                first_applicant.name_en
            )
            return DocumentEnvelopePreviewOut(
                document_id=document.id,
                case_id=case.id,
                case_no=case.case_no,
                client_id=case.client_id,
                client_name=client_name,
                recipient_name=recipient_name,
                recipient_address=recipient_address,
                address_source="FIRST_APPLICANT_ADDRESS",
            )

    return DocumentEnvelopePreviewOut(
        document_id=document.id,
        case_id=case.id,
        case_no=case.case_no,
        client_id=case.client_id,
        client_name=client_name,
        recipient_name=None,
        recipient_address=None,
        address_source="MANUAL_REQUIRED",
    )


def _create_document_record(
    db: Session,
    data: DocumentCreateIn,
    *,
    commit: bool,
) -> Document:
    case = db.execute(select(Case).where(Case.id == data.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    template = None
    if data.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == data.doc_template_id)
        ).scalar_one_or_none()
        if not template:
            raise_business_error(
                "DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404
            )
        _validate_document_template_execution_gate(template)

    _validate_reply_to_document(
        db,
        case_id=data.case_id,
        reply_to_id=data.reply_to_id,
        template=template,
    )

    extra_data = _merge_document_create_extra_data(data)
    _validate_document_create_deadline(template, extra_data)
    document = Document(
        id=str(uuid4()),
        case_id=data.case_id,
        doc_template_id=data.doc_template_id,
        doc_type=data.doc_type,
        direction=data.direction,
        doc_date=data.doc_date,
        title=data.title,
        ref_no=data.ref_no,
        extra_data=extra_data,
        reply_to_id=data.reply_to_id,
    )
    db.add(document)
    db.flush()

    _apply_template_defaults(case=case, document=document, template=template)
    _apply_reply_chain(
        db,
        document=document,
        doc_date=data.doc_date,
        template=template,
    )

    if commit:
        db.commit()
        db.refresh(document)
    return document


def list_documents(
    db: Session,
    *,
    q: str | None = None,
    doc_name: str | None = None,
    direction: DocumentDirection | None = None,
    doc_types: list[DocumentDocType] | None = None,
    template_code: str | None = None,
    doc_template_id: str | None = None,
    case_no: str | None = None,
    case_id: str | None = None,
    client_id: str | None = None,
    need_reply: bool | None = None,
    replied: bool | None = None,
    has_attachment: bool | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Document], int]:
    """List documents with filters and pagination."""
    stmt = select(Document)
    joined_case = False

    if q:
        q_like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Document.title).like(q_like),
                func.lower(Document.ref_no).like(q_like),
            )
        )
    if doc_name:
        stmt = stmt.where(func.lower(Document.title).like(f"%{doc_name.lower()}%"))

    if direction:
        stmt = stmt.where(Document.direction == direction)
    if doc_types:
        stmt = stmt.where(Document.doc_type.in_([doc_type.value for doc_type in doc_types]))
    if template_code:
        stmt = stmt.join(DocTemplate, Document.doc_template_id == DocTemplate.id)
        stmt = stmt.where(func.lower(DocTemplate.code) == template_code.lower())
    if doc_template_id:
        stmt = stmt.where(Document.doc_template_id == doc_template_id)
    if case_no:
        stmt = stmt.join(Case, Document.case_id == Case.id)
        joined_case = True
        stmt = stmt.where(func.lower(Case.case_no).like(f"%{case_no.lower()}%"))
    if case_id:
        stmt = stmt.where(Document.case_id == case_id)
    if client_id:
        if not joined_case:
            stmt = stmt.join(Case, Document.case_id == Case.id)
            joined_case = True
        stmt = stmt.where(Case.client_id == client_id)
    if need_reply is not None:
        stmt = stmt.where(Document.need_reply.is_(need_reply))
    if replied is True:
        stmt = stmt.where(Document.reply_date.is_not(None))
    elif replied is False:
        stmt = stmt.where(Document.reply_date.is_(None))
    if has_attachment is True:
        stmt = stmt.where(exists(select(1).where(DocAttachment.document_id == Document.id)))
    elif has_attachment is False:
        stmt = stmt.where(~exists(select(1).where(DocAttachment.document_id == Document.id)))
    if date_from:
        stmt = stmt.where(Document.doc_date >= date_from)
    if date_to:
        stmt = stmt.where(Document.doc_date <= date_to)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = (
        stmt.order_by(
            Document.doc_date.desc(),
            Document.created_at.desc(),
            Document.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    items = db.execute(stmt).scalars().all()
    return items, total


def create_document(db: Session, data: DocumentCreateIn) -> Document:
    return _create_document_record(db, data, commit=False)


def preview_document_impact(
    db: Session,
    data: DocumentImpactPreviewIn,
) -> DocumentImpactPreviewOut:
    case = db.execute(select(Case).where(Case.id == data.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    template = None
    if data.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == data.doc_template_id)
        ).scalar_one_or_none()
        if not template:
            raise_business_error(
                "DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404
            )

    status_impacts: list[DocumentImpactItemOut] = []
    deadline_impacts: list[DocumentImpactItemOut] = []
    task_impacts: list[DocumentImpactItemOut] = []
    fee_impacts: list[DocumentImpactItemOut] = []
    file_status_impacts: list[DocumentImpactItemOut] = []
    confirmation_items: list[str] = []
    risk_tips: list[str] = []
    deadline = parse_document_extra_data(_merge_document_create_extra_data(data))

    if template:
        semantics = resolve_document_semantics(template)
        if semantics.case_status_effect or _normalize_text(template.status_restore):
            risk_tips.append(
                "文书登记不会直接变更案件法律状态；"
                "请通过已复核证据的生命周期入口确认状态变化"
            )

        if semantics.deadline_source_policy == "EXPLICIT_OFFICIAL_DUE_REQUIRED" and (
            deadline.official_due_date is None or deadline.official_due_date_status != "CONFIRMED"
        ):
            error_code = {
                "OA_REPLY": "OA_OFFICIAL_DUE_DATE_REQUIRED",
                "GRANT_NOTICE": "GRANT_OFFICIAL_DUE_DATE_REQUIRED",
            }.get(
                semantics.execution_behavior,
                "DOCUMENT_OFFICIAL_DUE_DATE_REQUIRED",
            )
            raise_business_error(
                error_code,
                "Executable notice preview requires a confirmed explicit official due date",
                details={"status": deadline.official_due_date_status},
                status_code=409,
            )

        if semantics.deadline_source_policy == "EXPLICIT_OFFICIAL_DUE_REQUIRED":
            assert deadline.official_due_date is not None
            deadline_impacts.append(
                DocumentImpactItemOut(
                    kind="OFFICIAL_DUE_DATE",
                    title="官方期限",
                    effect=deadline.official_due_date.isoformat(),
                    detail=(
                        f"来源 {deadline.official_due_date_source}；"
                        f"确认状态 {deadline.official_due_date_status}"
                    ),
                )
            )
            if semantics.task_template_code:
                task_impacts.append(
                    DocumentImpactItemOut(
                        kind="AUTO_TASK",
                        title="任务影响",
                        effect=semantics.task_template_code,
                        requires_confirmation=True,
                        detail="登记后将按已确认官方期限生成或更新期限任务",
                    )
                )
                confirmation_items.append("期限任务将受已确认官方期限影响")
        elif _normalize_text(template.deadline_template_code):
            deadline_impacts.append(
                DocumentImpactItemOut(
                    kind="DEADLINE_TEMPLATE",
                    title="期限模板影响",
                    effect=template.deadline_template_code,
                    requires_confirmation=True,
                    detail="登记后将按模板计算期限",
                )
            )
            task_impacts.append(
                DocumentImpactItemOut(
                    kind="AUTO_TASK",
                    title="任务影响",
                    effect=template.deadline_template_code,
                    requires_confirmation=True,
                    detail="登记后将生成或更新期限任务",
                )
            )
            confirmation_items.append("期限任务将受模板影响")

        suppress_grant_auto_draft = (
            _normalize_text(template.code) or ""
        ).upper() == "GRANT_NOTICE" or (
            semantics.catalog_status == "EXECUTABLE"
            and semantics.execution_behavior == "GRANT_NOTICE"
            and semantics.fee_trigger == "GRANT_FEE"
        )
        if _normalize_text(template.fee_draft_type) and not suppress_grant_auto_draft:
            fee_impacts.append(
                DocumentImpactItemOut(
                    kind="FEE_DRAFT",
                    title="费用影响",
                    effect=template.fee_draft_type,
                    requires_confirmation=True,
                    detail="登记后将尝试生成费用草稿",
                )
            )
            confirmation_items.append("费用草稿将受模板影响")

        if semantics.requires_reply and data.direction == DocumentDirection.IN:
            file_status_impacts.append(
                DocumentImpactItemOut(
                    kind="NEED_REPLY",
                    title="文件状态影响",
                    effect="NEED_REPLY",
                    detail="登记后该文件将标记为需答复",
                )
            )
    else:
        risk_tips.append("未选择文件模板，系统不能预览模板驱动的状态、期限、任务或费用影响")

    if data.reply_to_id:
        source_document = db.execute(
            select(Document).where(Document.id == data.reply_to_id)
        ).scalar_one_or_none()
        if not source_document:
            raise_business_error(
                "REPLY_TO_DOC_NOT_FOUND", "Reply-to document not found", status_code=404
            )
        if source_document.case_id != data.case_id:
            raise_business_error(
                "REPLY_TO_DOC_CASE_MISMATCH",
                "Reply-to document does not belong to this case",
                status_code=400,
            )
        file_status_impacts.append(
            DocumentImpactItemOut(
                kind="REPLY_SOURCE",
                title="回复来源文件影响",
                effect="REPLIED",
                requires_confirmation=True,
                document_id=source_document.id,
                detail="登记后回复来源文件将记录答复日期",
            )
        )
        confirmation_items.append("回复来源文件将登记答复日期")
    elif data.direction == DocumentDirection.OUT:
        risk_tips.append("未选择回复来源文件，系统不能预览来源文件的答复状态影响")

    return DocumentImpactPreviewOut(
        case_id=case.id,
        case_no=case.case_no,
        template_code=template.code if template else None,
        official_due_date=deadline.official_due_date,
        official_due_date_source=deadline.official_due_date_source,
        official_due_date_status=deadline.official_due_date_status,
        description=deadline.description,
        status_impacts=status_impacts,
        deadline_impacts=deadline_impacts,
        task_impacts=task_impacts,
        fee_impacts=fee_impacts,
        file_status_impacts=file_status_impacts,
        confirmation_required=bool(confirmation_items),
        confirmation_items=list(dict.fromkeys(confirmation_items)),
        risk_tips=risk_tips,
    )


def create_document_wizard_batch(
    db: Session,
    data: DocumentWizardBatchCreateIn,
    *,
    actor_id: str | None = None,
) -> list[tuple[int, Document]]:
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == data.defaults.doc_template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)

    rows = data.rows
    _validate_document_wizard_rows(db, rows)

    created_rows: list[tuple[int, Document]] = []
    managed_generated_files: list[Path] = []
    committed = False
    task_rows_by_row_index: dict[int, list[DocumentWizardTaskFinalRowIn]] = {}
    fee_rows_by_row_index: dict[int, DocumentWizardFeeFinalRowIn] = {}
    attachment_rows_by_row_index: dict[int, list[DocumentWizardAttachmentFinalRowIn]] = {}
    if data.task_rows:
        task_rows_by_row_index = _group_document_wizard_task_rows(
            data.task_rows, row_count=len(rows)
        )
    if data.fee_rows:
        fee_rows_by_row_index = _group_document_wizard_fee_rows(data.fee_rows, row_count=len(rows))
    if fee_rows_by_row_index:
        semantics = resolve_document_semantics(template)
        if (
            semantics.catalog_status == "EXECUTABLE"
            and semantics.execution_behavior == "APPLICATION_FEE_NOTICE"
        ):
            raise_business_error(
                "DOCUMENT_WIZARD_BATCH_INVALID",
                "Document wizard batch contains invalid fee rows",
                details={
                    "row_errors": [
                        {
                            "row_index": row_index,
                            "field": "fee_draft_type",
                            "code": "APPLICATION_FEE_NOTICE_DRAFT_FORBIDDEN",
                            "message": (
                                "Application-fee notice wizard rows cannot create generic fee drafts"
                            ),
                        }
                        for row_index in sorted(fee_rows_by_row_index)
                    ]
                },
                status_code=400,
            )
    if data.attachment_rows:
        attachment_rows_by_row_index = _group_document_wizard_attachment_rows(
            data.attachment_rows, row_count=len(rows)
        )
    try:
        for idx, row in enumerate(rows, start=1):
            payload = _build_document_wizard_payload(data.defaults, row, template)
            document = _create_document_record(db, payload, commit=False)
            explicit_task_rows = task_rows_by_row_index.get(idx, [])
            if explicit_task_rows:
                _create_document_wizard_tasks_from_rows(
                    db,
                    document=document,
                    row_task_rows=explicit_task_rows,
                )
            explicit_fee_row = fee_rows_by_row_index.get(idx)
            if explicit_fee_row:
                if _normalize_text(explicit_fee_row.case_id) != document.case_id:
                    raise_business_error(
                        "DOCUMENT_WIZARD_BATCH_INVALID",
                        "Document wizard batch contains invalid fee rows",
                        details={
                            "row_errors": [
                                {
                                    "row_index": idx,
                                    "field": "case_id",
                                    "code": "CASE_ID_MISMATCH",
                                    "message": "Fee row case_id does not match document row case_id",
                                    "case_id": explicit_fee_row.case_id,
                                    "document_case_id": document.case_id,
                                }
                            ]
                        },
                        status_code=400,
                    )
                create_fee_draft_from_wizard_row(db, document, explicit_fee_row)
            else:
                maybe_create_fee_draft(db, document, template)
            explicit_attachment_rows = attachment_rows_by_row_index.get(idx, [])
            if explicit_attachment_rows:
                managed_generated_files.extend(
                    _create_document_wizard_attachments_from_rows(
                        db,
                        document=document,
                        doc_template=template,
                        row_attachment_rows=explicit_attachment_rows,
                        actor_id=actor_id,
                    )
                )
            if _is_oa_out_template(template):
                from app.modules.official_workflows.service import (
                    prepare_oa_out_package_link,
                )

                prepare_oa_out_package_link(
                    db,
                    reply_document=document,
                    actor_id=actor_id,
                )
            if not explicit_task_rows:
                TaskGenerationService().generate_from_document(db, document)
            created_rows.append((idx, document))

        db.commit()
        committed = True
        for _, document in created_rows:
            db.refresh(document)
        return created_rows
    except Exception as exc:
        db.rollback()
        if not committed:
            for managed_file_path in managed_generated_files:
                _remove_managed_attachment_file(managed_file_path, original_error=exc)
        raise


def preview_document_wizard_tasks(
    db: Session,
    data: DocumentWizardBatchCreateIn,
) -> list[dict[str, object]]:
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == data.defaults.doc_template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)

    _validate_document_wizard_rows(db, data.rows)

    case_ids = [_normalize_text(row.case_id) for row in data.rows]
    cases = db.execute(select(Case).where(Case.id.in_(case_ids))).scalars().all()
    case_by_id = {case.id: case for case in cases}
    task_service = TaskGenerationService()
    preview_rows: list[dict[str, object]] = []

    for idx, row in enumerate(data.rows, start=1):
        payload = _build_document_wizard_payload(data.defaults, row, template)
        case = case_by_id[payload.case_id]
        preview_document = SimpleNamespace(
            id=None,
            case_id=payload.case_id,
            doc_date=payload.doc_date,
            direction=getattr(payload.direction, "value", payload.direction),
            doc_template_id=payload.doc_template_id,
            extra_data=_merge_document_create_extra_data(payload),
            title=payload.title,
            case=case,
        )
        task_templates = _list_task_templates_for_preview(db, task_service, preview_document)
        if not task_templates:
            continue

        for task_template in task_templates:
            due_date = task_service._compute_due_date(preview_document, case, task_template)
            title = task_template.name or task_template.code
            inner_offset = getattr(task_template, "inner_offset_days", None)
            internal_due_date = (
                due_date - timedelta(days=inner_offset) if inner_offset is not None else None
            )
            remind1, remind2, remind3, daily_remind_from = task_service._compute_reminders(
                due_date,
                internal_due_date,
                task_template,
            )
            preview_rows.append(
                {
                    "row_index": idx,
                    "case_id": case.id,
                    "case_no": case.case_no,
                    "source_title": _resolve_case_title(case),
                    "document_title": payload.title,
                    "task_template_code": task_template.code,
                    "task_template_name": task_template.name,
                    "title": title,
                    "base_date": preview_document.doc_date,
                    "due_date": due_date,
                    "internal_due_date": internal_due_date,
                    "remind1": remind1,
                    "remind2": remind2,
                    "remind3": remind3,
                    "daily_remind_from": daily_remind_from,
                    "daily_remind": bool(getattr(task_template, "daily_remind", False)),
                }
            )

    return preview_rows


def _backend_storage_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "storage"


def _resolve_document_template_file_path(file_path: str) -> str:
    normalized_path = _normalize_text(file_path)
    if not normalized_path:
        raise_business_error(
            "DOCUMENT_TEMPLATE_SOURCE_NOT_FOUND",
            "Document template source is not configured",
            status_code=409,
        )

    candidate = Path(normalized_path)
    storage_root = _backend_storage_dir()

    if candidate.is_absolute():
        resolved = candidate
    elif normalized_path.startswith("storage/"):
        resolved = (storage_root.parent / candidate).resolve()
    elif normalized_path.startswith("templates/"):
        resolved = Path(safe_join(str(storage_root), normalized_path))
    else:
        resolved = Path(safe_join(str(storage_root / "templates"), normalized_path))

    if not resolved.exists():
        raise_business_error(
            "DOCUMENT_TEMPLATE_FILE_NOT_FOUND",
            "Document template file not found",
            details={"file_path": str(resolved)},
            status_code=409,
        )

    return str(resolved)


def resolve_document_template_render_source(
    db: Session,
    *,
    doc_template: DocTemplate,
) -> tuple[Template, str]:
    template_code = _normalize_text(getattr(doc_template, "code", None))
    if not template_code:
        raise_business_error(
            "DOCUMENT_TEMPLATE_SOURCE_NOT_FOUND",
            "Doc template code is required to resolve template source",
            status_code=409,
        )

    matches = (
        db.execute(
            select(Template).where(
                Template.group == "DOC_TEMPLATE",
                Template.name == template_code,
                Template.enabled.is_(True),
            )
        )
        .scalars()
        .all()
    )

    if not matches:
        raise_business_error(
            "DOCUMENT_TEMPLATE_SOURCE_NOT_FOUND",
            "Document template source mapping not found",
            details={"doc_template_code": template_code},
            status_code=409,
        )

    if len(matches) > 1:
        raise_business_error(
            "DOCUMENT_TEMPLATE_SOURCE_CONFLICT",
            "Multiple document template sources match the same doc template",
            details={"doc_template_code": template_code, "match_count": len(matches)},
            status_code=409,
        )

    template = matches[0]
    return template, _resolve_document_template_file_path(template.file_path)


def preview_document_wizard_fee_candidates(
    db: Session,
    data: DocumentWizardFeePreviewIn,
) -> list[dict[str, object]]:
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == data.defaults.doc_template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)

    _validate_document_wizard_rows(db, data.rows)

    fee_draft_type = _normalize_text(getattr(template, "fee_draft_type", None))
    if not fee_draft_type:
        return []

    semantics = resolve_document_semantics(template)
    if (
        semantics.catalog_status == "EXECUTABLE"
        and semantics.execution_behavior == "APPLICATION_FEE_NOTICE"
    ):
        return []

    case_ids = [_normalize_text(row.case_id) for row in data.rows]
    cases = db.execute(select(Case).where(Case.id.in_(case_ids))).scalars().all()
    case_by_id = {case.id: case for case in cases}
    fee_items = parse_fee_item_list_candidates(
        getattr(template, "fee_item_list", None), template.code
    )
    preview_rows: list[dict[str, object]] = []

    for idx, row in enumerate(data.rows, start=1):
        payload = _build_document_wizard_payload(data.defaults, row, template)
        case = case_by_id[payload.case_id]
        preview_rows.append(
            {
                "row_index": idx,
                "case_id": case.id,
                "case_no": case.case_no,
                "source_title": _resolve_case_title(case),
                "document_title": payload.title,
                "fee_draft_type": fee_draft_type,
                "fee_items": fee_items,
                "skip_this_candidate": False,
            }
        )

    return preview_rows


def preview_document_wizard_attachment_candidates(
    db: Session,
    data: DocumentWizardAttachmentPreviewIn,
) -> list[dict[str, object]]:
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == data.defaults.doc_template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)

    if not template.enabled:
        return []

    if _normalize_text(getattr(template, "direction", None)) != data.defaults.direction.value:
        return []

    _validate_document_wizard_rows(db, data.rows)

    case_ids = [_normalize_text(row.case_id) for row in data.rows]
    cases = db.execute(select(Case).where(Case.id.in_(case_ids))).scalars().all()
    case_by_id = {case.id: case for case in cases}
    preview_rows: list[dict[str, object]] = []

    for idx, row in enumerate(data.rows, start=1):
        payload = _build_document_wizard_payload(data.defaults, row, template)
        case = case_by_id[payload.case_id]
        output_name = _normalize_text(payload.title) or template.name or payload.case_id
        preview_rows.append(
            {
                "row_index": idx,
                "case_id": case.id,
                "case_no": case.case_no,
                "source_title": _resolve_case_title(case),
                "document_title": payload.title,
                "template_code": template.code,
                "template_name": template.name,
                "output_name": output_name,
                "output_file_name": f"{_sanitize_filename_component(output_name)}.docx",
                "output_format": "DOCX",
                "candidate_source_kind": "DOC_TEMPLATE",
                "generate_this_candidate": True,
                "remark": None,
            }
        )

    return preview_rows


def _group_document_wizard_task_rows(
    task_rows: list[DocumentWizardTaskFinalRowIn],
    *,
    row_count: int,
) -> dict[int, list[DocumentWizardTaskFinalRowIn]]:
    row_errors: list[dict[str, object]] = []
    grouped: dict[int, list[DocumentWizardTaskFinalRowIn]] = {}
    seen_keys: set[tuple[int, str]] = set()

    for idx, task_row in enumerate(task_rows, start=1):
        if task_row.row_index < 1 or task_row.row_index > row_count:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "row_index",
                    "code": "ROW_INDEX_OUT_OF_RANGE",
                    "message": "Task row row_index is out of range",
                    "value": task_row.row_index,
                }
            )
            continue

        template_code = _normalize_text(task_row.task_template_code)
        if not template_code:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "task_template_code",
                    "code": "TASK_TEMPLATE_CODE_REQUIRED",
                    "message": "task_template_code is required",
                }
            )
            continue

        key = (task_row.row_index, template_code.lower())
        if key in seen_keys:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "task_template_code",
                    "code": "DUPLICATE_TASK_TEMPLATE_CODE",
                    "message": "Duplicate task_template_code for the same row",
                    "task_template_code": template_code,
                }
            )
            continue

        seen_keys.add(key)
        grouped.setdefault(task_row.row_index, []).append(task_row)

    if row_errors:
        raise_business_error(
            "DOCUMENT_WIZARD_BATCH_INVALID",
            "Document wizard batch contains invalid task rows",
            details={"row_errors": row_errors},
            status_code=400,
        )

    return grouped


def _group_document_wizard_fee_rows(
    fee_rows: list[DocumentWizardFeeFinalRowIn],
    *,
    row_count: int,
) -> dict[int, DocumentWizardFeeFinalRowIn]:
    row_errors: list[dict[str, object]] = []
    grouped: dict[int, DocumentWizardFeeFinalRowIn] = {}
    seen_row_indices: set[int] = set()

    for idx, fee_row in enumerate(fee_rows, start=1):
        if fee_row.row_index < 1 or fee_row.row_index > row_count:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "row_index",
                    "code": "ROW_INDEX_OUT_OF_RANGE",
                    "message": "Fee row row_index is out of range",
                    "value": fee_row.row_index,
                }
            )
            continue

        if fee_row.row_index in seen_row_indices:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "row_index",
                    "code": "DUPLICATE_ROW_INDEX",
                    "message": "Duplicate fee row_index",
                    "value": fee_row.row_index,
                }
            )
            continue

        if not _normalize_text(fee_row.case_id):
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "case_id",
                    "code": "CASE_ID_REQUIRED",
                    "message": "case_id is required",
                }
            )
            continue

        if not _normalize_text(fee_row.fee_draft_type):
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "fee_draft_type",
                    "code": "FEE_DRAFT_TYPE_REQUIRED",
                    "message": "fee_draft_type is required",
                }
            )
            continue

        seen_row_indices.add(fee_row.row_index)
        grouped[fee_row.row_index] = fee_row

    if row_errors:
        raise_business_error(
            "DOCUMENT_WIZARD_BATCH_INVALID",
            "Document wizard batch contains invalid fee rows",
            details={"row_errors": row_errors},
            status_code=400,
        )

    return grouped


def _group_document_wizard_attachment_rows(
    attachment_rows: list[DocumentWizardAttachmentFinalRowIn],
    *,
    row_count: int,
) -> dict[int, list[DocumentWizardAttachmentFinalRowIn]]:
    row_errors: list[dict[str, object]] = []
    grouped: dict[int, list[DocumentWizardAttachmentFinalRowIn]] = {}
    seen_keys: set[tuple[int, str, str]] = set()

    for idx, attachment_row in enumerate(attachment_rows, start=1):
        if attachment_row.row_index < 1 or attachment_row.row_index > row_count:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "row_index",
                    "code": "ROW_INDEX_OUT_OF_RANGE",
                    "message": "Attachment row row_index is out of range",
                    "value": attachment_row.row_index,
                }
            )
            continue

        template_code = _normalize_text(attachment_row.template_code)
        if not template_code:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "template_code",
                    "code": "TEMPLATE_CODE_REQUIRED",
                    "message": "template_code is required",
                }
            )
            continue

        output_file_name = Path(_normalize_text(attachment_row.output_file_name) or "").name
        if not output_file_name:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "output_file_name",
                    "code": "OUTPUT_FILE_NAME_REQUIRED",
                    "message": "output_file_name is required",
                }
            )
            continue

        key = (attachment_row.row_index, template_code.lower(), output_file_name.lower())
        if key in seen_keys:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "output_file_name",
                    "code": "DUPLICATE_ATTACHMENT_OUTPUT",
                    "message": "Duplicate attachment output for the same row",
                    "output_file_name": output_file_name,
                }
            )
            continue

        seen_keys.add(key)
        grouped.setdefault(attachment_row.row_index, []).append(attachment_row)

    if row_errors:
        raise_business_error(
            "DOCUMENT_WIZARD_BATCH_INVALID",
            "Document wizard batch contains invalid attachment rows",
            details={"row_errors": row_errors},
            status_code=400,
        )

    return grouped


def _create_document_wizard_tasks_from_rows(
    db: Session,
    *,
    document: Document,
    row_task_rows: list[DocumentWizardTaskFinalRowIn],
) -> None:
    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    task_service = TaskGenerationService()
    preview_document = SimpleNamespace(
        id=document.id,
        case_id=document.case_id,
        doc_date=document.doc_date,
        direction=getattr(document.direction, "value", document.direction),
        doc_template_id=document.doc_template_id,
        extra_data=document.extra_data,
        title=document.title,
        case=case,
    )

    explicit_rows_by_code: dict[str, DocumentWizardTaskFinalRowIn] = {}
    for task_row in row_task_rows:
        template_code = _normalize_text(task_row.task_template_code)
        if not template_code:
            raise_business_error(
                "DOCUMENT_WIZARD_BATCH_INVALID",
                "Document wizard batch contains invalid task rows",
                details={
                    "row_errors": [
                        {
                            "row_index": task_row.row_index,
                            "field": "task_template_code",
                            "code": "TASK_TEMPLATE_CODE_REQUIRED",
                            "message": "task_template_code is required",
                        }
                    ]
                },
                status_code=400,
            )
        if _normalize_text(task_row.case_id) != document.case_id:
            raise_business_error(
                "DOCUMENT_WIZARD_BATCH_INVALID",
                "Document wizard batch contains invalid task rows",
                details={
                    "row_errors": [
                        {
                            "row_index": task_row.row_index,
                            "field": "case_id",
                            "code": "CASE_ID_MISMATCH",
                            "message": "Task row case_id does not match document row case_id",
                            "case_id": task_row.case_id,
                            "document_case_id": document.case_id,
                        }
                    ]
                },
                status_code=400,
            )
        explicit_rows_by_code[template_code.lower()] = task_row

    available_templates = _list_task_templates_for_preview(db, task_service, preview_document)
    available_templates_by_code = {
        template.code.lower(): template for template in available_templates
    }

    for template_code_lower, task_row in explicit_rows_by_code.items():
        template = available_templates_by_code.get(template_code_lower)
        if not template:
            raise_business_error(
                "TASK_TEMPLATE_NOT_FOUND",
                "Task template not found",
                status_code=404,
            )
        if getattr(template, "enabled", True) is False:
            raise_business_error(
                "TASK_TEMPLATE_DISABLED",
                "Task template disabled",
                status_code=400,
            )

        due_date = task_row.due_date or task_service._compute_due_date(
            preview_document, case, template
        )
        base_date = task_row.base_date or getattr(document, "doc_date", None)
        title = task_row.title or template.name or template.code

        effective_internal_due_date = task_row.internal_due_date
        if (
            effective_internal_due_date is None
            and getattr(template, "inner_offset_days", None) is not None
        ):
            effective_internal_due_date = due_date - timedelta(
                days=getattr(template, "inner_offset_days", 0) or 0
            )

        remind1, remind2, remind3, daily_remind_from = task_service._compute_reminders(
            due_date,
            effective_internal_due_date,
            template,
        )

        task = Task(
            id=str(uuid4()),
            case_id=document.case_id,
            document_id=document.id,
            task_template_id=template.id,
            title=title,
            base_date=base_date,
            due_date=due_date,
            internal_due_date=effective_internal_due_date,
            remind1=task_row.remind1 or remind1,
            remind2=task_row.remind2 or remind2,
            remind3=task_row.remind3 or remind3,
            daily_remind_from=task_row.daily_remind_from or daily_remind_from,
            daily_remind=task_row.daily_remind
            if task_row.daily_remind is not None
            else bool(getattr(template, "daily_remind", False)),
            status=TaskStatus.OPEN.value,
        )
        db.add(task)
        _create_task_log(
            db,
            task_id=task.id,
            action=TaskAction.AUTO_CREATE_FROM_DOCUMENT,
            from_status=None,
            to_status=TaskStatus.OPEN.value,
            remark=None,
        )


def batch_register_document_mailing(
    db: Session,
    data: DocumentMailingBatchIn,
    *,
    user_id: str,
) -> list[Document]:
    if not data.selected_document_ids:
        raise_business_error(
            "DOCUMENT_MAILING_SELECTION_REQUIRED",
            "selected_document_ids must not be empty",
            status_code=400,
        )

    outgoing_reg_no = _normalize_text(data.outgoing_reg_no)
    if not outgoing_reg_no:
        raise_business_error(
            "DOCUMENT_MAILING_OUTGOING_REG_NO_REQUIRED",
            "outgoing_reg_no is required",
            status_code=400,
        )

    unique_document_ids = list(dict.fromkeys(data.selected_document_ids))
    documents = db.query(Document).filter(Document.id.in_(unique_document_ids)).all()
    document_by_id = {document.id: document for document in documents}
    missing_document_ids = [
        document_id for document_id in unique_document_ids if document_id not in document_by_id
    ]
    if missing_document_ids:
        raise_business_error(
            "DOCUMENT_MAILING_DOCUMENT_NOT_FOUND",
            "One or more selected documents do not exist",
            details={"document_ids": missing_document_ids},
            status_code=404,
        )

    invalid_direction_document_ids = [
        document.id for document in documents if document.direction != DocumentDirection.OUT.value
    ]
    if invalid_direction_document_ids:
        raise_business_error(
            "DOCUMENT_MAILING_DIRECTION_INVALID",
            "Only OUT documents can be batch registered for mailing",
            details={"document_ids": invalid_direction_document_ids},
            status_code=400,
        )

    update_forward_date = "forward_date" in data.model_fields_set
    for document in documents:
        document.outgoing_reg_no = outgoing_reg_no
        if update_forward_date:
            document.forward_date = data.forward_date
        document.updated_by = user_id

    db.commit()
    for document in documents:
        db.refresh(document)
    return documents


def create_document_dispatch(
    db: Session,
    data: DocumentDispatchCreateIn,
    *,
    user_id: str,
) -> DocDispatch:
    selected_document_ids = list(dict.fromkeys(data.selected_document_ids))
    if not selected_document_ids:
        raise_business_error(
            "DOCUMENT_DISPATCH_SELECTION_REQUIRED",
            "selected_document_ids must not be empty",
            status_code=400,
        )

    client_id = _normalize_text(data.client_id)
    if not client_id:
        raise_business_error(
            "DOCUMENT_DISPATCH_CLIENT_REQUIRED",
            "client_id is required",
            status_code=400,
        )

    documents = (
        db.execute(
            select(Document)
            .where(Document.id.in_(selected_document_ids))
            .order_by(Document.created_at)
        )
        .scalars()
        .all()
    )
    document_by_id = {document.id: document for document in documents}
    missing_document_ids = [
        document_id for document_id in selected_document_ids if document_id not in document_by_id
    ]
    if missing_document_ids:
        raise_business_error(
            "DOCUMENT_DISPATCH_DOCUMENT_NOT_FOUND",
            "One or more selected documents do not exist",
            details={"document_ids": missing_document_ids},
            status_code=404,
        )

    invalid_direction_document_ids = [
        document.id for document in documents if document.direction != DocumentDirection.OUT.value
    ]
    if invalid_direction_document_ids:
        raise_business_error(
            "DOCUMENT_DISPATCH_DIRECTION_INVALID",
            "Only OUT documents can be included in a dispatch sheet",
            details={"document_ids": invalid_direction_document_ids},
            status_code=400,
        )

    case_ids = {document.case_id for document in documents if document.case_id}
    cases = (
        db.execute(select(Case).where(Case.id.in_(case_ids))).scalars().all() if case_ids else []
    )
    case_by_id = {case.id: case for case in cases}
    invalid_case_ids = [
        document.case_id
        for document in documents
        if not document.case_id or case_by_id.get(document.case_id) is None
    ]
    if invalid_case_ids:
        raise_business_error(
            "DOCUMENT_DISPATCH_CASE_NOT_FOUND",
            "One or more selected documents do not have a valid case",
            details={"case_ids": invalid_case_ids},
            status_code=404,
        )

    case_client_ids = {
        case.client_id for case in cases if case.client_id and case.client_id == client_id
    }
    if len(case_client_ids) != 1 or any(case.client_id != client_id for case in cases):
        raise_business_error(
            "DOCUMENT_DISPATCH_CLIENT_MISMATCH",
            "Selected documents must belong to the specified client",
            details={"client_id": client_id},
            status_code=400,
        )

    dispatch = DocDispatch(
        id=str(uuid4()),
        client_id=client_id,
        dispatch_date=data.dispatch_date,
        remark=_normalize_text(data.remark),
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(dispatch)
    db.flush()

    for document in documents:
        line = DocDispatchLine(
            id=str(uuid4()),
            dispatch_id=dispatch.id,
            document_id=document.id,
            case_id=document.case_id,
            doc_name=_normalize_text(document.title) or document.ref_no or "Untitled Document",
            outgoing_reg_no=document.outgoing_reg_no,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(line)

    db.commit()
    dispatch = db.execute(
        select(DocDispatch)
        .where(DocDispatch.id == dispatch.id)
        .options(
            selectinload(DocDispatch.lines)
            .selectinload(DocDispatchLine.document)
            .selectinload(Document.case)
        )
    ).scalar_one()
    return dispatch


def get_document_dispatch(db: Session, dispatch_id: str) -> DocDispatch:
    dispatch = db.execute(
        select(DocDispatch)
        .where(DocDispatch.id == dispatch_id)
        .options(
            selectinload(DocDispatch.lines)
            .selectinload(DocDispatchLine.document)
            .selectinload(Document.case)
        )
    ).scalar_one_or_none()
    if not dispatch:
        raise_business_error(
            "DOCUMENT_DISPATCH_NOT_FOUND", "Document dispatch not found", status_code=404
        )
    return dispatch


def get_document_envelope_preview(
    db: Session,
    *,
    document_id: str,
) -> DocumentEnvelopePreviewOut:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("DOCUMENT_CASE_NOT_FOUND", "Case not found", status_code=404)

    return _resolve_envelope_preview(db, document=document, case=case)


def _build_document_wizard_payload(
    defaults,
    row: DocumentWizardBatchRowIn,
    template: DocTemplate,
) -> DocumentCreateIn:
    data = defaults.model_dump(exclude_unset=True)
    row_data = row.model_dump(exclude_unset=True)
    data.update(row_data)
    data["case_id"] = _normalize_text(row.case_id)
    data["doc_template_id"] = defaults.doc_template_id
    data["direction"] = defaults.direction

    if data.get("doc_date") is None:
        data["doc_date"] = defaults.doc_date

    data["title"] = _normalize_text(data.get("title")) or template.name
    data["ref_no"] = _normalize_text(data.get("ref_no"))
    data["extra_data"] = _normalize_text(data.get("extra_data"))
    data["reply_to_id"] = _normalize_text(data.get("reply_to_id"))

    return DocumentCreateIn(**data)


def _sanitize_filename_component(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        return "attachment"
    return normalized.replace("/", "_").replace("\\", "_")


def _validate_document_wizard_rows(db: Session, rows: list[DocumentWizardBatchRowIn]) -> None:
    row_errors: list[dict[str, object]] = []
    seen_case_ids: set[str] = set()
    case_ids: list[str] = []

    for idx, row in enumerate(rows, start=1):
        case_id = _normalize_text(row.case_id)
        if not case_id:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "case_id",
                    "code": "CASE_ID_REQUIRED",
                    "message": "Case ID is required",
                }
            )
            continue
        if case_id in seen_case_ids:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "case_id",
                    "code": "CASE_ID_DUPLICATE",
                    "message": "Case ID must be unique within the batch",
                }
            )
            continue
        seen_case_ids.add(case_id)
        case_ids.append(case_id)

    existing_case_ids = set(
        db.execute(select(Case.id).where(Case.id.in_(case_ids))).scalars().all()
    )
    for idx, row in enumerate(rows, start=1):
        case_id = _normalize_text(row.case_id)
        if case_id and case_id not in existing_case_ids:
            row_errors.append(
                {
                    "row_index": idx,
                    "field": "case_id",
                    "code": "CASE_NOT_FOUND",
                    "message": "Case not found",
                    "case_id": case_id,
                }
            )

    if row_errors:
        raise_business_error(
            "DOCUMENT_WIZARD_BATCH_INVALID",
            "Document wizard batch contains invalid rows",
            details={"row_errors": row_errors},
            status_code=400,
        )


def _list_task_templates_for_preview(
    db: Session,
    task_service: TaskGenerationService,
    preview_document,
) -> list[TaskTemplate]:
    if not task_service._is_incoming(preview_document):
        return []

    doc_type = task_service._get_document_type(db, preview_document)
    if not doc_type:
        return []

    return db.query(TaskTemplate).filter(TaskTemplate.code == doc_type).all()


def get_document(db: Session, document_id: str) -> Document:
    stmt = (
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.attachments))
    )
    document = db.execute(stmt).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)
    return document


@dataclass(frozen=True, slots=True)
class AttachmentEvidenceReadProjection:
    evidence_version_id: str
    role: EvidenceRole
    creator_id: str
    reviewer_id: str | None
    review_state: EvidenceReviewState
    is_current: bool
    is_final: bool


def _attachment_current_evidence_invalid() -> None:
    raise_business_error(
        "DOCUMENT_ATTACHMENT_CURRENT_EVIDENCE_INVALID",
        "当前附件证据版本数据无效",
        status_code=409,
    )


def _is_valid_evidence_identifier(value: object) -> bool:
    return type(value) is str and bool(value.strip()) and len(value) <= 36


def get_current_attachment_evidence_versions(
    db: Session,
    *,
    document: Document,
) -> dict[str, AttachmentEvidenceReadProjection]:
    attachment_ids = tuple(attachment.id for attachment in document.attachments)
    if not attachment_ids:
        return {}
    attachment_id_set = set(attachment_ids)

    versions = (
        db.execute(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.attachment_id.in_(attachment_ids),
                DocumentEvidenceVersion.current_identity_key.is_not(None),
            )
        )
        .scalars()
        .all()
    )
    by_attachment: dict[str, AttachmentEvidenceReadProjection] = {}
    for version in versions:
        if (
            not _is_valid_evidence_identifier(version.id)
            or version.document_id != document.id
            or version.case_id != document.case_id
            or version.attachment_id not in attachment_id_set
            or type(version.lineage_key) is not str
            or not version.lineage_key.strip()
            or len(version.lineage_key) > 128
            or version.current_identity_key != f"{document.case_id}|{version.lineage_key}"
            or version.attachment_id in by_attachment
            or not _is_valid_evidence_identifier(version.creator_id)
        ):
            _attachment_current_evidence_invalid()
        try:
            role = EvidenceRole(version.role)
            state = EvidenceVersionState(version.state)
            review_state = EvidenceReviewState(version.review_state)
        except (TypeError, ValueError):
            _attachment_current_evidence_invalid()
        if (
            role in {EvidenceRole.RAW_ATTACHMENT, EvidenceRole.GENERATED_ATTACHMENT}
            and state is not EvidenceVersionState.DRAFT
        ):
            _attachment_current_evidence_invalid()
        if review_state is EvidenceReviewState.PENDING:
            if version.reviewer_id is not None or version.reviewed_at is not None:
                _attachment_current_evidence_invalid()
        elif (
            not _is_valid_evidence_identifier(version.reviewer_id)
            or type(version.reviewed_at) is not datetime
            or version.reviewed_at.tzinfo is not None
            or version.reviewer_id == version.creator_id
        ):
            _attachment_current_evidence_invalid()
        by_attachment[version.attachment_id] = AttachmentEvidenceReadProjection(
            evidence_version_id=version.id,
            role=role,
            creator_id=version.creator_id,
            reviewer_id=version.reviewer_id,
            review_state=review_state,
            is_current=True,
            is_final=state is EvidenceVersionState.FINAL,
        )
    return by_attachment


def _pop_reply_task_controls(updates: dict[str, object]) -> tuple[str | None, dict[str, date]]:
    action = updates.pop("reply_task_action", None)
    task_updates: dict[str, date] = {}
    field_map = {
        "reply_task_due_date": "due_date",
        "reply_task_internal_due_date": "internal_due_date",
        "reply_task_remind1": "remind1",
        "reply_task_remind2": "remind2",
        "reply_task_remind3": "remind3",
    }
    for input_field, task_field in field_map.items():
        if input_field in updates:
            value = updates.pop(input_field)
            if value is not None:
                task_updates[task_field] = value
    return action, task_updates


def _get_open_reply_task(db: Session, *, document_id: str) -> Task:
    task = (
        db.execute(
            select(Task)
            .where(Task.document_id == document_id, Task.status == TaskStatus.OPEN.value)
            .order_by(Task.created_at.asc(), Task.id.asc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    if not task:
        raise_business_error(
            "DOCUMENT_REPLY_TASK_NOT_FOUND",
            "Open reply task not found",
            status_code=404,
        )
    return task


def _apply_reply_task_update_controls(
    db: Session,
    *,
    document: Document,
    action: str | None,
    task_updates: dict[str, date],
    need_reply_update: bool,
) -> None:
    requires_explicit_action = bool(task_updates) or need_reply_update
    if requires_explicit_action and action is None:
        raise_business_error(
            "DOCUMENT_REPLY_TASK_ACTION_REQUIRED",
            "reply_task_action is required when editing reply task side effects",
            status_code=400,
        )
    if action in (None, "NONE"):
        return

    task = _get_open_reply_task(db, document_id=document.id)
    if action == "CANCEL":
        from_status = task.status
        task.status = TaskStatus.CANCELLED.value
        task.done_at = datetime.utcnow()
        _create_task_log(
            db,
            task_id=task.id,
            action=TaskAction.CANCEL,
            from_status=from_status,
            to_status=TaskStatus.CANCELLED.value,
            remark=f"Document reply task cancelled from document edit {document.id}",
        )
        return

    if action == "UPDATE":
        for field, value in task_updates.items():
            setattr(task, field, value)
        _create_task_log(
            db,
            task_id=task.id,
            action=TaskAction.UPDATE,
            from_status=task.status,
            to_status=task.status,
            remark=f"Document reply task updated from document edit {document.id}",
        )


def _merge_document_update_extra_data(
    document: Document,
    updates: dict,
) -> date | None:
    structured_fields = (
        "official_due_date",
        "official_due_date_source",
        "official_due_date_status",
        "description",
    )
    structured_updates = {
        field: updates.pop(field) for field in structured_fields if field in updates
    }
    raw_was_updated = "extra_data" in updates
    if not structured_updates and not raw_was_updated:
        return None

    raw = updates.pop("extra_data", document.extra_data)
    deadline_was_updated = raw_was_updated or any(
        field in structured_updates
        for field in (
            "official_due_date",
            "official_due_date_source",
            "official_due_date_status",
        )
    )
    try:
        existing = parse_document_extra_data(document.extra_data)
        existing_deadline_fields = {
            "official_due_date": existing.official_due_date,
            "official_due_date_source": existing.official_due_date_source,
            "official_due_date_status": existing.official_due_date_status,
        }
        confirmed_structured_override = existing.official_due_date_status == "CONFIRMED" and any(
            field in structured_updates
            and structured_updates[field] != existing_deadline_fields[field]
            for field in existing_deadline_fields
        )
        if confirmed_structured_override:
            raise_business_error(
                "DOCUMENT_DEADLINE_OVERRIDE_REQUIRED",
                "A confirmed official due date cannot be changed by ordinary edit",
                status_code=409,
            )
        merged = merge_document_extra_data(raw, **structured_updates) if structured_updates else raw
        proposed = parse_document_extra_data(merged)

        existing_identity = (
            existing.official_due_date,
            existing.official_due_date_source,
            existing.official_due_date_status,
        )
        proposed_identity = (
            proposed.official_due_date,
            proposed.official_due_date_source,
            proposed.official_due_date_status,
        )
        confirmed_override = (
            existing.official_due_date_status == "CONFIRMED"
            and proposed_identity != existing_identity
        )
        legacy_date_change = (
            existing.official_due_date_status == "LEGACY_UNVERIFIED"
            and deadline_was_updated
            and proposed.official_due_date != existing.official_due_date
        )
        if confirmed_override or legacy_date_change:
            raise_business_error(
                "DOCUMENT_DEADLINE_OVERRIDE_REQUIRED",
                "A confirmed or legacy official due date cannot be changed by ordinary edit",
                status_code=409,
            )
        if deadline_was_updated and proposed.official_due_date_status == "LEGACY_UNVERIFIED":
            raise DocumentExtraDataBusinessError(
                "OfficialDueDate",
                "writes require date, source, and write status together",
            )
        updates["extra_data"] = merged
        if (
            deadline_was_updated
            and existing.official_due_date_status in (None, "LEGACY_UNVERIFIED")
            and proposed.official_due_date_status == "CONFIRMED"
        ):
            return proposed.official_due_date
        return None
    except DocumentExtraDataShapeError as exc:
        raise_business_error(
            "DOCUMENT_EXTRA_DATA_INVALID",
            "Document extra data has an invalid shape",
            details={"field": exc.field, "reason": exc.reason},
            status_code=422,
        )
    except DocumentExtraDataBusinessError as exc:
        raise_business_error(
            "DOCUMENT_DEADLINE_INVALID",
            "Document deadline fields are incomplete or inconsistent",
            details={"field": exc.field, "reason": exc.reason},
            status_code=400,
        )


def update_document(db: Session, document_id: str, data: DocumentUpdateIn) -> Document:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    updates = data.model_dump(exclude_unset=True)
    reply_task_action, reply_task_updates = _pop_reply_task_controls(updates)
    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    template = None

    if "case_id" in updates:
        case = db.execute(select(Case).where(Case.id == updates["case_id"])).scalar_one_or_none()
        if not case:
            raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    if "doc_template_id" in updates and updates["doc_template_id"] is not None:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == updates["doc_template_id"])
        ).scalar_one_or_none()
        if not template:
            raise_business_error(
                "DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404
            )
    elif document.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
        ).scalar_one_or_none()

    confirmed_legacy_due_date = _merge_document_update_extra_data(document, updates)
    if confirmed_legacy_due_date is not None and template is not None:
        semantics = resolve_document_semantics(template)
        if semantics.execution_behavior == "OA_REPLY" and semantics.task_template_code:
            TaskGenerationService().synchronize_confirmed_oa_deadline(
                db,
                document=document,
                case_id=case.id,
                task_template_code=semantics.task_template_code,
                due_date=confirmed_legacy_due_date,
            )
    for field, value in updates.items():
        setattr(document, field, value)

    _apply_reply_task_update_controls(
        db,
        document=document,
        action=reply_task_action,
        task_updates=reply_task_updates,
        need_reply_update=("need_reply" in updates and updates["need_reply"] is False),
    )

    _apply_template_defaults(
        case=case,
        document=document,
        template=template,
        need_reply_overridden="need_reply" in updates,
    )
    if "reply_to_id" in updates or (
        "doc_template_id" in updates and getattr(template, "status_restore", None)
    ):
        _apply_reply_chain(
            db,
            document=document,
            doc_date=document.doc_date,
            template=template,
        )

    db.commit()
    db.refresh(document)
    return document


@dataclass(frozen=True, slots=True)
class PendingAttachmentEvidenceUpload:
    attachment: DocAttachment
    evidence_version: EvidenceVersionResult
    managed_file_path: Path


def _remove_managed_attachment_file(
    managed_file_path: Path,
    *,
    original_error: Exception,
) -> None:
    try:
        managed_file_path.unlink()
    except FileNotFoundError:
        return
    except Exception as cleanup_error:
        logger.error(
            "Attachment compensation failed; residual_path=%s; original_error=%r",
            managed_file_path,
            original_error,
            exc_info=(
                type(original_error),
                original_error,
                original_error.__traceback__,
            ),
        )
        raise BusinessError(
            "ATTACHMENT_STORAGE_COMPENSATION_FAILED",
            "Attachment storage compensation failed",
            status_code=500,
        ) from cleanup_error


def add_attachment(
    db: Session,
    document_id: str,
    upload_file,
    storage_dir: str,
    actor_id: str | None = None,
    official_file_role: str | None = None,
    source_role_alias: str | None = None,
    external_upload_position: str | None = None,
    package_usage_hint: str | None = None,
    is_archive_evidence: bool | None = None,
    is_receipt_evidence: bool | None = None,
) -> PendingAttachmentEvidenceUpload:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    creator_id = (actor_id or "").strip()
    if not creator_id:
        raise_business_error(
            "ATTACHMENT_ACTOR_REQUIRED",
            "Authenticated attachment creator is required",
            status_code=400,
        )

    original_name = (upload_file.filename or "").strip()
    if not original_name:
        raise_business_error(
            "ATTACHMENT_FILENAME_REQUIRED",
            "Attachment filename is required",
            status_code=400,
        )

    content_type = upload_file.content_type or "application/octet-stream"
    manifest_metadata = _resolve_attachment_manifest_metadata(
        official_file_role=official_file_role,
        source_role_alias=source_role_alias,
        external_upload_position=external_upload_position,
        package_usage_hint=package_usage_hint,
        is_archive_evidence=is_archive_evidence,
        is_receipt_evidence=is_receipt_evidence,
    )
    _validate_attachment_file_rule(
        official_file_role=manifest_metadata["official_file_role"],
        file_name=original_name,
        content_type=content_type,
    )

    max_size_bytes = 25 * 1024 * 1024
    stored_name = f"{uuid4().hex}_{Path(original_name).name}"
    relative_path = f"attachments/{document_id}/{stored_name}"
    managed_file_path = Path(safe_join(storage_dir, relative_path))

    size_bytes = 0
    content_hasher = sha256()
    try:
        ensure_dir(str(managed_file_path.parent))
        with open(managed_file_path, "wb") as f:
            while True:
                chunk = upload_file.file.read(1024 * 1024)
                if not chunk:
                    break
                size_bytes += len(chunk)
                if size_bytes > max_size_bytes:
                    raise_business_error(
                        "ATTACHMENT_TOO_LARGE",
                        "Attachment exceeds size limit",
                        status_code=400,
                    )
                content_hasher.update(chunk)
                f.write(chunk)
    except Exception as exc:
        _remove_managed_attachment_file(managed_file_path, original_error=exc)
        if isinstance(exc, BusinessError):
            raise
        raise_business_error(
            "ATTACHMENT_STORAGE_WRITE_FAILED",
            "Attachment storage write failed",
            status_code=500,
        )

    try:
        attachment = DocAttachment(
            id=str(uuid4()),
            document_id=document_id,
            file_name=original_name,
            file_path=relative_path,
            mime_type=content_type,
            file_size=size_bytes,
            official_file_role=manifest_metadata["official_file_role"],
            source_role_alias=manifest_metadata["source_role_alias"],
            external_upload_position=manifest_metadata["external_upload_position"],
            content_hash=f"sha256:{content_hasher.hexdigest()}",
            package_usage_hint=manifest_metadata["package_usage_hint"],
            is_archive_evidence=bool(manifest_metadata["is_archive_evidence"]),
            is_receipt_evidence=bool(manifest_metadata["is_receipt_evidence"]),
        )
        db.add(attachment)
        db.flush()
        final_official_roles = {
            "FILING_MERGED_PDF",
            "OFFICIAL_NOTICE_PDF",
        }
        evidence_role = (
            EvidenceRole.OFFICIAL_FINAL_PDF
            if official_file_role in final_official_roles
            else EvidenceRole.FILING_FULL_WORD
            if official_file_role == EvidenceRole.FILING_FULL_WORD.value
            else EvidenceRole.RAW_ATTACHMENT
        )
        evidence_state = (
            EvidenceVersionState.FINAL
            if evidence_role is EvidenceRole.OFFICIAL_FINAL_PDF
            else EvidenceVersionState.DRAFT
        )
        evidence_version = register_evidence_version(
            RegisterEvidenceVersionCommand(
                case_id=document.case_id,
                document_id=document_id,
                attachment_id=attachment.id,
                lineage_key=f"attachment:{attachment.id}",
                role=evidence_role,
                state=evidence_state,
                creator_id=creator_id,
                content_hash=attachment.content_hash,
            ),
            db,
        )
        _append_certificate_archived_activity(
            db,
            document=document,
            evidence_version=evidence_version,
        )
        _advance_grant_notice_case_after_attachment(db, document=document)
        db.flush()
        return PendingAttachmentEvidenceUpload(
            attachment=attachment,
            evidence_version=evidence_version,
            managed_file_path=managed_file_path,
        )
    except Exception as exc:
        _remove_managed_attachment_file(managed_file_path, original_error=exc)
        if isinstance(exc, BusinessError):
            raise
        raise_business_error(
            "ATTACHMENT_PERSIST_FAILED",
            "Attachment persistence failed",
            status_code=500,
        )


def persist_generated_attachment(
    db: Session,
    *,
    document_id: str,
    file_name: str,
    content_bytes: bytes,
    storage_dir: str,
    mime_type: str | None = None,
    commit: bool = True,
    official_file_role: str | None = None,
    source_role_alias: str | None = None,
    external_upload_position: str | None = None,
    package_usage_hint: str | None = None,
    is_archive_evidence: bool | None = None,
    is_receipt_evidence: bool | None = None,
    actor_id: str | None = None,
    template_id: str | None = None,
    template_code: str | None = None,
) -> DocAttachment:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    provenance_values = (actor_id, template_id, template_code)
    register_generated_evidence = any(value is not None for value in provenance_values)
    if register_generated_evidence and any(
        not isinstance(value, str) or not value.strip() for value in provenance_values
    ):
        raise_business_error(
            "GENERATED_ATTACHMENT_PROVENANCE_REQUIRED",
            "Generated attachment provenance is required",
            status_code=400,
        )

    normalized_actor_id = actor_id.strip() if register_generated_evidence else None
    normalized_template_id = template_id.strip() if register_generated_evidence else None
    normalized_template_code = template_code.strip() if register_generated_evidence else None
    if register_generated_evidence:
        doc_template = db.execute(
            select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
        ).scalar_one_or_none()
        if doc_template is None or _normalize_text(doc_template.code) != normalized_template_code:
            raise_business_error(
                "GENERATED_ATTACHMENT_TEMPLATE_MISMATCH",
                "Generated attachment template identity does not match the document",
                status_code=409,
            )
        resolved_template, _template_path = resolve_document_template_render_source(
            db,
            doc_template=doc_template,
        )
        if resolved_template.id != normalized_template_id:
            raise_business_error(
                "GENERATED_ATTACHMENT_TEMPLATE_MISMATCH",
                "Generated attachment template source identity does not match",
                status_code=409,
            )

    normalized_name = Path(_normalize_text(file_name) or "").name
    if not normalized_name:
        raise_business_error(
            "ATTACHMENT_FILENAME_REQUIRED",
            "Attachment filename is required",
            status_code=400,
        )

    stored_name = f"{uuid4().hex}_{normalized_name}"
    relative_path = f"attachments/{document_id}/{stored_name}"
    managed_file_path = Path(safe_join(storage_dir, relative_path))
    try:
        ensure_dir(str(managed_file_path.parent))
        with open(managed_file_path, "wb") as output_file:
            output_file.write(content_bytes)
    except Exception as exc:
        _remove_managed_attachment_file(managed_file_path, original_error=exc)
        raise_business_error(
            "ATTACHMENT_STORAGE_WRITE_FAILED",
            "Attachment storage write failed",
            status_code=500,
        )

    try:
        manifest_metadata = _resolve_attachment_manifest_metadata(
            official_file_role=official_file_role,
            source_role_alias=source_role_alias,
            external_upload_position=external_upload_position,
            package_usage_hint=package_usage_hint,
            is_archive_evidence=is_archive_evidence,
            is_receipt_evidence=is_receipt_evidence,
        )
        attachment = DocAttachment(
            id=str(uuid4()),
            document_id=document_id,
            file_name=normalized_name,
            file_path=relative_path,
            mime_type=mime_type or "application/octet-stream",
            file_size=len(content_bytes),
            official_file_role=manifest_metadata["official_file_role"],
            source_role_alias=manifest_metadata["source_role_alias"],
            external_upload_position=manifest_metadata["external_upload_position"],
            content_hash=f"sha256:{sha256(content_bytes).hexdigest()}",
            package_usage_hint=manifest_metadata["package_usage_hint"],
            is_archive_evidence=bool(manifest_metadata["is_archive_evidence"]),
            is_receipt_evidence=bool(manifest_metadata["is_receipt_evidence"]),
        )
        db.add(attachment)
        db.flush()
        if register_generated_evidence:
            template_code_hash = sha256(normalized_template_code.encode()).hexdigest()[:16]
            register_evidence_version(
                RegisterEvidenceVersionCommand(
                    case_id=document.case_id,
                    document_id=document_id,
                    attachment_id=attachment.id,
                    lineage_key=(
                        f"generated:{normalized_template_id}:{template_code_hash}:{attachment.id}"
                    ),
                    role=EvidenceRole.GENERATED_ATTACHMENT,
                    state=EvidenceVersionState.DRAFT,
                    creator_id=normalized_actor_id,
                    content_hash=attachment.content_hash,
                ),
                db,
            )
            db.flush()
        if commit:
            db.commit()
            db.refresh(attachment)
        return attachment
    except Exception as exc:
        if commit:
            db.rollback()
        _remove_managed_attachment_file(managed_file_path, original_error=exc)
        if isinstance(exc, BusinessError):
            raise
        raise_business_error(
            "ATTACHMENT_PERSIST_FAILED",
            "Attachment persistence failed",
            status_code=500,
        )


def build_document_template_render_context(
    db: Session,
    *,
    document: Document,
) -> dict[str, object]:
    case = db.execute(select(Case).where(Case.id == document.case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)

    client = None
    if case.client_id:
        client = db.execute(select(Client).where(Client.id == case.client_id)).scalar_one_or_none()

    template_code = None
    if document.doc_template_id:
        template = db.execute(
            select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
        ).scalar_one_or_none()
        template_code = getattr(template, "code", None) if template else None

    case_title = _normalize_text(case.title_cn) or _normalize_text(case.title_en)
    client_name_cn = _normalize_text(getattr(client, "name_cn", None)) if client else None
    client_name_en = _normalize_text(getattr(client, "name_en", None)) if client else None
    client_name = client_name_cn or client_name_en
    document_direction = getattr(document.direction, "value", document.direction)

    return {
        "document_id": document.id,
        "document_title": document.title,
        "document_direction": document_direction,
        "document_date": document.doc_date.isoformat() if document.doc_date else None,
        "document_ref_no": document.ref_no,
        "document_extra_data": document.extra_data,
        "template_code": template_code,
        "case": {
            "id": case.id,
            "case_no": case.case_no,
            "title": case_title,
            "title_cn": case.title_cn,
            "title_en": case.title_en,
            "app_no": case.app_no,
        },
        "client": {
            "id": getattr(client, "id", None),
            "name": client_name,
            "name_cn": client_name_cn,
            "name_en": client_name_en,
        },
        "document": {
            "id": document.id,
            "title": document.title,
            "direction": document_direction,
            "doc_date": document.doc_date.isoformat() if document.doc_date else None,
            "ref_no": document.ref_no,
            "extra_data": document.extra_data,
            "template_code": template_code,
        },
    }


def _create_document_wizard_attachments_from_rows(
    db: Session,
    *,
    document: Document,
    doc_template: DocTemplate,
    row_attachment_rows: list[DocumentWizardAttachmentFinalRowIn],
    actor_id: str | None = None,
) -> list[Path]:
    resolved_template, template_path = resolve_document_template_render_source(
        db, doc_template=doc_template
    )
    renderer = TemplateRenderer()
    base_context = build_document_template_render_context(db, document=document)
    managed_generated_files: list[Path] = []

    for attachment_row in row_attachment_rows:
        if _normalize_text(attachment_row.case_id) != document.case_id:
            raise_business_error(
                "DOCUMENT_WIZARD_BATCH_INVALID",
                "Document wizard batch contains invalid attachment rows",
                details={
                    "row_errors": [
                        {
                            "row_index": attachment_row.row_index,
                            "field": "case_id",
                            "code": "CASE_ID_MISMATCH",
                            "message": "Attachment row case_id does not match document row case_id",
                            "case_id": attachment_row.case_id,
                            "document_case_id": document.case_id,
                        }
                    ]
                },
                status_code=400,
            )

        if _normalize_text(attachment_row.template_code) != _normalize_text(doc_template.code):
            raise_business_error(
                "DOCUMENT_WIZARD_BATCH_INVALID",
                "Document wizard batch contains invalid attachment rows",
                details={
                    "row_errors": [
                        {
                            "row_index": attachment_row.row_index,
                            "field": "template_code",
                            "code": "TEMPLATE_CODE_MISMATCH",
                            "message": "Attachment row template_code does not match batch doc template",
                            "template_code": attachment_row.template_code,
                            "expected_template_code": doc_template.code,
                        }
                    ]
                },
                status_code=400,
            )

        if _normalize_text(attachment_row.candidate_source_kind) != "DOC_TEMPLATE":
            raise_business_error(
                "DOCUMENT_WIZARD_BATCH_INVALID",
                "Document wizard batch contains invalid attachment rows",
                details={
                    "row_errors": [
                        {
                            "row_index": attachment_row.row_index,
                            "field": "candidate_source_kind",
                            "code": "UNSUPPORTED_ATTACHMENT_SOURCE",
                            "message": "Only DOC_TEMPLATE attachment rows are supported",
                            "candidate_source_kind": attachment_row.candidate_source_kind,
                        }
                    ]
                },
                status_code=400,
            )

        if _normalize_text(attachment_row.output_format).upper() != "DOCX":
            raise_business_error(
                "DOCUMENT_WIZARD_BATCH_INVALID",
                "Document wizard batch contains invalid attachment rows",
                details={
                    "row_errors": [
                        {
                            "row_index": attachment_row.row_index,
                            "field": "output_format",
                            "code": "UNSUPPORTED_ATTACHMENT_FORMAT",
                            "message": "Only DOCX attachment output is supported",
                            "output_format": attachment_row.output_format,
                        }
                    ]
                },
                status_code=400,
            )

        render_context = {
            **base_context,
            "attachment": {
                "template_id": resolved_template.id,
                "template_code": attachment_row.template_code,
                "output_name": attachment_row.output_name,
                "output_file_name": attachment_row.output_file_name,
                "remark": attachment_row.remark,
            },
        }
        try:
            rendered_bytes = renderer.render_template_docx_bytes(
                template_path=template_path,
                context=render_context,
            )
        except Exception as exc:
            raise_business_error(
                "DOCUMENT_TEMPLATE_RENDER_FAILED",
                "Document template render failed",
                details={
                    "document_id": document.id,
                    "template_code": attachment_row.template_code,
                    "output_file_name": attachment_row.output_file_name,
                    "error": str(exc),
                },
                status_code=409,
            )

        storage_dir = _backend_storage_dir()
        provenance: dict[str, str] = {}
        if actor_id is not None:
            provenance = {
                "actor_id": actor_id,
                "template_id": resolved_template.id,
                "template_code": attachment_row.template_code,
            }
        attachment = persist_generated_attachment(
            db,
            document_id=document.id,
            file_name=attachment_row.output_file_name,
            content_bytes=rendered_bytes,
            storage_dir=str(storage_dir),
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            commit=False,
            **provenance,
        )
        managed_generated_files.append(Path(safe_join(str(storage_dir), attachment.file_path)))
    return managed_generated_files


def get_attachment_download(
    db: Session,
    document_id: str,
    attachment_id: str,
    storage_dir: str,
) -> tuple[str, str, str]:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)

    attachment = db.execute(
        select(DocAttachment).where(
            DocAttachment.id == attachment_id,
            DocAttachment.document_id == document_id,
        )
    ).scalar_one_or_none()
    if not attachment:
        raise_business_error("ATTACHMENT_NOT_FOUND", "Attachment not found", status_code=404)

    abs_path = safe_join(storage_dir, attachment.file_path)
    if not Path(abs_path).exists():
        raise_business_error("ATTACHMENT_NOT_FOUND", "Attachment not found", status_code=404)

    mime_type = attachment.mime_type or "application/octet-stream"
    return (abs_path, attachment.file_name, mime_type)


# ---------------------------------------------------------------------------
# B1: DocTemplate CRUD
# ---------------------------------------------------------------------------


def list_doc_templates(
    db: Session,
    *,
    direction: DocumentDirection | None = None,
    enabled: bool | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DocTemplate], int]:
    """List doc templates with optional filters and pagination."""
    stmt = select(DocTemplate)

    if direction:
        stmt = stmt.where(DocTemplate.direction == direction)
    if enabled is not None:
        stmt = stmt.where(DocTemplate.enabled == enabled)
    if q:
        q_like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(DocTemplate.code).like(q_like),
                func.lower(DocTemplate.name).like(q_like),
                func.lower(DocTemplate.input_fields).like(q_like),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(DocTemplate.code.asc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total


def get_doc_template(db: Session, template_id: str) -> DocTemplate:
    """Get a single doc template by ID. Raises 404 if not found."""
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)
    return template


def create_doc_template(db: Session, data: DocTemplateCreateIn) -> DocTemplate:
    """Create a new doc template. Raises 409 if code already exists."""
    existing = db.execute(
        select(DocTemplate).where(DocTemplate.code == data.code)
    ).scalar_one_or_none()
    if existing:
        raise_business_error(
            "DOC_TEMPLATE_CODE_EXISTS",
            f"Doc template code '{data.code}' already exists",
            status_code=409,
        )

    template = DocTemplate(
        id=str(uuid4()),
        code=data.code,
        name=data.name,
        direction=data.direction,
        enabled=data.enabled,
        status_effect=data.status_effect,
        status_restore=data.status_restore,
        deadline_template_code=data.deadline_template_code,
        fee_draft_type=data.fee_draft_type,
        fee_item_list=data.fee_item_list,
        need_reply=data.need_reply,
        reply_to_template_code=data.reply_to_template_code,
        input_fields=data.input_fields,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_doc_template(db: Session, template_id: str, data: DocTemplateUpdateIn) -> DocTemplate:
    """Update an existing doc template. Raises 404 if not found."""
    template = db.execute(
        select(DocTemplate).where(DocTemplate.id == template_id)
    ).scalar_one_or_none()
    if not template:
        raise_business_error("DOC_TEMPLATE_NOT_FOUND", "Doc template not found", status_code=404)

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template
