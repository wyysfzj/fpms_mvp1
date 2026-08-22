"""add case lifecycle projection carriers

Revision ID: v8_w1_l1_case_lifecycle_01
Revises: addgap_grant_lineage_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_l1_case_lifecycle_01"
down_revision = "addgap_grant_lineage_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("t_case") as batch_op:
        batch_op.add_column(sa.Column("business_stage", sa.String(32), nullable=True))
        batch_op.add_column(sa.Column("official_procedure_stage", sa.String(64), nullable=True))
        batch_op.add_column(sa.Column("legal_status", sa.String(32), nullable=True))
        batch_op.add_column(sa.Column("lifecycle_revision", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("lifecycle_verification_status", sa.String(32), nullable=True)
        )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
