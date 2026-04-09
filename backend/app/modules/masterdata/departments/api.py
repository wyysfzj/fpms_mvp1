from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.masterdata.departments.schemas import (
    DepartmentCreateIn,
    DepartmentListItemOut,
    DepartmentOut,
    DepartmentUpdateIn,
    OkOut,
)
from app.modules.masterdata.departments.service import (
    create_department,
    deactivate_department,
    list_departments,
    update_department,
)

router = APIRouter()


@router.get("/departments", summary="List departments")
def get_departments(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    is_active: bool | None = Query(default=None),
    _perm: None = Depends(require_perm("Department.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    departments, total = list_departments(
        db,
        q=q,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    items = [
        DepartmentListItemOut.model_validate(department).model_dump(mode="json")
        for department in departments
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post(
    "/departments",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentOut,
    summary="Create department",
)
def create_department_endpoint(
    payload: DepartmentCreateIn,
    _perm: None = Depends(require_perm("Department.Write")),
    db: Session = Depends(get_db),
) -> DepartmentOut:
    department = create_department(db, data=payload)
    return DepartmentOut.model_validate(department)


@router.put(
    "/departments/{department_id}",
    response_model=DepartmentOut,
    summary="Update department",
)
def update_department_endpoint(
    department_id: str,
    payload: DepartmentUpdateIn,
    _perm: None = Depends(require_perm("Department.Write")),
    db: Session = Depends(get_db),
) -> DepartmentOut:
    department = update_department(db, department_id=department_id, data=payload)
    return DepartmentOut.model_validate(department)


@router.put(
    "/departments/{department_id}/deactivate",
    response_model=OkOut,
    summary="Deactivate department",
)
def deactivate_department_endpoint(
    department_id: str,
    _perm: None = Depends(require_perm("Department.Write")),
    db: Session = Depends(get_db),
) -> OkOut:
    deactivate_department(db, department_id=department_id)
    return OkOut()
