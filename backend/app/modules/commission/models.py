from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
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


class CommissionRule(Base):
    __tablename__ = "t_commission_rule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False)
    case_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fee_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    flow_dir: Mapped[str | None] = mapped_column(String(32), nullable=True)
    patent_category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    s1_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, server_default=text("0"))
    s2_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, server_default=text("0"))
    s1_fixed_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    s2_fixed_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    wait_pay: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    force_settle: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class Commission(Base):
    __tablename__ = "t_commission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("t_commission_rule.id", ondelete="SET NULL"), nullable=True
    )
    fee_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    base_fee: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text("0"))
    s1_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, server_default=text("0"))
    s1_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    s1_done: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    s2_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, server_default=text("0"))
    s2_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    s2_done: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    wait_pay: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    force_settle: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'OPEN'"))
    is_settleable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    settleable_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class CommissionSettlement(Base):
    __tablename__ = "t_commission_settlement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    settlement_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'DRAFT'"))
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    settle_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    line_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class CommissionSettleLine(Base):
    __tablename__ = "t_commission_settle_line"
    __table_args__ = (
        UniqueConstraint("settlement_id", "line_no", name="uq_t_comm_settle_line_no"),
        UniqueConstraint(
            "settlement_id", "commission_id", name="uq_t_comm_settle_line_commission"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    settlement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_commission_settlement.id", ondelete="CASCADE"), nullable=False
    )
    commission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_commission.id", ondelete="RESTRICT"), nullable=False
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'PENDING'")
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
