"""add audit columns across MVP1 tables (idempotent).

Revision ID: e109a0b1c2d3
Revises: enh_10_04_add_foreign_keys
Create Date: 2026-01-31
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e109a0b1c2d3"
down_revision = "enh_10_04_add_foreign_keys"
branch_labels = None
depends_on = None


_TABLES = [
    "t_user",
    "t_role",
    "t_user_role",
    "t_role_perm",
    "t_client",
    "t_client_address",
    "t_client_contact",
    "t_case",
    "t_case_receipt",
    "t_document",
    "t_doc_attachment",
    "t_doc_template",
    "t_template",
    "t_letter_head",
    "t_task",
    "t_task_template",
    "t_task_log",
    "t_fee_rate",
    "t_fee_draft",
    "t_fee_item",
    "t_bill",
    "t_bill_item",
    "t_payment",
    "t_payment_line",
    "t_offset",
    "t_system_param",
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
    # No-op: dropping columns across many tables is unsafe on SQLite.
    pass
