"""pe_be_db_01_create_t_expense

Revision ID: pe_be_db_01_expense_01
Revises: b5_case_receipt_01
Create Date: 2026-02-28

Create t_expense for generic third-party expense records.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_01_expense_01"
down_revision = "b5_case_receipt_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_expense",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "case_id",
            sa.String(36),
            sa.ForeignKey("t_case.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("expense_no", sa.String(64), nullable=True),
        sa.Column("category", sa.String(32), nullable=False, server_default=sa.text("'OTHER'")),
        sa.Column("vendor_name", sa.String(255), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("tax_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'DRAFT'")),
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

    op.create_index("ix_t_expense_case_id", "t_expense", ["case_id"])
    op.create_index("ix_t_expense_client_id", "t_expense", ["client_id"])
    op.create_index("ix_t_expense_expense_date", "t_expense", ["expense_date"])


def downgrade() -> None:
    op.drop_index("ix_t_expense_expense_date", table_name="t_expense")
    op.drop_index("ix_t_expense_client_id", table_name="t_expense")
    op.drop_index("ix_t_expense_case_id", table_name="t_expense")
    op.drop_table("t_expense")
