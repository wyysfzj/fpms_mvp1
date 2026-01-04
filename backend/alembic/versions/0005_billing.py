"""billing + payment + offset + case receipt

Revision ID: 0005_billing
Revises: 0004_fees
Create Date: 2025-12-20T16:24:58
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_billing"
down_revision = "0004_fees"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_bill",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bill_no", sa.String(64), nullable=True, unique=True),
        sa.Column("client_id", sa.String(36), sa.ForeignKey("t_client.id"), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("direction", sa.String(8), nullable=False, server_default=sa.text("'AR'")),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'UNSETTLED'")),
        sa.Column("bill_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("total_gov", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_service", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("total_misc", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("idx_bill_client_status_date", "t_bill", ["client_id", "status", "bill_date"])

    op.create_table(
        "t_bill_item",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "bill_id", sa.String(36), sa.ForeignKey("t_bill.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("t_case.id"), nullable=True),
        sa.Column("draft_id", sa.String(36), sa.ForeignKey("t_fee_draft.id"), nullable=True),
        sa.Column("fee_item_id", sa.String(36), sa.ForeignKey("t_fee_item.id"), nullable=True),
        sa.Column("fee_code", sa.String(64), nullable=True),
        sa.Column("fee_name", sa.String(256), nullable=True),
        sa.Column("fee_type", sa.String(16), nullable=True),
        sa.Column("year_no", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
    )

    op.create_table(
        "t_payment",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("pay_no", sa.String(64), nullable=True),
        sa.Column("client_id", sa.String(36), sa.ForeignKey("t_client.id"), nullable=False),
        sa.Column("pay_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("idx_payment_client_date", "t_payment", ["client_id", "pay_date"])

    op.create_table(
        "t_payment_line",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "payment_id",
            sa.String(36),
            sa.ForeignKey("t_payment.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("t_case.id"), nullable=True),
        sa.Column("raw_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("allocated_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("balance_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
    )

    op.create_table(
        "t_offset",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "payment_line_id",
            sa.String(36),
            sa.ForeignKey("t_payment_line.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "bill_id", sa.String(36), sa.ForeignKey("t_bill.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("offset_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("offset_date", sa.Date(), nullable=True),
        sa.Column("is_reversed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("reversed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_offset_bill", "t_offset", ["bill_id"])

    op.create_table(
        "t_case_receipt",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "case_id", sa.String(36), sa.ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("fee_type", sa.String(16), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("receivable_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("received_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("last_receipt_date", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    raise NotImplementedError("Downgrade not implemented for MVP migrations (intentional).")
