"""add document evidence derivation carrier

Revision ID: v8_w1_d2_evidence_derivation_01
Revises: v8_w1_d1_doc_evidence_version_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_d2_evidence_derivation_01"
down_revision = "v8_w1_d1_doc_evidence_version_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_document_evidence_derivation",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("parent_evidence_version_id", sa.String(36), nullable=False),
        sa.Column("child_evidence_version_id", sa.String(36), nullable=False),
        sa.Column("derivation_type", sa.String(64), nullable=False),
        sa.Column("actor_id", sa.String(36), nullable=False),
        sa.Column("derived_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("source_snapshot", sa.Text(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_document_evidence_derivation_case_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["child_evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_document_evidence_derivation_child_evidence_version_id",
        ),
        sa.ForeignKeyConstraint(
            ["parent_evidence_version_id"],
            ["t_document_evidence_version.id"],
            name="fk_t_document_evidence_derivation_parent_evidence_version_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
