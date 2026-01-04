from __future__ import annotations

from datetime import date
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.cases.models import Case
from app.modules.cases.schemas import CaseCreateIn

router = APIRouter()


@router.get("/cases")
def get_cases(
    q: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Case)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Case.case_no.ilike(pattern),
                Case.title_cn.ilike(pattern),
                Case.title_en.ilike(pattern),
                Case.app_no.ilike(pattern),
            )
        )
    if case_no:
        query = query.filter(Case.case_no == case_no)
    if app_no:
        query = query.filter(Case.app_no == app_no)
    if client_id:
        query = query.filter(Case.client_id == client_id)
    if status:
        query = query.filter(Case.status == status)
    if date_from:
        query = query.filter(Case.recv_date >= date_from)
    if date_to:
        query = query.filter(Case.recv_date <= date_to)

    total = query.count()

    sort_field = Case.case_no
    allowed_sort_fields = {
        "case_no": Case.case_no,
        "recv_date": Case.recv_date,
        "filing_date": Case.filing_date,
        "created_at": Case.created_at,
    }
    if sort_by in allowed_sort_fields:
        sort_field = allowed_sort_fields[sort_by]

    if sort_dir.lower() == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    cases = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [
        {
            "id": case.id,
            "case_no": case.case_no,
            "case_type": case.case_type,
            "patent_category": case.patent_category,
        }
        for case in cases
    ]

    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post("/cases", status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreateIn,
    _perm: None = Depends(require_perm("Case.Create")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    case_no = payload.case_no
    if not case_no:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="case_no is required")

    exists = db.query(Case).filter(Case.case_no == case_no).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="case_no already exists")

    case = Case(
        id=str(uuid4()),
        case_no=case_no,
        case_type=payload.case_type or "NORMAL",
        patent_category=payload.patent_category or "INV",
        flow_dir=payload.flow_dir or "CN_DOMESTIC",
        client_id=payload.client_id,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "patent_category": case.patent_category,
        "flow_dir": case.flow_dir,
        "client_id": case.client_id,
    }


@router.post("/cases/{case_id}/limited-edit")
def limited_edit_case(
    case_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Case.EditLimited")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if "title_cn" in payload:
        case.title_cn = payload.get("title_cn")
    if "title_en" in payload:
        case.title_en = payload.get("title_en")

    db.commit()
    return {"status": "ok"}


@router.get("/cases/export")
def export_cases(
    q: str | None = Query(default=None),
    case_no: str | None = Query(default=None),
    app_no: str | None = Query(default=None),
    client_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _perm: None = Depends(require_perm("Case.Export")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Case)

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Case.case_no.ilike(pattern),
                Case.title_cn.ilike(pattern),
                Case.title_en.ilike(pattern),
                Case.app_no.ilike(pattern),
            )
        )
    if case_no:
        query = query.filter(Case.case_no == case_no)
    if app_no:
        query = query.filter(Case.app_no == app_no)
    if client_id:
        query = query.filter(Case.client_id == client_id)
    if status:
        query = query.filter(Case.status == status)
    if date_from:
        query = query.filter(Case.recv_date >= date_from)
    if date_to:
        query = query.filter(Case.recv_date <= date_to)

    total = query.count()

    sort_field = Case.case_no
    allowed_sort_fields = {
        "case_no": Case.case_no,
        "recv_date": Case.recv_date,
        "filing_date": Case.filing_date,
        "created_at": Case.created_at,
    }
    if sort_by in allowed_sort_fields:
        sort_field = allowed_sort_fields[sort_by]

    if sort_dir.lower() == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    cases = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [
        {
            "id": case.id,
            "case_no": case.case_no,
            "case_type": case.case_type,
            "patent_category": case.patent_category,
        }
        for case in cases
    ]

    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.put("/cases/{case_id}")
def update_case(
    case_id: str,
    payload: dict[str, Any],
    _perm: None = Depends(require_perm("Case.Edit")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    new_case_no = payload.get("case_no")
    if new_case_no and new_case_no != case.case_no:
        exists = db.query(Case).filter(Case.case_no == new_case_no, Case.id != case_id).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="case_no already exists"
            )
        case.case_no = new_case_no

    case.case_type = payload.get("case_type", case.case_type)
    case.patent_category = payload.get("patent_category", case.patent_category)
    case.flow_dir = payload.get("flow_dir", case.flow_dir)
    case.client_id = payload.get("client_id", case.client_id)

    db.commit()
    db.refresh(case)

    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "patent_category": case.patent_category,
        "flow_dir": case.flow_dir,
        "client_id": case.client_id,
    }


@router.get("/cases/{case_id}")
def get_case(
    case_id: str,
    _perm: None = Depends(require_perm("Case.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    return {
        "id": case.id,
        "case_no": case.case_no,
        "case_type": case.case_type,
        "patent_category": case.patent_category,
        "flow_dir": case.flow_dir,
        "client_id": case.client_id,
    }
