"""pd_p1_db_01_case_official_fields

Revision ID: pd_p1_db_01_case_official_fields_01
Revises: apptype_db_01_applicant_type_01
Create Date: 2026-05-31

Add case applicant/inventor official submission field carriers for P1
post-demo filing and OA workflow readiness.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pd_p1_db_01_case_official_fields_01"
down_revision = "apptype_db_01_applicant_type_01"
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
    if _table_exists("t_case_applicant"):
        applicant_columns = [
            ("nationality", sa.String(64)),
            ("certificate_type", sa.String(32)),
            ("certificate_no", sa.String(128)),
            ("official_postcode", sa.String(32)),
            ("official_applicant_kind", sa.String(32)),
        ]
        with op.batch_alter_table("t_case_applicant") as batch_op:
            for column_name, column_type in applicant_columns:
                if not _column_exists("t_case_applicant", column_name):
                    batch_op.add_column(sa.Column(column_name, column_type, nullable=True))

    if _table_exists("t_case_inventor"):
        inventor_columns = [
            ("nationality", sa.String(64)),
            ("china_id_no", sa.String(64)),
        ]
        with op.batch_alter_table("t_case_inventor") as batch_op:
            for column_name, column_type in inventor_columns:
                if not _column_exists("t_case_inventor", column_name):
                    batch_op.add_column(sa.Column(column_name, column_type, nullable=True))


def downgrade() -> None:
    pass
