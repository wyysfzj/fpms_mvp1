import { mapFieldErrors } from './errors'
import { http } from './http'
import type {
    BadDebtBillResult,
    CollectionsApiError,
    CollectionsErrorCategory,
    DunningBatchListItem,
    DunningDetail,
    DunningDetailLine,
    DunningGenerateBatch,
    DunningGenerateBatchLine,
    DunningGeneratePayload,
    DunningGenerateResult,
    DunningGenerateSummary,
    DunningListParams,
} from './collections.types'
import type { ApiError, Pagination } from './types'

interface BackendDunningBatchListItem {
    id: number
    dunning_no: string | null
    client_id: string
    round_no: number
    to_date: string | null
    currency: string
    total_amount: number | string | null
    status: string
    sent_date: string | null
    remark: string | null
    created_at: string
    updated_at: string
}

interface BackendDunningGenerateSummary {
    to_date: string
    eligible_bills: number
    groups: number
    created: number
    reused: number
    batches: number
}

interface BackendDunningGenerateBatchLine {
    id: number
    line_no: number
    bill_id: string
    bill_no_snapshot: string | null
    due_date_snapshot: string | null
    bill_status_snapshot: string | null
    outstanding_amount: number | string | null
    currency_snapshot: string | null
}

interface BackendDunningGenerateBatch {
    id: number
    dunning_no: string | null
    client_id: string
    round_no: number
    to_date: string | null
    currency: string
    total_amount: number | string | null
    status: string
    reused: boolean
    line_count: number
    lines: BackendDunningGenerateBatchLine[]
}

interface BackendDunningGenerateResult {
    summary: BackendDunningGenerateSummary
    batches: BackendDunningGenerateBatch[]
}

interface BackendBadDebtBillResult {
    id: string
    bill_no: string | null
    client_id: string
    currency: string
    status: string
    bill_date: string | null
    due_date: string | null
    amount: number | string | null
    balance: number | string | null
    updated_at: string
}

interface BackendDunningDetailLine {
    id: number
    line_no: number
    bill_id: string
    bill_no_snapshot: string | null
    due_date_snapshot: string | null
    bill_status_snapshot: string | null
    outstanding_amount: number | string | null
    currency_snapshot: string | null
    remark: string | null
}

interface BackendDunningDetail {
    id: number
    dunning_no: string | null
    client_id: string
    round_no: number
    to_date: string | null
    currency: string
    total_amount: number | string | null
    status: string
    sent_date: string | null
    remark: string | null
    created_at: string
    updated_at: string
    line_count: number
    lines: BackendDunningDetailLine[]
    summary: {
        line_count: number
        bill_count: number
        bad_debt_line_count: number
    }
}

function asNumber(input: number | string | null | undefined): number {
    if (input === null || input === undefined || input === '') return 0
    const parsed = Number(input)
    return Number.isFinite(parsed) ? parsed : 0
}

function mapDunningBatchListItem(input: BackendDunningBatchListItem): DunningBatchListItem {
    return {
        id: input.id,
        dunning_no: input.dunning_no,
        client_id: input.client_id,
        round_no: input.round_no,
        to_date: input.to_date,
        currency: input.currency,
        total_amount: asNumber(input.total_amount),
        status: input.status,
        sent_date: input.sent_date,
        remark: input.remark,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapDunningGenerateSummary(input: BackendDunningGenerateSummary): DunningGenerateSummary {
    return {
        to_date: input.to_date,
        eligible_bills: input.eligible_bills,
        groups: input.groups,
        created: input.created,
        reused: input.reused,
        batches: input.batches,
    }
}

function mapDunningGenerateBatchLine(input: BackendDunningGenerateBatchLine): DunningGenerateBatchLine {
    return {
        id: input.id,
        line_no: input.line_no,
        bill_id: input.bill_id,
        bill_no_snapshot: input.bill_no_snapshot,
        due_date_snapshot: input.due_date_snapshot,
        bill_status_snapshot: input.bill_status_snapshot,
        outstanding_amount: asNumber(input.outstanding_amount),
        currency_snapshot: input.currency_snapshot,
    }
}

function mapDunningGenerateBatch(input: BackendDunningGenerateBatch): DunningGenerateBatch {
    return {
        id: input.id,
        dunning_no: input.dunning_no,
        client_id: input.client_id,
        round_no: input.round_no,
        to_date: input.to_date,
        currency: input.currency,
        total_amount: asNumber(input.total_amount),
        status: input.status,
        reused: input.reused,
        line_count: input.line_count,
        lines: input.lines.map(mapDunningGenerateBatchLine),
    }
}

function mapBadDebtBillResult(input: BackendBadDebtBillResult): BadDebtBillResult {
    return {
        id: input.id,
        bill_no: input.bill_no,
        client_id: input.client_id,
        currency: input.currency,
        status: input.status,
        bill_date: input.bill_date,
        due_date: input.due_date,
        amount: asNumber(input.amount),
        balance: asNumber(input.balance),
        updated_at: input.updated_at,
    }
}

function isApiError(error: unknown): error is ApiError {
    if (!error || typeof error !== 'object') return false
    const candidate = error as Partial<ApiError>
    return (
        typeof candidate.status === 'number'
        && typeof candidate.code === 'string'
        && typeof candidate.message === 'string'
    )
}

function resolveCollectionsErrorCategory(status: number): CollectionsErrorCategory {
    if (status === 401) return 'unauthenticated'
    if (status === 403) return 'permission_denied'
    if (status === 422) return 'validation'
    if (status === 404) return 'not_found'
    if (status === 409) return 'conflict'
    if (status === 400) return 'business'
    return 'unknown'
}

/**
 * Map normalized ApiError into collections-friendly categories.
 */
export function mapCollectionsError(error: unknown): CollectionsApiError {
    if (!isApiError(error)) {
        return {
            status: 0,
            code: 'UNKNOWN_ERROR',
            message: 'UNKNOWN_ERROR',
            category: 'unknown',
        }
    }

    const category = resolveCollectionsErrorCategory(error.status)
    const mapped: CollectionsApiError = {
        status: error.status,
        code: error.code,
        message: error.message,
        details: error.details,
        requestId: error.requestId,
        category,
    }

    if (category === 'validation') {
        const fieldErrors = mapFieldErrors(error.details)
        if (fieldErrors.size > 0) {
            mapped.field_errors = fieldErrors
        }
    }

    return mapped
}

function mapDunningDetailLine(input: BackendDunningDetailLine): DunningDetailLine {
    return {
        id: input.id,
        line_no: input.line_no,
        bill_id: input.bill_id,
        bill_no_snapshot: input.bill_no_snapshot,
        due_date_snapshot: input.due_date_snapshot,
        bill_status_snapshot: input.bill_status_snapshot,
        outstanding_amount: asNumber(input.outstanding_amount),
        currency_snapshot: input.currency_snapshot,
        remark: input.remark || undefined,
    }
}

function mapDunningDetail(input: BackendDunningDetail): DunningDetail {
    return {
        id: input.id,
        dunning_no: input.dunning_no,
        client_id: input.client_id,
        round_no: input.round_no,
        to_date: input.to_date,
        currency: input.currency,
        total_amount: asNumber(input.total_amount),
        status: input.status,
        sent_date: input.sent_date,
        remark: input.remark,
        created_at: input.created_at,
        updated_at: input.updated_at,
        line_count: input.line_count,
        summary: input.summary,
        lines: input.lines.map(mapDunningDetailLine),
    }
}

export async function getDunning(params: DunningListParams = {}): Promise<Pagination<DunningBatchListItem>> {
    const {
        round_no,
        status,
        client_id,
        page = 1,
        page_size = 20,
    } = params
    const response = await http.get<Pagination<BackendDunningBatchListItem>>('/dunning', {
        params: {
            round_no,
            status,
            client_id,
            page,
            page_size,
        },
    })

    return {
        ...response.data,
        items: response.data.items.map(mapDunningBatchListItem),
    }
}

export async function generateDunning(payload: DunningGeneratePayload): Promise<DunningGenerateResult> {
    const response = await http.post<BackendDunningGenerateResult>('/dunning', {
        to_date: payload.to_date,
        client_id: payload.client_id,
        client_ids: payload.client_ids,
        include_statuses: payload.include_statuses,
        exclude_statuses: payload.exclude_statuses,
        strict_conflict: payload.strict_conflict,
    })

    return {
        summary: mapDunningGenerateSummary(response.data.summary),
        batches: response.data.batches.map(mapDunningGenerateBatch),
    }
}

export async function markBillBadDebt(billId: string): Promise<BadDebtBillResult> {
    const response = await http.post<BackendBadDebtBillResult>(`/bills/${billId}/bad-debt`)
    return mapBadDebtBillResult(response.data)
}

export async function restoreBillBadDebt(billId: string): Promise<BadDebtBillResult> {
    const response = await http.post<BackendBadDebtBillResult>(`/bills/${billId}/bad-debt/restore`)
    return mapBadDebtBillResult(response.data)
}

export async function getDunningDetail(id: number): Promise<DunningDetail> {
    const response = await http.get<BackendDunningDetail>(`/dunning/${id}`)
    return mapDunningDetail(response.data)
}
