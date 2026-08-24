"""allow the frozen V6 GovPayment demo command operation

Revision ID: demo_v6_gov_payment_operation_01
Revises: demo_abc_command_reconcile_01
"""

from __future__ import annotations

from alembic import op

revision = "demo_v6_gov_payment_operation_01"
down_revision = "demo_abc_command_reconcile_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table(
        "t_demo_finance_command",
        recreate="always",
    ) as batch:
        batch.drop_constraint(
            "ck_demo_finance_command_operation",
            type_="check",
        )
        batch.create_check_constraint(
            "ck_demo_finance_command_operation",
            "operation IN ('BILL', 'PAYMENT', 'OFFSET', 'GOV_PAYMENT')",
        )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
