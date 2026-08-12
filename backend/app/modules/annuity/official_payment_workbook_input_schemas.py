from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReviewWorkbookInputIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["APPROVE", "REJECT"]
    reason: str = Field(..., min_length=1, max_length=2000)


class ActivateWorkbookInputIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idempotency_key: str = Field(..., min_length=1, max_length=128)


class RetireWorkbookInputIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(..., min_length=1, max_length=2000)
    idempotency_key: str = Field(..., min_length=1, max_length=128)


class WorkbookInputOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version_id: str
    scope_key: str
    source_classification: str
    template_version: str
    template_content_hash: str
    upload_proof_content_hash: str
    structure_snapshot_hash: str
    workflow_status: str
    activation_status: str
    effective_from: datetime
    effective_to: datetime | None
    supersedes_version_id: str | None
    current_identity_key: str | None
    created_by: str
    validated_by: str | None
    validated_at: datetime | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    activated_by: str | None
    activated_at: datetime | None
    retired_by: str | None
    retired_at: datetime | None
    retirement_reason: str | None
    disposition: str
