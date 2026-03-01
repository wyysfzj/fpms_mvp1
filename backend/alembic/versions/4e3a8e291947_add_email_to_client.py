"""add_email_to_client

Revision ID: 4e3a8e291947
Revises: e109a0b1c2d3
Create Date: 2026-02-12 00:19:44.380929

"""

from alembic import op
import sqlalchemy as sa

revision = "4e3a8e291947"
down_revision = "e109a0b1c2d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("t_client", sa.Column("email", sa.String(254), nullable=True))


def downgrade() -> None:
    op.drop_column("t_client", "email")
