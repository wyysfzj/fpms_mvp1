from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.documents.enums import DocumentDocType
from app.modules.documents.extra_data import DeadlineSource, DeadlineWriteStatus
from app.modules.documents.schemas import DocumentOut


class GrantFeeTaskModuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    module: str = Field(default="grant_fees")
    permission_namespace: str = Field(default="GrantFeeTask")
    permission_codes: list[str]
    status: str = Field(default="ok")


class GrantFeeTaskStateActionIn(BaseModel):
    action: str = Field(..., min_length=1, max_length=32)


class GrantNoticeLifecycleIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewed_evidence_version_id: str = Field(..., strict=True, min_length=1, max_length=36)
    expected_content_hash: str = Field(
        ...,
        strict=True,
        pattern=r"^sha256:[0-9a-f]{64}$",
    )
    recorded_at: datetime
    idempotency_key: str = Field(..., strict=True, min_length=1, max_length=102)

    @field_validator("reviewed_evidence_version_id", "idempotency_key")
    @classmethod
    def require_exact_trimmed_text(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("必须移除首尾空白")
        return value

    @field_validator("recorded_at")
    @classmethod
    def require_naive_recorded_at(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            raise ValueError("必须为不带时区的日期时间")
        return value


class GrantOfficialFeeReviewLineIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    obligation_line_id: str = Field(..., strict=True, min_length=1, max_length=36)
    official_full_amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=18,
        decimal_places=2,
    )
    confirmed_payable_amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=18,
        decimal_places=2,
    )

    @field_validator("obligation_line_id")
    @classmethod
    def require_exact_line_id(cls, value: str) -> str:
        if value != value.strip() or "\x00" in value:
            raise ValueError("必须为无首尾空白的有效标识")
        return value


class GrantOfficialFeeReviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_activity_id: str = Field(..., strict=True, min_length=1, max_length=36)
    obligation_id: str = Field(..., strict=True, min_length=1, max_length=36)
    reviewed_evidence_version_id: str = Field(..., strict=True, min_length=1, max_length=36)
    expected_content_hash: str = Field(
        ...,
        strict=True,
        pattern=r"^sha256:[0-9a-f]{64}$",
    )
    confirmed_at: datetime
    idempotency_key: str = Field(..., strict=True, min_length=1, max_length=128)
    lines: list[GrantOfficialFeeReviewLineIn] = Field(..., min_length=1)

    @field_validator(
        "source_activity_id",
        "obligation_id",
        "reviewed_evidence_version_id",
        "idempotency_key",
    )
    @classmethod
    def require_exact_review_text(cls, value: str) -> str:
        if value != value.strip() or "\x00" in value:
            raise ValueError("必须为无首尾空白的有效文本")
        return value

    @field_validator("confirmed_at")
    @classmethod
    def require_naive_confirmation_time(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            raise ValueError("必须为不带时区的日期时间")
        return value


class GrantOfficialFeeReviewOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grant_fee_task_id: str
    fee_obligation_id: str
    source_activity_id: str
    review_activity_id: str
    reviewed_line_ids: list[str]
    confirmed_at: datetime
    idempotency_key: str
    reused: bool


class GrantFeeReplacementDocumentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    doc_template_id: str
    doc_type: DocumentDocType | None = None
    doc_date: date
    title: str
    ref_no: str
    extra_data: str | None = None
    official_due_date: date | None = None
    official_due_date_source: DeadlineSource | None = None
    official_due_date_status: DeadlineWriteStatus | None = None
    description: str | None = None


class GrantFeeTaskReplacementNoticeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idempotency_key: str
    reason: str
    document: GrantFeeReplacementDocumentIn


class GrantFeeTaskBatchInstructionIn(BaseModel):
    task_ids: list[str] = Field(..., min_length=1)
    action: str = Field(..., min_length=1, max_length=32)


class GrantFeeTaskStateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    case_id: str
    state: str
    lineage_status: Literal["SUPERSEDED", "LEGACY_UNVERIFIED", "CONFIRMED"]
    source_document_id: str | None = None
    deadline_source: str | None = None
    deadline_confirmed_at: datetime | None = None
    client_instruction: str
    notify_count: int
    draft_generated: bool
    notice_sent: bool
    is_overdue: bool
    allowed_actions: list[str] = Field(default_factory=list)
    trigger_rule: str
    deadline_rule: str
    fee_basis: str
    fee_node_explanation: str


class GrantFeeTaskListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    case_id: str
    case_no: str | None = None
    status: str
    lineage_status: Literal["SUPERSEDED", "LEGACY_UNVERIFIED", "CONFIRMED"]
    source_document_id: str | None = None
    deadline_source: str | None = None
    deadline_confirmed_at: datetime | None = None
    due_date: date
    client_instruction: str
    gov_fee_amt: Decimal
    service_fee_amt: Decimal
    currency: str
    draft_generated: bool
    notice_sent: bool
    notify_count: int
    is_overdue: bool
    billed: bool = False
    linked_bill_id: str | None = None
    linked_bill_no: str | None = None
    trigger_rule: str
    deadline_rule: str
    fee_basis: str
    fee_node_explanation: str


class GrantFeeTaskReplacementNoticeOut(BaseModel):
    document: DocumentOut
    replacement_task: GrantFeeTaskListItemResponse
    superseded_task_id: str
    reused: bool


class GrantFeeTaskListResponse(BaseModel):
    items: list[GrantFeeTaskListItemResponse]
    page: int
    page_size: int
    total: int


class GrantFeeTaskBatchInstructionOut(BaseModel):
    success_count: int
    failure_count: int
    updated_task_ids: list[str] = Field(default_factory=list)


class GrantFeeTaskBatchNoticeGenerateIn(BaseModel):
    task_ids: list[str] = Field(..., min_length=1)


class GrantFeeTaskBatchNoticeGenerateItemOut(BaseModel):
    task_id: str
    case_id: str
    document_id: str
    attachment_id: str
    file_name: str
    notify_count: int


class GrantFeeTaskBatchNoticeGenerateOut(BaseModel):
    success_count: int
    failure_count: int
    generated_document_ids: list[str] = Field(default_factory=list)
    items: list[GrantFeeTaskBatchNoticeGenerateItemOut] = Field(default_factory=list)


class GrantFeeDraftGenerateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    case_id: str
    draft_id: str
    draft_type: str
    state: str
    draft_generated: bool
    currency: str
    amount: Decimal
    item_count: int
    reused: bool = Field(default=False)
