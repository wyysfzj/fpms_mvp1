"""baddebt_db_01_create_bad_debt_tables

Revision ID: baddebt_db_01_create_bad_debt_tables_01
Revises: frcom03_db_merge_01_merge_heads
Create Date: 2026-03-28

Create AR bad-debt voucher and recovery tables plus bill bad-debt state carriers.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "baddebt_db_01_create_bad_debt_tables_01"
down_revision = "frcom03_db_merge_01_merge_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "t_bill",
        sa.Column(
            "bad_debt_status",
            sa.String(24),
            nullable=False,
            server_default=sa.text("'NONE'"),
        ),
    )
    op.add_column(
        "t_bill",
        sa.Column("bad_debt_substatus", sa.String(24), nullable=True),
    )
    op.create_index("ix_t_bill_bad_debt_status", "t_bill", ["bad_debt_status"])

    op.create_table(
        "t_bad_debt_voucher",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "bill_id",
            sa.String(36),
            sa.ForeignKey("t_bill.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column(
            "bad_debt_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "recovered_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("bad_debt_date", sa.Date(), nullable=True),
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
        sa.UniqueConstraint("bill_id", name="uq_t_bad_debt_voucher_bill"),
    )
    op.create_index(
        "ix_t_bad_debt_voucher_bill_id", "t_bad_debt_voucher", ["bill_id"]
    )
    op.create_index("ix_t_bad_debt_voucher_status", "t_bad_debt_voucher", ["status"])

    op.create_table(
        "t_bad_debt_recovery",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "voucher_id",
            sa.String(36),
            sa.ForeignKey("t_bad_debt_voucher.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "recovery_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("recovery_date", sa.Date(), nullable=True),
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
    op.create_index(
        "ix_t_bad_debt_recovery_voucher_id", "t_bad_debt_recovery", ["voucher_id"]
    )
    op.create_index(
        "ix_t_bad_debt_recovery_recovery_date", "t_bad_debt_recovery", ["recovery_date"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_t_bad_debt_recovery_recovery_date", table_name="t_bad_debt_recovery"
    )
    op.drop_index("ix_t_bad_debt_recovery_voucher_id", table_name="t_bad_debt_recovery")
    op.drop_table("t_bad_debt_recovery")

    op.drop_index("ix_t_bad_debt_voucher_status", table_name="t_bad_debt_voucher")
    op.drop_index("ix_t_bad_debt_voucher_bill_id", table_name="t_bad_debt_voucher")
    op.drop_table("t_bad_debt_voucher")

    op.drop_index("ix_t_bill_bad_debt_status", table_name="t_bill")
    op.drop_column("t_bill", "bad_debt_substatus")
    op.drop_column("t_bill", "bad_debt_status")
