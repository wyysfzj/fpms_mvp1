/**
 * Billing API Types
 */

import type { Pagination } from './types'

export type BillStatus = string
export type BillDirection = 'AR' | 'AP'
export type BadDebtStatus = 'NONE' | 'OPEN' | 'CLOSED' | string
export type BadDebtSubstatus =
    | 'MANUAL_MARK'
    | 'PARTIAL_TRANSFER'
    | 'PARTIAL_RECOVERY'
    | 'FULLY_RECOVERED'
    | string

export interface BillListItem {
    id: string
    bill_no: string
    client_id: string
    client_name?: string
    direction?: BillDirection | string
    status: BillStatus
    amount: number
    balance: number
    currency: string
    issue_date?: string
    bill_date?: string
    due_date?: string
    days_past_due?: number
    aging_bucket?: string
    is_overdue?: boolean
    is_bad_debt?: boolean
}

export interface BillListBadDebtSummary {
    bad_debt_bill_count: number
    bad_debt_amount: number
    total_recovered_amount: number
    remaining_bad_debt_balance: number
}

export interface BillListAgingBucket {
    bucket: string
    bill_count: number
    amount: number
}

export interface BillListReportSummary extends BillListBadDebtSummary {
    receivable_bill_count: number
    receivable_amount: number
    overdue_bill_count: number
    overdue_amount: number
    aging_buckets: BillListAgingBucket[]
}

export interface BillListResponse extends Pagination<BillListItem>, BillListBadDebtSummary {
    summary: BillListReportSummary
}

export interface BillItem {
    id: string
    bill_id?: string
    case_id?: string
    draft_id?: string
    fee_code?: string
    fee_name?: string
    fee_type?: string
    year_no?: number
    description: string
    quantity: number
    unit_price: number
    amount: number
}

export interface BillDetail {
    id: string
    bill_no: string
    client_id: string
    client_name?: string
    case_id?: string
    case_no?: string
    status: BillStatus
    amount: number
    balance: number
    currency: string
    direction?: string
    issue_date?: string
    bill_date?: string
    due_date?: string
    bad_debt_status?: BadDebtStatus
    bad_debt_substatus?: BadDebtSubstatus | null
    total_gov?: number
    total_service?: number
    total_misc?: number
    items: BillItem[]
    source_draft_ids?: string[]
    source_draft_labels?: string[]
    primary_draft_id?: string
    primary_draft_label?: string
    notes?: string
    bad_debt_voucher?: BillBadDebtVoucher | null
    bad_debt_recoveries?: BillBadDebtRecovery[]
    bad_debt_total_recovered?: number
    bad_debt_remaining_amount?: number
    created_at?: string
    updated_at?: string
}

export interface BillBadDebtVoucher {
    id: string
    bill_id: string
    status: BadDebtStatus
    bad_debt_amount: number
    recovered_amount: number
    bad_debt_date?: string
    remark?: string
}

export interface BillBadDebtRecovery {
    id: string
    voucher_id: string
    recovery_amount: number
    recovery_date?: string
    remark?: string
}

export interface BillListParams {
    page?: number
    page_size?: number
    status?: BillStatus
    bill_status?: BillStatus
    client_id?: string
    currency?: string
    bill_date_from?: string
    bill_date_to?: string
    aging_bucket?: string
    is_overdue?: boolean
    is_bad_debt?: boolean
    bad_debt_status?: BadDebtStatus
}

// Bill Creation Types
export interface BillFromDraftsPayload {
    draft_ids: string[]
    bill_no?: string
    currency?: string
    notes?: string
}

export interface BillManualPayload {
    client_id: string
    case_id?: string
    currency: string
    direction?: BillDirection
    status?: string
    items: BillManualItem[]
    notes?: string
}

export interface BillManualItem {
    description: string
    quantity: number
    unit_price: number
    fee_type?: string
    year_no?: number
}

export interface BillBadDebtActionPayload {
    mode: 'MARK' | 'TRANSFER'
    bad_debt_date?: string
    remark?: string
}

export interface BillBadDebtRecoveryPayload {
    recovery_amount: number
    recovery_date?: string
    remark?: string
}

// Payment Types
export type PaymentMethod = 'CASH' | 'BANK_TRANSFER' | 'CHECK' | 'OTHER'

export interface PaymentListItem {
    id: string
    bill_id?: string
    bill_no?: string
    client_id: string
    client_name?: string
    amount: number
    currency: string
    allocated_amt?: number
    unapplied_amt?: number
    line_count?: number
    prepayment_status?: string
    payment_method: PaymentMethod
    payment_date: string
    reference?: string
    notes?: string
    created_at: string
}

export interface PaymentListSummary {
    prepayment_count: number
    prepayment_total_amount: number
    allocated_total_amount: number
    remaining_prepayment_balance: number
}

export interface PaymentListResponse extends Pagination<PaymentListItem>, PaymentListSummary {}

export interface PaymentListParams {
    page?: number
    page_size?: number
    bill_id?: string
    client_id?: string
    prepayment_status?: string
    pay_date_from?: string
    pay_date_to?: string
    has_unapplied_only?: boolean
}

export interface PaymentCreatePayload {
    bill_id?: string
    client_id?: string
    amount: number
    payment_method: PaymentMethod
    payment_date: string
    reference?: string
    notes?: string
    currency?: string
}

export interface PaymentLineItem {
    id: string
    payment_id: string
    case_id?: string
    raw_amount: number
    allocated_amt: number
    balance_amt: number
}

// Offset Types
export interface OffsetListItem {
    id: string
    payment_line_id: string
    bill_id: string
    bill_no?: string
    amount: number
    currency: string
    offset_date?: string
    is_reversed: boolean
    reversed_at?: string
    created_at: string
}

export interface OffsetCreatePayload {
    payment_line_id: string
    bill_id: string
    offset_amt: number
    offset_date?: string
}

// Unified fee query types
export interface FeeUnifiedQueryItem {
    record_type: string
    record_id: string
    case_id?: string | null
    biz_no?: string | null
    party_name?: string | null
    amount: number
    currency: string
    status?: string | null
    biz_date?: string | null
    remark?: string | null
}

export interface FeeUnifiedQueryParams {
    page?: number
    page_size?: number
    record_type?: string
    case_id?: string
    biz_no?: string
    party_name?: string
    status?: string
    currency?: string
    date_range?: [string, string] | []
    amount_range?: [number, number] | []
}

export type FeeUnifiedQueryResponse = Pagination<FeeUnifiedQueryItem>

export interface FeeOverviewGovPaymentItem {
    gov_payment_id: number
    pay_list_id: number
    case_id: string
    case_no?: string | null
    app_no?: string | null
    patent_no?: string | null
    fee_item_id?: string | null
    fee_code?: string | null
    fee_name?: string | null
    year_no?: number | null
    planned_amt: number
    paid_amt: number
    currency: string
    list_no?: string | null
    voucher_no?: string | null
    invoice_no?: string | null
    planned_pay_date?: string | null
    paid_date?: string | null
}

export interface FeeOverviewGovPaymentParams {
    page?: number
    page_size?: number
    case_no?: string
    app_no?: string
    patent_no?: string
    client_id?: string
    applicant_name?: string
    fee_type?: string
    paid_date_range?: [string, string] | []
}

export type FeeOverviewGovPaymentResponse = Pagination<FeeOverviewGovPaymentItem>

export interface FeeOverviewCaseReceiptItem {
    receipt_id: string
    case_id: string
    case_no?: string | null
    app_no?: string | null
    patent_no?: string | null
    fee_code?: string | null
    fee_name?: string | null
    year_no?: number | null
    fee_type?: string | null
    receivable_amt: number
    received_amt: number
    currency: string
    is_arrears?: boolean | null
    is_prepayment?: boolean | null
    is_commissionable?: boolean | null
    receipt_date?: string | null
    due_date?: string | null
    invoice_no?: string | null
}

export interface FeeOverviewCaseReceiptParams {
    page?: number
    page_size?: number
    case_no?: string
    app_no?: string
    patent_no?: string
    client_id?: string
    applicant_name?: string
    fee_type?: string
    receipt_date_range?: [string, string] | []
}

export type FeeOverviewCaseReceiptResponse = Pagination<FeeOverviewCaseReceiptItem>

// Case Receipts Summary
export interface CaseReceiptsSummary {
    case_id: string
    total_billed: number
    total_paid: number
    total_outstanding: number
    currency: string
    bills: CaseReceiptBill[]
    // B5 enriched fields
    fee_type?: string
    fee_code?: string
    year_no?: number
    last_receipt_date?: string
    is_arrears?: boolean
    invoice_no?: string
    is_commissionable?: boolean
}

export interface CaseReceiptBill {
    id: string
    bill_no: string
    status: BillStatus
    amount: number
    balance: number
    issue_date?: string
}

export interface CaseReceiptCreate {
  case_id: string
  fee_type?: string | null
  fee_code?: string | null
  fee_name?: string | null
  year_no?: number | null
  currency?: string
  receivable_amt: number | string
  received_amt: number | string
  last_receipt_date?: string | null
  due_date?: string | null
  is_arrears?: boolean | null
  is_prepayment?: boolean | null
  is_commissionable?: boolean | null
  invoice_no?: string | null
  remark?: string | null
}

export interface CaseReceiptUpdate {
  fee_type?: string | null
  fee_code?: string | null
  fee_name?: string | null
  year_no?: number | null
  currency?: string | null
  receivable_amt?: number | string | null
  received_amt?: number | string | null
  last_receipt_date?: string | null
  due_date?: string | null
  is_arrears?: boolean | null
  is_prepayment?: boolean | null
  is_commissionable?: boolean | null
  invoice_no?: string | null
  remark?: string | null
}

export interface CaseReceiptListItem {
  id: string
  case_id: string
  case_no?: string | null
  client_name?: string | null
  fee_type?: string | null
  currency: string
  receivable_amt: number
  received_amt: number
  last_receipt_date?: string | null
  fee_code?: string | null
  fee_name?: string | null
  year_no?: number | null
  due_date?: string | null
  is_arrears?: boolean | null
  is_prepayment?: boolean | null
  is_commissionable?: boolean | null
  invoice_no?: string | null
  remark?: string | null
}

export interface CaseReceiptListResponse {
  items: CaseReceiptListItem[]
  page: number
  page_size: number
  total: number
}
