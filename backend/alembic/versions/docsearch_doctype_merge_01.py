"""docsearch_doctype_merge_01

Revision ID: docsearch_doctype_merge_01
Revises: caserpt_trend_carrier_db_merge_01, docsearch_doctype_pre_db_01
Create Date: 2026-04-06

Merge the document search DocType prerequisite back into the current Alembic head.
"""

from __future__ import annotations

revision = "docsearch_doctype_merge_01"
down_revision = (
    "caserpt_trend_carrier_db_merge_01",
    "docsearch_doctype_pre_db_01",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
