"""pe_fr_fe_07_case_receipt_ext

Revision ID: pe_fr_fe_07_01
Revises: pe_be_db_cm_02_case_ext_01
Create Date: 2026-03-24

Add 4 columns to t_case_receipt: fee_name, due_date, is_prepayment, remark.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_fr_fe_07_01"
down_revision = "pe_be_db_cm_02_case_ext_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_case_receipt"):
        return

    existing = {col["name"] for col in insp.get_columns("t_case_receipt")}

    columns = [
        ("fee_name", sa.String(128), None),
        ("due_date", sa.Date(), None),
        ("is_prepayment", sa.Boolean(), sa.text("0")),
        ("remark", sa.String(512), None),
    ]

    with op.batch_alter_table("t_case_receipt") as batch_op:
        for col_name, col_type, server_default in columns:
            if col_name not in existing:
                batch_op.add_column(
                    sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                )


def downgrade() -> None:
    pass
