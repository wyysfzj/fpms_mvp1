from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.pagination import PageResult
from app.modules.documents.enums import DocumentDirection


class DocAttachmentOut(BaseModel):
    id: str
    document_id: str
    file_name: str
    mime_type: str
    file_size: int
    uploaded_at: datetime


class DocumentCreateIn(BaseModel):
    case_id: str
    doc_template_id: str | None = None
    direction: DocumentDirection
    doc_date: date
    title: str
    ref_no: str | None = None
    extra_data: str | None = None
    reply_to_id: str | None = None


class DocumentUpdateIn(BaseModel):
    case_id: str | None = None
    doc_template_id: str | None = None
    direction: DocumentDirection | None = None
    doc_date: date | None = None
    title: str | None = None
    ref_no: str | None = None
    extra_data: str | None = None
    reply_to_id: str | None = None
    need_reply: bool | None = None
    reply_date: date | None = None


class DocumentOut(BaseModel):
    id: str
    case_id: str
    case_no: str | None = None
    doc_template_id: str | None
    direction: DocumentDirection
    doc_date: date | None
    title: str | None
    ref_no: str | None
    extra_data: str | None
    reply_to_id: str | None = None
    need_reply: bool | None = None
    reply_date: date | None = None
    created_at: datetime
    updated_at: datetime
    attachments: list[DocAttachmentOut] = Field(default_factory=list)


class DocumentListOut(PageResult[DocumentOut]):
    pass


# --- B1: DocTemplate schemas ---


class DocTemplateCreateIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=256)
    direction: DocumentDirection = DocumentDirection.IN
    enabled: bool = True
    status_effect: str | None = Field(default=None, max_length=32)
    status_restore: str | None = Field(default=None, max_length=32)
    deadline_template_code: str | None = Field(default=None, max_length=64)
    fee_draft_type: str | None = Field(default=None, max_length=32)
    fee_item_list: str | None = None  # JSON string
    need_reply: bool | None = False
    reply_to_template_code: str | None = Field(default=None, max_length=64)
    input_fields: str | None = None  # JSON string


class DocTemplateUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=256)
    direction: DocumentDirection | None = None
    enabled: bool | None = None
    status_effect: str | None = Field(default=None, max_length=32)
    status_restore: str | None = Field(default=None, max_length=32)
    deadline_template_code: str | None = Field(default=None, max_length=64)
    fee_draft_type: str | None = Field(default=None, max_length=32)
    fee_item_list: str | None = None
    need_reply: bool | None = None
    reply_to_template_code: str | None = Field(default=None, max_length=64)
    input_fields: str | None = None


class DocTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    direction: DocumentDirection
    enabled: bool
    status_effect: str | None = None
    status_restore: str | None = None
    deadline_template_code: str | None = None
    fee_draft_type: str | None = None
    fee_item_list: str | None = None
    need_reply: bool | None = None
    reply_to_template_code: str | None = None
    input_fields: str | None = None
    created_at: datetime
    updated_at: datetime


class DocTemplateListOut(PageResult[DocTemplateOut]):
    pass
