"""pd_p1_db_02_attachment_manifest

Revision ID: pd_p1_db_02_attachment_manifest_01
Revises: pd_p1_db_01_case_official_fields_01
Create Date: 2026-05-31

Add official attachment manifest carriers for P1 post-demo filing and OA
workflow readiness.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pd_p1_db_02_attachment_manifest_01"
down_revision = "pd_p1_db_01_case_official_fields_01"
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
    if not _table_exists("t_doc_attachment"):
        return

    columns = [
        ("official_file_role", sa.String(64), True, None),
        ("source_role_alias", sa.String(128), True, None),
        ("external_upload_position", sa.String(128), True, None),
        ("content_hash", sa.String(128), True, None),
        ("package_usage_hint", sa.String(64), True, None),
        ("is_archive_evidence", sa.Boolean(), False, sa.text("0")),
        ("is_receipt_evidence", sa.Boolean(), False, sa.text("0")),
    ]
    with op.batch_alter_table("t_doc_attachment") as batch_op:
        for column_name, column_type, nullable, server_default in columns:
            if not _column_exists("t_doc_attachment", column_name):
                batch_op.add_column(
                    sa.Column(
                        column_name,
                        column_type,
                        nullable=nullable,
                        server_default=server_default,
                    )
                )


def downgrade() -> None:
    pass
