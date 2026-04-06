import type { ApiError, Pagination } from './types'

export type ExpenseCategory = 'SEARCH_DB' | 'TRANSLATION' | 'TRANSPORT' | 'OTHER'

export interface ExpenseItem {
    id: number
    expense_no: string | null
    case_id: string | null
    category: ExpenseCategory | string
    expense_date: string | null
    amount: number
    currency: string
    status: string
    remark: string | null
    created_at: string
    updated_at: string
}

export interface ExpenseGroupedStat {
    key: string
    label: string
    expense_count: number
    total_amount: number
}

export interface ExpenseGrossProfitStat {
    key: string
    label: string
    currency: string
    expense_total: number
    received_total: number
    gross_profit_total: number
}

export interface ExpenseStats {
    count_by_category: Record<string, number>
    sum_by_category: Record<string, number>
    count_total: number
    sum_total: number
    case_amounts?: ExpenseGroupedStat[]
    client_amounts?: ExpenseGroupedStat[]
    gross_profit_amounts?: ExpenseGrossProfitStat[]
}

export interface ExpenseListResponse extends Pagination<ExpenseItem> {
    stats?: ExpenseStats
}

export interface ExpenseListParams {
    case_id?: string
    category?: ExpenseCategory | string
    date_from?: string
    date_to?: string
    currency?: string
    status?: string
    q?: string
    include_stats?: boolean
    page?: number
    page_size?: number
}

export interface ExpenseCreatePayload {
    case_id: string
    category: ExpenseCategory
    expense_date: string
    amount: number
    client_id?: string
    expense_no?: string
    vendor_name?: string
    currency?: string
    tax_amount?: number
    remark?: string
}

export type ExpenseErrorCategory =
    | 'unauthenticated'
    | 'permission_denied'
    | 'validation'
    | 'business'
    | 'not_found'
    | 'conflict'
    | 'unknown'

export type ExpenseApiAction = 'list' | 'create'

export interface ExpenseApiError extends ApiError {
    category: ExpenseErrorCategory
    field_errors?: Map<string, string[]>
}
