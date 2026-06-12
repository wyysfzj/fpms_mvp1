from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.modules.documents.schemas import LetterHandoffOut

OFFICIAL_WORK_PACKAGE_KINDS = ("FILING_PREP", "OA_REPLY")
OFFICIAL_WORK_PACKAGE_STATUSES = (
    "PREPARING",
    "NEEDS_MAINTENANCE",
    "NEEDS_CONFIRMATION",
    "READY_FOR_EXTERNAL_SUBMIT",
    "SUBMITTED",
    "WAITING_RECEIPT",
    "ARCHIVED",
    "EXCEPTION",
    "OVERRIDE",
)
OFFICIAL_WORK_PACKAGE_RECEIPT_KINDS = (
    "RECEIPT_PDF",
    "MERGED_PDF",
    "ELECTRONIC_APPLICATION_RECEIPT",
)


class OfficialWorkPackageOut(BaseModel):
    id: str
    case_id: str
    package_kind: str
    status: str = "PREPARING"
    source_document_id: str | None = None
    reply_document_id: str | None = None
    external_system: str | None = None
    remark: str | None = None


class OfficialWorkPackageChecklistOut(BaseModel):
    id: str
    package_id: str
    section_code: str
    item_code: str
    item_label: str
    status: str = "PENDING"
    required: bool = True
    sort_order: int | None = None
    evidence_note: str | None = None


class OfficialWorkPackageManifestOut(BaseModel):
    id: str
    package_id: str
    attachment_id: str | None = None
    official_file_role: str | None = None
    source_role_alias: str | None = None
    external_upload_position: str | None = None
    content_hash: str | None = None
    required: bool = False
    present: bool = False
    sort_order: int | None = None
    note: str | None = None


class OfficialWorkPackageReceiptOut(BaseModel):
    id: str
    package_id: str
    receipt_kind: str = "RECEIPT_PDF"
    receipt_attachment_id: str | None = None
    receiving_case_no: str | None = None
    submitter: str | None = None
    received_at: datetime | None = None
    received_file_list: str | None = None
    archive_status: str = "PENDING"
    note: str | None = None


class OfficialWorkPackageOverrideOut(BaseModel):
    id: str
    package_id: str
    override_action: str = Field(..., min_length=1, max_length=64)
    override_reason: str = Field(..., min_length=1)
    override_by: str | None = Field(default=None, max_length=36)
    override_at: datetime
    follow_up_owner: str | None = Field(default=None, max_length=36)
    follow_up_due_date: date | None = None
    follow_up_note: str | None = None


class OfficialWorkPackageBlockerOut(BaseModel):
    blocker_type: str
    item_code: str | None = None
    item_label: str | None = None
    status: str
    message: str


class OfficialWorkPackageStatusEvaluationOut(BaseModel):
    package_id: str
    status: str
    can_archive: bool = False
    receipt_hard_gate_satisfied: bool = False
    blockers: list[OfficialWorkPackageBlockerOut] = Field(default_factory=list)


class OfficialWorkPackageReceiptCreateIn(BaseModel):
    receipt_kind: str = "RECEIPT_PDF"
    receipt_attachment_id: str | None = None
    receiving_case_no: str | None = Field(default=None, max_length=128)
    submitter: str | None = Field(default=None, max_length=128)
    received_at: datetime | None = None
    received_file_list: str | None = None
    archive_status: str = "PENDING"
    note: str | None = None


class OfficialWorkPackageArchiveIn(BaseModel):
    override_reason: str | None = None
    follow_up_owner: str | None = Field(default=None, max_length=36)
    follow_up_due_date: date | None = None
    follow_up_note: str | None = None


class OfficialWorkPackageArchiveResultOut(BaseModel):
    package: OfficialWorkPackageOut
    evaluation: OfficialWorkPackageStatusEvaluationOut


class OfficialFieldCheckOut(BaseModel):
    code: str
    label: str
    status: str
    message: str | None = None


class OfficialFieldSummaryOut(BaseModel):
    status: str
    missing_codes: list[str] = Field(default_factory=list)
    items: list[OfficialFieldCheckOut] = Field(default_factory=list)


class FilingPackageGateOut(BaseModel):
    role: str
    required: bool = True
    status: str
    attachment_id: str | None = None
    file_name: str | None = None


class FilingPackageXmlZipOut(BaseModel):
    status: str
    attachment_id: str | None = None
    file_name: str | None = None
    placeholder: str | None = None


class FilingPackageFeeSummaryOut(BaseModel):
    draft_count: int = 0
    pay_list_count: int = 0
    official_template_ready: bool = False
    blocker_count: int = 0


class FilingPreparationRefreshIn(BaseModel):
    require_commission_instruction: bool = False


class FilingPreparationChecklistUpdateIn(BaseModel):
    status: str = Field(..., min_length=1, max_length=32)
    evidence_note: str | None = None


class FilingPreparationExternalOperationIn(BaseModel):
    operation_code: str = Field(..., min_length=1, max_length=64)
    occurred_at: datetime
    note: str | None = None


class FilingPreparationPackageOut(BaseModel):
    package: OfficialWorkPackageOut
    official_field_summary: OfficialFieldSummaryOut
    technical_disclosure_gate: FilingPackageGateOut
    commission_instruction_gate: FilingPackageGateOut
    filing_file_roles: list[OfficialWorkPackageManifestOut] = Field(default_factory=list)
    official_page_checklist: list[OfficialWorkPackageChecklistOut] = Field(default_factory=list)
    xml_zip: FilingPackageXmlZipOut
    merged_pdf_archive_status: str
    fee_summary: FilingPackageFeeSummaryOut


class FilingPreparationChecklistResultOut(BaseModel):
    package_id: str
    checklist_item: OfficialWorkPackageChecklistOut


class OaReplyDocumentOut(BaseModel):
    id: str
    title: str | None = None
    template_code: str | None = None
    direction: str
    doc_date: date | None = None
    ref_no: str | None = None
    reply_to_id: str | None = None
    need_reply: bool | None = None
    reply_date: date | None = None


class OaReplyAttachmentOut(BaseModel):
    role: str
    status: str
    attachment_id: str | None = None
    file_name: str | None = None
    external_upload_position: str | None = None


class OaReplyLinkDocumentIn(BaseModel):
    reply_document_id: str = Field(..., min_length=1, max_length=36)


class OaReplyChecklistUpdateIn(BaseModel):
    status: str = Field(..., min_length=1, max_length=32)
    evidence_note: str | None = None


class OaReplyRefreshIn(BaseModel):
    experiment_data_submitted: bool | None = None


class OaReplyPackageOut(BaseModel):
    package: OfficialWorkPackageOut
    source_document: OaReplyDocumentOut | None = None
    reply_document: OaReplyDocumentOut | None = None
    application_no: str | None = None
    applicant_display: str | None = None
    notice_code: str | None = None
    notice_name: str | None = None
    issue_sequence: str | None = None
    issue_date: date | None = None
    official_due_date: date | None = None
    internal_due_date: date | None = None
    reply_status: str
    statement_text: str | None = None
    statement_word: OaReplyAttachmentOut
    statement_pdf: OaReplyAttachmentOut
    modified_claim_files: list[OaReplyAttachmentOut] = Field(default_factory=list)
    comparison_page: OaReplyAttachmentOut
    proof_files: list[OaReplyAttachmentOut] = Field(default_factory=list)
    experiment_data_submitted: bool = False
    official_page_checklist: list[OfficialWorkPackageChecklistOut] = Field(default_factory=list)
    oa_file_roles: list[OfficialWorkPackageManifestOut] = Field(default_factory=list)


class OaReplyChecklistResultOut(BaseModel):
    package_id: str
    checklist_item: OfficialWorkPackageChecklistOut


class LetterHandoffMappingOut(BaseModel):
    id: str | None = None
    format_letter_template_id: str | None = None
    format_letter_template_code: str | None = None
    output_name_rule: str | None = None
    contact_rule_code: str | None = None
    salutation_rule_code: str | None = None


class LetterHandoffContactOut(BaseModel):
    id: str
    contact_name: str
    title: str | None = None
    email: str | None = None


class LetterHandoffPreviewAttachmentOut(BaseModel):
    attachment_id: str | None = None
    file_name: str
    file_path: str | None = None
    attachment_role: str
    required: bool = False
    included: bool = False
    sort_order: int | None = None


class LetterHandoffPreviewOut(BaseModel):
    source_document_id: str
    case_id: str
    case_no: str
    mapping: LetterHandoffMappingOut | None = None
    template_status: str
    client_contact_id: str | None = None
    contact: LetterHandoffContactOut | None = None
    contact_selection_source: str
    salutation_source: str
    salutation_text: str
    generated_word_path: str | None = None
    mail_subject: str
    mail_body_draft: str
    attachments: list[LetterHandoffPreviewAttachmentOut] = Field(default_factory=list)


class LetterHandoffCreateIn(BaseModel):
    remark: str | None = None


class LetterHandoffStatusUpdateIn(BaseModel):
    longxia_handoff_status: str = Field(..., min_length=1, max_length=32)
    longxia_handoff_payload: str | None = None
    handoff_at: datetime | None = None


class LetterHandoffResultOut(BaseModel):
    preview: LetterHandoffPreviewOut | None = None
    handoff: LetterHandoffOut


class OfficialFeeDraftLinkOut(BaseModel):
    id: str
    draft_type: str
    status: str
    currency: str
    total_gov: Decimal
    total_service: Decimal
    total_misc: Decimal
    amount: Decimal
    official_fee_reduction_note: str | None = None
    customer_fee_reduction_ratio: str | None = None
    payable_fee_ratio: str | None = None
    fee_reduction_conversion_status: str | None = None
    fee_reduction_conversion_note: str | None = None
    official_template_status: str | None = None
    official_template_version: str | None = None
    official_template_note: str | None = None


class OfficialPayListLinkOut(BaseModel):
    id: int
    pay_list_no: str | None = None
    status: str
    currency: str
    planned_pay_date: date | None = None
    paid_date: date | None = None
    total_amount: Decimal
    official_upload_template_status: str | None = None
    official_upload_template_name: str | None = None
    official_upload_batch_limit: int | None = None
    official_pay_list_boundary_note: str | None = None
    manual_payment_status: str
    gov_payment_statuses: list[str] = Field(default_factory=list)


class OfficialFeeLinkageBlockerOut(BaseModel):
    blocker_code: str
    blocker_label: str
    source_type: str
    source_id: str | None = None
    status: str
    message: str


class OfficialFeeLinkageOut(BaseModel):
    package_id: str
    case_id: str
    payment_execution_mode: str = "MANUAL_ONLY"
    official_excel_template_ready: bool = False
    official_excel_generation_allowed: bool = False
    fee_drafts: list[OfficialFeeDraftLinkOut] = Field(default_factory=list)
    pay_lists: list[OfficialPayListLinkOut] = Field(default_factory=list)
    checklist: list["OfficialFeeChecklistOut"] = Field(default_factory=list)
    customer_confirmation_blockers: list[OfficialFeeLinkageBlockerOut] = Field(default_factory=list)


class OfficialFeeChecklistOut(BaseModel):
    id: str
    fee_draft_id: str | None = None
    pay_list_id: int | None = None
    checklist_code: str
    checklist_label: str
    status: str
    required: bool = True
    blocker_reason: str | None = None
    sort_order: int | None = None
