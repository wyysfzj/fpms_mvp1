"""pe_be_db_08_create_t_commission_settlement

Revision ID: pe_be_db_08_comm_settle_01
Revises: pe_be_db_07_commission_01
Create Date: 2026-02-28

Create t_commission_settlement and t_commission_settle_line.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_08_comm_settle_01"
down_revision = "pe_be_db_07_commission_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_commission_settlement",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("settlement_no", sa.String(64), nullable=True),
        sa.Column("agent_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("currency", sa.String(8), nullable=False, server_default=sa.text("'CNY'")),
        sa.Column("settle_date", sa.Date(), nullable=True),
        sa.Column("period_from", sa.Date(), nullable=True),
        sa.Column("period_to", sa.Date(), nullable=True),
        sa.Column("line_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
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
    op.create_index("ix_t_commission_settlement_status", "t_commission_settlement", ["status"])
    op.create_index(
        "ix_t_commission_settlement_settle_date", "t_commission_settlement", ["settle_date"]
    )

    op.create_table(
        "t_commission_settle_line",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "settlement_id",
            sa.Integer(),
            sa.ForeignKey("t_commission_settlement.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "commission_id",
            sa.Integer(),
            sa.ForeignKey("t_commission.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("line_no", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.String(24), nullable=False, server_default=sa.text("'PENDING'")),
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
        sa.UniqueConstraint("settlement_id", "line_no", name="uq_t_comm_settle_line_no"),
        sa.UniqueConstraint(
            "settlement_id", "commission_id", name="uq_t_comm_settle_line_commission"
        ),
    )
    op.create_index(
        "ix_t_commission_settle_line_settlement_id",
        "t_commission_settle_line",
        ["settlement_id"],
    )
    op.create_index(
        "ix_t_commission_settle_line_commission_id",
        "t_commission_settle_line",
        ["commission_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_t_commission_settle_line_commission_id", table_name="t_commission_settle_line"
    )
    op.drop_index(
        "ix_t_commission_settle_line_settlement_id", table_name="t_commission_settle_line"
    )
    op.drop_table("t_commission_settle_line")

    op.drop_index("ix_t_commission_settlement_settle_date", table_name="t_commission_settlement")
    op.drop_index("ix_t_commission_settlement_status", table_name="t_commission_settlement")
    op.drop_table("t_commission_settlement")
