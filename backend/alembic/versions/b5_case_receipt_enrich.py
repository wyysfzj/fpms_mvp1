"""b5_case_receipt_enrich

Revision ID: b5_case_receipt_01
Revises: b4_fee_rate_dims_01
Create Date: 2026-02-26

Add 5 enrichment columns to t_case_receipt.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b5_case_receipt_01"
down_revision = "b4_fee_rate_dims_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_case_receipt"):
        return

    existing = {col["name"] for col in insp.get_columns("t_case_receipt")}

    columns = [
        ("fee_code", sa.String(64), None),
        ("year_no", sa.Integer(), None),
        ("is_arrears", sa.Boolean(), sa.text("0")),
        ("invoice_no", sa.String(64), None),
        ("is_commissionable", sa.Boolean(), sa.text("0")),
    ]

    with op.batch_alter_table("t_case_receipt") as batch_op:
        for col_name, col_type, server_default in columns:
            if col_name not in existing:
                batch_op.add_column(
                    sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                )


def downgrade() -> None:
    pass
