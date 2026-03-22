/**
 * Billing API Types
 */

export type BillStatus = string
export type BillDirection = 'AR' | 'AP'

export interface BillListItem {
    id: string
    bill_no: string
    client_id: string
    client_name?: string
    status: BillStatus
    amount: number
    balance: number
    currency: string
    issue_date?: string
    due_date?: string
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
    total_gov?: number
    total_service?: number
    total_misc?: number
    items: BillItem[]
    source_draft_ids?: string[]
    source_draft_labels?: string[]
    primary_draft_id?: string
    primary_draft_label?: string
    notes?: string
    created_at?: string
    updated_at?: string
}

export interface BillListParams {
    page?: number
    page_size?: number
    status?: BillStatus
    client_id?: string
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

// Payment Types
export type PaymentMethod = 'CASH' | 'BANK_TRANSFER' | 'CHECK' | 'OTHER'

export interface PaymentListItem {
    id: string
    bill_id?: string
    bill_no?: string
    client_id: string
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

export interface PaymentListParams {
    page?: number
    page_size?: number
    bill_id?: string
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
