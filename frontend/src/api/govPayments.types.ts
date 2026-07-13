import type { ApiError } from './types'

export interface PayListCreatePayload {
    fee_item_ids: string[]
    planned_pay_date?: string
    remark?: string
}

export interface PayListCreateSummary {
    requested: number
    success: number
    failed: number
    pay_list_created: boolean
}

export interface PayListInfo {
    id: number
    pay_list_no: string | null
    client_id: string
    client_name?: string | null
    currency: string
    status: string
    planned_pay_date: string | null
    total_amount: number
    paid_date?: string | null
    remark?: string | null
    created_at?: string
    updated_at?: string
    created_by?: string | null
    updated_by?: string | null
}

export interface PayListCreateSuccessItem {
    fee_item_id: string
    case_id: string
    amount: number
    currency: string
    pay_list_id: number
}

export interface PayListCreateFailedItem {
    fee_item_id: string
    code: string
    message: string
    status_code: number
}

export interface PayListCreateResult {
    summary: PayListCreateSummary
    pay_list: PayListInfo | null
    success: PayListCreateSuccessItem[]
    failed: PayListCreateFailedItem[]
}

export interface GovPaymentRegisterPayload {
    pay_list_id: number
    fee_item_id: string
    paid_date?: string
    paid_amount?: number | string
    official_receipt_no?: string
    remark?: string
}

export interface GovPaymentInfo {
    id: number
    pay_list_id: number
    case_id: string
    case_no?: string | null
    fee_item_id: string | null
    status: string
    currency: string
    paid_date: string | null
    paid_amount: number
    official_receipt_no: string | null
    remark: string | null
    created_at?: string
    updated_at?: string
    created_by?: string | null
    updated_by?: string | null
}

export interface GovPaymentRegisterResult {
    gov_payment: GovPaymentInfo
    pay_list: PayListInfo
}

export interface PayListQuery {
    pay_list_no?: string
    client_id?: string
    status?: string
    currency?: string
    planned_pay_date_from?: string
    planned_pay_date_to?: string
    page?: number
    page_size?: number
}

export interface PayListListItem extends PayListInfo {
    client_name: string | null
    remark: string | null
    created_at: string
    updated_at: string
    created_by: string | null
    updated_by: string | null
}

export interface PayListListResult {
    items: PayListListItem[]
    page: number
    page_size: number
    total: number
}

export interface PayListDetailResult {
    pay_list: PayListInfo & {
        remark: string | null
        created_at: string
        updated_at: string
        created_by: string | null
        updated_by: string | null
    }
    gov_payments: GovPaymentInfo[]
}

export interface HistoricalPayListCreatePayload {
    client_id?: string
    currency: string
    planned_pay_date?: string
    remark?: string
}

export type HistoricalPayListCreateResult = PayListInfo

export interface PayListMarkPaidPayload {
    paid_date: string
}

export interface PayListMarkPaidResult {
    pay_list: PayListInfo & {
        remark?: string | null
        updated_by?: string | null
    }
}

export interface ManualGovPaymentCreatePayload {
    case_id: string
    fee_item_id?: string | null
    paid_date: string
    paid_amount: number | string
    official_receipt_no?: string
    remark?: string
}

export interface ManualGovPaymentCreateResult {
    gov_payment: GovPaymentInfo
    pay_list: PayListInfo
}

export type GovPaymentsErrorCategory =
    | 'unauthenticated'
    | 'permission_denied'
    | 'validation'
    | 'business'
    | 'not_found'
    | 'conflict'
    | 'unknown'

export interface GovPaymentsApiError extends ApiError {
    category: GovPaymentsErrorCategory
    field_errors?: Map<string, string[]>
}
