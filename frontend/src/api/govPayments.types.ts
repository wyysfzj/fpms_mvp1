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
    currency: string
    status: string
    planned_pay_date: string | null
    total_amount: number
    paid_date?: string | null
}

export interface PayListGovPaymentRow {
    id: number
    pay_list_id: number
    case_id: string
    fee_item_id: string | null
    status: string
    currency: string
    paid_date: string | null
    paid_amount: number
    official_receipt_no: string | null
    remark: string | null
    created_at?: string | null
    updated_at?: string | null
}

export interface PayListDetail extends PayListInfo {
    remark?: string | null
    created_at?: string | null
    updated_at?: string | null
    gov_payments: PayListGovPaymentRow[]
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
    fee_item_id: string
    status: string
    currency: string
    paid_date: string | null
    paid_amount: number
    official_receipt_no: string | null
    remark: string | null
}

export interface GovPaymentRegisterResult {
    gov_payment: GovPaymentInfo
    pay_list: PayListInfo
}

export interface PayListMarkPaidPayload {
    paid_date?: string
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
