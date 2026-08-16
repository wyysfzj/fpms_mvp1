from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class BillListBadDebtSummaryResponse(BaseModel):
    """Summary fields for the bill list bad-debt report slice."""

    bad_debt_bill_count: int = 0
    bad_debt_amount: Decimal = Field(Decimal("0"), ge=0)
    total_recovered_amount: Decimal = Field(Decimal("0"), ge=0)
    remaining_bad_debt_balance: Decimal = Field(Decimal("0"), ge=0)


class BillListAgingBucketResponse(BaseModel):
    """Aggregated aging bucket row for the billing report."""

    bucket: str
    bill_count: int = 0
    amount: Decimal = Field(Decimal("0"), ge=0)


class BillListItemResponse(BaseModel):
    """Response schema for the billing report list rows."""

    id: str
    bill_no: str | None = None
    client_id: str
    client_name: str | None = None
    currency: str
    status: str
    amount: Decimal = Field(Decimal("0"), ge=0)
    balance: Decimal = Field(Decimal("0"), ge=0)
    bill_date: date | None = None
    due_date: date | None = None
    days_past_due: int | None = None
    aging_bucket: str = "CURRENT"
    is_overdue: bool = False
    is_bad_debt: bool = False


class BillListReportSummaryResponse(BaseModel):
    """Summary block for the first-round billing statistics report."""

    receivable_bill_count: int = 0
    receivable_amount: Decimal = Field(Decimal("0"), ge=0)
    overdue_bill_count: int = 0
    overdue_amount: Decimal = Field(Decimal("0"), ge=0)
    bad_debt_bill_count: int = 0
    bad_debt_amount: Decimal = Field(Decimal("0"), ge=0)
    total_recovered_amount: Decimal = Field(Decimal("0"), ge=0)
    remaining_bad_debt_balance: Decimal = Field(Decimal("0"), ge=0)
    aging_buckets: list[BillListAgingBucketResponse] = Field(default_factory=list)


class BillListResponse(BaseModel):
    """Response schema for the billing statistics list/report contract."""

    items: list[BillListItemResponse]
    page: int
    page_size: int
    total: int
    summary: BillListReportSummaryResponse
    bad_debt_bill_count: int = 0
    bad_debt_amount: Decimal = Field(Decimal("0"), ge=0)
    total_recovered_amount: Decimal = Field(Decimal("0"), ge=0)
    remaining_bad_debt_balance: Decimal = Field(Decimal("0"), ge=0)


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


class BillBadDebtRecoveryResponse(BaseModel):
    """Response schema for bad-debt recovery rows."""

    id: str
    voucher_id: str
    recovery_amount: Decimal = Field(Decimal("0"), ge=0)
    recovery_date: date | None = None
    remark: str | None = None


class BillBadDebtVoucherResponse(BaseModel):
    """Response schema for the bill-level bad-debt master voucher."""

    id: str
    bill_id: str
    status: str
    bad_debt_amount: Decimal = Field(Decimal("0"), ge=0)
    recovered_amount: Decimal = Field(Decimal("0"), ge=0)
    bad_debt_date: date | None = None
    remark: str | None = None


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
    bad_debt_status: str = "NONE"
    bad_debt_substatus: str | None = None
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
    bad_debt_voucher: BillBadDebtVoucherResponse | None = None
    bad_debt_recoveries: list[BillBadDebtRecoveryResponse] = []
    bad_debt_total_recovered: Decimal = Field(Decimal("0"), ge=0)
    bad_debt_remaining_amount: Decimal = Field(Decimal("0"), ge=0)


class DemoBillFromDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: str = Field(..., min_length=1, max_length=36)
    bill_no: str | None = Field(None, min_length=1, max_length=64)
    bill_date: date
    due_date: date | None = None
    idempotency_key: str = Field(..., min_length=1, max_length=96)

    @model_validator(mode="after")
    def validate_date_order(self) -> "DemoBillFromDraftRequest":
        if self.due_date is not None and self.due_date < self.bill_date:
            raise ValueError("due_date must not precede bill_date")
        return self


class DemoBillFromDraftResponse(BaseModel):
    bill: BillDetailResponse
    idempotency_key: str
    reused: bool


class PaymentSchema(BaseModel):
    """Schema for recording payments."""

    client_id: str | None = Field(None, min_length=1)
    bill_id: str | None = Field(None, min_length=1)
    amount: Decimal
    pay_no: str | None = Field(None, max_length=64)
    pay_date: date | None = None
    currency: str = Field("CNY", max_length=8)
    remark: str | None = None


class PaymentResponse(BaseModel):
    """Response schema for payments."""

    id: str
    pay_no: str | None
    bill_id: str | None = None
    client_id: str
    pay_date: date | None
    currency: str
    amount: Decimal


class PaymentListItemResponse(BaseModel):
    """Response schema for payment list items."""

    id: str
    pay_no: str | None
    bill_id: str | None = None
    bill_no: str | None = None
    client_id: str
    client_name: str | None = None
    pay_date: date | None
    currency: str
    amount: Decimal = Field(Decimal("0"), ge=0)
    line_count: int = 0
    allocated_amt: Decimal = Field(Decimal("0"), ge=0)
    unapplied_amt: Decimal = Field(Decimal("0"), ge=0)
    prepayment_status: str


class PaymentListResponse(BaseModel):
    """Response schema for payment list/report results."""

    items: list[PaymentListItemResponse]
    page: int
    page_size: int
    total: int
    prepayment_count: int = 0
    prepayment_total_amount: Decimal = Field(Decimal("0"), ge=0)
    allocated_total_amount: Decimal = Field(Decimal("0"), ge=0)
    remaining_prepayment_balance: Decimal = Field(Decimal("0"), ge=0)


class FeeUnifiedQueryItemResponse(BaseModel):
    """Response schema for the fee unified query projection."""

    record_type: Literal["PAYMENT", "RECEIPT"]
    record_id: str
    case_id: str | None = None
    biz_no: str | None = None
    party_name: str | None = None
    amount: Decimal = Field(Decimal("0"), ge=0)
    currency: str
    status: str
    biz_date: date | None = None
    remark: str | None = None


class FeeUnifiedQueryListResponse(BaseModel):
    """Response schema for the first-round fee unified query list."""

    items: list[FeeUnifiedQueryItemResponse]
    page: int
    page_size: int
    total: int


class FeeOverviewGovPaymentItemResponse(BaseModel):
    """Upper-pane row for the SPEC 5.11 GovPayment overview."""

    gov_payment_id: int
    pay_list_id: int
    case_id: str
    case_no: str | None = None
    app_no: str | None = None
    patent_no: str | None = None
    fee_item_id: str | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    year_no: int | None = None
    planned_amt: Decimal = Field(Decimal("0"), ge=0)
    paid_amt: Decimal = Field(Decimal("0"), ge=0)
    currency: str
    list_no: str | None = None
    voucher_no: str | None = None
    invoice_no: str | None = None
    planned_pay_date: date | None = None
    paid_date: date | None = None


class FeeOverviewGovPaymentListResponse(BaseModel):
    """Paginated upper-pane response for the SPEC 5.11 GovPayment overview."""

    items: list[FeeOverviewGovPaymentItemResponse]
    page: int
    page_size: int
    total: int


class FeeOverviewCaseReceiptItemResponse(BaseModel):
    """Lower-pane row for the SPEC 5.11 CaseReceipt overview."""

    receipt_id: str
    case_id: str
    case_no: str | None = None
    app_no: str | None = None
    patent_no: str | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    year_no: int | None = None
    fee_type: str | None = None
    receivable_amt: Decimal = Field(Decimal("0"), ge=0)
    received_amt: Decimal = Field(Decimal("0"), ge=0)
    currency: str
    is_arrears: bool | None = None
    is_prepayment: bool | None = None
    is_commissionable: bool | None = None
    receipt_date: date | None = None
    due_date: date | None = None
    invoice_no: str | None = None


class FeeOverviewCaseReceiptListResponse(BaseModel):
    """Paginated lower-pane response for the SPEC 5.11 CaseReceipt overview."""

    items: list[FeeOverviewCaseReceiptItemResponse]
    page: int
    page_size: int
    total: int


class OffsetCreateSchema(BaseModel):
    """Schema for creating offsets."""

    payment_line_id: str = Field(..., min_length=1)
    bill_id: str = Field(..., min_length=1)
    offset_amt: Decimal
    offset_date: date | None = None


class OffsetResponse(BaseModel):
    """Response schema for offsets."""

    id: str
    payment_line_id: str
    bill_id: str
    offset_amt: Decimal
    offset_date: date | None
    is_reversed: bool


class OffsetListItemResponse(BaseModel):
    """Enriched response schema for offset list items."""

    id: str
    payment_line_id: str
    bill_id: str
    bill_no: str | None = None
    offset_amt: Decimal
    offset_date: date | None = None
    is_reversed: bool
    reversed_at: str | None = None
    created_at: str | None = None


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
    unit_price: Decimal
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


class BillBadDebtActionSchema(BaseModel):
    """Schema for bill bad-debt write actions."""

    mode: Literal["MARK", "TRANSFER"] = "MARK"
    bad_debt_date: date | None = None
    remark: str | None = Field(None, max_length=512)


class BillBadDebtRecoveryActionSchema(BaseModel):
    """Schema for bill bad-debt recovery writes."""

    recovery_amount: Decimal = Field(..., gt=0)
    recovery_date: date | None = None
    remark: str | None = Field(None, max_length=512)
