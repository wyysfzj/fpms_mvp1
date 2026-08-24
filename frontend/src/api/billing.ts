import { http } from './http'
import type { Pagination } from './types'
import type {
    BadDebtStatus,
    BillDetail,
    BillBadDebtActionPayload,
    BillBadDebtRecovery,
    BillBadDebtRecoveryPayload,
    BillBadDebtVoucher,
    BillFromDraftsPayload,
    BillListItem,
    BillListParams,
    BillListResponse,
    BillManualPayload,
    CaseReceiptCreate,
    CaseReceiptListResponse,
    CaseReceiptsSummary,
    CaseReceiptUpdate,
    OffsetCreatePayload,
    OffsetListItem,
    FeeUnifiedQueryItem,
    FeeOverviewCaseReceiptItem,
    FeeOverviewCaseReceiptParams,
    FeeOverviewCaseReceiptResponse,
    FeeOverviewGovPaymentItem,
    FeeOverviewGovPaymentParams,
    FeeOverviewGovPaymentResponse,
    FeeUnifiedQueryParams,
    FeeUnifiedQueryResponse,
    PaymentCreatePayload,
    PaymentLineItem,
    PaymentListItem,
    PaymentListParams,
    PaymentListResponse,
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
    bad_debt_status?: string | null
    bad_debt_substatus?: string | null
    total_gov?: number | string | null
    total_service?: number | string | null
    total_misc?: number | string | null
    amount?: number | string | null
    balance?: number | string | null
    currency?: string | null
    issue_date?: string | null
    bill_date?: string | null
    due_date?: string | null
    days_past_due?: number | null
    aging_bucket?: string | null
    is_overdue?: boolean | null
    is_bad_debt?: boolean | null
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
    bad_debt_voucher?: BackendBadDebtVoucher | null
    bad_debt_recoveries?: BackendBadDebtRecovery[] | null
    bad_debt_total_recovered?: number | string | null
    bad_debt_remaining_amount?: number | string | null
}

interface BackendBillListResponse extends Pagination<BackendBill> {
    summary: {
        receivable_bill_count?: number | string
        receivable_amount?: number | string
        overdue_bill_count?: number | string
        overdue_amount?: number | string
        bad_debt_bill_count?: number | string
        bad_debt_amount?: number | string
        total_recovered_amount?: number | string
        remaining_bad_debt_balance?: number | string
        aging_buckets?: {
            bucket: string
            bill_count?: number | string
            amount?: number | string
        }[]
    }
    bad_debt_bill_count: number
    bad_debt_amount: number | string
    total_recovered_amount: number | string
    remaining_bad_debt_balance: number | string
}

interface BackendBadDebtVoucher {
    id: string
    bill_id: string
    status: string
    bad_debt_amount: number | string | null
    recovered_amount: number | string | null
    bad_debt_date?: string | null
    remark?: string | null
}

interface BackendBadDebtRecovery {
    id: string
    voucher_id: string
    recovery_amount: number | string | null
    recovery_date?: string | null
    remark?: string | null
}

interface BackendPayment {
    id: string
    pay_no?: string | null
    bill_id?: string | null
    bill_no?: string | null
    client_id: string
    client_name?: string | null
    pay_date?: string | null
    currency?: string | null
    amount?: string | number | null
    allocated_amt?: string | number | null
    unapplied_amt?: string | number | null
    line_count?: number | null
    prepayment_status?: string | null
}

interface BackendPaymentListResponse extends Pagination<BackendPayment> {
    prepayment_count: number | string
    prepayment_total_amount: number | string
    allocated_total_amount: number | string
    remaining_prepayment_balance: number | string
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
    bill_no?: string | null
    offset_amt: string | number
    offset_date?: string | null
    is_reversed: boolean
    reversed_at?: string | null
    created_at?: string | null
}

interface BackendFeeOverviewGovPaymentItem {
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
    planned_amt?: number | string | null
    paid_amt?: number | string | null
    currency?: string | null
    list_no?: string | null
    voucher_no?: string | null
    invoice_no?: string | null
    planned_pay_date?: string | null
    paid_date?: string | null
}

interface BackendFeeOverviewCaseReceiptItem {
    receipt_id: string
    case_id: string
    case_no?: string | null
    app_no?: string | null
    patent_no?: string | null
    fee_code?: string | null
    fee_name?: string | null
    year_no?: number | null
    fee_type?: string | null
    receivable_amt?: number | string | null
    received_amt?: number | string | null
    currency?: string | null
    is_arrears?: boolean | null
    is_prepayment?: boolean | null
    is_commissionable?: boolean | null
    receipt_date?: string | null
    due_date?: string | null
    invoice_no?: string | null
}

function asNumber(input: number | string | null | undefined): number {
    if (input === null || input === undefined || input === '') return 0
    const parsed = Number(input)
    return Number.isFinite(parsed) ? parsed : 0
}

export function settlementStatusText(status?: string): string {
    switch ((status || '').toUpperCase()) {
        case 'UNSETTLED':
            return '未结清'
        case 'PARTIALLY_SETTLED':
            return '部分结清'
        case 'SETTLED':
            return '已结清'
        default:
            return '未知结清状态'
    }
}

function mapBillListItem(input: BackendBill): BillListItem {
    return {
        id: input.id,
        bill_no: input.bill_no || input.id,
        client_id: input.client_id,
        client_name: input.client_name || undefined,
        direction: input.direction || undefined,
        status: input.status || 'DRAFT',
        amount: asNumber(input.amount),
        balance: asNumber(input.balance),
        currency: input.currency || 'CNY',
        issue_date: input.bill_date || input.issue_date || undefined,
        bill_date: input.bill_date || undefined,
        due_date: input.due_date || undefined,
        days_past_due: input.days_past_due ?? undefined,
        aging_bucket: input.aging_bucket || undefined,
        is_overdue: input.is_overdue ?? false,
        is_bad_debt: input.is_bad_debt ?? false,
    }
}

function mapBillDetail(input: BackendBill): BillDetail {
    return {
        ...mapBillListItem(input),
        case_id: input.case_id || undefined,
        case_no: input.case_no || undefined,
        direction: input.direction || undefined,
        bill_date: input.bill_date || undefined,
        bad_debt_status: (input.bad_debt_status || 'NONE') as BadDebtStatus,
        bad_debt_substatus: input.bad_debt_substatus || undefined,
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
        bad_debt_voucher: input.bad_debt_voucher ? mapBadDebtVoucher(input.bad_debt_voucher) : null,
        bad_debt_recoveries: (input.bad_debt_recoveries || []).map(mapBadDebtRecovery),
        bad_debt_total_recovered:
            input.bad_debt_total_recovered != null ? asNumber(input.bad_debt_total_recovered) : 0,
        bad_debt_remaining_amount:
            input.bad_debt_remaining_amount != null ? asNumber(input.bad_debt_remaining_amount) : 0,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapBadDebtVoucher(input: BackendBadDebtVoucher): BillBadDebtVoucher {
    return {
        id: input.id,
        bill_id: input.bill_id,
        status: (input.status || 'OPEN') as BadDebtStatus,
        bad_debt_amount: asNumber(input.bad_debt_amount),
        recovered_amount: asNumber(input.recovered_amount),
        bad_debt_date: input.bad_debt_date || undefined,
        remark: input.remark || undefined,
    }
}

function mapBadDebtRecovery(input: BackendBadDebtRecovery): BillBadDebtRecovery {
    return {
        id: input.id,
        voucher_id: input.voucher_id,
        recovery_amount: asNumber(input.recovery_amount),
        recovery_date: input.recovery_date || undefined,
        remark: input.remark || undefined,
    }
}

function mapFeeOverviewGovPaymentItem(input: BackendFeeOverviewGovPaymentItem): FeeOverviewGovPaymentItem {
    return {
        gov_payment_id: input.gov_payment_id,
        pay_list_id: input.pay_list_id,
        case_id: input.case_id,
        case_no: input.case_no || undefined,
        app_no: input.app_no || undefined,
        patent_no: input.patent_no || undefined,
        fee_item_id: input.fee_item_id || undefined,
        fee_code: input.fee_code || undefined,
        fee_name: input.fee_name || undefined,
        year_no: input.year_no ?? undefined,
        planned_amt: asNumber(input.planned_amt),
        paid_amt: asNumber(input.paid_amt),
        currency: input.currency || 'CNY',
        list_no: input.list_no || undefined,
        voucher_no: input.voucher_no || undefined,
        invoice_no: input.invoice_no || undefined,
        planned_pay_date: input.planned_pay_date || undefined,
        paid_date: input.paid_date || undefined,
    }
}

function mapFeeOverviewCaseReceiptItem(input: BackendFeeOverviewCaseReceiptItem): FeeOverviewCaseReceiptItem {
    return {
        receipt_id: input.receipt_id,
        case_id: input.case_id,
        case_no: input.case_no || undefined,
        app_no: input.app_no || undefined,
        patent_no: input.patent_no || undefined,
        fee_code: input.fee_code || undefined,
        fee_name: input.fee_name || undefined,
        year_no: input.year_no ?? undefined,
        fee_type: input.fee_type || undefined,
        receivable_amt: asNumber(input.receivable_amt),
        received_amt: asNumber(input.received_amt),
        currency: input.currency || 'CNY',
        is_arrears: input.is_arrears ?? undefined,
        is_prepayment: input.is_prepayment ?? undefined,
        is_commissionable: input.is_commissionable ?? undefined,
        receipt_date: input.receipt_date || undefined,
        due_date: input.due_date || undefined,
        invoice_no: input.invoice_no || undefined,
    }
}

function mapPayment(
    input: BackendPayment,
    extras: Partial<PaymentListItem> = {}
): PaymentListItem {
    return {
        id: input.id,
        bill_id: input.bill_id || extras.bill_id,
        bill_no: input.bill_no || extras.bill_no,
        client_id: input.client_id,
        client_name: input.client_name || undefined,
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
        bill_no: input.bill_no || undefined,
        amount: asNumber(input.offset_amt),
        currency: 'CNY',
        offset_date: input.offset_date || undefined,
        is_reversed: input.is_reversed,
        reversed_at: input.reversed_at || undefined,
        created_at: input.created_at || input.offset_date || '',
    }
}

interface BackendFeeUnifiedQueryItem {
    record_type: string
    record_id: string
    case_id?: string | null
    biz_no?: string | null
    party_name?: string | null
    amount?: number | string | null
    currency?: string | null
    status?: string | null
    biz_date?: string | null
    remark?: string | null
}

function mapFeeUnifiedQueryItem(input: BackendFeeUnifiedQueryItem): FeeUnifiedQueryItem {
    return {
        record_type: input.record_type,
        record_id: input.record_id,
        case_id: input.case_id || undefined,
        biz_no: input.biz_no || undefined,
        party_name: input.party_name || undefined,
        amount: asNumber(input.amount),
        currency: input.currency || 'CNY',
        status: input.status || undefined,
        biz_date: input.biz_date || undefined,
        remark: input.remark || undefined,
    }
}

/**
 * Get paginated list of bills
 */
export async function getBills(params: BillListParams = {}): Promise<BillListResponse> {
    const {
        page = 1,
        page_size = 20,
        status,
        bill_status,
        client_id,
        currency,
        bill_date_from,
        bill_date_to,
        aging_bucket,
        is_overdue,
        is_bad_debt,
        bad_debt_status,
    } = params
    const response = await http.get<BackendBillListResponse>('/bills', {
        params: {
            page,
            page_size,
            status,
            bill_status,
            client_id,
            currency,
            bill_date_from,
            bill_date_to,
            aging_bucket,
            is_overdue,
            is_bad_debt,
            bad_debt_status,
        },
    })

    return {
        ...response.data,
        summary: {
            receivable_bill_count: asNumber(response.data.summary?.receivable_bill_count),
            receivable_amount: asNumber(response.data.summary?.receivable_amount),
            overdue_bill_count: asNumber(response.data.summary?.overdue_bill_count),
            overdue_amount: asNumber(response.data.summary?.overdue_amount),
            bad_debt_bill_count: asNumber(response.data.summary?.bad_debt_bill_count),
            bad_debt_amount: asNumber(response.data.summary?.bad_debt_amount),
            total_recovered_amount: asNumber(response.data.summary?.total_recovered_amount),
            remaining_bad_debt_balance: asNumber(response.data.summary?.remaining_bad_debt_balance),
            aging_buckets: (response.data.summary?.aging_buckets || []).map((bucket) => ({
                bucket: bucket.bucket,
                bill_count: asNumber(bucket.bill_count),
                amount: asNumber(bucket.amount),
            })),
        },
        bad_debt_bill_count: response.data.bad_debt_bill_count,
        bad_debt_amount: asNumber(response.data.bad_debt_amount),
        total_recovered_amount: asNumber(response.data.total_recovered_amount),
        remaining_bad_debt_balance: asNumber(response.data.remaining_bad_debt_balance),
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

export async function markBillBadDebt(
    billId: string,
    payload: BillBadDebtActionPayload
): Promise<BillDetail> {
    const response = await http.post<BackendBill>(`/bills/${billId}/bad-debt`, payload)
    return mapBillDetail(response.data)
}

export async function recoverBillBadDebt(
    billId: string,
    payload: BillBadDebtRecoveryPayload
): Promise<BillDetail> {
    const response = await http.post<BackendBill>(`/bills/${billId}/bad-debt/recover`, payload)
    return mapBillDetail(response.data)
}

// ============ Payments ============

/**
 * Get paginated list of payments
 */
export async function getPayments(params: PaymentListParams = {}): Promise<PaymentListResponse> {
    const {
        page = 1,
        page_size = 20,
        bill_id,
        client_id,
        prepayment_status,
        pay_date_from,
        pay_date_to,
        has_unapplied_only,
    } = params
    const response = await http.get<BackendPaymentListResponse>('/payments', {
        params: {
            page,
            page_size,
            bill_id,
            client_id,
            prepayment_status,
            pay_date_from,
            pay_date_to,
            has_unapplied_only,
        },
    })

    return {
        ...response.data,
        prepayment_count: asNumber(response.data.prepayment_count),
        prepayment_total_amount: asNumber(response.data.prepayment_total_amount),
        allocated_total_amount: asNumber(response.data.allocated_total_amount),
        remaining_prepayment_balance: asNumber(response.data.remaining_prepayment_balance),
        items: response.data.items.map((item) =>
            mapPayment(item, {
                bill_id: item.bill_id || bill_id,
                bill_no: item.bill_no || bill_id,
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
        bill_id: payload.bill_id || undefined,
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

// ============ Fee Unified Query ============

/**
 * Get unified fee query records with pagination and filters.
 */
export async function getFeeUnifiedQuery(
    params: FeeUnifiedQueryParams = {}
): Promise<FeeUnifiedQueryResponse> {
    const {
        page = 1,
        page_size = 20,
        record_type,
        case_id,
        biz_no,
        party_name,
        status,
        currency,
        date_range,
        amount_range,
    } = params
    const date_from = date_range?.[0]
    const date_to = date_range?.[1]
    const amount_from = amount_range?.[0]
    const amount_to = amount_range?.[1]

    const response = await http.get<Pagination<BackendFeeUnifiedQueryItem>>('/fee-unified-query', {
        params: {
            page,
            page_size,
            record_type,
            case_id,
            biz_no,
            party_name,
            status,
            currency,
            date_from,
            date_to,
            amount_from,
            amount_to,
        },
    })

    return {
        ...response.data,
        items: response.data.items.map(mapFeeUnifiedQueryItem),
    }
}

export async function getFeeOverviewGovPayments(
    params: FeeOverviewGovPaymentParams = {}
): Promise<FeeOverviewGovPaymentResponse> {
    const {
        page = 1,
        page_size = 20,
        case_no,
        app_no,
        patent_no,
        client_id,
        applicant_name,
        fee_type,
        paid_date_range,
    } = params

    const response = await http.get<Pagination<BackendFeeOverviewGovPaymentItem>>(
        '/fee-overview/gov-payments',
        {
            params: {
                page,
                page_size,
                case_no,
                app_no,
                patent_no,
                client_id,
                applicant_name,
                fee_type,
                paid_date_from: paid_date_range?.[0],
                paid_date_to: paid_date_range?.[1],
            },
        }
    )

    return {
        ...response.data,
        items: response.data.items.map(mapFeeOverviewGovPaymentItem),
    }
}

export async function getFeeOverviewCaseReceipts(
    params: FeeOverviewCaseReceiptParams = {}
): Promise<FeeOverviewCaseReceiptResponse> {
    const {
        page = 1,
        page_size = 20,
        case_no,
        app_no,
        patent_no,
        client_id,
        applicant_name,
        fee_type,
        receipt_date_range,
    } = params

    const response = await http.get<Pagination<BackendFeeOverviewCaseReceiptItem>>(
        '/fee-overview/case-receipts',
        {
            params: {
                page,
                page_size,
                case_no,
                app_no,
                patent_no,
                client_id,
                applicant_name,
                fee_type,
                receipt_date_from: receipt_date_range?.[0],
                receipt_date_to: receipt_date_range?.[1],
            },
        }
    )

    return {
        ...response.data,
        items: response.data.items.map(mapFeeOverviewCaseReceiptItem),
    }
}

// ============ Offsets ============

/**
 * List offsets with pagination and optional filters.
 */
export async function getOffsets(
    params: { page?: number; page_size?: number; bill_id?: string; is_reversed?: boolean } = {}
): Promise<Pagination<OffsetListItem>> {
    const response = await http.get<{
        items: BackendOffset[]
        page: number
        page_size: number
        total: number
    }>('/offsets', { params })
    return {
        items: response.data.items.map(mapOffset),
        page: response.data.page,
        page_size: response.data.page_size,
        total: response.data.total,
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
    bills?: {
        id: string
        bill_no?: string | null
        status?: string | null
        amount?: string | number | null
        balance?: string | number | null
        issue_date?: string | null
    }[]
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
        bills: (input.bills || []).map((bill) => ({
            id: bill.id,
            bill_no: bill.bill_no || bill.id,
            status: bill.status || 'DRAFT',
            amount: asNumber(bill.amount),
            balance: asNumber(bill.balance),
            issue_date: bill.issue_date || undefined,
        })),
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

export async function createCaseReceipt(payload: CaseReceiptCreate) {
    const { data } = await http.post('/case-receipts', payload)
    return data
}

export async function updateCaseReceipt(id: string, payload: CaseReceiptUpdate) {
    const { data } = await http.put(`/case-receipts/${id}`, payload)
    return data
}

export async function listCaseReceipts(params: Record<string, unknown> = {}): Promise<CaseReceiptListResponse> {
    const { data } = await http.get<CaseReceiptListResponse>('/case-receipts', { params })
    return data
}
