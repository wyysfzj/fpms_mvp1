from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FeeDraft(Base):
    __tablename__ = "t_fee_draft"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_client.id"), nullable=True
    )
    draft_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'GENERIC'")
    )
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default=text("'OPEN'"))
    total_gov: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    total_service: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    total_misc: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class FeeItem(Base):
    __tablename__ = "t_fee_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    draft_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_fee_draft.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("t_case.id"), nullable=True)
    rate_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_fee_rate.id"), nullable=True
    )
    fee_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fee_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    fee_type: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'SERVICE'")
    )
    year_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)


class FeeRate(Base):
    __tablename__ = "t_fee_rate"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    fee_code: Mapped[str] = mapped_column(String(64), nullable=False)
    fee_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    fee_type: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'SERVICE'")
    )
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    default_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
