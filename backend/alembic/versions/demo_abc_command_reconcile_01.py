"""bind demo commands to exact projections and enforce money checks

Revision ID: demo_abc_command_reconcile_01
Revises: demo_abc_payment_offset_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "demo_abc_command_reconcile_01"
down_revision = "demo_abc_payment_offset_01"
branch_labels = None
depends_on = None


def _assert_no_invalid_rows(bind, table: str, predicate: str) -> None:
    if bind.execute(sa.text(f"SELECT 1 FROM {table} WHERE {predicate} LIMIT 1")).first():
        raise RuntimeError(f"invalid {table} money projection blocks demo reconciliation migration")


def upgrade() -> None:
    bind = op.get_bind()
    for table, predicate in (
        ("t_bill", "amount < 0 OR balance < 0 OR balance > amount"),
        ("t_bill_item", "amount < 0"),
        (
            "t_case_receipt",
            "receivable_amt < 0 OR received_amt < 0 OR received_amt > receivable_amt",
        ),
        ("t_offset", "offset_amt <= 0"),
        ("t_payment", "amount <= 0"),
        (
            "t_payment_line",
            "raw_amount <= 0 OR allocated_amt < 0 OR balance_amt < 0 "
            "OR raw_amount != allocated_amt + balance_amt",
        ),
    ):
        _assert_no_invalid_rows(bind, table, predicate)
    if bind.execute(sa.text("SELECT 1 FROM t_demo_payment_command LIMIT 1")).first():
        raise RuntimeError("existing demo payment commands require explicit target ownership migration")
    if bind.execute(sa.text("SELECT 1 FROM t_demo_offset_command LIMIT 1")).first():
        raise RuntimeError("existing demo offset commands require explicit receipt ownership migration")

    with op.batch_alter_table("t_demo_payment_command", recreate="always") as batch:
        batch.add_column(sa.Column("target_bill_id", sa.String(36), nullable=False))
        batch.create_foreign_key(
            "fk_demo_payment_command_target_bill",
            "t_bill",
            ["target_bill_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch.create_unique_constraint(
            "uq_demo_payment_command_target_bill", ["target_bill_id"]
        )
    with op.batch_alter_table("t_demo_offset_command", recreate="always") as batch:
        batch.add_column(sa.Column("receipt_id", sa.String(36), nullable=False))
        batch.create_foreign_key(
            "fk_demo_offset_command_receipt",
            "t_case_receipt",
            ["receipt_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch.create_unique_constraint("uq_demo_offset_command_receipt", ["receipt_id"])

    checks = {
        "t_bill": (
            ("ck_bill_amount_nonnegative", "amount >= 0"),
            ("ck_bill_balance_nonnegative", "balance >= 0"),
            ("ck_bill_balance_not_above_amount", "balance <= amount"),
        ),
        "t_bill_item": (("ck_bill_item_amount_nonnegative", "amount >= 0"),),
        "t_case_receipt": (
            ("ck_case_receipt_receivable_nonnegative", "receivable_amt >= 0"),
            ("ck_case_receipt_received_nonnegative", "received_amt >= 0"),
            (
                "ck_case_receipt_received_not_above_receivable",
                "received_amt <= receivable_amt",
            ),
        ),
        "t_offset": (("ck_offset_amount_positive", "offset_amt > 0"),),
        "t_payment": (("ck_payment_amount_positive", "amount > 0"),),
        "t_payment_line": (
            ("ck_payment_line_raw_positive", "raw_amount > 0"),
            ("ck_payment_line_allocated_nonnegative", "allocated_amt >= 0"),
            ("ck_payment_line_balance_nonnegative", "balance_amt >= 0"),
            (
                "ck_payment_line_projection_exact",
                "raw_amount = allocated_amt + balance_amt",
            ),
        ),
    }
    for table, table_checks in checks.items():
        with op.batch_alter_table(table, recreate="always") as batch:
            for name, condition in table_checks:
                batch.create_check_constraint(name, condition)


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
