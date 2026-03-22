from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.collections.models import Dunning
from app.modules.collections.service import (
    generate_dunning_batches,
    get_dunning_detail,
    mark_bill_bad_debt,
    restore_bill_from_bad_debt,
)

router = APIRouter()


class DunningGenerateIn(BaseModel):
    to_date: date
    client_id: str | None = None
    client_ids: list[str] | None = None
    include_statuses: list[str] | None = None
    exclude_statuses: list[str] | None = None
    strict_conflict: bool = False


@router.get("/dunning", summary="List dunning batches")
def get_dunning(
    round_no: int | None = Query(default=None),
    status: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _perm: None = Depends(require_perm("Dunning.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(Dunning)

    if round_no is not None:
        stmt = stmt.where(Dunning.round_no == round_no)
    if status:
        stmt = stmt.where(Dunning.status == status)
    if client_id:
        stmt = stmt.where(Dunning.client_id == client_id)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    offset = (page - 1) * page_size
    items = (
        db.execute(
            stmt.order_by(Dunning.created_at.desc(), Dunning.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    return {
        "items": [
            {
                "id": item.id,
                "dunning_no": item.dunning_no,
                "client_id": item.client_id,
                "round_no": item.round_no,
                "to_date": item.to_date,
                "currency": item.currency,
                "total_amount": item.total_amount,
                "status": item.status,
                "sent_date": item.sent_date,
                "remark": item.remark,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in items
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.post("/dunning", summary="Generate dunning batches")
def post_dunning(
    payload: DunningGenerateIn,
    _perm: None = Depends(require_perm("Dunning.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return generate_dunning_batches(
        db,
        to_date=payload.to_date,
        client_id=payload.client_id,
        client_ids=payload.client_ids,
        include_statuses=payload.include_statuses,
        exclude_statuses=payload.exclude_statuses,
        strict_conflict=payload.strict_conflict,
    )


@router.get("/dunning/{dunning_id}", summary="Get dunning batch detail")
def get_dunning_batch_detail(
    dunning_id: int,
    _perm: None = Depends(require_perm("Dunning.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return get_dunning_detail(db, dunning_id=dunning_id)


@router.post("/bills/{bill_id}/bad-debt", summary="Mark bill as bad debt")
def post_bill_bad_debt(
    bill_id: str,
    _perm: None = Depends(require_perm("BadDebt.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    bill = mark_bill_bad_debt(db, bill_id=bill_id)
    return {
        "id": bill.id,
        "bill_no": bill.bill_no,
        "client_id": bill.client_id,
        "currency": bill.currency,
        "status": bill.status,
        "bill_date": bill.bill_date,
        "due_date": bill.due_date,
        "amount": bill.amount,
        "balance": bill.balance,
        "updated_at": bill.updated_at,
    }


@router.post("/bills/{bill_id}/bad-debt/restore", summary="Restore bill from bad debt")
def post_bill_bad_debt_restore(
    bill_id: str,
    _perm: None = Depends(require_perm("BadDebt.Action")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    bill = restore_bill_from_bad_debt(db, bill_id=bill_id)
    return {
        "id": bill.id,
        "bill_no": bill.bill_no,
        "client_id": bill.client_id,
        "currency": bill.currency,
        "status": bill.status,
        "bill_date": bill.bill_date,
        "due_date": bill.due_date,
        "amount": bill.amount,
        "balance": bill.balance,
        "updated_at": bill.updated_at,
    }
