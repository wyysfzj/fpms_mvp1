"""dltpl_db_01_task_template_reminder_fields

Revision ID: dltpl_db_01_task_template_reminder_fields_01
Revises: baddebt_db_01_create_bad_debt_tables_01
Create Date: 2026-03-29

Add reminder configuration fields to t_task_template and runtime reminder
fields to t_task, keeping the change SQLite-safe and idempotent.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

from app.modules.tasks.enums import TaskDeadlineBase, TaskRemindBase

revision = "dltpl_db_01_task_template_reminder_fields_01"
down_revision = "baddebt_db_01_create_bad_debt_tables_01"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table"),
        {"table": table},
    )
    return result.first() is not None


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

    if _table_exists("t_task_template"):
        existing_columns = {col["name"] for col in insp.get_columns("t_task_template")}
        existing_fks = {_fk_key(fk) for fk in insp.get_foreign_keys("t_task_template")}
        template_columns = [
            (
                "deadline_base",
                sa.Enum(
                    TaskDeadlineBase,
                    name="task_deadline_base",
                    native_enum=False,
                    validate_strings=True,
                ),
            ),
            (
                "remind_base",
                sa.Enum(
                    TaskRemindBase,
                    name="task_remind_base",
                    native_enum=False,
                    validate_strings=True,
                ),
            ),
            ("remind_1_offset_days", sa.Integer()),
            ("remind_2_offset_days", sa.Integer()),
            ("remind_3_offset_days", sa.Integer()),
            ("daily_remind", sa.Boolean()),
            ("default_supervisor_id", sa.String(36)),
        ]
        default_supervisor_fk = _spec_key(
            ["default_supervisor_id"],
            "t_user",
            ["id"],
        )
        add_default_supervisor_fk = default_supervisor_fk not in existing_fks
        with op.batch_alter_table("t_task_template") as batch_op:
            for name, column_type in template_columns:
                if name in existing_columns:
                    continue
                if name == "daily_remind":
                    batch_op.add_column(
                        sa.Column(name, column_type, nullable=False, server_default=sa.text("0"))
                    )
                    continue
                if name == "default_supervisor_id":
                    batch_op.add_column(sa.Column(name, column_type, nullable=True))
                    continue
                batch_op.add_column(sa.Column(name, column_type, nullable=True))
            if add_default_supervisor_fk:
                batch_op.create_foreign_key(
                    "fk_task_template_default_supervisor_id_user",
                    "t_user",
                    ["default_supervisor_id"],
                    ["id"],
                )

    if _table_exists("t_task"):
        task_columns = [
            ("remind1", sa.Date()),
            ("remind2", sa.Date()),
            ("remind3", sa.Date()),
            ("daily_remind_from", sa.Date()),
            ("daily_remind", sa.Boolean()),
        ]
        with op.batch_alter_table("t_task") as batch_op:
            for name, column_type in task_columns:
                if _col_exists("t_task", name):
                    continue
                if name == "daily_remind":
                    batch_op.add_column(
                        sa.Column(name, column_type, nullable=False, server_default=sa.text("0"))
                    )
                    continue
                batch_op.add_column(sa.Column(name, column_type, nullable=True))


def downgrade() -> None:
    pass
