"""casebf_db_01_case_submitted_date

Revision ID: casebf_db_01_case_submitted_date_01
Revises: casefld_db_01_case_missing_fields_01
Create Date: 2026-03-30

Add submitted_date to t_case for the batch filing workflow.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "casebf_db_01_case_submitted_date_01"
down_revision = "casefld_db_01_case_missing_fields_01"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table"),
        {"table": table},
    )
    return result.first() is not None


def upgrade() -> None:
    if not _table_exists("t_case"):
        return

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("t_case")}

    if "submitted_date" in existing_columns:
        return

    with op.batch_alter_table("t_case") as batch_op:
        batch_op.add_column(sa.Column("submitted_date", sa.Date(), nullable=True))


def downgrade() -> None:
    pass
