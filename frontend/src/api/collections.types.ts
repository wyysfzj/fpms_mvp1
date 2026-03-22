import type { ApiError } from './types'

export interface DunningListParams {
    round_no?: number
    status?: string
    client_id?: string
    page?: number
    page_size?: number
}

export interface DunningBatchListItem {
    id: number
    dunning_no: string | null
    client_id: string
    round_no: number
    to_date: string | null
    currency: string
    total_amount: number
    status: string
    sent_date: string | null
    remark: string | null
    created_at: string
    updated_at: string
}

export interface DunningGeneratePayload {
    to_date: string
    client_id?: string
    client_ids?: string[]
    include_statuses?: string[]
    exclude_statuses?: string[]
    strict_conflict?: boolean
}

export interface DunningGenerateSummary {
    to_date: string
    eligible_bills: number
    groups: number
    created: number
    reused: number
    batches: number
}

export interface DunningGenerateBatchLine {
    id: number
    line_no: number
    bill_id: string
    bill_no_snapshot: string | null
    due_date_snapshot: string | null
    bill_status_snapshot: string | null
    outstanding_amount: number
    currency_snapshot: string | null
}

export interface DunningGenerateBatch {
    id: number
    dunning_no: string | null
    client_id: string
    round_no: number
    to_date: string | null
    currency: string
    total_amount: number
    status: string
    reused: boolean
    line_count: number
    lines: DunningGenerateBatchLine[]
}

export interface DunningDetailLine {
    id: number
    line_no: number
    bill_id: string
    bill_no_snapshot: string | null
    due_date_snapshot: string | null
    bill_status_snapshot: string | null
    outstanding_amount: number
    currency_snapshot: string | null
    remark?: string | null
}

export interface DunningDetail {
    id: number
    dunning_no: string | null
    client_id: string
    round_no: number
    to_date: string | null
    currency: string
    total_amount: number
    status: string
    sent_date: string | null
    remark: string | null
    created_at: string
    updated_at: string
    line_count: number
    lines: DunningDetailLine[]
    summary: {
        line_count: number
        bill_count: number
        bad_debt_line_count: number
    }
}

export interface DunningGenerateResult {
    summary: DunningGenerateSummary
    batches: DunningGenerateBatch[]
}

export interface BadDebtBillResult {
    id: string
    bill_no: string | null
    client_id: string
    currency: string
    status: string
    bill_date: string | null
    due_date: string | null
    amount: number
    balance: number
    updated_at: string
}

export type CollectionsErrorCategory =
    | 'unauthenticated'
    | 'permission_denied'
    | 'validation'
    | 'business'
    | 'not_found'
    | 'conflict'
    | 'unknown'

export interface CollectionsApiError extends ApiError {
    category: CollectionsErrorCategory
    field_errors?: Map<string, string[]>
}
