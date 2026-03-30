from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import raise_business_error
from app.modules.masterdata.countries.models import Country
from app.modules.masterdata.countries.schemas import CountryCreateIn, CountryUpdateIn


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


def get_country(db: Session, *, country_id: str) -> Country:
    country = db.execute(select(Country).where(Country.id == country_id)).scalar_one_or_none()
    if not country:
        raise_business_error("COUNTRY_NOT_FOUND", "Country not found", status_code=404)
    return country


def assert_country_code_unique(
    db: Session,
    *,
    code: str,
    exclude_country_id: str | None = None,
) -> None:
    stmt = select(Country).where(Country.code == code)
    if exclude_country_id:
        stmt = stmt.where(Country.id != exclude_country_id)
    if db.execute(stmt).scalar_one_or_none():
        raise_business_error("COUNTRY_CODE_DUPLICATE", "Country code already exists")


def assert_country_name_cn_unique(
    db: Session,
    *,
    name_cn: str,
    exclude_country_id: str | None = None,
) -> None:
    stmt = select(Country).where(Country.name_cn == name_cn)
    if exclude_country_id:
        stmt = stmt.where(Country.id != exclude_country_id)
    if db.execute(stmt).scalar_one_or_none():
        raise_business_error("COUNTRY_NAME_CN_DUPLICATE", "Country Chinese name already exists")


def create_country(db: Session, *, data: CountryCreateIn) -> Country:
    assert_country_code_unique(db, code=data.code)
    assert_country_name_cn_unique(db, name_cn=data.name_cn)

    country = Country(
        id=str(uuid4()),
        code=data.code,
        name_cn=data.name_cn,
        name_en=data.name_en,
        is_active=data.is_active,
    )
    db.add(country)
    db.commit()
    db.refresh(country)
    return country


def update_country(
    db: Session,
    *,
    country_id: str,
    data: CountryUpdateIn,
) -> Country:
    country = get_country(db, country_id=country_id)
    updates = data.model_dump(exclude_unset=True)

    if "code" in updates and updates["code"] is not None and updates["code"] != country.code:
        assert_country_code_unique(db, code=updates["code"], exclude_country_id=country_id)
    if (
        "name_cn" in updates
        and updates["name_cn"] is not None
        and updates["name_cn"] != country.name_cn
    ):
        assert_country_name_cn_unique(
            db,
            name_cn=updates["name_cn"],
            exclude_country_id=country_id,
        )

    for field, value in updates.items():
        setattr(country, field, value)

    db.commit()
    db.refresh(country)
    return country


def deactivate_country(db: Session, *, country_id: str) -> None:
    country = get_country(db, country_id=country_id)
    if country.is_active:
        country.is_active = False
        db.commit()
