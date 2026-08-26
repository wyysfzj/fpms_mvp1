from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from app.modules.fees.obligation_schemas import FeeObligationDetailOut


class DemoServiceLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_code: str
    name_zh_cn: str
    currency: str
    unit_price: Decimal
    quantity: int
    final_quantity: int
    adjustable: bool
    amount: Decimal
    source_ref: str
    source_version: str
    source_sha256: str
    disclaimer_zh_cn: str


class DemoServiceItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    classification: str
    bundle_id: str
    bundle_version: str
    manifest_sha256: str
    template_code: str
    template_sha256: str
    template_required_variables: tuple[str, ...]
    items: tuple[DemoServiceLineOut, ...]
    total_amount: Decimal


class DemoBusinessCountsOut(RootModel[dict[str, int]]):
    pass


class DemoPreflightOut(DemoServiceItemOut):
    authority_classification: str
    customer_activation_eligible: bool
    readiness: str
    run_id: str
    candidate_commit: str
    candidate_tree: str
    authority_sha256: str
    contract_version: str
    business_counts: DemoBusinessCountsOut


class DemoServiceObligationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    idempotency_key: str = Field(..., min_length=1, max_length=96)


class DemoServiceObligationOut(DemoServiceItemOut):
    obligation: FeeObligationDetailOut
    source_activity_id: str
    idempotency_key: str
    reused: bool


class DemoServiceAdjustmentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: UUID
    expected_quantity: int = Field(..., ge=1)
    new_quantity: int = Field(..., ge=1)
    reason: str = Field(..., min_length=1, max_length=256)
    idempotency_key: str = Field(..., min_length=1, max_length=96)

    @field_validator("reason")
    @classmethod
    def reason_must_include_chinese(cls, value: str) -> str:
        if value != value.strip() or not any("\u4e00" <= char <= "\u9fff" for char in value):
            raise ValueError("调整原因必须包含中文")
        return value


class DemoServiceAdjustmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    draft_id: str
    original_obligation_id: str
    superseding_obligation_id: str
    adjustment_activity_id: str
    instruction_activity_id: str
    fee_item_ids: tuple[str, ...]
    before_total: Decimal
    after_total: Decimal
    idempotency_key: str
    reused: bool


class DemoV6DraftSourceFactLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current_item_id: str
    obligation_line_id: str
    fee_code: str
    fee_name: str
    quantity: int
    unit_price: Decimal
    amount: Decimal
    source_authority: str
    source_ref: str
    source_version: str
    effective_date: date | None
    source_sha256: str
    activation_status: str
    adjustable: bool
    adjustment_activity_id: str | None
    adjustment_reason: str | None
    adjustment_before_digest: str | None
    adjustment_after_digest: str | None


class DemoV6DraftSourceFactsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    draft_id: str
    draft_status: str
    fee_domain: str
    lines: tuple[DemoV6DraftSourceFactLineOut, ...]
