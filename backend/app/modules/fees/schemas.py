from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.modules.fees.enums import CalcMode, FeeDraftStatus, FeeType


class FeeDraftCreateIn(BaseModel):
    case_id: str
    client_id: str | None = None
    draft_type: str | None = None
    currency: str


class FeeDraftUpdateIn(BaseModel):
    draft_type: str | None = None
    currency: str | None = None


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
    created_at: datetime
    updated_at: datetime


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
    client_amounts: list["FeeDraftGroupedAmountResponse"] = []
    case_type_amounts: list["FeeDraftGroupedAmountResponse"] = []
    country_amounts: list["FeeDraftGroupedAmountResponse"] = []
    agent_service_amounts: list["FeeDraftAgentServiceAmountResponse"] = []


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
    case_id: str
    rate_id: str
    fee_code: str
    fee_name: str
    fee_type: FeeType
    year_no: int | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    amount: Decimal
    remark: str | None = None


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
    calc_mode: CalcMode | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None


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
    calc_mode: CalcMode | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None


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
    calc_mode: str | None = None
    calc_params: str | None = None
    allow_reduction: bool | None = None
    effective_from: date_type | None = None
    effective_to: date_type | None = None


class OkOut(BaseModel):
    status: str = "ok"
