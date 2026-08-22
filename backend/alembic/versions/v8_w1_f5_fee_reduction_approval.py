"""add fee reduction approval carrier

Revision ID: v8_w1_f5_fee_reduction_01
Revises: v8_w1_f4_payment_link_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_f5_fee_reduction_01"
down_revision = "v8_w1_f4_payment_link_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_fee_reduction_approval",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("scope_type", sa.String(32), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=True),
        sa.Column("applicant_set_key", sa.String(64), nullable=True),
        sa.Column("reduction_ratio", sa.Numeric(5, 4), nullable=False),
        sa.Column("fee_scope_snapshot", sa.Text(), nullable=False),
        sa.Column("fee_scope_hash", sa.String(64), nullable=False),
        sa.Column("fee_year_from", sa.Integer(), nullable=True),
        sa.Column("fee_year_to", sa.Integer(), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("source_evidence_version_id", sa.String(36), nullable=False),
        sa.Column("confirmation_status", sa.String(32), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("confirmed_by", sa.String(36), nullable=True),
        sa.Column("eligibility_snapshot", sa.Text(), nullable=False),
        sa.Column("eligibility_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("approval_identity_key", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_fee_reduction_approval_case_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_fee_reduction_approval_source_evidence_version_id",
        ),
        sa.CheckConstraint(
            "(scope_type = 'CASE' AND case_id IS NOT NULL AND applicant_set_key IS NULL) OR "
            "(scope_type = 'APPLICANT_SET' AND case_id IS NULL AND applicant_set_key IS NOT NULL)",
            name="ck_t_fee_reduction_approval_scope_exclusive",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "approval_identity_key",
            name="uq_t_fee_reduction_approval_identity_key",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
