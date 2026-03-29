from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin
from app.modules.tasks.enums import TaskDeadlineBase, TaskRemindBase


class TaskTemplate(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_task_template"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    deadline_base: Mapped[TaskDeadlineBase | None] = mapped_column(
        SAEnum(
            TaskDeadlineBase,
            name="task_deadline_base",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=True,
    )
    add_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    add_months: Mapped[int | None] = mapped_column(Integer, nullable=True, server_default=text("0"))
    inner_offset_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remind_base: Mapped[TaskRemindBase | None] = mapped_column(
        SAEnum(
            TaskRemindBase,
            name="task_remind_base",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=True,
    )
    remind_1_offset_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remind_2_offset_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remind_3_offset_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    daily_remind: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    default_supervisor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_user.id"), nullable=True
    )
    default_worker_role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class Task(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_task"

    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_document.id"), nullable=True
    )
    task_template_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_task_template.id"), nullable=True
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    internal_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    remind1: Mapped[date | None] = mapped_column(Date, nullable=True)
    remind2: Mapped[date | None] = mapped_column(Date, nullable=True)
    remind3: Mapped[date | None] = mapped_column(Date, nullable=True)
    daily_remind_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    daily_remind: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    worker_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_user.id"), nullable=True
    )
    supervisor_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_user.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default=text("'OPEN'"))
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)


class TaskLog(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_task_log"

    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_task.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
