from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class FeeDraft(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_fee_draft"

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


class FeeItem(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_fee_item"

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


class FeeRate(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_fee_rate"

    fee_code: Mapped[str] = mapped_column(String(64), nullable=False)
    fee_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    fee_type: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'SERVICE'")
    )
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    default_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    rate_group: Mapped[str | None] = mapped_column(String(32), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    case_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    patent_category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    calc_mode: Mapped[str | None] = mapped_column(
        String(16), nullable=True, server_default=text("'FIXED'")
    )
    calc_params: Mapped[str | None] = mapped_column(Text, nullable=True)
    allow_reduction: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
