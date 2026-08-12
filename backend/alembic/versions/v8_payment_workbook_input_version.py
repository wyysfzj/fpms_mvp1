"""add official payment workbook input version carrier

Revision ID: v8_payment_workbook_input_01
Revises: v8_grant_official_copy_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_payment_workbook_input_01"
down_revision = "v8_grant_official_copy_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_official_payment_workbook_input_version",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("scope_key", sa.String(36), nullable=False),
        sa.Column("source_classification", sa.String(24), nullable=False),
        sa.Column("template_version", sa.String(128), nullable=False),
        sa.Column("template_storage_path", sa.Text(), nullable=False),
        sa.Column("template_content_hash", sa.String(64), nullable=False),
        sa.Column("upload_proof_storage_path", sa.Text(), nullable=False),
        sa.Column("upload_proof_content_hash", sa.String(64), nullable=False),
        sa.Column("structure_snapshot", sa.Text(), nullable=False),
        sa.Column("structure_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("workflow_status", sa.String(24), nullable=False),
        sa.Column("validated_by", sa.String(36), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("validation_reason", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("review_reason", sa.Text(), nullable=True),
        sa.Column("activation_status", sa.String(24), nullable=False),
        sa.Column("activated_by", sa.String(36), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("retired_by", sa.String(36), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("retirement_reason", sa.Text(), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=False), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=False), nullable=True),
        sa.Column("supersedes_version_id", sa.String(36), nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("current_identity_key", sa.String(128), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("updated_by", sa.String(36), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["validated_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_validated_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_reviewed_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["activated_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_activated_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["retired_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_retired_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_created_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["t_user.id"],
            name="fk_t_official_payment_workbook_input_updated_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_version_id"],
            ["t_official_payment_workbook_input_version.id"],
            name="fk_t_official_payment_workbook_input_supersedes",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "scope_key",
            "template_version",
            name="uq_t_official_payment_workbook_input_scope_version",
        ),
        sa.UniqueConstraint(
            "idempotency_key", name="uq_t_official_payment_workbook_input_idempotency_key"
        ),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_official_payment_workbook_input_current_identity_key",
        ),
        sa.CheckConstraint(
            "scope_key = 'GLOBAL'", name="ck_t_official_payment_workbook_input_scope"
        ),
        sa.CheckConstraint(
            "source_classification IN ('PRODUCTION', 'TEST_ONLY')",
            name="ck_t_official_payment_workbook_input_source_classification",
        ),
        sa.CheckConstraint(
            "workflow_status IN ('DRAFT', 'VALIDATED', 'APPROVED', 'REJECTED')",
            name="ck_t_official_payment_workbook_input_workflow_status",
        ),
        sa.CheckConstraint(
            "activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')",
            name="ck_t_official_payment_workbook_input_activation_status",
        ),
        sa.CheckConstraint(
            "length(template_content_hash) = 64 "
            "AND length(upload_proof_content_hash) = 64 "
            "AND length(structure_snapshot_hash) = 64",
            name="ck_t_official_payment_workbook_input_hashes",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_t_official_payment_workbook_input_effective_interval",
        ),
        sa.CheckConstraint(
            "(workflow_status = 'DRAFT' "
            "AND validated_by IS NULL AND validated_at IS NULL AND validation_reason IS NULL "
            "AND reviewed_by IS NULL AND reviewed_at IS NULL AND review_reason IS NULL) "
            "OR (workflow_status = 'VALIDATED' "
            "AND validated_by IS NOT NULL AND validated_at IS NOT NULL "
            "AND validation_reason IS NOT NULL "
            "AND reviewed_by IS NULL AND reviewed_at IS NULL AND review_reason IS NULL) "
            "OR (workflow_status IN ('APPROVED', 'REJECTED') "
            "AND validated_by IS NOT NULL AND validated_at IS NOT NULL "
            "AND validation_reason IS NOT NULL "
            "AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL "
            "AND review_reason IS NOT NULL AND reviewed_by <> created_by)",
            name="ck_t_official_payment_workbook_input_workflow_tuple",
        ),
        sa.CheckConstraint(
            "(activation_status = 'INACTIVE' "
            "AND activated_by IS NULL AND activated_at IS NULL "
            "AND retired_by IS NULL AND retired_at IS NULL AND retirement_reason IS NULL "
            "AND current_identity_key IS NULL) "
            "OR (activation_status = 'ACTIVE' "
            "AND source_classification = 'PRODUCTION' AND workflow_status = 'APPROVED' "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_by IS NULL AND retired_at IS NULL AND retirement_reason IS NULL "
            "AND current_identity_key IS NOT NULL AND current_identity_key = 'GLOBAL') "
            "OR (activation_status = 'RETIRED' "
            "AND source_classification = 'PRODUCTION' AND workflow_status = 'APPROVED' "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_by IS NOT NULL AND retired_at IS NOT NULL "
            "AND retirement_reason IS NOT NULL AND current_identity_key IS NULL)",
            name="ck_t_official_payment_workbook_input_activation_tuple",
        ),
    )
    op.create_index(
        "ix_t_official_payment_workbook_input_scope_status_effective",
        "t_official_payment_workbook_input_version",
        ["scope_key", "workflow_status", "activation_status", "effective_from", "effective_to"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
