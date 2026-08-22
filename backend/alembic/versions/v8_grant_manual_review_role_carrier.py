"""add grant manual-review role configuration carrier

Revision ID: v8_grant_manual_review_role_01
Revises: v8_future_annuity_exception_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_grant_manual_review_role_01"
down_revision = "v8_future_annuity_exception_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_grant_manual_review_role_config",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("gate_code", sa.String(32), nullable=False),
        sa.Column("scope_key", sa.String(64), nullable=False),
        sa.Column("official_copy_acquirer_role_id", sa.String(36), nullable=False),
        sa.Column("first_verifier_role_id", sa.String(36), nullable=False),
        sa.Column("second_verifier_role_id", sa.String(36), nullable=False),
        sa.Column("manual_review_proposer_role_id", sa.String(36), nullable=False),
        sa.Column("manual_review_second_reviewer_role_id", sa.String(36), nullable=False),
        sa.Column("config_version", sa.String(128), nullable=False),
        sa.Column("config_status", sa.String(32), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=False), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=False), nullable=True),
        sa.Column("confirmed_by", sa.String(36), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("supersedes_config_id", sa.String(36), nullable=True),
        sa.Column("config_snapshot", sa.Text(), nullable=False),
        sa.Column("config_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("current_identity_key", sa.String(128), nullable=True),
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
            "config_version",
            name="uq_t_grant_manual_review_role_config_version",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_t_grant_manual_review_role_config_idempotency_key",
        ),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_grant_manual_review_role_config_current_identity_key",
        ),
        sa.ForeignKeyConstraint(
            ["official_copy_acquirer_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_acquirer_role",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["first_verifier_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_first_verifier_role",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["second_verifier_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_second_verifier_role",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["manual_review_proposer_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_proposer_role",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["manual_review_second_reviewer_role_id"],
            ["t_role.id"],
            name="fk_t_grant_manual_role_config_second_reviewer_role",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_grant_manual_role_config_confirmed_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_config_id"],
            ["t_grant_manual_review_role_config.id"],
            name="fk_t_grant_manual_role_config_supersedes_config",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "gate_code = 'DG-GRANT-MANUAL-REVIEW' AND scope_key = 'GLOBAL'",
            name="ck_t_grant_manual_review_role_config_gate",
        ),
        sa.CheckConstraint(
            "config_status IN ('ACTIVE', 'REVOKED')",
            name="ck_t_grant_manual_review_role_config_status",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_grant_manual_review_role_config_interval",
        ),
        sa.CheckConstraint(
            "length(config_snapshot_hash) = 64 "
            "AND config_snapshot_hash = lower(config_snapshot_hash) "
            "AND config_snapshot_hash NOT GLOB '*[^0-9a-f]*'",
            name="ck_t_grant_manual_review_role_config_hash",
        ),
        sa.CheckConstraint(
            "current_identity_key IS NULL OR "
            "current_identity_key = gate_code || '|' || scope_key",
            name="ck_t_grant_manual_review_role_config_current_key",
        ),
    )
    op.create_index(
        "ix_t_grant_manual_review_role_config_interval",
        "t_grant_manual_review_role_config",
        ["scope_key", "config_status", "effective_from", "effective_to"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
