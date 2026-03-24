"""pe_fr_fe_06_annuity_task_ext

Revision ID: pe_fr_fe_06_01
Revises: pe_fr_fe_07_01
Create Date: 2026-03-25

Add 6 columns to t_annuity_task and 1 column to t_case (first_annuity_year).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_fr_fe_06_01"
down_revision = "pe_fr_fe_07_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # -- t_annuity_task: 6 new columns --
    if insp.has_table("t_annuity_task"):
        existing = {col["name"] for col in insp.get_columns("t_annuity_task")}
        annuity_cols = [
            ("gov_fee_amt", sa.Numeric(18, 2), sa.text("0")),
            ("service_fee_amt", sa.Numeric(18, 2), sa.text("0")),
            ("notify_count", sa.Integer(), sa.text("0")),
            ("pay_next_year", sa.Boolean(), sa.text("0")),
            ("draft_generated", sa.Boolean(), sa.text("0")),
            ("notice_sent", sa.Boolean(), sa.text("0")),
        ]
        with op.batch_alter_table("t_annuity_task") as batch_op:
            for col_name, col_type, server_default in annuity_cols:
                if col_name not in existing:
                    batch_op.add_column(
                        sa.Column(col_name, col_type, nullable=True, server_default=server_default)
                    )

    # -- t_case: first_annuity_year --
    if insp.has_table("t_case"):
        existing_case = {col["name"] for col in insp.get_columns("t_case")}
        if "first_annuity_year" not in existing_case:
            with op.batch_alter_table("t_case") as batch_op:
                batch_op.add_column(
                    sa.Column("first_annuity_year", sa.Integer(), nullable=True)
                )


def downgrade() -> None:
    pass
