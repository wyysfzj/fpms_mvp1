"""pe_be_db_03_create_t_gov_payment

Revision ID: pe_be_db_03_gov_payment_01
Revises: pe_be_db_02_pay_list_01
Create Date: 2026-02-28

Create t_gov_payment for official payment detail records.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_03_gov_payment_01"
down_revision = "pe_be_db_02_pay_list_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_gov_payment",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "pay_list_id",
            sa.Integer(),
            sa.ForeignKey("t_pay_list.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "case_id",
            sa.String(36),
            sa.ForeignKey("t_case.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "fee_item_id",
            sa.String(36),
            sa.ForeignKey("t_fee_item.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'RECORDED'")),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column("paid_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("official_receipt_no", sa.String(64), nullable=True),
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

    op.create_index("ix_t_gov_payment_pay_list_id", "t_gov_payment", ["pay_list_id"])
    op.create_index("ix_t_gov_payment_case_id", "t_gov_payment", ["case_id"])
    op.create_index("ix_t_gov_payment_fee_item_id", "t_gov_payment", ["fee_item_id"])
    op.create_index("ix_t_gov_payment_paid_date", "t_gov_payment", ["paid_date"])


def downgrade() -> None:
    op.drop_index("ix_t_gov_payment_paid_date", table_name="t_gov_payment")
    op.drop_index("ix_t_gov_payment_fee_item_id", table_name="t_gov_payment")
    op.drop_index("ix_t_gov_payment_case_id", table_name="t_gov_payment")
    op.drop_index("ix_t_gov_payment_pay_list_id", table_name="t_gov_payment")
    op.drop_table("t_gov_payment")
