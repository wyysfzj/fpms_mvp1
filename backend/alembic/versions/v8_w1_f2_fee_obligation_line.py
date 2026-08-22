"""add fee obligation line carrier

Revision ID: v8_w1_f2_fee_obligation_line_01
Revises: v8_w1_f1_fee_obligation_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_f2_fee_obligation_line_01"
down_revision = "v8_w1_f1_fee_obligation_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_fee_obligation_line",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("obligation_id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("source_activity_id", sa.String(36), nullable=False),
        sa.Column("fee_code", sa.String(64), nullable=False),
        sa.Column("fee_name", sa.String(256), nullable=False),
        sa.Column("fee_year_key", sa.Integer(), nullable=False),
        sa.Column("official_full_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("reduction_ratio", sa.Numeric(5, 4), nullable=False),
        sa.Column("payable_amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("source_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("source_date", sa.Date(), nullable=True),
        sa.Column("difference_review_state", sa.String(32), nullable=False),
        sa.Column("current_identity_key", sa.String(64), nullable=True),
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
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_fee_obligation_line_case_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["case_id", "obligation_id"],
            ["t_fee_obligation.case_id", "t_fee_obligation.id"],
            name="fk_t_fee_obligation_line_obligation_same_case",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["case_id", "source_activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_fee_obligation_line_source_activity_same_case",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_fee_obligation_line_current_identity_key",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
