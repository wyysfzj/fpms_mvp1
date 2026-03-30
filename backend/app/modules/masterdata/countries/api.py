from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_perm
from app.db.session import get_db
from app.modules.masterdata.countries.schemas import CountryListItemOut
from app.modules.masterdata.countries.service import list_countries

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
