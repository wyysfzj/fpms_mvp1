from __future__ import annotations

import re
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator

from app.modules.fees.enums import CalcMode, FeeDraftStatus, FeeType
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeEstimateStatus,
    FeeSourceStatus,
)

OFFICIAL_FEE_TEMPLATE_STATUSES = (
    "UNCONFIRMED",
    "NOT_APPLICABLE",
    "READY",
    "BLOCKED",
)


class FeeDraftCreateIn(BaseModel):
    case_id: str
    client_id: str | None = None
    draft_type: str | None = None
    currency: str


class FeeDraftUpdateIn(BaseModel):
    draft_type: str | None = None
    currency: str | None = None


class ApplyFeeDraftGenerateIn(BaseModel):
    case_id: str
    currency: str = "CNY"
    discount_rate: Decimal | None = None


class OfficialFeePreviewTriggerContextIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trigger: str
    source_document_id: str | None


class OfficialFeePreviewIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    trigger_context: OfficialFeePreviewTriggerContextIn
    currency: Literal["CNY"]
    rate_effective_on: date_type

    @field_validator("rate_effective_on", mode="before")
    @classmethod
    def validate_iso_calendar_date(cls, value: object) -> object:
        if isinstance(value, date_type) and not isinstance(value, datetime):
            return value
        if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            raise ValueError("rate_effective_on must be an ISO calendar date")
        return value


class FeeDraftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    case_no: str | None = None
    client_id: str | None = None
    client_name: str | None = None
    draft_type: str
    currency: str
    status: FeeDraftStatus
    total_gov: Decimal
    total_service: Decimal
    total_misc: Decimal
    amount: Decimal
    official_fee_reduction_note: str | None = None
    official_template_status: str | None = None
    official_template_version: str | None = None
    official_template_note: str | None = None
    created_at: datetime
    updated_at: datetime


class OfficialFeeChecklistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    fee_draft_id: str | None = None
    pay_list_id: int | None = None
    checklist_code: str
    checklist_label: str
    status: str
    required: bool = True
    blocker_reason: str | None = None
    sort_order: int | None = None


class FeeDraftListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    case_no: str | None = None
    client_id: str | None = None
    client_name: str | None = None
    currency: str
    status: FeeDraftStatus
    amount: Decimal


class FeeDraftReportSummaryResponse(BaseModel):
    total_draft_count: int = 0
    service_fee_amount: Decimal = Decimal("0")
    government_fee_amount: Decimal = Decimal("0")
    income_amount: Decimal = Decimal("0")
    billed_amount: Decimal = Decimal("0")
    received_amount: Decimal = Decimal("0")
    unpaid_balance_amount: Decimal = Decimal("0")
    partially_received_bill_count: int = 0
    client_amounts: list["FeeDraftGroupedAmountResponse"] = []
    case_type_amounts: list["FeeDraftGroupedAmountResponse"] = []
    country_amounts: list["FeeDraftGroupedAmountResponse"] = []
    agent_service_amounts: list["FeeDraftAgentServiceAmountResponse"] = []
    year_amounts: list["FeeDraftTrendAmountResponse"] = []
    month_amounts: list["FeeDraftTrendAmountResponse"] = []


class FeeDraftGroupedAmountResponse(BaseModel):
    key: str
    label: str
    draft_count: int = 0
    service_fee_amount: Decimal = Decimal("0")
    government_fee_amount: Decimal = Decimal("0")
    income_amount: Decimal = Decimal("0")


class FeeDraftAgentServiceAmountResponse(BaseModel):
    key: str
    label: str
    draft_count: int = 0
    service_fee_amount: Decimal = Decimal("0")


class FeeDraftTrendAmountResponse(BaseModel):
    key: str
    label: str
    draft_count: int = 0
    service_fee_amount: Decimal = Decimal("0")
    government_fee_amount: Decimal = Decimal("0")
    income_amount: Decimal = Decimal("0")
    draft_type_amounts: list[FeeDraftGroupedAmountResponse] = []


class FeeDraftReportListResponse(BaseModel):
    items: list[FeeDraftListItemOut]
    page: int
    page_size: int
    total: int
    summary: FeeDraftReportSummaryResponse


class FeeItemCreateIn(BaseModel):
    rate_id: str
    year_no: int | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    remark: str | None = None


class FeeItemUpdateIn(BaseModel):
    year_no: int | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    remark: str | None = None


class FeeItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    draft_id: str
    case_id: str | None = None
    rate_id: str | None = None
    fee_code: str | None = None
    fee_name: str | None = None
    fee_type: FeeType | None = None
    year_no: int | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal
    remark: str | None = None


class OfficialFeePreviewLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fee_code: str
    fee_name: str
    fee_year_key: int
    official_full_amount: Decimal | None
    reduction_ratio: Decimal
    payable_amount: Decimal
    source_amount: Decimal | None
    source_date: date_type | None
    difference_review_state: FeeDifferenceReviewState

    @field_serializer("official_full_amount", "payable_amount", "source_amount")
    def serialize_money(self, value: Decimal | None) -> str | None:
        return format(value, ".2f") if value is not None else None

    @field_serializer("reduction_ratio")
    def serialize_reduction_ratio(self, value: Decimal) -> str:
        return format(value, ".4f")


class OfficialFeePreviewSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rate_id: str | None
    source_document_id: str | None
    source_doc: str | None = None
    source_url: str | None
    source_policy: str | None
    source_version: str | None
    status: FeeSourceStatus


class OfficialFeePreviewCandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    line: OfficialFeePreviewLineOut
    source: OfficialFeePreviewSourceOut


class OfficialFeePreviewTriggerContextOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trigger: str
    source_document_id: str | None


class OfficialFeePreviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    estimate_status: FeeEstimateStatus
    trigger_context: OfficialFeePreviewTriggerContextOut
    currency: Literal["CNY"]
    candidates: list[OfficialFeePreviewCandidateOut]
    total_payable_amount: Decimal

    @field_serializer("total_payable_amount")
    def serialize_total_payable_amount(self, value: Decimal) -> str:
        return format(value, ".2f")


class FeeRateCreateIn(BaseModel):
    fee_code: str
    fee_name: str
    fee_type: FeeType
    currency: str
    default_amount: Decimal
    enabled: bool = True
    rate_group: str | None = None
    country_code: str | None = None
    case_type: str | None = None
    patent_category: str | None = None
    fee_domain: str | None = None
    fee_section: str | None = None
    fee_category: str | None = None
    fee_subtype: str | None = None
    reduction_scope: str | None = None
    calc_mode: CalcMode | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None
    source_doc: str | None = None
    source_url: str | None = None
    source_policy: str | None = None
    source_version: str | None = None
    source_status: str | None = None


class FeeRateUpdateIn(BaseModel):
    fee_name: str | None = None
    fee_type: FeeType | None = None
    currency: str | None = None
    default_amount: Decimal | None = None
    enabled: bool | None = None
    rate_group: str | None = None
    country_code: str | None = None
    case_type: str | None = None
    patent_category: str | None = None
    fee_domain: str | None = None
    fee_section: str | None = None
    fee_category: str | None = None
    fee_subtype: str | None = None
    reduction_scope: str | None = None
    calc_mode: CalcMode | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None
    source_doc: str | None = None
    source_url: str | None = None
    source_policy: str | None = None
    source_version: str | None = None
    source_status: str | None = None


class FeeRateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    fee_code: str
    fee_name: str
    fee_type: FeeType
    currency: str
    default_amount: Decimal | None = None
    enabled: bool
    rate_group: str | None = None
    country_code: str | None = None
    case_type: str | None = None
    patent_category: str | None = None
    fee_domain: str | None = None
    fee_section: str | None = None
    fee_category: str | None = None
    fee_subtype: str | None = None
    reduction_scope: str | None = None
    calc_mode: str | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None
    source_doc: str | None = None
    source_url: str | None = None
    source_policy: str | None = None
    source_version: str | None = None
    source_status: str | None = None


class OkOut(BaseModel):
    status: str = "ok"
