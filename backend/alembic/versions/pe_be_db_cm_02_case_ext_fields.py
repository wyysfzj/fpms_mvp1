"""pe_be_db_cm_02_case_ext_fields

Revision ID: pe_be_db_cm_02_case_ext_01
Revises: pe_be_db_08_comm_settle_01
Create Date: 2026-03-15

Add deferred Batch 1 case fields:
- foreign agent / foreign ref
- PCT fields
- invalidation fields
- t_bio_deposit
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "pe_be_db_cm_02_case_ext_01"
down_revision = "pe_be_db_08_comm_settle_01"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table"),
        {"table": table},
    )
    return result.first() is not None


def _col_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(sa.text(f"PRAGMA table_info('{table}')"))
    return any(row[1] == column for row in result)


def upgrade() -> None:
    case_columns = [
        ("foreign_agent_id", sa.String(36)),
        ("foreign_ref", sa.String(64)),
        ("ro", sa.String(64)),
        ("isa", sa.String(64)),
        ("ipea", sa.String(64)),
        ("intl_app_no", sa.String(64)),
        ("intl_app_date", sa.Date()),
        ("intl_pub_no", sa.String(64)),
        ("intl_pub_date", sa.Date()),
        ("intl_pub_lang", sa.String(32)),
        ("need_iper", sa.Boolean()),
        ("iper_date", sa.Date()),
        ("pct_national_entry_date", sa.Date()),
        ("original_case_id", sa.String(36)),
        ("invalid_client_id", sa.String(36)),
        ("invalid_patentee", sa.String(255)),
        ("invalid_requester", sa.String(255)),
        ("invalid_role", sa.String(32)),
    ]

    with op.batch_alter_table("t_case") as batch_op:
        for name, column_type in case_columns:
            if not _col_exists("t_case", name):
                batch_op.add_column(sa.Column(name, column_type, nullable=True))

    if not _table_exists("t_bio_deposit"):
        op.create_table(
            "t_bio_deposit",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "case_id",
                sa.String(36),
                sa.ForeignKey("t_case.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("seq", sa.Integer(), nullable=False),
            sa.Column("deposit_no", sa.String(64), nullable=True),
            sa.Column("deposit_unit_name", sa.String(255), nullable=True),
            sa.Column("deposit_date", sa.Date(), nullable=True),
            sa.Column("name", sa.String(255), nullable=True),
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
            sa.UniqueConstraint("case_id", "seq", name="uq_bio_deposit_seq"),
        )
        op.create_index("ix_t_bio_deposit_case_id", "t_bio_deposit", ["case_id"])


def downgrade() -> None:
    pass
