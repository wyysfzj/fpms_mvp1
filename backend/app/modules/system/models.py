from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CustomerDecisionGate(Base):
    __tablename__ = "t_customer_decision_gate"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    gate_code: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_key: Mapped[str] = mapped_column(String(256), nullable=False)
    decision_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_status: Mapped[str] = mapped_column(String(32), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    source_version: Mapped[str] = mapped_column(String(128), nullable=False)
    confirmed_by: Mapped[str] = mapped_column(String(36), nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    supersedes_gate_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    decision_snapshot: Mapped[str] = mapped_column(Text, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    current_identity_key: Mapped[str | None] = mapped_column(String(320), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        CheckConstraint(
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
        CheckConstraint(
            "decision_status IN ('CONFIRMED', 'REVOKED')",
            name="ck_t_customer_decision_gate_decision_status",
        ),
        ForeignKeyConstraint(
            ["confirmed_by"],
            ["t_user.id"],
            name="fk_t_customer_decision_gate_confirmed_by",
        ),
        ForeignKeyConstraint(
            ["supersedes_gate_id"],
            ["t_customer_decision_gate.id"],
            name="fk_t_customer_decision_gate_supersedes_gate_id",
        ),
        UniqueConstraint(
            "idempotency_key",
            name="uq_t_customer_decision_gate_idempotency_key",
        ),
        UniqueConstraint(
            "current_identity_key",
            name="uq_t_customer_decision_gate_current_identity_key",
        ),
    )
