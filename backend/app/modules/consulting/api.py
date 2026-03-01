from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.consulting.service import (
    create_consulting_case,
    generate_consulting_fee_draft,
)

router = APIRouter()


class ConsultingCaseCreateIn(BaseModel):
    case_no: str | None = None
    case_type: str | None = None
    client_id: str | None = None
    title_cn: str | None = None
    primary_agent_id: str | None = None
    recv_date: date | None = None


class ConsultingCaseOut(BaseModel):
    id: str
    case_no: str
    case_type: str
    status: str
    client_id: str | None
    title_cn: str | None
    primary_agent_id: str | None
    recv_date: date | None
    created_at: datetime


class ConsultingFeeDraftHourlyLineIn(BaseModel):
    fee_code: str
    fee_name: str
    hours: Decimal
    hourly_rate: Decimal
    remark: str | None = None
    trace_key: str | None = None


class ConsultingFeeDraftMiscLineIn(BaseModel):
    fee_code: str
    fee_name: str
    amount: Decimal
    remark: str | None = None
    trace_key: str | None = None


class ConsultingFeeDraftCreateIn(BaseModel):
    case_id: str
    mode: str
    currency: str | None = None
    fixed_fee: Decimal | None = None
    hourly_lines: list[ConsultingFeeDraftHourlyLineIn] | None = None
    misc_lines: list[ConsultingFeeDraftMiscLineIn] | None = None


class ConsultingFeeDraftTotalsOut(BaseModel):
    total_gov: Decimal
    total_service: Decimal
    total_misc: Decimal
    amount: Decimal


class ConsultingFeeDraftLineOut(BaseModel):
    item_id: str
    fee_code: str | None
    fee_name: str | None
    fee_type: str
    quantity: Decimal | None
    unit_price: Decimal | None
    amount: Decimal
    trace_key: str
    remark: str | None


class ConsultingFeeDraftOut(BaseModel):
    draft_id: str
    draft_type: str
    mode: str
    currency: str
    totals: ConsultingFeeDraftTotalsOut
    items: list[ConsultingFeeDraftLineOut]
    created_line_count: int


@router.post(
    "/consulting/cases",
    status_code=status.HTTP_201_CREATED,
    response_model=ConsultingCaseOut,
    summary="Create consulting/search case",
)
def post_consulting_case(
    payload: ConsultingCaseCreateIn,
    _perm: None = Depends(require_perm("ConsultingCase.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    case = create_consulting_case(
        db,
        case_no=payload.case_no,
        case_type=payload.case_type,
        client_id=payload.client_id,
        title_cn=payload.title_cn,
        primary_agent_id=payload.primary_agent_id,
        recv_date=payload.recv_date,
    )
    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "status": case.status,
        "client_id": case.client_id,
        "title_cn": case.title_cn,
        "primary_agent_id": case.primary_agent_id,
        "recv_date": case.recv_date,
        "created_at": case.created_at,
    }


@router.post(
    "/consulting/fee-drafts",
    status_code=status.HTTP_201_CREATED,
    response_model=ConsultingFeeDraftOut,
    summary="Generate consulting/search fee draft",
)
def post_consulting_fee_drafts(
    payload: ConsultingFeeDraftCreateIn,
    _perm: None = Depends(require_perm("ConsultingFeeDraft.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return generate_consulting_fee_draft(
        db,
        case_id=payload.case_id,
        mode=payload.mode,
        currency=payload.currency,
        fixed_fee=payload.fixed_fee,
        hourly_lines=[line.model_dump(exclude_none=True) for line in (payload.hourly_lines or [])],
        misc_lines=[line.model_dump(exclude_none=True) for line in (payload.misc_lines or [])],
    )
