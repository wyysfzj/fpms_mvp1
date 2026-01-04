"""documents + templates tables

Revision ID: 0002_documents
Revises: 0001_mvp1_core
Create Date: 2025-12-20T16:24:58
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0002_documents"
down_revision = "0001_mvp1_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_doc_template",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("direction", sa.String(8), nullable=False, server_default=sa.text("'IN'")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )

    op.create_table(
        "t_template",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("group", sa.String(64), nullable=True),
        sa.Column("language", sa.String(16), nullable=True),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )

    op.create_table(
        "t_document",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "case_id", sa.String(36), sa.ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "doc_template_id", sa.String(36), sa.ForeignKey("t_doc_template.id"), nullable=True
        ),
        sa.Column("direction", sa.String(8), nullable=False, server_default=sa.text("'IN'")),
        sa.Column("doc_date", sa.Date(), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("ref_no", sa.String(128), nullable=True),
        sa.Column("extra_data", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("idx_doc_case_date", "t_document", ["case_id", "doc_date"])

    op.create_table(
        "t_doc_attachment",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(36),
            sa.ForeignKey("t_document.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(256), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(128), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("Downgrade not implemented for MVP migrations (intentional).")
