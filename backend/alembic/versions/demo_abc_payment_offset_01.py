"""add local-demo payment and offset carriers

Revision ID: demo_abc_payment_offset_01
Revises: demo_abc_bill_source_01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "demo_abc_payment_offset_01"
down_revision = "demo_abc_bill_source_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    duplicate_pay_no = bind.execute(
        sa.text(
            "SELECT pay_no FROM t_payment WHERE pay_no IS NOT NULL "
            "GROUP BY pay_no HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate_pay_no is not None:
        raise RuntimeError("duplicate pay_no blocks demo payment migration")

    op.add_column("t_payment", sa.Column("pay_method", sa.String(24), nullable=True))
    op.add_column("t_payment", sa.Column("bank_ref_no", sa.String(96), nullable=True))
    op.add_column("t_case_receipt", sa.Column("receipt_key", sa.String(192), nullable=True))
    op.create_index("ux_payment_pay_no_nonnull", "t_payment", ["pay_no"], unique=True)
    op.create_index(
        "ux_payment_bank_ref_no_nonnull", "t_payment", ["bank_ref_no"], unique=True
    )
    op.create_index(
        "ux_case_receipt_key_nonnull", "t_case_receipt", ["receipt_key"], unique=True
    )

    for table_name, target_column, target_table in (
        ("t_demo_payment_command", "payment_id", "t_payment"),
        ("t_demo_offset_command", "offset_id", "t_offset"),
    ):
        op.create_table(
            table_name,
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column(target_column, sa.String(36), nullable=False),
            sa.Column("idempotency_key", sa.String(96), nullable=False),
            sa.Column("command_hash", sa.String(64), nullable=False),
            sa.Column("created_by", sa.String(36), nullable=True),
            sa.Column("updated_by", sa.String(36), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(
                [target_column],
                [f"{target_table}.id"],
                name=f"fk_{table_name}_target",
                ondelete="CASCADE",
            ),
            sa.UniqueConstraint(target_column, name=f"uq_{table_name}_target"),
            sa.UniqueConstraint("idempotency_key", name=f"uq_{table_name}_idempotency"),
            sa.CheckConstraint("length(command_hash) = 64", name=f"ck_{table_name}_hash"),
        )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
