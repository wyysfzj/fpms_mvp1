from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.masterdata.applicants.models import Applicant


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
