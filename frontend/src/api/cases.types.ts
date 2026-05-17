/**
 * Case API Types
 */

export interface CaseApplicant {
    seq: number
    is_first?: boolean
    name_cn?: string
    name_en?: string
    address_cn?: string
    address_en?: string
    source_client_id?: string
}

export interface CaseInventor {
    seq: number
    name_cn?: string
    name_en?: string
}

export interface CasePriority {
    seq: number
    country_code?: string
    prio_no?: string
    prio_date?: string
}

export interface CaseBioDeposit {
    seq: number
    deposit_no?: string
    deposit_unit_name?: string
    deposit_date?: string
    name?: string
}

export interface CaseAgentSplit {
    agent_id: string
    role?: string
    share_ratio: number | null
}

export interface Case {
    id: string
    case_no: string
    case_type?: string
    patent_category?: string
    flow_dir?: string
    title?: string
    client_id: string | number
    client_name?: string
    foreign_agent_id?: string
    foreign_agent_name?: string
    foreign_ref?: string
    status?: string
    filing_date?: string
    recv_date?: string
    issue_date?: string
    app_date?: string
    app_no?: string
    from_country?: string
    to_country?: string
    doc_address_id?: string
    bill_address_id?: string
    cert_no?: string
    draw_pages?: number
    claim_pages?: number
    manuscript_words?: number
    discount_rate?: string
    no_power?: boolean
    no_prio_text?: boolean
    require_hk?: boolean
    first_annuity_year?: number
    applicants?: CaseApplicant[]
    inventors?: CaseInventor[]
    priorities?: CasePriority[]
    bio_deposits?: CaseBioDeposit[]
    ro?: string
    isa?: string
    ipea?: string
    intl_app_no?: string
    intl_app_date?: string
    intl_pub_no?: string
    intl_pub_date?: string
    intl_pub_lang?: string
    need_iper?: boolean
    iper_date?: string
    pct_national_entry_date?: string
    original_case_id?: string
    invalid_client_id?: string
    invalid_client_name?: string
    invalid_patentee?: string
    invalid_requester?: string
    invalid_role?: string
    notes?: string
    // A3: Publication & Grant
    pub_date?: string
    pub_no?: string
    grant_date?: string
    grant_no?: string
    patent_no?: string
    valid_until?: string
    // A3: Specification
    spec_pages?: number
    claim_count?: number
    has_exam_request?: boolean
    // A3: Agent Assignment
    primary_agent_id?: string
    second_agent_id?: string
    draftor_id?: string
    // A3: Control Flags
    is_fee_monitor?: boolean
    fee_reduction?: string
    applicant_kind?: string
    agent_splits?: CaseAgentSplit[]
    created_at: string
    updated_at: string
}

export interface CaseListParams {
    page?: number
    page_size?: number
    case_no?: string
    client_id?: string
    status?: string
    case_type?: string
    patent_category?: string
    country?: string
    agent_id?: string
    date_from?: string
    date_to?: string
    applicant_id?: string
    patent_no?: string
    fee_status?: string
}

export interface CaseReportCount {
    key: string
    count: number
}

export interface CaseClientReportCount {
    key: string
    label: string
    count: number
    case_type_counts: CaseReportCount[]
}

export interface CaseTrendReportCount {
    key: string
    label: string
    new_case_count: number
    granted_count: number
    terminated_count: number
    invalidated_count: number
    withdrawn_count: number
    abandoned_count: number
}

export interface CaseListSummary {
    total_case_count: number
    status_counts: CaseReportCount[]
    case_type_counts: CaseReportCount[]
    client_counts: CaseClientReportCount[]
    country_counts: CaseReportCount[]
    agent_counts: CaseReportCount[]
    year_trends: CaseTrendReportCount[]
    month_trends: CaseTrendReportCount[]
    granted_count: number
    grant_rate: number | null
    terminated_count: number
    invalidated_count: number
    in_prosecution_count: number
}

export interface CaseListResponse {
    items: Case[]
    page: number
    page_size: number
    total: number
    summary: CaseListSummary
}

export interface CaseCreatePayload {
    case_no: string
    case_type?: string
    title?: string
    client_id: string | number
    patent_category?: string
    flow_dir?: string
    foreign_agent_id?: string
    foreign_ref?: string
    from_country?: string
    to_country?: string
    doc_address_id?: string
    bill_address_id?: string
    app_no?: string
    recv_date?: string
    issue_date?: string
    cert_no?: string
    draw_pages?: number
    claim_pages?: number
    manuscript_words?: number
    discount_rate?: string
    no_power?: boolean
    no_prio_text?: boolean
    require_hk?: boolean
    first_annuity_year?: number
    filing_date?: string
    status?: string
    bio_deposits?: CaseBioDeposit[]
    ro?: string
    isa?: string
    ipea?: string
    intl_app_no?: string
    intl_app_date?: string
    intl_pub_no?: string
    intl_pub_date?: string
    intl_pub_lang?: string
    need_iper?: boolean
    iper_date?: string
    pct_national_entry_date?: string
    original_case_id?: string
    invalid_client_id?: string
    invalid_patentee?: string
    invalid_requester?: string
    invalid_role?: string
    // A3 fields (all optional on create)
    pub_date?: string
    pub_no?: string
    grant_date?: string
    grant_no?: string
    patent_no?: string
    valid_until?: string
    spec_pages?: number
    claim_count?: number
    has_exam_request?: boolean
    primary_agent_id?: string
    second_agent_id?: string
    draftor_id?: string
    is_fee_monitor?: boolean
    fee_reduction?: string
    applicant_kind?: string
    applicants?: CaseApplicant[]
    priorities?: CasePriority[]
    agent_splits?: CaseAgentSplit[]
}

export interface CaseUpdatePayload {
    title?: string
    status?: string
    filing_date?: string
    recv_date?: string | null
    foreign_agent_id?: string | null
    foreign_ref?: string | null
    from_country?: string | null
    to_country?: string | null
    doc_address_id?: string | null
    bill_address_id?: string | null
    app_no?: string | null
    issue_date?: string | null
    cert_no?: string | null
    draw_pages?: number | null
    claim_pages?: number | null
    manuscript_words?: number | null
    discount_rate?: string | null
    no_power?: boolean | null
    no_prio_text?: boolean | null
    require_hk?: boolean | null
    first_annuity_year?: number | null
    case_type?: string | null
    patent_category?: string | null
    flow_dir?: string | null
    priorities?: CasePriority[] | null
    bio_deposits?: CaseBioDeposit[] | null
    ro?: string | null
    isa?: string | null
    ipea?: string | null
    intl_app_no?: string | null
    intl_app_date?: string | null
    intl_pub_no?: string | null
    intl_pub_date?: string | null
    intl_pub_lang?: string | null
    need_iper?: boolean | null
    iper_date?: string | null
    pct_national_entry_date?: string | null
    original_case_id?: string | null
    invalid_client_id?: string | null
    invalid_patentee?: string | null
    invalid_requester?: string | null
    invalid_role?: string | null
    agent_splits?: CaseAgentSplit[] | null
    // A3 fields (all optional on update, | null for explicit clearing)
    pub_date?: string | null
    pub_no?: string | null
    grant_date?: string | null
    grant_no?: string | null
    patent_no?: string | null
    valid_until?: string | null
    spec_pages?: number | null
    claim_count?: number | null
    has_exam_request?: boolean | null
    primary_agent_id?: string | null
    second_agent_id?: string | null
    draftor_id?: string | null
    is_fee_monitor?: boolean | null
    fee_reduction?: string | null
    applicant_kind?: string | null
    applicants?: CaseApplicant[] | null
}

export interface CaseLimitedEditPayload {
    notes?: string
}

export type CaseDocumentGateConclusion = 'PASS' | 'WARNING' | 'BLOCKED'

export interface CaseDocumentGateMatchedDocument {
    id: string
    title?: string
    doc_type?: string
    template_code?: string
}

export interface CaseDocumentGateCheck {
    requirement_code: string
    requirement_name: string
    role: string
    blocks_submission: boolean
    afterfill_allowed: boolean
    status: string
    matched_documents: CaseDocumentGateMatchedDocument[]
}

export interface CaseDocumentGateMissingItem {
    requirement_code: string
    requirement_name: string
    role: string
    blocks_submission: boolean
    afterfill_allowed: boolean
}

export interface CaseDocumentGateFileEvent {
    document_id: string
    title?: string
    doc_type?: string
    direction: string
    event_status: string
    need_reply?: boolean | null
    reply_date?: string
    reply_to_id?: string
}

export interface CaseDocumentGatePreview {
    case_type: string
    patent_category: string
    flow_dir: string
    conclusion: CaseDocumentGateConclusion
    hard_block: boolean
    afterfill_audit_required: boolean
    material_count: number
    checks: CaseDocumentGateCheck[]
    missing_items: CaseDocumentGateMissingItem[]
    file_events: CaseDocumentGateFileEvent[]
    suggested_actions: string[]
}

export interface CaseIntakeDocumentGateParams {
    case_type: string
    patent_category: string
    flow_dir: string
    has_exam_request?: boolean
    no_power?: boolean
    has_priority?: boolean
    source_document_ids?: string[]
}

export interface CaseBatchFilingExecutionPreview {
    kind: string
    label: string
    enabled: boolean
    detail?: string
}

export interface CaseBatchFilingFinalMaterialGate {
    material_count: number
    missing_items: CaseDocumentGateMissingItem[]
    conclusion: CaseDocumentGateConclusion
    hard_block: boolean
    afterfill_audit_required: boolean
    execution_preview: CaseBatchFilingExecutionPreview[]
}

export interface CaseBatchFilingCandidate {
    id: string
    case_no: string
    title_cn?: string
    client_name?: string
    case_type: string
    patent_category: string
    flow_dir: string
    recv_date?: string
    status: string
    has_exam_request?: boolean
    final_material_gate?: CaseBatchFilingFinalMaterialGate
}

export interface CaseBatchFilingQueryParams {
    case_type?: string
    flow_dir?: string
    status?: string
    recv_date_from?: string
    recv_date_to?: string
    client_id?: string
    primary_agent_id?: string
    patent_category?: string
    page?: number
    page_size?: number
}

export interface CaseBatchFilingActionPayload {
    selected_case_ids: string[]
    submitted_date: string
    apply_exam_now: boolean
    generate_list: boolean
}

export interface CaseBatchFilingActionResult {
    success_count: number
    failure_count: number
    updated_case_ids: string[]
}
