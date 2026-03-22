import { http } from './http'
import type { Pagination } from './types'
import type {
    BillDetail,
    BillFromDraftsPayload,
    BillListItem,
    BillListParams,
    BillManualPayload,
    CaseReceiptsSummary,
    OffsetCreatePayload,
    OffsetListItem,
    PaymentCreatePayload,
    PaymentLineItem,
    PaymentListItem,
    PaymentListParams,
} from './billing.types'

interface BackendBill {
    id: string
    bill_no?: string | null
    client_id: string
    client_name?: string | null
    case_id?: string | null
    case_no?: string | null
    direction?: string | null
    status?: string | null
    total_gov?: number | string | null
    total_service?: number | string | null
    total_misc?: number | string | null
    amount?: number | string | null
    balance?: number | string | null
    currency?: string | null
    issue_date?: string | null
    bill_date?: string | null
    due_date?: string | null
    notes?: string | null
    created_at?: string
    updated_at?: string
    items?: {
        id?: string
        bill_id?: string
        case_id?: string | null
        draft_id?: string | null
        fee_code?: string | null
        fee_name?: string | null
        fee_type?: string | null
        year_no?: number | null
        description?: string | null
        quantity?: number | string | null
        unit_price?: number | string | null
        amount?: number | string | null
    }[]
    source_draft_ids?: string[] | null
    source_draft_labels?: string[] | null
    primary_draft_id?: string | null
    primary_draft_label?: string | null
}

interface BackendPayment {
    id: string
    pay_no?: string | null
    client_id: string
    pay_date?: string | null
    currency?: string | null
    amount?: string | number | null
    allocated_amt?: string | number | null
    unapplied_amt?: string | number | null
    line_count?: number | null
    prepayment_status?: string | null
}

interface BackendPaymentLine {
    id: string
    payment_id: string
    case_id?: string | null
    raw_amount?: string | number | null
    allocated_amt?: string | number | null
    balance_amt?: string | number | null
}

interface BackendPaymentDetail extends BackendPayment {
    payment_lines?: BackendPaymentLine[]
}

interface BackendOffset {
    id: string
    payment_line_id: string
    bill_id: string
    offset_amt: string | number
    offset_date?: string | null
    is_reversed: boolean
    reversed_at?: string | null
}

function asNumber(input: number | string | null | undefined): number {
    if (input === null || input === undefined || input === '') return 0
    const parsed = Number(input)
    return Number.isFinite(parsed) ? parsed : 0
}

function mapBillListItem(input: BackendBill): BillListItem {
    return {
        id: input.id,
        bill_no: input.bill_no || input.id,
        client_id: input.client_id,
        client_name: input.client_name || undefined,
        status: input.status || 'DRAFT',
        amount: asNumber(input.amount),
        balance: asNumber(input.balance),
        currency: input.currency || 'CNY',
        issue_date: input.bill_date || input.issue_date || undefined,
        due_date: input.due_date || undefined,
    }
}

function mapBillDetail(input: BackendBill): BillDetail {
    return {
        ...mapBillListItem(input),
        case_id: input.case_id || undefined,
        case_no: input.case_no || undefined,
        direction: input.direction || undefined,
        bill_date: input.bill_date || undefined,
        total_gov: input.total_gov != null ? asNumber(input.total_gov) : undefined,
        total_service: input.total_service != null ? asNumber(input.total_service) : undefined,
        total_misc: input.total_misc != null ? asNumber(input.total_misc) : undefined,
        items: (input.items || []).map((item, index) => ({
            id: item.id || `${input.id}-item-${index}`,
            bill_id: item.bill_id || input.id,
            case_id: item.case_id || undefined,
            draft_id: item.draft_id || undefined,
            fee_code: item.fee_code || undefined,
            fee_name: item.fee_name || undefined,
            fee_type: item.fee_type || undefined,
            year_no: item.year_no ?? undefined,
            description: item.description || item.fee_name || item.fee_code || '',
            quantity: asNumber(item.quantity),
            unit_price: asNumber(item.unit_price),
            amount: asNumber(item.amount),
        })),
        source_draft_ids: input.source_draft_ids || undefined,
        source_draft_labels: input.source_draft_labels || undefined,
        primary_draft_id: input.primary_draft_id || undefined,
        primary_draft_label: input.primary_draft_label || undefined,
        notes: input.notes || undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapPayment(
    input: BackendPayment,
    extras: Partial<PaymentListItem> = {}
): PaymentListItem {
    return {
        id: input.id,
        bill_id: extras.bill_id,
        bill_no: extras.bill_no,
        client_id: input.client_id,
        amount: asNumber(input.amount),
        currency: input.currency || extras.currency || 'CNY',
        allocated_amt: input.allocated_amt != null ? asNumber(input.allocated_amt) : undefined,
        unapplied_amt: input.unapplied_amt != null ? asNumber(input.unapplied_amt) : undefined,
        line_count: input.line_count ?? undefined,
        prepayment_status: input.prepayment_status || undefined,
        payment_method: extras.payment_method || 'OTHER',
        payment_date: input.pay_date || '',
        reference: input.pay_no || undefined,
        notes: extras.notes,
        created_at: extras.created_at || '',
    }
}

function mapPaymentLine(input: BackendPaymentLine): PaymentLineItem {
    return {
        id: input.id,
        payment_id: input.payment_id,
        case_id: input.case_id || undefined,
        raw_amount: asNumber(input.raw_amount),
        allocated_amt: asNumber(input.allocated_amt),
        balance_amt: asNumber(input.balance_amt),
    }
}

function mapOffset(input: BackendOffset): OffsetListItem {
    return {
        id: input.id,
        payment_line_id: input.payment_line_id,
        bill_id: input.bill_id,
        amount: asNumber(input.offset_amt),
        currency: 'CNY',
        offset_date: input.offset_date || undefined,
        is_reversed: input.is_reversed,
        reversed_at: input.reversed_at || undefined,
        created_at: input.offset_date || '',
    }
}

/**
 * Get paginated list of bills
 */
export async function getBills(params: BillListParams = {}): Promise<Pagination<BillListItem>> {
    const { page = 1, page_size = 20, status, client_id } = params
    const response = await http.get<Pagination<BackendBill>>('/bills', {
        params: { page, page_size, status, client_id }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapBillListItem),
    }
}

/**
 * Get a single bill by ID
 */
export async function getBill(id: string): Promise<BillDetail> {
    const response = await http.get<BackendBill>(`/bills/${id}`)
    return mapBillDetail(response.data)
}

/**
 * Create a bill from fee drafts
 */
export async function createBillFromDrafts(payload: BillFromDraftsPayload): Promise<BillDetail> {
    const response = await http.post<BackendBill>('/bills/from-drafts', {
        draft_ids: payload.draft_ids,
        bill_no: payload.bill_no || undefined,
    })
    return mapBillDetail(response.data)
}

/**
 * Create a manual bill with items
 */
export async function createManualBill(payload: BillManualPayload): Promise<BillDetail> {
    const response = await http.post<BackendBill>('/bills/manual', payload)
    return mapBillDetail(response.data)
}

/**
 * Print/download a bill as docx
 */
export async function printBill(id: string): Promise<Blob> {
    const response = await http.get(`/bills/${id}/print`, { responseType: 'blob' })
    return response.data
}

// ============ Payments ============

/**
 * Get paginated list of payments
 */
export async function getPayments(params: PaymentListParams = {}): Promise<Pagination<PaymentListItem>> {
    const { page = 1, page_size = 20, bill_id } = params
    const response = await http.get<Pagination<BackendPayment>>('/payments', {
        params: { page, page_size, bill_id }
    })

    return {
        ...response.data,
        items: response.data.items.map((item) =>
            mapPayment(item, {
                bill_id,
                bill_no: bill_id,
            })
        ),
    }
}

/**
 * Create a payment
 */
export async function createPayment(payload: PaymentCreatePayload): Promise<PaymentListItem> {
    let clientId = payload.client_id?.trim()
    let billNo = payload.bill_id

    if (!clientId && payload.bill_id) {
        const bill = await getBill(payload.bill_id)
        clientId = bill.client_id
        billNo = bill.bill_no
    }

    if (!clientId) {
        throw {
            status: 422,
            code: 'VALIDATION_ERROR',
            message: 'client_id is required (or provide a valid bill_id)',
            details: {
                errors: [{ loc: ['body', 'client_id'], msg: 'Field required' }],
            },
        }
    }

    const response = await http.post<BackendPayment>('/payments', {
        client_id: clientId,
        amount: payload.amount,
        pay_no: payload.reference || undefined,
        pay_date: payload.payment_date || undefined,
        currency: payload.currency || 'CNY',
        remark: payload.notes || undefined,
    })

    return mapPayment(response.data, {
        bill_id: payload.bill_id,
        bill_no: billNo,
        payment_method: payload.payment_method,
        notes: payload.notes,
    })
}

/**
 * Get payment lines for a payment.
 */
export async function getPaymentLines(paymentId: string): Promise<PaymentLineItem[]> {
    const response = await http.get<BackendPaymentDetail>(`/payments/${paymentId}`)
    const lines = response.data.payment_lines || []
    return lines.map(mapPaymentLine)
}

// ============ Offsets ============

/**
 * Offsets list endpoint is not exposed by current backend contract.
 */
export async function getOffsets(
    params: { page?: number; page_size?: number; bill_id?: string } = {}
): Promise<Pagination<OffsetListItem>> {
    const page = params.page || 1
    const pageSize = params.page_size || 20

    return {
        items: [],
        page,
        page_size: pageSize,
        total: 0,
    }
}

/**
 * Create an offset
 */
export async function createOffset(payload: OffsetCreatePayload): Promise<OffsetListItem> {
    const response = await http.post<BackendOffset>('/offsets', payload)
    return mapOffset(response.data)
}

/**
 * Reverse an offset
 */
export async function reverseOffset(id: string): Promise<OffsetListItem> {
    const response = await http.post<BackendOffset>(`/offsets/${id}/reverse`)
    return mapOffset(response.data)
}

// ============ Case Receipts ============

interface BackendCaseReceipt {
    id: string
    case_id: string
    fee_type?: string | null
    currency: string
    receivable_amt: string | number
    received_amt: string | number
    last_receipt_date?: string | null
    fee_code?: string | null
    year_no?: number | null
    is_arrears?: boolean | null
    invoice_no?: string | null
    is_commissionable?: boolean | null
}

function mapCaseReceipt(input: BackendCaseReceipt): CaseReceiptsSummary {
    const totalBilled = asNumber(input.receivable_amt)
    const totalPaid = asNumber(input.received_amt)
    return {
        case_id: input.case_id,
        total_billed: totalBilled,
        total_paid: totalPaid,
        total_outstanding: totalBilled - totalPaid,
        currency: input.currency || 'CNY',
        bills: [],
        fee_type: input.fee_type || undefined,
        fee_code: input.fee_code || undefined,
        year_no: input.year_no ?? undefined,
        last_receipt_date: input.last_receipt_date || undefined,
        is_arrears: input.is_arrears ?? undefined,
        invoice_no: input.invoice_no || undefined,
        is_commissionable: input.is_commissionable ?? undefined,
    }
}

/**
 * Get receipts summary for a case
 */
export async function getCaseReceipts(caseId: number | string): Promise<CaseReceiptsSummary> {
    const response = await http.get<BackendCaseReceipt>(`/cases/${caseId}/receipts`)
    return mapCaseReceipt(response.data)
}
