from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Dunning(Base):
    __tablename__ = "t_dunning"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_client.id", ondelete="RESTRICT"), nullable=False
    )
    dunning_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    round_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    to_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'DRAFT'"))
    sent_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class DunningLine(Base):
    __tablename__ = "t_dunning_line"
    __table_args__ = (UniqueConstraint("dunning_id", "line_no", name="uq_t_dunning_line_no"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dunning_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_dunning.id", ondelete="CASCADE"), nullable=False
    )
    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_bill.id", ondelete="RESTRICT"), nullable=False
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    bill_no_snapshot: Mapped[str | None] = mapped_column(String(64), nullable=True)
    due_date_snapshot: Mapped[date | None] = mapped_column(Date, nullable=True)
    bill_status_snapshot: Mapped[str | None] = mapped_column(String(24), nullable=True)
    outstanding_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    currency_snapshot: Mapped[str | None] = mapped_column(String(8), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
