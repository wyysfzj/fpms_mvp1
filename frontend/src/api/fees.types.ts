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
}

export interface ApplyFeeDraftGeneratePayload {
    case_id: string
    currency?: string
    discount_rate?: number | string | null
}

export interface OfficialFeePreviewPayload {
    case_id: string
    trigger_event: 'FILING_ACCEPTED' | 'REEXAM_REQUESTED'
    currency?: string
    source_document_id?: string | null
}

export interface OfficialFeePreviewCandidate {
    rate_id?: string | null
    fee_code: string
    fee_name?: string | null
    fee_type: string
    quantity: FeeMoney
    unit_price: FeeMoney
    amount: FeeMoney
    calculation_note?: string | null
    source_doc?: string | null
    source_status?: string | null
    fee_category?: string | null
    fee_subtype?: string | null
    trigger_rule?: string | null
    deadline_rule?: string | null
    reduction_scope?: string | null
    source_document_id?: string | null
    amount_before_reduction?: FeeMoney | null
    reduction_ratio?: FeeMoney | null
    payable_ratio?: FeeMoney | null
}

export interface OfficialFeePreview {
    case_id: string
    draft_type: string
    trigger_event: string
    source_document_id?: string | null
    idempotency_key: string
    currency: string
    preview_only: boolean
    total_gov: FeeMoney
    candidates: OfficialFeePreviewCandidate[]
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
