from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class TaskTemplate(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_task_template"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    add_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    add_months: Mapped[int | None] = mapped_column(Integer, nullable=True, server_default=text("0"))
    inner_offset_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
