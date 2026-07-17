from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.modules.fees.obligation_contracts import (
    FeeClientInstruction,
    FeeClientInstructionStatus,
)


class FeeObligationInstructionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instruction: FeeClientInstruction
    idempotency_key: str


class FeeObligationInstructionOut(BaseModel):
    obligation_id: str
    client_instruction_status: FeeClientInstructionStatus
    activity_id: str
    idempotency_key: str
    reused: bool
