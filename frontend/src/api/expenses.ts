import { mapFieldErrors } from './errors'
import { http } from './http'
import type {
    ExpenseApiAction,
    ExpenseApiError,
    ExpenseErrorCategory,
    ExpenseCreatePayload,
    ExpenseGrossProfitStat,
    ExpenseGroupedStat,
    ExpenseItem,
    ExpenseListParams,
    ExpenseListResponse,
    ExpenseStats,
} from './expenses.types'
import type { ApiError } from './types'

interface BackendExpenseItem {
    id: number
    expense_no: string | null
    case_id: string | null
    worker_id: string | null
    category: string
    expense_date: string | null
    amount: number | string
    currency: string
    status: string
    remark: string | null
    created_at: string
    updated_at: string
}

interface BackendExpenseStats {
    count_by_category: Record<string, number | string>
    sum_by_category: Record<string, number | string>
    count_total: number | string
    sum_total: number | string
    case_amounts?: BackendExpenseGroupedStat[]
    client_amounts?: BackendExpenseGroupedStat[]
    gross_profit_amounts?: BackendExpenseGrossProfitStat[]
}

interface BackendExpenseGroupedStat {
    key: string
    label: string
    expense_count: number | string
    total_amount: number | string
}

interface BackendExpenseGrossProfitStat {
    key: string
    label: string
    currency: string
    expense_total: number | string
    received_total: number | string
    gross_profit_total: number | string
}

interface BackendExpenseListResponse {
    items: BackendExpenseItem[]
    page: number
    page_size: number
    total: number
    stats?: BackendExpenseStats
}

function asNumber(input: number | string | null | undefined): number {
    if (input === null || input === undefined || input === '') return 0
    const parsed = Number(input)
    return Number.isFinite(parsed) ? parsed : 0
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

function mapExpenseItem(input: BackendExpenseItem): ExpenseItem {
    return {
        id: input.id,
        expense_no: input.expense_no,
        case_id: input.case_id,
        worker_id: input.worker_id,
        category: input.category,
        expense_date: input.expense_date,
        amount: asNumber(input.amount),
        currency: input.currency,
        status: input.status,
        remark: input.remark,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapExpenseStats(input: BackendExpenseStats): ExpenseStats {
    const count_by_category = Object.fromEntries(
        Object.entries(input.count_by_category || {}).map(([key, value]) => [key, asNumber(value)]),
    )

    const sum_by_category = Object.fromEntries(
        Object.entries(input.sum_by_category || {}).map(([key, value]) => [key, asNumber(value)]),
    )

    const mapGroupedStats = (rows: BackendExpenseGroupedStat[] | undefined): ExpenseGroupedStat[] =>
        (rows || []).map((row) => ({
            key: row.key,
            label: row.label,
            expense_count: asNumber(row.expense_count),
            total_amount: asNumber(row.total_amount),
        }))

    const mapGrossProfitStats = (
        rows: BackendExpenseGrossProfitStat[] | undefined,
    ): ExpenseGrossProfitStat[] =>
        (rows || []).map((row) => ({
            key: row.key,
            label: row.label,
            currency: row.currency,
            expense_total: asNumber(row.expense_total),
            received_total: asNumber(row.received_total),
            gross_profit_total: asNumber(row.gross_profit_total),
        }))

    return {
        count_by_category,
        sum_by_category,
        count_total: asNumber(input.count_total),
        sum_total: asNumber(input.sum_total),
        case_amounts: mapGroupedStats(input.case_amounts),
        client_amounts: mapGroupedStats(input.client_amounts),
        gross_profit_amounts: mapGrossProfitStats(input.gross_profit_amounts),
    }
}

function resolveExpenseErrorCategory(status: number): ExpenseErrorCategory {
    if (status === 401) return 'unauthenticated'
    if (status === 403) return 'permission_denied'
    if (status === 422) return 'validation'
    if (status === 404) return 'not_found'
    if (status === 409) return 'conflict'
    if (status === 400) return 'business'
    return 'unknown'
}

function resolveExpenseErrorMessage(error: ApiError, action: ExpenseApiAction): string {
    const code = error.code.toUpperCase()

    if (code === 'CASE_NOT_FOUND') {
        return '关联案件或项目不存在，请确认后重试。'
    }

    if (code === 'EXPENSE_INVALID') {
        return action === 'create'
            ? '支出数据不合法，请检查类别、日期与金额后重试。'
            : '筛选条件不合法，请调整后重试。'
    }

    if (code === 'PERMISSION_DENIED') {
        return '当前账号没有支出模块权限，请联系管理员。'
    }

    if (code === 'UNAUTHENTICATED') {
        return '登录状态已失效，请重新登录。'
    }

    if (error.status === 401) return '登录状态已失效，请重新登录。'
    if (error.status === 403) return '当前账号没有支出模块权限，请联系管理员。'
    if (error.status === 404) return '未找到相关支出数据或关联案件。'
    if (error.status === 409) return '当前操作存在冲突，请刷新后重试。'
    if (error.status === 422) return '提交数据校验失败，请检查输入内容。'
    if (error.status === 400) {
        return action === 'create'
            ? '支出录入参数有误，请检查后重试。'
            : '筛选参数有误，请检查后重试。'
    }

    return action === 'create'
        ? '支出录入失败，请稍后重试。'
        : '支出列表加载失败，请稍后重试。'
}

function buildExpenseListQuery(params: ExpenseListParams): Record<string, unknown> {
    const query: Record<string, unknown> = {
        page: params.page ?? 1,
        page_size: params.page_size ?? 20,
        include_stats: params.include_stats ?? true,
    }

    const caseId = params.case_id?.trim()
    if (caseId) query.case_id = caseId

    const workerId = params.worker_id?.trim()
    if (workerId) query.worker_id = workerId

    const category = params.category?.trim()
    if (category) query.category = category

    const dateFrom = params.date_from?.trim()
    if (dateFrom) query.date_from = dateFrom

    const dateTo = params.date_to?.trim()
    if (dateTo) query.date_to = dateTo

    const currency = params.currency?.trim()
    if (currency) query.currency = currency

    const status = params.status?.trim()
    if (status) query.status = status

    const q = params.q?.trim()
    if (q) query.q = q

    return query
}

function toCreatePayload(payload: ExpenseCreatePayload): Record<string, unknown> {
    return {
        case_id: payload.case_id.trim(),
        ...(payload.worker_id?.trim() ? { worker_id: payload.worker_id.trim() } : {}),
        category: payload.category,
        expense_date: payload.expense_date,
        amount: payload.amount,
        ...(payload.client_id?.trim() ? { client_id: payload.client_id.trim() } : {}),
        ...(payload.expense_no?.trim() ? { expense_no: payload.expense_no.trim() } : {}),
        ...(payload.vendor_name?.trim() ? { vendor_name: payload.vendor_name.trim() } : {}),
        ...(payload.currency?.trim() ? { currency: payload.currency.trim().toUpperCase() } : {}),
        ...(payload.tax_amount !== undefined ? { tax_amount: payload.tax_amount } : {}),
        ...(payload.remark?.trim() ? { remark: payload.remark.trim() } : {}),
    }
}

export function mapExpenseError(error: unknown, action: ExpenseApiAction): ExpenseApiError {
    if (!isApiError(error)) {
        return {
            status: 0,
            code: 'UNKNOWN_ERROR',
            message: action === 'create'
                ? '网络异常，支出录入失败，请稍后重试。'
                : '网络异常，支出列表加载失败，请稍后重试。',
            category: 'unknown',
        }
    }

    const category = resolveExpenseErrorCategory(error.status)
    const mapped: ExpenseApiError = {
        status: error.status,
        code: error.code,
        message: resolveExpenseErrorMessage(error, action),
        details: error.details,
        requestId: error.requestId,
        category,
    }

    if ((category === 'validation' || category === 'business') && error.details) {
        const fieldErrors = mapFieldErrors(error.details)
        if (fieldErrors.size > 0) {
            mapped.field_errors = fieldErrors
        }
    }

    return mapped
}

export async function getExpenses(params: ExpenseListParams = {}): Promise<ExpenseListResponse> {
    try {
        const response = await http.get<BackendExpenseListResponse>('/expenses', {
            params: buildExpenseListQuery(params),
        })

        return {
            items: response.data.items.map(mapExpenseItem),
            page: response.data.page,
            page_size: response.data.page_size,
            total: response.data.total,
            ...(response.data.stats ? { stats: mapExpenseStats(response.data.stats) } : {}),
        }
    } catch (error) {
        throw mapExpenseError(error, 'list')
    }
}

export async function createExpense(payload: ExpenseCreatePayload): Promise<ExpenseItem> {
    try {
        const response = await http.post<BackendExpenseItem>('/expenses', toCreatePayload(payload))
        return mapExpenseItem(response.data)
    } catch (error) {
        throw mapExpenseError(error, 'create')
    }
}
