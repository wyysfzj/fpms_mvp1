"""pe_be_db_04_create_t_annuity_task

Revision ID: pe_be_db_04_annuity_task_01
Revises: pe_be_db_03_gov_payment_01
Create Date: 2026-02-28

Create t_annuity_task for annual fee task lifecycle.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_04_annuity_task_01"
down_revision = "pe_be_db_03_gov_payment_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_annuity_task",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "case_id",
            sa.String(36),
            sa.ForeignKey("t_case.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("year_no", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("client_instruction", sa.String(24), nullable=True),
        sa.Column("instruction_date", sa.Date(), nullable=True),
        sa.Column(
            "notice_status", sa.String(24), nullable=False, server_default=sa.text("'PENDING'")
        ),
        sa.Column("notice_sent_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column("remark", sa.Text(), nullable=True),
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
    )

    op.create_index("ix_t_annuity_task_case_id", "t_annuity_task", ["case_id"])
    op.create_index("ix_t_annuity_task_client_id", "t_annuity_task", ["client_id"])
    op.create_index("ix_t_annuity_task_due_date", "t_annuity_task", ["due_date"])
    op.create_index("ix_t_annuity_task_notice_status", "t_annuity_task", ["notice_status"])
    op.create_index("ix_t_annuity_task_status", "t_annuity_task", ["status"])


def downgrade() -> None:
    op.drop_index("ix_t_annuity_task_status", table_name="t_annuity_task")
    op.drop_index("ix_t_annuity_task_notice_status", table_name="t_annuity_task")
    op.drop_index("ix_t_annuity_task_due_date", table_name="t_annuity_task")
    op.drop_index("ix_t_annuity_task_client_id", table_name="t_annuity_task")
    op.drop_index("ix_t_annuity_task_case_id", table_name="t_annuity_task")
    op.drop_table("t_annuity_task")
