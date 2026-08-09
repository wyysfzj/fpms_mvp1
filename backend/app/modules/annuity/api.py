from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.core.errors import raise_business_error
from app.db.session import get_db
from app.modules.annuity.models import PayList
from app.modules.annuity.schemas import AnnuityTaskListResponse
from app.modules.annuity.service import (
    ExportInternalPayListCommand,
    add_manual_gov_payment,
    compensate_internal_pay_list_export,
    create_historical_pay_list,
    create_pay_list_from_fee_items,
    export_internal_pay_list,
    generate_fee_drafts_from_annuity_tasks,
    get_pay_list_detail,
    list_annuity_tasks_report,
    list_pay_lists,
    mark_pay_list_paid,
    register_gov_payment,
    update_annuity_task_instruction,
)
from app.modules.auth.models import T_User
from app.modules.cases.models import Case

router = APIRouter()

_ANNUITY_TRIGGER_RULE = "年费节点到期"
_ANNUITY_DEADLINE_RULE = (
    "以年费任务到期日为准；滞纳金按每超过规定缴费时间 1 个月加收当年全额年费 5% 提示"
)
_ANNUITY_FEE_NODE_EXPLANATION = (
    "年费费用节点：客户指示缴费后生成官费草单，进入官费清单并登记官方缴费回执。"
)


class AnnuityInstructionUpdateIn(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=24)
    instruction_date: date | None = None


class AnnuityGenerateDraftsIn(BaseModel):
    task_ids: list[int] = Field(..., min_length=1)
    pay_next_year: bool = False
    currency: str = Field(default="CNY", min_length=1, max_length=8)


class AnnuityTaskGenerateIn(BaseModel):
    case_id: str = Field(..., min_length=1)


class PayListFromFeeItemsIn(BaseModel):
    fee_item_ids: list[str] = Field(..., min_length=1)
    planned_pay_date: date | None = None
    remark: str | None = None


class HistoricalPayListCreateIn(BaseModel):
    client_id: str | None = Field(default=None, max_length=36)
    currency: str = Field(default="CNY", min_length=1, max_length=8)
    planned_pay_date: date | None = None
    remark: str | None = None
    list_type: str | None = Field(default=None, max_length=32)
    flow_dir: str | None = Field(default=None, max_length=32)
    invoice_no_from: str | None = Field(default=None, max_length=64)
    invoice_no_to: str | None = Field(default=None, max_length=64)


class GovPaymentCreateIn(BaseModel):
    pay_list_id: int
    fee_item_id: str = Field(..., min_length=1, max_length=36)
    paid_date: date | None = None
    paid_amount: Decimal | None = None
    official_receipt_no: str | None = Field(default=None, max_length=64)
    remark: str | None = None
    paid_currency: str | None = Field(default=None, max_length=8)
    voucher_no: str | None = Field(default=None, max_length=64)
    invoice_no: str | None = Field(default=None, max_length=64)


class ManualGovPaymentCreateIn(BaseModel):
    case_id: str = Field(..., min_length=1, max_length=36)
    fee_item_id: str | None = Field(default=None, max_length=36)
    paid_date: date
    paid_amount: Decimal = Field(..., gt=0)
    official_receipt_no: str | None = Field(default=None, max_length=64)
    remark: str | None = None
    fee_code: str | None = Field(default=None, max_length=64)
    year_no: int | None = Field(default=None, ge=1)
    paid_currency: str | None = Field(default=None, max_length=8)
    voucher_no: str | None = Field(default=None, max_length=64)
    invoice_no: str | None = Field(default=None, max_length=64)


class PayListMarkPaidIn(BaseModel):
    paid_date: date


def _annuity_deadline_preview_fields(year_no: int) -> dict[str, str]:
    return {
        "trigger_rule": _ANNUITY_TRIGGER_RULE,
        "deadline_rule": _ANNUITY_DEADLINE_RULE,
        "fee_basis": f"第{year_no}年度年费，按专利类型和年度阶梯费率预估",
        "fee_node_explanation": _ANNUITY_FEE_NODE_EXPLANATION,
    }


@router.get("/annuity/tasks", response_model=AnnuityTaskListResponse, summary="List annuity tasks")
def get_annuity_tasks(
    due_from: date | None = Query(default=None),
    due_to: date | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    status: str | None = Query(default=None),
    task_status: str | None = Query(default=None),
    pending_mode: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    country: str | None = Query(default=None),
    annuity_year: int | None = Query(default=None, ge=1),
    payment_status: str | None = Query(default=None),
    notice_status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("AnnuityTask.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List annuity tasks with filters and pagination."""
    filters = {
        "due_from": due_from,
        "due_to": due_to,
        "date_from": date_from,
        "date_to": date_to,
        "status": status,
        "task_status": task_status,
        "pending_mode": pending_mode,
        "case_id": case_id,
        "case_no": case_no,
        "client_id": client_id,
        "country": country,
        "annuity_year": annuity_year,
        "payment_status": payment_status,
        "notice_status": notice_status,
    }
    tasks, total, summary = list_annuity_tasks_report(
        db, filters=filters, page=page, page_size=page_size
    )
    case_no_map: dict[str, str] = {}
    case_ids = sorted({task.case_id for task in tasks})
    if case_ids:
        cases = db.query(Case.id, Case.case_no).filter(Case.id.in_(case_ids)).all()
        case_no_map = {case.id: case.case_no for case in cases}

    items = [
        {
            "id": task.id,
            "case_id": task.case_id,
            "case_no": case_no_map.get(task.case_id),
            "client_id": task.client_id,
            "year_no": task.year_no,
            "due_date": task.due_date,
            "client_instruction": task.client_instruction,
            "instruction_date": task.instruction_date,
            "notice_status": task.notice_status,
            "notice_sent_date": task.notice_sent_date,
            "status": task.status,
            "remark": task.remark,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "gov_fee_amt": task.gov_fee_amt,
            "service_fee_amt": task.service_fee_amt,
            "notify_count": task.notify_count,
            "pay_next_year": task.pay_next_year,
            "draft_generated": task.draft_generated,
            "notice_sent": task.notice_sent,
            "is_overdue": task.due_date < date.today() and task.status == "OPEN",
            **_annuity_deadline_preview_fields(task.year_no),
        }
        for task in tasks
    ]
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "summary": summary,
    }


@router.put("/annuity/tasks/{task_id}/instruction", summary="Update annuity task instruction")
def put_annuity_task_instruction(
    task_id: int,
    payload: AnnuityInstructionUpdateIn,
    _perm: None = Depends(require_perm("AnnuityTask.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    task = update_annuity_task_instruction(
        db,
        task_id=task_id,
        instruction=payload.instruction,
        instruction_date=payload.instruction_date,
    )
    return {
        "id": task.id,
        "case_id": task.case_id,
        "client_id": task.client_id,
        "year_no": task.year_no,
        "due_date": task.due_date,
        "client_instruction": task.client_instruction,
        "instruction_date": task.instruction_date,
        "notice_status": task.notice_status,
        "notice_sent_date": task.notice_sent_date,
        "status": task.status,
        "remark": task.remark,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.post("/annuity/tasks/generate-drafts", summary="Generate fee drafts from annuity tasks")
def post_annuity_generate_drafts(
    payload: AnnuityGenerateDraftsIn,
    _perm: None = Depends(require_perm("AnnuityTask.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return generate_fee_drafts_from_annuity_tasks(
        db,
        task_ids=payload.task_ids,
        pay_next_year=payload.pay_next_year,
        currency=payload.currency,
    )


@router.post(
    "/annuity/tasks/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate annuity tasks for a case",
)
def generate_annuity_tasks_endpoint(
    payload: AnnuityTaskGenerateIn,
    _perm: None = Depends(require_perm("AnnuityTask.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Generate multi-year annuity tasks for a GRANTED case.

    **Auth**: Bearer JWT
    **Permission**: AnnuityTask.Action
    """
    from app.modules.annuity.service import generate_annuity_tasks_for_case

    result = generate_annuity_tasks_for_case(db, case_id=payload.case_id)
    db.commit()
    return result


@router.post("/pay-lists/from-fee-items", summary="Create pay list from fee items")
def post_pay_list_from_fee_items(
    payload: PayListFromFeeItemsIn,
    _perm: None = Depends(require_perm("PayList.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        result = create_pay_list_from_fee_items(
            db,
            fee_item_ids=payload.fee_item_ids,
            planned_pay_date=payload.planned_pay_date,
            remark=payload.remark,
            actor_id=current_user.id,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result


@router.get("/pay-lists", summary="List pay lists")
def get_pay_lists(
    pay_list_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    planned_pay_date_from: date | None = Query(default=None),
    planned_pay_date_to: date | None = Query(default=None),
    currency: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    list_type: str | None = Query(default=None),
    flow_dir: str | None = Query(default=None),
    fee_code: str | None = Query(default=None),
    voucher_no: str | None = Query(default=None),
    invoice_no: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("PayList.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List pay-list headers with supported read-only filters and pagination."""
    filters = {
        "pay_list_no": pay_list_no,
        "client_id": client_id,
        "status": status,
        "planned_pay_date_from": planned_pay_date_from,
        "planned_pay_date_to": planned_pay_date_to,
        "currency": currency,
        "case_no": case_no,
        "app_no": app_no,
        "list_type": list_type,
        "flow_dir": flow_dir,
        "fee_code": fee_code,
        "voucher_no": voucher_no,
        "invoice_no": invoice_no,
    }
    pay_lists, total = list_pay_lists(db, filters=filters, page=page, page_size=page_size)

    client_ids = {pay_list.client_id for pay_list in pay_lists if pay_list.client_id}
    client_name_map: dict[str, str] = {}
    if client_ids:
        from app.modules.masterdata.clients.models import Client

        clients = db.query(Client.id, Client.name_cn).filter(Client.id.in_(client_ids)).all()
        client_name_map = {client.id: client.name_cn for client in clients}

    items = [
        {
            "id": pay_list.id,
            "pay_list_no": pay_list.pay_list_no,
            "client_id": pay_list.client_id,
            "client_name": client_name_map.get(pay_list.client_id),
            "status": pay_list.status,
            "currency": pay_list.currency,
            "planned_pay_date": pay_list.planned_pay_date,
            "paid_date": pay_list.paid_date,
            "total_amount": str(pay_list.total_amount),
            "remark": pay_list.remark,
            "list_type": pay_list.list_type,
            "flow_dir": pay_list.flow_dir,
            "invoice_no_from": pay_list.invoice_no_from,
            "invoice_no_to": pay_list.invoice_no_to,
            "created_at": pay_list.created_at,
            "updated_at": pay_list.updated_at,
            "created_by": pay_list.created_by,
            "updated_by": pay_list.updated_by,
        }
        for pay_list in pay_lists
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.get("/pay-lists/{pay_list_id}", summary="Get pay list detail")
def get_pay_list(
    pay_list_id: int,
    _perm: None = Depends(require_perm("PayList.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return get_pay_list_detail(db, pay_list_id=pay_list_id)


@router.post(
    "/pay-lists/{pay_list_id}/export",
    summary="Export pay list to Excel",
    response_class=Response,
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}},
            "description": "Excel export generated",
        }
    },
)
def post_pay_list_export(
    pay_list_id: int,
    _perm: None = Depends(require_perm("PayList.Export")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> Response:
    pay_list = db.get(PayList, pay_list_id)
    if pay_list is None:
        raise_business_error("PAY_LIST_NOT_FOUND", "Pay list not found", status_code=404)
    if (pay_list.status or "").strip().upper() != "DRAFT":
        raise_business_error(
            "PAY_LIST_STATE_CONFLICT",
            "Pay list can only be exported from DRAFT status",
            details={"status": pay_list.status},
            status_code=409,
        )

    export_result = None
    try:
        export_result = export_internal_pay_list(
            ExportInternalPayListCommand(
                pay_list_id=pay_list_id,
                actor_id=current_user.id,
                idempotency_key=f"pay-list-internal-export:http-v1:{pay_list_id}",
            ),
            db,
        )
        db.commit()
    except Exception:
        db.rollback()
        if export_result is not None and not export_result.reused:
            compensate_internal_pay_list_export(export_result.managed_storage_path)
        raise
    return Response(
        content=export_result.content,
        media_type=export_result.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{export_result.filename}"',
        },
    )


@router.post("/pay-lists/{pay_list_id}/mark-paid", summary="Mark pay list paid")
def post_pay_list_mark_paid(
    pay_list_id: int,
    payload: PayListMarkPaidIn,
    _perm: None = Depends(require_perm("Billing.Edit")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return mark_pay_list_paid(
        db,
        pay_list_id=pay_list_id,
        paid_date=payload.paid_date,
        actor_id=current_user.id,
    )


@router.post(
    "/pay-lists",
    status_code=status.HTTP_201_CREATED,
    summary="Create historical pay list",
)
def post_pay_lists(
    payload: HistoricalPayListCreateIn,
    _perm: None = Depends(require_perm("PayList.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return create_historical_pay_list(
        db,
        client_id=payload.client_id,
        currency=payload.currency,
        planned_pay_date=payload.planned_pay_date,
        remark=payload.remark,
        list_type=payload.list_type,
        flow_dir=payload.flow_dir,
        invoice_no_from=payload.invoice_no_from,
        invoice_no_to=payload.invoice_no_to,
        actor_id=current_user.id,
    )


@router.post("/gov-payments", summary="Register official payment")
def post_gov_payments(
    payload: GovPaymentCreateIn,
    _perm: None = Depends(require_perm("GovPayment.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return register_gov_payment(
        db,
        pay_list_id=payload.pay_list_id,
        fee_item_id=payload.fee_item_id,
        paid_date=payload.paid_date,
        paid_amount=payload.paid_amount,
        official_receipt_no=payload.official_receipt_no,
        remark=payload.remark,
        paid_currency=payload.paid_currency,
        voucher_no=payload.voucher_no,
        invoice_no=payload.invoice_no,
    )


@router.post("/pay-lists/{pay_list_id}/manual-items", summary="Add manual gov payment item")
def post_pay_list_manual_items(
    pay_list_id: int,
    payload: ManualGovPaymentCreateIn,
    _perm: None = Depends(require_perm("GovPayment.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return add_manual_gov_payment(
        db,
        pay_list_id=pay_list_id,
        case_id=payload.case_id,
        fee_item_id=payload.fee_item_id,
        paid_date=payload.paid_date,
        paid_amount=payload.paid_amount,
        official_receipt_no=payload.official_receipt_no,
        remark=payload.remark,
        fee_code=payload.fee_code,
        year_no=payload.year_no,
        paid_currency=payload.paid_currency,
        voucher_no=payload.voucher_no,
        invoice_no=payload.invoice_no,
        actor_id=current_user.id,
    )
