"""pd_p1_db_03_official_work_packages

Revision ID: pd_p1_db_03_official_work_packages_01
Revises: pd_p1_db_02_attachment_manifest_01
Create Date: 2026-05-31

Create official work-package carrier tables for P1 post-demo filing and OA
workflow readiness.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pd_p1_db_03_official_work_packages_01"
down_revision = "pd_p1_db_02_attachment_manifest_01"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return insp.has_table(table)


def _audit_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
    ]


def _create_index_if_missing(index_name: str, table: str, columns: list[str]) -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing = {idx["name"] for idx in insp.get_indexes(table) if idx.get("name")}
    if index_name not in existing:
        op.create_index(index_name, table, columns)


def upgrade() -> None:
    if not _table_exists("t_official_work_package"):
        op.create_table(
            "t_official_work_package",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "case_id",
                sa.String(36),
                sa.ForeignKey("t_case.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("package_kind", sa.String(32), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'PREPARING'")),
            sa.Column("source_document_id", sa.String(36), sa.ForeignKey("t_document.id"), nullable=True),
            sa.Column("reply_document_id", sa.String(36), sa.ForeignKey("t_document.id"), nullable=True),
            sa.Column("external_system", sa.String(64), nullable=True),
            sa.Column("remark", sa.Text(), nullable=True),
            *_audit_columns(),
        )

    if not _table_exists("t_official_work_package_checklist"):
        op.create_table(
            "t_official_work_package_checklist",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "package_id",
                sa.String(36),
                sa.ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("section_code", sa.String(64), nullable=False),
            sa.Column("item_code", sa.String(64), nullable=False),
            sa.Column("item_label", sa.String(256), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'PENDING'")),
            sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("sort_order", sa.Integer(), nullable=True),
            sa.Column("evidence_note", sa.Text(), nullable=True),
            *_audit_columns(),
        )

    if not _table_exists("t_official_work_package_manifest"):
        op.create_table(
            "t_official_work_package_manifest",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "package_id",
                sa.String(36),
                sa.ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("attachment_id", sa.String(36), sa.ForeignKey("t_doc_attachment.id"), nullable=True),
            sa.Column("official_file_role", sa.String(64), nullable=True),
            sa.Column("source_role_alias", sa.String(128), nullable=True),
            sa.Column("external_upload_position", sa.String(128), nullable=True),
            sa.Column("content_hash", sa.String(128), nullable=True),
            sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("present", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("sort_order", sa.Integer(), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            *_audit_columns(),
        )

    if not _table_exists("t_official_work_package_receipt"):
        op.create_table(
            "t_official_work_package_receipt",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "package_id",
                sa.String(36),
                sa.ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("receipt_kind", sa.String(32), nullable=False, server_default=sa.text("'RECEIPT_PDF'")),
            sa.Column("receipt_attachment_id", sa.String(36), sa.ForeignKey("t_doc_attachment.id"), nullable=True),
            sa.Column("receiving_case_no", sa.String(128), nullable=True),
            sa.Column("submitter", sa.String(128), nullable=True),
            sa.Column("received_at", sa.DateTime(), nullable=True),
            sa.Column("received_file_list", sa.Text(), nullable=True),
            sa.Column("archive_status", sa.String(32), nullable=False, server_default=sa.text("'PENDING'")),
            sa.Column("note", sa.Text(), nullable=True),
            *_audit_columns(),
        )

    if not _table_exists("t_official_work_package_override"):
        op.create_table(
            "t_official_work_package_override",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "package_id",
                sa.String(36),
                sa.ForeignKey("t_official_work_package.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("override_action", sa.String(64), nullable=False),
            sa.Column("override_reason", sa.Text(), nullable=False),
            sa.Column("override_by", sa.String(36), nullable=True),
            sa.Column(
                "override_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("follow_up_owner", sa.String(36), nullable=True),
            sa.Column("follow_up_due_date", sa.Date(), nullable=True),
            sa.Column("follow_up_note", sa.Text(), nullable=True),
            *_audit_columns(),
        )

    index_specs = [
        ("ix_t_official_work_package_case_id", "t_official_work_package", ["case_id"]),
        ("ix_t_official_work_package_package_kind", "t_official_work_package", ["package_kind"]),
        ("ix_t_official_work_package_status", "t_official_work_package", ["status"]),
        (
            "ix_t_official_work_package_source_document_id",
            "t_official_work_package",
            ["source_document_id"],
        ),
        (
            "ix_t_official_work_package_reply_document_id",
            "t_official_work_package",
            ["reply_document_id"],
        ),
        (
            "ix_t_official_work_package_checklist_package_id",
            "t_official_work_package_checklist",
            ["package_id"],
        ),
        (
            "ix_t_official_work_package_manifest_package_id",
            "t_official_work_package_manifest",
            ["package_id"],
        ),
        (
            "ix_t_official_work_package_manifest_attachment_id",
            "t_official_work_package_manifest",
            ["attachment_id"],
        ),
        (
            "ix_t_official_work_package_receipt_package_id",
            "t_official_work_package_receipt",
            ["package_id"],
        ),
        (
            "ix_t_official_work_package_receipt_attachment_id",
            "t_official_work_package_receipt",
            ["receipt_attachment_id"],
        ),
        (
            "ix_t_official_work_package_override_package_id",
            "t_official_work_package_override",
            ["package_id"],
        ),
    ]
    for index_name, table, columns in index_specs:
        if _table_exists(table):
            _create_index_if_missing(index_name, table, columns)


def downgrade() -> None:
    pass
