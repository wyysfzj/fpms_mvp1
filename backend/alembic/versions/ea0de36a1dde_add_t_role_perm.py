"""add_t_role_perm

Revision ID: ea0de36a1dde
Revises: 0007_02_create_t_letter_head
Create Date: 2026-01-05 00:25:47.094460

"""

from alembic import op
import sqlalchemy as sa

revision = "ea0de36a1dde"
down_revision = "0007_02_create_t_letter_head"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_role_perm",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("role_id", sa.String(36), nullable=False),
        sa.Column("perm_code", sa.String(128), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["t_role.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("role_id", "perm_code", name="uq_role_perm"),
    )
    op.create_index("ix_t_role_perm_role_id", "t_role_perm", ["role_id"])
    op.create_index("ix_t_role_perm_perm_code", "t_role_perm", ["perm_code"])

    op.add_column(
        "t_role_perm",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_index("ix_t_role_perm_perm_code", table_name="t_role_perm")
    op.drop_index("ix_t_role_perm_role_id", table_name="t_role_perm")
    op.drop_table("t_role_perm")
