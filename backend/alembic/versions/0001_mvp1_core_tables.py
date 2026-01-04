"""mvp1 core tables (RBAC + Client + Case)

Revision ID: 0001_mvp1_core
Revises:
Create Date: 2025-12-20T16:22:05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_mvp1_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_user",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("display_name", sa.String(128)),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_table(
        "t_role",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
    )
    op.create_table(
        "t_user_role",
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("t_user.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            sa.String(36),
            sa.ForeignKey("t_role.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "t_client",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("client_code", sa.String(64), unique=True),
        sa.Column("name_cn", sa.String(256), nullable=False),
        sa.Column("name_en", sa.String(256)),
        sa.Column("client_type", sa.String(32), nullable=False, server_default=sa.text("'CLIENT'")),
        sa.Column(
            "default_currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )

    op.create_table(
        "t_case",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_no", sa.String(64), nullable=False, unique=True),
        sa.Column("case_type", sa.String(32), nullable=False, server_default=sa.text("'NORMAL'")),
        sa.Column(
            "patent_category", sa.String(32), nullable=False, server_default=sa.text("'INV'")
        ),
        sa.Column(
            "flow_dir", sa.String(32), nullable=False, server_default=sa.text("'CN_DOMESTIC'")
        ),
        sa.Column("client_id", sa.String(36), sa.ForeignKey("t_client.id")),
        sa.Column("title_cn", sa.Text()),
        sa.Column("title_en", sa.Text()),
        sa.Column("app_no", sa.String(64)),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'NOT_FILED'")),
        sa.Column("recv_date", sa.Date()),
        sa.Column("filing_date", sa.Date()),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("idx_case_client", "t_case", ["client_id"])
    op.create_index("idx_case_appno", "t_case", ["app_no"])


def downgrade() -> None:
    op.drop_index("idx_case_appno", table_name="t_case")
    op.drop_index("idx_case_client", table_name="t_case")
    op.drop_table("t_case")
    op.drop_table("t_client")
    op.drop_table("t_user_role")
    op.drop_table("t_role")
    op.drop_table("t_user")
