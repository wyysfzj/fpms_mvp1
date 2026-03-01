from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SystemParamUpsertIn(BaseModel):
    param_value: str
    value_type: str | None = None
    description: str | None = None
    is_secret: bool | None = None


class SystemParamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    param_key: str
    param_value: str
    value_type: str
    description: str | None
    is_secret: bool
    updated_at: datetime
    created_at: datetime


class SystemParamListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    param_key: str
    param_value: str
    value_type: str
    is_secret: bool


class OkOut(BaseModel):
    status: str = "ok"
