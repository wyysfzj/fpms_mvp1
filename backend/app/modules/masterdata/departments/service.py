from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.masterdata.departments.models import Department
from app.modules.masterdata.departments.schemas import DepartmentCreateIn, DepartmentUpdateIn


def list_departments(
    db: Session,
    *,
    q: str | None,
    is_active: bool | None,
    page: int,
    page_size: int,
) -> tuple[list[Department], int]:
    stmt = select(Department)

    if q:
        needle = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Department.department_code).like(needle),
                func.lower(Department.name_cn).like(needle),
            )
        )

    if is_active is not None:
        stmt = stmt.where(Department.is_active == is_active)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(Department.department_code.asc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total


def get_department(db: Session, *, department_id: str) -> Department:
    department = db.execute(
        select(Department).where(Department.id == department_id)
    ).scalar_one_or_none()
    if not department:
        raise_business_error("DEPARTMENT_NOT_FOUND", "Department not found", status_code=404)
    return department


def assert_department_code_unique(
    db: Session,
    *,
    department_code: str,
    exclude_department_id: str | None = None,
) -> None:
    stmt = select(Department).where(Department.department_code == department_code)
    if exclude_department_id:
        stmt = stmt.where(Department.id != exclude_department_id)
    if db.execute(stmt).scalar_one_or_none():
        raise_business_error(
            "DEPARTMENT_CODE_DUPLICATE",
            "Department code already exists",
        )


def assert_department_name_unique(
    db: Session,
    *,
    name_cn: str,
    exclude_department_id: str | None = None,
) -> None:
    stmt = select(Department).where(Department.name_cn == name_cn)
    if exclude_department_id:
        stmt = stmt.where(Department.id != exclude_department_id)
    if db.execute(stmt).scalar_one_or_none():
        raise_business_error(
            "DEPARTMENT_NAME_DUPLICATE",
            "Department Chinese name already exists",
        )


def create_department(db: Session, *, data: DepartmentCreateIn) -> Department:
    assert_department_code_unique(db, department_code=data.department_code)
    assert_department_name_unique(db, name_cn=data.name_cn)

    department = Department(
        id=str(uuid4()),
        department_code=data.department_code,
        name_cn=data.name_cn,
        is_active=data.is_active,
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def update_department(
    db: Session,
    *,
    department_id: str,
    data: DepartmentUpdateIn,
) -> Department:
    department = get_department(db, department_id=department_id)
    updates = data.model_dump(exclude_unset=True)

    if (
        "department_code" in updates
        and updates["department_code"] is not None
        and updates["department_code"] != department.department_code
    ):
        assert_department_code_unique(
            db,
            department_code=updates["department_code"],
            exclude_department_id=department_id,
        )
    if (
        "name_cn" in updates
        and updates["name_cn"] is not None
        and updates["name_cn"] != department.name_cn
    ):
        assert_department_name_unique(
            db,
            name_cn=updates["name_cn"],
            exclude_department_id=department_id,
        )

    for field, value in updates.items():
        setattr(department, field, value)

    db.commit()
    db.refresh(department)
    return department


def deactivate_department(db: Session, *, department_id: str) -> None:
    department = get_department(db, department_id=department_id)
    if department.is_active:
        department.is_active = False
        db.commit()
