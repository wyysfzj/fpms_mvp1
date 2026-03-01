"""a2_client_address_contact

Revision ID: a2_client_addr_01
Revises: a1_task_template_01
Create Date: 2026-02-24

Drop and recreate t_client_address and t_client_contact
with UUID PKs, AuditMixin, and spec-compliant field names.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a2_client_addr_01"
down_revision = "a1_task_template_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("t_client_contact")
    op.drop_table("t_client_address")

    op.create_table(
        "t_client_address",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "address_type", sa.String(16), nullable=False, server_default=sa.text("'GENERAL'")
        ),
        sa.Column("address_line1", sa.Text, nullable=True),
        sa.Column("address_line2", sa.Text, nullable=True),
        sa.Column("city", sa.String(128), nullable=True),
        sa.Column("province", sa.String(128), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("country_code", sa.String(10), nullable=True, server_default=sa.text("'CN'")),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
    )
    op.create_index("ix_t_client_address_client_id", "t_client_address", ["client_id"])

    op.create_table(
        "t_client_contact",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("contact_name", sa.String(200), nullable=False),
        sa.Column("title", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("mobile", sa.String(50), nullable=True),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
    )
    op.create_index("ix_t_client_contact_client_id", "t_client_contact", ["client_id"])


def downgrade() -> None:
    pass
