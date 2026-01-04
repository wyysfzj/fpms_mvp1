"""0006-01 create t_client_address

Revision ID: 0006_01_create_t_client_address
Revises: 0005_billing
Create Date: 2025-12-24T08:06:30
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_01_create_t_client_address"
down_revision = "0005_billing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_client_address",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("address_type", sa.String(32), nullable=False),
        sa.Column("line1", sa.String(255), nullable=False),
        sa.Column("line2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("ix_t_client_address_client_id", "t_client_address", ["client_id"])


def downgrade() -> None:
    op.drop_index("ix_t_client_address_client_id", table_name="t_client_address")
    op.drop_table("t_client_address")
