from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.tasks.enums import TaskAction, TaskStatus


class TaskCreateIn(BaseModel):
    case_id: str
    document_id: str | None = None
    task_template_id: str | None = None
    title: str = Field(..., min_length=1)
    base_date: date | None = None
    due_date: date
    internal_due_date: date | None = None
    worker_id: str | None = None
    supervisor_id: str | None = None
    remark: str | None = None


class TaskUpdateIn(BaseModel):
    case_id: str | None = None
    document_id: str | None = None
    task_template_id: str | None = None
    title: str | None = None
    base_date: date | None = None
    due_date: date | None = None
    internal_due_date: date | None = None
    worker_id: str | None = None
    supervisor_id: str | None = None
    remark: str | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str | None = None
    document_id: str | None = None
    task_template_id: str | None = None
    title: str
    base_date: date | None = None
    due_date: date
    internal_due_date: date | None = None
    worker_id: str | None = None
    supervisor_id: str | None = None
    remark: str | None = None
    status: TaskStatus
    done_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TaskListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str | None = None
    case_no: str | None = None
    client_name: str | None = None
    document_id: str | None = None
    task_template_id: str | None = None
    title: str
    due_date: date
    internal_due_date: date | None = None
    worker_id: str | None = None
    supervisor_id: str | None = None
    remark: str | None = None
    status: TaskStatus
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TaskActionIn(BaseModel):
    remark: str | None = None


class TaskAssignIn(BaseModel):
    worker_id: str | None = None
    supervisor_id: str | None = None
    remark: str | None = None

    @model_validator(mode="after")
    def check_assignee(self) -> "TaskAssignIn":
        if not self.worker_id and not self.supervisor_id:
            raise ValueError("worker_id or supervisor_id must be provided")
        return self


class TaskActionOut(BaseModel):
    status: str = "ok"


class TaskLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    action: TaskAction
    from_status: TaskStatus | None = None
    to_status: TaskStatus | None = None
    remark: str | None = None
    created_at: datetime


class TaskTemplateCreateIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=256)
    add_days: int | None = None
    add_months: int | None = None
    inner_offset_days: int | None = None
    default_worker_role: str | None = None
    description: str | None = None


class TaskTemplateUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    add_days: int | None = None
    add_months: int | None = None
    inner_offset_days: int | None = None
    default_worker_role: str | None = None
    enabled: bool | None = None
    description: str | None = None


class TaskTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    add_days: int | None = None
    add_months: int | None = None
    inner_offset_days: int | None = None
    default_worker_role: str | None = None
    enabled: bool
    description: str | None = None
    created_at: datetime
    updated_at: datetime
