"""add mvp1 indexes and unique constraints (idempotent).

Revision ID: enh_10_03_add_indexes
Revises: enh_10_02_mvp1_baseline_schema
Create Date: 2026-01-31
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "enh_10_03_add_indexes"
down_revision = "enh_10_02_mvp1_baseline_schema"
branch_labels = None
depends_on = None


def _index_names(insp: sa.Inspector, table: str) -> set[str]:
    return {idx["name"] for idx in insp.get_indexes(table) if idx.get("name")}


def _unique_names(insp: sa.Inspector, table: str) -> set[str]:
    return {uc["name"] for uc in insp.get_unique_constraints(table) if uc.get("name")}


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    def ensure_index(table: str, name: str, columns: list[str], unique: bool = False) -> None:
        if not insp.has_table(table):
            return
        if name in _index_names(insp, table):
            return
        op.create_index(name, table, columns, unique=unique)

    def ensure_unique(table: str, name: str, columns: list[str]) -> None:
        if not insp.has_table(table):
            return
        if name in _unique_names(insp, table) or name in _index_names(insp, table):
            return
        op.create_index(name, table, columns, unique=True)

    # Unique constraints / unique indexes
    ensure_unique("t_user", "uq_t_user_username", ["username"])
    ensure_unique("t_role", "uq_t_role_code", ["code"])
    ensure_unique("t_user_role", "uq_t_user_role_user_id_role_id", ["user_id", "role_id"])
    ensure_unique("t_role_perm", "uq_role_perm", ["role_id", "perm_code"])
    ensure_unique("t_client", "uq_t_client_client_code", ["client_code"])
    ensure_unique("t_case", "uq_t_case_case_no", ["case_no"])
    ensure_unique("t_case_applicant", "uq_case_applicant_seq", ["case_id", "seq"])
    ensure_unique("t_case_inventor", "uq_case_inventor_seq", ["case_id", "seq"])
    ensure_unique("t_priority", "uq_priority_seq", ["case_id", "seq"])
    ensure_unique("t_doc_template", "uq_t_doc_template_code", ["code"])
    ensure_unique("t_task_template", "uq_t_task_template_code", ["code"])
    ensure_unique("t_bill", "uq_t_bill_bill_no", ["bill_no"])

    # Indexes from models/spec
    ensure_index("t_role_perm", "ix_t_role_perm_role_id", ["role_id"])
    ensure_index("t_role_perm", "ix_t_role_perm_perm_code", ["perm_code"])
    ensure_index("t_case", "idx_case_client", ["client_id"])
    ensure_index("t_case", "idx_case_appno", ["app_no"])
    ensure_index("t_document", "idx_doc_case_date", ["case_id", "doc_date"])
    ensure_index("t_case_applicant", "ix_t_case_applicant_case_id", ["case_id"])
    ensure_index("t_case_inventor", "ix_t_case_inventor_case_id", ["case_id"])
    ensure_index("t_priority", "ix_t_priority_case_id", ["case_id"])
    ensure_index("t_task", "idx_task_case_due_status", ["case_id", "due_date", "status"])
    ensure_index("t_task", "idx_task_worker_due", ["worker_id", "due_date"])
    ensure_index("t_fee_draft", "idx_fee_draft_case", ["case_id", "status"])
    ensure_index("t_bill", "idx_bill_client_status_date", ["client_id", "status", "bill_date"])
    ensure_index("t_payment", "idx_payment_client_date", ["client_id", "pay_date"])
    ensure_index("t_offset", "idx_offset_bill", ["bill_id"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    def drop_index(table: str, name: str) -> None:
        if not insp.has_table(table):
            return
        if name not in _index_names(insp, table):
            return
        op.drop_index(name, table_name=table)

    def drop_unique(table: str, name: str) -> None:
        if not insp.has_table(table):
            return
        if name not in _index_names(insp, table) and name not in _unique_names(insp, table):
            return
        op.drop_index(name, table_name=table)

    drop_index("t_offset", "idx_offset_bill")
    drop_index("t_payment", "idx_payment_client_date")
    drop_index("t_bill", "idx_bill_client_status_date")
    drop_index("t_fee_draft", "idx_fee_draft_case")
    drop_index("t_task", "idx_task_worker_due")
    drop_index("t_task", "idx_task_case_due_status")
    drop_index("t_priority", "ix_t_priority_case_id")
    drop_index("t_case_inventor", "ix_t_case_inventor_case_id")
    drop_index("t_case_applicant", "ix_t_case_applicant_case_id")
    drop_index("t_document", "idx_doc_case_date")
    drop_index("t_case", "idx_case_appno")
    drop_index("t_case", "idx_case_client")
    drop_index("t_role_perm", "ix_t_role_perm_perm_code")
    drop_index("t_role_perm", "ix_t_role_perm_role_id")

    drop_unique("t_bill", "uq_t_bill_bill_no")
    drop_unique("t_task_template", "uq_t_task_template_code")
    drop_unique("t_doc_template", "uq_t_doc_template_code")
    drop_unique("t_priority", "uq_priority_seq")
    drop_unique("t_case_inventor", "uq_case_inventor_seq")
    drop_unique("t_case_applicant", "uq_case_applicant_seq")
    drop_unique("t_case", "uq_t_case_case_no")
    drop_unique("t_client", "uq_t_client_client_code")
    drop_unique("t_role_perm", "uq_role_perm")
    drop_unique("t_user_role", "uq_t_user_role_user_id_role_id")
    drop_unique("t_role", "uq_t_role_code")
    drop_unique("t_user", "uq_t_user_username")
