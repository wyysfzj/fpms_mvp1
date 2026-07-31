"""add Future Annuity reduction lineage carrier

Revision ID: v8_d27_annuity_reduction_01
Revises: v8_d4_evidence_kind_capacity_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "v8_d27_annuity_reduction_01"
down_revision = "v8_d4_evidence_kind_capacity_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_future_annuity_reduction_lineage",
        sa.Column("annuity_task_id", sa.Integer(), nullable=False),
        sa.Column("fee_obligation_line_id", sa.String(36), nullable=False),
        sa.Column("reduction_input_provenance", sa.String(32), nullable=False),
        sa.Column("reduction_approval_id", sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint(
            "annuity_task_id",
            name="pk_t_future_annuity_reduction_lineage",
        ),
        sa.ForeignKeyConstraint(
            ["annuity_task_id"],
            ["t_annuity_task.id"],
            name="fk_t_future_annuity_reduction_lineage_annuity_task_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["fee_obligation_line_id"],
            ["t_fee_obligation_line.id"],
            name="fk_t_future_annuity_reduction_lineage_fee_obligation_line_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reduction_approval_id"],
            ["t_fee_reduction_approval.id"],
            name="fk_t_future_annuity_reduction_lineage_reduction_approval_id",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "fee_obligation_line_id",
            name="uq_t_future_annuity_reduction_lineage_fee_obligation_line_id",
        ),
        sa.CheckConstraint(
            "reduction_input_provenance IN "
            "('EXPLICIT_ENTRY', 'CONFIRMED_MIGRATION')",
            name="ck_t_future_annuity_reduction_lineage_provenance",
        ),
        sa.CheckConstraint(
            "reduction_input_provenance != 'CONFIRMED_MIGRATION' "
            "OR reduction_approval_id IS NOT NULL",
            name="ck_t_future_annuity_reduction_lineage_approval_shape",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
