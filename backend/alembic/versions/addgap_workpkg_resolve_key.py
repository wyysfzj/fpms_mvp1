"""add work-package resolve identity

Revision ID: addgap_workpkg_resolve_key_01
Revises: frfe04_block_struct_cols_01
Create Date: 2026-07-10
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "addgap_workpkg_resolve_key_01"
down_revision = "frfe04_block_struct_cols_01"
branch_labels = None
depends_on = None

TABLE = "t_official_work_package"
INDEX = "ux_t_official_work_package_resolve_key"


def _column_exists(column: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(item["name"] == column for item in inspector.get_columns(TABLE))


def _index_exists(index: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(item["name"] == index for item in inspector.get_indexes(TABLE))


def _preflight_resolve_identities() -> None:
    rows = (
        op.get_bind()
        .execute(
            sa.text(
                f"SELECT id, case_id, package_kind, source_document_id FROM {TABLE} "
                "WHERE package_kind IN ('FILING_PREP', 'OA_REPLY')"
            )
        )
        .mappings()
    )
    seen: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}
    missing: list[str] = []
    for row in rows:
        identity_field = "case_id" if row["package_kind"] == "FILING_PREP" else "source_document_id"
        identity = row[identity_field]
        if not identity or not str(identity).strip():
            missing.append(f"{row['id']} missing {identity_field}")
            continue
        resolve_key = f"{row['package_kind']}:{identity}"
        existing_id = seen.get(resolve_key)
        if existing_id is None:
            seen[resolve_key] = row["id"]
            continue
        duplicates.setdefault(resolve_key, [existing_id]).append(row["id"])

    if missing:
        raise RuntimeError(f"Work-package resolve identities are incomplete: {'; '.join(missing)}")
    if duplicates:
        details = "; ".join(
            f"{resolve_key} ({', '.join(package_ids)})"
            for resolve_key, package_ids in sorted(duplicates.items())
        )
        raise RuntimeError(f"Duplicate work-package resolve identities: {details}")


def _backfill_resolve_keys() -> None:
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            f"SELECT id, case_id, package_kind, source_document_id FROM {TABLE} "
            "WHERE package_kind IN ('FILING_PREP', 'OA_REPLY')"
        )
    ).mappings()
    for row in rows:
        identity = (
            row["case_id"] if row["package_kind"] == "FILING_PREP" else row["source_document_id"]
        )
        if identity is None:
            continue
        bind.execute(
            sa.text(f"UPDATE {TABLE} SET resolve_key = :resolve_key WHERE id = :id"),
            {"id": row["id"], "resolve_key": f"{row['package_kind']}:{identity}"},
        )


def upgrade() -> None:
    _preflight_resolve_identities()
    if not _column_exists("resolve_key"):
        op.add_column(TABLE, sa.Column("resolve_key", sa.String(128), nullable=True))
    _backfill_resolve_keys()
    if not _index_exists(INDEX):
        op.create_index(INDEX, TABLE, ["resolve_key"], unique=True)


def downgrade() -> None:
    pass
