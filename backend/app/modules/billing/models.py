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
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class Bill(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_bill"

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
    bad_debt_status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'NONE'")
    )
    bad_debt_substatus: Mapped[str | None] = mapped_column(String(24), nullable=True)


class BillItem(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_bill_item"

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


class BillDraftSource(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_bill_draft_source"

    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_bill.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    draft_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_fee_draft.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(96), nullable=False, unique=True)
    command_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class BadDebtVoucher(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_bad_debt_voucher"

    bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_bill.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'OPEN'"))
    bad_debt_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    recovered_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    bad_debt_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)


class BadDebtRecovery(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_bad_debt_recovery"

    voucher_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_bad_debt_voucher.id", ondelete="CASCADE"), nullable=False
    )
    recovery_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    recovery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)


class CaseReceipt(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_case_receipt"

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
    fee_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    year_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_arrears: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    invoice_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_commissionable: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    fee_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_prepayment: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(String(512), nullable=True)
    receipt_key: Mapped[str | None] = mapped_column(String(192), nullable=True, unique=True)


class Offset(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_offset"

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


class Payment(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_payment"

    pay_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("t_client.id"), nullable=False)
    pay_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    pay_method: Mapped[str | None] = mapped_column(String(24), nullable=True)
    bank_ref_no: Mapped[str | None] = mapped_column(String(96), nullable=True, unique=True)


class PaymentLine(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_payment_line"

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


class DemoPaymentCommand(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_demo_payment_command"

    payment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_payment.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    target_bill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_bill.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(96), nullable=False, unique=True)
    command_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class DemoOffsetCommand(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_demo_offset_command"

    offset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_offset.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    receipt_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case_receipt.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(96), nullable=False, unique=True)
    command_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class DemoFinanceCommand(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_demo_finance_command"
    __table_args__ = (
        UniqueConstraint(
            "operation",
            "idempotency_key",
            name="uq_demo_finance_command_operation_key",
        ),
    )

    operation: Mapped[str] = mapped_column(String(16), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(96), nullable=False)
    state: Mapped[str] = mapped_column(String(16), nullable=False)
    command_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    command_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    result_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
