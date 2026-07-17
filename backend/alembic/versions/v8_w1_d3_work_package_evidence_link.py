"""add work-package evidence version link carrier

Revision ID: v8_w1_d3_workpkg_evidence_01
Revises: v8_w1_d2_evidence_derivation_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_w1_d3_workpkg_evidence_01"
down_revision = "v8_w1_d2_evidence_derivation_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("t_official_work_package_manifest") as batch_op:
        batch_op.add_column(sa.Column("evidence_version_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_t_official_work_package_manifest_evidence_version_id",
            "t_document_evidence_version",
            ["evidence_version_id"],
            ["id"],
        )

    op.create_index(
        "ix_t_official_work_package_manifest_evidence_version_id",
        "t_official_work_package_manifest",
        ["evidence_version_id"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
