"""add local-demo bill source ownership

Revision ID: demo_abc_bill_source_01
Revises: v8_w6_service_price_book_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "demo_abc_bill_source_01"
down_revision = "v8_w6_service_price_book_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    duplicate = bind.execute(
        sa.text(
            "SELECT fee_item_id FROM t_bill_item "
            "WHERE fee_item_id IS NOT NULL GROUP BY fee_item_id HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate is not None:
        raise RuntimeError("duplicate billed fee_item_id blocks demo bill-source migration")

    op.create_table(
        "t_bill_draft_source",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("bill_id", sa.String(36), nullable=False),
        sa.Column("draft_id", sa.String(36), nullable=False),
        sa.Column("idempotency_key", sa.String(96), nullable=False),
        sa.Column("command_hash", sa.String(64), nullable=False),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["bill_id"], ["t_bill.id"], name="fk_bill_draft_source_bill", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["draft_id"],
            ["t_fee_draft.id"],
            name="fk_bill_draft_source_draft",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("bill_id", name="uq_bill_draft_source_bill"),
        sa.UniqueConstraint("draft_id", name="uq_bill_draft_source_draft"),
        sa.UniqueConstraint("idempotency_key", name="uq_bill_draft_source_idempotency"),
        sa.CheckConstraint("length(command_hash) = 64", name="ck_bill_draft_source_hash"),
    )
    op.create_index(
        "ux_bill_item_fee_item_id_nonnull",
        "t_bill_item",
        ["fee_item_id"],
        unique=True,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
