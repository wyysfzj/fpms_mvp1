from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, text
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
    official_fee_reduction_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    official_template_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    official_template_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    official_template_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class OfficialFeeChecklist(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_official_fee_checklist"

    fee_draft_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_fee_draft.id", ondelete="CASCADE"), nullable=True
    )
    pay_list_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("t_pay_list.id", ondelete="CASCADE"), nullable=True
    )
    checklist_code: Mapped[str] = mapped_column(String(64), nullable=False)
    checklist_label: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    blocker_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)


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
    fee_domain: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fee_section: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fee_category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fee_subtype: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reduction_scope: Mapped[str | None] = mapped_column(String(256), nullable=True)
    calc_mode: Mapped[str | None] = mapped_column(
        String(16), nullable=True, server_default=text("'FIXED'")
    )
    calc_params: Mapped[str | None] = mapped_column(Text, nullable=True)
    allow_reduction: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, server_default=text("0")
    )
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_doc: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_policy: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_status: Mapped[str | None] = mapped_column(String(32), nullable=True)


class T_GrantFeeTask(Base):
    __tablename__ = "t_grant_fee_task"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(16), nullable=False, server_default=text("'GRANT'"))
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    gov_fee_amt: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    service_fee_amt: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    client_instruction: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default=text("'NONE'")
    )
    notify_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    draft_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    notice_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    is_overdue: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
