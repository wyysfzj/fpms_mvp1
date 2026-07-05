"""pd_fee_scenario_rate_metadata

Revision ID: pd_fee_scenario_rate_metadata_01
Revises: pd_p1_db_06_applicant_total_poa_01
Create Date: 2026-07-05

Add auditable source metadata fields to t_fee_rate for post-demo official fee
scenario parameterization.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pd_fee_scenario_rate_metadata_01"
down_revision = "pd_p1_db_06_applicant_total_poa_01"
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
    if not _table_exists("t_fee_rate"):
        return

    columns = [
        ("fee_domain", sa.String(32)),
        ("fee_section", sa.String(128)),
        ("fee_category", sa.String(128)),
        ("fee_subtype", sa.String(128)),
        ("reduction_scope", sa.String(256)),
        ("source_doc", sa.String(256)),
        ("source_url", sa.String(512)),
        ("source_policy", sa.String(256)),
        ("source_version", sa.String(64)),
        ("source_status", sa.String(32)),
    ]

    with op.batch_alter_table("t_fee_rate") as batch_op:
        for column_name, column_type in columns:
            if not _column_exists("t_fee_rate", column_name):
                batch_op.add_column(sa.Column(column_name, column_type, nullable=True))


def downgrade() -> None:
    pass
