from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AnnuityTaskListItemResponse(BaseModel):
    id: int
    case_id: str
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


class AnnuityTaskReportCountResponse(BaseModel):
    key: str
    count: int = 0


class AnnuityTaskReportSummaryResponse(BaseModel):
    total_task_count: int = 0
    open_task_count: int = 0
    done_task_count: int = 0
    overdue_task_count: int = 0
    status_counts: list[AnnuityTaskReportCountResponse] = Field(default_factory=list)
    year_counts: list[AnnuityTaskReportCountResponse] = Field(default_factory=list)


class AnnuityTaskListResponse(BaseModel):
    items: list[AnnuityTaskListItemResponse]
    page: int
    page_size: int
    total: int
    summary: AnnuityTaskReportSummaryResponse
