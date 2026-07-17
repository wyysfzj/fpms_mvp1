from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.system.decision_gate_service import (
    DecisionGateCode,
    DecisionGateRecordDisposition,
    DecisionGateStatus,
)


class DecisionGateRecordIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_code: DecisionGateCode
    scope_key: str
    decision_value: str | None
    decision_status: DecisionGateStatus
    source_reference: str
    source_version: str
    effective_at: datetime
    idempotency_key: str
    expected_current_gate_id: str | None


class DecisionGateRecordOut(BaseModel):
    gate_id: str
    gate_code: DecisionGateCode
    scope_key: str
    decision_value: str | None
    decision_status: DecisionGateStatus
    source_reference: str
    source_version: str
    confirmed_by: str
    effective_at: datetime
    supersedes_gate_id: str | None
    decision_snapshot: str
    idempotency_key: str
    current_identity_key: str | None
    disposition: DecisionGateRecordDisposition
