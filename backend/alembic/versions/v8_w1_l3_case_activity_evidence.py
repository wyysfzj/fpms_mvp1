"""add case activity evidence carrier

Revision ID: v8_w1_l3_activity_evidence_01
Revises: v8_w1_l2_case_activity_event_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_l3_activity_evidence_01"
down_revision = "v8_w1_l2_case_activity_event_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_case_activity_event_evidence",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("activity_id", sa.String(36), nullable=False),
        sa.Column("evidence_kind", sa.String(32), nullable=False),
        sa.Column("object_type", sa.String(64), nullable=False),
        sa.Column("object_id", sa.String(36), nullable=False),
        sa.Column("content_hash", sa.String(128), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=False), nullable=False),
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
            ["case_id", "activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_case_activity_event_evidence_activity_same_case",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "case_id",
            "activity_id",
            "evidence_kind",
            "object_type",
            "object_id",
            name="uq_t_case_activity_event_evidence_link",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
