"""add service price book carrier

Revision ID: v8_w6_service_price_book_01
Revises: v8_payment_workbook_input_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w6_service_price_book_01"
down_revision = "v8_payment_workbook_input_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_service_price_book",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("source_classification", sa.String(24), nullable=False),
        sa.Column("book_version", sa.String(128), nullable=False),
        sa.Column("scope_key", sa.String(128), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("tax_policy", sa.Text(), nullable=False),
        sa.Column("discount_policy", sa.Text(), nullable=False),
        sa.Column("source_reference", sa.Text(), nullable=False),
        sa.Column("source_content_hash", sa.String(64), nullable=False),
        sa.Column("item_snapshot", sa.Text(), nullable=False),
        sa.Column("item_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("approved_by", sa.String(36), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("approval_reason", sa.Text(), nullable=True),
        sa.Column("activated_by", sa.String(36), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("retired_by", sa.String(36), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("retirement_reason", sa.Text(), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=False), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=False), nullable=True),
        sa.Column("supersedes_price_book_id", sa.String(36), nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("current_identity_key", sa.String(128), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("updated_by", sa.String(36), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["t_user.id"],
            name="fk_t_service_price_book_approved_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["activated_by"],
            ["t_user.id"],
            name="fk_t_service_price_book_activated_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["retired_by"],
            ["t_user.id"],
            name="fk_t_service_price_book_retired_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["t_user.id"],
            name="fk_t_service_price_book_created_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["t_user.id"],
            name="fk_t_service_price_book_updated_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_price_book_id"],
            ["t_service_price_book.id"],
            name="fk_t_service_price_book_supersedes",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "scope_key", "book_version", name="uq_t_service_price_book_scope_version"
        ),
        sa.UniqueConstraint("idempotency_key", name="uq_t_service_price_book_idempotency_key"),
        sa.UniqueConstraint(
            "current_identity_key", name="uq_t_service_price_book_current_identity_key"
        ),
        sa.CheckConstraint("scope_key = 'GLOBAL'", name="ck_t_service_price_book_scope"),
        sa.CheckConstraint(
            "source_classification IN ('PRODUCTION', 'TEST_ONLY')",
            name="ck_t_service_price_book_source_classification",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'ACTIVE', 'RETIRED')", name="ck_t_service_price_book_status"
        ),
        sa.CheckConstraint(
            "length(source_content_hash) = 64 AND length(item_snapshot_hash) = 64",
            name="ck_t_service_price_book_hashes",
        ),
        sa.CheckConstraint("item_count >= 0", name="ck_t_service_price_book_item_count"),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_service_price_book_effective_interval",
        ),
        sa.CheckConstraint(
            "(approved_by IS NULL AND approved_at IS NULL AND approval_reason IS NULL) OR "
            "(approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND approval_reason IS NOT NULL AND approved_by <> created_by)",
            name="ck_t_service_price_book_approval_tuple",
        ),
        sa.CheckConstraint(
            "(status = 'DRAFT' AND activated_by IS NULL AND activated_at IS NULL "
            "AND retired_by IS NULL AND retired_at IS NULL AND retirement_reason IS NULL "
            "AND current_identity_key IS NULL) OR "
            "(status = 'ACTIVE' AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND approval_reason IS NOT NULL AND item_count > 0 "
            "AND length(trim(item_snapshot)) > 2 "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_by IS NULL AND retired_at IS NULL AND retirement_reason IS NULL "
            "AND current_identity_key IS NOT NULL AND current_identity_key = 'GLOBAL') OR "
            "(status = 'RETIRED' AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND approval_reason IS NOT NULL AND item_count > 0 "
            "AND length(trim(item_snapshot)) > 2 "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_by IS NOT NULL AND retired_at IS NOT NULL "
            "AND retirement_reason IS NOT NULL AND current_identity_key IS NULL)",
            name="ck_t_service_price_book_status_tuple",
        ),
    )
    op.create_index(
        "ix_t_service_price_book_scope_status_effective",
        "t_service_price_book",
        ["scope_key", "status", "effective_from", "effective_to"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
