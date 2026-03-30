"""gfpre_db_01_create_t_grant_fee_task

Revision ID: gfpre_db_01_create_t_grant_fee_task_01
Revises: mdpre_db_01_masterdata_carriers_01
Create Date: 2026-03-30

Create the minimal SQLite-safe grant fee task carrier.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "gfpre_db_01_create_t_grant_fee_task_01"
down_revision = "mdpre_db_01_masterdata_carriers_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_grant_fee_task",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "case_id",
            sa.String(36),
            sa.ForeignKey("t_case.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(16), nullable=False, server_default=sa.text("'GRANT'")),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("gov_fee_amt", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "service_fee_amt",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column(
            "client_instruction",
            sa.String(24),
            nullable=False,
            server_default=sa.text("'NONE'"),
        ),
        sa.Column("notify_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "draft_generated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("notice_sent", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_overdue", sa.Boolean(), nullable=False, server_default=sa.text("0")),
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


def downgrade() -> None:
    raise NotImplementedError("Downgrade not implemented for MVP migrations (intentional).")
