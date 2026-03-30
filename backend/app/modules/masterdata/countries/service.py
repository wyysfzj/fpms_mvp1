from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.masterdata.countries.models import Country


def list_countries(
    db: Session,
    *,
    q: str | None,
    is_active: bool | None,
    page: int,
    page_size: int,
) -> tuple[list[Country], int]:
    stmt = select(Country)

    if q:
        needle = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Country.code).like(needle),
                func.lower(Country.name_cn).like(needle),
                func.lower(Country.name_en).like(needle),
            )
        )

    if is_active is not None:
        stmt = stmt.where(Country.is_active == is_active)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    offset = (page - 1) * page_size
    stmt = stmt.order_by(Country.code.asc()).offset(offset).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total
