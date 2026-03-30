from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CountryCreateIn(BaseModel):
    code: str
    name_cn: str
    name_en: str | None = None
    is_active: bool = True


class CountryUpdateIn(BaseModel):
    code: str | None = None
    name_cn: str | None = None
    name_en: str | None = None
    is_active: bool | None = None


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name_cn: str
    name_en: str | None
    is_active: bool


class CountryListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name_cn: str
    name_en: str | None
    is_active: bool


class OkOut(BaseModel):
    status: str = "ok"
