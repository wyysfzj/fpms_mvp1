"""caserpt_trend_carrier_db_merge_01

Revision ID: caserpt_trend_carrier_db_merge_01
Revises: casefilter_pre_01_case_applicant_masterdata_link_01, caserpt_trend_carrier_db_01
Create Date: 2026-04-05

Merge the case trend carrier migration branch back into the current Alembic head.
"""

from __future__ import annotations

revision = "caserpt_trend_carrier_db_merge_01"
down_revision = (
    "casefilter_pre_01_case_applicant_masterdata_link_01",
    "caserpt_trend_carrier_db_01",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
