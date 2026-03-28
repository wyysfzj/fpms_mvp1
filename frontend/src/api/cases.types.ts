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
    app_date?: string
    app_no?: string
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
    app_no?: string
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
}

export interface CaseUpdatePayload {
    title?: string
    status?: string
    filing_date?: string
    foreign_agent_id?: string | null
    foreign_ref?: string | null
    app_no?: string | null
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
