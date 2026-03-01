from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BillCreateSchema(BaseModel):
    """Schema for creating bills."""

    client_id: str = Field(..., min_length=1)
    bill_no: str | None = Field(None, max_length=64)
    currency: str = Field("CNY", max_length=8)
    direction: str = Field("AR", max_length=8)
    status: str = Field("UNSETTLED", max_length=24)
    bill_date: date | None = None
    due_date: date | None = None
    total_gov: Decimal = Field(Decimal("0"), ge=0)
    total_service: Decimal = Field(Decimal("0"), ge=0)
    total_misc: Decimal = Field(Decimal("0"), ge=0)


class BillUpdateSchema(BaseModel):
    """Schema for updating bills."""

    bill_no: str | None = Field(None, max_length=64)
    currency: str | None = Field(None, max_length=8)
    direction: str | None = Field(None, max_length=8)
    status: str | None = Field(None, max_length=24)
    bill_date: date | None = None
    due_date: date | None = None
    total_gov: Decimal | None = Field(None, ge=0)
    total_service: Decimal | None = Field(None, ge=0)
    total_misc: Decimal | None = Field(None, ge=0)
    amount: Decimal | None = Field(None, ge=0)
    balance: Decimal | None = Field(None, ge=0)


class BillFromDraftsRequest(BaseModel):
    """Request schema for creating a bill from fee drafts."""

    draft_ids: list[str] = Field(..., min_length=1)
    bill_no: str | None = Field(None, max_length=64)


class BillResponse(BaseModel):
    """Response schema for bills."""

    id: str
    bill_no: str | None
    client_id: str
    currency: str
    direction: str
    status: str


class PaymentSchema(BaseModel):
    """Schema for recording payments."""

    client_id: str = Field(..., min_length=1)
    amount: Decimal = Field(..., ge=0)
    pay_no: str | None = Field(None, max_length=64)
    pay_date: date | None = None
    currency: str = Field("CNY", max_length=8)
    remark: str | None = None


class PaymentResponse(BaseModel):
    """Response schema for payments."""

    id: str
    pay_no: str | None
    client_id: str
    pay_date: date | None
    currency: str
    amount: Decimal


class OffsetCreateSchema(BaseModel):
    """Schema for creating offsets."""

    payment_line_id: str = Field(..., min_length=1)
    bill_id: str = Field(..., min_length=1)
    offset_amt: Decimal = Field(..., gt=0)
    offset_date: date | None = None


class OffsetResponse(BaseModel):
    """Response schema for offsets."""

    id: str
    payment_line_id: str
    bill_id: str
    offset_amt: Decimal
    offset_date: date | None
    is_reversed: bool


class CaseReceiptResponse(BaseModel):
    """Response schema for case receipts."""

    id: str
    case_id: str
    fee_type: str | None
    currency: str
    receivable_amt: Decimal
    received_amt: Decimal
    last_receipt_date: date | None
    fee_code: str | None = None
    year_no: int | None = None
    is_arrears: bool | None = None
    invoice_no: str | None = None
    is_commissionable: bool | None = None


class BillStatusSchema(BaseModel):
    """Schema for bill status transitions."""

    status: str = Field(..., max_length=24)
