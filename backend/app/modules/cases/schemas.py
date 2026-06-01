from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, Field, field_validator

from app.modules.cases.enums import CaseStatus, CaseType, FlowDir, PatentCategory


class CaseApplicantIn(BaseModel):
    seq: int = Field(..., ge=1)
    is_first: bool = False
    applicant_id: str | None = Field(default=None, max_length=36)
    name_cn: str | None = None
    name_en: str | None = None
    address_cn: str | None = None
    address_en: str | None = None
    nationality: str | None = Field(None, max_length=64)
    certificate_type: str | None = Field(None, max_length=32)
    certificate_no: str | None = Field(None, max_length=128)
    official_postcode: str | None = Field(None, max_length=32)
    official_applicant_kind: str | None = Field(None, max_length=32)

    @field_validator("applicant_id", mode="before")
    @classmethod
    def _blank_applicant_id_to_none(cls, value):
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value


class CaseInventorIn(BaseModel):
    seq: int = Field(..., ge=1)
    name_cn: str | None = None
    name_en: str | None = None
    nationality: str | None = Field(None, max_length=64)
    china_id_no: str | None = Field(None, max_length=64)


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


class CaseAgentSplitIn(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=36)
    role: str | None = Field(default=None, max_length=32)
    share_ratio: Decimal


class CaseCreate(BaseModel):
    case_no: str = Field(..., min_length=1, max_length=64, strip_whitespace=True)
    case_type: CaseType = CaseType.NORMAL
    patent_category: PatentCategory = PatentCategory.INV
    flow_dir: FlowDir = FlowDir.CN_DOMESTIC
    status: CaseStatus | None = None
    filing_date: date | None = None
    client_id: str | None = None
    foreign_agent_id: str | None = None
    foreign_ref: str | None = Field(None, max_length=64)
    from_country: str | None = Field(None, max_length=10)
    to_country: str | None = Field(None, max_length=10)
    doc_address_id: str | None = Field(None, max_length=36)
    bill_address_id: str | None = Field(None, max_length=36)
    title_cn: str | None = None
    title_en: str | None = None
    app_no: str | None = Field(None, max_length=64)
    recv_date: date | None = None
    # A3 — Publication / Grant
    pub_date: date | None = None
    pub_no: str | None = Field(None, max_length=64)
    issue_date: date | None = None
    grant_date: date | None = None
    grant_no: str | None = Field(None, max_length=64)
    cert_no: str | None = Field(None, max_length=64)
    patent_no: str | None = Field(None, max_length=64)
    valid_until: date | None = None
    # A3 — Spec details
    spec_pages: int | None = Field(None, ge=0)
    draw_pages: int | None = Field(None, ge=0)
    claim_count: int | None = Field(None, ge=0)
    claim_pages: int | None = Field(None, ge=0)
    manuscript_words: int | None = Field(None, ge=0)
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
    discount_rate: Decimal | None = Field(None, ge=Decimal("0"), le=Decimal("1"))
    no_power: bool | None = None
    no_prio_text: bool | None = None
    require_hk: bool | None = None
    first_annuity_year: int | None = Field(None, ge=1)
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
    recv_date: date | None = None
    foreign_agent_id: str | None = None
    foreign_ref: str | None = Field(None, max_length=64)
    from_country: str | None = Field(None, max_length=10)
    to_country: str | None = Field(None, max_length=10)
    doc_address_id: str | None = Field(None, max_length=36)
    bill_address_id: str | None = Field(None, max_length=36)
    # A3 — Publication / Grant
    pub_date: date | None = None
    pub_no: str | None = Field(None, max_length=64)
    issue_date: date | None = None
    grant_date: date | None = None
    grant_no: str | None = Field(None, max_length=64)
    cert_no: str | None = Field(None, max_length=64)
    patent_no: str | None = Field(None, max_length=64)
    valid_until: date | None = None
    # A3 — Spec details
    spec_pages: int | None = Field(None, ge=0)
    draw_pages: int | None = Field(None, ge=0)
    claim_count: int | None = Field(None, ge=0)
    claim_pages: int | None = Field(None, ge=0)
    manuscript_words: int | None = Field(None, ge=0)
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
    discount_rate: Decimal | None = Field(None, ge=Decimal("0"), le=Decimal("1"))
    no_power: bool | None = None
    no_prio_text: bool | None = None
    require_hk: bool | None = None
    first_annuity_year: int | None = Field(None, ge=1)
    # Sub-tables
    applicants: list[CaseApplicantIn] | None = None
    inventors: list[CaseInventorIn] | None = None
    priorities: list[PriorityIn] | None = None
    bio_deposits: list[BioDepositIn] | None = None
    agent_splits: list[CaseAgentSplitIn] | None = None

    @field_validator(
        "filing_date",
        "recv_date",
        "pub_date",
        "issue_date",
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
    draw_pages: int | None = Field(None, ge=0)
    claim_count: int | None = Field(None, ge=0)
    claim_pages: int | None = Field(None, ge=0)
    manuscript_words: int | None = Field(None, ge=0)
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
    from_country: str | None = None
    to_country: str | None = None
    doc_address_id: str | None = None
    bill_address_id: str | None = None
    title_cn: str | None
    title_en: str | None
    app_no: str | None
    status: str
    filing_date: str | None = None
    recv_date: str | None = None
    # A3 — Publication / Grant
    pub_date: str | None = None
    pub_no: str | None = None
    issue_date: str | None = None
    grant_date: str | None = None
    grant_no: str | None = None
    cert_no: str | None = None
    patent_no: str | None = None
    valid_until: str | None = None
    # A3 — Spec details
    spec_pages: int | None = None
    draw_pages: int | None = None
    claim_count: int | None = None
    claim_pages: int | None = None
    manuscript_words: int | None = None
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
    discount_rate: str | None = None
    no_power: bool | None = None
    no_prio_text: bool | None = None
    require_hk: bool | None = None
    first_annuity_year: int | None = None
    agent_splits: list[dict] | None = None
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
    applicants: list[dict] = Field(default_factory=list)
    inventors: list[dict] = Field(default_factory=list)


class CaseReportCountResponse(BaseModel):
    key: str
    count: int = 0


class CaseClientReportCountResponse(BaseModel):
    key: str
    label: str
    count: int = 0
    case_type_counts: list[CaseReportCountResponse] = Field(default_factory=list)


class CaseTrendReportCountResponse(BaseModel):
    key: str
    label: str
    new_case_count: int = 0
    granted_count: int = 0
    terminated_count: int = 0
    invalidated_count: int = 0
    withdrawn_count: int = 0
    abandoned_count: int = 0


class CaseReportSummaryResponse(BaseModel):
    total_case_count: int = 0
    status_counts: list[CaseReportCountResponse] = Field(default_factory=list)
    case_type_counts: list[CaseReportCountResponse] = Field(default_factory=list)
    client_counts: list[CaseClientReportCountResponse] = Field(default_factory=list)
    country_counts: list[CaseReportCountResponse] = Field(default_factory=list)
    agent_counts: list[CaseReportCountResponse] = Field(default_factory=list)
    year_trends: list[CaseTrendReportCountResponse] = Field(default_factory=list)
    month_trends: list[CaseTrendReportCountResponse] = Field(default_factory=list)
    granted_count: int = 0
    grant_rate: float | None = None
    terminated_count: int = 0
    invalidated_count: int = 0
    in_prosecution_count: int = 0


class CaseListReportResponse(BaseModel):
    items: list[CaseListItem]
    page: int
    page_size: int
    total: int
    summary: CaseReportSummaryResponse


class CaseBatchFilingCandidateItem(BaseModel):
    id: str
    case_no: str
    title_cn: str | None = None
    client_name: str | None = None
    case_type: str
    patent_category: str
    flow_dir: str
    recv_date: str | None = None
    status: str
    has_exam_request: bool | None = None
    final_material_gate: CaseBatchFilingFinalMaterialGateOut | None = None


class CaseBatchFilingActionIn(BaseModel):
    selected_case_ids: list[str] = Field(default_factory=list)
    submitted_date: date
    apply_exam_now: bool = False
    generate_list: bool = False


class CaseBatchFilingActionOut(BaseModel):
    success_count: int
    failure_count: int
    updated_case_ids: list[str]
    document_ids: list[str] = Field(default_factory=list)
    created_task_ids: list[str] = Field(default_factory=list)


class CaseDocumentGateMatchedDocumentOut(BaseModel):
    id: str
    title: str | None = None
    doc_type: str | None = None
    template_code: str | None = None


class CaseDocumentGateCheckOut(BaseModel):
    requirement_code: str
    requirement_name: str
    role: str
    blocks_submission: bool
    afterfill_allowed: bool
    status: str
    matched_documents: list[CaseDocumentGateMatchedDocumentOut] = Field(default_factory=list)


class CaseDocumentGateMissingItemOut(BaseModel):
    requirement_code: str
    requirement_name: str
    role: str
    blocks_submission: bool
    afterfill_allowed: bool


class CaseDocumentGateFileEventOut(BaseModel):
    document_id: str
    title: str | None = None
    doc_type: str | None = None
    direction: str
    event_status: str
    need_reply: bool | None = None
    reply_date: str | None = None
    reply_to_id: str | None = None


class CaseDocumentGatePreviewOut(BaseModel):
    case_type: str
    patent_category: str
    flow_dir: str
    conclusion: str
    hard_block: bool
    afterfill_audit_required: bool
    material_count: int
    checks: list[CaseDocumentGateCheckOut] = Field(default_factory=list)
    missing_items: list[CaseDocumentGateMissingItemOut] = Field(default_factory=list)
    file_events: list[CaseDocumentGateFileEventOut] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)


class CaseBatchFilingExecutionPreviewOut(BaseModel):
    kind: str
    label: str
    enabled: bool
    detail: str | None = None


class CaseBatchFilingFinalMaterialGateOut(BaseModel):
    material_count: int
    missing_items: list[CaseDocumentGateMissingItemOut] = Field(default_factory=list)
    conclusion: str
    hard_block: bool
    afterfill_audit_required: bool
    execution_preview: list[CaseBatchFilingExecutionPreviewOut] = Field(default_factory=list)
