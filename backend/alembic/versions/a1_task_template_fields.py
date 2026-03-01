"""a1_task_template_fields

Revision ID: a1_task_template_01
Revises: 53f7a0c139cc
Create Date: 2026-02-24

Add deadline calculation fields to t_task_template:
add_days, add_months, inner_offset_days, default_worker_role, description.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a1_task_template_01"
down_revision = "53f7a0c139cc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_task_template"):
        return

    existing = {col["name"] for col in insp.get_columns("t_task_template")}

    new_columns = []
    if "add_days" not in existing:
        new_columns.append(sa.Column("add_days", sa.Integer, nullable=True))
    if "add_months" not in existing:
        new_columns.append(
            sa.Column("add_months", sa.Integer, nullable=True, server_default=sa.text("0"))
        )
    if "inner_offset_days" not in existing:
        new_columns.append(sa.Column("inner_offset_days", sa.Integer, nullable=True))
    if "default_worker_role" not in existing:
        new_columns.append(sa.Column("default_worker_role", sa.String(32), nullable=True))
    if "description" not in existing:
        new_columns.append(sa.Column("description", sa.Text, nullable=True))

    if new_columns:
        with op.batch_alter_table("t_task_template") as batch_op:
            for column in new_columns:
                batch_op.add_column(column)


def downgrade() -> None:
    pass
