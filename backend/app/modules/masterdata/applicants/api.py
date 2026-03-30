from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.masterdata.applicants.schemas import ApplicantListItemOut
from app.modules.masterdata.applicants.service import list_applicants

router = APIRouter()


@router.get("/applicants", summary="List applicants")
def get_applicants(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    is_active: bool | None = Query(default=None),
    _perm: None = Depends(require_perm("Applicant.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    applicants, total = list_applicants(
        db,
        q=q,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    items = [
        ApplicantListItemOut.model_validate(applicant).model_dump(mode="json")
        for applicant in applicants
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}
