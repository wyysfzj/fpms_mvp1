"""add grant-evidence source, configuration and candidate carriers

Revision ID: v8_grant_source_carrier_01
Revises: v8_d31_overlay_conflict_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_grant_source_carrier_01"
down_revision = "v8_d31_overlay_conflict_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_grant_evidence_source_record",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("source_authority", sa.String(32), nullable=False),
        sa.Column("source_code", sa.String(64), nullable=False),
        sa.Column("source_version", sa.String(128), nullable=False),
        sa.Column("evidence_scope", sa.String(32), nullable=False),
        sa.Column("source_reference_kind", sa.String(32), nullable=False),
        sa.Column("source_reference_value", sa.String(512), nullable=False),
        sa.Column("acquisition_method", sa.String(64), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=False), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=False), nullable=True),
        sa.Column("source_snapshot", sa.Text(), nullable=False),
        sa.Column("source_snapshot_hash", sa.String(64), nullable=False),
        sa.Column(
            "review_status",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("review_reason", sa.Text(), nullable=True),
        sa.Column(
            "activation_status",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'INACTIVE'"),
        ),
        sa.Column("activated_by", sa.String(36), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("supersedes_source_id", sa.String(36), nullable=True),
        sa.Column("current_identity_key", sa.String(128), nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("updated_by", sa.String(36), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_authority",
            "evidence_scope",
            "source_code",
            "source_version",
            name="uq_t_grant_evidence_source_record_series_version",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_evidence_source_record_idempotency_key",
        ),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_evidence_source_record_current_identity_key",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_created_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_updated_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_reviewed_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["activated_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_record_activated_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_source_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_evidence_source_record_supersedes_source_id",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "source_authority = 'CNIPA'",
            name="ck_t_grant_evidence_source_record_authority",
        ),
        sa.CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_evidence_source_record_scope",
        ),
        sa.CheckConstraint(
            "source_reference_kind IN ('DATA', 'QUERY_CHANNEL', 'FILE')",
            name="ck_t_grant_evidence_source_record_reference_kind",
        ),
        sa.CheckConstraint(
            "length(source_snapshot_hash) = 64",
            name="ck_t_grant_evidence_source_record_hash_length",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_grant_evidence_source_record_interval",
        ),
        sa.CheckConstraint(
            "review_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_t_grant_evidence_source_record_review_status",
        ),
        sa.CheckConstraint(
            "(review_status = 'PENDING' AND reviewed_by IS NULL "
            "AND reviewed_at IS NULL AND review_reason IS NULL) OR "
            "(review_status IN ('APPROVED', 'REJECTED') "
            "AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL "
            "AND review_reason IS NOT NULL AND reviewed_by <> created_by)",
            name="ck_t_grant_evidence_source_record_review_tuple",
        ),
        sa.CheckConstraint(
            "activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')",
            name="ck_t_grant_evidence_source_record_activation_status",
        ),
        sa.CheckConstraint(
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
    )
    op.create_table(
        "t_grant_evidence_source_config",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("gate_code", sa.String(32), nullable=False),
        sa.Column("scope_key", sa.String(64), nullable=False),
        sa.Column("evidence_scope", sa.String(32), nullable=False),
        sa.Column("source_record_id", sa.String(36), nullable=False),
        sa.Column("config_version", sa.String(128), nullable=False),
        sa.Column("config_status", sa.String(32), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=False), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=False), nullable=True),
        sa.Column("selected_by", sa.String(36), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("selection_reason", sa.Text(), nullable=False),
        sa.Column("supersedes_config_id", sa.String(36), nullable=True),
        sa.Column("config_snapshot", sa.Text(), nullable=False),
        sa.Column("config_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("current_identity_key", sa.String(160), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "gate_code",
            "scope_key",
            "evidence_scope",
            "config_version",
            name="uq_t_grant_evidence_source_config_version",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_evidence_source_config_idempotency_key",
        ),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_evidence_source_config_current_identity_key",
        ),
        sa.ForeignKeyConstraint(
            ["source_record_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_evidence_source_config_source_record_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["selected_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_source_config_selected_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_config_id"],
            ["t_grant_evidence_source_config.id"],
            name="fk_t_grant_evidence_source_config_supersedes_config_id",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "gate_code = 'DG-GRANT-EVIDENCE-SOURCE' AND scope_key = 'GLOBAL'",
            name="ck_t_grant_evidence_source_config_gate",
        ),
        sa.CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_evidence_source_config_scope",
        ),
        sa.CheckConstraint(
            "config_status IN ('ACTIVE', 'REVOKED')",
            name="ck_t_grant_evidence_source_config_status",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_grant_evidence_source_config_interval",
        ),
        sa.CheckConstraint(
            "length(config_snapshot_hash) = 64",
            name="ck_t_grant_evidence_source_config_hash_length",
        ),
        sa.CheckConstraint(
            "current_identity_key IS NULL OR current_identity_key = gate_code || '|' "
            "|| scope_key || '|' || evidence_scope",
            name="ck_t_grant_evidence_source_config_current_key",
        ),
    )
    op.create_table(
        "t_grant_evidence_candidate",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("evidence_version_id", sa.String(36), nullable=False),
        sa.Column("source_config_id", sa.String(36), nullable=False),
        sa.Column("source_record_id", sa.String(36), nullable=False),
        sa.Column("evidence_scope", sa.String(32), nullable=False),
        sa.Column("source_version_snapshot", sa.String(128), nullable=False),
        sa.Column("original_reference", sa.String(512), nullable=False),
        sa.Column("acquisition_method_snapshot", sa.String(64), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("acquisition_snapshot", sa.Text(), nullable=False),
        sa.Column("acquisition_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("candidate_snapshot", sa.Text(), nullable=False),
        sa.Column("candidate_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("proposed_by", sa.String(36), nullable=False),
        sa.Column("proposed_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column(
            "review_status",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
        sa.Column("reviewer_id", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("review_reason", sa.Text(), nullable=True),
        sa.Column("conflict_snapshot", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "evidence_version_id",
            name="uq_t_grant_evidence_candidate_evidence_version_id",
        ),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_grant_evidence_candidate_case_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["t_document.id"],
            name="fk_t_grant_evidence_candidate_document_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_grant_evidence_candidate_evidence_version_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_config_id"],
            ["t_grant_evidence_source_config.id"],
            name="fk_t_grant_evidence_candidate_source_config_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_record_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_evidence_candidate_source_record_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["proposed_by"],
            ["t_user.id"],
            name="fk_t_grant_evidence_candidate_proposed_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["t_user.id"],
            name="fk_t_grant_evidence_candidate_reviewer_id",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_evidence_candidate_scope",
        ),
        sa.CheckConstraint(
            "length(acquisition_snapshot_hash) = 64",
            name="ck_t_grant_evidence_candidate_acquisition_hash_length",
        ),
        sa.CheckConstraint(
            "length(candidate_snapshot_hash) = 64",
            name="ck_t_grant_evidence_candidate_candidate_hash_length",
        ),
        sa.CheckConstraint(
            "review_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_t_grant_evidence_candidate_review_status",
        ),
        sa.CheckConstraint(
            "(review_status = 'PENDING' AND reviewer_id IS NULL "
            "AND reviewed_at IS NULL AND review_reason IS NULL) OR "
            "(review_status IN ('APPROVED', 'REJECTED') "
            "AND reviewer_id IS NOT NULL AND reviewed_at IS NOT NULL "
            "AND review_reason IS NOT NULL AND reviewer_id <> proposed_by)",
            name="ck_t_grant_evidence_candidate_review_tuple",
        ),
    )
    op.create_index(
        "ix_t_grant_evidence_source_record_scope_interval",
        "t_grant_evidence_source_record",
        ["evidence_scope", "activation_status", "effective_from", "effective_to"],
        unique=False,
    )
    op.create_index(
        "ix_t_grant_evidence_source_config_scope_interval",
        "t_grant_evidence_source_config",
        [
            "scope_key",
            "evidence_scope",
            "config_status",
            "effective_from",
            "effective_to",
        ],
        unique=False,
    )
    op.create_index(
        "ix_t_grant_evidence_candidate_document_review",
        "t_grant_evidence_candidate",
        ["document_id", "review_status", "proposed_at"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
