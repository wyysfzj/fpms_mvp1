from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DepartmentCreateIn(BaseModel):
    department_code: str
    name_cn: str
    is_active: bool = True


class DepartmentUpdateIn(BaseModel):
    department_code: str | None = None
    name_cn: str | None = None
    is_active: bool | None = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    department_code: str
    name_cn: str
    is_active: bool


class DepartmentListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    department_code: str
    name_cn: str
    is_active: bool


class OkOut(BaseModel):
    status: str = "ok"
