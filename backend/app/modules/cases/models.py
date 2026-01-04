from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Case(Base):
    __tablename__ = "t_case"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    case_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'NORMAL'")
    )
    patent_category: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'INV'")
    )
    flow_dir: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'CN_DOMESTIC'")
    )
    client_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_client.id"), nullable=True
    )
    title_cn: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    app_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'NOT_FILED'")
    )
    recv_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
