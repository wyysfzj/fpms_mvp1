"""widen lifecycle evidence-kind capacity

Revision ID: v8_d4_evidence_kind_capacity_01
Revises: v8_d4_legacy_fee_provenance_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_d4_evidence_kind_capacity_01"
down_revision = "v8_d4_legacy_fee_provenance_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table(
        "t_case_activity_event_evidence",
        recreate="always",
    ) as batch_op:
        batch_op.alter_column(
            "evidence_kind",
            existing_type=sa.String(length=32),
            type_=sa.String(length=64),
            existing_nullable=False,
        )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
