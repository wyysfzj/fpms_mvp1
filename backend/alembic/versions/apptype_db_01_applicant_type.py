"""apptype_db_01_applicant_type

Revision ID: apptype_db_01_applicant_type_01
Revises: expstat_department_db_01
Create Date: 2026-04-18

Add persisted applicant_type to t_applicant and backfill existing rows with
the default ENTITY value in a SQLite-safe way.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "apptype_db_01_applicant_type_01"
down_revision = "expstat_department_db_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_applicant"):
        return

    existing = {col["name"] for col in insp.get_columns("t_applicant")}

    if "applicant_type" not in existing:
        with op.batch_alter_table("t_applicant") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "applicant_type",
                    sa.String(16),
                    nullable=False,
                    server_default=sa.text("'ENTITY'"),
                )
            )

    bind.execute(
        sa.text(
            """
            UPDATE t_applicant
            SET applicant_type = 'ENTITY'
            WHERE applicant_type IS NULL OR applicant_type = ''
            """
        )
    )


def downgrade() -> None:
    pass
