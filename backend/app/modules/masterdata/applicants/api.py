from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.masterdata.applicants.schemas import (
    ApplicantCreateIn,
    ApplicantListItemOut,
    ApplicantOut,
    ApplicantUpdateIn,
    OkOut,
)
from app.modules.masterdata.applicants.service import (
    create_applicant,
    deactivate_applicant,
    list_applicants,
    update_applicant,
)

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


@router.post(
    "/applicants",
    status_code=status.HTTP_201_CREATED,
    response_model=ApplicantOut,
    summary="Create applicant",
)
def create_applicant_endpoint(
    payload: ApplicantCreateIn,
    _perm: None = Depends(require_perm("Applicant.Write")),
    db: Session = Depends(get_db),
) -> ApplicantOut:
    applicant = create_applicant(db, data=payload)
    if applicant.applicant_type != payload.applicant_type:
        applicant.applicant_type = payload.applicant_type
        db.commit()
        db.refresh(applicant)
    return ApplicantOut.model_validate(applicant)


@router.put("/applicants/{applicant_id}", response_model=ApplicantOut, summary="Update applicant")
def update_applicant_endpoint(
    applicant_id: str,
    payload: ApplicantUpdateIn,
    _perm: None = Depends(require_perm("Applicant.Write")),
    db: Session = Depends(get_db),
) -> ApplicantOut:
    applicant = update_applicant(db, applicant_id=applicant_id, data=payload)
    return ApplicantOut.model_validate(applicant)


@router.put(
    "/applicants/{applicant_id}/deactivate",
    response_model=OkOut,
    summary="Deactivate applicant",
)
def deactivate_applicant_endpoint(
    applicant_id: str,
    _perm: None = Depends(require_perm("Applicant.Write")),
    db: Session = Depends(get_db),
) -> OkOut:
    deactivate_applicant(db, applicant_id=applicant_id)
    return OkOut()
