"""b1_doc_template_spec_fields

Revision ID: b1_doc_tpl_01
Revises: a3_case_fields_01
Create Date: 2026-02-25

Add SPEC configuration fields to t_doc_template for downstream automation.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b1_doc_tpl_01"
down_revision = "a3_case_fields_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_doc_template"):
        return

    existing = {col["name"] for col in insp.get_columns("t_doc_template")}

    new_columns = []
    if "status_effect" not in existing:
        new_columns.append(sa.Column("status_effect", sa.String(32), nullable=True))
    if "status_restore" not in existing:
        new_columns.append(sa.Column("status_restore", sa.String(32), nullable=True))
    if "deadline_template_code" not in existing:
        new_columns.append(sa.Column("deadline_template_code", sa.String(64), nullable=True))
    if "fee_draft_type" not in existing:
        new_columns.append(sa.Column("fee_draft_type", sa.String(32), nullable=True))
    if "fee_item_list" not in existing:
        new_columns.append(sa.Column("fee_item_list", sa.Text, nullable=True))
    if "need_reply" not in existing:
        new_columns.append(
            sa.Column("need_reply", sa.Boolean, nullable=True, server_default=sa.text("0"))
        )
    if "reply_to_template_code" not in existing:
        new_columns.append(sa.Column("reply_to_template_code", sa.String(64), nullable=True))
    if "input_fields" not in existing:
        new_columns.append(sa.Column("input_fields", sa.Text, nullable=True))

    if new_columns:
        with op.batch_alter_table("t_doc_template") as batch_op:
            for column in new_columns:
                batch_op.add_column(column)


def downgrade() -> None:
    pass
