"""add document evidence version carrier

Revision ID: v8_w1_d1_doc_evidence_version_01
Revises: v8_w1_l3_activity_evidence_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_d1_doc_evidence_version_01"
down_revision = "v8_w1_l3_activity_evidence_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_document_evidence_version",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("attachment_id", sa.String(36), nullable=False),
        sa.Column("lineage_key", sa.String(128), nullable=False),
        sa.Column("role", sa.String(64), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("creator_id", sa.String(36), nullable=False),
        sa.Column("review_state", sa.String(32), nullable=False),
        sa.Column("reviewer_id", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("final_submitted_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("content_hash", sa.String(128), nullable=False),
        sa.Column("current_identity_key", sa.String(256), nullable=True),
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
            ["attachment_id"],
            ["t_doc_attachment.id"],
            name="fk_t_document_evidence_version_attachment_id",
        ),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_document_evidence_version_case_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["t_document.id"],
            name="fk_t_document_evidence_version_document_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_document_evidence_version_current_identity_key",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
