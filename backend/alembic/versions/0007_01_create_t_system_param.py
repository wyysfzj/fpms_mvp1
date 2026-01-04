"""0007-01 create t_system_param

Revision ID: 0007_01_create_t_system_param
Revises: 0006_02_create_t_client_contact
Create Date: 2025-12-24 16:17:18.350536
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_01_create_t_system_param"
down_revision = "0006_02_create_t_client_contact"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_system_param",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("param_key", sa.String(120), nullable=False),
        sa.Column("param_value", sa.Text(), nullable=False),
        sa.Column("value_type", sa.String(20), nullable=False, server_default=sa.text("'string'")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_secret", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "updated_by_user_id",
            sa.String(36),
            sa.ForeignKey("t_user.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.UniqueConstraint("param_key", name="uq_t_system_param_param_key"),
    )
    op.create_index("ix_t_system_param_value_type", "t_system_param", ["value_type"])


def downgrade() -> None:
    op.drop_index("ix_t_system_param_value_type", table_name="t_system_param")
    op.drop_table("t_system_param")
