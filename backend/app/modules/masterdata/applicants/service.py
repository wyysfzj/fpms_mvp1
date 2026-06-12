from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.masterdata.applicants.models import Applicant
from app.modules.masterdata.applicants.schemas import ApplicantCreateIn, ApplicantUpdateIn


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def list_applicants(
    db: Session,
    *,
    q: str | None,
    is_active: bool | None,
    page: int,
    page_size: int,
) -> tuple[list[Applicant], int]:
    stmt = select(Applicant)

    if q:
        needle = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Applicant.code).like(needle),
                func.lower(Applicant.name_cn).like(needle),
                func.lower(Applicant.name_en).like(needle),
            )
        )

    if is_active is not None:
        stmt = stmt.where(Applicant.is_active == is_active)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(Applicant.code.asc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total


def assert_applicant_code_unique(
    db: Session,
    *,
    code: str,
    exclude_applicant_id: str | None = None,
) -> None:
    stmt = select(Applicant).where(Applicant.code == code)
    if exclude_applicant_id:
        stmt = stmt.where(Applicant.id != exclude_applicant_id)
    if db.execute(stmt).scalar_one_or_none():
        raise_business_error("APPLICANT_CODE_DUPLICATE", "Applicant code already exists")


def assert_applicant_name_cn_unique(
    db: Session,
    *,
    name_cn: str,
    exclude_applicant_id: str | None = None,
) -> None:
    stmt = select(Applicant).where(Applicant.name_cn == name_cn)
    if exclude_applicant_id:
        stmt = stmt.where(Applicant.id != exclude_applicant_id)
    if db.execute(stmt).scalar_one_or_none():
        raise_business_error(
            "APPLICANT_NAME_CN_DUPLICATE",
            "Applicant Chinese name already exists",
        )


def create_applicant(db: Session, *, data: ApplicantCreateIn) -> Applicant:
    assert_applicant_code_unique(db, code=data.code)
    assert_applicant_name_cn_unique(db, name_cn=data.name_cn)

    applicant = Applicant(
        id=str(uuid4()),
        code=data.code,
        name_cn=data.name_cn,
        name_en=data.name_en,
        total_power_of_attorney_no=_normalize_optional_text(data.total_power_of_attorney_no),
        is_active=data.is_active,
    )
    db.add(applicant)
    db.commit()
    db.refresh(applicant)
    return applicant


def get_applicant(db: Session, *, applicant_id: str) -> Applicant:
    applicant = db.execute(
        select(Applicant).where(Applicant.id == applicant_id)
    ).scalar_one_or_none()
    if not applicant:
        raise_business_error("APPLICANT_NOT_FOUND", "Applicant not found", status_code=404)
    return applicant


def update_applicant(
    db: Session,
    *,
    applicant_id: str,
    data: ApplicantUpdateIn,
) -> Applicant:
    applicant = get_applicant(db, applicant_id=applicant_id)
    updates = data.model_dump(exclude_unset=True)

    if "code" in updates and updates["code"] is not None and updates["code"] != applicant.code:
        assert_applicant_code_unique(db, code=updates["code"], exclude_applicant_id=applicant_id)
    if (
        "name_cn" in updates
        and updates["name_cn"] is not None
        and updates["name_cn"] != applicant.name_cn
    ):
        assert_applicant_name_cn_unique(
            db,
            name_cn=updates["name_cn"],
            exclude_applicant_id=applicant_id,
        )

    for field, value in updates.items():
        if field == "total_power_of_attorney_no":
            value = _normalize_optional_text(value)
        setattr(applicant, field, value)

    db.commit()
    db.refresh(applicant)
    return applicant


def deactivate_applicant(db: Session, *, applicant_id: str) -> None:
    applicant = get_applicant(db, applicant_id=applicant_id)
    if applicant.is_active:
        applicant.is_active = False
        db.commit()
