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


class BillItemDetailResponse(BaseModel):
    """Response schema for bill detail items."""

    id: str
    bill_id: str
    case_id: str | None = None
    draft_id: str | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    fee_type: str | None = None
    year_no: int | None = None
    description: str
    quantity: Decimal = Field(Decimal("1"), ge=0)
    unit_price: Decimal = Field(Decimal("0"), ge=0)
    amount: Decimal = Field(Decimal("0"), ge=0)


class BillDetailResponse(BaseModel):
    """Enriched bill detail response schema."""

    id: str
    bill_no: str | None = None
    client_id: str
    client_name: str | None = None
    case_id: str | None = None
    case_no: str | None = None
    currency: str
    direction: str
    status: str
    total_gov: Decimal = Field(Decimal("0"), ge=0)
    total_service: Decimal = Field(Decimal("0"), ge=0)
    total_misc: Decimal = Field(Decimal("0"), ge=0)
    amount: Decimal = Field(Decimal("0"), ge=0)
    balance: Decimal = Field(Decimal("0"), ge=0)
    bill_date: date | None = None
    due_date: date | None = None
    items: list[BillItemDetailResponse] = []
    source_draft_ids: list[str] = []
    source_draft_labels: list[str] = []
    primary_draft_id: str | None = None
    primary_draft_label: str | None = None


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
    fee_type: str | None = None
    currency: str
    receivable_amt: Decimal
    received_amt: Decimal
    last_receipt_date: date | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    year_no: int | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = None
    remark: str | None = None
    bills: list["CaseReceiptBillResponse"] = []


class CaseReceiptBillResponse(BaseModel):
    """Bill overview row under case receipt summary."""

    id: str
    bill_no: str | None = None
    status: str
    amount: Decimal = Field(Decimal("0"), ge=0)
    balance: Decimal = Field(Decimal("0"), ge=0)
    issue_date: date | None = None


class CaseReceiptCreate(BaseModel):
    """Schema for creating a case receipt manually."""

    case_id: str = Field(..., min_length=1)
    fee_type: str | None = Field(None, max_length=16)
    fee_code: str | None = Field(None, max_length=64)
    fee_name: str | None = Field(None, max_length=128)
    year_no: int | None = None
    currency: str = Field("CNY", max_length=8)
    receivable_amt: Decimal = Field(..., ge=0)
    received_amt: Decimal = Field(..., ge=0)
    last_receipt_date: date | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = Field(None, max_length=64)
    remark: str | None = Field(None, max_length=512)


class CaseReceiptUpdate(BaseModel):
    """Schema for updating a case receipt (partial)."""

    fee_type: str | None = Field(None, max_length=16)
    fee_code: str | None = Field(None, max_length=64)
    fee_name: str | None = Field(None, max_length=128)
    year_no: int | None = None
    currency: str | None = Field(None, max_length=8)
    receivable_amt: Decimal | None = Field(None, ge=0)
    received_amt: Decimal | None = Field(None, ge=0)
    last_receipt_date: date | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = Field(None, max_length=64)
    remark: str | None = Field(None, max_length=512)


class CaseReceiptListItem(BaseModel):
    """List item for cross-case receipt query."""

    id: str
    case_id: str
    case_no: str | None = None
    client_name: str | None = None
    fee_type: str | None = None
    currency: str
    receivable_amt: Decimal
    received_amt: Decimal
    last_receipt_date: date | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    year_no: int | None = None
    due_date: date | None = None
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    invoice_no: str | None = None
    remark: str | None = None


class BillManualItemSchema(BaseModel):
    description: str = Field(..., max_length=256)
    quantity: int = Field(1, gt=0)
    unit_price: Decimal = Field(..., ge=0)
    fee_type: str | None = Field(None, max_length=16)
    year_no: int | None = None


class BillManualCreateSchema(BaseModel):
    client_id: str = Field(..., min_length=1)
    case_id: str | None = Field(None, min_length=1)
    currency: str = Field("CNY", max_length=8)
    direction: str = Field("AR", pattern="^(AR|AP)$")
    status: str = Field("UNSETTLED", max_length=24)
    bill_date: date | None = None
    due_date: date | None = None
    items: list[BillManualItemSchema] = Field(..., min_length=1)
    notes: str | None = Field(None, max_length=512)


class BillStatusSchema(BaseModel):
    """Schema for bill status transitions."""

    status: str = Field(..., max_length=24)
