"""pe_be_db_06_create_t_commission_rule

Revision ID: pe_be_db_06_comm_rule_01
Revises: pe_be_db_05_dunning_01
Create Date: 2026-02-28

Create t_commission_rule for commission calculation rules.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_06_comm_rule_01"
down_revision = "pe_be_db_05_dunning_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_commission_rule",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("rule_name", sa.String(128), nullable=False),
        sa.Column("case_type", sa.String(32), nullable=True),
        sa.Column("fee_type", sa.String(32), nullable=True),
        sa.Column("flow_dir", sa.String(32), nullable=True),
        sa.Column("patent_category", sa.String(32), nullable=True),
        sa.Column(
            "s1_rate",
            sa.Numeric(8, 4),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "s2_rate",
            sa.Numeric(8, 4),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "s1_fixed_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "s2_fixed_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "wait_pay",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "force_settle",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
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

    op.create_index("ix_t_commission_rule_case_type", "t_commission_rule", ["case_type"])
    op.create_index("ix_t_commission_rule_fee_type", "t_commission_rule", ["fee_type"])
    op.create_index("ix_t_commission_rule_enabled", "t_commission_rule", ["enabled"])


def downgrade() -> None:
    op.drop_index("ix_t_commission_rule_enabled", table_name="t_commission_rule")
    op.drop_index("ix_t_commission_rule_fee_type", table_name="t_commission_rule")
    op.drop_index("ix_t_commission_rule_case_type", table_name="t_commission_rule")
    op.drop_table("t_commission_rule")
