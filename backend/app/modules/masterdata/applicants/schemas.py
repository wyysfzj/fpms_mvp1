from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ApplicantType = Literal["INDIVIDUAL", "ENTITY"]


class ApplicantCreateIn(BaseModel):
    code: str
    name_cn: str
    name_en: str | None = None
    total_power_of_attorney_no: str | None = Field(default=None, max_length=128)
    applicant_type: ApplicantType = "ENTITY"
    is_active: bool = True


class ApplicantUpdateIn(BaseModel):
    code: str | None = None
    name_cn: str | None = None
    name_en: str | None = None
    total_power_of_attorney_no: str | None = Field(default=None, max_length=128)
    applicant_type: ApplicantType | None = None
    is_active: bool | None = None


class ApplicantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name_cn: str
    name_en: str | None
    total_power_of_attorney_no: str | None
    applicant_type: ApplicantType
    is_active: bool


class ApplicantListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name_cn: str
    name_en: str | None
    total_power_of_attorney_no: str | None
    applicant_type: ApplicantType
    is_active: bool


class OkOut(BaseModel):
    status: str = "ok"
