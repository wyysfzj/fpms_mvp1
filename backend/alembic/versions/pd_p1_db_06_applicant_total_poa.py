"""pd_p1_db_06_applicant_total_poa

Revision ID: pd_p1_db_06_applicant_total_poa_01
Revises: pd_p1_db_05_letter_handoff_carriers_01
Create Date: 2026-06-11

Add applicant-level total power of attorney number for P1 post-demo
answer-delta readiness.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pd_p1_db_06_applicant_total_poa_01"
down_revision = "pd_p1_db_05_letter_handoff_carriers_01"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return insp.has_table(table)


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(f"PRAGMA table_info('{table}')"))
    return any(row[1] == column for row in result)


def upgrade() -> None:
    if not _table_exists("t_applicant"):
        return

    if _column_exists("t_applicant", "total_power_of_attorney_no"):
        return

    with op.batch_alter_table("t_applicant") as batch_op:
        batch_op.add_column(sa.Column("total_power_of_attorney_no", sa.String(128), nullable=True))


def downgrade() -> None:
    pass
