"""fee rate + fee draft + fee items

Revision ID: 0004_fees
Revises: 0003_tasks
Create Date: 2025-12-20T16:24:58
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_fees"
down_revision = "0003_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_fee_rate",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("fee_code", sa.String(64), nullable=False),
        sa.Column("fee_name", sa.String(256), nullable=True),
        sa.Column("fee_type", sa.String(16), nullable=False, server_default=sa.text("'SERVICE'")),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("default_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )

    op.create_table(
        "t_fee_draft",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "case_id", sa.String(36), sa.ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("client_id", sa.String(36), sa.ForeignKey("t_client.id"), nullable=True),
        sa.Column("draft_type", sa.String(32), nullable=False, server_default=sa.text("'GENERIC'")),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column("total_gov", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_service", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_misc", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("idx_fee_draft_case", "t_fee_draft", ["case_id", "status"])

    op.create_table(
        "t_fee_item",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "draft_id",
            sa.String(36),
            sa.ForeignKey("t_fee_draft.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("t_case.id"), nullable=True),
        sa.Column("rate_id", sa.String(36), sa.ForeignKey("t_fee_rate.id"), nullable=True),
        sa.Column("fee_code", sa.String(64), nullable=True),
        sa.Column("fee_name", sa.String(256), nullable=True),
        sa.Column("fee_type", sa.String(16), nullable=False, server_default=sa.text("'SERVICE'")),
        sa.Column("year_no", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=True),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("remark", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    raise NotImplementedError("Downgrade not implemented for MVP migrations (intentional).")
