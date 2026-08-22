"""add frozen PayList export-artifact carrier

Revision ID: v8_w5_pay_list_export_artifact_01
Revises: v8_w4_official_rate_book_01
"""

from alembic import op
import sqlalchemy as sa


revision = "v8_w5_pay_list_export_artifact_01"
down_revision = "v8_w4_official_rate_book_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_pay_list_export_artifact",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("pay_list_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("managed_storage_path", sa.Text(), nullable=False),
        sa.Column("template_version", sa.String(length=128), nullable=True),
        sa.Column("generated_by", sa.String(length=36), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column(
            "official_acceptance_evidence_ref",
            sa.String(length=512),
            nullable=True,
        ),
        sa.Column(
            "official_acceptance_evidence_hash",
            sa.String(length=64),
            nullable=True,
        ),
        sa.Column("official_accepted_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "kind IN ('INTERNAL_XLSX', 'OFFICIAL_XLSM')",
            name="ck_t_pay_list_export_artifact_kind",
        ),
        sa.CheckConstraint(
            "status IN ('GENERATED', 'OFFICIAL_SITE_ACCEPTED')",
            name="ck_t_pay_list_export_artifact_status",
        ),
        sa.CheckConstraint(
            "length(content_sha256) = 64",
            name="ck_t_pay_list_export_artifact_content_sha256",
        ),
        sa.CheckConstraint(
            "official_acceptance_evidence_hash IS NULL "
            "OR length(official_acceptance_evidence_hash) = 64",
            name="ck_t_pay_list_export_artifact_acceptance_hash",
        ),
        sa.CheckConstraint(
            "(kind = 'INTERNAL_XLSX' AND template_version IS NULL) "
            "OR (kind = 'OFFICIAL_XLSM' AND template_version IS NOT NULL)",
            name="ck_t_pay_list_export_artifact_kind_payload",
        ),
        sa.CheckConstraint(
            "(status = 'GENERATED' "
            "AND official_acceptance_evidence_ref IS NULL "
            "AND official_acceptance_evidence_hash IS NULL "
            "AND official_accepted_at IS NULL) "
            "OR (status = 'OFFICIAL_SITE_ACCEPTED' "
            "AND kind = 'OFFICIAL_XLSM' "
            "AND official_acceptance_evidence_ref IS NOT NULL "
            "AND official_acceptance_evidence_hash IS NOT NULL "
            "AND official_accepted_at IS NOT NULL)",
            name="ck_t_pay_list_export_artifact_acceptance_tuple",
        ),
        sa.ForeignKeyConstraint(
            ["pay_list_id"],
            ["t_pay_list.id"],
            name="fk_t_pay_list_export_artifact_pay_list_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["generated_by"],
            ["t_user.id"],
            name="fk_t_pay_list_export_artifact_generated_by",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "pay_list_id",
            "idempotency_key",
            name="uq_t_pay_list_export_artifact_pay_list_idempotency_key",
        ),
    )
    op.create_index(
        "ix_t_pay_list_export_artifact_pay_list_generated_at",
        "t_pay_list_export_artifact",
        ["pay_list_id", "generated_at"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
