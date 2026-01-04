"""0007-02 create t_letter_head

Revision ID: 0007_02_create_t_letter_head
Revises: 0007_01_create_t_system_param
Create Date: 2025-12-24 16:20:44.999348
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_02_create_t_letter_head"
down_revision = "0007_01_create_t_system_param"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_letter_head",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("locale", sa.String(10), nullable=True),
        sa.Column("logo_file_path", sa.String(512), nullable=True),
        sa.Column("header_text", sa.Text(), nullable=True),
        sa.Column("footer_text", sa.Text(), nullable=True),
        sa.Column("address_block", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("website", sa.String(254), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_by_user_id",
            sa.String(36),
            sa.ForeignKey("t_user.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("ix_t_letter_head_is_default", "t_letter_head", ["is_default"])
    op.create_index("ix_t_letter_head_locale", "t_letter_head", ["locale"])


def downgrade() -> None:
    op.drop_index("ix_t_letter_head_locale", table_name="t_letter_head")
    op.drop_index("ix_t_letter_head_is_default", table_name="t_letter_head")
    op.drop_table("t_letter_head")
