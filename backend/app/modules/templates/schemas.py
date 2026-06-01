from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TemplateCreateIn(BaseModel):
    name: str
    group: str | None = None
    language: str | None = None
    file_path: str
    enabled: bool = True


class TemplateUpdateIn(BaseModel):
    name: str | None = None
    group: str | None = None
    language: str | None = None
    file_path: str | None = None
    enabled: bool | None = None


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    group: str | None
    language: str | None
    file_path: str
    enabled: bool
    created_at: datetime


class TemplateListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    group: str | None
    language: str | None
    enabled: bool


class FormatLetterMappingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    official_doc_template_id: str | None = None
    official_doc_template_code: str | None = None
    official_doc_name_pattern: str | None = None
    format_letter_template_id: str | None = None
    format_letter_template_code: str | None = None
    output_name_rule: str | None = None
    salutation_rule_code: str | None = None
    contact_rule_code: str | None = None
    enabled: bool
    remark: str | None = None


class LetterHeadCreateIn(BaseModel):
    name: str
    locale: str | None = None
    logo_file_path: str | None = None
    header_text: str | None = None
    footer_text: str | None = None
    address_block: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    is_default: bool | None = None
    created_by_user_id: str | None = None


class LetterHeadUpdateIn(BaseModel):
    name: str | None = None
    locale: str | None = None
    logo_file_path: str | None = None
    header_text: str | None = None
    footer_text: str | None = None
    address_block: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    is_default: bool | None = None
    created_by_user_id: str | None = None


class LetterHeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    locale: str | None
    logo_file_path: str | None
    header_text: str | None
    footer_text: str | None
    address_block: str | None
    phone: str | None
    email: str | None
    website: str | None
    is_default: bool
    created_by_user_id: str | None
    created_at: datetime
    updated_at: datetime


class OkOut(BaseModel):
    status: str = "ok"
