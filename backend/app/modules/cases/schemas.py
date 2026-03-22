from __future__ import annotations

from datetime import date

from pydantic import AliasChoices, BaseModel, Field, field_validator

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


class BioDepositIn(BaseModel):
    seq: int = Field(..., ge=1)
    deposit_no: str | None = Field(None, max_length=64)
    deposit_unit_name: str | None = Field(None, max_length=255)
    deposit_date: date | None = None
    name: str | None = Field(None, max_length=255)


class CaseCreate(BaseModel):
    case_no: str = Field(..., min_length=1, max_length=64, strip_whitespace=True)
    case_type: CaseType = CaseType.NORMAL
    patent_category: PatentCategory = PatentCategory.INV
    flow_dir: FlowDir = FlowDir.CN_DOMESTIC
    client_id: str | None = None
    foreign_agent_id: str | None = None
    foreign_ref: str | None = Field(None, max_length=64)
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
    # Deferred Batch 1 — PCT / invalidation
    ro: str | None = Field(None, max_length=64)
    isa: str | None = Field(None, max_length=64)
    ipea: str | None = Field(None, max_length=64)
    intl_app_no: str | None = Field(None, max_length=64)
    intl_app_date: date | None = None
    intl_pub_no: str | None = Field(None, max_length=64)
    intl_pub_date: date | None = None
    intl_pub_lang: str | None = Field(None, max_length=32)
    need_iper: bool | None = None
    iper_date: date | None = None
    pct_national_entry_date: date | None = None
    original_case_id: str | None = None
    invalid_client_id: str | None = None
    invalid_patentee: str | None = Field(None, max_length=255)
    invalid_requester: str | None = Field(None, max_length=255)
    invalid_role: str | None = Field(None, max_length=32)
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
    bio_deposits: list[BioDepositIn] = []


class CaseCreateIn(CaseCreate):
    """Backward-compatible case creation input schema."""


class CaseUpdateFull(BaseModel):
    title_cn: str | None = Field(default=None, validation_alias=AliasChoices("title_cn", "title"))
    title_en: str | None = None
    app_no: str | None = Field(None, max_length=64)
    status: CaseStatus | None = None
    filing_date: date | None = None
    foreign_agent_id: str | None = None
    foreign_ref: str | None = Field(None, max_length=64)
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
    # Deferred Batch 1 — PCT / invalidation
    ro: str | None = Field(None, max_length=64)
    isa: str | None = Field(None, max_length=64)
    ipea: str | None = Field(None, max_length=64)
    intl_app_no: str | None = Field(None, max_length=64)
    intl_app_date: date | None = None
    intl_pub_no: str | None = Field(None, max_length=64)
    intl_pub_date: date | None = None
    intl_pub_lang: str | None = Field(None, max_length=32)
    need_iper: bool | None = None
    iper_date: date | None = None
    pct_national_entry_date: date | None = None
    original_case_id: str | None = None
    invalid_client_id: str | None = None
    invalid_patentee: str | None = Field(None, max_length=255)
    invalid_requester: str | None = Field(None, max_length=255)
    invalid_role: str | None = Field(None, max_length=32)
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
    bio_deposits: list[BioDepositIn] | None = None

    @field_validator(
        "filing_date",
        "pub_date",
        "grant_date",
        "valid_until",
        "intl_app_date",
        "intl_pub_date",
        "iper_date",
        "pct_national_entry_date",
        mode="before",
    )
    @classmethod
    def _blank_dates_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value


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
    foreign_agent_id: str | None = None
    foreign_agent_name: str | None = None
    foreign_ref: str | None = None
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
    # Deferred Batch 1 — PCT / invalidation
    ro: str | None = None
    isa: str | None = None
    ipea: str | None = None
    intl_app_no: str | None = None
    intl_app_date: str | None = None
    intl_pub_no: str | None = None
    intl_pub_date: str | None = None
    intl_pub_lang: str | None = None
    need_iper: bool | None = None
    iper_date: str | None = None
    pct_national_entry_date: str | None = None
    original_case_id: str | None = None
    invalid_client_id: str | None = None
    invalid_patentee: str | None = None
    invalid_requester: str | None = None
    invalid_role: str | None = None
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
    bio_deposits: list[dict]
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
