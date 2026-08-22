"""add customer decision gate carrier

Revision ID: v8_post_w1_customer_decision_gate_01
Revises: v8_w1_f5_fee_reduction_01
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "v8_post_w1_customer_decision_gate_01"
down_revision = "v8_w1_f5_fee_reduction_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_customer_decision_gate",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("gate_code", sa.String(32), nullable=False),
        sa.Column("scope_key", sa.String(256), nullable=False),
        sa.Column("decision_value", sa.Text(), nullable=True),
        sa.Column("decision_status", sa.String(32), nullable=False),
        sa.Column("source_reference", sa.String(512), nullable=False),
        sa.Column("source_version", sa.String(128), nullable=False),
        sa.Column("confirmed_by", sa.String(36), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("supersedes_gate_id", sa.String(36), nullable=True),
        sa.Column("decision_snapshot", sa.Text(), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("current_identity_key", sa.String(320), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "gate_code IN ("
            "'DG-FEE-APPLICATION-DRAFT', "
            "'DG-FEE-GRANT-YEAR-DRAFT', "
            "'DG-FEE-FUTURE-ANNUITY', "
            "'DG-GRANT-EVIDENCE-SOURCE', "
            "'DG-GRANT-MANUAL-REVIEW', "
            "'DG-PAYMENT-WORKBOOK', "
            "'DG-SERVICE-RATE-VERSION', "
            "'DG-LEGACY-FORM-CLASS'"
            ")",
            name="ck_t_customer_decision_gate_gate_code",
        ),
        sa.CheckConstraint(
            "decision_status IN ('CONFIRMED', 'REVOKED')",
            name="ck_t_customer_decision_gate_decision_status",
        ),
        sa.ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_customer_decision_gate_confirmed_by",
        ),
        sa.ForeignKeyConstraint(
            ["supersedes_gate_id"],
            ["t_customer_decision_gate.id"],
            name="fk_t_customer_decision_gate_supersedes_gate_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_t_customer_decision_gate_idempotency_key",
        ),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_customer_decision_gate_current_identity_key",
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
