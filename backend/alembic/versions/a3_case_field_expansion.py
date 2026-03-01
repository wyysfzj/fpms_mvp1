"""a3_case_field_expansion

Revision ID: a3_case_fields_01
Revises: a2_client_addr_01
Create Date: 2026-02-24

Add 15 new columns to t_case for NORMAL case type support.
Groups: publication/grant, spec details, agent assignment, control flags.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a3_case_fields_01"
down_revision = "a2_client_addr_01"
branch_labels = None
depends_on = None


def _col_exists(table: str, column: str) -> bool:
    """Check whether *column* already exists in *table* (SQLite-compatible)."""
    bind = op.get_bind()
    result = bind.execute(sa.text(f"PRAGMA table_info('{table}')"))
    return any(row[1] == column for row in result)


def upgrade() -> None:
    columns = [
        # Group 1 — Publication / Grant
        ("pub_date", sa.Date(), None),
        ("pub_no", sa.String(64), None),
        ("grant_date", sa.Date(), None),
        ("grant_no", sa.String(64), None),
        ("patent_no", sa.String(64), None),
        ("valid_until", sa.Date(), None),
        # Group 2 — Spec details
        ("spec_pages", sa.Integer(), None),
        ("claim_count", sa.Integer(), None),
        ("has_exam_request", sa.Boolean(), None),
        # Group 3 — Agent assignment (no FK)
        ("primary_agent_id", sa.String(36), None),
        ("second_agent_id", sa.String(36), None),
        ("draftor_id", sa.String(36), None),
        # Group 4 — Control flags
        ("is_fee_monitor", sa.Boolean(), None),
        ("fee_reduction", sa.String(32), None),
        ("applicant_kind", sa.String(32), None),
    ]

    with op.batch_alter_table("t_case") as batch_op:
        for col_name, col_type, server_default in columns:
            if not _col_exists("t_case", col_name):
                batch_op.add_column(
                    sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                )


def downgrade() -> None:
    pass
