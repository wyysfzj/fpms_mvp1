"""frfe04_paylist_govpayment_struct

Revision ID: frfe04_block_struct_cols_01
Revises: pd_fee_scenario_rate_metadata_01
Create Date: 2026-07-09

Close FRFE04-BLOCK-01/02: add the approved structural columns to
t_pay_list (list_type, flow_dir, invoice_no_from, invoice_no_to) and
t_gov_payment (fee_code, year_no, planned_amt, planned_currency,
paid_currency, voucher_no, invoice_no) per FRMS_SPEC2_2nd_POST.md.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "frfe04_block_struct_cols_01"
down_revision = "pd_fee_scenario_rate_metadata_01"
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


def upgrade() -> None:
    if _table_exists("t_pay_list"):
        pay_list_columns = [
            ("list_type", sa.String(32)),
            ("flow_dir", sa.String(32)),
            ("invoice_no_from", sa.String(64)),
            ("invoice_no_to", sa.String(64)),
        ]
        with op.batch_alter_table("t_pay_list") as batch_op:
            for column_name, column_type in pay_list_columns:
                if not _column_exists("t_pay_list", column_name):
                    batch_op.add_column(sa.Column(column_name, column_type, nullable=True))

    if _table_exists("t_gov_payment"):
        gov_payment_columns = [
            ("fee_code", sa.String(64)),
            ("year_no", sa.Integer()),
            ("planned_amt", sa.Numeric(18, 2)),
            ("planned_currency", sa.String(8)),
            ("paid_currency", sa.String(8)),
            ("voucher_no", sa.String(64)),
            ("invoice_no", sa.String(64)),
        ]
        with op.batch_alter_table("t_gov_payment") as batch_op:
            for column_name, column_type in gov_payment_columns:
                if not _column_exists("t_gov_payment", column_name):
                    batch_op.add_column(sa.Column(column_name, column_type, nullable=True))


def downgrade() -> None:
    pass
