from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClientCreateIn(BaseModel):
    client_code: str | None = None
    name_cn: str
    name_en: str | None = None
    email: str | None = None
    client_type: str | None = None
    default_currency: str | None = None
    is_active: bool | None = None


class ClientUpdateIn(BaseModel):
    client_code: str | None = None
    name_cn: str | None = None
    name_en: str | None = None
    email: str | None = None
    client_type: str | None = None
    default_currency: str | None = None
    is_active: bool | None = None


class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_code: str | None
    name_cn: str
    name_en: str | None
    email: str | None = None
    client_type: str
    default_currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClientAddressCreateIn(BaseModel):
    address_type: str = "GENERAL"
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    country_code: str | None = "CN"
    is_default: bool = False


class ClientAddressUpdateIn(BaseModel):
    address_type: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    country_code: str | None = None
    is_default: bool | None = None


class ClientAddressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    address_type: str
    address_line1: str | None
    address_line2: str | None
    city: str | None
    province: str | None
    postal_code: str | None
    country_code: str | None
    is_default: bool
    created_at: datetime
    updated_at: datetime


class ClientContactCreateIn(BaseModel):
    contact_name: str
    title: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    is_primary: bool = False


class ClientContactUpdateIn(BaseModel):
    contact_name: str | None = None
    title: str | None = None
    phone: str | None = None
    mobile: str | None = None
    email: str | None = None
    is_primary: bool | None = None


class ClientContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    contact_name: str
    title: str | None
    phone: str | None
    mobile: str | None
    email: str | None
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class ClientListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_code: str | None
    name_cn: str
    name_en: str | None


class OkOut(BaseModel):
    status: str = "ok"
