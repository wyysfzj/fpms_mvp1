"""add future-annuity draft-exception carrier

Revision ID: v8_future_annuity_exception_01
Revises: v8_grant_source_carrier_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_future_annuity_exception_01"
down_revision = "v8_grant_source_carrier_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_future_annuity_draft_exception_record",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("record_type", sa.String(16), nullable=False),
        sa.Column("scope_type", sa.String(16), nullable=True),
        sa.Column("client_id", sa.String(36), nullable=True),
        sa.Column("case_id", sa.String(36), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=False), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=False), nullable=True),
        sa.Column("target_publication_id", sa.String(36), nullable=True),
        sa.Column("record_version", sa.String(128), nullable=False),
        sa.Column("source_reference", sa.String(512), nullable=False),
        sa.Column("source_version", sa.String(128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("record_snapshot", sa.Text(), nullable=False),
        sa.Column("record_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("confirmed_by", sa.String(36), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "record_version",
            name="uq_t_future_annuity_draft_exception_record_version",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_t_future_annuity_draft_exception_idempotency_key",
        ),
        sa.UniqueConstraint(
            "target_publication_id",
            name="uq_t_future_annuity_draft_exception_target_publication_id",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["t_client.id"],
            name="fk_t_future_annuity_draft_exception_client_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_future_annuity_draft_exception_case_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["target_publication_id"],
            ["t_future_annuity_draft_exception_record.id"],
            name="fk_t_future_annuity_draft_exception_target_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_future_annuity_draft_exception_confirmed_by",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "record_type IN ('PUBLISHED', 'REVOKED')",
            name="ck_t_future_annuity_draft_exception_record_type",
        ),
        sa.CheckConstraint(
            "length(record_snapshot_hash) = 64 "
            "AND record_snapshot_hash = lower(record_snapshot_hash) "
            "AND record_snapshot_hash NOT GLOB '*[^0-9a-f]*'",
            name="ck_t_future_annuity_draft_exception_hash",
        ),
        sa.CheckConstraint(
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
    )
    op.create_index(
        "ix_t_future_annuity_draft_exception_client_interval",
        "t_future_annuity_draft_exception_record",
        ["client_id", "record_type", "effective_from", "effective_to", "effective_at"],
        unique=False,
    )
    op.create_index(
        "ix_t_future_annuity_draft_exception_case_interval",
        "t_future_annuity_draft_exception_record",
        ["case_id", "record_type", "effective_from", "effective_to", "effective_at"],
        unique=False,
    )
    op.create_index(
        "ix_t_future_annuity_draft_exception_target",
        "t_future_annuity_draft_exception_record",
        ["target_publication_id", "record_type", "effective_at"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
