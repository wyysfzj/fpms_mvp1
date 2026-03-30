"""mdpre_db_01_masterdata_carriers

Revision ID: mdpre_db_01_masterdata_carriers_01
Revises: docdsp_db_01_doc_dispatch_tables_01
Create Date: 2026-03-30

Introduce structured Applicant/Country carriers with SQLite-safe minimal fields.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "mdpre_db_01_masterdata_carriers_01"
down_revision = "docdsp_db_01_doc_dispatch_tables_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if not _table_exists("t_applicant"):
        op.create_table(
            "t_applicant",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("code", sa.String(64), nullable=False, unique=True),
            sa.Column("name_cn", sa.String(256), nullable=False),
            sa.Column("name_en", sa.String(256), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.UniqueConstraint("name_cn", name="uq_applicant_name_cn"),
        )

    if not _table_exists("t_country"):
        op.create_table(
            "t_country",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("code", sa.String(64), nullable=False, unique=True),
            sa.Column("name_cn", sa.String(256), nullable=False),
            sa.Column("name_en", sa.String(256), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.UniqueConstraint("name_cn", name="uq_country_name_cn"),
        )


def downgrade() -> None:
    pass


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
        {"table_name": table_name},
    )
    return result.first() is not None
