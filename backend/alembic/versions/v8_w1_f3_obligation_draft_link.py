"""add obligation draft-item link carrier

Revision ID: v8_w1_f3_draft_item_link_01
Revises: v8_w1_f2_fee_obligation_line_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_f3_draft_item_link_01"
down_revision = "v8_w1_f2_fee_obligation_line_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_fee_obligation_draft_item_link",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("obligation_line_id", sa.String(36), nullable=False),
        sa.Column("fee_item_id", sa.String(36), nullable=False),
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
            ["obligation_line_id"],
            ["t_fee_obligation_line.id"],
            name="fk_t_fee_obligation_draft_item_link_obligation_line_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["fee_item_id"],
            ["t_fee_item.id"],
            name="fk_t_fee_obligation_draft_item_link_fee_item_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "obligation_line_id",
            "fee_item_id",
            name="uq_t_fee_obligation_draft_item_link_pair",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
