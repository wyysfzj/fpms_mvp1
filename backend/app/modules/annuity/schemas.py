from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PayListOfficialReadinessOut(BaseModel):
    pay_list_id: int
    official_upload_template_status: str | None = None
    official_upload_template_name: str | None = None
    official_upload_batch_limit: int | None = None
    official_pay_list_boundary_note: str | None = None


class OfficialWorkbookAcceptanceIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(..., min_length=1, max_length=36)
    evidence_ref: str = Field(..., min_length=1, max_length=512)
    evidence_sha256: str = Field(..., pattern=r"^[0-9a-f]{64}$")
    accepted_at: datetime
    idempotency_key: str = Field(..., min_length=1, max_length=128)


class OfficialWorkbookAcceptanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    artifact_id: str
    pay_list_id: int
    evidence_ref: str
    evidence_sha256: str
    accepted_at: datetime
    activity_id: str
    status: str
    accepted: bool
    paid: bool
    ticket_verified: bool
    idempotency_key: str
    disposition: str


class AnnuityTaskListItemResponse(BaseModel):
    id: int
    case_id: str
    case_no: str | None = None
    client_id: str
    year_no: int
    due_date: date
    client_instruction: str | None = None
    instruction_date: date | None = None
    notice_status: str
    notice_sent_date: date | None = None
    status: str
    remark: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    gov_fee_amt: Decimal | None = Field(default=None)
    service_fee_amt: Decimal | None = Field(default=None)
    notify_count: int | None = None
    pay_next_year: bool | None = None
    draft_generated: bool | None = None
    notice_sent: bool | None = None
    is_overdue: bool = False
    trigger_rule: str
    deadline_rule: str
    fee_basis: str
    fee_node_explanation: str


class AnnuityTaskReportCountResponse(BaseModel):
    key: str
    count: int = 0


class AnnuityTaskGroupedAmountResponse(BaseModel):
    key: str
    label: str
    task_count: int = 0
    payable_amount: Decimal = Decimal("0")
    official_paid_amount: Decimal = Decimal("0")
    client_received_amount: Decimal = Decimal("0")


class AnnuityTaskReportSummaryResponse(BaseModel):
    total_task_count: int = 0
    open_task_count: int = 0
    done_task_count: int = 0
    overdue_task_count: int = 0
    official_paid_task_count: int = 0
    client_received_task_count: int = 0
    collected_not_paid_task_count: int = 0
    outstanding_task_count: int = 0
    monitored_task_count: int = 0
    on_time_paid_count: int = 0
    late_paid_count: int = 0
    success_rate: float | None = None
    status_counts: list[AnnuityTaskReportCountResponse] = Field(default_factory=list)
    year_counts: list[AnnuityTaskReportCountResponse] = Field(default_factory=list)
    client_amounts: list[AnnuityTaskGroupedAmountResponse] = Field(default_factory=list)
    country_amounts: list[AnnuityTaskGroupedAmountResponse] = Field(default_factory=list)
    year_amounts: list[AnnuityTaskGroupedAmountResponse] = Field(default_factory=list)


class AnnuityTaskListResponse(BaseModel):
    items: list[AnnuityTaskListItemResponse]
    page: int
    page_size: int
    total: int
    summary: AnnuityTaskReportSummaryResponse
