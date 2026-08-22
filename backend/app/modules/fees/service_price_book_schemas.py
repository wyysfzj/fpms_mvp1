from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ServicePriceBookImportItemIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_code: str
    unit_price: Decimal


class ServicePriceBookImportIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_classification: str
    book_version: str
    scope_key: str
    currency: str
    tax_policy: str
    discount_policy: str
    source_reference: str
    source_content: str
    expected_source_content_hash: str
    items: list[ServicePriceBookImportItemIn]
    effective_from: datetime
    effective_to: datetime | None = None
    idempotency_key: str


class ServicePriceBookImportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    price_book_id: str
    source_classification: str
    book_version: str
    scope_key: str
    currency: str
    tax_policy: str
    discount_policy: str
    source_reference: str
    source_content_hash: str
    item_snapshot_hash: str
    item_count: int
    status: str
    effective_from: datetime
    effective_to: datetime | None
    created_by: str
    disposition: str


class ServicePriceBookActivationIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_reason: str
    expected_current_price_book_id: UUID | None


class ServicePriceBookActivationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    price_book_id: str
    source_classification: str
    book_version: str
    scope_key: str
    source_content_hash: str
    item_snapshot_hash: str
    item_count: int
    status: str
    effective_from: datetime
    effective_to: datetime | None
    approved_by: str
    approved_at: datetime
    activated_by: str
    activated_at: datetime
    current_identity_key: str
    supersedes_price_book_id: str | None
    disposition: Literal["ACTIVATED", "REUSED"]
