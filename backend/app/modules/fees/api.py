from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.fees.models import FeeDraft, FeeItem, FeeRate

router = APIRouter()


@router.get("/fees/drafts")
def get_fee_drafts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Fee.Draft.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(FeeDraft)
    total = query.count()
    drafts = (
        query.order_by(FeeDraft.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [
        {
            "id": draft.id,
            "case_id": draft.case_id,
            "client_id": draft.client_id,
            "draft_type": draft.draft_type,
        }
        for draft in drafts
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/fees/drafts", status_code=status.HTTP_201_CREATED)
def create_fee_draft(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Fee.Draft.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    case_id = payload.get("case_id")
    if not case_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="case_id is required")

    draft = FeeDraft(
        id=str(uuid4()),
        case_id=case_id,
        client_id=payload.get("client_id"),
        draft_type=payload.get("draft_type") or "GENERIC",
        currency=payload.get("currency") or "CNY",
        status=payload.get("status") or "OPEN",
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)

    return {
        "id": draft.id,
        "case_id": draft.case_id,
        "client_id": draft.client_id,
        "draft_type": draft.draft_type,
        "currency": draft.currency,
        "status": draft.status,
    }


@router.post("/fees/drafts/{draft_id}/lock")
def lock_fee_draft(
    draft_id: str,
    _perm: None = Depends(require_perm("Fee.Draft.Action")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    draft = db.query(FeeDraft).filter(FeeDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee draft not found")

    draft.status = "LOCKED"
    db.commit()

    return {"status": "ok"}


@router.post("/fees/drafts/{draft_id}/unlock")
def unlock_fee_draft(
    draft_id: str,
    _perm: None = Depends(require_perm("Fee.Draft.Action")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    draft = db.query(FeeDraft).filter(FeeDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee draft not found")

    draft.status = "OPEN"
    db.commit()

    return {"status": "ok"}


@router.post("/fees/drafts/{draft_id}/items", status_code=status.HTTP_201_CREATED)
def create_fee_item(
    draft_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Fee.Item.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    draft = db.query(FeeDraft).filter(FeeDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee draft not found")

    item = FeeItem(
        id=str(uuid4()),
        draft_id=draft_id,
        case_id=payload.get("case_id"),
        rate_id=payload.get("rate_id"),
        fee_code=payload.get("fee_code"),
        fee_name=payload.get("fee_name"),
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "draft_id": item.draft_id,
        "case_id": item.case_id,
        "rate_id": item.rate_id,
        "fee_code": item.fee_code,
        "fee_name": item.fee_name,
    }


@router.put("/fees/items/{item_id}")
def update_fee_item(
    item_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Fee.Item.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    item = db.query(FeeItem).filter(FeeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee item not found")

    if "draft_id" in payload:
        item.draft_id = payload.get("draft_id")
    if "case_id" in payload:
        item.case_id = payload.get("case_id")
    if "rate_id" in payload:
        item.rate_id = payload.get("rate_id")
    if "fee_code" in payload:
        item.fee_code = payload.get("fee_code")
    if "fee_name" in payload:
        item.fee_name = payload.get("fee_name")

    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "draft_id": item.draft_id,
        "case_id": item.case_id,
        "rate_id": item.rate_id,
        "fee_code": item.fee_code,
        "fee_name": item.fee_name,
    }


@router.delete("/fees/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee_item(
    item_id: str,
    _perm: None = Depends(require_perm("Fee.Item.Delete")),
    db: Session = Depends(get_db),
) -> Response:
    item = db.query(FeeItem).filter(FeeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee item not found")

    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/fees/drafts/{draft_id}")
def get_fee_draft(
    draft_id: str,
    _perm: None = Depends(require_perm("Fee.Draft.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    draft = db.query(FeeDraft).filter(FeeDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee draft not found")

    return {
        "id": draft.id,
        "case_id": draft.case_id,
        "client_id": draft.client_id,
        "draft_type": draft.draft_type,
        "currency": draft.currency,
        "status": draft.status,
    }


@router.put("/fees/drafts/{draft_id}")
def update_fee_draft(
    draft_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Fee.Draft.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    draft = db.query(FeeDraft).filter(FeeDraft.id == draft_id).first()
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee draft not found")

    if "case_id" in payload:
        draft.case_id = payload.get("case_id")
    if "client_id" in payload:
        draft.client_id = payload.get("client_id")
    if "draft_type" in payload:
        draft.draft_type = payload.get("draft_type") or draft.draft_type
    if "currency" in payload:
        draft.currency = payload.get("currency") or draft.currency
    if "status" in payload:
        draft.status = payload.get("status") or draft.status

    db.commit()
    db.refresh(draft)

    return {
        "id": draft.id,
        "case_id": draft.case_id,
        "client_id": draft.client_id,
        "draft_type": draft.draft_type,
        "currency": draft.currency,
        "status": draft.status,
    }


@router.get("/fees/rates")
def get_fee_rates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Fee.Rate.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(FeeRate)
    total = query.count()
    rates = query.order_by(FeeRate.fee_code).offset((page - 1) * page_size).limit(page_size).all()
    items = [
        {
            "id": rate.id,
            "fee_code": rate.fee_code,
            "fee_name": rate.fee_name,
            "fee_type": rate.fee_type,
        }
        for rate in rates
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/fees/rates", status_code=status.HTTP_201_CREATED)
def create_fee_rate(
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Fee.Rate.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    fee_code = payload.get("fee_code")
    if not fee_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="fee_code is required")

    rate = FeeRate(
        id=str(uuid4()),
        fee_code=fee_code,
        fee_name=payload.get("fee_name"),
        fee_type=payload.get("fee_type") or "SERVICE",
        currency=payload.get("currency") or "CNY",
        default_amount=payload.get("default_amount"),
    )
    db.add(rate)
    db.commit()
    db.refresh(rate)

    return {
        "id": rate.id,
        "fee_code": rate.fee_code,
        "fee_name": rate.fee_name,
        "fee_type": rate.fee_type,
        "currency": rate.currency,
        "default_amount": rate.default_amount,
    }


@router.put("/fees/rates/{rate_id}")
def update_fee_rate(
    rate_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Fee.Rate.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rate = db.query(FeeRate).filter(FeeRate.id == rate_id).first()
    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee rate not found")

    if "fee_code" in payload:
        rate.fee_code = payload.get("fee_code") or rate.fee_code
    if "fee_name" in payload:
        rate.fee_name = payload.get("fee_name")
    if "fee_type" in payload:
        rate.fee_type = payload.get("fee_type") or rate.fee_type
    if "currency" in payload:
        rate.currency = payload.get("currency") or rate.currency
    if "default_amount" in payload:
        rate.default_amount = payload.get("default_amount")

    db.commit()
    db.refresh(rate)

    return {
        "id": rate.id,
        "fee_code": rate.fee_code,
        "fee_name": rate.fee_name,
        "fee_type": rate.fee_type,
        "currency": rate.currency,
        "default_amount": rate.default_amount,
    }
