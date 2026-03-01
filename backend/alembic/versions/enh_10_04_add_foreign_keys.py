"""add mvp1 foreign keys (sqlite-safe, idempotent).

Revision ID: enh_10_04_add_foreign_keys
Revises: enh_10_03_add_indexes
Create Date: 2026-01-31
"""

from __future__ import annotations

from collections import defaultdict
from typing import NamedTuple

import sqlalchemy as sa
from alembic import op

revision = "enh_10_04_add_foreign_keys"
down_revision = "enh_10_03_add_indexes"
branch_labels = None
depends_on = None


class _FKSpec(NamedTuple):
    table: str
    name: str
    columns: list[str]
    ref_table: str
    ref_columns: list[str]
    ondelete: str | None = None


_FKS: list[_FKSpec] = [
    _FKSpec("t_user_role", "fk_user_role_user_id_user", ["user_id"], "t_user", ["id"], "CASCADE"),
    _FKSpec("t_user_role", "fk_user_role_role_id_role", ["role_id"], "t_role", ["id"], "CASCADE"),
    _FKSpec("t_role_perm", "fk_role_perm_role_id_role", ["role_id"], "t_role", ["id"], "CASCADE"),
    _FKSpec("t_case", "fk_case_client_id_client", ["client_id"], "t_client", ["id"]),
    _FKSpec(
        "t_case_applicant",
        "fk_case_applicant_case_id_case",
        ["case_id"],
        "t_case",
        ["id"],
        "CASCADE",
    ),
    _FKSpec(
        "t_case_inventor",
        "fk_case_inventor_case_id_case",
        ["case_id"],
        "t_case",
        ["id"],
        "CASCADE",
    ),
    _FKSpec("t_priority", "fk_priority_case_id_case", ["case_id"], "t_case", ["id"], "CASCADE"),
    _FKSpec(
        "t_doc_attachment",
        "fk_doc_attachment_document_id_document",
        ["document_id"],
        "t_document",
        ["id"],
        "CASCADE",
    ),
    _FKSpec(
        "t_document",
        "fk_document_case_id_case",
        ["case_id"],
        "t_case",
        ["id"],
        "CASCADE",
    ),
    _FKSpec(
        "t_document",
        "fk_document_doc_template_id_doc_template",
        ["doc_template_id"],
        "t_doc_template",
        ["id"],
    ),
    _FKSpec("t_task", "fk_task_case_id_case", ["case_id"], "t_case", ["id"], "CASCADE"),
    _FKSpec(
        "t_task",
        "fk_task_document_id_document",
        ["document_id"],
        "t_document",
        ["id"],
    ),
    _FKSpec(
        "t_task",
        "fk_task_task_template_id_task_template",
        ["task_template_id"],
        "t_task_template",
        ["id"],
    ),
    _FKSpec("t_task", "fk_task_worker_id_user", ["worker_id"], "t_user", ["id"]),
    _FKSpec(
        "t_task",
        "fk_task_supervisor_id_user",
        ["supervisor_id"],
        "t_user",
        ["id"],
    ),
    _FKSpec("t_task_log", "fk_task_log_task_id_task", ["task_id"], "t_task", ["id"], "CASCADE"),
    _FKSpec("t_fee_draft", "fk_fee_draft_case_id_case", ["case_id"], "t_case", ["id"], "CASCADE"),
    _FKSpec("t_fee_draft", "fk_fee_draft_client_id_client", ["client_id"], "t_client", ["id"]),
    _FKSpec(
        "t_fee_item",
        "fk_fee_item_draft_id_fee_draft",
        ["draft_id"],
        "t_fee_draft",
        ["id"],
        "CASCADE",
    ),
    _FKSpec("t_fee_item", "fk_fee_item_case_id_case", ["case_id"], "t_case", ["id"]),
    _FKSpec("t_fee_item", "fk_fee_item_rate_id_fee_rate", ["rate_id"], "t_fee_rate", ["id"]),
    _FKSpec("t_bill", "fk_bill_client_id_client", ["client_id"], "t_client", ["id"]),
    _FKSpec(
        "t_bill_item",
        "fk_bill_item_bill_id_bill",
        ["bill_id"],
        "t_bill",
        ["id"],
        "CASCADE",
    ),
    _FKSpec("t_bill_item", "fk_bill_item_case_id_case", ["case_id"], "t_case", ["id"]),
    _FKSpec(
        "t_bill_item",
        "fk_bill_item_draft_id_fee_draft",
        ["draft_id"],
        "t_fee_draft",
        ["id"],
    ),
    _FKSpec(
        "t_bill_item",
        "fk_bill_item_fee_item_id_fee_item",
        ["fee_item_id"],
        "t_fee_item",
        ["id"],
    ),
    _FKSpec(
        "t_case_receipt",
        "fk_case_receipt_case_id_case",
        ["case_id"],
        "t_case",
        ["id"],
        "CASCADE",
    ),
    _FKSpec("t_payment", "fk_payment_client_id_client", ["client_id"], "t_client", ["id"]),
    _FKSpec(
        "t_payment_line",
        "fk_payment_line_payment_id_payment",
        ["payment_id"],
        "t_payment",
        ["id"],
        "CASCADE",
    ),
    _FKSpec(
        "t_payment_line",
        "fk_payment_line_case_id_case",
        ["case_id"],
        "t_case",
        ["id"],
    ),
    _FKSpec(
        "t_offset",
        "fk_offset_payment_line_id_payment_line",
        ["payment_line_id"],
        "t_payment_line",
        ["id"],
        "CASCADE",
    ),
    _FKSpec("t_offset", "fk_offset_bill_id_bill", ["bill_id"], "t_bill", ["id"], "CASCADE"),
    _FKSpec(
        "t_client_address",
        "fk_client_address_client_id_client",
        ["client_id"],
        "t_client",
        ["id"],
        "CASCADE",
    ),
    _FKSpec(
        "t_client_contact",
        "fk_client_contact_client_id_client",
        ["client_id"],
        "t_client",
        ["id"],
        "CASCADE",
    ),
    _FKSpec(
        "t_system_param",
        "fk_system_param_updated_by_user_id_user",
        ["updated_by_user_id"],
        "t_user",
        ["id"],
        "SET NULL",
    ),
    _FKSpec(
        "t_letter_head",
        "fk_letter_head_created_by_user_id_user",
        ["created_by_user_id"],
        "t_user",
        ["id"],
        "SET NULL",
    ),
]


def _fk_key(fk: dict) -> tuple[tuple[str, ...], str | None, tuple[str, ...]]:
    return (
        tuple(fk.get("constrained_columns") or []),
        fk.get("referred_table"),
        tuple(fk.get("referred_columns") or []),
    )


def _spec_key(spec: _FKSpec) -> tuple[tuple[str, ...], str, tuple[str, ...]]:
    return (tuple(spec.columns), spec.ref_table, tuple(spec.ref_columns))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    fks_by_table: dict[str, list[_FKSpec]] = defaultdict(list)
    for spec in _FKS:
        fks_by_table[spec.table].append(spec)

    for table, specs in fks_by_table.items():
        if not insp.has_table(table):
            continue
        existing = {_fk_key(fk) for fk in insp.get_foreign_keys(table)}
        missing = [spec for spec in specs if _spec_key(spec) not in existing]
        if not missing:
            continue
        with op.batch_alter_table(table) as batch_op:
            for spec in missing:
                batch_op.create_foreign_key(
                    spec.name,
                    spec.ref_table,
                    spec.columns,
                    spec.ref_columns,
                    ondelete=spec.ondelete,
                )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    fks_by_table: dict[str, list[_FKSpec]] = defaultdict(list)
    for spec in _FKS:
        fks_by_table[spec.table].append(spec)

    for table, specs in fks_by_table.items():
        if not insp.has_table(table):
            continue
        existing_names = {fk.get("name") for fk in insp.get_foreign_keys(table) if fk.get("name")}
        to_drop = [spec for spec in specs if spec.name in existing_names]
        if not to_drop:
            continue
        with op.batch_alter_table(table) as batch_op:
            for spec in to_drop:
                batch_op.drop_constraint(spec.name, type_="foreignkey")
