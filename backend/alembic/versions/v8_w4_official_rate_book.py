"""add frozen official-rate-book carrier and fee-rate compatibility link

Revision ID: v8_w4_official_rate_book_01
Revises: v8_post_w1_customer_decision_gate_01
"""

from alembic import op
import sqlalchemy as sa


revision = "v8_w4_official_rate_book_01"
down_revision = "v8_post_w1_customer_decision_gate_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_fee_rate_book",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("book_code", sa.String(length=64), nullable=False),
        sa.Column("version_code", sa.String(length=128), nullable=False),
        sa.Column("source_authority", sa.String(length=32), nullable=False),
        sa.Column("source_reference", sa.String(length=512), nullable=False),
        sa.Column("source_version", sa.String(length=128), nullable=False),
        sa.Column("source_published_on", sa.Date(), nullable=False),
        sa.Column("source_snapshot", sa.Text(), nullable=False),
        sa.Column("source_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "approval_status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
        sa.Column("approved_by", sa.String(length=36), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column(
            "activation_status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'INACTIVE'"),
        ),
        sa.Column("activated_by", sa.String(length=36), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("current_identity_key", sa.String(length=128), nullable=True),
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
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("updated_by", sa.String(length=36), nullable=True),
        sa.CheckConstraint(
            "source_authority = 'CNIPA'",
            name="ck_t_fee_rate_book_source_authority",
        ),
        sa.CheckConstraint(
            "length(source_snapshot_hash) = 64",
            name="ck_t_fee_rate_book_source_hash",
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_t_fee_rate_book_effective_interval",
        ),
        sa.CheckConstraint(
            "approval_status IN ('PENDING', 'APPROVED', 'REJECTED')",
            name="ck_t_fee_rate_book_approval_status",
        ),
        sa.CheckConstraint(
            "(approval_status = 'PENDING' AND approved_by IS NULL "
            "AND approved_at IS NULL) "
            "OR (approval_status IN ('APPROVED', 'REJECTED') "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL)",
            name="ck_t_fee_rate_book_approval_tuple",
        ),
        sa.CheckConstraint(
            "activation_status IN ('INACTIVE', 'ACTIVE', 'RETIRED')",
            name="ck_t_fee_rate_book_activation_status",
        ),
        sa.CheckConstraint(
            "(activation_status = 'INACTIVE' AND activated_by IS NULL "
            "AND activated_at IS NULL AND current_identity_key IS NULL) "
            "OR (activation_status = 'ACTIVE' AND approval_status = 'APPROVED' "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND current_identity_key = source_authority || '|' || book_code) "
            "OR (activation_status = 'RETIRED' AND approval_status = 'APPROVED' "
            "AND approved_by IS NOT NULL AND approved_at IS NOT NULL "
            "AND activated_by IS NOT NULL AND activated_at IS NOT NULL "
            "AND current_identity_key IS NULL)",
            name="ck_t_fee_rate_book_activation_tuple",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"],
            ["t_user.id"],
            name="fk_t_fee_rate_book_approved_by",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["activated_by"],
            ["t_user.id"],
            name="fk_t_fee_rate_book_activated_by",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_authority",
            "book_code",
            "version_code",
            name="uq_t_fee_rate_book_series_version",
        ),
        sa.UniqueConstraint(
            "current_identity_key",
            name="uq_t_fee_rate_book_current_identity_key",
        ),
    )

    with op.batch_alter_table("t_fee_rate") as batch_op:
        batch_op.add_column(sa.Column("official_rate_book_id", sa.String(length=36), nullable=True))
        batch_op.create_foreign_key(
            "fk_t_fee_rate_official_rate_book_id",
            "t_fee_rate_book",
            ["official_rate_book_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_check_constraint(
            "ck_t_fee_rate_official_book_gov_only",
            "official_rate_book_id IS NULL OR fee_type = 'GOV'",
        )

    op.create_index(
        "ix_t_fee_rate_book_series_interval",
        "t_fee_rate_book",
        [
            "source_authority",
            "book_code",
            "activation_status",
            "effective_from",
            "effective_to",
        ],
        unique=False,
    )
    op.create_index(
        "ix_t_fee_rate_official_rate_book_id",
        "t_fee_rate",
        ["official_rate_book_id"],
        unique=False,
    )


def downgrade() -> None:
    raise NotImplementedError("This is a forward-only migration")
