from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.modules.cases.enums import CaseStatus, CaseType, FlowDir, PatentCategory


class CaseApplicantIn(BaseModel):
    seq: int = Field(..., ge=1)
    is_first: bool = False
    name_cn: str | None = None
    name_en: str | None = None
    address_cn: str | None = None
    address_en: str | None = None


class CaseInventorIn(BaseModel):
    seq: int = Field(..., ge=1)
    name_cn: str | None = None
    name_en: str | None = None


class PriorityIn(BaseModel):
    seq: int = Field(..., ge=1)
    country_code: str | None = Field(None, max_length=10)
    prio_no: str | None = Field(None, max_length=64)
    prio_date: date | None = None


class CaseCreate(BaseModel):
    case_no: str = Field(..., min_length=1, max_length=64, strip_whitespace=True)
    case_type: CaseType = CaseType.NORMAL
    patent_category: PatentCategory = PatentCategory.INV
    flow_dir: FlowDir = FlowDir.CN_DOMESTIC
    client_id: str | None = None
    title_cn: str | None = None
    title_en: str | None = None
    app_no: str | None = Field(None, max_length=64)
    # A3 — Publication / Grant
    pub_date: date | None = None
    pub_no: str | None = Field(None, max_length=64)
    grant_date: date | None = None
    grant_no: str | None = Field(None, max_length=64)
    patent_no: str | None = Field(None, max_length=64)
    valid_until: date | None = None
    # A3 — Spec details
    spec_pages: int | None = Field(None, ge=0)
    claim_count: int | None = Field(None, ge=0)
    has_exam_request: bool | None = None
    # A3 — Agent assignment
    primary_agent_id: str | None = Field(None, max_length=36)
    second_agent_id: str | None = Field(None, max_length=36)
    draftor_id: str | None = Field(None, max_length=36)
    # A3 — Control flags
    is_fee_monitor: bool | None = None
    fee_reduction: str | None = Field(None, max_length=32)
    applicant_kind: str | None = Field(None, max_length=32)
    # Sub-tables
    applicants: list[CaseApplicantIn] = []
    inventors: list[CaseInventorIn] = []
    priorities: list[PriorityIn] = []


class CaseCreateIn(CaseCreate):
    """Backward-compatible case creation input schema."""


class CaseUpdateFull(BaseModel):
    title_cn: str | None = None
    title_en: str | None = None
    app_no: str | None = Field(None, max_length=64)
    status: CaseStatus | None = None
    # A3 — Publication / Grant
    pub_date: date | None = None
    pub_no: str | None = Field(None, max_length=64)
    grant_date: date | None = None
    grant_no: str | None = Field(None, max_length=64)
    patent_no: str | None = Field(None, max_length=64)
    valid_until: date | None = None
    # A3 — Spec details
    spec_pages: int | None = Field(None, ge=0)
    claim_count: int | None = Field(None, ge=0)
    has_exam_request: bool | None = None
    # A3 — Agent assignment
    primary_agent_id: str | None = Field(None, max_length=36)
    second_agent_id: str | None = Field(None, max_length=36)
    draftor_id: str | None = Field(None, max_length=36)
    # A3 — Control flags
    is_fee_monitor: bool | None = None
    fee_reduction: str | None = Field(None, max_length=32)
    applicant_kind: str | None = Field(None, max_length=32)
    # Sub-tables
    applicants: list[CaseApplicantIn] | None = None
    inventors: list[CaseInventorIn] | None = None
    priorities: list[PriorityIn] | None = None


class CaseUpdateLimited(BaseModel):
    """Limited fields editable by Agent role."""

    title_cn: str | None = None
    title_en: str | None = None
    # A3 — Spec details (Agent can update these)
    spec_pages: int | None = Field(None, ge=0)
    claim_count: int | None = Field(None, ge=0)
    inventors: list[CaseInventorIn] | None = None


class CaseDetail(BaseModel):
    id: str
    case_no: str
    case_type: str
    patent_category: str
    flow_dir: str
    client_id: str | None
    client_name: str | None = None
    title_cn: str | None
    title_en: str | None
    app_no: str | None
    status: str
    filing_date: str | None = None
    recv_date: str | None = None
    # A3 — Publication / Grant
    pub_date: str | None = None
    pub_no: str | None = None
    grant_date: str | None = None
    grant_no: str | None = None
    patent_no: str | None = None
    valid_until: str | None = None
    # A3 — Spec details
    spec_pages: int | None = None
    claim_count: int | None = None
    has_exam_request: bool | None = None
    # A3 — Agent assignment
    primary_agent_id: str | None = None
    second_agent_id: str | None = None
    draftor_id: str | None = None
    # A3 — Control flags
    is_fee_monitor: bool | None = None
    fee_reduction: str | None = None
    applicant_kind: str | None = None
    # Sub-tables & timestamps
    applicants: list[dict]  # CaseApplicantOut
    inventors: list[dict]  # CaseInventorOut
    priorities: list[dict]  # PriorityOut
    created_at: str | None = None
    updated_at: str | None = None


class CaseListItem(BaseModel):
    id: str
    case_no: str
    case_type: str
    patent_category: str
    client_id: str | None
    client_name: str | None = None
    title_cn: str | None
    title_en: str | None
    app_no: str | None = None
    status: str
    filing_date: str | None = None
    recv_date: str | None = None
    # A3 — key list fields
    patent_no: str | None = None
    primary_agent_id: str | None = None
