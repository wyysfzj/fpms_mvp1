"""casefilter_pre_01_case_applicant_masterdata_link

Revision ID: casefilter_pre_01_case_applicant_masterdata_link_01
Revises: gfpre_db_01_create_t_grant_fee_task_01
Create Date: 2026-04-01

Add the nullable applicant masterdata carrier to t_case_applicant so later
case filtering and payload wiring can join applicant masterdata through a
stable, indexed reference.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "casefilter_pre_01_case_applicant_masterdata_link_01"
down_revision = "gfpre_db_01_create_t_grant_fee_task_01"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table"),
        {"table": table},
    )
    return result.first() is not None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(f"PRAGMA table_info('{table}')"))
    return any(row[1] == column for row in result)


def _fk_key(fk: dict) -> tuple[tuple[str, ...], str | None, tuple[str, ...]]:
    return (
        tuple(fk.get("constrained_columns") or []),
        fk.get("referred_table"),
        tuple(fk.get("referred_columns") or []),
    )


def upgrade() -> None:
    if not _table_exists("t_case_applicant"):
        return

    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_columns = {col["name"] for col in insp.get_columns("t_case_applicant")}
    existing_fks = {_fk_key(fk) for fk in insp.get_foreign_keys("t_case_applicant")}
    existing_indexes = {
        idx["name"] for idx in insp.get_indexes("t_case_applicant") if idx.get("name")
    }

    with op.batch_alter_table("t_case_applicant") as batch_op:
        if "applicant_id" not in existing_columns:
            batch_op.add_column(sa.Column("applicant_id", sa.String(36), nullable=True))
        if (("applicant_id",), "t_applicant", ("id",)) not in existing_fks:
            batch_op.create_foreign_key(
                "fk_case_applicant_applicant_id_applicant",
                "t_applicant",
                ["applicant_id"],
                ["id"],
            )

    if "ix_t_case_applicant_applicant_id" not in existing_indexes and _column_exists(
        "t_case_applicant", "applicant_id"
    ):
        op.create_index(
            "ix_t_case_applicant_applicant_id",
            "t_case_applicant",
            ["applicant_id"],
        )


def downgrade() -> None:
    pass
