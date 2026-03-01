"""mvp1 baseline schema (idempotent, create-if-missing).

Revision ID: enh_10_02_mvp1_baseline_schema
Revises: ea0de36a1dde
Create Date: 2026-01-31
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "enh_10_02_mvp1_baseline_schema"
down_revision = "ea0de36a1dde"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("t_user"):
        op.create_table(
            "t_user",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("username", sa.String(64), nullable=False, unique=True),
            sa.Column("display_name", sa.String(128)),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
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
        )

    if not insp.has_table("t_role"):
        op.create_table(
            "t_role",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("code", sa.String(64), nullable=False, unique=True),
            sa.Column("name", sa.String(128), nullable=False),
        )

    if not insp.has_table("t_user_role"):
        op.create_table(
            "t_user_role",
            sa.Column("user_id", sa.String(36), primary_key=True, nullable=False),
            sa.Column("role_id", sa.String(36), primary_key=True, nullable=False),
        )

    if not insp.has_table("t_role_perm"):
        op.create_table(
            "t_role_perm",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("role_id", sa.String(36), nullable=False),
            sa.Column("perm_code", sa.String(128), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("role_id", "perm_code", name="uq_role_perm"),
        )

    if not insp.has_table("t_client"):
        op.create_table(
            "t_client",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("client_code", sa.String(64), unique=True),
            sa.Column("name_cn", sa.String(256), nullable=False),
            sa.Column("name_en", sa.String(256)),
            sa.Column(
                "client_type", sa.String(32), nullable=False, server_default=sa.text("'CLIENT'")
            ),
            sa.Column(
                "default_currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")
            ),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
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
        )

    if not insp.has_table("t_client_address"):
        op.create_table(
            "t_client_address",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("client_id", sa.String(36), nullable=False),
            sa.Column("address_type", sa.String(32), nullable=False),
            sa.Column("line1", sa.String(255), nullable=False),
            sa.Column("line2", sa.String(255)),
            sa.Column("city", sa.String(100)),
            sa.Column("state", sa.String(100)),
            sa.Column("postal_code", sa.String(20)),
            sa.Column("country", sa.String(2)),
            sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("0")),
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
        )

    if not insp.has_table("t_client_contact"):
        op.create_table(
            "t_client_contact",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("client_id", sa.String(36), nullable=False),
            sa.Column("contact_name", sa.String(120), nullable=False),
            sa.Column("email", sa.String(254)),
            sa.Column("phone", sa.String(50)),
            sa.Column("title", sa.String(120)),
            sa.Column("department", sa.String(120)),
            sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("notes", sa.Text()),
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
        )

    if not insp.has_table("t_case"):
        op.create_table(
            "t_case",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_no", sa.String(64), nullable=False, unique=True),
            sa.Column(
                "case_type", sa.String(32), nullable=False, server_default=sa.text("'NORMAL'")
            ),
            sa.Column(
                "patent_category", sa.String(32), nullable=False, server_default=sa.text("'INV'")
            ),
            sa.Column(
                "flow_dir", sa.String(32), nullable=False, server_default=sa.text("'CN_DOMESTIC'")
            ),
            sa.Column("client_id", sa.String(36)),
            sa.Column("title_cn", sa.Text()),
            sa.Column("title_en", sa.Text()),
            sa.Column("app_no", sa.String(64)),
            sa.Column(
                "status", sa.String(32), nullable=False, server_default=sa.text("'NOT_FILED'")
            ),
            sa.Column("recv_date", sa.Date()),
            sa.Column("filing_date", sa.Date()),
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
        )

    if not insp.has_table("t_case_applicant"):
        op.create_table(
            "t_case_applicant",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_id", sa.String(36), nullable=False),
            sa.Column("seq", sa.Integer(), nullable=False),
            sa.Column("is_first", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("name_cn", sa.String(200)),
            sa.Column("name_en", sa.String(200)),
            sa.Column("address_cn", sa.Text()),
            sa.Column("address_en", sa.Text()),
            sa.UniqueConstraint("case_id", "seq", name="uq_case_applicant_seq"),
        )

    if not insp.has_table("t_case_inventor"):
        op.create_table(
            "t_case_inventor",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_id", sa.String(36), nullable=False),
            sa.Column("seq", sa.Integer(), nullable=False),
            sa.Column("name_cn", sa.String(200)),
            sa.Column("name_en", sa.String(200)),
            sa.UniqueConstraint("case_id", "seq", name="uq_case_inventor_seq"),
        )

    if not insp.has_table("t_priority"):
        op.create_table(
            "t_priority",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_id", sa.String(36), nullable=False),
            sa.Column("seq", sa.Integer(), nullable=False),
            sa.Column("country_code", sa.String(10)),
            sa.Column("prio_no", sa.String(64)),
            sa.Column("prio_date", sa.Date()),
            sa.UniqueConstraint("case_id", "seq", name="uq_priority_seq"),
        )

    if not insp.has_table("t_doc_template"):
        op.create_table(
            "t_doc_template",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("code", sa.String(64), nullable=False, unique=True),
            sa.Column("name", sa.String(256), nullable=False),
            sa.Column("direction", sa.String(8), nullable=False, server_default=sa.text("'IN'")),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        )

    if not insp.has_table("t_template"):
        op.create_table(
            "t_template",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("name", sa.String(256), nullable=False),
            sa.Column("group", sa.String(64)),
            sa.Column("language", sa.String(16)),
            sa.Column("file_path", sa.Text(), nullable=False),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not insp.has_table("t_document"):
        op.create_table(
            "t_document",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_id", sa.String(36), nullable=False),
            sa.Column("doc_template_id", sa.String(36)),
            sa.Column("direction", sa.String(8), nullable=False, server_default=sa.text("'IN'")),
            sa.Column("doc_date", sa.Date()),
            sa.Column("title", sa.Text()),
            sa.Column("ref_no", sa.String(128)),
            sa.Column("extra_data", sa.Text()),
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
        )

    if not insp.has_table("t_doc_attachment"):
        op.create_table(
            "t_doc_attachment",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("document_id", sa.String(36), nullable=False),
            sa.Column("file_name", sa.String(256), nullable=False),
            sa.Column("file_path", sa.Text(), nullable=False),
            sa.Column("mime_type", sa.String(128)),
            sa.Column("file_size", sa.Integer()),
            sa.Column(
                "uploaded_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not insp.has_table("t_task_template"):
        op.create_table(
            "t_task_template",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("code", sa.String(64), nullable=False, unique=True),
            sa.Column("name", sa.String(256), nullable=False),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        )

    if not insp.has_table("t_task"):
        op.create_table(
            "t_task",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_id", sa.String(36), nullable=False),
            sa.Column("document_id", sa.String(36)),
            sa.Column("task_template_id", sa.String(36)),
            sa.Column("title", sa.Text()),
            sa.Column("base_date", sa.Date()),
            sa.Column("due_date", sa.Date()),
            sa.Column("internal_due_date", sa.Date()),
            sa.Column("worker_id", sa.String(36)),
            sa.Column("supervisor_id", sa.String(36)),
            sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'OPEN'")),
            sa.Column("done_at", sa.DateTime()),
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
        )

    if not insp.has_table("t_task_log"):
        op.create_table(
            "t_task_log",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("task_id", sa.String(36), nullable=False),
            sa.Column("action", sa.String(32), nullable=False),
            sa.Column("from_status", sa.String(16)),
            sa.Column("to_status", sa.String(16)),
            sa.Column("remark", sa.Text()),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not insp.has_table("t_fee_rate"):
        op.create_table(
            "t_fee_rate",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("fee_code", sa.String(64), nullable=False),
            sa.Column("fee_name", sa.String(256)),
            sa.Column(
                "fee_type", sa.String(16), nullable=False, server_default=sa.text("'SERVICE'")
            ),
            sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
            sa.Column("default_amount", sa.Numeric(18, 2)),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        )

    if not insp.has_table("t_fee_draft"):
        op.create_table(
            "t_fee_draft",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_id", sa.String(36), nullable=False),
            sa.Column("client_id", sa.String(36)),
            sa.Column(
                "draft_type", sa.String(32), nullable=False, server_default=sa.text("'GENERIC'")
            ),
            sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
            sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'OPEN'")),
            sa.Column("total_gov", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column(
                "total_service", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")
            ),
            sa.Column("total_misc", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
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
        )

    if not insp.has_table("t_fee_item"):
        op.create_table(
            "t_fee_item",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("draft_id", sa.String(36), nullable=False),
            sa.Column("case_id", sa.String(36)),
            sa.Column("rate_id", sa.String(36)),
            sa.Column("fee_code", sa.String(64)),
            sa.Column("fee_name", sa.String(256)),
            sa.Column(
                "fee_type", sa.String(16), nullable=False, server_default=sa.text("'SERVICE'")
            ),
            sa.Column("year_no", sa.Integer()),
            sa.Column("quantity", sa.Numeric(18, 4)),
            sa.Column("unit_price", sa.Numeric(18, 2)),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("remark", sa.Text()),
        )

    if not insp.has_table("t_bill"):
        op.create_table(
            "t_bill",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("bill_no", sa.String(64), unique=True),
            sa.Column("client_id", sa.String(36), nullable=False),
            sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
            sa.Column("direction", sa.String(8), nullable=False, server_default=sa.text("'AR'")),
            sa.Column(
                "status", sa.String(24), nullable=False, server_default=sa.text("'UNSETTLED'")
            ),
            sa.Column("bill_date", sa.Date()),
            sa.Column("due_date", sa.Date()),
            sa.Column("total_gov", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column(
                "total_service", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")
            ),
            sa.Column("total_misc", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("balance", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
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
        )

    if not insp.has_table("t_bill_item"):
        op.create_table(
            "t_bill_item",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("bill_id", sa.String(36), nullable=False),
            sa.Column("case_id", sa.String(36)),
            sa.Column("draft_id", sa.String(36)),
            sa.Column("fee_item_id", sa.String(36)),
            sa.Column("fee_code", sa.String(64)),
            sa.Column("fee_name", sa.String(256)),
            sa.Column("fee_type", sa.String(16)),
            sa.Column("year_no", sa.Integer()),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        )

    if not insp.has_table("t_payment"):
        op.create_table(
            "t_payment",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("pay_no", sa.String(64)),
            sa.Column("client_id", sa.String(36), nullable=False),
            sa.Column("pay_date", sa.Date()),
            sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("remark", sa.Text()),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not insp.has_table("t_payment_line"):
        op.create_table(
            "t_payment_line",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("payment_id", sa.String(36), nullable=False),
            sa.Column("case_id", sa.String(36)),
            sa.Column("raw_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column(
                "allocated_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")
            ),
            sa.Column(
                "balance_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")
            ),
        )

    if not insp.has_table("t_offset"):
        op.create_table(
            "t_offset",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("payment_line_id", sa.String(36), nullable=False),
            sa.Column("bill_id", sa.String(36), nullable=False),
            sa.Column("offset_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("offset_date", sa.Date()),
            sa.Column("is_reversed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("reversed_at", sa.DateTime()),
        )

    if not insp.has_table("t_case_receipt"):
        op.create_table(
            "t_case_receipt",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("case_id", sa.String(36), nullable=False),
            sa.Column("fee_type", sa.String(16)),
            sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
            sa.Column(
                "receivable_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")
            ),
            sa.Column(
                "received_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")
            ),
            sa.Column("last_receipt_date", sa.Date()),
        )

    if not insp.has_table("t_system_param"):
        op.create_table(
            "t_system_param",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("param_key", sa.String(120), nullable=False),
            sa.Column("param_value", sa.Text(), nullable=False),
            sa.Column(
                "value_type", sa.String(20), nullable=False, server_default=sa.text("'string'")
            ),
            sa.Column("description", sa.Text()),
            sa.Column("is_secret", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("updated_by_user_id", sa.String(36)),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    if not insp.has_table("t_letter_head"):
        op.create_table(
            "t_letter_head",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("locale", sa.String(10)),
            sa.Column("logo_file_path", sa.String(512)),
            sa.Column("header_text", sa.Text()),
            sa.Column("footer_text", sa.Text()),
            sa.Column("address_block", sa.Text()),
            sa.Column("phone", sa.String(50)),
            sa.Column("email", sa.String(254)),
            sa.Column("website", sa.String(254)),
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("created_by_user_id", sa.String(36)),
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
        )


def downgrade() -> None:
    # No-op: upgrade is idempotent and may have skipped existing tables.
    pass
