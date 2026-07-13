from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PayList(Base):
    __tablename__ = "t_pay_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_client.id", ondelete="RESTRICT"), nullable=False
    )
    pay_list_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'DRAFT'"))
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    planned_pay_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    list_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    flow_dir: Mapped[str | None] = mapped_column(String(32), nullable=True)
    invoice_no_from: Mapped[str | None] = mapped_column(String(64), nullable=True)
    invoice_no_to: Mapped[str | None] = mapped_column(String(64), nullable=True)
    official_upload_template_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    official_upload_template_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    official_upload_batch_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    official_pay_list_boundary_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class GovPayment(Base):
    __tablename__ = "t_gov_payment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pay_list_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_pay_list.id", ondelete="CASCADE"), nullable=False
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="RESTRICT"), nullable=False
    )
    fee_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_fee_item.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'RECORDED'")
    )
    currency: Mapped[str] = mapped_column(String(8), nullable=False, server_default=text("'CNY'"))
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    official_receipt_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fee_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    year_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_amt: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    planned_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    paid_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    voucher_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    invoice_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)


class AnnuityTask(Base):
    __tablename__ = "t_annuity_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_client.id", ondelete="RESTRICT"), nullable=False
    )
    year_no: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    client_instruction: Mapped[str | None] = mapped_column(String(24), nullable=True)
    instruction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notice_status: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'PENDING'")
    )
    notice_sent_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'OPEN'"))
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    gov_fee_amt: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, server_default=text("0")
    )
    service_fee_amt: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, server_default=text("0")
    )
    notify_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    pay_next_year: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    draft_generated: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    notice_sent: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
