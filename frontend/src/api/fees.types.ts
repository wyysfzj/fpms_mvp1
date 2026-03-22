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
    currency: string
    status: FeeDraftStatus
    amount: FeeMoney
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
    created_at?: string
    updated_at?: string
}

export interface FeeDraftListParams {
    page?: number
    page_size?: number
    case_id?: string
    client_id?: string
    status?: FeeDraftStatus
}

export interface FeeDraftCreatePayload {
    case_id: string
    client_id?: string | null
    currency: string
    draft_type?: string
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
    description: string
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
