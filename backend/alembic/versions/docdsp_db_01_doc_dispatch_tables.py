"""docdsp_db_01_doc_dispatch_tables

Revision ID: docdsp_db_01_doc_dispatch_tables_01
Revises: casebf_db_01_case_submitted_date_01
Create Date: 2026-03-30

Add dispatch mail fields and dispatch header/line tables in a SQLite-safe way.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "docdsp_db_01_doc_dispatch_tables_01"
down_revision = "casebf_db_01_case_submitted_date_01"
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


def upgrade() -> None:
    if _table_exists("t_document"):
        with op.batch_alter_table("t_document") as batch_op:
            if not _col_exists("t_document", "outgoing_reg_no"):
                batch_op.add_column(sa.Column("outgoing_reg_no", sa.String(128), nullable=True))
            if not _col_exists("t_document", "forward_date"):
                batch_op.add_column(sa.Column("forward_date", sa.Date(), nullable=True))

    if not _table_exists("t_doc_dispatch"):
        op.create_table(
            "t_doc_dispatch",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "client_id",
                sa.String(36),
                sa.ForeignKey("t_client.id"),
                nullable=False,
            ),
            sa.Column("dispatch_date", sa.Date(), nullable=False),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("created_by", sa.String(36), nullable=True),
            sa.Column("updated_by", sa.String(36), nullable=True),
        )

    if not _table_exists("t_doc_dispatch_line"):
        op.create_table(
            "t_doc_dispatch_line",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "dispatch_id",
                sa.String(36),
                sa.ForeignKey("t_doc_dispatch.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "document_id",
                sa.String(36),
                sa.ForeignKey("t_document.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "case_id",
                sa.String(36),
                sa.ForeignKey("t_case.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("doc_name", sa.String(256), nullable=False),
            sa.Column("outgoing_reg_no", sa.String(128), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("created_by", sa.String(36), nullable=True),
            sa.Column("updated_by", sa.String(36), nullable=True),
        )


def downgrade() -> None:
    pass
