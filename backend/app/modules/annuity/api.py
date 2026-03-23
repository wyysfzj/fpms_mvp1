from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.db.session import get_db
from app.modules.annuity.service import (
    create_historical_pay_list,
    create_pay_list_from_fee_items,
    generate_fee_drafts_from_annuity_tasks,
    list_annuity_tasks,
    register_gov_payment,
    update_annuity_task_instruction,
)
from app.modules.auth.models import T_User

router = APIRouter()


class AnnuityInstructionUpdateIn(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=24)
    instruction_date: date | None = None


class AnnuityGenerateDraftsIn(BaseModel):
    task_ids: list[int] = Field(..., min_length=1)
    pay_next_year: bool = False
    currency: str = Field(default="CNY", min_length=1, max_length=8)


class PayListFromFeeItemsIn(BaseModel):
    fee_item_ids: list[str] = Field(..., min_length=1)
    planned_pay_date: date | None = None
    remark: str | None = None


class HistoricalPayListCreateIn(BaseModel):
    client_id: str | None = Field(default=None, max_length=36)
    currency: str = Field(default="CNY", min_length=1, max_length=8)
    planned_pay_date: date | None = None
    remark: str | None = None


class GovPaymentCreateIn(BaseModel):
    pay_list_id: int
    fee_item_id: str = Field(..., min_length=1, max_length=36)
    paid_date: date | None = None
    paid_amount: Decimal | None = Field(default=None, gt=0)
    official_receipt_no: str | None = Field(default=None, max_length=64)
    remark: str | None = None


@router.get("/annuity/tasks", summary="List annuity tasks")
def get_annuity_tasks(
    due_from: date | None = Query(default=None),
    due_to: date | None = Query(default=None),
    status: str | None = Query(default=None),
    pending_mode: str | None = Query(default=None),
    case_id: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
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
        "status": status,
        "pending_mode": pending_mode,
        "case_id": case_id,
        "client_id": client_id,
        "notice_status": notice_status,
    }
    tasks, total = list_annuity_tasks(db, filters=filters, page=page, page_size=page_size)

    items = [
        {
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
        for task in tasks
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


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


@router.post("/pay-lists/from-fee-items", summary="Create pay list from fee items")
def post_pay_list_from_fee_items(
    payload: PayListFromFeeItemsIn,
    _perm: None = Depends(require_perm("PayList.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return create_pay_list_from_fee_items(
        db,
        fee_item_ids=payload.fee_item_ids,
        planned_pay_date=payload.planned_pay_date,
        remark=payload.remark,
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
    )
