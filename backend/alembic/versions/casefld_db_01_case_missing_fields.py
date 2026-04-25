"""casefld_db_01_case_missing_fields

Revision ID: casefld_db_01_case_missing_fields_01
Revises: dltpl_db_01_task_template_reminder_fields_01
Create Date: 2026-03-29

Add missing structured case fields required by P1 #10 while keeping the
change SQLite-safe and idempotent.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "casefld_db_01_case_missing_fields_01"
down_revision = "dltpl_db_01_task_template_reminder_fields_01"
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


def _spec_key(
    columns: list[str], referred_table: str, referred_columns: list[str]
) -> tuple[tuple[str, ...], str, tuple[str, ...]]:
    return (tuple(columns), referred_table, tuple(referred_columns))


def upgrade() -> None:
    if not _table_exists("t_case"):
        return

    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_columns = {col["name"] for col in insp.get_columns("t_case")}
    existing_fks = {_fk_key(fk) for fk in insp.get_foreign_keys("t_case")}

    case_columns = [
        ("from_country", sa.String(10)),
        ("to_country", sa.String(10)),
        ("doc_address_id", sa.String(36)),
        ("bill_address_id", sa.String(36)),
        ("issue_date", sa.Date()),
        ("cert_no", sa.String(64)),
        ("draw_pages", sa.Integer()),
        ("claim_pages", sa.Integer()),
        ("manuscript_words", sa.Integer()),
        ("discount_rate", sa.Numeric(5, 4)),
        ("no_power", sa.Boolean()),
        ("no_prio_text", sa.Boolean()),
        ("require_hk", sa.Boolean()),
    ]
    doc_address_fk = _spec_key(["doc_address_id"], "t_client_address", ["id"])
    bill_address_fk = _spec_key(["bill_address_id"], "t_client_address", ["id"])

    with op.batch_alter_table("t_case") as batch_op:
        for name, column_type in case_columns:
            if name in existing_columns:
                continue
            if name in {"no_power", "no_prio_text", "require_hk"}:
                batch_op.add_column(
                    sa.Column(name, column_type, nullable=True, server_default=sa.text("0"))
                )
                continue
            batch_op.add_column(sa.Column(name, column_type, nullable=True))

        if doc_address_fk not in existing_fks:
            batch_op.create_foreign_key(
                "fk_case_doc_address_id_client_address",
                "t_client_address",
                ["doc_address_id"],
                ["id"],
            )
        if bill_address_fk not in existing_fks:
            batch_op.create_foreign_key(
                "fk_case_bill_address_id_client_address",
                "t_client_address",
                ["bill_address_id"],
                ["id"],
            )


def downgrade() -> None:
    pass
