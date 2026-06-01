"""pd_p1_db_05_letter_handoff_carriers

Revision ID: pd_p1_db_05_letter_handoff_carriers_01
Revises: pd_p1_db_04_official_fee_carriers_01
Create Date: 2026-05-31

Add format-letter mapping and Longxia handoff carrier tables for P1 post-demo
letter workflow readiness.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pd_p1_db_05_letter_handoff_carriers_01"
down_revision = "pd_p1_db_04_official_fee_carriers_01"
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
    if not _table_exists("t_format_letter_mapping"):
        op.create_table(
            "t_format_letter_mapping",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "official_doc_template_id",
                sa.String(36),
                sa.ForeignKey("t_doc_template.id"),
                nullable=True,
            ),
            sa.Column("official_doc_template_code", sa.String(64), nullable=True),
            sa.Column("official_doc_name_pattern", sa.String(256), nullable=True),
            sa.Column(
                "format_letter_template_id",
                sa.String(36),
                sa.ForeignKey("t_template.id"),
                nullable=True,
            ),
            sa.Column("format_letter_template_code", sa.String(64), nullable=True),
            sa.Column("output_name_rule", sa.Text(), nullable=True),
            sa.Column("salutation_rule_code", sa.String(64), nullable=True),
            sa.Column("contact_rule_code", sa.String(64), nullable=True),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("remark", sa.Text(), nullable=True),
            *_audit_columns(),
        )

    if not _table_exists("t_letter_handoff"):
        op.create_table(
            "t_letter_handoff",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "source_document_id",
                sa.String(36),
                sa.ForeignKey("t_document.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "generated_document_id",
                sa.String(36),
                sa.ForeignKey("t_document.id"),
                nullable=True,
            ),
            sa.Column(
                "format_letter_mapping_id",
                sa.String(36),
                sa.ForeignKey("t_format_letter_mapping.id"),
                nullable=True,
            ),
            sa.Column(
                "format_letter_template_id",
                sa.String(36),
                sa.ForeignKey("t_template.id"),
                nullable=True,
            ),
            sa.Column(
                "client_contact_id",
                sa.String(36),
                sa.ForeignKey("t_client_contact.id"),
                nullable=True,
            ),
            sa.Column("contact_selection_source", sa.String(64), nullable=True),
            sa.Column("salutation_source", sa.String(64), nullable=True),
            sa.Column("salutation_text", sa.String(256), nullable=True),
            sa.Column("generated_word_path", sa.Text(), nullable=True),
            sa.Column("mail_subject", sa.Text(), nullable=True),
            sa.Column("mail_body_draft", sa.Text(), nullable=True),
            sa.Column(
                "longxia_handoff_status",
                sa.String(32),
                nullable=False,
                server_default=sa.text("'PENDING'"),
            ),
            sa.Column("longxia_handoff_payload", sa.Text(), nullable=True),
            sa.Column("handoff_at", sa.DateTime(), nullable=True),
            sa.Column("remark", sa.Text(), nullable=True),
            *_audit_columns(),
        )

    if not _table_exists("t_letter_handoff_attachment"):
        op.create_table(
            "t_letter_handoff_attachment",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "handoff_id",
                sa.String(36),
                sa.ForeignKey("t_letter_handoff.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "attachment_id",
                sa.String(36),
                sa.ForeignKey("t_doc_attachment.id"),
                nullable=True,
            ),
            sa.Column("file_name", sa.String(256), nullable=False),
            sa.Column("file_path", sa.Text(), nullable=True),
            sa.Column("attachment_role", sa.String(64), nullable=True),
            sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("included", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("sort_order", sa.Integer(), nullable=True),
            *_audit_columns(),
        )

    index_specs = [
        (
            "ix_t_format_letter_mapping_official_doc_template_id",
            "t_format_letter_mapping",
            ["official_doc_template_id"],
        ),
        (
            "ix_t_format_letter_mapping_official_doc_template_code",
            "t_format_letter_mapping",
            ["official_doc_template_code"],
        ),
        ("ix_t_letter_handoff_source_document_id", "t_letter_handoff", ["source_document_id"]),
        (
            "ix_t_letter_handoff_generated_document_id",
            "t_letter_handoff",
            ["generated_document_id"],
        ),
        (
            "ix_t_letter_handoff_longxia_handoff_status",
            "t_letter_handoff",
            ["longxia_handoff_status"],
        ),
        (
            "ix_t_letter_handoff_attachment_handoff_id",
            "t_letter_handoff_attachment",
            ["handoff_id"],
        ),
        (
            "ix_t_letter_handoff_attachment_attachment_id",
            "t_letter_handoff_attachment",
            ["attachment_id"],
        ),
    ]
    for index_name, table, columns in index_specs:
        if _table_exists(table):
            _create_index_if_missing(index_name, table, columns)


def downgrade() -> None:
    pass
