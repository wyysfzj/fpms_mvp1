"""b4_fee_rate_dimensions

Revision ID: b4_fee_rate_dims_01
Revises: b2_doc_reply_01
Create Date: 2026-02-26

Add 9 dimension/calc columns to t_fee_rate.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b4_fee_rate_dims_01"
down_revision = "b2_doc_reply_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_fee_rate"):
        return

    existing = {col["name"] for col in insp.get_columns("t_fee_rate")}

    columns = [
        ("rate_group", sa.String(32), None),
        ("country_code", sa.String(10), None),
        ("case_type", sa.String(32), None),
        ("patent_category", sa.String(32), None),
        ("calc_mode", sa.String(16), sa.text("'FIXED'")),
        ("calc_params", sa.Text(), None),
        ("allow_reduction", sa.Boolean(), sa.text("0")),
        ("effective_from", sa.Date(), None),
        ("effective_to", sa.Date(), None),
    ]

    with op.batch_alter_table("t_fee_rate") as batch_op:
        for col_name, col_type, server_default in columns:
            if col_name not in existing:
                batch_op.add_column(
                    sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                )


def downgrade() -> None:
    pass
