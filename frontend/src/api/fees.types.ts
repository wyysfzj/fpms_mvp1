/**
 * Fee API Types
 */

export type CalcMode = 'FIXED' | 'PER_CLAIM' | 'PER_PAGE' | 'TIER'
export type RateGroup = 'DOMESTIC' | 'PCT' | 'ANNUITY'

export interface FeeRate {
    id: string
    name: string
    rate: number
    currency?: string
    description?: string
    fee_code?: string
    fee_type?: string
    enabled?: boolean
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    fee_domain?: string | null
    fee_section?: string | null
    fee_category?: string | null
    fee_subtype?: string | null
    reduction_scope?: string | null
    calc_mode?: CalcMode | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
    source_doc?: string | null
    source_url?: string | null
    source_policy?: string | null
    source_version?: string | null
    source_status?: string | null
    created_at?: string
    updated_at?: string
}

export interface FeeRateListParams {
    page?: number
    page_size?: number
    fee_code?: string
    fee_type?: string
    currency?: string
    enabled?: boolean
    rate_group?: string
    country_code?: string
    case_type?: string
    patent_category?: string
    fee_domain?: string
    fee_section?: string
    fee_category?: string
    fee_subtype?: string
    calc_mode?: string
}

export interface FeeRateCreatePayload {
    name: string
    rate: number
    currency?: string
    description?: string
    fee_code?: string
    fee_type?: string
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    fee_domain?: string | null
    fee_section?: string | null
    fee_category?: string | null
    fee_subtype?: string | null
    reduction_scope?: string | null
    calc_mode?: CalcMode | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
}

export interface FeeRateUpdatePayload {
    name?: string
    rate?: number
    currency?: string
    description?: string
    fee_type?: string
    enabled?: boolean
    rate_group?: string | null
    country_code?: string | null
    case_type?: string | null
    patent_category?: string | null
    fee_domain?: string | null
    fee_section?: string | null
    fee_category?: string | null
    fee_subtype?: string | null
    reduction_scope?: string | null
    calc_mode?: CalcMode | null
    calc_params?: string | null
    allow_reduction?: boolean | null
    effective_from?: string | null
    effective_to?: string | null
}

// Fee Draft Types
export type FeeDraftStatus = 'OPEN' | 'LOCKED'
export type FeeMoney = number | string

export interface FeeDraftListItem {
    id: string
    case_id: string
    case_no?: string | null
    client_id: string | null
    client_name?: string | null
    draft_type?: string | null
    currency: string
    status: FeeDraftStatus
    amount: FeeMoney
}

export interface FeeDraftReportSummary {
    total_draft_count: number
    service_fee_amount: FeeMoney
    government_fee_amount: FeeMoney
    income_amount: FeeMoney
    billed_amount: FeeMoney
    received_amount: FeeMoney
    unpaid_balance_amount: FeeMoney
    partially_received_bill_count: number
    client_amounts: FeeDraftGroupedAmount[]
    case_type_amounts: FeeDraftGroupedAmount[]
    country_amounts: FeeDraftGroupedAmount[]
    agent_service_amounts: FeeDraftAgentServiceAmount[]
    year_amounts: FeeDraftTrendAmount[]
    month_amounts: FeeDraftTrendAmount[]
}

export interface FeeDraftGroupedAmount {
    key: string
    label: string
    draft_count: number
    service_fee_amount: FeeMoney
    government_fee_amount: FeeMoney
    income_amount: FeeMoney
}

export interface FeeDraftAgentServiceAmount {
    key: string
    label: string
    draft_count: number
    service_fee_amount: FeeMoney
}

export interface FeeDraftTrendAmount {
    key: string
    label: string
    draft_count: number
    service_fee_amount: FeeMoney
    government_fee_amount: FeeMoney
    income_amount: FeeMoney
    draft_type_amounts: FeeDraftGroupedAmount[]
}

export interface FeeDraftListResponse {
    items: FeeDraftListItem[]
    page: number
    page_size: number
    total: number
    summary: FeeDraftReportSummary
}

export interface FeeDraftDetail {
    id: string
    case_id: string
    case_no?: string | null
    client_id: string | null
    client_name?: string | null
    draft_type: string
    currency: string
    status: FeeDraftStatus
    total_gov?: FeeMoney
    total_service?: FeeMoney
    total_misc?: FeeMoney
    amount?: FeeMoney
    official_fee_reduction_note?: string | null
    official_template_status?: string | null
    official_template_version?: string | null
    official_template_note?: string | null
    created_at?: string
    updated_at?: string
}

export interface FeeDraftListParams {
    page?: number
    page_size?: number
    case_id?: string
    case_no?: string
    client_id?: string
    status?: FeeDraftStatus
    draft_status?: FeeDraftStatus
    fee_type?: string
    currency?: string
    date_from?: string
    date_to?: string
    bill_status?: string
}

export interface FeeDraftCreatePayload {
    case_id: string
    client_id?: string | null
    currency: string
    draft_type?: string
    obligation_id?: string | null
}

export interface ApplyFeeDraftGeneratePayload {
    case_id: string
    currency?: string
    discount_rate?: number | string | null
}

export interface OfficialFeeEstimateContext {
    case_id: string
    trigger_context: {
        trigger: string
        source_document_id: string | null
    }
    currency: 'CNY'
    rate_effective_on: string
}

export interface OfficialFeeEstimateResult {
    case_id: string
    estimate_status: 'ESTIMATE'
    trigger_context: {
        trigger: string
        source_document_id: string | null
    }
    currency: 'CNY'
    candidates: {
        line: {
            fee_code: string
            fee_name: string
            fee_year_key: number
            official_full_amount: string | null
            reduction_ratio: string
            payable_amount: string
            source_amount: string | null
            source_date: string | null
            difference_review_state: 'MATCHED' | 'SOURCE_PENDING' | 'REVIEW_REQUIRED'
        }
        source: {
            rate_id: string | null
            source_document_id: string | null
            source_doc: string | null
            source_url: string | null
            source_policy: string | null
            source_version: string | null
            status: 'VERIFIED' | 'REVIEW_REQUIRED' | 'LEGACY_UNVERIFIED'
        }
    }[]
    total_payable_amount: string
}

export type FeeReductionApprovalScopeType = 'CASE' | 'APPLICANT_SET'

export interface FeeReductionApprovalCreatePayload {
    case_id: string
    scope_type: FeeReductionApprovalScopeType
    applicant_ids: string[]
    eligibility_attributes_version: string
    eligibility_attributes_json: string
    reduction_ratio: '0.7' | '0.85'
    fee_codes: string[]
    fee_year_from: number | null
    fee_year_to: number | null
    effective_from: string
    effective_to: string | null
    source_evidence_version_id: string
    expected_source_content_hash: string
    confirmed_at: string
}

export interface FeeReductionApprovalCreateResult {
    approval_id: string
}

export interface FeeReductionApprovalListItem {
    approval_id: string
    scope_type: FeeReductionApprovalScopeType
    case_id: string | null
    applicant_set_key: string | null
    reduction_ratio: string
    fee_codes: string[]
    fee_year_from: number | null
    fee_year_to: number | null
    effective_from: string
    effective_to: string | null
    source_evidence_version_id: string
    confirmation_status: string
    confirmed_at: string
    confirmed_by: string
    is_current: boolean
}

export interface FeeObligationInstructionPayload {
    instruction: 'PAY' | 'HOLD' | 'ABANDON'
    idempotency_key: string
}

export interface FeeObligationInstructionResult {
    obligation_id: string
    client_instruction_status: 'PENDING' | 'PAY' | 'HOLD' | 'ABANDON'
    activity_id: string
    idempotency_key: string
    reused: boolean
}

export interface FeeObligationDetail {
    id: string
    case_id: string
    source: {
        source_activity_id: string
        source_document_id: string | null
        status: 'VERIFIED' | 'REVIEW_REQUIRED' | 'LEGACY_UNVERIFIED'
    }
    fee_domain: 'GOV' | 'SERVICE'
    obligation_type: string
    due_date: string | null
    currency: string
    statuses: {
        estimate_status: 'ESTIMATE' | null
        obligation_status: 'RECOGNIZED' | 'SUPERSEDED'
        client_instruction_status: 'PENDING' | 'PAY' | 'HOLD' | 'ABANDON'
        draft_status: 'NOT_CREATED' | 'CREATED'
        pay_list_status: 'NOT_CREATED' | 'CREATED'
        payment_status: 'UNPAID' | 'PAID'
        official_evidence_status: 'PENDING' | 'VERIFIED' | 'NOT_APPLICABLE'
    }
    lines: {
        id: string
        obligation_id: string
        case_id: string
        source_activity_id: string
        fee_code: string
        fee_name: string
        fee_year_key: number
        official_full_amount: string | null
        reduction_ratio: string
        payable_amount: string
        source_amount: string | null
        source_date: string | null
        difference_review_state: 'MATCHED' | 'SOURCE_PENDING' | 'REVIEW_REQUIRED'
        current_identity_key: string | null
    }[]
    supersedes_obligation_id: string | null
    supersede_reason: string | null
}

export interface FeeDraftUpdatePayload {
    case_id?: string
    client_id?: string | null
    draft_type?: string
    currency?: string
    status?: FeeDraftStatus
}

// Fee Item Types

export interface FeeItem {
    id: string
    draft_id: string
    case_id?: string | null
    description: string
    fee_code?: string | null
    fee_name?: string | null
    fee_type?: string | null
    quantity: number
    unit_price: number
    amount: number
    rate_id?: string
}

export interface FeeItemCreatePayload {
    rate_id?: string
    description: string
    quantity: number
    unit_price: number
}

export interface FeeItemUpdatePayload {
    description?: string
    quantity?: number
    unit_price?: number
}
