"""bind demo commands to exact reconciliation ownership

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


def upgrade() -> None:
    bind = op.get_bind()
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

def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
