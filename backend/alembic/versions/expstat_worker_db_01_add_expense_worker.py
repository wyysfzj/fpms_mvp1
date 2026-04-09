"""Add worker carrier to t_expense.

Revision ID: expstat_worker_db_01
Revises: docsearch_doctype_merge_01
Create Date: 2026-04-09 18:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "expstat_worker_db_01"
down_revision = "docsearch_doctype_merge_01"
branch_labels = None
depends_on = None


def _col_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(f"PRAGMA table_info('{table}')"))
    return any(row[1] == column for row in result)


def _fk_key(fk: dict) -> tuple[tuple[str, ...], str | None, tuple[str, ...]]:
    return (
        tuple(fk.get("constrained_columns") or []),
        fk.get("referred_table"),
        tuple(fk.get("referred_columns") or []),
    )


def _spec_key(columns: list[str], referred_table: str, referred_columns: list[str]) -> tuple[
    tuple[str, ...],
    str,
    tuple[str, ...],
]:
    return (tuple(columns), referred_table, tuple(referred_columns))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_fks = {_fk_key(fk) for fk in insp.get_foreign_keys("t_expense")}
    worker_fk = _spec_key(["worker_id"], "t_user", ["id"])

    with op.batch_alter_table("t_expense") as batch_op:
        if not _col_exists("t_expense", "worker_id"):
            batch_op.add_column(sa.Column("worker_id", sa.String(length=36), nullable=True))
        if worker_fk not in existing_fks:
            batch_op.create_foreign_key(
                "fk_t_expense_worker_id_user",
                "t_user",
                ["worker_id"],
                ["id"],
                ondelete="SET NULL",
            )
        batch_op.create_index("ix_t_expense_worker_id", ["worker_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("t_expense") as batch_op:
        if _col_exists("t_expense", "worker_id"):
            batch_op.drop_index("ix_t_expense_worker_id")
            batch_op.drop_constraint("fk_t_expense_worker_id_user", type_="foreignkey")
            batch_op.drop_column("worker_id")
