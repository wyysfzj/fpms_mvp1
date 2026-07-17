"""add case activity event carrier

Revision ID: v8_w1_l2_case_activity_event_01
Revises: v8_w1_l1_case_lifecycle_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_l2_case_activity_event_01"
down_revision = "v8_w1_l1_case_lifecycle_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_case_activity_event",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("lane", sa.String(16), nullable=False),
        sa.Column("activity_type", sa.String(64), nullable=False),
        sa.Column("source_activity_id", sa.String(36), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("confirmation_status", sa.String(32), nullable=False),
        sa.Column("old_business_stage", sa.String(32), nullable=True),
        sa.Column("new_business_stage", sa.String(32), nullable=True),
        sa.Column("old_official_procedure_stage", sa.String(64), nullable=True),
        sa.Column("new_official_procedure_stage", sa.String(64), nullable=True),
        sa.Column("old_legal_status", sa.String(32), nullable=True),
        sa.Column("new_legal_status", sa.String(32), nullable=True),
        sa.Column("actor_id", sa.String(36), nullable=False),
        sa.Column("reviewer_id", sa.String(36), nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("supersedes_event_id", sa.String(36), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_case_activity_event_case_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["case_id", "source_activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_case_activity_event_source_same_case",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "case_id",
            "sequence",
            name="uq_t_case_activity_event_case_sequence",
        ),
        sa.UniqueConstraint(
            "case_id",
            "idempotency_key",
            name="uq_t_case_activity_event_case_idempotency_key",
        ),
        sa.UniqueConstraint(
            "case_id",
            "id",
            name="uq_t_case_activity_event_case_id",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
