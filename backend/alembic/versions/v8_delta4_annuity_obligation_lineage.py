"""add annuity task obligation lineage carrier

Revision ID: v8_d4_annuity_lineage_01
Revises: v8_w5_pay_list_export_artifact_01
"""

from alembic import op
import sqlalchemy as sa


revision = "v8_d4_annuity_lineage_01"
down_revision = "v8_w5_pay_list_export_artifact_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("t_annuity_task", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("source_activity_id", sa.String(36), nullable=True))
        batch_op.add_column(sa.Column("source_document_id", sa.String(36), nullable=True))
        batch_op.add_column(sa.Column("source_evidence_version_id", sa.String(36), nullable=True))
        batch_op.add_column(
            sa.Column("source_evidence_content_hash", sa.String(128), nullable=True)
        )
        batch_op.add_column(sa.Column("fee_obligation_id", sa.String(36), nullable=True))
        batch_op.add_column(sa.Column("grant_fee_year_key", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_t_annuity_task_source_activity_id",
            "t_case_activity_event",
            ["source_activity_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_foreign_key(
            "fk_t_annuity_task_source_document_id",
            "t_document",
            ["source_document_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_foreign_key(
            "fk_t_annuity_task_source_evidence_version_id",
            "t_document_evidence_version",
            ["source_evidence_version_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_foreign_key(
            "fk_t_annuity_task_fee_obligation_id",
            "t_fee_obligation",
            ["fee_obligation_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_unique_constraint(
            "uq_t_annuity_task_fee_obligation_id",
            ["fee_obligation_id"],
        )
        batch_op.create_check_constraint(
            "ck_t_annuity_task_lineage_tuple",
            "(source_activity_id IS NULL AND source_document_id IS NULL "
            "AND source_evidence_version_id IS NULL "
            "AND source_evidence_content_hash IS NULL "
            "AND fee_obligation_id IS NULL AND grant_fee_year_key IS NULL) "
            "OR (source_activity_id IS NOT NULL AND source_document_id IS NOT NULL "
            "AND source_evidence_version_id IS NOT NULL "
            "AND source_evidence_content_hash IS NOT NULL "
            "AND fee_obligation_id IS NOT NULL "
            "AND grant_fee_year_key IS NOT NULL AND grant_fee_year_key >= 1)",
        )
        batch_op.create_check_constraint(
            "ck_t_annuity_task_source_evidence_hash",
            "source_evidence_content_hash IS NULL OR "
            "(length(source_evidence_content_hash) = 71 "
            "AND substr(source_evidence_content_hash, 1, 7) = 'sha256:' "
            "AND substr(source_evidence_content_hash, 8) "
            "NOT GLOB '*[^0-9a-f]*')",
        )


def downgrade() -> None:
    with op.batch_alter_table("t_annuity_task", recreate="always") as batch_op:
        batch_op.drop_constraint(
            "ck_t_annuity_task_source_evidence_hash",
            type_="check",
        )
        batch_op.drop_constraint("ck_t_annuity_task_lineage_tuple", type_="check")
        batch_op.drop_constraint(
            "uq_t_annuity_task_fee_obligation_id",
            type_="unique",
        )
        batch_op.drop_constraint(
            "fk_t_annuity_task_fee_obligation_id",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_t_annuity_task_source_evidence_version_id",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_t_annuity_task_source_document_id",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_t_annuity_task_source_activity_id",
            type_="foreignkey",
        )
        batch_op.drop_column("grant_fee_year_key")
        batch_op.drop_column("fee_obligation_id")
        batch_op.drop_column("source_evidence_content_hash")
        batch_op.drop_column("source_evidence_version_id")
        batch_op.drop_column("source_document_id")
        batch_op.drop_column("source_activity_id")
