from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    event,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CustomerDecisionGate(Base):
    __tablename__ = "t_customer_decision_gate"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    gate_code: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_key: Mapped[str] = mapped_column(String(256), nullable=False)
    decision_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_status: Mapped[str] = mapped_column(String(32), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    source_version: Mapped[str] = mapped_column(String(128), nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    supersedes_gate_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    decision_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(320), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        CheckConstraint(
            "gate_code IN ("
            "'DG-FEE-APPLICATION-DRAFT', "
            "'DG-FEE-GRANT-YEAR-DRAFT', "
            "'DG-FEE-FUTURE-ANNUITY', "
            "'DG-GRANT-EVIDENCE-SOURCE', "
            "'DG-GRANT-MANUAL-REVIEW', "
            "'DG-PAYMENT-WORKBOOK', "
            "'DG-SERVICE-RATE-VERSION', "
            "'DG-LEGACY-FORM-CLASS'"
            ")",
            name="ck_t_customer_decision_gate_gate_code",
        ),
        CheckConstraint(
            "decision_status IN ('CONFIRMED', 'REVOKED')",
            name="ck_t_customer_decision_gate_decision_status",
        ),
        ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_customer_decision_gate_confirmed_by",
        ),
        ForeignKeyConstraint(
            ["supersedes_gate_id"],
            ["t_customer_decision_gate.id"],
            name="fk_t_customer_decision_gate_supersedes_gate_id",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_customer_decision_gate_idempotency_key",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_customer_decision_gate_current_identity_key",
        ),
    )


class GrantEvidenceSourceRecord(Base):
    __tablename__ = "t_grant_evidence_source_record"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_authority: Mapped[str] = mapped_column(String(32), nullable=False)
    source_code: Mapped[str] = mapped_column(String(64), nullable=False)
    source_version: Mapped[str] = mapped_column(String(128), nullable=False)
    evidence_scope: Mapped[str] = mapped_column(String(32), nullable=False)
    source_reference_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    source_reference_value: Mapped[str] = mapped_column(String(512), nullable=False)
    acquisition_method: Mapped[str] = mapped_column(String(64), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    source_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    source_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    activation_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'INACTIVE'")
    )
    activated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    supersedes_source_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    current_identity_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_by: Mapped[str] = mapped_column(String(36), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "source_authority",
            "evidence_scope",
            "source_code",
            "source_version",
            name="uq_t_grant_evidence_source_record_series_version",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_evidence_source_record_idempotency_key",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_evidence_source_record_current_identity_key",
        ),
        ForeignKeyConstraint(
            ["created_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_created_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["updated_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_updated_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["reviewed_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_reviewed_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["activated_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_activated_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["supersedes_source_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_evidence_source_record_supersedes_source_id",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "source_authority = 'CNIPA'",
            name="ck_t_grant_evidence_source_record_authority",
        ),
        CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_evidence_source_record_scope",
        ),
        CheckConstraint(
            "source_reference_kind IN ('DATA', 'QUERY_CHANNEL', 'FILE')",
            name="ck_t_grant_evidence_source_record_reference_kind",
        ),
        CheckConstraint(
            "length(source_snapshot_hash) = 64",
            name="ck_t_grant_evidence_source_record_hash_length",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_grant_evidence_source_record_interval",
        ),
        CheckConstraint(
            "review_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_t_grant_evidence_source_record_review_status",
        ),
        CheckConstraint(
            "(review_status = 'PENDING' AND reviewed_by IS NULL "
            "AND reviewed_at IS NULL AND review_reason IS NULL) OR "
            "(review_status IN ('APPROVED', 'REJECTED') "
            "AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL "
            "AND review_reason IS NOT NULL AND reviewed_by <> created_by)",
            name="ck_t_grant_evidence_source_record_review_tuple",
        ),
        CheckConstraint(
            "activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')",
            name="ck_t_grant_evidence_source_record_activation_status",
        ),
        CheckConstraint(
            "(activation_status = 'INACTIVE' AND activated_by IS NULL "
            "AND activated_at IS NULL AND current_identity_key IS NULL) OR "
            "(activation_status = 'ACTIVE' AND review_status = 'APPROVED' "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND current_identity_key = source_authority || '|' || evidence_scope "
            "|| '|' || source_code) OR "
            "(activation_status = 'RETIRED' AND review_status = 'APPROVED' "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND current_identity_key IS NULL)",
            name="ck_t_grant_evidence_source_record_activation_tuple",
        ),
        Index(
            "ix_t_grant_evidence_source_record_scope_interval",
            "evidence_scope",
            "activation_status",
            "effective_from",
            "effective_to",
        ),
    )


class GrantEvidenceSourceConfig(Base):
    __tablename__ = "t_grant_evidence_source_config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    gate_code: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_scope: Mapped[str] = mapped_column(String(32), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(36), nullable=False)
    config_version: Mapped[str] = mapped_column(String(128), nullable=False)
    config_status: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    selected_by: Mapped[str] = mapped_column(String(36), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    selection_reason: Mapped[str] = mapped_column(Text, nullable=False)
    supersedes_config_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    config_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    config_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "gate_code",
            "scope_key",
            "evidence_scope",
            "config_version",
            name="uq_t_grant_evidence_source_config_version",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_evidence_source_config_idempotency_key",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_evidence_source_config_current_identity_key",
        ),
        ForeignKeyConstraint(
            ["source_record_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_evidence_source_config_source_record_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["selected_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_config_selected_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["supersedes_config_id"],
            ["t_grant_evidence_source_config.id"],
            name="fk_t_grant_evidence_source_config_supersedes_config_id",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "gate_code = 'DG-GRANT-EVIDENCE-SOURCE' AND scope_key = 'GLOBAL'",
            name="ck_t_grant_evidence_source_config_gate",
        ),
        CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_evidence_source_config_scope",
        ),
        CheckConstraint(
            "config_status IN ('ACTIVE', 'REVOKED')",
            name="ck_t_grant_evidence_source_config_status",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_grant_evidence_source_config_interval",
        ),
        CheckConstraint(
            "length(config_snapshot_hash) = 64",
            name="ck_t_grant_evidence_source_config_hash_length",
        ),
        CheckConstraint(
            "current_identity_key IS NULL OR current_identity_key = gate_code || '|' "
            "|| scope_key || '|' || evidence_scope",
            name="ck_t_grant_evidence_source_config_current_key",
        ),
        Index(
            "ix_t_grant_evidence_source_config_scope_interval",
            "scope_key",
            "evidence_scope",
            "config_status",
            "effective_from",
            "effective_to",
        ),
    )


class FutureAnnuityDraftExceptionRecord(Base):
    __tablename__ = "t_future_annuity_draft_exception_record"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    record_type: Mapped[str] = mapped_column(String(16), nullable=False)
    scope_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    client_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    case_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    target_publication_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    record_version: Mapped[str] = mapped_column(String(128), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    source_version: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    record_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    record_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "record_version",
            name="uq_t_future_annuity_draft_exception_record_version",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_future_annuity_draft_exception_idempotency_key",
        ),
        UniqueConstraint(
            "target_publication_id",
            name="uq_t_future_annuity_draft_exception_target_publication_id",
        ),
        ForeignKeyConstraint(
            ["client_id"],
            ["t_client.id"],
            name="fk_t_future_annuity_draft_exception_client_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_future_annuity_draft_exception_case_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["target_publication_id"],
            ["t_future_annuity_draft_exception_record.id"],
            name="fk_t_future_annuity_draft_exception_target_id",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_future_annuity_draft_exception_confirmed_by",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "record_type IN ('PUBLISHED', 'REVOKED')",
            name="ck_t_future_annuity_draft_exception_record_type",
        ),
        CheckConstraint(
            "length(record_snapshot_hash) = 64 "
            "AND record_snapshot_hash = lower(record_snapshot_hash) "
            "AND record_snapshot_hash NOT GLOB '*[^0-9a-f]*'",
            name="ck_t_future_annuity_draft_exception_hash",
        ),
        CheckConstraint(
            "(record_type = 'PUBLISHED' AND target_publication_id IS NULL "
            "AND scope_type IS NOT NULL AND scope_type IN ('CLIENT', 'CASE') "
            "AND effective_from IS NOT NULL AND effective_to IS NOT NULL "
            "AND effective_to > effective_from "
            "AND ((scope_type = 'CLIENT' AND client_id IS NOT NULL AND case_id IS NULL) "
            "OR (scope_type = 'CASE' AND client_id IS NULL AND case_id IS NOT NULL))) "
            "OR (record_type = 'REVOKED' AND target_publication_id IS NOT NULL "
            "AND scope_type IS NULL AND client_id IS NULL AND case_id IS NULL "
            "AND effective_from IS NULL AND effective_to IS NULL)",
            name="ck_t_future_annuity_draft_exception_shape",
        ),
        Index(
            "ix_t_future_annuity_draft_exception_client_interval",
            "client_id",
            "record_type",
            "effective_from",
            "effective_to",
            "effective_at",
        ),
        Index(
            "ix_t_future_annuity_draft_exception_case_interval",
            "case_id",
            "record_type",
            "effective_from",
            "effective_to",
            "effective_at",
        ),
        Index(
            "ix_t_future_annuity_draft_exception_target",
            "target_publication_id",
            "record_type",
            "effective_at",
        ),
    )


@event.listens_for(FutureAnnuityDraftExceptionRecord, "before_update")
@event.listens_for(FutureAnnuityDraftExceptionRecord, "before_delete")
def _prevent_future_annuity_exception_mutation(
    *_args: object,
    **_kwargs: object,
) -> None:
    raise ValueError("future annuity draft exception record is append-only")


class GrantManualReviewRoleConfig(Base):
    __tablename__ = "t_grant_manual_review_role_config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    gate_code: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False)
    official_copy_acquirer_role_id: Mapped[str] = mapped_column(String(36), nullable=False)
    first_verifier_role_id: Mapped[str] = mapped_column(String(36), nullable=False)
    second_verifier_role_id: Mapped[str] = mapped_column(String(36), nullable=False)
    manual_review_proposer_role_id: Mapped[str] = mapped_column(String(36), nullable=False)
    manual_review_second_reviewer_role_id: Mapped[str] = mapped_column(
        String(36), nullable=False
    )
    config_version: Mapped[str] = mapped_column(String(128), nullable=False)
    config_status: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    confirmed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    supersedes_config_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    config_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    config_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint(
            "config_version",
            name="uq_t_grant_manual_review_role_config_version",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_manual_review_role_config_idempotency_key",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_manual_review_role_config_current_identity_key",
        ),
        ForeignKeyConstraint(
            ["official_copy_acquirer_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_acquirer_role",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["first_verifier_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_first_verifier_role",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["second_verifier_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_second_verifier_role",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["manual_review_proposer_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_proposer_role",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["manual_review_second_reviewer_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_second_reviewer_role",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_grant_manual_role_config_confirmed_by",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["supersedes_config_id"],
            ["t_grant_manual_review_role_config.id"],
            name="fk_t_grant_manual_role_config_supersedes_config",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "gate_code = 'DG-GRANT-MANUAL-REVIEW' AND scope_key = 'GLOBAL'",
            name="ck_t_grant_manual_review_role_config_gate",
        ),
        CheckConstraint(
            "config_status IN ('ACTIVE', 'REVOKED')",
            name="ck_t_grant_manual_review_role_config_status",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_grant_manual_review_role_config_interval",
        ),
        CheckConstraint(
            "length(config_snapshot_hash) = 64 "
            "AND config_snapshot_hash = lower(config_snapshot_hash) "
            "AND config_snapshot_hash NOT GLOB '*[^0-9a-f]*'",
            name="ck_t_grant_manual_review_role_config_hash",
        ),
        CheckConstraint(
            "current_identity_key IS NULL OR "
            "current_identity_key = gate_code || '|' || scope_key",
            name="ck_t_grant_manual_review_role_config_current_key",
        ),
        Index(
            "ix_t_grant_manual_review_role_config_interval",
            "scope_key",
            "config_status",
            "effective_from",
            "effective_to",
        ),
    )
