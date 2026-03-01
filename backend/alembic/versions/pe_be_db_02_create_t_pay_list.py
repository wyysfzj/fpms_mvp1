"""pe_be_db_02_create_t_pay_list

Revision ID: pe_be_db_02_pay_list_01
Revises: pe_be_db_01_expense_01
Create Date: 2026-02-28

Create t_pay_list for gov-fee payment list header.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_02_pay_list_01"
down_revision = "pe_be_db_01_expense_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_pay_list",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("pay_list_no", sa.String(64), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("planned_pay_date", sa.Date(), nullable=True),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
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

    op.create_index("ix_t_pay_list_client_id", "t_pay_list", ["client_id"])
    op.create_index("ix_t_pay_list_status", "t_pay_list", ["status"])
    op.create_index("ix_t_pay_list_planned_pay_date", "t_pay_list", ["planned_pay_date"])


def downgrade() -> None:
    op.drop_index("ix_t_pay_list_planned_pay_date", table_name="t_pay_list")
    op.drop_index("ix_t_pay_list_status", table_name="t_pay_list")
    op.drop_index("ix_t_pay_list_client_id", table_name="t_pay_list")
    op.drop_table("t_pay_list")
