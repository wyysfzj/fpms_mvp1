from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.fees.obligation_schemas import FeeObligationDetailOut


class DemoServiceItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    classification: str
    bundle_id: str
    bundle_version: str
    manifest_sha256: str
    template_code: str
    template_sha256: str
    template_required_variables: tuple[str, ...]
    item_code: str
    name_zh_cn: str
    currency: str
    amount: Decimal
    source_ref: str
    source_version: str
    source_sha256: str
    disclaimer_zh_cn: str


class DemoServiceObligationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    item_code: str = Field(..., min_length=1, max_length=64)
    idempotency_key: str = Field(..., min_length=1, max_length=96)


class DemoServiceObligationOut(DemoServiceItemOut):
    obligation: FeeObligationDetailOut
    source_activity_id: str
    idempotency_key: str
    reused: bool
