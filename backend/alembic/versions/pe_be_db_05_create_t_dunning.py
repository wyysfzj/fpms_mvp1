"""pe_be_db_05_create_t_dunning

Revision ID: pe_be_db_05_dunning_01
Revises: pe_be_db_04_annuity_task_01
Create Date: 2026-02-28

Create t_dunning and t_dunning_line for dunning batches and line snapshots.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_05_dunning_01"
down_revision = "pe_be_db_04_annuity_task_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_dunning",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("t_client.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("dunning_no", sa.String(64), nullable=True),
        sa.Column("round_no", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("to_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("sent_date", sa.Date(), nullable=True),
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
    op.create_index("ix_t_dunning_client_id", "t_dunning", ["client_id"])
    op.create_index("ix_t_dunning_round_no", "t_dunning", ["round_no"])
    op.create_index("ix_t_dunning_status", "t_dunning", ["status"])

    op.create_table(
        "t_dunning_line",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "dunning_id",
            sa.Integer(),
            sa.ForeignKey("t_dunning.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "bill_id",
            sa.String(36),
            sa.ForeignKey("t_bill.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("line_no", sa.Integer(), nullable=False, server_default=sa.text("1")),
        # Snapshot fields captured at dunning generation time.
        sa.Column("bill_no_snapshot", sa.String(64), nullable=True),
        sa.Column("due_date_snapshot", sa.Date(), nullable=True),
        sa.Column(
            "bill_status_snapshot",
            sa.String(24),
            nullable=True,
        ),
        sa.Column(
            "outstanding_amount",
            sa.Numeric(18, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("currency_snapshot", sa.String(8), nullable=True),
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
        sa.UniqueConstraint("dunning_id", "line_no", name="uq_t_dunning_line_no"),
    )
    op.create_index("ix_t_dunning_line_dunning_id", "t_dunning_line", ["dunning_id"])
    op.create_index("ix_t_dunning_line_bill_id", "t_dunning_line", ["bill_id"])


def downgrade() -> None:
    op.drop_index("ix_t_dunning_line_bill_id", table_name="t_dunning_line")
    op.drop_index("ix_t_dunning_line_dunning_id", table_name="t_dunning_line")
    op.drop_table("t_dunning_line")

    op.drop_index("ix_t_dunning_status", table_name="t_dunning")
    op.drop_index("ix_t_dunning_round_no", table_name="t_dunning")
    op.drop_index("ix_t_dunning_client_id", table_name="t_dunning")
    op.drop_table("t_dunning")
