"""add fee obligation carrier

Revision ID: v8_w1_f1_fee_obligation_01
Revises: v8_w1_d3_workpkg_evidence_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_f1_fee_obligation_01"
down_revision = "v8_w1_d3_workpkg_evidence_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_fee_obligation",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("source_activity_id", sa.String(36), nullable=False),
        sa.Column("source_document_id", sa.String(36), nullable=True),
        sa.Column("fee_domain", sa.String(16), nullable=False),
        sa.Column("obligation_type", sa.String(64), nullable=False),
        sa.Column("obligation_status", sa.String(32), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("source_status", sa.String(32), nullable=False),
        sa.Column("client_instruction_status", sa.String(32), nullable=False),
        sa.Column("draft_status", sa.String(32), nullable=False),
        sa.Column("payment_status", sa.String(32), nullable=False),
        sa.Column("official_evidence_status", sa.String(32), nullable=False),
        sa.Column("supersedes_obligation_id", sa.String(36), nullable=True),
        sa.Column("supersede_reason", sa.Text(), nullable=True),
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
            name="fk_t_fee_obligation_case_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["source_document_id"],
            ["t_document.id"],
            name="fk_t_fee_obligation_source_document_id",
        ),
        sa.ForeignKeyConstraint(
            ["case_id", "source_activity_id"],
            ["t_case_activity_event.case_id", "t_case_activity_event.id"],
            name="fk_t_fee_obligation_source_activity_same_case",
        ),
        sa.ForeignKeyConstraint(
            ["case_id", "supersedes_obligation_id"],
            ["t_fee_obligation.case_id", "t_fee_obligation.id"],
            name="fk_t_fee_obligation_supersedes_same_case",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "case_id",
            "id",
            name="uq_t_fee_obligation_case_id",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
