"""pe_be_db_07_create_t_commission

Revision ID: pe_be_db_07_commission_01
Revises: pe_be_db_06_comm_rule_01
Create Date: 2026-02-28

Create t_commission for commission records.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_07_commission_01"
down_revision = "pe_be_db_06_comm_rule_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_commission",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "case_id",
            sa.String(36),
            sa.ForeignKey("t_case.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("agent_id", sa.String(36), nullable=True),
        sa.Column(
            "rule_id",
            sa.Integer(),
            sa.ForeignKey("t_commission_rule.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("fee_type", sa.String(32), nullable=True),
        sa.Column("base_fee", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("s1_rate", sa.Numeric(8, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("s1_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("s1_done", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("s2_rate", sa.Numeric(8, 4), nullable=False, server_default=sa.text("0")),
        sa.Column("s2_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("s2_done", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("wait_pay", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("force_settle", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column("is_settleable", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("settleable_date", sa.Date(), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
    )

    op.create_index("ix_t_commission_case_id", "t_commission", ["case_id"])
    op.create_index("ix_t_commission_agent_id", "t_commission", ["agent_id"])
    op.create_index("ix_t_commission_status", "t_commission", ["status"])
    op.create_index("ix_t_commission_is_settleable", "t_commission", ["is_settleable"])


def downgrade() -> None:
    op.drop_index("ix_t_commission_is_settleable", table_name="t_commission")
    op.drop_index("ix_t_commission_status", table_name="t_commission")
    op.drop_index("ix_t_commission_agent_id", table_name="t_commission")
    op.drop_index("ix_t_commission_case_id", table_name="t_commission")
    op.drop_table("t_commission")
