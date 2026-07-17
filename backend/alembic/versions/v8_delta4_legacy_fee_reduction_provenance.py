"""add legacy fee reduction provenance carrier

Revision ID: v8_d4_legacy_fee_provenance_01
Revises: v8_d4_annuity_lineage_01
"""

from alembic import op
import sqlalchemy as sa


revision = "v8_d4_legacy_fee_provenance_01"
down_revision = "v8_d4_annuity_lineage_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_legacy_fee_reduction_provenance",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("legacy_value", sa.String(), nullable=False),
        sa.Column("source_reference", sa.String(), nullable=False),
        sa.Column("source_version", sa.String(), nullable=False),
        sa.Column("source_snapshot_hash", sa.String(64), nullable=False),
        sa.Column("manifest_hash", sa.String(64), nullable=False),
        sa.Column("confirmed_by", sa.String(36), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("approval_id", sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["t_case.id"],
            name="fk_t_legacy_fee_reduction_provenance_case_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_legacy_fee_reduction_provenance_confirmed_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["approval_id"],
            ["t_fee_reduction_approval.id"],
            name="fk_t_legacy_fee_reduction_provenance_approval_id",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "case_id",
            "manifest_hash",
            name="uq_t_legacy_fee_reduction_provenance_case_manifest",
        ),
        sa.CheckConstraint(
            "legacy_value IN ('0', '0.7', '0.85')",
            name="ck_t_legacy_fee_reduction_provenance_legacy_value",
        ),
        sa.CheckConstraint(
            "(legacy_value = '0' AND approval_id IS NULL) OR "
            "(legacy_value IN ('0.7', '0.85') AND approval_id IS NOT NULL)",
            name="ck_t_legacy_fee_reduction_provenance_approval",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
