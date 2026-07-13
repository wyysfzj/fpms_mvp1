"""add grant task lineage carriers

Revision ID: addgap_grant_lineage_01
Revises: addgap_workpkg_resolve_key_01
Create Date: 2026-07-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "addgap_grant_lineage_01"
down_revision = "addgap_workpkg_resolve_key_01"
branch_labels = None
depends_on = None

TABLE = "t_grant_fee_task"
SOURCE_INDEX = "ux_t_grant_fee_task_source_document_id"
REQUEST_INDEX = "ux_t_grant_fee_task_supersede_request_key"
SUPERSEDED_BY_INDEX = "ix_t_grant_fee_task_superseded_by_task_id"
LINEAGE_COLUMN_TYPES = {
    "source_document_id": "VARCHAR(36)",
    "deadline_source": "VARCHAR(32)",
    "deadline_confirmed_at": "DATETIME",
    "superseded_by_task_id": "VARCHAR(36)",
    "supersede_reason": "TEXT",
    "superseded_at": "DATETIME",
    "superseded_by": "VARCHAR(36)",
    "supersede_request_key": "VARCHAR(64)",
}
LINEAGE_FOREIGN_KEYS = {
    "source_document_id": ("t_document", "id"),
    "superseded_by_task_id": (TABLE, "id"),
}


def _column_exists(column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(item["name"] == column for item in inspector.get_columns(TABLE))


def _index_exists(index: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(item["name"] == index for item in inspector.get_indexes(TABLE))


def _preflight_existing_carriers() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {item["name"]: item for item in inspector.get_columns(TABLE)}
    present = set(columns).intersection(LINEAGE_COLUMN_TYPES)
    if not present:
        return
    if present != set(LINEAGE_COLUMN_TYPES):
        missing = sorted(set(LINEAGE_COLUMN_TYPES) - present)
        raise RuntimeError(
            f"Incompatible partial grant lineage schema; missing columns: {', '.join(missing)}"
        )

    issues: list[str] = []
    for column_name, expected_type in LINEAGE_COLUMN_TYPES.items():
        column = columns[column_name]
        if str(column["type"]).upper() != expected_type:
            issues.append(f"{column_name} type is {column['type']}, expected {expected_type}")
        if column["nullable"] is not True:
            issues.append(f"{column_name} must be nullable")

    foreign_keys = {
        tuple(item["constrained_columns"]): (
            item["referred_table"],
            tuple(item["referred_columns"]),
        )
        for item in inspector.get_foreign_keys(TABLE)
    }
    for column_name, (referred_table, referred_column) in LINEAGE_FOREIGN_KEYS.items():
        if foreign_keys.get((column_name,)) != (referred_table, (referred_column,)):
            issues.append(
                f"{column_name} missing foreign key to {referred_table}.{referred_column}"
            )

    if issues:
        raise RuntimeError(f"Incompatible grant lineage schema: {'; '.join(issues)}")


def _preflight_unique_column(column: str) -> None:
    if not _column_exists(column):
        return
    rows = op.get_bind().execute(
        sa.text(
            f"SELECT {column}, GROUP_CONCAT(id) AS task_ids, COUNT(*) AS duplicate_count "
            f"FROM {TABLE} WHERE {column} IS NOT NULL "
            f"GROUP BY {column} HAVING COUNT(*) > 1"
        )
    )
    duplicates = [f"{row[0]} ({row[1]})" for row in rows]
    if duplicates:
        raise RuntimeError(f"Duplicate grant lineage {column}: {'; '.join(duplicates)}")


def upgrade() -> None:
    _preflight_unique_column("source_document_id")
    _preflight_unique_column("supersede_request_key")
    _preflight_existing_carriers()

    columns = (
        sa.Column(
            "source_document_id",
            sa.String(36),
            sa.ForeignKey(
                "t_document.id",
                name="fk_t_grant_fee_task_source_document_id",
            ),
            nullable=True,
        ),
        sa.Column("deadline_source", sa.String(32), nullable=True),
        sa.Column("deadline_confirmed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "superseded_by_task_id",
            sa.String(36),
            sa.ForeignKey(
                "t_grant_fee_task.id",
                name="fk_t_grant_fee_task_superseded_by_task_id",
            ),
            nullable=True,
        ),
        sa.Column("supersede_reason", sa.Text(), nullable=True),
        sa.Column("superseded_at", sa.DateTime(), nullable=True),
        sa.Column("superseded_by", sa.String(36), nullable=True),
        sa.Column("supersede_request_key", sa.String(64), nullable=True),
    )
    missing_columns = [column for column in columns if not _column_exists(column.name)]
    if missing_columns:
        with op.batch_alter_table(TABLE) as batch_op:
            for column in missing_columns:
                batch_op.add_column(column)

    _preflight_unique_column("source_document_id")
    _preflight_unique_column("supersede_request_key")
    _preflight_existing_carriers()
    if not _index_exists(SOURCE_INDEX):
        op.create_index(SOURCE_INDEX, TABLE, ["source_document_id"], unique=True)
    if not _index_exists(REQUEST_INDEX):
        op.create_index(REQUEST_INDEX, TABLE, ["supersede_request_key"], unique=True)
    if not _index_exists(SUPERSEDED_BY_INDEX):
        op.create_index(SUPERSEDED_BY_INDEX, TABLE, ["superseded_by_task_id"])


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
