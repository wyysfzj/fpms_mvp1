from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class Template(Base):
    __tablename__ = "t_template"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    group: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.current_timestamp()
    )


class FormatLetterMapping(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_format_letter_mapping"

    official_doc_template_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_doc_template.id"), nullable=True
    )
    official_doc_template_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    official_doc_name_pattern: Mapped[str | None] = mapped_column(String(256), nullable=True)
    format_letter_template_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_template.id"), nullable=True
    )
    format_letter_template_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_name_rule: Mapped[str | None] = mapped_column(Text, nullable=True)
    salutation_rule_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    contact_rule_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
