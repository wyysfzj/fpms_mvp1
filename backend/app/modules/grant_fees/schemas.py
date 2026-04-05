from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GrantFeeTaskModuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    module: str = Field(default="grant_fees")
    permission_namespace: str = Field(default="GrantFeeTask")
    permission_codes: list[str]
    status: str = Field(default="ok")


class GrantFeeTaskStateActionIn(BaseModel):
    action: str = Field(..., min_length=1, max_length=32)


class GrantFeeTaskStateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    case_id: str
    state: str
    client_instruction: str
    notify_count: int
    draft_generated: bool
    notice_sent: bool
    is_overdue: bool
    allowed_actions: list[str] = Field(default_factory=list)


class GrantFeeTaskListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: str
    case_id: str
    status: str
    due_date: date
    client_instruction: str
    gov_fee_amt: Decimal
    service_fee_amt: Decimal
    currency: str
    draft_generated: bool
    notice_sent: bool
    is_overdue: bool
    billed: bool = False
    linked_bill_id: str | None = None
    linked_bill_no: str | None = None


class GrantFeeTaskListResponse(BaseModel):
    items: list[GrantFeeTaskListItemResponse]
    page: int
    page_size: int
    total: int


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
