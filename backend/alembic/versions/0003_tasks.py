"""task templates + tasks + logs

Revision ID: 0003_tasks
Revises: 0002_documents
Create Date: 2025-12-20T16:24:58
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_tasks"
down_revision = "0002_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "t_task_template",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )

    op.create_table(
        "t_task",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "case_id", sa.String(36), sa.ForeignKey("t_case.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("document_id", sa.String(36), sa.ForeignKey("t_document.id"), nullable=True),
        sa.Column(
            "task_template_id", sa.String(36), sa.ForeignKey("t_task_template.id"), nullable=True
        ),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("base_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("internal_due_date", sa.Date(), nullable=True),
        sa.Column("worker_id", sa.String(36), sa.ForeignKey("t_user.id"), nullable=True),
        sa.Column("supervisor_id", sa.String(36), sa.ForeignKey("t_user.id"), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column("done_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )
    op.create_index("idx_task_case_due_status", "t_task", ["case_id", "due_date", "status"])
    op.create_index("idx_task_worker_due", "t_task", ["worker_id", "due_date"])

    op.create_table(
        "t_task_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "task_id", sa.String(36), sa.ForeignKey("t_task.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("from_status", sa.String(16), nullable=True),
        sa.Column("to_status", sa.String(16), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
    )


def downgrade() -> None:
    raise NotImplementedError("Downgrade not implemented for MVP migrations (intentional).")
