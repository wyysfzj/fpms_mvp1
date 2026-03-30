from __future__ import annotations

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
