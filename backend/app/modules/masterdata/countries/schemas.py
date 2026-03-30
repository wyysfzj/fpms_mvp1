from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CountryListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name_cn: str
    name_en: str | None
    is_active: bool
