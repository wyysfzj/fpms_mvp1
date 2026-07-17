from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    event,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, validates

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
    official_rate_book_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["official_rate_book_id"],
            ["t_fee_rate_book.id"],
            name="fk_t_fee_rate_official_rate_book_id",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "official_rate_book_id IS NULL OR fee_type = 'GOV'",
            name="ck_t_fee_rate_official_book_gov_only",
        ),
        Index(
            "ix_t_fee_rate_official_rate_book_id",
            "official_rate_book_id",
        ),
    )


class OfficialRateBook(Base):
    __tablename__ = "t_fee_rate_book"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    book_code: Mapped[str] = mapped_column(String(64), nullable=False)
    version_code: Mapped[str] = mapped_column(String(128), nullable=False)
    source_authority: Mapped[str] = mapped_column(String(32), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    source_version: Mapped[str] = mapped_column(String(128), nullable=False)
    source_published_on: Mapped[date] = mapped_column(Date, nullable=False)
    source_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    source_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    approval_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )
    approved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    activation_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'INACTIVE'")
    )
    activated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    current_identity_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "source_authority",
            "book_code",
            "version_code",
            name="uq_t_fee_rate_book_series_version",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_fee_rate_book_current_identity_key",
        ),
        ForeignKeyConstraint(
            ["approved_by"],
            ["t_user.id"],
            name="fk_t_fee_rate_book_approved_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["activated_by"],
            ["t_user.id"],
            name="fk_t_fee_rate_book_activated_by",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "source_authority = 'CNIPA'",
            name="ck_t_fee_rate_book_source_authority",
        ),
        CheckConstraint(
            "length(source_snapshot_hash) = 64",
            name="ck_t_fee_rate_book_source_hash",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_t_fee_rate_book_effective_interval",
        ),
        CheckConstraint(
            "approval_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_t_fee_rate_book_approval_status",
        ),
        CheckConstraint(
            "(approval_status = 'PENDING' AND approved_by IS NULL "
            "AND approved_at IS NULL) "
            "OR (approval_status IN ('APPROVED', 'REJECTED') "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL)",
            name="ck_t_fee_rate_book_approval_tuple",
        ),
        CheckConstraint(
            "activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')",
            name="ck_t_fee_rate_book_activation_status",
        ),
        CheckConstraint(
            "(activation_status = 'INACTIVE' AND activated_by IS NULL "
            "AND activated_at IS NULL AND current_identity_key IS NULL) "
            "OR (activation_status = 'ACTIVE' AND approval_status = 'APPROVED' "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND current_identity_key = source_authority || '|' || book_code) "
            "OR (activation_status = 'RETIRED' AND approval_status = 'APPROVED' "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND current_identity_key IS NULL)",
            name="ck_t_fee_rate_book_activation_tuple",
        ),
        Index(
            "ix_t_fee_rate_book_series_interval",
            "source_authority",
            "book_code",
            "activation_status",
            "effective_from",
            "effective_to",
        ),
    )


class FeeObligation(Base):
    __tablename__ = "t_fee_obligation"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    case_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_activity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    fee_domain: Mapped[str] = mapped_column(String(16), nullable=False)
    obligation_type: Mapped[str] = mapped_column(String(64), nullable=False)
    obligation_status: Mapped[str] = mapped_column(String(32), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    source_status: Mapped[str] = mapped_column(String(32), nullable=False)
    client_instruction_status: Mapped[str] = mapped_column(String(32), nullable=False)
    draft_status: Mapped[str] = mapped_column(String(32), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(32), nullable=False)
    official_evidence_status: Mapped[str] = mapped_column(String(32), nullable=False)
    supersedes_obligation_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    supersede_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_fee_obligation_case_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["source_document_id"],
            ["t_document.id"],
            name="fk_t_fee_obligation_source_document_id",
        ),
        ForeignKeyConstraint(
            ["case_id", "source_activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_fee_obligation_source_activity_same_case",
        ),
        ForeignKeyConstraint(
            ["case_id", "supersedes_obligation_id"],
            ["t_fee_obligation.case_id", "t_fee_obligation.id"],
            name="fk_t_fee_obligation_supersedes_same_case",
        ),
        UniqueConstraint(
            "case_id",
            "id",
            name="uq_t_fee_obligation_case_id",
        ),
    )


class FeeObligationLine(Base):
    __tablename__ = "t_fee_obligation_line"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    obligation_id: Mapped[str] = mapped_column(String(36), nullable=False)
    case_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_activity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    fee_code: Mapped[str] = mapped_column(String(64), nullable=False)
    fee_name: Mapped[str] = mapped_column(String(256), nullable=False)
    fee_year_key: Mapped[int] = mapped_column(Integer, nullable=False)
    official_full_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    reduction_ratio: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    payable_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    source_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    source_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    difference_review_state: Mapped[str] = mapped_column(String(32), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_fee_obligation_line_case_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["case_id", "obligation_id"],
            ["t_fee_obligation.case_id", "t_fee_obligation.id"],
            name="fk_t_fee_obligation_line_obligation_same_case",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["case_id", "source_activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_fee_obligation_line_source_activity_same_case",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_fee_obligation_line_current_identity_key",
        ),
    )


class FeeObligationDraftItemLink(Base):
    __tablename__ = "t_fee_obligation_draft_item_link"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    obligation_line_id: Mapped[str] = mapped_column(String(36), nullable=False)
    fee_item_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["obligation_line_id"],
            ["t_fee_obligation_line.id"],
            name="fk_t_fee_obligation_draft_item_link_obligation_line_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["fee_item_id"],
            ["t_fee_item.id"],
            name="fk_t_fee_obligation_draft_item_link_fee_item_id",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "obligation_line_id",
            "fee_item_id",
            name="uq_t_fee_obligation_draft_item_link_pair",
        ),
    )


class FeeObligationPaymentEvidenceLink(Base):
    __tablename__ = "t_fee_obligation_payment_evidence_link"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    obligation_line_id: Mapped[str] = mapped_column(String(36), nullable=False)
    gov_payment_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["obligation_line_id"],
            ["t_fee_obligation_line.id"],
            name="fk_t_fee_obligation_payment_evidence_link_obligation_line_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["gov_payment_id"],
            ["t_gov_payment.id"],
            name="fk_t_fee_obligation_payment_evidence_link_gov_payment_id",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "obligation_line_id",
            "gov_payment_id",
            name="uq_t_fee_obligation_payment_evidence_link_pair",
        ),
    )


class FeeReductionApproval(Base):
    __tablename__ = "t_fee_reduction_approval"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    case_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    applicant_set_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reduction_ratio: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    fee_scope_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    fee_scope_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    fee_year_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fee_year_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_evidence_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    confirmation_status: Mapped[str] = mapped_column(String(32), nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    confirmed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    eligibility_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    approval_identity_key: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_fee_reduction_approval_case_id",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["source_evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_fee_reduction_approval_source_evidence_version_id",
        ),
        CheckConstraint(
            "(scope_type = 'CASE' AND case_id IS NOT NULL AND applicant_set_key IS NULL) OR "
            "(scope_type = 'APPLICANT_SET' AND case_id IS NULL AND applicant_set_key IS NOT NULL)",
            name="ck_t_fee_reduction_approval_scope_exclusive",
        ),
        UniqueConstraint(
            "approval_identity_key",
            name="uq_t_fee_reduction_approval_identity_key",
        ),
    )


class LegacyFeeReductionProvenance(Base):
    __tablename__ = "t_legacy_fee_reduction_provenance"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    case_id: Mapped[str] = mapped_column(String(36), nullable=False)
    legacy_value: Mapped[str] = mapped_column(String(), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(), nullable=False)
    source_version: Mapped[str] = mapped_column(String(), nullable=False)
    source_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    approval_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_legacy_fee_reduction_provenance_case_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_legacy_fee_reduction_provenance_confirmed_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["approval_id"],
            ["t_fee_reduction_approval.id"],
            name="fk_t_legacy_fee_reduction_provenance_approval_id",
            ondelete="RESTRICT",
        ),
        UniqueConstraint(
            "case_id",
            "manifest_hash",
            name="uq_t_legacy_fee_reduction_provenance_case_manifest",
        ),
        CheckConstraint(
            "legacy_value IN ('0', '0.7', '0.85')",
            name="ck_t_legacy_fee_reduction_provenance_legacy_value",
        ),
        CheckConstraint(
            "(legacy_value = '0' AND approval_id IS NULL) OR "
            "(legacy_value IN ('0.7', '0.85') AND approval_id IS NOT NULL)",
            name="ck_t_legacy_fee_reduction_provenance_approval",
        ),
    )

    @validates("legacy_value")
    def validate_legacy_value(self, _key: str, value: str) -> str:
        if not isinstance(value, str) or value not in {"0", "0.7", "0.85"}:
            raise ValueError("legacy_value must be exactly '0', '0.7', or '0.85'")
        return value

    @validates("confirmed_at")
    def validate_confirmed_at(self, _key: str, value: datetime) -> datetime:
        if not isinstance(value, datetime) or value.tzinfo is not None:
            raise ValueError("confirmed_at must be an explicitly supplied naive datetime")
        return value


@event.listens_for(LegacyFeeReductionProvenance, "before_insert")
def validate_legacy_fee_reduction_provenance_insert(
    _mapper, _connection, target: LegacyFeeReductionProvenance
) -> None:
    if target.confirmed_at is None:
        raise ValueError("confirmed_at must be supplied explicitly")
    approval_is_valid = (target.legacy_value == "0" and target.approval_id is None) or (
        target.legacy_value in {"0.7", "0.85"} and target.approval_id is not None
    )
    if not approval_is_valid:
        raise ValueError("approval_id must match the exact legacy_value approval invariant")


@event.listens_for(LegacyFeeReductionProvenance, "before_update")
def reject_legacy_fee_reduction_provenance_update(
    _mapper, _connection, _target: LegacyFeeReductionProvenance
) -> None:
    raise ValueError("legacy fee reduction provenance is immutable")


@event.listens_for(LegacyFeeReductionProvenance, "before_delete")
def reject_legacy_fee_reduction_provenance_delete(
    _mapper, _connection, _target: LegacyFeeReductionProvenance
) -> None:
    raise ValueError("legacy fee reduction provenance is immutable")


class T_GrantFeeTask(Base):
    __tablename__ = "t_grant_fee_task"
    __table_args__ = (
        Index("ux_t_grant_fee_task_source_document_id", "source_document_id", unique=True),
        Index(
            "ux_t_grant_fee_task_supersede_request_key",
            "supersede_request_key",
            unique=True,
        ),
        Index("ix_t_grant_fee_task_superseded_by_task_id", "superseded_by_task_id"),
    )

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
    source_document_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("t_document.id", name="fk_t_grant_fee_task_source_document_id"),
        nullable=True,
    )
    deadline_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    deadline_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    superseded_by_task_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey(
            "t_grant_fee_task.id",
            name="fk_t_grant_fee_task_superseded_by_task_id",
        ),
        nullable=True,
    )
    supersede_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    superseded_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    supersede_request_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
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
