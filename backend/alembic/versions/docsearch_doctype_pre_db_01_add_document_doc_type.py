"""Add independent doc_type carrier to t_document.

Revision ID: docsearch_doctype_pre_db_01
Revises: gfpre_db_01_create_t_grant_fee_task_01
Create Date: 2026-04-06 10:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "docsearch_doctype_pre_db_01"
down_revision = "gfpre_db_01_create_t_grant_fee_task_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("t_document", sa.Column("doc_type", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("t_document", "doc_type")
