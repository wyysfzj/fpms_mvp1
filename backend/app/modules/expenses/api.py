from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import current_user_dep, require_perm
from app.db.session import get_db
from app.modules.auth.models import T_User
from app.modules.expenses.service import create_expense, list_expenses

router = APIRouter()


class ExpenseCreateIn(BaseModel):
    case_id: str
    department_id: str | None = None
    worker_id: str | None = None
    category: str
    expense_date: date
    amount: Decimal
    client_id: str | None = None
    expense_no: str | None = None
    vendor_name: str | None = None
    currency: str | None = None
    tax_amount: Decimal | None = None
    remark: str | None = None


class ExpenseOut(BaseModel):
    id: int
    expense_no: str | None
    case_id: str | None
    department_id: str | None
    worker_id: str | None
    category: str
    expense_date: date | None
    amount: Decimal
    currency: str
    status: str
    remark: str | None
    created_at: datetime
    updated_at: datetime


@router.get(
    "/expenses",
    summary="List expenses",
)
def get_expenses(
    case_id: str | None = Query(default=None),
    department_id: str | None = Query(default=None),
    worker_id: str | None = Query(default=None),
    category: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    currency: str | None = Query(default=None),
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    include_stats: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Expense.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    items, total, stats = list_expenses(
        db,
        case_id=case_id,
        department_id=department_id,
        worker_id=worker_id,
        category=category,
        date_from=date_from,
        date_to=date_to,
        currency=currency,
        status=status,
        q=q,
        page=page,
        page_size=page_size,
        include_stats=include_stats,
    )

    response: dict[str, Any] = {
        "items": [
            {
                "id": expense.id,
                "expense_no": expense.expense_no,
                "case_id": expense.case_id,
                "department_id": expense.department_id,
                "worker_id": expense.worker_id,
                "category": expense.category,
                "expense_date": expense.expense_date,
                "amount": expense.amount,
                "currency": expense.currency,
                "status": expense.status,
                "remark": expense.remark,
                "created_at": expense.created_at,
                "updated_at": expense.updated_at,
            }
            for expense in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }
    if include_stats:
        response["stats"] = stats
    return response


@router.post(
    "/expenses",
    status_code=status.HTTP_201_CREATED,
    response_model=ExpenseOut,
    summary="Create expense",
)
def post_expense(
    payload: ExpenseCreateIn,
    _perm: None = Depends(require_perm("Expense.Create")),
    current_user: T_User = current_user_dep,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    expense = create_expense(
        db,
        case_id=payload.case_id,
        department_id=payload.department_id,
        worker_id=payload.worker_id,
        category=payload.category,
        expense_date=payload.expense_date,
        amount=payload.amount,
        client_id=payload.client_id,
        expense_no=payload.expense_no,
        vendor_name=payload.vendor_name,
        currency=payload.currency,
        tax_amount=payload.tax_amount,
        remark=payload.remark,
        actor_id=current_user.id,
    )
    return {
        "id": expense.id,
        "expense_no": expense.expense_no,
        "case_id": expense.case_id,
        "department_id": expense.department_id,
        "worker_id": expense.worker_id,
        "category": expense.category,
        "expense_date": expense.expense_date,
        "amount": expense.amount,
        "currency": expense.currency,
        "status": expense.status,
        "remark": expense.remark,
        "created_at": expense.created_at,
        "updated_at": expense.updated_at,
    }
