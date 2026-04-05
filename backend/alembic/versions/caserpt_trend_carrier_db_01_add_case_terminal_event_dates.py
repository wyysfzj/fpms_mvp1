"""caserpt_trend_carrier_db_01_add_case_terminal_event_dates

Revision ID: caserpt_trend_carrier_db_01
Revises: pe_fr_fe_06_01
Create Date: 2026-04-05

Add terminal-event date carriers to t_case for honest case trend reporting.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "caserpt_trend_carrier_db_01"
down_revision = "pe_fr_fe_06_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_case"):
        return

    existing = {col["name"] for col in insp.get_columns("t_case")}
    columns = [
        "terminated_date",
        "invalidated_date",
        "withdrawn_date",
        "abandoned_date",
    ]

    with op.batch_alter_table("t_case") as batch_op:
        for column_name in columns:
            if column_name not in existing:
                batch_op.add_column(sa.Column(column_name, sa.Date(), nullable=True))


def downgrade() -> None:
    pass
