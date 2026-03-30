from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.masterdata.countries.schemas import (
    CountryCreateIn,
    CountryListItemOut,
    CountryOut,
    CountryUpdateIn,
    OkOut,
)
from app.modules.masterdata.countries.service import (
    create_country,
    deactivate_country,
    list_countries,
    update_country,
)

router = APIRouter()


@router.get("/countries", summary="List countries")
def get_countries(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    is_active: bool | None = Query(default=None),
    _perm: None = Depends(require_perm("Country.Read")),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    countries, total = list_countries(
        db,
        q=q,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )
    items = [
        CountryListItemOut.model_validate(country).model_dump(mode="json") for country in countries
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total}


@router.post(
    "/countries",
    status_code=status.HTTP_201_CREATED,
    response_model=CountryOut,
    summary="Create country",
)
def create_country_endpoint(
    payload: CountryCreateIn,
    _perm: None = Depends(require_perm("Country.Write")),
    db: Session = Depends(get_db),
) -> CountryOut:
    country = create_country(db, data=payload)
    return CountryOut.model_validate(country)


@router.put(
    "/countries/{country_id}",
    response_model=CountryOut,
    summary="Update country",
)
def update_country_endpoint(
    country_id: str,
    payload: CountryUpdateIn,
    _perm: None = Depends(require_perm("Country.Write")),
    db: Session = Depends(get_db),
) -> CountryOut:
    country = update_country(db, country_id=country_id, data=payload)
    return CountryOut.model_validate(country)


@router.put(
    "/countries/{country_id}/deactivate",
    response_model=OkOut,
    summary="Deactivate country",
)
def deactivate_country_endpoint(
    country_id: str,
    _perm: None = Depends(require_perm("Country.Write")),
    db: Session = Depends(get_db),
) -> OkOut:
    deactivate_country(db, country_id=country_id)
    return OkOut()
