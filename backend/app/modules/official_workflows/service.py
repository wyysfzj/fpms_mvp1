from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.annuity.models import GovPayment, PayList
from app.modules.cases.enums import CaseStatus
from app.modules.cases.lifecycle_contracts import (
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    EvidenceReference,
    LegalStatus,
    LifecycleEventCommand,
    OfficialProcedureStage,
)
from app.modules.cases.lifecycle_service import apply_lifecycle_event
from app.modules.cases.models import (
    Case,
    CaseActivityEvent,
    CaseActivityEventEvidence,
    T_CaseApplicant,
    T_CaseInventor,
)
from app.modules.documents.evidence_contracts import (
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
)
from app.modules.documents.evidence_policy import (
    _COPYABLE_OA_ATTACHMENT_ROLES,
    CopyableOaAttachmentEvidence,
    is_filing_full_word_ready,
)
from app.modules.documents.evidence_workflow_service import (
    FinalizeExternalSubmissionCommand,
    OaReplyPackageResult,
    PrepareOaReplyCommand,
    finalize_external_submission,
    prepare_oa_reply,
)
from app.modules.documents.models import (
    DocAttachment,
    DocTemplate,
    Document,
    DocumentEvidenceVersion,
    LetterHandoff,
    LetterHandoffAttachment,
)
from app.modules.documents.schemas import LetterHandoffAttachmentOut, LetterHandoffOut
from app.modules.documents.semantics import resolve_document_semantics
from app.modules.documents.service import summarize_attachment_manifest
from app.modules.fees.models import FeeDraft, OfficialFeeChecklist
from app.modules.masterdata.applicants.models import Applicant
from app.modules.masterdata.clients.models import ClientContact
from app.modules.official_workflows.filing_evidence_resolver import (
    resolve_filing_final_evidence,
)
from app.modules.official_workflows.models import (
    OfficialWorkPackage,
    OfficialWorkPackageChecklist,
    OfficialWorkPackageManifest,
    OfficialWorkPackageOverride,
    OfficialWorkPackageReceipt,
)
from app.modules.official_workflows.schemas import (
    OFFICIAL_WORK_PACKAGE_RECEIPT_KINDS,
    FilingPackageFeeSummaryOut,
    FilingPackageGateOut,
    FilingPackageXmlZipOut,
    FilingPreparationPackageOut,
    LetterHandoffContactOut,
    LetterHandoffMappingOut,
    LetterHandoffPreviewAttachmentOut,
    LetterHandoffPreviewOut,
    LetterHandoffResultOut,
    OaReplyAttachmentOut,
    OaReplyDocumentOut,
    OaReplyPackageOut,
    OfficialFeeChecklistOut,
    OfficialFeeDraftLinkOut,
    OfficialFeeLinkageBlockerOut,
    OfficialFeeLinkageOut,
    OfficialFieldCheckOut,
    OfficialFieldSummaryOut,
    OfficialPayListLinkOut,
    OfficialWorkPackageBlockerOut,
    OfficialWorkPackageChecklistOut,
    OfficialWorkPackageManifestOut,
    OfficialWorkPackageOut,
    OfficialWorkPackageStatusEvaluationOut,
)
from app.modules.tasks.enums import TaskAction, TaskStatus
from app.modules.tasks.models import Task, TaskLog, TaskTemplate
from app.modules.templates.models import FormatLetterMapping, Template

CHECKLIST_COMPLETE_STATUSES = {"DONE", "NOT_APPLICABLE", "OVERRIDDEN"}
OFFICIAL_FEE_COMPLETE_STATUSES = {"DONE", "READY", "NOT_APPLICABLE", "OVERRIDDEN"}
MAINTENANCE_MISSING_KINDS = {"SYSTEM_FIELD", "SYSTEM_FILE", "REQUIRED_MANIFEST"}
CONFIRMATION_MISSING_KINDS = {
    "OFFICIAL_TRANSIENT",
    "UNCONFIRMED_OWNERSHIP",
    "INTEGRATION_ONLY",
}
RECEIPT_ARCHIVED_STATUSES = {"ARCHIVED", "CONFIRMED", "RECEIVED"}
_MULTI_FILE_MANIFEST_ROLES = {"OA_ADDITIONAL_FILE", "OA_OTHER_PROOF"}


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_code(value: str | None) -> str | None:
    normalized = _normalize_text(value)
    if not normalized:
        return None
    return normalized.upper()


def classify_work_package_missing_item(missing_kind: str) -> str:
    kind = _normalize_code(missing_kind)
    if kind in MAINTENANCE_MISSING_KINDS:
        return "NEEDS_MAINTENANCE"
    if kind in CONFIRMATION_MISSING_KINDS:
        return "NEEDS_CONFIRMATION"
    raise_business_error(
        "OFFICIAL_WORK_PACKAGE_MISSING_KIND_INVALID",
        "Official work-package missing item kind is invalid",
        details={"missing_kind": missing_kind},
        status_code=400,
    )


def _get_package(db: Session, package_id: str) -> OfficialWorkPackage:
    package = db.execute(
        select(OfficialWorkPackage).where(OfficialWorkPackage.id == package_id)
    ).scalar_one_or_none()
    if not package:
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_NOT_FOUND",
            "Official work package not found",
            status_code=404,
        )
    return package


def _require_filing_package(package: OfficialWorkPackage) -> None:
    if _normalize_code(package.package_kind) != "FILING_PREP":
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_KIND_INVALID",
            "Official work package is not a filing preparation package",
            details={"package_kind": package.package_kind},
            status_code=400,
        )


def _require_oa_package(package: OfficialWorkPackage) -> None:
    if _normalize_code(package.package_kind) != "OA_REPLY":
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_KIND_INVALID",
            "Official work package is not an OA reply package",
            details={"package_kind": package.package_kind},
            status_code=400,
        )


def _get_case(db: Session, case_id: str) -> Case:
    case = db.execute(select(Case).where(Case.id == case_id)).scalar_one_or_none()
    if not case:
        raise_business_error("CASE_NOT_FOUND", "Case not found", status_code=404)
    return case


def _get_document(db: Session, document_id: str) -> Document:
    document = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if not document:
        raise_business_error("DOCUMENT_NOT_FOUND", "Document not found", status_code=404)
    return document


def _package_out(package: OfficialWorkPackage) -> OfficialWorkPackageOut:
    return OfficialWorkPackageOut(
        id=package.id,
        case_id=package.case_id,
        package_kind=package.package_kind,
        status=package.status,
        source_document_id=package.source_document_id,
        reply_document_id=package.reply_document_id,
        external_system=package.external_system,
        remark=package.remark,
    )


def _checklist_out(checklist: OfficialWorkPackageChecklist) -> OfficialWorkPackageChecklistOut:
    return OfficialWorkPackageChecklistOut(
        id=checklist.id,
        package_id=checklist.package_id,
        section_code=checklist.section_code,
        item_code=checklist.item_code,
        item_label=checklist.item_label,
        status=checklist.status,
        required=checklist.required,
        sort_order=checklist.sort_order,
        evidence_note=checklist.evidence_note,
    )


def _manifest_out(manifest: OfficialWorkPackageManifest) -> OfficialWorkPackageManifestOut:
    return OfficialWorkPackageManifestOut(
        id=manifest.id,
        package_id=manifest.package_id,
        attachment_id=manifest.attachment_id,
        evidence_version_id=manifest.evidence_version_id,
        official_file_role=manifest.official_file_role,
        source_role_alias=manifest.source_role_alias,
        external_upload_position=manifest.external_upload_position,
        content_hash=manifest.content_hash,
        required=manifest.required,
        present=manifest.present,
        sort_order=manifest.sort_order,
        note=manifest.note,
    )


def _get_attachment(db: Session, attachment_id: str) -> DocAttachment:
    attachment = db.execute(
        select(DocAttachment).where(DocAttachment.id == attachment_id)
    ).scalar_one_or_none()
    if not attachment:
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_RECEIPT_ATTACHMENT_NOT_FOUND",
            "Receipt attachment not found",
            status_code=404,
        )
    return attachment


def _case_attachments(db: Session, *, case_id: str) -> list[DocAttachment]:
    return (
        db.execute(
            select(DocAttachment)
            .join(Document, DocAttachment.document_id == Document.id)
            .where(Document.case_id == case_id)
            .order_by(DocAttachment.created_at.asc(), DocAttachment.id.asc())
        )
        .scalars()
        .all()
    )


def _official_field_summary(db: Session, *, case: Case) -> OfficialFieldSummaryOut:
    items: list[OfficialFieldCheckOut] = []

    def add_check(
        code: str,
        label: str,
        present: bool,
        message: str | None = None,
        status: str | None = None,
    ) -> None:
        resolved_status = status or ("READY" if present else "MISSING")
        items.append(
            OfficialFieldCheckOut(
                code=code,
                label=label,
                status=resolved_status,
                message=None if resolved_status == "READY" else message,
            )
        )

    add_check("TITLE_CN", "发明名称", bool(_normalize_text(case.title_cn)), "发明名称缺失")
    add_check(
        "PRIMARY_AGENT_ID",
        "代理人",
        bool(_normalize_text(case.primary_agent_id)),
        "代理人缺失",
    )
    add_check("SPEC_PAGES", "说明书页数", case.spec_pages is not None, "说明书页数缺失")
    add_check("CLAIM_COUNT", "权利要求项数", case.claim_count is not None, "权利要求项数缺失")
    add_check(
        "FEE_REDUCTION",
        "费减比例",
        bool(_normalize_text(case.fee_reduction)),
        "费减比例缺失或语义待确认",
    )

    applicants = (
        db.execute(
            select(T_CaseApplicant)
            .where(T_CaseApplicant.case_id == case.id)
            .order_by(T_CaseApplicant.seq.asc())
        )
        .scalars()
        .all()
    )
    if not applicants:
        add_check("APPLICANT_REQUIRED", "申请人", False, "至少需要一个申请人")
    applicant_master_ids = [
        applicant.applicant_id
        for applicant in applicants
        if _normalize_text(applicant.applicant_id)
    ]
    applicant_master_by_id = (
        {
            applicant.id: applicant
            for applicant in db.execute(
                select(Applicant).where(Applicant.id.in_(applicant_master_ids))
            ).scalars()
        }
        if applicant_master_ids
        else {}
    )
    for applicant in applicants:
        prefix = f"APPLICANT_{applicant.seq}"
        add_check(
            f"{prefix}_NAME",
            "申请人名称",
            bool(_normalize_text(applicant.name_cn) or _normalize_text(applicant.name_en)),
            "申请人名称缺失",
        )
        add_check(
            f"{prefix}_NATIONALITY",
            "申请人国籍",
            bool(_normalize_text(applicant.nationality)),
            "申请人国籍缺失",
        )
        add_check(
            f"{prefix}_CERTIFICATE_TYPE",
            "申请人证件类型",
            bool(_normalize_text(applicant.certificate_type)),
            "申请人证件类型缺失",
        )
        add_check(
            f"{prefix}_CERTIFICATE_NO",
            "申请人证件号",
            bool(_normalize_text(applicant.certificate_no)),
            "申请人证件号缺失",
        )
        add_check(
            f"{prefix}_OFFICIAL_POSTCODE",
            "申请人官方邮编",
            bool(_normalize_text(applicant.official_postcode)),
            "申请人官方邮编缺失",
        )
        applicant_master = (
            applicant_master_by_id.get(applicant.applicant_id) if applicant.applicant_id else None
        )
        if not applicant.applicant_id:
            add_check(
                f"{prefix}_TOTAL_POWER_OF_ATTORNEY_NO",
                "总委托书备案编号",
                False,
                "申请人主数据映射待确认，需先关联官方申请人后复用总委托书备案编号",
                status="NEEDS_CONFIRMATION",
            )
        else:
            add_check(
                f"{prefix}_TOTAL_POWER_OF_ATTORNEY_NO",
                "总委托书备案编号",
                bool(_normalize_text(applicant_master.total_power_of_attorney_no))
                if applicant_master
                else False,
                "总委托书备案编号缺失，请到申请人主数据维护",
            )

    inventors = (
        db.execute(
            select(T_CaseInventor)
            .where(T_CaseInventor.case_id == case.id)
            .order_by(T_CaseInventor.seq.asc())
        )
        .scalars()
        .all()
    )
    if not inventors:
        add_check("INVENTOR_REQUIRED", "发明人", False, "至少需要一个发明人")
    for inventor in inventors:
        prefix = f"INVENTOR_{inventor.seq}"
        add_check(
            f"{prefix}_NAME",
            "发明人名称",
            bool(_normalize_text(inventor.name_cn) or _normalize_text(inventor.name_en)),
            "发明人名称缺失",
        )
        add_check(
            f"{prefix}_NATIONALITY",
            "发明人国籍",
            bool(_normalize_text(inventor.nationality)),
            "发明人国籍缺失",
        )
        if _normalize_code(inventor.nationality) in {"CN", "CHINA", "中国"}:
            add_check(
                f"{prefix}_CHINA_ID_NO",
                "中国籍发明人身份证号",
                bool(_normalize_text(inventor.china_id_no)),
                "中国籍发明人身份证号缺失",
            )

    missing_codes = [item.code for item in items if item.status != "READY"]
    return OfficialFieldSummaryOut(
        status="READY" if not missing_codes else "NEEDS_MAINTENANCE",
        missing_codes=missing_codes,
        items=items,
    )


def _upsert_manifest_role(
    db: Session,
    *,
    package_id: str,
    role: str,
    required: bool,
    sort_order: int,
    attachment: DocAttachment | None = None,
    external_upload_position: str | None = None,
    note: str | None = None,
) -> OfficialWorkPackageManifest:
    if role in _MULTI_FILE_MANIFEST_ROLES:
        if attachment:
            placeholders = (
                db.execute(
                    select(OfficialWorkPackageManifest).where(
                        OfficialWorkPackageManifest.package_id == package_id,
                        OfficialWorkPackageManifest.official_file_role == role,
                        OfficialWorkPackageManifest.attachment_id.is_(None),
                    )
                )
                .scalars()
                .all()
            )
            for placeholder in placeholders:
                db.delete(placeholder)
            existing = (
                db.execute(
                    select(OfficialWorkPackageManifest).where(
                        OfficialWorkPackageManifest.package_id == package_id,
                        OfficialWorkPackageManifest.official_file_role == role,
                        OfficialWorkPackageManifest.attachment_id == attachment.id,
                    )
                )
                .scalars()
                .first()
            )
        else:
            existing = (
                db.execute(
                    select(OfficialWorkPackageManifest).where(
                        OfficialWorkPackageManifest.package_id == package_id,
                        OfficialWorkPackageManifest.official_file_role == role,
                        OfficialWorkPackageManifest.attachment_id.is_(None),
                    )
                )
                .scalars()
                .first()
            )
    else:
        existing = (
            db.execute(
                select(OfficialWorkPackageManifest).where(
                    OfficialWorkPackageManifest.package_id == package_id,
                    OfficialWorkPackageManifest.official_file_role == role,
                )
            )
            .scalars()
            .first()
        )
    manifest = existing or OfficialWorkPackageManifest(
        id=str(uuid4()),
        package_id=package_id,
        official_file_role=role,
    )
    evidence_version_ids = (
        db.execute(
            select(DocumentEvidenceVersion.id)
            .where(DocumentEvidenceVersion.attachment_id == attachment.id)
            .limit(2)
        )
        .scalars()
        .all()
        if attachment
        else []
    )
    if len(evidence_version_ids) > 1:
        raise_business_error(
            "WORK_PACKAGE_MANIFEST_EVIDENCE_CONFLICT",
            "Attachment evidence-version identity is ambiguous",
            status_code=409,
        )
    manifest.attachment_id = attachment.id if attachment else None
    manifest.evidence_version_id = evidence_version_ids[0] if evidence_version_ids else None
    manifest.source_role_alias = (
        getattr(attachment, "source_role_alias", None) if attachment else None
    )
    manifest.external_upload_position = external_upload_position or (
        getattr(attachment, "external_upload_position", None) if attachment else None
    )
    manifest.content_hash = getattr(attachment, "content_hash", None) if attachment else None
    manifest.required = required
    manifest.present = bool(attachment)
    manifest.sort_order = sort_order
    manifest.note = note
    if not existing:
        db.add(manifest)
    return manifest


def _prune_stale_multi_file_manifest_rows(
    db: Session,
    *,
    package_id: str,
    role: str,
    current_attachment_ids: set[str],
) -> None:
    manifests = (
        db.execute(
            select(OfficialWorkPackageManifest).where(
                OfficialWorkPackageManifest.package_id == package_id,
                OfficialWorkPackageManifest.official_file_role == role,
            )
        )
        .scalars()
        .all()
    )
    for manifest in manifests:
        if manifest.attachment_id and manifest.attachment_id not in current_attachment_ids:
            db.delete(manifest)
        elif current_attachment_ids and manifest.attachment_id is None:
            db.delete(manifest)


def _upsert_checklist(
    db: Session,
    *,
    package_id: str,
    section_code: str,
    item_code: str,
    item_label: str,
    status: str = "PENDING",
    required: bool = True,
    sort_order: int | None = None,
    evidence_note: str | None = None,
) -> OfficialWorkPackageChecklist:
    existing = (
        db.execute(
            select(OfficialWorkPackageChecklist).where(
                OfficialWorkPackageChecklist.package_id == package_id,
                OfficialWorkPackageChecklist.item_code == item_code,
            )
        )
        .scalars()
        .first()
    )
    checklist = existing or OfficialWorkPackageChecklist(
        id=str(uuid4()),
        package_id=package_id,
        item_code=item_code,
    )
    checklist.section_code = section_code
    checklist.item_label = item_label
    checklist.status = _normalize_code(status) or "PENDING"
    checklist.required = required
    checklist.sort_order = sort_order
    if evidence_note is not None:
        checklist.evidence_note = _normalize_text(evidence_note)
    if not existing:
        db.add(checklist)
    return checklist


def _checklist_blocker_status(checklist: OfficialWorkPackageChecklist) -> str:
    status = _normalize_code(checklist.status) or "PENDING"
    if status == "NEEDS_CONFIRMATION":
        return "NEEDS_CONFIRMATION"
    return "NEEDS_MAINTENANCE"


def _has_archived_receipt(receipts: list[OfficialWorkPackageReceipt]) -> bool:
    return any(
        bool(receipt.receipt_attachment_id)
        and (_normalize_code(receipt.archive_status) in RECEIPT_ARCHIVED_STATUSES)
        for receipt in receipts
    )


def _manual_payment_status(payments: list[GovPayment]) -> str:
    if not payments:
        return "NOT_CREATED"
    paid_rows = [
        payment
        for payment in payments
        if (_normalize_code(payment.status) in {"PAID", "RECORDED"})
        or payment.paid_date is not None
    ]
    if not paid_rows:
        return "MANUAL_PENDING"
    if len(paid_rows) == len(payments):
        return "MANUAL_CONFIRMED"
    return "MANUAL_PARTIAL"


def _is_confirmed_official_fee_checklist(checklist: OfficialFeeChecklist) -> bool:
    return _normalize_code(checklist.status) in OFFICIAL_FEE_COMPLETE_STATUSES


def _fee_checklist_blockers(
    checklists: list[OfficialFeeChecklist],
    *,
    skip_codes: set[str] | None = None,
) -> list[OfficialFeeLinkageBlockerOut]:
    blockers: list[OfficialFeeLinkageBlockerOut] = []
    skipped = skip_codes or set()
    for checklist in checklists:
        if checklist.checklist_code in skipped:
            continue
        if checklist.required and not _is_confirmed_official_fee_checklist(checklist):
            source_type = "FEE_DRAFT" if checklist.fee_draft_id else "PAY_LIST"
            source_id = checklist.fee_draft_id or (
                str(checklist.pay_list_id) if checklist.pay_list_id is not None else None
            )
            blockers.append(
                OfficialFeeLinkageBlockerOut(
                    blocker_code=checklist.checklist_code,
                    blocker_label=checklist.checklist_label,
                    source_type=source_type,
                    source_id=source_id,
                    status=_normalize_code(checklist.status) or "PENDING",
                    message=checklist.blocker_reason or "Customer confirmation is required",
                )
            )
    return blockers


def _format_ratio(value: Decimal) -> str:
    if value == Decimal("1"):
        return "1.0"
    if value == Decimal("0"):
        return "0"
    return format(value.normalize(), "f")


def _official_fee_reduction_conversion(
    customer_reduction_ratio: str | None,
) -> dict[str, str | None]:
    raw_value = _normalize_text(customer_reduction_ratio)
    if raw_value is None:
        return {
            "customer_fee_reduction_ratio": "0",
            "payable_fee_ratio": "1.0",
            "fee_reduction_conversion_status": "CONFIRMED",
            "fee_reduction_conversion_note": "无费减时客户减免比例为 0，官方应缴比例为 1.0。",
        }

    try:
        reduction_ratio = Decimal(raw_value)
    except InvalidOperation:
        return {
            "customer_fee_reduction_ratio": raw_value,
            "payable_fee_ratio": None,
            "fee_reduction_conversion_status": "NEEDS_CONFIRMATION",
            "fee_reduction_conversion_note": "费减比例不是可识别数值，需人工确认。",
        }

    if reduction_ratio not in {Decimal("0"), Decimal("0.7"), Decimal("0.85")}:
        return {
            "customer_fee_reduction_ratio": _format_ratio(reduction_ratio),
            "payable_fee_ratio": None,
            "fee_reduction_conversion_status": "NEEDS_CONFIRMATION",
            "fee_reduction_conversion_note": "该费减值不属于客户已确认的 0 / 0.7 / 0.85 规则。",
        }

    payable_ratio = Decimal("1") - reduction_ratio
    return {
        "customer_fee_reduction_ratio": _format_ratio(reduction_ratio),
        "payable_fee_ratio": _format_ratio(payable_ratio),
        "fee_reduction_conversion_status": "CONFIRMED",
        "fee_reduction_conversion_note": (
            f"客户旧系统值表示减免比例 {_format_ratio(reduction_ratio)}，"
            f"官方计费应缴比例为 {_format_ratio(payable_ratio)}。"
        ),
    }


def _official_fee_reduction_note_for_response(
    *,
    draft_note: str | None,
    conversion: dict[str, str | None],
) -> str | None:
    note = _normalize_text(draft_note)
    conversion_note = conversion["fee_reduction_conversion_note"]
    if conversion["fee_reduction_conversion_status"] == "CONFIRMED" and (
        not note or "待确认" in note or "未确认" in note
    ):
        return conversion_note
    return note


def _template_status_blockers(
    *,
    fee_drafts: list[FeeDraft],
    pay_lists: list[PayList],
) -> list[OfficialFeeLinkageBlockerOut]:
    blockers: list[OfficialFeeLinkageBlockerOut] = []
    for draft in fee_drafts:
        status = _normalize_code(draft.official_template_status)
        if status in {"UNCONFIRMED", "BLOCKED"}:
            blockers.append(
                OfficialFeeLinkageBlockerOut(
                    blocker_code="FEE_DRAFT_OFFICIAL_TEMPLATE_UNCONFIRMED",
                    blocker_label="费用草单官方模板兼容性",
                    source_type="FEE_DRAFT",
                    source_id=draft.id,
                    status=status,
                    message=draft.official_template_note
                    or "Official payment template compatibility is not confirmed",
                )
            )

    for pay_list in pay_lists:
        status = _normalize_code(pay_list.official_upload_template_status)
        if status in {"UNCONFIRMED", "BLOCKED"}:
            blockers.append(
                OfficialFeeLinkageBlockerOut(
                    blocker_code="OFFICIAL_UPLOAD_TEMPLATE_UNCONFIRMED",
                    blocker_label="官网补充缴费信息模板兼容性",
                    source_type="PAY_LIST",
                    source_id=str(pay_list.id),
                    status=status,
                    message=pay_list.official_pay_list_boundary_note
                    or "Official upload template compatibility is not confirmed",
                )
            )
    return blockers


def get_official_fee_linkage(
    db: Session,
    *,
    package_id: str,
) -> OfficialFeeLinkageOut:
    package = _get_package(db, package_id)
    case = _get_case(db, package.case_id)
    fee_reduction_conversion = _official_fee_reduction_conversion(case.fee_reduction)
    fee_drafts = (
        db.execute(
            select(FeeDraft)
            .where(FeeDraft.case_id == package.case_id)
            .order_by(FeeDraft.updated_at.desc(), FeeDraft.id.desc())
        )
        .scalars()
        .all()
    )
    draft_ids = [draft.id for draft in fee_drafts]

    gov_payments = (
        db.execute(
            select(GovPayment)
            .where(GovPayment.case_id == package.case_id)
            .order_by(GovPayment.id.asc())
        )
        .scalars()
        .all()
    )
    pay_list_ids = sorted({payment.pay_list_id for payment in gov_payments})
    pay_lists = (
        db.execute(select(PayList).where(PayList.id.in_(pay_list_ids)).order_by(PayList.id.asc()))
        .scalars()
        .all()
        if pay_list_ids
        else []
    )
    payments_by_pay_list: dict[int, list[GovPayment]] = {
        pay_list_id: [] for pay_list_id in pay_list_ids
    }
    for payment in gov_payments:
        payments_by_pay_list.setdefault(payment.pay_list_id, []).append(payment)

    checklist_conditions = []
    if draft_ids:
        checklist_conditions.append(OfficialFeeChecklist.fee_draft_id.in_(draft_ids))
    if pay_list_ids:
        checklist_conditions.append(OfficialFeeChecklist.pay_list_id.in_(pay_list_ids))
    checklists = (
        db.execute(
            select(OfficialFeeChecklist)
            .where(or_(*checklist_conditions))
            .order_by(OfficialFeeChecklist.sort_order.asc(), OfficialFeeChecklist.id.asc())
        )
        .scalars()
        .all()
        if checklist_conditions
        else []
    )

    skip_checklist_codes: set[str] = set()
    if fee_reduction_conversion["fee_reduction_conversion_status"] == "CONFIRMED":
        skip_checklist_codes.add("FEE_REDUCTION_RATE")
    blockers = _fee_checklist_blockers(list(checklists), skip_codes=skip_checklist_codes)
    blockers.extend(
        _template_status_blockers(fee_drafts=list(fee_drafts), pay_lists=list(pay_lists))
    )

    fee_rate_source_ready = any(
        checklist.checklist_code == "FEE_RATE_SOURCE_READABLE"
        and _is_confirmed_official_fee_checklist(checklist)
        for checklist in checklists
    )
    if not fee_rate_source_ready:
        blockers.append(
            OfficialFeeLinkageBlockerOut(
                blocker_code="FEE_RATE_SOURCE_UNCONFIRMED",
                blocker_label="官费标准费率来源",
                source_type="CUSTOMER_CONFIRMATION",
                source_id=None,
                status="UNCONFIRMED",
                message="官费标准费率清单来自不可机读图片，需客户提供 Excel、可复制表格或清晰 PDF",
            )
        )

    template_statuses = [
        _normalize_code(draft.official_template_status) for draft in fee_drafts
    ] + [_normalize_code(pay_list.official_upload_template_status) for pay_list in pay_lists]
    known_template_statuses = [status for status in template_statuses if status]
    official_excel_template_ready = bool(known_template_statuses) and all(
        status == "READY" for status in known_template_statuses
    )

    return OfficialFeeLinkageOut(
        package_id=package.id,
        case_id=package.case_id,
        official_excel_template_ready=official_excel_template_ready,
        official_excel_generation_allowed=official_excel_template_ready and fee_rate_source_ready,
        fee_drafts=[
            OfficialFeeDraftLinkOut(
                id=draft.id,
                draft_type=draft.draft_type,
                status=draft.status,
                currency=draft.currency,
                total_gov=draft.total_gov,
                total_service=draft.total_service,
                total_misc=draft.total_misc,
                amount=draft.amount,
                official_fee_reduction_note=_official_fee_reduction_note_for_response(
                    draft_note=draft.official_fee_reduction_note,
                    conversion=fee_reduction_conversion,
                ),
                customer_fee_reduction_ratio=fee_reduction_conversion[
                    "customer_fee_reduction_ratio"
                ],
                payable_fee_ratio=fee_reduction_conversion["payable_fee_ratio"],
                fee_reduction_conversion_status=fee_reduction_conversion[
                    "fee_reduction_conversion_status"
                ],
                fee_reduction_conversion_note=fee_reduction_conversion[
                    "fee_reduction_conversion_note"
                ],
                official_template_status=draft.official_template_status,
                official_template_version=draft.official_template_version,
                official_template_note=draft.official_template_note,
            )
            for draft in fee_drafts
        ],
        pay_lists=[
            OfficialPayListLinkOut(
                id=pay_list.id,
                pay_list_no=pay_list.pay_list_no,
                status=pay_list.status,
                currency=pay_list.currency,
                planned_pay_date=pay_list.planned_pay_date,
                paid_date=pay_list.paid_date,
                total_amount=pay_list.total_amount,
                official_upload_template_status=pay_list.official_upload_template_status,
                official_upload_template_name=pay_list.official_upload_template_name,
                official_upload_batch_limit=pay_list.official_upload_batch_limit,
                official_pay_list_boundary_note=pay_list.official_pay_list_boundary_note,
                manual_payment_status=_manual_payment_status(
                    payments_by_pay_list.get(pay_list.id, [])
                ),
                gov_payment_statuses=[
                    payment.status for payment in payments_by_pay_list.get(pay_list.id, [])
                ],
            )
            for pay_list in pay_lists
        ],
        checklist=[
            OfficialFeeChecklistOut(
                id=checklist.id,
                fee_draft_id=checklist.fee_draft_id,
                pay_list_id=checklist.pay_list_id,
                checklist_code=checklist.checklist_code,
                checklist_label=checklist.checklist_label,
                status=checklist.status,
                required=checklist.required,
                blocker_reason=checklist.blocker_reason,
                sort_order=checklist.sort_order,
            )
            for checklist in checklists
        ],
        customer_confirmation_blockers=blockers,
    )


def _filing_manifest_lookup(
    manifests: list[OfficialWorkPackageManifest],
) -> dict[str, OfficialWorkPackageManifest]:
    return {
        manifest.official_file_role: manifest
        for manifest in manifests
        if manifest.official_file_role
    }


def _gate_from_manifest(
    manifest_by_role: dict[str, OfficialWorkPackageManifest],
    *,
    role: str,
    required: bool,
) -> FilingPackageGateOut:
    manifest = manifest_by_role.get(role)
    return FilingPackageGateOut(
        role=role,
        required=manifest.required if manifest else required,
        status="READY" if manifest and manifest.present else "MISSING",
        attachment_id=manifest.attachment_id if manifest else None,
        file_name=None,
    )


def _xml_zip_from_manifest(
    manifest_by_role: dict[str, OfficialWorkPackageManifest],
) -> FilingPackageXmlZipOut:
    manifest = manifest_by_role.get("FILING_XML_ZIP")
    if manifest and manifest.present:
        return FilingPackageXmlZipOut(
            status="PRESENT",
            attachment_id=manifest.attachment_id,
            placeholder=None,
        )
    return FilingPackageXmlZipOut(
        status="MISSING",
        placeholder="P1 records XML zip readiness only; generation is out of scope.",
    )


def _filing_fee_summary(db: Session, *, package_id: str) -> FilingPackageFeeSummaryOut:
    linkage = get_official_fee_linkage(db, package_id=package_id)
    return FilingPackageFeeSummaryOut(
        draft_count=len(linkage.fee_drafts),
        pay_list_count=len(linkage.pay_lists),
        official_template_ready=linkage.official_excel_template_ready,
        blocker_count=len(linkage.customer_confirmation_blockers),
    )


def ensure_filing_preparation_package(
    db: Session,
    *,
    case_id: str,
    actor_id: str,
) -> FilingPreparationPackageOut:
    if type(actor_id) is not str or not actor_id.strip() or len(actor_id) > 36:
        raise_business_error(
            "FILING_PREPARATION_ACTOR_INVALID",
            "Filing preparation actor is invalid",
            status_code=400,
        )
    case = _get_case(db, case_id)
    resolve_key = f"FILING_PREP:{case.id}"
    existing = (
        db.execute(
            select(OfficialWorkPackage)
            .where(
                OfficialWorkPackage.case_id == case.id,
                OfficialWorkPackage.package_kind == "FILING_PREP",
            )
            .order_by(OfficialWorkPackage.created_at.asc(), OfficialWorkPackage.id.asc())
        )
        .scalars()
        .all()
    )
    if existing and (len(existing) != 1 or existing[0].resolve_key != resolve_key):
        raise_business_error(
            "FILING_PREPARATION_IDENTITY_CONFLICT",
            "Filing preparation package identity is inconsistent",
            details={
                "case_id": case.id,
                "expected_resolve_key": resolve_key,
                "packages": [
                    {"id": package.id, "resolve_key": package.resolve_key} for package in existing
                ],
            },
            status_code=409,
        )
    if existing:
        package = existing[0]
        if (
            type(package.created_by) is not str
            or not package.created_by.strip()
            or len(package.created_by) > 36
        ):
            raise_business_error(
                "FILING_PREPARATION_PROVENANCE_CONFLICT",
                "Filing preparation package creator is missing or invalid",
                status_code=409,
            )
        _record_filing_preparation_started(db, package=package, actor_id=actor_id)
        return get_filing_preparation_package(db, package_id=package.id)

    if _normalize_code(case.status) != "NOT_FILED":
        raise_business_error(
            "FILING_PREPARATION_CASE_STATE_INVALID",
            "Filing preparation package can only be created for a NOT_FILED case",
            details={"case_id": case.id, "case_status": case.status},
            status_code=409,
        )

    package = OfficialWorkPackage(
        id=str(uuid4()),
        case_id=case.id,
        package_kind="FILING_PREP",
        status="PREPARING",
        resolve_key=resolve_key,
        created_by=actor_id,
        updated_by=actor_id,
    )
    resolve_collision = db.execute(
        select(OfficialWorkPackage).where(OfficialWorkPackage.resolve_key == resolve_key)
    ).scalar_one_or_none()
    if resolve_collision is not None:
        raise_business_error(
            "FILING_PREPARATION_IDENTITY_CONFLICT",
            "Filing preparation package identity is inconsistent",
            details={"case_id": case.id, "expected_resolve_key": resolve_key},
            status_code=409,
        )
    db.add(package)
    try:
        db.flush()
    except IntegrityError:
        raise_business_error(
            "FILING_PREPARATION_IDENTITY_CONFLICT",
            "Filing preparation package identity is inconsistent",
            details={"case_id": case.id, "expected_resolve_key": resolve_key},
            status_code=409,
        )
    db.refresh(package)
    result = _refresh_filing_preparation_package(db, package=package)
    _record_filing_preparation_started(db, package=package, actor_id=actor_id)
    return result


def _canonical_filing_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _filing_snapshot(package: OfficialWorkPackage) -> dict[str, object]:
    return {
        "case_id": package.case_id,
        "id": package.id,
        "package_kind": package.package_kind,
        "resolve_key": package.resolve_key,
    }


def _filing_snapshot_hash(snapshot: dict[str, object]) -> str:
    canonical = _canonical_filing_json(snapshot).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def _filing_provenance_conflict() -> None:
    raise_business_error(
        "LIFECYCLE_IDEMPOTENCY_CONFLICT",
        "Persisted filing preparation provenance is inconsistent",
        status_code=409,
    )


def _stored_filing_command(
    db: Session,
    *,
    package: OfficialWorkPackage,
    actor_id: str,
    activity: CaseActivityEvent,
) -> LifecycleEventCommand:
    evidence_rows = (
        db.execute(
            select(CaseActivityEventEvidence).where(
                CaseActivityEventEvidence.activity_id == activity.id
            )
        )
        .scalars()
        .all()
    )
    try:
        payload = json.loads(activity.payload_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        _filing_provenance_conflict()
    if (
        type(payload) is not dict
        or _canonical_filing_json(payload) != activity.payload_json
        or set(payload) != {"evidence_schema", "source_snapshot", "source_snapshot_hash"}
        or payload.get("evidence_schema") != "FPMS_FILING_PREPARATION_EVIDENCE_V1"
    ):
        _filing_provenance_conflict()
    snapshot = payload.get("source_snapshot")
    if (
        type(snapshot) is not dict
        or set(snapshot) != {"case_id", "id", "package_kind", "resolve_key"}
        or any(type(snapshot.get(key)) is not str or not snapshot[key] for key in snapshot)
        or snapshot["case_id"] != package.case_id
        or snapshot["id"] != package.id
        or snapshot["package_kind"] != "FILING_PREP"
        or snapshot["resolve_key"] != f"FILING_PREP:{snapshot['case_id']}"
    ):
        _filing_provenance_conflict()
    snapshot_hash = _filing_snapshot_hash(snapshot)
    if payload.get("source_snapshot_hash") != snapshot_hash or len(evidence_rows) != 1:
        _filing_provenance_conflict()
    evidence = evidence_rows[0]
    if (
        activity.activity_type != "FILING_PREPARATION_STARTED"
        or activity.lane != ActivityLane.LIFECYCLE.value
        or activity.confirmation_status != ConfirmationStatus.CONFIRMED.value
        or activity.effective_at != activity.occurred_at
        or activity.effective_at != package.created_at
        or activity.occurred_at != package.created_at
        or evidence.case_id != package.case_id
        or evidence.evidence_kind != "FILING_WORK_PACKAGE"
        or evidence.object_type != "OfficialWorkPackage"
        or evidence.object_id != package.id
        or evidence.content_hash != snapshot_hash
        or evidence.captured_at != activity.effective_at
        or evidence.captured_at != package.created_at
    ):
        _filing_provenance_conflict()
    return LifecycleEventCommand(
        case_id=package.case_id,
        event_type="FILING_PREPARATION_STARTED",
        lane=ActivityLane.LIFECYCLE,
        effective_at=activity.effective_at,
        occurred_at=activity.occurred_at,
        evidence_refs=(
            EvidenceReference(
                case_id=evidence.case_id,
                evidence_kind=evidence.evidence_kind,
                object_type=evidence.object_type,
                object_id=evidence.object_id,
                content_hash=evidence.content_hash,
                captured_at=evidence.captured_at,
            ),
        ),
        actor_id=actor_id,
        idempotency_key=f"filing-preparation-started:{package.id}",
        confirmation_status=ConfirmationStatus.CONFIRMED,
        payload=payload,
    )


def _record_filing_preparation_started(
    db: Session,
    *,
    package: OfficialWorkPackage,
    actor_id: str,
) -> None:
    idempotency_key = f"filing-preparation-started:{package.id}"
    activity = db.execute(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == package.case_id,
            CaseActivityEvent.idempotency_key == idempotency_key,
        )
    ).scalar_one_or_none()
    if activity is None:
        snapshot = _filing_snapshot(package)
        snapshot_hash = _filing_snapshot_hash(snapshot)
        payload = {
            "evidence_schema": "FPMS_FILING_PREPARATION_EVIDENCE_V1",
            "source_snapshot": snapshot,
            "source_snapshot_hash": snapshot_hash,
        }
        command = LifecycleEventCommand(
            case_id=package.case_id,
            event_type="FILING_PREPARATION_STARTED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=package.created_at,
            occurred_at=package.created_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=package.case_id,
                    evidence_kind="FILING_WORK_PACKAGE",
                    object_type="OfficialWorkPackage",
                    object_id=package.id,
                    content_hash=snapshot_hash,
                    captured_at=package.created_at,
                ),
            ),
            actor_id=actor_id,
            idempotency_key=idempotency_key,
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload=payload,
        )
    else:
        command = _stored_filing_command(
            db,
            package=package,
            actor_id=actor_id,
            activity=activity,
        )
    apply_lifecycle_event(command, db)


def get_filing_preparation_package(
    db: Session,
    *,
    package_id: str,
) -> FilingPreparationPackageOut:
    package = _get_package(db, package_id)
    _require_filing_package(package)
    case = _get_case(db, package.case_id)
    manifests = (
        db.execute(
            select(OfficialWorkPackageManifest)
            .where(OfficialWorkPackageManifest.package_id == package_id)
            .order_by(OfficialWorkPackageManifest.sort_order.asc())
        )
        .scalars()
        .all()
    )
    checklists = (
        db.execute(
            select(OfficialWorkPackageChecklist)
            .where(OfficialWorkPackageChecklist.package_id == package_id)
            .order_by(
                OfficialWorkPackageChecklist.sort_order.asc(), OfficialWorkPackageChecklist.id.asc()
            )
        )
        .scalars()
        .all()
    )
    manifest_by_role = _filing_manifest_lookup(list(manifests))
    merged_pdf = manifest_by_role.get("FILING_MERGED_PDF")

    return FilingPreparationPackageOut(
        package=_package_out(package),
        official_field_summary=_official_field_summary(db, case=case),
        technical_disclosure_gate=_gate_from_manifest(
            manifest_by_role,
            role="TECHNICAL_DISCLOSURE",
            required=True,
        ),
        commission_instruction_gate=_gate_from_manifest(
            manifest_by_role,
            role="COMMISSION_INSTRUCTION",
            required=False,
        ),
        filing_file_roles=[_manifest_out(manifest) for manifest in manifests],
        official_page_checklist=[_checklist_out(checklist) for checklist in checklists],
        xml_zip=_xml_zip_from_manifest(manifest_by_role),
        merged_pdf_archive_status="PRESENT" if merged_pdf and merged_pdf.present else "MISSING",
        fee_summary=_filing_fee_summary(db, package_id=package_id),
    )


def refresh_filing_preparation_package(
    db: Session,
    *,
    package_id: str,
    require_commission_instruction: bool = False,
) -> FilingPreparationPackageOut:
    package = _get_package(db, package_id)
    _require_filing_package(package)
    result = _refresh_filing_preparation_package(
        db,
        package=package,
        require_commission_instruction=require_commission_instruction,
    )
    db.commit()
    return result


def _refresh_filing_preparation_package(
    db: Session,
    *,
    package: OfficialWorkPackage,
    require_commission_instruction: bool = False,
) -> FilingPreparationPackageOut:
    attachments = _case_attachments(db, case_id=package.case_id)
    summary = summarize_attachment_manifest(
        attachments,
        require_commission_instruction=require_commission_instruction,
    )
    items_by_role = {
        item.official_file_role: item
        for item in (
            summary.intake_gate_roles
            + summary.filing_roles
            + summary.archive_roles
            + summary.historical_alias_roles
        )
        if item.official_file_role
    }
    attachments_by_id = {attachment.id: attachment for attachment in attachments}

    desired_roles = [
        ("TECHNICAL_DISCLOSURE", True, 10, None),
        (
            "COMMISSION_INSTRUCTION",
            require_commission_instruction,
            20,
            "客户明确有委托指示时必须上传；无则保持 optional gate",
        ),
        ("FILING_XML_ZIP", True, 30, "P1 只记录 XML zip 引用，不生成 XML"),
        ("FILING_MERGED_PDF", False, 40, "官方提交后归档合并 PDF"),
    ]
    for role, required, sort_order, note in desired_roles:
        item = items_by_role.get(role)
        attachment = attachments_by_id.get(item.attachment_id) if item else None
        _upsert_manifest_role(
            db,
            package_id=package.id,
            role=role,
            required=required,
            sort_order=sort_order,
            attachment=attachment,
            external_upload_position=item.external_upload_position if item else None,
            note=note,
        )

    full_word_item = items_by_role.get("FILING_FULL_WORD")
    existing_full_word_manifest = (
        db.execute(
            select(OfficialWorkPackageManifest).where(
                OfficialWorkPackageManifest.package_id == package.id,
                OfficialWorkPackageManifest.official_file_role == "FILING_FULL_WORD",
            )
        )
        .scalars()
        .first()
    )
    if full_word_item is not None or existing_full_word_manifest is not None:
        full_word_attachment = (
            attachments_by_id.get(full_word_item.attachment_id) if full_word_item else None
        )
        evidence_versions = (
            db.execute(
                select(DocumentEvidenceVersion)
                .where(DocumentEvidenceVersion.attachment_id == full_word_attachment.id)
                .limit(2)
            )
            .scalars()
            .all()
            if full_word_attachment
            else []
        )
        ready_attachment = (
            full_word_attachment
            if len(evidence_versions) == 1
            and is_filing_full_word_ready(
                case_id=package.case_id,
                evidence_version=evidence_versions[0],
            )
            else None
        )
        _upsert_manifest_role(
            db,
            package_id=package.id,
            role="FILING_FULL_WORD",
            required=True,
            sort_order=25,
            attachment=ready_attachment,
        )

    _upsert_checklist(
        db,
        package_id=package.id,
        section_code="OFFICIAL_PAGE",
        item_code="PREVIEW_CONFIRMED",
        item_label="官方页面预览已确认",
        status="PENDING",
        required=True,
        sort_order=10,
    )
    _upsert_checklist(
        db,
        package_id=package.id,
        section_code="OFFICIAL_PAGE",
        item_code="SIGNATURE_CONFIRMED",
        item_label="签名/提交由人工完成",
        status="PENDING",
        required=True,
        sort_order=20,
    )

    package.status = "NEEDS_MAINTENANCE"
    db.flush()
    return get_filing_preparation_package(db, package_id=package.id)


def update_filing_preparation_checklist(
    db: Session,
    *,
    package_id: str,
    item_code: str,
    status: str,
    evidence_note: str | None = None,
) -> OfficialWorkPackageChecklist:
    package = _get_package(db, package_id)
    _require_filing_package(package)
    checklist = _upsert_checklist(
        db,
        package_id=package.id,
        section_code="OFFICIAL_PAGE",
        item_code=_normalize_code(item_code) or item_code,
        item_label=item_code,
        status=status,
        required=True,
        evidence_note=evidence_note,
    )
    db.commit()
    db.refresh(checklist)
    return checklist


def record_filing_preparation_external_operation(
    db: Session,
    *,
    package_id: str,
    operation_code: str,
    occurred_at: datetime,
    note: str | None = None,
    actor_id: str | None = None,
) -> OfficialWorkPackageChecklist:
    normalized_operation = _normalize_code(operation_code) or operation_code
    if normalized_operation == "EXTERNAL_SUBMISSION_RECORDED":
        initial_evidence = resolve_filing_final_evidence(package_id, db)
        is_fresh = (
            initial_evidence.final_submitted_at is None
            and initial_evidence.submission_activity_id is None
            and initial_evidence.submission_activity_hash is None
        )
        is_replay = (
            initial_evidence.final_submitted_at == occurred_at
            and initial_evidence.submission_activity_id is not None
            and initial_evidence.submission_activity_hash is not None
        )
        if not is_fresh and not is_replay:
            raise_business_error(
                "FILING_FINAL_EVIDENCE_CONFLICT",
                "Filing submission evidence conflicts with this external operation",
                status_code=409,
            )

        idempotency_key = f"filing-external:{package_id}:{occurred_at.isoformat()}"
        finalized = finalize_external_submission(
            FinalizeExternalSubmissionCommand(
                case_id=initial_evidence.case_id,
                evidence_version_id=initial_evidence.evidence_version_id,
                actor_id=actor_id,
                submitted_at=occurred_at,
                idempotency_key=idempotency_key,
            ),
            db,
        )
        db.flush()
        resolved_evidence = resolve_filing_final_evidence(package_id, db)
        unchanged_resolution = (
            resolved_evidence.package_id == initial_evidence.package_id
            and resolved_evidence.case_id == initial_evidence.case_id
            and resolved_evidence.evidence_version_id == initial_evidence.evidence_version_id
            and resolved_evidence.content_hash == initial_evidence.content_hash
            and resolved_evidence.reviewer_id == initial_evidence.reviewer_id
            and resolved_evidence.reviewed_at == initial_evidence.reviewed_at
        )
        exact_finalization = (
            finalized.case_id == initial_evidence.case_id
            and finalized.evidence_version_id == initial_evidence.evidence_version_id
            and finalized.content_hash == initial_evidence.content_hash
            and finalized.submitted_at == occurred_at
            and finalized.idempotency_key == idempotency_key
            and finalized.reused is is_replay
            and resolved_evidence.final_submitted_at == occurred_at
            and resolved_evidence.submission_activity_id == finalized.activity_id
            and resolved_evidence.submission_activity_hash is not None
        )
        exact_replay = is_fresh or (
            resolved_evidence.submission_activity_id == initial_evidence.submission_activity_id
            and resolved_evidence.submission_activity_hash
            == initial_evidence.submission_activity_hash
        )
        if not unchanged_resolution or not exact_finalization or not exact_replay:
            raise_business_error(
                "FILING_FINAL_EVIDENCE_CONFLICT",
                "Finalized filing evidence does not match the external operation",
                status_code=409,
            )

        lifecycle_idempotency_key = (
            f"filing-external-lifecycle:{package_id}:{occurred_at.isoformat()}"
        )
        lifecycle_result = apply_lifecycle_event(
            LifecycleEventCommand(
                case_id=resolved_evidence.case_id,
                event_type="FILING_EXTERNAL_SUBMISSION_RECORDED",
                lane=ActivityLane.LIFECYCLE,
                effective_at=occurred_at,
                occurred_at=occurred_at,
                evidence_refs=(
                    EvidenceReference(
                        case_id=resolved_evidence.case_id,
                        evidence_kind="FINAL_SUBMISSION_VERSION",
                        object_type="DocumentEvidenceVersion",
                        object_id=resolved_evidence.evidence_version_id,
                        content_hash=resolved_evidence.content_hash,
                        captured_at=resolved_evidence.reviewed_at,
                    ),
                    EvidenceReference(
                        case_id=resolved_evidence.case_id,
                        evidence_kind="MANUAL_EXTERNAL_SUBMISSION_RECORD",
                        object_type="CaseActivityEvent",
                        object_id=resolved_evidence.submission_activity_id,
                        content_hash=resolved_evidence.submission_activity_hash,
                        captured_at=occurred_at,
                    ),
                ),
                actor_id=actor_id,
                idempotency_key=lifecycle_idempotency_key,
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload={},
            ),
            db,
        )
        if (
            lifecycle_result.case_id != resolved_evidence.case_id
            or lifecycle_result.activity_id == finalized.activity_id
            or lifecycle_result.sequence != finalized.activity_sequence + 1
            or lifecycle_result.lifecycle_revision != finalized.lifecycle_revision + 1
            or lifecycle_result.lane is not ActivityLane.LIFECYCLE
            or lifecycle_result.event_type != "FILING_EXTERNAL_SUBMISSION_RECORDED"
            or lifecycle_result.confirmation_status is not ConfirmationStatus.CONFIRMED
            or lifecycle_result.idempotency_key != lifecycle_idempotency_key
            or lifecycle_result.reused is not is_replay
        ):
            raise_business_error(
                "FILING_FINAL_EVIDENCE_CONFLICT",
                "Lifecycle result conflicts with the filing submission evidence",
                status_code=409,
            )

        evidence_parts = [f"occurred_at={occurred_at.isoformat()}"]
        normalized_note = _normalize_text(note)
        if normalized_note:
            evidence_parts.append(f"note={normalized_note}")
        checklist = _upsert_checklist(
            db,
            package_id=package_id,
            section_code="OFFICIAL_PAGE",
            item_code=normalized_operation,
            item_label=normalized_operation,
            status="DONE",
            required=True,
            evidence_note="; ".join(evidence_parts),
        )
        db.commit()
        db.refresh(checklist)
        return checklist

    evidence_parts = [f"occurred_at={occurred_at.isoformat()}"]
    normalized_note = _normalize_text(note)
    if normalized_note:
        evidence_parts.append(f"note={normalized_note}")
    return update_filing_preparation_checklist(
        db,
        package_id=package_id,
        item_code=operation_code,
        status="DONE",
        evidence_note="; ".join(evidence_parts),
    )


def _document_extra_data(document: Document | None) -> dict[str, object]:
    if not document or not document.extra_data:
        return {}
    try:
        parsed = json.loads(document.extra_data)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _extra_text(extra_data: dict[str, object], *keys: str) -> str | None:
    for key in keys:
        value = extra_data.get(key)
        if isinstance(value, str):
            normalized = _normalize_text(value)
            if normalized:
                return normalized
    return None


def _extra_bool(extra_data: dict[str, object], key: str) -> bool:
    value = extra_data.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "是"}
    return False


def _parse_date_value(value: object) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _extra_date(extra_data: dict[str, object], *keys: str) -> date | None:
    for key in keys:
        parsed = _parse_date_value(extra_data.get(key))
        if parsed:
            return parsed
    return None


def _document_template_code(db: Session, document: Document | None) -> str | None:
    if not document or not document.doc_template_id:
        return None
    doc_template = db.execute(
        select(DocTemplate).where(DocTemplate.id == document.doc_template_id)
    ).scalar_one_or_none()
    return doc_template.code if doc_template else None


def _oa_document_out(db: Session, document: Document | None) -> OaReplyDocumentOut | None:
    if not document:
        return None
    return OaReplyDocumentOut(
        id=document.id,
        title=document.title,
        template_code=_document_template_code(db, document),
        direction=str(document.direction),
        doc_date=document.doc_date,
        ref_no=document.ref_no,
        reply_to_id=document.reply_to_id,
        need_reply=document.need_reply,
        reply_date=document.reply_date,
    )


def _first_applicant_display(db: Session, *, case_id: str) -> str | None:
    applicant = db.execute(
        select(T_CaseApplicant)
        .where(T_CaseApplicant.case_id == case_id)
        .order_by(T_CaseApplicant.is_first.desc(), T_CaseApplicant.seq.asc())
    ).scalar_one_or_none()
    if not applicant:
        return None
    return _normalize_text(applicant.name_cn) or _normalize_text(applicant.name_en)


def _source_reply_task(db: Session, *, source_document_id: str | None) -> Task | None:
    if not source_document_id:
        return None
    return db.execute(
        select(Task)
        .where(Task.document_id == source_document_id)
        .order_by(Task.due_date.asc(), Task.id.asc())
    ).scalar_one_or_none()


def _require_oa_documents(
    db: Session,
    *,
    package: OfficialWorkPackage,
) -> tuple[Document | None, Document | None]:
    source = _get_document(db, package.source_document_id) if package.source_document_id else None
    reply = _get_document(db, package.reply_document_id) if package.reply_document_id else None
    return source, reply


def _oa_attachment_lookup(attachments: list[DocAttachment]) -> dict[str, list[DocAttachment]]:
    by_role: dict[str, list[DocAttachment]] = {}
    for attachment in attachments:
        role = _normalize_code(getattr(attachment, "official_file_role", None))
        if role:
            by_role.setdefault(role, []).append(attachment)
    return by_role


def _oa_attachment_out(role: str, attachment: DocAttachment | None) -> OaReplyAttachmentOut:
    return OaReplyAttachmentOut(
        role=role,
        status="PRESENT" if attachment else "MISSING",
        attachment_id=attachment.id if attachment else None,
        file_name=attachment.file_name if attachment else None,
        external_upload_position=attachment.external_upload_position if attachment else None,
    )


def _oa_reply_status(source: Document | None, reply: Document | None) -> str:
    if not source:
        return "SOURCE_MISSING"
    if source.reply_date:
        return "REPLIED"
    if reply:
        return "REPLY_DOCUMENT_LINKED"
    return "WAITING_REPLY_DOCUMENT"


def _oa_atomic_link_conflict(message: str) -> None:
    raise_business_error(
        "OA_REPLY_IDENTITY_CONFLICT",
        message,
        status_code=409,
    )


def _oa_evidence_result(version: DocumentEvidenceVersion) -> EvidenceVersionResult:
    try:
        role = EvidenceRole(version.role)
        state = EvidenceVersionState(version.state)
        review_state = EvidenceReviewState(version.review_state)
    except (TypeError, ValueError):
        _oa_atomic_link_conflict("OA reply attachment evidence identity is invalid")
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


def prepare_oa_out_package_link(
    db: Session,
    *,
    reply_document: Document,
    actor_id: str,
) -> OaReplyPackageResult:
    packages = list(
        db.scalars(
            select(OfficialWorkPackage).where(
                OfficialWorkPackage.source_document_id == reply_document.reply_to_id,
                OfficialWorkPackage.package_kind == "OA_REPLY",
            )
        )
    )
    if len(packages) != 1:
        _oa_atomic_link_conflict("OA reply package identity is not unique")
    package = packages[0]

    source_versions = list(
        db.scalars(
            select(DocumentEvidenceVersion).where(
                DocumentEvidenceVersion.case_id == reply_document.case_id,
                DocumentEvidenceVersion.document_id == package.source_document_id,
                DocumentEvidenceVersion.current_identity_key.is_not(None),
            )
        )
    )
    if len(source_versions) != 1:
        _oa_atomic_link_conflict("Source OA notice evidence identity is not unique")
    source_version = source_versions[0]

    reply_attachments = list(
        db.scalars(select(DocAttachment).where(DocAttachment.document_id == reply_document.id))
    )
    if len(reply_attachments) != 1:
        _oa_atomic_link_conflict("OA reply attachment identity is not unique")
    reply_attachment = reply_attachments[0]

    manifests = list(
        db.scalars(
            select(OfficialWorkPackageManifest).where(
                OfficialWorkPackageManifest.package_id == package.id,
                OfficialWorkPackageManifest.official_file_role.in_(_COPYABLE_OA_ATTACHMENT_ROLES),
                OfficialWorkPackageManifest.present.is_(True),
            )
        )
    )
    selected: list[CopyableOaAttachmentEvidence] = []
    for manifest in manifests:
        if not manifest.evidence_version_id:
            _oa_atomic_link_conflict("OA reply manifest evidence identity is missing")
        version = db.get(DocumentEvidenceVersion, manifest.evidence_version_id)
        if version is None:
            _oa_atomic_link_conflict("OA reply manifest evidence identity is missing")
        selected.append(
            CopyableOaAttachmentEvidence(
                evidence_version=_oa_evidence_result(version),
                manifest_id=manifest.id,
                manifest_case_id=package.case_id,
                manifest_package_id=package.id,
                manifest_role=manifest.official_file_role,
                manifest_evidence_version_id=manifest.evidence_version_id,
                manifest_content_hash=manifest.content_hash,
            )
        )

    return prepare_oa_reply(
        PrepareOaReplyCommand(
            case_id=reply_document.case_id,
            source_document_id=package.source_document_id,
            source_evidence_version_id=source_version.id,
            package_id=package.id,
            reply_document_id=reply_document.id,
            reply_attachment_id=reply_attachment.id,
            reply_content_hash=reply_attachment.content_hash,
            actor_id=actor_id,
            attachments=tuple(selected),
        ),
        db,
    )


def _oa_manifest_roles(
    db: Session,
    *,
    package: OfficialWorkPackage,
    reply_document: Document | None,
) -> None:
    attachments = (
        db.execute(
            select(DocAttachment)
            .where(DocAttachment.document_id == reply_document.id)
            .order_by(DocAttachment.created_at.asc(), DocAttachment.id.asc())
        )
        .scalars()
        .all()
        if reply_document
        else []
    )
    summary = summarize_attachment_manifest(list(attachments))
    items_by_role: dict[str, list] = {}
    for item in summary.oa_roles:
        if item.official_file_role:
            items_by_role.setdefault(item.official_file_role, []).append(item)
    attachments_by_id = {attachment.id: attachment for attachment in attachments}
    desired_roles = [
        ("OA_STATEMENT_WORD", True, 10, "意见陈述 Word 源文件"),
        ("OA_STATEMENT_PDF", True, 20, "PDF 保真附件"),
        ("OA_MODIFIED_CLAIMS", True, 30, "修改后的权利要求书"),
        ("OA_AMENDMENT_COMPARISON", False, 40, "修改对照页"),
        ("OA_OTHER_PROOF", False, 50, "其他证明文件/实验数据"),
        ("OA_ADDITIONAL_FILE", False, 60, "附加文件"),
    ]
    for role, required, sort_order, note in desired_roles:
        items = items_by_role.get(role, [])
        if role in _MULTI_FILE_MANIFEST_ROLES:
            current_attachment_ids = {item.attachment_id for item in items}
            _prune_stale_multi_file_manifest_rows(
                db,
                package_id=package.id,
                role=role,
                current_attachment_ids=current_attachment_ids,
            )
            if items:
                for offset, item in enumerate(items):
                    attachment = attachments_by_id.get(item.attachment_id)
                    _upsert_manifest_role(
                        db,
                        package_id=package.id,
                        role=role,
                        required=required,
                        sort_order=sort_order + offset,
                        attachment=attachment,
                        external_upload_position=item.external_upload_position,
                        note=note,
                    )
            else:
                _upsert_manifest_role(
                    db,
                    package_id=package.id,
                    role=role,
                    required=required,
                    sort_order=sort_order,
                    note=note,
                )
            continue

        item = next(iter(items), None)
        attachment = attachments_by_id.get(item.attachment_id) if item else None
        _upsert_manifest_role(
            db,
            package_id=package.id,
            role=role,
            required=required,
            sort_order=sort_order,
            attachment=attachment,
            external_upload_position=item.external_upload_position if item else None,
            note=note,
        )


def _oa_checklist_defaults(db: Session, *, package_id: str) -> None:
    defaults = [
        ("OA_REPLY", "STATEMENT_TEXT_CONFIRMED", "陈述意见文本已确认", 10),
        ("OA_REPLY", "PDF_FIDELITY_CONFIRMED", "PDF 保真附件已确认", 20),
        ("OA_REPLY", "MODIFIED_CLAIMS_CONFIRMED", "修改文件已确认", 30),
        ("OA_REPLY", "EXPERIMENT_DATA_FLAG_CONFIRMED", "补交实验数据勾选已确认", 40),
        ("OFFICIAL_PAGE", "PREVIEW_CONFIRMED", "官方页面预览已确认", 50),
        ("OFFICIAL_PAGE", "SIGNATURE_CONFIRMED", "签名/提交由人工完成", 60),
    ]
    for section_code, item_code, item_label, sort_order in defaults:
        _upsert_checklist(
            db,
            package_id=package_id,
            section_code=section_code,
            item_code=item_code,
            item_label=item_label,
            status="PENDING",
            required=True,
            sort_order=sort_order,
        )


def ensure_oa_reply_package(
    db: Session,
    *,
    source_document_id: str,
) -> OaReplyPackageOut:
    source = _get_document(db, source_document_id)
    resolve_key = f"OA_REPLY:{source.id}"
    existing = (
        db.execute(
            select(OfficialWorkPackage)
            .where(
                OfficialWorkPackage.source_document_id == source.id,
                OfficialWorkPackage.package_kind == "OA_REPLY",
            )
            .order_by(OfficialWorkPackage.created_at.asc(), OfficialWorkPackage.id.asc())
        )
        .scalars()
        .all()
    )
    if existing and (
        len(existing) != 1
        or existing[0].case_id != source.case_id
        or existing[0].resolve_key != resolve_key
    ):
        raise_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            "OA reply package identity is inconsistent",
            details={
                "source_document_id": source.id,
                "expected_case_id": source.case_id,
                "expected_resolve_key": resolve_key,
                "packages": [
                    {
                        "id": package.id,
                        "case_id": package.case_id,
                        "resolve_key": package.resolve_key,
                    }
                    for package in existing
                ],
            },
            status_code=409,
        )
    if _normalize_code(source.direction) != "IN":
        raise_business_error(
            "OA_REPLY_SOURCE_DIRECTION_INVALID",
            "OA reply package source must be an incoming document",
            details={"source_document_id": source.id, "direction": source.direction},
            status_code=400,
        )

    template = (
        db.execute(select(DocTemplate).where(DocTemplate.id == source.doc_template_id))
        .scalars()
        .one_or_none()
        if source.doc_template_id
        else None
    )
    semantics = resolve_document_semantics(template)
    expected_case_status = _normalize_code(semantics.case_status_effect)
    if (
        semantics.catalog_status != "EXECUTABLE"
        or semantics.execution_behavior != "OA_REPLY"
        or expected_case_status not in {"OA1", "OA2"}
    ):
        raise_business_error(
            "OA_REPLY_SOURCE_SEMANTICS_INVALID",
            "Document does not have executable OA reply semantics",
            details={
                "source_document_id": source.id,
                "catalog_status": semantics.catalog_status,
                "execution_behavior": semantics.execution_behavior,
                "case_status_effect": semantics.case_status_effect,
            },
            status_code=409,
        )

    if existing:
        return get_oa_reply_package(db, package_id=existing[0].id)

    case = _get_case(db, source.case_id)
    if _normalize_code(case.status) != expected_case_status:
        raise_business_error(
            "OA_REPLY_CASE_STATE_INVALID",
            "OA reply package case state does not match the source document semantics",
            details={
                "source_document_id": source.id,
                "case_id": case.id,
                "case_status": case.status,
                "expected_case_status": expected_case_status,
            },
            status_code=409,
        )

    package = OfficialWorkPackage(
        id=str(uuid4()),
        case_id=case.id,
        package_kind="OA_REPLY",
        status="PREPARING",
        source_document_id=source.id,
        resolve_key=resolve_key,
    )
    db.add(package)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        winner = db.execute(
            select(OfficialWorkPackage).where(
                OfficialWorkPackage.resolve_key == resolve_key,
                OfficialWorkPackage.case_id == source.case_id,
                OfficialWorkPackage.package_kind == "OA_REPLY",
                OfficialWorkPackage.source_document_id == source.id,
            )
        ).scalar_one_or_none()
        if winner:
            return get_oa_reply_package(db, package_id=winner.id)
        raise_business_error(
            "OA_REPLY_IDENTITY_CONFLICT",
            "OA reply package identity is inconsistent",
            details={
                "source_document_id": source.id,
                "expected_case_id": source.case_id,
                "expected_resolve_key": resolve_key,
            },
            status_code=409,
        )
    return refresh_oa_reply_package(db, package_id=package.id)


def get_oa_reply_package(
    db: Session,
    *,
    package_id: str,
) -> OaReplyPackageOut:
    package = _get_package(db, package_id)
    _require_oa_package(package)
    case = _get_case(db, package.case_id)
    source, reply = _require_oa_documents(db, package=package)
    source_extra = _document_extra_data(source)
    reply_extra = _document_extra_data(reply)
    task = _source_reply_task(db, source_document_id=package.source_document_id)

    reply_attachments = (
        db.execute(
            select(DocAttachment)
            .where(DocAttachment.document_id == reply.id)
            .order_by(DocAttachment.created_at.asc(), DocAttachment.id.asc())
        )
        .scalars()
        .all()
        if reply
        else []
    )
    attachments_by_role = _oa_attachment_lookup(list(reply_attachments))
    manifests = (
        db.execute(
            select(OfficialWorkPackageManifest)
            .where(OfficialWorkPackageManifest.package_id == package_id)
            .order_by(OfficialWorkPackageManifest.sort_order.asc())
        )
        .scalars()
        .all()
    )
    checklists = (
        db.execute(
            select(OfficialWorkPackageChecklist)
            .where(OfficialWorkPackageChecklist.package_id == package_id)
            .order_by(
                OfficialWorkPackageChecklist.sort_order.asc(), OfficialWorkPackageChecklist.id.asc()
            )
        )
        .scalars()
        .all()
    )

    official_due_date = _extra_date(
        source_extra,
        "official_due_date",
        "OfficialDueDate",
        "reply_due_date",
    ) or (task.due_date if task else None)
    issue_date = _extra_date(source_extra, "issue_date") or (source.doc_date if source else None)

    return OaReplyPackageOut(
        package=_package_out(package),
        source_document=_oa_document_out(db, source),
        reply_document=_oa_document_out(db, reply),
        application_no=case.app_no,
        applicant_display=_first_applicant_display(db, case_id=case.id),
        notice_code=_extra_text(source_extra, "official_notice_code", "notice_code")
        or (source.ref_no if source else None),
        notice_name=_extra_text(source_extra, "official_notice_name", "notice_name")
        or (source.title if source else None),
        issue_sequence=_extra_text(source_extra, "issue_sequence", "issue_no"),
        issue_date=issue_date,
        official_due_date=official_due_date,
        internal_due_date=task.internal_due_date if task else None,
        reply_status=_oa_reply_status(source, reply),
        statement_text=_extra_text(reply_extra, "reply_statement_text", "statement_text"),
        statement_word=_oa_attachment_out(
            "OA_STATEMENT_WORD",
            next(iter(attachments_by_role.get("OA_STATEMENT_WORD", [])), None),
        ),
        statement_pdf=_oa_attachment_out(
            "OA_STATEMENT_PDF",
            next(iter(attachments_by_role.get("OA_STATEMENT_PDF", [])), None),
        ),
        modified_claim_files=[
            _oa_attachment_out("OA_MODIFIED_CLAIMS", attachment)
            for attachment in attachments_by_role.get("OA_MODIFIED_CLAIMS", [])
        ],
        comparison_page=_oa_attachment_out(
            "OA_AMENDMENT_COMPARISON",
            next(iter(attachments_by_role.get("OA_AMENDMENT_COMPARISON", [])), None),
        ),
        proof_files=[
            _oa_attachment_out(role, attachment)
            for role in ("OA_OTHER_PROOF", "OA_ADDITIONAL_FILE")
            for attachment in attachments_by_role.get(role, [])
        ],
        experiment_data_submitted=_extra_bool(reply_extra, "experiment_data_submitted"),
        official_page_checklist=[_checklist_out(checklist) for checklist in checklists],
        oa_file_roles=[_manifest_out(manifest) for manifest in manifests],
    )


def refresh_oa_reply_package(
    db: Session,
    *,
    package_id: str,
    experiment_data_submitted: bool | None = None,
) -> OaReplyPackageOut:
    package = _get_package(db, package_id)
    _require_oa_package(package)
    _, reply = _require_oa_documents(db, package=package)
    if experiment_data_submitted is not None and reply:
        extra_data = _document_extra_data(reply)
        extra_data["experiment_data_submitted"] = experiment_data_submitted
        reply.extra_data = json.dumps(extra_data, ensure_ascii=False)
    _oa_manifest_roles(db, package=package, reply_document=reply)
    _oa_checklist_defaults(db, package_id=package.id)
    package.status = "NEEDS_MAINTENANCE"
    db.commit()
    return get_oa_reply_package(db, package_id=package_id)


def update_oa_reply_checklist(
    db: Session,
    *,
    package_id: str,
    item_code: str,
    status: str,
    evidence_note: str | None = None,
) -> OfficialWorkPackageChecklist:
    package = _get_package(db, package_id)
    _require_oa_package(package)
    checklist = _upsert_checklist(
        db,
        package_id=package.id,
        section_code="OA_REPLY",
        item_code=_normalize_code(item_code) or item_code,
        item_label=item_code,
        status=status,
        required=True,
        evidence_note=evidence_note,
    )
    db.commit()
    db.refresh(checklist)
    return checklist


def link_oa_reply_document(
    db: Session,
    *,
    package_id: str,
    reply_document_id: str,
) -> OaReplyPackageOut:
    package = _get_package(db, package_id)
    _require_oa_package(package)
    reply = _get_document(db, reply_document_id)
    if reply.case_id != package.case_id:
        raise_business_error(
            "OA_REPLY_DOCUMENT_CASE_MISMATCH",
            "Reply document does not belong to the package case",
            status_code=400,
        )
    package.reply_document_id = reply.id
    if package.source_document_id:
        reply.reply_to_id = package.source_document_id
    db.commit()
    return get_oa_reply_package(db, package_id=package_id)


def _find_letter_mapping(
    db: Session,
    *,
    document: Document,
) -> FormatLetterMapping | None:
    template_code = _document_template_code(db, document)
    mappings = (
        db.execute(
            select(FormatLetterMapping)
            .where(FormatLetterMapping.enabled.is_(True))
            .order_by(FormatLetterMapping.created_at.asc(), FormatLetterMapping.id.asc())
        )
        .scalars()
        .all()
    )

    scored: list[tuple[int, FormatLetterMapping]] = []
    for mapping in mappings:
        score = 0
        if (
            document.doc_template_id
            and mapping.official_doc_template_id == document.doc_template_id
        ):
            score = max(score, 100)
        if template_code and _normalize_code(mapping.official_doc_template_code) == _normalize_code(
            template_code
        ):
            score = max(score, 80)
        pattern = _normalize_text(mapping.official_doc_name_pattern)
        if pattern and pattern in (document.title or ""):
            score = max(score, 60)
        if score:
            scored.append((score, mapping))

    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def _letter_mapping_out(mapping: FormatLetterMapping | None) -> LetterHandoffMappingOut | None:
    if not mapping:
        return None
    return LetterHandoffMappingOut(
        id=mapping.id,
        format_letter_template_id=mapping.format_letter_template_id,
        format_letter_template_code=mapping.format_letter_template_code,
        output_name_rule=mapping.output_name_rule,
        contact_rule_code=mapping.contact_rule_code,
        salutation_rule_code=mapping.salutation_rule_code,
    )


def _letter_template_ready(db: Session, mapping: FormatLetterMapping | None) -> bool:
    if not mapping:
        return False
    if mapping.format_letter_template_id:
        template = db.execute(
            select(Template).where(
                Template.id == mapping.format_letter_template_id,
                Template.enabled.is_(True),
            )
        ).scalar_one_or_none()
        return bool(template)
    return bool(_normalize_text(mapping.format_letter_template_code))


def _select_letter_contact(
    db: Session,
    *,
    case: Case,
    mapping: FormatLetterMapping | None,
) -> tuple[ClientContact | None, str]:
    if (
        not mapping
        or _normalize_code(mapping.contact_rule_code) != "CLIENT_PRIMARY_CONTACT"
        or not case.client_id
    ):
        return None, "UNCONFIRMED"
    contact = db.execute(
        select(ClientContact)
        .where(ClientContact.client_id == case.client_id)
        .order_by(ClientContact.is_primary.desc(), ClientContact.created_at.asc())
    ).scalar_one_or_none()
    return contact, "CLIENT_PRIMARY_CONTACT" if contact else "CLIENT_PRIMARY_CONTACT_MISSING"


def _letter_contact_out(contact: ClientContact | None) -> LetterHandoffContactOut | None:
    if not contact:
        return None
    return LetterHandoffContactOut(
        id=contact.id,
        contact_name=contact.contact_name,
        title=contact.title,
        email=contact.email,
    )


def _letter_salutation(
    *,
    contact: ClientContact | None,
    mapping: FormatLetterMapping | None,
) -> tuple[str, str]:
    if (
        contact
        and mapping
        and _normalize_code(mapping.salutation_rule_code) == "PRIMARY_CONTACT_TITLE"
    ):
        title = _normalize_text(contact.title) or ""
        return f"{contact.contact_name}{title}：您好", "PRIMARY_CONTACT_TITLE"
    return "尊敬的：您好", "DEFAULT"


def _letter_first_applicant_name(db: Session, *, case: Case) -> str:
    """First applicant display name for letter filenames (信函生成 P0004)."""
    first_applicant = (
        db.execute(
            select(T_CaseApplicant)
            .where(T_CaseApplicant.case_id == case.id)
            .order_by(T_CaseApplicant.seq.asc())
        )
        .scalars()
        .first()
    )
    if first_applicant is None:
        return ""
    return (
        _normalize_text(first_applicant.name_cn) or _normalize_text(first_applicant.name_en) or ""
    )


def _letter_output_filename(
    db: Session,
    *,
    case: Case,
    document: Document,
    mapping: FormatLetterMapping | None,
) -> str:
    applicant_name = _letter_first_applicant_name(db, case=case)
    # 客户口径（信函生成操作 P0004）：{案号}-给{申请人名称}的邮件.docx
    if applicant_name:
        default_name = f"{case.case_no}-给{applicant_name}的邮件.docx"
    else:
        default_name = f"{case.case_no}-格式函.docx"
    rule = _normalize_text(mapping.output_name_rule if mapping else None)
    if not rule:
        return default_name
    try:
        return rule.format(
            case_no=case.case_no,
            app_no=case.app_no or "",
            document_title=document.title or "",
            applicant_name=applicant_name,
        )
    except (KeyError, ValueError):
        return default_name


def _letter_preview_attachments(
    db: Session,
    *,
    source_document_id: str,
    generated_word_path: str | None,
) -> list[LetterHandoffPreviewAttachmentOut]:
    attachments: list[LetterHandoffPreviewAttachmentOut] = []
    if generated_word_path:
        attachments.append(
            LetterHandoffPreviewAttachmentOut(
                file_name=generated_word_path.rsplit("/", 1)[-1],
                file_path=generated_word_path,
                attachment_role="FORMAT_LETTER_WORD",
                required=True,
                included=True,
                sort_order=1,
            )
        )
    source_attachments = (
        db.execute(
            select(DocAttachment)
            .where(DocAttachment.document_id == source_document_id)
            .order_by(DocAttachment.created_at.asc(), DocAttachment.id.asc())
        )
        .scalars()
        .all()
    )
    for index, attachment in enumerate(source_attachments, start=2):
        attachments.append(
            LetterHandoffPreviewAttachmentOut(
                attachment_id=attachment.id,
                file_name=attachment.file_name,
                file_path=attachment.file_path,
                attachment_role="SOURCE_OFFICIAL_DOCUMENT",
                required=True,
                included=True,
                sort_order=index,
            )
        )
    return attachments


def get_letter_handoff_preview(
    db: Session,
    *,
    source_document_id: str,
) -> LetterHandoffPreviewOut:
    document = _get_document(db, source_document_id)
    case = _get_case(db, document.case_id)
    mapping = _find_letter_mapping(db, document=document)
    contact, contact_source = _select_letter_contact(db, case=case, mapping=mapping)
    salutation_text, salutation_source = _letter_salutation(contact=contact, mapping=mapping)
    template_ready = _letter_template_ready(db, mapping)
    generated_word_path = None
    if template_ready:
        output_filename = _letter_output_filename(db, case=case, document=document, mapping=mapping)
        generated_word_path = f"letters/{case.case_no}/{output_filename}"

    mail_subject = f"{case.case_no} {document.title or '官方来文'}"
    case_title = _normalize_text(case.title_cn) or _normalize_text(case.title_en) or case.case_no
    mail_body_draft = (
        f"{salutation_text}\n\n请查收{case_title}相关{document.title or '官方来文'}及格式函附件。"
    )

    return LetterHandoffPreviewOut(
        source_document_id=document.id,
        case_id=case.id,
        case_no=case.case_no,
        mapping=_letter_mapping_out(mapping),
        template_status="READY" if template_ready else "PENDING_TEMPLATE",
        client_contact_id=contact.id if contact else None,
        contact=_letter_contact_out(contact),
        contact_selection_source=contact_source,
        salutation_source=salutation_source,
        salutation_text=salutation_text,
        generated_word_path=generated_word_path,
        mail_subject=mail_subject,
        mail_body_draft=mail_body_draft,
        attachments=_letter_preview_attachments(
            db,
            source_document_id=document.id,
            generated_word_path=generated_word_path,
        ),
    )


def _letter_handoff_payload(preview: LetterHandoffPreviewOut) -> str:
    return json.dumps(
        {
            "source_document_id": preview.source_document_id,
            "mail_subject": preview.mail_subject,
            "generated_word_path": preview.generated_word_path,
            "attachments": [
                {
                    "file_name": attachment.file_name,
                    "file_path": attachment.file_path,
                    "attachment_role": attachment.attachment_role,
                }
                for attachment in preview.attachments
                if attachment.included
            ],
        },
        ensure_ascii=False,
    )


def _letter_handoff_out(
    db: Session,
    *,
    handoff: LetterHandoff,
) -> LetterHandoffOut:
    attachments = (
        db.execute(
            select(LetterHandoffAttachment)
            .where(LetterHandoffAttachment.handoff_id == handoff.id)
            .order_by(LetterHandoffAttachment.sort_order.asc(), LetterHandoffAttachment.id.asc())
        )
        .scalars()
        .all()
    )
    return LetterHandoffOut(
        id=handoff.id,
        source_document_id=handoff.source_document_id,
        generated_document_id=handoff.generated_document_id,
        format_letter_mapping_id=handoff.format_letter_mapping_id,
        format_letter_template_id=handoff.format_letter_template_id,
        client_contact_id=handoff.client_contact_id,
        contact_selection_source=handoff.contact_selection_source,
        salutation_source=handoff.salutation_source,
        salutation_text=handoff.salutation_text,
        generated_word_path=handoff.generated_word_path,
        mail_subject=handoff.mail_subject,
        mail_body_draft=handoff.mail_body_draft,
        longxia_handoff_status=handoff.longxia_handoff_status,
        longxia_handoff_payload=handoff.longxia_handoff_payload,
        handoff_at=handoff.handoff_at,
        remark=handoff.remark,
        attachments=[
            LetterHandoffAttachmentOut(
                id=attachment.id,
                handoff_id=attachment.handoff_id,
                attachment_id=attachment.attachment_id,
                file_name=attachment.file_name,
                file_path=attachment.file_path,
                attachment_role=attachment.attachment_role,
                required=attachment.required,
                included=attachment.included,
                sort_order=attachment.sort_order,
            )
            for attachment in attachments
        ],
    )


def prepare_letter_handoff(
    db: Session,
    *,
    source_document_id: str,
    remark: str | None = None,
) -> LetterHandoffResultOut:
    preview = get_letter_handoff_preview(db, source_document_id=source_document_id)
    handoff = LetterHandoff(
        id=str(uuid4()),
        source_document_id=preview.source_document_id,
        format_letter_mapping_id=preview.mapping.id if preview.mapping else None,
        format_letter_template_id=preview.mapping.format_letter_template_id
        if preview.mapping
        else None,
        client_contact_id=preview.client_contact_id,
        contact_selection_source=preview.contact_selection_source,
        salutation_source=preview.salutation_source,
        salutation_text=preview.salutation_text,
        generated_word_path=preview.generated_word_path,
        mail_subject=preview.mail_subject,
        mail_body_draft=preview.mail_body_draft,
        longxia_handoff_status="READY" if preview.template_status == "READY" else "PENDING",
        longxia_handoff_payload=_letter_handoff_payload(preview),
        remark=remark,
    )
    db.add(handoff)
    db.flush()
    for attachment in preview.attachments:
        db.add(
            LetterHandoffAttachment(
                id=str(uuid4()),
                handoff_id=handoff.id,
                attachment_id=attachment.attachment_id,
                file_name=attachment.file_name,
                file_path=attachment.file_path,
                attachment_role=attachment.attachment_role,
                required=attachment.required,
                included=attachment.included,
                sort_order=attachment.sort_order,
            )
        )
    db.commit()
    return LetterHandoffResultOut(
        preview=preview,
        handoff=_letter_handoff_out(db, handoff=handoff),
    )


def _get_letter_handoff(db: Session, handoff_id: str) -> LetterHandoff:
    handoff = db.execute(
        select(LetterHandoff).where(LetterHandoff.id == handoff_id)
    ).scalar_one_or_none()
    if not handoff:
        raise_business_error(
            "LETTER_HANDOFF_NOT_FOUND",
            "Letter handoff not found",
            status_code=404,
        )
    return handoff


def record_letter_handoff_status(
    db: Session,
    *,
    source_document_id: str,
    handoff_id: str,
    longxia_handoff_status: str,
    longxia_handoff_payload: str | None = None,
    handoff_at: datetime | None = None,
) -> LetterHandoffResultOut:
    handoff = _get_letter_handoff(db, handoff_id)
    if handoff.source_document_id != source_document_id:
        raise_business_error(
            "LETTER_HANDOFF_SOURCE_MISMATCH",
            "Letter handoff does not belong to the source document",
            status_code=400,
        )
    handoff.longxia_handoff_status = _normalize_code(longxia_handoff_status) or "PENDING"
    if longxia_handoff_payload is not None:
        handoff.longxia_handoff_payload = longxia_handoff_payload
    if handoff_at is not None:
        handoff.handoff_at = handoff_at
    db.commit()
    return LetterHandoffResultOut(
        preview=None,
        handoff=_letter_handoff_out(db, handoff=handoff),
    )


def evaluate_official_work_package(
    db: Session,
    *,
    package_id: str,
) -> OfficialWorkPackageStatusEvaluationOut:
    package = _get_package(db, package_id)
    checklists = (
        db.execute(
            select(OfficialWorkPackageChecklist).where(
                OfficialWorkPackageChecklist.package_id == package_id
            )
        )
        .scalars()
        .all()
    )
    manifests = (
        db.execute(
            select(OfficialWorkPackageManifest).where(
                OfficialWorkPackageManifest.package_id == package_id
            )
        )
        .scalars()
        .all()
    )
    receipts = (
        db.execute(
            select(OfficialWorkPackageReceipt).where(
                OfficialWorkPackageReceipt.package_id == package_id
            )
        )
        .scalars()
        .all()
    )

    blockers: list[OfficialWorkPackageBlockerOut] = []
    for checklist in checklists:
        status = _normalize_code(checklist.status) or "PENDING"
        if checklist.required and status not in CHECKLIST_COMPLETE_STATUSES:
            blockers.append(
                OfficialWorkPackageBlockerOut(
                    blocker_type="CHECKLIST_INCOMPLETE",
                    item_code=checklist.item_code,
                    item_label=checklist.item_label,
                    status=_checklist_blocker_status(checklist),
                    message="Required checklist item is not complete",
                )
            )

    for manifest in manifests:
        if manifest.required and not manifest.present:
            blockers.append(
                OfficialWorkPackageBlockerOut(
                    blocker_type="MANIFEST_MISSING",
                    item_code=manifest.official_file_role,
                    item_label=manifest.source_role_alias,
                    status="NEEDS_MAINTENANCE",
                    message="Required package manifest file is missing",
                )
            )

    manifest_roles = {manifest.official_file_role for manifest in manifests}
    if (
        _normalize_code(package.package_kind) == "FILING_PREP"
        and "FILING_FULL_WORD" not in manifest_roles
    ):
        blockers.append(
            OfficialWorkPackageBlockerOut(
                blocker_type="MANIFEST_MISSING",
                item_code="FILING_FULL_WORD",
                item_label="FILING_FULL_WORD",
                status="NEEDS_MAINTENANCE",
                message="Required package manifest file is missing",
            )
        )

    receipt_hard_gate_satisfied = _has_archived_receipt(list(receipts))
    if not receipt_hard_gate_satisfied:
        blockers.append(
            OfficialWorkPackageBlockerOut(
                blocker_type="RECEIPT_MISSING",
                status="WAITING_RECEIPT",
                message="Receipt or archive evidence is required before archive",
            )
        )

    if any(blocker.status == "NEEDS_MAINTENANCE" for blocker in blockers):
        status = "NEEDS_MAINTENANCE"
    elif any(blocker.status == "NEEDS_CONFIRMATION" for blocker in blockers):
        status = "NEEDS_CONFIRMATION"
    elif any(blocker.blocker_type == "RECEIPT_MISSING" for blocker in blockers):
        status = "WAITING_RECEIPT"
    else:
        status = "ARCHIVED"

    return OfficialWorkPackageStatusEvaluationOut(
        package_id=package_id,
        status=status,
        can_archive=not blockers,
        receipt_hard_gate_satisfied=receipt_hard_gate_satisfied,
        blockers=blockers,
    )


def _filing_receipt_conflict(message: str) -> None:
    raise_business_error(
        "FILING_RECEIPT_EVIDENCE_CONFLICT",
        message,
        status_code=409,
    )


def _filing_receipt_attachment_hash(attachment: DocAttachment) -> str:
    file_path = _normalize_text(attachment.file_path)
    if not file_path:
        _filing_receipt_conflict("Receipt attachment path is missing")
    candidate = Path(file_path)
    backend_root = Path(__file__).resolve().parents[3]
    storage_root = (backend_root / "storage").resolve()
    if candidate.is_absolute():
        resolved = candidate
    elif file_path.startswith("storage/"):
        resolved = (backend_root / candidate).resolve()
    else:
        resolved = (storage_root / candidate).resolve()
    if not candidate.is_absolute():
        try:
            resolved.relative_to(storage_root)
        except ValueError:
            _filing_receipt_conflict("Receipt attachment path is invalid")
    try:
        content = resolved.read_bytes()
    except OSError:
        _filing_receipt_conflict("Receipt attachment bytes are unavailable")
    content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
    if attachment.content_hash != content_hash:
        _filing_receipt_conflict("Receipt attachment content hash is inconsistent")
    return content_hash


def _require_filing_submission_lifecycle_link(
    db: Session,
    *,
    package_id: str,
    case_id: str,
    evidence_version_id: str,
    evidence_content_hash: str,
    reviewed_at: datetime,
    submitted_at: datetime,
    submission_activity_id: str,
    submission_activity_hash: str,
) -> CaseActivityEvent:
    submission_activity = db.get(CaseActivityEvent, submission_activity_id)
    lifecycle_key = f"filing-external-lifecycle:{package_id}:{submitted_at.isoformat()}"
    lifecycle_activities = (
        db.execute(
            select(CaseActivityEvent)
            .where(
                CaseActivityEvent.case_id == case_id,
                CaseActivityEvent.idempotency_key == lifecycle_key,
            )
            .limit(2)
        )
        .scalars()
        .all()
    )
    if submission_activity is None or len(lifecycle_activities) != 1:
        _filing_receipt_conflict("Final filing submission lifecycle link is missing")
    lifecycle_activity = lifecycle_activities[0]
    evidence_links = (
        db.execute(
            select(CaseActivityEventEvidence)
            .where(CaseActivityEventEvidence.activity_id == lifecycle_activity.id)
            .order_by(CaseActivityEventEvidence.evidence_kind)
            .limit(3)
        )
        .scalars()
        .all()
    )
    exact_activity = (
        submission_activity.case_id == case_id
        and lifecycle_activity.case_id == case_id
        and lifecycle_activity.sequence == submission_activity.sequence + 1
        and lifecycle_activity.lane == ActivityLane.LIFECYCLE.value
        and lifecycle_activity.activity_type == "FILING_EXTERNAL_SUBMISSION_RECORDED"
        and lifecycle_activity.confirmation_status == ConfirmationStatus.CONFIRMED.value
        and lifecycle_activity.actor_id == submission_activity.actor_id
        and lifecycle_activity.effective_at == submitted_at
        and lifecycle_activity.occurred_at == submitted_at
        and lifecycle_activity.idempotency_key == lifecycle_key
        and lifecycle_activity.old_business_stage == BusinessStage.FILING_PREPARATION.value
        and lifecycle_activity.new_business_stage == BusinessStage.WAITING_EXTERNAL_RECEIPT.value
        and lifecycle_activity.old_official_procedure_stage
        == OfficialProcedureStage.NOT_SUBMITTED.value
        and lifecycle_activity.new_official_procedure_stage
        == OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT.value
        and lifecycle_activity.old_legal_status == LegalStatus.NOT_ESTABLISHED.value
        and lifecycle_activity.new_legal_status == LegalStatus.NOT_ESTABLISHED.value
    )
    exact_links = [
        (
            link.case_id,
            link.evidence_kind,
            link.object_type,
            link.object_id,
            link.content_hash,
            link.captured_at,
        )
        for link in evidence_links
    ] == [
        (
            case_id,
            "FINAL_SUBMISSION_VERSION",
            "DocumentEvidenceVersion",
            evidence_version_id,
            evidence_content_hash,
            reviewed_at,
        ),
        (
            case_id,
            "MANUAL_EXTERNAL_SUBMISSION_RECORD",
            "CaseActivityEvent",
            submission_activity_id,
            submission_activity_hash,
            submitted_at,
        ),
    ]
    if not exact_activity or not exact_links:
        _filing_receipt_conflict("Final filing submission lifecycle link is inconsistent")
    return lifecycle_activity


def record_official_work_package_receipt(
    db: Session,
    *,
    package_id: str,
    receipt_kind: str,
    receipt_attachment_id: str | None = None,
    receiving_case_no: str | None = None,
    submitter: str | None = None,
    received_at: datetime | None = None,
    received_file_list: str | None = None,
    archive_status: str = "PENDING",
    note: str | None = None,
    actor_id: str | None = None,
) -> OfficialWorkPackageReceipt:
    package = _get_package(db, package_id)
    case = _get_case(db, package.case_id)
    normalized_receipt_kind = _normalize_code(receipt_kind) or "RECEIPT_PDF"
    normalized_archive_status = _normalize_code(archive_status) or "PENDING"
    normalized_receiving_case_no = _normalize_text(receiving_case_no)
    normalized_submitter = _normalize_text(submitter)
    normalized_received_file_list = _normalize_text(received_file_list)
    normalized_note = _normalize_text(note)
    normalized_actor = _normalize_text(actor_id)
    if normalized_receipt_kind not in OFFICIAL_WORK_PACKAGE_RECEIPT_KINDS:
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_RECEIPT_KIND_INVALID",
            "Official work-package receipt kind is invalid",
            details={"receipt_kind": receipt_kind},
            status_code=400,
        )

    attachment = None
    if receipt_attachment_id:
        attachment = _get_attachment(db, receipt_attachment_id)
        attachment_document = _get_document(db, attachment.document_id)
        if attachment_document.case_id != package.case_id:
            raise_business_error(
                "OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH",
                "Receipt attachment belongs to another case",
                details={
                    "package_id": package.id,
                    "package_case_id": package.case_id,
                    "attachment_id": attachment.id,
                    "attachment_case_id": attachment_document.case_id,
                },
                status_code=400,
            )
        if (
            _normalize_code(package.package_kind) == "OA_REPLY"
            and attachment.document_id != package.reply_document_id
        ):
            manifest_id = db.execute(
                select(OfficialWorkPackageManifest.id)
                .where(
                    OfficialWorkPackageManifest.package_id == package.id,
                    OfficialWorkPackageManifest.attachment_id == attachment.id,
                    OfficialWorkPackageManifest.present.is_(True),
                )
                .limit(1)
            ).scalar_one_or_none()
            if manifest_id is None:
                raise_business_error(
                    "OA_RECEIPT_ATTACHMENT_SOURCE_INVALID",
                    "OA receipt attachment is not linked to the reply package",
                    details={
                        "package_id": package.id,
                        "reply_document_id": package.reply_document_id,
                        "attachment_id": attachment.id,
                        "attachment_document_id": attachment.document_id,
                    },
                    status_code=400,
                )

    receipt_candidates: list[OfficialWorkPackageReceipt] = []
    filing_archived = (
        _normalize_code(package.package_kind) == "FILING_PREP"
        and normalized_archive_status == "ARCHIVED"
    )
    if filing_archived and receipt_attachment_id is not None and received_at is not None:
        receipt_candidates = (
            db.execute(
                select(OfficialWorkPackageReceipt)
                .where(
                    OfficialWorkPackageReceipt.package_id == package.id,
                    OfficialWorkPackageReceipt.receipt_attachment_id == receipt_attachment_id,
                    OfficialWorkPackageReceipt.received_at == received_at,
                )
                .order_by(OfficialWorkPackageReceipt.id)
                .limit(2)
            )
            .scalars()
            .all()
        )
    legacy_projection = (
        case.business_stage is None
        and case.official_procedure_stage is None
        and case.legal_status is None
        and case.lifecycle_verification_status is None
        and case.lifecycle_revision is None
    )
    filing_lifecycle = filing_archived and (bool(receipt_candidates) or not legacy_projection)
    receipt_replay = bool(receipt_candidates)

    resolution = None
    receipt_content_hash = None
    prior_revision = case.lifecycle_revision
    if filing_lifecycle:
        _require_filing_package(package)
        if (
            attachment is None
            or received_at is None
            or received_at.tzinfo is not None
            or normalized_actor is None
        ):
            _filing_receipt_conflict("Archived filing receipt identity is incomplete")
        if len(receipt_candidates) > 1:
            _filing_receipt_conflict("Archived filing receipt identity is ambiguous")
        receipt_content_hash = _filing_receipt_attachment_hash(attachment)
        resolution = resolve_filing_final_evidence(package.id, db)
        if (
            resolution.final_submitted_at is None
            or resolution.submission_activity_id is None
            or resolution.submission_activity_hash is None
            or type(prior_revision) is not int
            or prior_revision < 0
        ):
            _filing_receipt_conflict("Final filing submission evidence is incomplete")
        submission_lifecycle = _require_filing_submission_lifecycle_link(
            db,
            package_id=package.id,
            case_id=package.case_id,
            evidence_version_id=resolution.evidence_version_id,
            evidence_content_hash=resolution.content_hash,
            reviewed_at=resolution.reviewed_at,
            submitted_at=resolution.final_submitted_at,
            submission_activity_id=resolution.submission_activity_id,
            submission_activity_hash=resolution.submission_activity_hash,
        )
        fresh_projection_matches = (
            case.status == CaseStatus.WAITING_RECEIPT.value
            and case.business_stage == BusinessStage.WAITING_EXTERNAL_RECEIPT.value
            and case.official_procedure_stage
            == OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT.value
            and case.legal_status == LegalStatus.NOT_ESTABLISHED.value
            and case.lifecycle_verification_status == ConfirmationStatus.CONFIRMED.value
            and prior_revision == submission_lifecycle.sequence
        )
        replay_projection_matches = (
            case.status == CaseStatus.WAITING_RECEIPT.value
            and case.business_stage == BusinessStage.PROSECUTION_MANAGEMENT.value
            and case.official_procedure_stage
            == OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE.value
            and case.legal_status == LegalStatus.APPLICATION_PENDING.value
            and case.lifecycle_verification_status == ConfirmationStatus.CONFIRMED.value
            and prior_revision == submission_lifecycle.sequence + 1
        )
        if not (
            (not receipt_replay and fresh_projection_matches)
            or (receipt_replay and replay_projection_matches)
        ):
            _filing_receipt_conflict("Case projection conflicts with the archived filing receipt")

    if receipt_replay:
        receipt = receipt_candidates[0]
        if (
            receipt.receipt_kind != normalized_receipt_kind
            or receipt.receiving_case_no != normalized_receiving_case_no
            or receipt.submitter != normalized_submitter
            or receipt.received_file_list != normalized_received_file_list
            or receipt.archive_status != normalized_archive_status
            or receipt.note != normalized_note
            or receipt.created_by != normalized_actor
            or receipt.updated_by != normalized_actor
        ):
            _filing_receipt_conflict("Archived filing receipt replay is inconsistent")
    else:
        receipt = OfficialWorkPackageReceipt(
            id=str(uuid4()),
            package_id=package_id,
            receipt_kind=normalized_receipt_kind,
            receipt_attachment_id=receipt_attachment_id,
            receiving_case_no=normalized_receiving_case_no,
            submitter=normalized_submitter,
            received_at=received_at,
            received_file_list=normalized_received_file_list,
            archive_status=normalized_archive_status,
            note=normalized_note,
            created_by=normalized_actor,
            updated_by=normalized_actor,
        )
        db.add(receipt)

    if receipt_attachment_id and filing_lifecycle and receipt_replay:
        if (
            attachment.is_archive_evidence is not True
            or attachment.is_receipt_evidence is not (normalized_receipt_kind != "MERGED_PDF")
            or attachment.updated_by != normalized_actor
        ):
            _filing_receipt_conflict("Archived filing receipt attachment state is inconsistent")
    elif receipt_attachment_id:
        attachment.is_archive_evidence = True
        attachment.is_receipt_evidence = normalized_receipt_kind != "MERGED_PDF"
        attachment.updated_by = normalized_actor
    db.flush()

    if filing_lifecycle:
        lifecycle_key = f"filing-receipt-archived:{receipt.id}"
        lifecycle_result = apply_lifecycle_event(
            LifecycleEventCommand(
                case_id=package.case_id,
                event_type="FILING_RECEIPT_ARCHIVED",
                lane=ActivityLane.LIFECYCLE,
                effective_at=received_at,
                occurred_at=received_at,
                evidence_refs=(
                    EvidenceReference(
                        case_id=package.case_id,
                        evidence_kind="FINAL_SUBMISSION_VERSION",
                        object_type="DocumentEvidenceVersion",
                        object_id=resolution.evidence_version_id,
                        content_hash=resolution.content_hash,
                        captured_at=resolution.reviewed_at,
                    ),
                    EvidenceReference(
                        case_id=package.case_id,
                        evidence_kind="VALID_FILING_RECEIPT",
                        object_type="OfficialWorkPackageReceipt",
                        object_id=receipt.id,
                        content_hash=receipt_content_hash,
                        captured_at=received_at,
                    ),
                ),
                actor_id=normalized_actor,
                idempotency_key=lifecycle_key,
                confirmation_status=ConfirmationStatus.CONFIRMED,
                payload={},
            ),
            db,
        )
        previous_projection = lifecycle_result.previous_projection
        current_projection = lifecycle_result.current_projection
        expected_revision = prior_revision if receipt_replay else prior_revision + 1
        exact_lifecycle = (
            lifecycle_result.case_id == package.case_id
            and lifecycle_result.activity_id != resolution.submission_activity_id
            and lifecycle_result.sequence == expected_revision
            and lifecycle_result.lifecycle_revision == expected_revision
            and lifecycle_result.lane is ActivityLane.LIFECYCLE
            and lifecycle_result.event_type == "FILING_RECEIPT_ARCHIVED"
            and lifecycle_result.confirmation_status is ConfirmationStatus.CONFIRMED
            and lifecycle_result.idempotency_key == lifecycle_key
            and lifecycle_result.reused is receipt_replay
            and lifecycle_result.legacy_case_status == CaseStatus.WAITING_RECEIPT.value
            and lifecycle_result.conflict_codes == ()
            and previous_projection.business_stage is BusinessStage.WAITING_EXTERNAL_RECEIPT
            and previous_projection.official_procedure_stage
            is OfficialProcedureStage.SUBMITTED_WAITING_RECEIPT
            and previous_projection.legal_status is LegalStatus.NOT_ESTABLISHED
            and previous_projection.lifecycle_verification_status is ConfirmationStatus.CONFIRMED
            and current_projection.business_stage is BusinessStage.PROSECUTION_MANAGEMENT
            and current_projection.official_procedure_stage
            is OfficialProcedureStage.SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE
            and current_projection.legal_status is LegalStatus.APPLICATION_PENDING
            and current_projection.lifecycle_verification_status is ConfirmationStatus.CONFIRMED
        )
        if not exact_lifecycle:
            _filing_receipt_conflict("Lifecycle result conflicts with the archived filing receipt")

    db.commit()
    return receipt


def _raise_oa_receipt_archive_evidence_invalid(
    *,
    package: OfficialWorkPackage,
    receipt: OfficialWorkPackageReceipt,
    reason: str,
    attachment_id: str | None = None,
) -> None:
    raise_business_error(
        "OA_RECEIPT_ARCHIVE_EVIDENCE_INVALID",
        "OA receipt archive evidence is invalid",
        details={
            "package_id": package.id,
            "receipt_id": receipt.id,
            "attachment_id": attachment_id or receipt.receipt_attachment_id,
            "reason": reason,
        },
        status_code=409,
    )


def _revalidate_oa_archived_receipts(
    db: Session,
    *,
    package: OfficialWorkPackage,
) -> list[str]:
    archived_receipts = [
        receipt
        for receipt in (
            db.execute(
                select(OfficialWorkPackageReceipt)
                .where(OfficialWorkPackageReceipt.package_id == package.id)
                .order_by(
                    OfficialWorkPackageReceipt.created_at.asc(),
                    OfficialWorkPackageReceipt.id.asc(),
                )
            )
            .scalars()
            .all()
        )
        if _normalize_code(receipt.archive_status) in RECEIPT_ARCHIVED_STATUSES
    ]
    if not archived_receipts:
        raise_business_error(
            "OA_RECEIPT_ARCHIVE_EVIDENCE_INVALID",
            "OA receipt archive evidence is missing",
            details={"package_id": package.id, "reason": "ARCHIVED_RECEIPT_MISSING"},
            status_code=409,
        )

    receipt_ids: list[str] = []
    for receipt in archived_receipts:
        if not receipt.receipt_attachment_id:
            _raise_oa_receipt_archive_evidence_invalid(
                package=package,
                receipt=receipt,
                reason="RECEIPT_ATTACHMENT_MISSING",
            )
        attachment = db.execute(
            select(DocAttachment).where(DocAttachment.id == receipt.receipt_attachment_id)
        ).scalar_one_or_none()
        if attachment is None:
            _raise_oa_receipt_archive_evidence_invalid(
                package=package,
                receipt=receipt,
                reason="RECEIPT_ATTACHMENT_NOT_FOUND",
            )
        attachment_document = db.execute(
            select(Document).where(Document.id == attachment.document_id)
        ).scalar_one_or_none()
        if attachment_document is None:
            _raise_oa_receipt_archive_evidence_invalid(
                package=package,
                receipt=receipt,
                attachment_id=attachment.id,
                reason="RECEIPT_DOCUMENT_NOT_FOUND",
            )
        if attachment_document.case_id != package.case_id:
            _raise_oa_receipt_archive_evidence_invalid(
                package=package,
                receipt=receipt,
                attachment_id=attachment.id,
                reason="RECEIPT_CASE_MISMATCH",
            )
        if attachment.document_id != package.reply_document_id:
            manifest_id = db.execute(
                select(OfficialWorkPackageManifest.id)
                .where(
                    OfficialWorkPackageManifest.package_id == package.id,
                    OfficialWorkPackageManifest.attachment_id == attachment.id,
                    OfficialWorkPackageManifest.present.is_(True),
                )
                .limit(1)
            ).scalar_one_or_none()
            if manifest_id is None:
                _raise_oa_receipt_archive_evidence_invalid(
                    package=package,
                    receipt=receipt,
                    attachment_id=attachment.id,
                    reason="OA_RECEIPT_SOURCE_INVALID",
                )
        receipt_ids.append(receipt.id)
    return receipt_ids


def _prepare_oa_receipt_archive_event(
    db: Session,
    *,
    package: OfficialWorkPackage,
) -> tuple[Case, Document, Task, str, list[str]] | None:
    receipt_ids = _revalidate_oa_archived_receipts(db, package=package)
    if not package.source_document_id:
        return None

    source = db.execute(
        select(Document).where(Document.id == package.source_document_id)
    ).scalar_one_or_none()
    template = (
        db.execute(select(DocTemplate).where(DocTemplate.id == source.doc_template_id))
        .scalars()
        .one_or_none()
        if source and source.doc_template_id
        else None
    )
    semantics = resolve_document_semantics(template)
    expected_case_status = _normalize_code(semantics.case_status_effect)
    restore_status = _normalize_code(semantics.archive_status_restore)
    if (
        source is None
        or source.case_id != package.case_id
        or _normalize_code(source.direction) != "IN"
        or semantics.catalog_status != "EXECUTABLE"
        or semantics.execution_behavior != "OA_REPLY"
        or semantics.completion_event != "OFFICIAL_RECEIPT_ARCHIVED"
        or expected_case_status not in {"OA1", "OA2"}
        or restore_status != "SUB_EXAM"
        or not semantics.task_template_code
    ):
        raise_business_error(
            "OA_RECEIPT_ARCHIVE_SOURCE_INVALID",
            "OA receipt archive source semantics are invalid",
            details={
                "package_id": package.id,
                "source_document_id": package.source_document_id,
                "catalog_status": semantics.catalog_status,
                "execution_behavior": semantics.execution_behavior,
                "completion_event": semantics.completion_event,
                "case_status_effect": semantics.case_status_effect,
                "archive_status_restore": semantics.archive_status_restore,
            },
            status_code=409,
        )

    task_template_id = db.execute(
        select(TaskTemplate.id).where(TaskTemplate.code == semantics.task_template_code)
    ).scalar_one_or_none()
    matching_tasks = (
        db.execute(
            select(Task)
            .where(
                Task.case_id == package.case_id,
                Task.document_id == source.id,
                Task.task_template_id == task_template_id,
                Task.status == TaskStatus.OPEN.value,
            )
            .order_by(Task.created_at.asc(), Task.id.asc())
        )
        .scalars()
        .all()
        if task_template_id
        else []
    )
    if len(matching_tasks) != 1:
        raise_business_error(
            "OA_RECEIPT_ARCHIVE_TASK_MATCH_INVALID",
            "OA receipt archive requires exactly one matching open task",
            details={
                "package_id": package.id,
                "source_document_id": source.id,
                "task_template_code": semantics.task_template_code,
                "matching_open_task_count": len(matching_tasks),
                "matching_open_task_ids": [task.id for task in matching_tasks],
            },
            status_code=409,
        )

    case = _get_case(db, package.case_id)
    if _normalize_code(case.status) != expected_case_status:
        raise_business_error(
            "OA_RECEIPT_ARCHIVE_CASE_STATE_INVALID",
            "OA receipt archive case state does not match source semantics",
            details={
                "package_id": package.id,
                "case_id": case.id,
                "case_status": case.status,
                "expected_case_status": expected_case_status,
            },
            status_code=409,
        )
    return case, source, matching_tasks[0], restore_status, receipt_ids


def _apply_oa_receipt_archive_event(
    db: Session,
    *,
    package: OfficialWorkPackage,
    actor_id: str | None,
    event_context: tuple[Case, Document, Task, str, list[str]],
) -> None:
    case, source, task, restore_status, receipt_ids = event_context
    from_case_status = case.status
    receipt = db.execute(
        select(OfficialWorkPackageReceipt).where(OfficialWorkPackageReceipt.id == receipt_ids[0])
    ).scalar_one()
    receipt_snapshot = {
        "archive_status": receipt.archive_status,
        "id": receipt.id,
        "note": receipt.note,
        "package_id": receipt.package_id,
        "received_at": receipt.received_at.isoformat() if receipt.received_at else None,
        "received_file_list": receipt.received_file_list,
        "receipt_attachment_id": receipt.receipt_attachment_id,
        "receipt_kind": receipt.receipt_kind,
        "receiving_case_no": receipt.receiving_case_no,
        "submitter": receipt.submitter,
    }
    receipt_content = json.dumps(
        receipt_snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    captured_at = receipt.received_at or receipt.created_at
    if captured_at.tzinfo is not None:
        captured_at = captured_at.astimezone(timezone.utc).replace(tzinfo=None)
    apply_lifecycle_event(
        LifecycleEventCommand(
            case_id=case.id,
            event_type="OA_RECEIPT_ARCHIVED",
            lane=ActivityLane.LIFECYCLE,
            effective_at=captured_at,
            occurred_at=captured_at,
            evidence_refs=(
                EvidenceReference(
                    case_id=case.id,
                    evidence_kind="OA_RECEIPT",
                    object_type="OfficialWorkPackageReceipt",
                    object_id=receipt.id,
                    content_hash=(
                        "sha256:" + hashlib.sha256(receipt_content.encode("utf-8")).hexdigest()
                    ),
                    captured_at=captured_at,
                ),
            ),
            actor_id=_normalize_text(actor_id) or "",
            idempotency_key=f"oa-receipt-archived:{receipt.id}",
            confirmation_status=ConfirmationStatus.CONFIRMED,
            payload={},
        ),
        db,
    )
    source.reply_date = captured_at.date()
    evidence_note = json.dumps(
        {
            "actor_id": _normalize_text(actor_id),
            "case_transition": {
                "from_status": from_case_status,
                "to_status": restore_status,
            },
            "closed_task_id": task.id,
            "event": "OFFICIAL_RECEIPT_ARCHIVED",
            "receipt_ids": receipt_ids,
            "source_document_id": source.id,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    task.status = TaskStatus.DONE.value
    task.done_at = datetime.utcnow()
    db.add(
        TaskLog(
            id=str(uuid4()),
            task_id=task.id,
            action=TaskAction.CLOSE.value,
            from_status=TaskStatus.OPEN.value,
            to_status=TaskStatus.DONE.value,
            remark=evidence_note,
        )
    )
    _upsert_checklist(
        db,
        package_id=package.id,
        section_code="ARCHIVE",
        item_code="OFFICIAL_RECEIPT_ARCHIVED",
        item_label="官方回执已归档",
        status="DONE",
        required=False,
        sort_order=70,
        evidence_note=evidence_note,
    )


def _validate_archive_override(
    *,
    actor_id: str | None,
    override_reason: str | None,
    follow_up_owner: str | None,
    follow_up_due_date: date | None,
    follow_up_note: str | None,
) -> None:
    if not _normalize_text(actor_id):
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_OVERRIDE_INCOMPLETE",
            "Override user is required",
            status_code=400,
        )
    if not _normalize_text(override_reason):
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_OVERRIDE_INCOMPLETE",
            "Override reason is required",
            status_code=400,
        )
    if not _normalize_text(follow_up_owner):
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_OVERRIDE_INCOMPLETE",
            "Override follow-up owner is required",
            status_code=400,
        )
    if not follow_up_due_date and not _normalize_text(follow_up_note):
        raise_business_error(
            "OFFICIAL_WORK_PACKAGE_OVERRIDE_INCOMPLETE",
            "Override follow-up responsibility is required",
            status_code=400,
        )


def archive_official_work_package(
    db: Session,
    *,
    package_id: str,
    actor_id: str | None,
    override_reason: str | None = None,
    follow_up_owner: str | None = None,
    follow_up_due_date: date | None = None,
    follow_up_note: str | None = None,
) -> OfficialWorkPackage:
    package = _get_package(db, package_id)
    if _normalize_code(package.status) == "ARCHIVED":
        return package
    evaluation = evaluate_official_work_package(db, package_id=package_id)
    if evaluation.can_archive:
        event_context = None
        if _normalize_code(package.package_kind) == "OA_REPLY":
            event_context = _prepare_oa_receipt_archive_event(db, package=package)
        if event_context is not None:
            _apply_oa_receipt_archive_event(
                db,
                package=package,
                actor_id=actor_id,
                event_context=event_context,
            )
        package.status = "ARCHIVED"
        db.commit()
        db.refresh(package)
        return package

    non_receipt_blockers = [
        blocker for blocker in evaluation.blockers if blocker.blocker_type != "RECEIPT_MISSING"
    ]
    if override_reason or follow_up_owner or follow_up_due_date or follow_up_note:
        _validate_archive_override(
            actor_id=actor_id,
            override_reason=override_reason,
            follow_up_owner=follow_up_owner,
            follow_up_due_date=follow_up_due_date,
            follow_up_note=follow_up_note,
        )
        if non_receipt_blockers:
            raise_business_error(
                "OFFICIAL_WORK_PACKAGE_ARCHIVE_BLOCKED",
                "Official work package still has non-receipt blockers",
                details={
                    "blockers": [
                        blocker.model_dump(mode="json") for blocker in non_receipt_blockers
                    ]
                },
                status_code=409,
            )
        db.add(
            OfficialWorkPackageOverride(
                id=str(uuid4()),
                package_id=package_id,
                override_action="ARCHIVE_WITHOUT_RECEIPT",
                override_reason=_normalize_text(override_reason) or "",
                override_by=_normalize_text(actor_id),
                follow_up_owner=_normalize_text(follow_up_owner),
                follow_up_due_date=follow_up_due_date,
                follow_up_note=_normalize_text(follow_up_note),
            )
        )
        package.status = "OVERRIDE"
        db.commit()
        db.refresh(package)
        return package

    raise_business_error(
        "OFFICIAL_WORK_PACKAGE_ARCHIVE_BLOCKED",
        "工作包不能归档：请先完成清单、文件清单和回执门禁。",
        details={"blockers": [blocker.model_dump(mode="json") for blocker in evaluation.blockers]},
        status_code=409,
    )
