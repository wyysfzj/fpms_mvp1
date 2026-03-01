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
}

export interface CaseInventor {
    seq: number
    name_cn?: string
    name_en?: string
}

export interface Case {
    id: string
    case_no: string
    title?: string
    client_id: string | number
    client_name?: string
    status?: string
    filing_date?: string
    recv_date?: string
    app_date?: string
    app_no?: string
    applicants?: CaseApplicant[]
    inventors?: CaseInventor[]
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
    created_at: string
    updated_at: string
}

export interface CaseListParams {
    page?: number
    page_size?: number
}

export interface CaseCreatePayload {
    case_no: string
    title?: string
    client_id: string | number
    patent_category?: string
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
}

export interface CaseUpdatePayload {
    title?: string
    status?: string
    filing_date?: string
    app_date?: string
    notes?: string
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
}

export interface CaseLimitedEditPayload {
    notes?: string
}
