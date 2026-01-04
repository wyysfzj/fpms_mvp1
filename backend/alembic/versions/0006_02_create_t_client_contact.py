"""0006-02 create t_client_contact

Revision ID: 0006_02_create_t_client_contact
Revises: 0006_01_create_t_client_address
Create Date: 2025-12-24 16:14:20.664973
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_02_create_t_client_contact"
down_revision = "0006_01_create_t_client_address"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_client_contact",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("contact_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("title", sa.String(120), nullable=True),
        sa.Column("department", sa.String(120), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("ix_t_client_contact_client_id", "t_client_contact", ["client_id"])
    op.create_index("ix_t_client_contact_email", "t_client_contact", ["email"])


def downgrade() -> None:
    op.drop_index("ix_t_client_contact_email", table_name="t_client_contact")
    op.drop_index("ix_t_client_contact_client_id", table_name="t_client_contact")
    op.drop_table("t_client_contact")
