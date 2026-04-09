"""add expense department carrier

Revision ID: expstat_department_db_01
Revises: deptmaster_db_01
Create Date: 2026-04-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "expstat_department_db_01"
down_revision = "deptmaster_db_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("t_expense") as batch_op:
        batch_op.add_column(sa.Column("department_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_t_expense_department_id_department",
            "t_department",
            ["department_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            "ix_t_expense_department_id",
            ["department_id"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("t_expense") as batch_op:
        batch_op.drop_index("ix_t_expense_department_id")
        batch_op.drop_constraint("fk_t_expense_department_id_department", type_="foreignkey")
        batch_op.drop_column("department_id")
