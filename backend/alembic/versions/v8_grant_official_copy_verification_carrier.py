"""add grant official-copy verification event carrier

Revision ID: v8_grant_official_copy_01
Revises: v8_grant_manual_review_role_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_grant_official_copy_01"
down_revision = "v8_grant_manual_review_role_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_grant_official_copy_verification_event",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("evidence_version_id", sa.String(36), nullable=False),
        sa.Column("source_config_id", sa.String(36), nullable=False),
        sa.Column("source_record_id", sa.String(36), nullable=False),
        sa.Column("role_config_id", sa.String(36), nullable=False),
        sa.Column("evidence_scope", sa.String(32), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("actor_id", sa.String(36), nullable=False),
        sa.Column("action_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("original_reference", sa.String(512), nullable=False),
        sa.Column("acquisition_method_snapshot", sa.String(64), nullable=False),
        sa.Column("evidence_content_hash", sa.String(128), nullable=False),
        sa.Column("source_config_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("source_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("role_config_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("predecessor_event_id", sa.String(36), nullable=True),
        sa.Column("event_snapshot", sa.Text(), nullable=False),
        sa.Column("event_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("current_identity_key", sa.String(96), nullable=True),
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
            "event_type",
            name="uq_t_grant_official_copy_event_stage",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_official_copy_event_idempotency_key",
        ),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_official_copy_event_current_identity_key",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_grant_official_copy_event_evidence_version",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_config_id"],
            ["t_grant_evidence_source_config.id"],
            name="fk_t_grant_official_copy_event_source_config",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_record_id"],
            ["t_grant_evidence_source_record.id"],
            name="fk_t_grant_official_copy_event_source_record",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["role_config_id"],
            ["t_grant_manual_review_role_config.id"],
            name="fk_t_grant_official_copy_event_role_config",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["t_user.id"],
            name="fk_t_grant_official_copy_event_actor",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["predecessor_event_id"],
            ["t_grant_official_copy_verification_event.id"],
            name="fk_t_grant_official_copy_event_predecessor",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "evidence_scope IN ('GRANT_ANNOUNCEMENT', 'PATENT_REGISTER')",
            name="ck_t_grant_official_copy_event_scope",
        ),
        sa.CheckConstraint(
            "event_type IN ('ACQUIRED', 'FIRST_VERIFIED', 'SECOND_VERIFIED')",
            name="ck_t_grant_official_copy_event_type",
        ),
        sa.CheckConstraint(
            "(event_type = 'ACQUIRED' AND predecessor_event_id IS NULL) OR "
            "(event_type IN ('FIRST_VERIFIED', 'SECOND_VERIFIED') "
            "AND predecessor_event_id IS NOT NULL)",
            name="ck_t_grant_official_copy_event_predecessor_shape",
        ),
        sa.CheckConstraint(
            "length(source_config_snapshot_hash) = 64 "
            "AND source_config_snapshot_hash = lower(source_config_snapshot_hash) "
            "AND source_config_snapshot_hash NOT GLOB '*[^0-9a-f]*' "
            "AND length(source_snapshot_hash) = 64 "
            "AND source_snapshot_hash = lower(source_snapshot_hash) "
            "AND source_snapshot_hash NOT GLOB '*[^0-9a-f]*' "
            "AND length(role_config_snapshot_hash) = 64 "
            "AND role_config_snapshot_hash = lower(role_config_snapshot_hash) "
            "AND role_config_snapshot_hash NOT GLOB '*[^0-9a-f]*' "
            "AND length(event_snapshot_hash) = 64 "
            "AND event_snapshot_hash = lower(event_snapshot_hash) "
            "AND event_snapshot_hash NOT GLOB '*[^0-9a-f]*'",
            name="ck_t_grant_official_copy_event_hashes",
        ),
        sa.CheckConstraint(
            "length(evidence_content_hash) BETWEEN 1 AND 128 "
            "AND evidence_content_hash = trim(evidence_content_hash) "
            "AND instr(evidence_content_hash, char(0)) = 0",
            name="ck_t_grant_official_copy_event_content_hash",
        ),
        sa.CheckConstraint(
            "current_identity_key IS NULL OR "
            "current_identity_key = 'GRANT_OFFICIAL_COPY|' || evidence_version_id",
            name="ck_t_grant_official_copy_event_current_key",
        ),
    )
    op.create_index(
        "ix_t_grant_official_copy_event_evidence_stage",
        "t_grant_official_copy_verification_event",
        ["evidence_version_id", "event_type", "action_at"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
