from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.modules.fees.fee_reduction import FeeReductionApprovalScopeType


class FeeReductionApprovalCreateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    scope_type: FeeReductionApprovalScopeType
    applicant_ids: tuple[str, ...]
    eligibility_attributes_version: str
    eligibility_attributes_json: str
    reduction_ratio: Decimal
    fee_codes: tuple[str, ...]
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    expected_source_content_hash: str
    confirmed_at: datetime

    @field_validator("confirmed_at")
    @classmethod
    def require_naive_confirmed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            raise ValueError("confirmed_at must be naive")
        return value


class FeeReductionApprovalCreateOut(BaseModel):
    approval_id: str


class FeeReductionApprovalListItemOut(BaseModel):
    approval_id: str
    scope_type: FeeReductionApprovalScopeType
    case_id: str | None
    applicant_set_key: str | None
    reduction_ratio: Decimal
    fee_codes: tuple[str, ...]
    fee_year_from: int | None
    fee_year_to: int | None
    effective_from: date
    effective_to: date | None
    source_evidence_version_id: str
    confirmation_status: str
    confirmed_at: datetime
    confirmed_by: str
    is_current: bool
