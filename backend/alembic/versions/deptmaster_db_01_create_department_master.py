"""create department master

Revision ID: deptmaster_db_01
Revises: expstat_worker_db_01
Create Date: 2026-04-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "deptmaster_db_01"
down_revision = "expstat_worker_db_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_department",
        sa.Column("department_code", sa.String(length=64), nullable=False),
        sa.Column("name_cn", sa.String(length=128), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column(
            "id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("department_code"),
    )
    op.create_index(
        "ix_t_department_department_code",
        "t_department",
        ["department_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_t_department_department_code", table_name="t_department")
    op.drop_table("t_department")
