"""b2_document_reply_chain

Revision ID: b2_doc_reply_01
Revises: b1_doc_tpl_01
Create Date: 2026-02-26

Add reply chain columns to t_document: reply_to_id, need_reply, reply_date.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b2_doc_reply_01"
down_revision = "b1_doc_tpl_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_document"):
        return

    existing = {col["name"] for col in insp.get_columns("t_document")}

    new_columns = []
    add_fk = False
    if "reply_to_id" not in existing:
        new_columns.append(sa.Column("reply_to_id", sa.String(36), nullable=True))
        add_fk = True
    if "need_reply" not in existing:
        new_columns.append(
            sa.Column("need_reply", sa.Boolean, nullable=True, server_default=sa.text("0"))
        )
    if "reply_date" not in existing:
        new_columns.append(sa.Column("reply_date", sa.Date, nullable=True))

    if new_columns:
        with op.batch_alter_table("t_document") as batch_op:
            for column in new_columns:
                batch_op.add_column(column)
            if add_fk:
                batch_op.create_foreign_key(
                    "fk_document_reply_to_id",
                    "t_document",
                    ["reply_to_id"],
                    ["id"],
                )


def downgrade() -> None:
    pass
