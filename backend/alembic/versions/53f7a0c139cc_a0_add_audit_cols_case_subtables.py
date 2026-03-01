"""a0_add_audit_cols_case_subtables

Revision ID: 53f7a0c139cc
Revises: 4e3a8e291947
Create Date: 2026-02-23

Add missing audit columns to t_case_applicant, t_case_inventor, t_priority.
These tables use AuditMixin in the model but were omitted from the earlier
e109a0b1c2d3 migration.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "53f7a0c139cc"
down_revision = "4e3a8e291947"
branch_labels = None
depends_on = None

_TABLES = [
    "t_case_applicant",
    "t_case_inventor",
    "t_priority",
]


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    audit_columns = {
        "created_at": sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        "updated_at": sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        "created_by": sa.Column("created_by", sa.String(36), nullable=True),
        "updated_by": sa.Column("updated_by", sa.String(36), nullable=True),
    }

    for table in _TABLES:
        if not insp.has_table(table):
            continue
        existing = {col["name"] for col in insp.get_columns(table)}
        missing = [column for name, column in audit_columns.items() if name not in existing]
        if not missing:
            continue
        with op.batch_alter_table(table) as batch_op:
            for column in missing:
                batch_op.add_column(column)


def downgrade() -> None:
    pass
