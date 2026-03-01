from __future__ import annotations

from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AuditMixin, UUIDPrimaryKeyMixin


class Case(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "t_case"

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

    # -- A3: Publication / Grant --
    pub_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pub_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    grant_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    grant_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    patent_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    # -- A3: Spec details --
    spec_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claim_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_exam_request: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # -- A3: Agent assignment (no FK — app-level validation only) --
    primary_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    second_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    draftor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # -- A3: Control flags --
    is_fee_monitor: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fee_reduction: Mapped[str | None] = mapped_column(String(32), nullable=True)
    applicant_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)


class T_CaseApplicant(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """Case applicant (one or more per case)."""

    __tablename__ = "t_case_applicant"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)  # Display order
    is_first: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    name_cn: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    address_cn: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_en: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("case_id", "seq", name="uq_case_applicant_seq"),)


class T_CaseInventor(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """Case inventor (one or more per case)."""

    __tablename__ = "t_case_inventor"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    name_cn: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)

    __table_args__ = (UniqueConstraint("case_id", "seq", name="uq_case_inventor_seq"),)


class T_Priority(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """Priority claim information."""

    __tablename__ = "t_priority"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(10), nullable=True)  # e.g., "CN", "US"
    prio_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prio_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (UniqueConstraint("case_id", "seq", name="uq_priority_seq"),)
