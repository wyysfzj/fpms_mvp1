"""pd_p1_db_04_official_fee_carriers

Revision ID: pd_p1_db_04_official_fee_carriers_01
Revises: pd_p1_db_03_official_work_packages_01
Create Date: 2026-05-31

Add official fee readiness carriers for P1 post-demo filing and OA workflow
preparation without changing payment execution.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pd_p1_db_04_official_fee_carriers_01"
down_revision = "pd_p1_db_03_official_work_packages_01"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return insp.has_table(table)


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(f"PRAGMA table_info('{table}')"))
    return any(row[1] == column for row in result)


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
    if _table_exists("t_fee_draft"):
        fee_draft_columns = [
            ("official_fee_reduction_note", sa.Text()),
            ("official_template_status", sa.String(32)),
            ("official_template_version", sa.String(64)),
            ("official_template_note", sa.Text()),
        ]
        with op.batch_alter_table("t_fee_draft") as batch_op:
            for column_name, column_type in fee_draft_columns:
                if not _column_exists("t_fee_draft", column_name):
                    batch_op.add_column(sa.Column(column_name, column_type, nullable=True))

    if _table_exists("t_pay_list"):
        pay_list_columns = [
            ("official_upload_template_status", sa.String(32)),
            ("official_upload_template_name", sa.String(128)),
            ("official_upload_batch_limit", sa.Integer()),
            ("official_pay_list_boundary_note", sa.Text()),
        ]
        with op.batch_alter_table("t_pay_list") as batch_op:
            for column_name, column_type in pay_list_columns:
                if not _column_exists("t_pay_list", column_name):
                    batch_op.add_column(sa.Column(column_name, column_type, nullable=True))

    if not _table_exists("t_official_fee_checklist"):
        op.create_table(
            "t_official_fee_checklist",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "fee_draft_id",
                sa.String(36),
                sa.ForeignKey("t_fee_draft.id", ondelete="CASCADE"),
                nullable=True,
            ),
            sa.Column(
                "pay_list_id",
                sa.Integer(),
                sa.ForeignKey("t_pay_list.id", ondelete="CASCADE"),
                nullable=True,
            ),
            sa.Column("checklist_code", sa.String(64), nullable=False),
            sa.Column("checklist_label", sa.String(256), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'PENDING'")),
            sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("blocker_reason", sa.Text(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=True),
            *_audit_columns(),
        )

    if _table_exists("t_official_fee_checklist"):
        index_specs = [
            ("ix_t_official_fee_checklist_fee_draft_id", ["fee_draft_id"]),
            ("ix_t_official_fee_checklist_pay_list_id", ["pay_list_id"]),
            ("ix_t_official_fee_checklist_status", ["status"]),
        ]
        for index_name, columns in index_specs:
            _create_index_if_missing(index_name, "t_official_fee_checklist", columns)


def downgrade() -> None:
    pass
