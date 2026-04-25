from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.core.errors import raise_business_error
from app.db.session import get_db
from app.modules.cases.models import Case
from app.modules.commission.export_excel import (
    COMMISSION_REPORT_EXPORT_MIME_TYPE,
    build_commission_settlement_report_xlsx,
)
from app.modules.commission.models import Commission, CommissionRule, CommissionSettlement
from app.modules.commission.service import (
    create_commission_rule,
    create_commission_settlement,
    generate_commission_settlement_lines,
    get_commission_settlement_report,
    update_commission_rule,
)

router = APIRouter()


class CommissionRuleCreateIn(BaseModel):
    rule_name: str
    case_type: str | None = None
    fee_type: str | None = None
    flow_dir: str | None = None
    patent_category: str | None = None
    s1_rate: Decimal
    s2_rate: Decimal
    s1_fixed_amount: Decimal = Decimal("0")
    s2_fixed_amount: Decimal = Decimal("0")
    wait_pay: bool
    force_settle: bool
    enabled: bool = True
    effective_from: date | None = None
    effective_to: date | None = None
    remark: str | None = None


class CommissionRuleOut(BaseModel):
    id: int
    rule_name: str
    case_type: str | None
    fee_type: str | None
    flow_dir: str | None
    patent_category: str | None
    s1_rate: Decimal
    s2_rate: Decimal
    s1_fixed_amount: Decimal
    s2_fixed_amount: Decimal
    wait_pay: bool
    force_settle: bool
    enabled: bool
    effective_from: date | None
    effective_to: date | None
    remark: str | None
    created_at: datetime
    updated_at: datetime


class CommissionRuleUpdateIn(BaseModel):
    rule_name: str | None = None
    case_type: str | None = None
    fee_type: str | None = None
    flow_dir: str | None = None
    patent_category: str | None = None
    s1_rate: Decimal | None = None
    s2_rate: Decimal | None = None
    s1_fixed_amount: Decimal | None = None
    s2_fixed_amount: Decimal | None = None
    wait_pay: bool | None = None
    force_settle: bool | None = None
    enabled: bool | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    remark: str | None = None


class CommissionSettlementCreateIn(BaseModel):
    agent_id: str
    period_from: date | None = None
    period_to: date | None = None
    currency: str
    remark: str | None = None


class CommissionSettlementOut(BaseModel):
    id: int
    settlement_no: str | None
    agent_id: str | None
    status: str
    currency: str
    period_from: date | None
    period_to: date | None
    line_count: int
    total_amount: Decimal
    remark: str | None
    created_at: datetime
    updated_at: datetime


def _to_out(rule: Any) -> dict[str, Any]:
    return {
        "id": rule.id,
        "rule_name": rule.rule_name,
        "case_type": rule.case_type,
        "fee_type": rule.fee_type,
        "flow_dir": rule.flow_dir,
        "patent_category": rule.patent_category,
        "s1_rate": rule.s1_rate,
        "s2_rate": rule.s2_rate,
        "s1_fixed_amount": rule.s1_fixed_amount,
        "s2_fixed_amount": rule.s2_fixed_amount,
        "wait_pay": rule.wait_pay,
        "force_settle": rule.force_settle,
        "enabled": rule.enabled,
        "effective_from": rule.effective_from,
        "effective_to": rule.effective_to,
        "remark": rule.remark,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
    }


def _to_settlement_out(item: CommissionSettlement) -> dict[str, Any]:
    return {
        "id": item.id,
        "settlement_no": item.settlement_no,
        "agent_id": item.agent_id,
        "status": item.status,
        "currency": item.currency,
        "period_from": item.period_from,
        "period_to": item.period_to,
        "line_count": item.line_count,
        "total_amount": item.total_amount,
        "remark": item.remark,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def _to_commission_out(item: Commission, *, case_no: str | None = None) -> dict[str, Any]:
    return {
        "id": item.id,
        "case_id": item.case_id,
        "case_no": case_no,
        "agent_id": item.agent_id,
        "rule_id": item.rule_id,
        "fee_type": item.fee_type,
        "base_fee": item.base_fee,
        "s1_rate": item.s1_rate,
        "s1_amount": item.s1_amount,
        "s1_done": item.s1_done,
        "s2_rate": item.s2_rate,
        "s2_amount": item.s2_amount,
        "s2_done": item.s2_done,
        "wait_pay": item.wait_pay,
        "force_settle": item.force_settle,
        "status": item.status,
        "is_settleable": item.is_settleable,
        "settleable_date": item.settleable_date,
        "remark": item.remark,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


@router.get("/commission", summary="List commission records")
def get_commission(
    agent_id: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    status: str | None = Query(default=None),
    settleable_date_from: date | None = Query(default=None),
    settleable_date_to: date | None = Query(default=None),
    created_at_from: date | None = Query(default=None),
    created_at_to: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Commission.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if settleable_date_from and settleable_date_to and settleable_date_from > settleable_date_to:
        raise_business_error(
            "COMMISSION_FILTER_INVALID",
            "settleable_date_from must be less than or equal to settleable_date_to",
            status_code=400,
        )
    if created_at_from and created_at_to and created_at_from > created_at_to:
        raise_business_error(
            "COMMISSION_FILTER_INVALID",
            "created_at_from must be less than or equal to created_at_to",
            status_code=400,
        )

    stmt = select(Commission, Case.case_no).join(Case, Case.id == Commission.case_id)
    if agent_id:
        stmt = stmt.where(Commission.agent_id == agent_id.strip())
    if case_id:
        stmt = stmt.where(Commission.case_id == case_id.strip())
    if case_no:
        stmt = stmt.where(Case.case_no == case_no.strip())
    if status:
        stmt = stmt.where(Commission.status == status.strip())
    if settleable_date_from:
        stmt = stmt.where(Commission.settleable_date >= settleable_date_from)
    if settleable_date_to:
        stmt = stmt.where(Commission.settleable_date <= settleable_date_to)
    if created_at_from:
        stmt = stmt.where(Commission.created_at >= datetime.combine(created_at_from, time.min))
    if created_at_to:
        stmt = stmt.where(Commission.created_at <= datetime.combine(created_at_to, time.max))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    offset = (page - 1) * page_size
    items = db.execute(
        stmt.order_by(Commission.created_at.desc(), Commission.id.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    return {
        "items": [_to_commission_out(item, case_no=case_no_value) for item, case_no_value in items],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.post(
    "/commission/settlements",
    status_code=status.HTTP_201_CREATED,
    response_model=CommissionSettlementOut,
    summary="Create a commission settlement batch",
)
def post_commission_settlement(
    payload: CommissionSettlementCreateIn,
    _perm: None = Depends(require_perm("CommissionSettlement.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    settlement = create_commission_settlement(
        db,
        agent_id=payload.agent_id,
        period_from=payload.period_from,
        period_to=payload.period_to,
        currency=payload.currency,
        remark=payload.remark,
    )
    return _to_settlement_out(settlement)


@router.get(
    "/commission/reports/settlement",
    summary="Get commission settlement report",
)
def get_commission_reports_settlement(
    agent_id: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    settlement_status: str | None = Query(default=None),
    line_status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    time_field: str = Query(default="line_created_at"),
    _perm: None = Depends(require_perm("CommissionReport.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return get_commission_settlement_report(
        db,
        agent_id=agent_id,
        case_id=case_id,
        currency=currency,
        settlement_status=settlement_status,
        line_status=line_status,
        date_from=date_from,
        date_to=date_to,
        time_field=time_field,
    )


@router.get(
    "/commission/reports/settlement/export",
    summary="Export commission settlement report to Excel",
    response_class=Response,
    responses={
        200: {
            "content": {COMMISSION_REPORT_EXPORT_MIME_TYPE: {}},
            "description": "Commission settlement report Excel export generated",
        }
    },
)
def export_commission_reports_settlement(
    agent_id: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    settlement_status: str | None = Query(default=None),
    line_status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    time_field: str = Query(default="line_created_at"),
    _perm: None = Depends(require_perm("CommissionReport.Read")),
    db: Session = Depends(get_db),
) -> Response:
    report = get_commission_settlement_report(
        db,
        agent_id=agent_id,
        case_id=case_id,
        currency=currency,
        settlement_status=settlement_status,
        line_status=line_status,
        date_from=date_from,
        date_to=date_to,
        time_field=time_field,
    )
    content = build_commission_settlement_report_xlsx(report=report)
    return Response(
        content=content,
        media_type=COMMISSION_REPORT_EXPORT_MIME_TYPE,
        headers={"Content-Disposition": 'attachment; filename="commission-settlement-report.xlsx"'},
    )


@router.post(
    "/commission/settlements/{id}/generate-lines",
    summary="Generate settlement lines for a commission settlement batch",
)
def post_commission_settlement_generate_lines(
    id: int,
    _perm: None = Depends(require_perm("CommissionSettlement.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return generate_commission_settlement_lines(
        db,
        settlement_id=id,
    )


@router.get("/commission/rules", summary="List commission rules")
def get_commission_rules(
    enabled: bool | None = Query(default=None),
    case_type: str | None = Query(default=None),
    fee_type: str | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("CommissionRule.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(CommissionRule)

    if enabled is not None:
        stmt = stmt.where(CommissionRule.enabled == enabled)
    if case_type:
        stmt = stmt.where(CommissionRule.case_type == case_type.strip())
    if fee_type:
        stmt = stmt.where(CommissionRule.fee_type == fee_type.strip())
    if q:
        keyword = q.strip().lower()
        if keyword:
            like_pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    func.lower(CommissionRule.rule_name).like(like_pattern),
                    func.lower(func.coalesce(CommissionRule.remark, "")).like(like_pattern),
                )
            )

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    offset = (page - 1) * page_size
    items = (
        db.execute(
            stmt.order_by(CommissionRule.created_at.desc(), CommissionRule.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    return {
        "items": [_to_out(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.post(
    "/commission/rules",
    status_code=status.HTTP_201_CREATED,
    response_model=CommissionRuleOut,
    summary="Create a commission rule",
)
def post_commission_rule(
    payload: CommissionRuleCreateIn,
    _perm: None = Depends(require_perm("CommissionRule.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rule = create_commission_rule(
        db,
        rule_name=payload.rule_name,
        case_type=payload.case_type,
        fee_type=payload.fee_type,
        flow_dir=payload.flow_dir,
        patent_category=payload.patent_category,
        s1_rate=payload.s1_rate,
        s2_rate=payload.s2_rate,
        s1_fixed_amount=payload.s1_fixed_amount,
        s2_fixed_amount=payload.s2_fixed_amount,
        wait_pay=payload.wait_pay,
        force_settle=payload.force_settle,
        enabled=payload.enabled,
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        remark=payload.remark,
    )
    return _to_out(rule)


@router.put(
    "/commission/rules/{rule_id}",
    response_model=CommissionRuleOut,
    summary="Update a commission rule",
)
def put_commission_rule(
    rule_id: int,
    payload: CommissionRuleUpdateIn,
    _perm: None = Depends(require_perm("CommissionRule.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rule = update_commission_rule(
        db,
        rule_id=rule_id,
        patch=payload.model_dump(exclude_unset=True),
    )
    return _to_out(rule)
