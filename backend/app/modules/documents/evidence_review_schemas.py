from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.documents.evidence_service import EvidenceReviewDecision


class EvidenceVersionReviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(strict=True)
    decision: EvidenceReviewDecision
    reviewed_at: datetime
    idempotency_key: str = Field(strict=True)

    @field_validator("reviewed_at")
    @classmethod
    def require_naive_reviewed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            raise ValueError("reviewed_at must be naive")
        return value
