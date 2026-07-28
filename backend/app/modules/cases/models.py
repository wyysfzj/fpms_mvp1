from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
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
    foreign_agent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_client.id"), nullable=True
    )
    foreign_ref: Mapped[str | None] = mapped_column(String(64), nullable=True)
    from_country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    to_country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    doc_address_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_client_address.id"), nullable=True
    )
    bill_address_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_client_address.id"), nullable=True
    )
    title_cn: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    app_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'NOT_FILED'")
    )
    business_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    official_procedure_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    legal_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lifecycle_revision: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lifecycle_verification_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    recv_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    submitted_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # -- A3: Publication / Grant --
    pub_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pub_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    grant_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    terminated_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    invalidated_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    withdrawn_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    abandoned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    grant_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    cert_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    patent_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    # -- A3: Spec details --
    spec_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    draw_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claim_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claim_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manuscript_words: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_exam_request: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # -- Deferred Batch 1: PCT / invalidation --
    ro: Mapped[str | None] = mapped_column(String(64), nullable=True)
    isa: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ipea: Mapped[str | None] = mapped_column(String(64), nullable=True)
    intl_app_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    intl_app_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    intl_pub_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    intl_pub_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    intl_pub_lang: Mapped[str | None] = mapped_column(String(32), nullable=True)
    need_iper: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    iper_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pct_national_entry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    original_case_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_case.id"), nullable=True
    )
    invalid_client_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("t_client.id"), nullable=True
    )
    invalid_patentee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invalid_requester: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invalid_role: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # -- A3: Agent assignment (no FK — app-level validation only) --
    primary_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    second_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    draftor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # -- A3: Control flags --
    is_fee_monitor: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fee_reduction: Mapped[str | None] = mapped_column(String(32), nullable=True)
    discount_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    applicant_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    no_power: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    no_prio_text: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    require_hk: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    first_annuity_year: Mapped[int | None] = mapped_column(Integer, nullable=True)


class CaseActivityEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "t_case_activity_event"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "t_case.id",
            name="fk_t_case_activity_event_case_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    lane: Mapped[str] = mapped_column(String(16), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_activity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    confirmation_status: Mapped[str] = mapped_column(String(32), nullable=False)
    old_business_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_business_stage: Mapped[str | None] = mapped_column(String(32), nullable=True)
    old_official_procedure_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    new_official_procedure_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    old_legal_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    new_legal_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    supersedes_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "sequence",
            name="uq_t_case_activity_event_case_sequence",
        ),
        UniqueConstraint(
            "case_id",
            "idempotency_key",
            name="uq_t_case_activity_event_case_idempotency_key",
        ),
        UniqueConstraint(
            "case_id",
            "id",
            name="uq_t_case_activity_event_case_id",
        ),
        ForeignKeyConstraint(
            ["case_id", "source_activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_case_activity_event_source_same_case",
        ),
    )


class CaseActivityEventEvidence(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "t_case_activity_event_evidence"

    case_id: Mapped[str] = mapped_column(String(36), nullable=False)
    activity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    evidence_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    object_type: Mapped[str] = mapped_column(String(64), nullable=False)
    object_id: Mapped[str] = mapped_column(String(36), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["case_id", "activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_case_activity_event_evidence_activity_same_case",
        ),
        UniqueConstraint(
            "case_id",
            "activity_id",
            "evidence_kind",
            "object_type",
            "object_id",
            name="uq_t_case_activity_event_evidence_link",
        ),
    )


class T_CaseAgentSplit(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """Current effective case-level agent split line."""

    __tablename__ = "t_case_agent_split"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    agent_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    share_ratio: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)

    __table_args__ = (UniqueConstraint("case_id", "agent_id", name="uq_case_agent_split_agent"),)


class T_CaseApplicant(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """Case applicant (one or more per case)."""

    __tablename__ = "t_case_applicant"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    applicant_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("t_applicant.id"),
        nullable=True,
        index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)  # Display order
    is_first: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    name_cn: Mapped[str | None] = mapped_column(String(200), nullable=True)
    name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    address_cn: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    certificate_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    certificate_no: Mapped[str | None] = mapped_column(String(128), nullable=True)
    official_postcode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    official_applicant_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)

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
    nationality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    china_id_no: Mapped[str | None] = mapped_column(String(64), nullable=True)

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


class T_BioDeposit(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """Bio deposit records attached to a case."""

    __tablename__ = "t_bio_deposit"

    case_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("t_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    deposit_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deposit_unit_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deposit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("case_id", "seq", name="uq_bio_deposit_seq"),)
