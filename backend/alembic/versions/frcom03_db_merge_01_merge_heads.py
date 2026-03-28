"""frcom03_db_merge_01_merge_heads

Revision ID: frcom03_db_merge_01_merge_heads
Revises: frcom03_db_01_case_agent_split_01, pe_fr_fe_06_01
Create Date: 2026-03-28

Merge the FR-COM-03 DB prerequisite branch with the existing PE FR FE branch
so the repository returns to a single Alembic head.
"""

from __future__ import annotations

from alembic import op  # noqa: F401

revision = "frcom03_db_merge_01_merge_heads"
down_revision = ("frcom03_db_01_case_agent_split_01", "pe_fr_fe_06_01")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Empty merge revision: no schema changes, only graph convergence.
    pass


def downgrade() -> None:
    # Merge revisions are intentionally no-op on downgrade for this PoC.
    pass
