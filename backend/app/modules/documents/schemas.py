from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.pagination import PageResult
from app.modules.documents.enums import DocumentDirection, DocumentDocType


class DocAttachmentOut(BaseModel):
    id: str
    document_id: str
    file_name: str
    mime_type: str
    file_size: int
    uploaded_at: datetime


class DocumentCreateIn(BaseModel):
    case_id: str
    doc_template_id: str | None = None
    doc_type: DocumentDocType | None = None
    direction: DocumentDirection
    doc_date: date
    title: str
    ref_no: str | None = None
    extra_data: str | None = None
    reply_to_id: str | None = None


class DocumentImpactPreviewIn(BaseModel):
    case_id: str = Field(..., min_length=1)
    doc_template_id: str | None = None
    doc_type: DocumentDocType | None = None
    direction: DocumentDirection
    doc_date: date
    title: str = Field(..., min_length=1)
    ref_no: str | None = None
    extra_data: str | None = None
    reply_to_id: str | None = None


class DocumentImpactItemOut(BaseModel):
    kind: str
    title: str
    effect: str | None = None
    enabled: bool = True
    requires_confirmation: bool = False
    document_id: str | None = None
    detail: str | None = None


class DocumentImpactPreviewOut(BaseModel):
    case_id: str
    case_no: str | None = None
    template_code: str | None = None
    status_impacts: list[DocumentImpactItemOut] = Field(default_factory=list)
    deadline_impacts: list[DocumentImpactItemOut] = Field(default_factory=list)
    task_impacts: list[DocumentImpactItemOut] = Field(default_factory=list)
    fee_impacts: list[DocumentImpactItemOut] = Field(default_factory=list)
    file_status_impacts: list[DocumentImpactItemOut] = Field(default_factory=list)
    confirmation_required: bool = False
    confirmation_items: list[str] = Field(default_factory=list)
    risk_tips: list[str] = Field(default_factory=list)


class DocumentWizardBatchDefaultsIn(BaseModel):
    doc_template_id: str = Field(..., min_length=1)
    direction: DocumentDirection
    doc_date: date
    title: str | None = None
    ref_no: str | None = None
    extra_data: str | None = None
    reply_to_id: str | None = None


class DocumentWizardBatchRowIn(BaseModel):
    case_id: str = Field(..., min_length=1)
    title: str | None = None
    doc_date: date | None = None
    ref_no: str | None = None
    extra_data: str | None = None
    reply_to_id: str | None = None


class DocumentWizardTaskFinalRowIn(BaseModel):
    row_index: int = Field(..., ge=1)
    case_id: str = Field(..., min_length=1, max_length=36)
    task_template_code: str = Field(..., min_length=1, max_length=64)
    title: str | None = None
    base_date: date | None = None
    due_date: date | None = None
    internal_due_date: date | None = None
    remind1: date | None = None
    remind2: date | None = None
    remind3: date | None = None
    daily_remind_from: date | None = None
    daily_remind: bool | None = None


class DocumentWizardFeeFinalFeeItemIn(BaseModel):
    fee_code: str | None = None
    fee_name: str | None = None
    fee_type: str = Field(default="SERVICE", max_length=16)
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal = Field(default=Decimal("0"), ge=0)
    remark: str | None = None


class DocumentWizardFeeFinalRowIn(BaseModel):
    row_index: int = Field(..., ge=1)
    case_id: str = Field(..., min_length=1, max_length=36)
    fee_draft_type: str = Field(..., min_length=1, max_length=32)
    skip_this_candidate: bool = False
    fee_items: list[DocumentWizardFeeFinalFeeItemIn] = Field(default_factory=list)


class DocumentWizardAttachmentFinalRowIn(BaseModel):
    row_index: int = Field(..., ge=1)
    case_id: str = Field(..., min_length=1, max_length=36)
    template_code: str = Field(..., min_length=1, max_length=64)
    output_name: str | None = None
    output_file_name: str = Field(..., min_length=1, max_length=256)
    output_format: str = Field(default="DOCX", max_length=16)
    candidate_source_kind: str = Field(default="DOC_TEMPLATE", max_length=32)
    remark: str | None = None


class DocumentWizardBatchCreateIn(BaseModel):
    defaults: DocumentWizardBatchDefaultsIn
    rows: list[DocumentWizardBatchRowIn] = Field(..., min_length=1)
    task_rows: list[DocumentWizardTaskFinalRowIn] = Field(default_factory=list)
    fee_rows: list[DocumentWizardFeeFinalRowIn] = Field(default_factory=list)
    attachment_rows: list[DocumentWizardAttachmentFinalRowIn] = Field(default_factory=list)


class DocumentWizardFeePreviewIn(BaseModel):
    defaults: DocumentWizardBatchDefaultsIn
    rows: list[DocumentWizardBatchRowIn] = Field(..., min_length=1)


class DocumentWizardTaskPreviewItemOut(BaseModel):
    row_index: int
    case_id: str
    case_no: str | None = None
    source_title: str | None = None
    document_title: str | None = None
    task_template_code: str
    task_template_name: str | None = None
    title: str | None = None
    base_date: date | None = None
    due_date: date | None = None
    internal_due_date: date | None = None
    remind1: date | None = None
    remind2: date | None = None
    remind3: date | None = None
    daily_remind_from: date | None = None
    daily_remind: bool = False


class DocumentWizardTaskPreviewOut(BaseModel):
    total_candidates: int
    items: list[DocumentWizardTaskPreviewItemOut]


class DocumentWizardFeePreviewFeeItemOut(BaseModel):
    fee_code: str | None = None
    fee_name: str | None = None
    fee_type: str = Field(default="SERVICE", max_length=16)
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal = Field(default=Decimal("0"), ge=0)
    remark: str | None = None


class DocumentWizardFeePreviewItemOut(BaseModel):
    row_index: int
    case_id: str
    case_no: str | None = None
    source_title: str | None = None
    document_title: str | None = None
    fee_draft_type: str
    fee_items: list[DocumentWizardFeePreviewFeeItemOut] = Field(default_factory=list)
    skip_this_candidate: bool = False


class DocumentWizardFeePreviewOut(BaseModel):
    total_candidates: int
    items: list[DocumentWizardFeePreviewItemOut]


class DocumentWizardAttachmentPreviewIn(BaseModel):
    defaults: DocumentWizardBatchDefaultsIn
    rows: list[DocumentWizardBatchRowIn] = Field(..., min_length=1)


class DocumentWizardAttachmentPreviewItemOut(BaseModel):
    row_index: int
    case_id: str
    case_no: str | None = None
    source_title: str | None = None
    document_title: str | None = None
    template_code: str
    template_name: str | None = None
    output_name: str | None = None
    output_file_name: str
    output_format: str = "DOCX"
    candidate_source_kind: str = "DOC_TEMPLATE"
    generate_this_candidate: bool = True
    remark: str | None = None


class DocumentWizardAttachmentPreviewOut(BaseModel):
    total_candidates: int
    items: list[DocumentWizardAttachmentPreviewItemOut]


class DocumentUpdateIn(BaseModel):
    case_id: str | None = None
    doc_template_id: str | None = None
    doc_type: DocumentDocType | None = None
    direction: DocumentDirection | None = None
    doc_date: date | None = None
    title: str | None = None
    ref_no: str | None = None
    extra_data: str | None = None
    reply_to_id: str | None = None
    need_reply: bool | None = None
    reply_date: date | None = None
    reply_task_action: Literal["UPDATE", "CANCEL", "NONE"] | None = None
    reply_task_due_date: date | None = None
    reply_task_internal_due_date: date | None = None
    reply_task_remind1: date | None = None
    reply_task_remind2: date | None = None
    reply_task_remind3: date | None = None


class DocumentOut(BaseModel):
    id: str
    case_id: str
    case_no: str | None = None
    doc_template_id: str | None
    template_code: str | None = None
    doc_type: DocumentDocType | None = None
    direction: DocumentDirection
    doc_date: date | None
    title: str | None
    ref_no: str | None
    extra_data: str | None
    reply_to_id: str | None = None
    need_reply: bool | None = None
    reply_date: date | None = None
    created_at: datetime
    updated_at: datetime
    attachments: list[DocAttachmentOut] = Field(default_factory=list)


class DocumentListOut(PageResult[DocumentOut]):
    pass


class DocumentWizardBatchRowOut(BaseModel):
    row_index: int
    document: DocumentOut


class DocumentWizardBatchCreateOut(BaseModel):
    created: int
    total: int
    items: list[DocumentWizardBatchRowOut]


class DocumentMailingBatchIn(BaseModel):
    selected_document_ids: list[str] = Field(default_factory=list)
    outgoing_reg_no: str = Field(..., min_length=1, max_length=128)
    forward_date: date | None = None


class DocumentMailingBatchItemOut(BaseModel):
    document_id: str
    case_id: str
    case_no: str | None = None
    outgoing_reg_no: str | None = None
    forward_date: date | None = None


class DocumentMailingBatchOut(BaseModel):
    success_count: int
    failure_count: int
    items: list[DocumentMailingBatchItemOut]


class DocumentDispatchCreateIn(BaseModel):
    client_id: str = Field(..., min_length=1)
    dispatch_date: date
    selected_document_ids: list[str] = Field(..., min_length=1)
    remark: str | None = None


class DocumentDispatchLineOut(BaseModel):
    id: str
    dispatch_id: str
    document_id: str
    case_id: str
    case_no: str | None = None
    doc_name: str
    outgoing_reg_no: str | None = None


class DocumentDispatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    client_name: str | None = None
    dispatch_date: date
    remark: str | None = None
    created_at: datetime
    updated_at: datetime
    lines: list[DocumentDispatchLineOut] = Field(default_factory=list)


class DocumentEnvelopePreviewOut(BaseModel):
    document_id: str
    case_id: str
    case_no: str | None = None
    client_id: str | None = None
    client_name: str | None = None
    recipient_name: str | None = None
    recipient_address: str | None = None
    address_source: str


# --- B1: DocTemplate schemas ---


class DocTemplateCreateIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=256)
    direction: DocumentDirection = DocumentDirection.IN
    enabled: bool = True
    status_effect: str | None = Field(default=None, max_length=32)
    status_restore: str | None = Field(default=None, max_length=32)
    deadline_template_code: str | None = Field(default=None, max_length=64)
    fee_draft_type: str | None = Field(default=None, max_length=32)
    fee_item_list: str | None = None  # JSON string
    need_reply: bool | None = False
    reply_to_template_code: str | None = Field(default=None, max_length=64)
    input_fields: str | None = None  # JSON string


class DocTemplateUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    direction: DocumentDirection | None = None
    enabled: bool | None = None
    status_effect: str | None = Field(default=None, max_length=32)
    status_restore: str | None = Field(default=None, max_length=32)
    deadline_template_code: str | None = Field(default=None, max_length=64)
    fee_draft_type: str | None = Field(default=None, max_length=32)
    fee_item_list: str | None = None
    need_reply: bool | None = None
    reply_to_template_code: str | None = Field(default=None, max_length=64)
    input_fields: str | None = None


class DocTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    direction: DocumentDirection
    enabled: bool
    status_effect: str | None = None
    status_restore: str | None = None
    deadline_template_code: str | None = None
    fee_draft_type: str | None = None
    fee_item_list: str | None = None
    need_reply: bool | None = None
    reply_to_template_code: str | None = None
    input_fields: str | None = None
    created_at: datetime
    updated_at: datetime


class DocTemplateListOut(PageResult[DocTemplateOut]):
    pass
