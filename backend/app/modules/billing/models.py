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
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Bill(Base):
    __tablename__ = "t_bill"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bill_no: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("t_client.id"), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    direction: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'AR'"))
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'UNSETTLED'")
    )
    bill_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
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
    balance: Mapped[Decimal] = mapped_column(
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


class BillItem(Base):
    __tablename__ = "t_bill_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_bill.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("t_case.id"), nullable=True)
    draft_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_fee_draft.id"), nullable=True
    )
    fee_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_fee_item.id"), nullable=True
    )
    fee_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fee_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    fee_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    year_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )


class CaseReceipt(Base):
    __tablename__ = "t_case_receipt"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    fee_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    receivable_amt: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    received_amt: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    last_receipt_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class Offset(Base):
    __tablename__ = "t_offset"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payment_line_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_payment_line.id", ondelete="CASCADE"), nullable=False
    )
    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_bill.id", ondelete="CASCADE"), nullable=False
    )
    offset_amt: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    offset_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_reversed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)


class Payment(Base):
    __tablename__ = "t_payment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    pay_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("t_client.id"), nullable=False)
    pay_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.current_timestamp()
    )


class PaymentLine(Base):
    __tablename__ = "t_payment_line"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_payment.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("t_case.id"), nullable=True)
    raw_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    allocated_amt: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    balance_amt: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
