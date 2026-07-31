import { mapFieldErrors } from './errors'
import { http } from './http'
import type {
    GovPaymentRegisterPayload,
    GovPaymentRegisterResult,
    HistoricalPayListCreatePayload,
    HistoricalPayListCreateResult,
    ManualGovPaymentCreatePayload,
    ManualGovPaymentCreateResult,
    PayListDetailResult,
    PayListListResult,
    PayListMarkPaidPayload,
    PayListMarkPaidResult,
    PayListQuery,
    PayListExportArtifactInfo,
    PayListInternalArtifactInfo,
    PayListOfficialEvidenceInfo,
    PayListOfficialWorkbookInfo,
    GovPaymentsApiError,
    GovPaymentsErrorCategory,
    PayListCreatePayload,
    PayListCreateResult,
} from './govPayments.types'
import type { ApiError } from './types'

interface BackendPayListCreateResult {
    summary: {
        requested: number
        success: number
        failed: number
        pay_list_created: boolean
    }
    pay_list: {
        id: number
        pay_list_no: string | null
        client_id: string
        currency: string
        status: string
        planned_pay_date: string | null
        total_amount: number | string | null
    } | null
    success: {
        fee_item_id: string
        case_id: string
        amount: number | string | null
        currency: string
        pay_list_id: number
    }[]
    failed: {
        fee_item_id: string
        code: string
        message: string
        status_code: number
    }[]
}

interface BackendGovPaymentRegisterResult {
    gov_payment: {
        id: number
        pay_list_id: number
        case_id: string
        fee_item_id: string
        status: string
        currency: string
        paid_date: string | null
        paid_amount: number | string | null
        official_receipt_no: string | null
        remark: string | null
    }
    pay_list: {
        id: number
        pay_list_no: string | null
        status: string
        paid_date: string | null
        total_amount: number | string | null
        currency: string
        client_id: string
    }
}

interface BackendPayListListResult {
    items: {
        id: number
        pay_list_no: string | null
        client_id: string
        client_name: string | null
        currency: string
        status: string
        planned_pay_date: string | null
        paid_date: string | null
        total_amount: number | string | null
        remark: string | null
        created_at: string
        updated_at: string
        created_by: string | null
        updated_by: string | null
    }[]
    page: number
    page_size: number
    total: number
}

interface BackendPayListDetailResult {
    pay_list: {
        id: number
        pay_list_no: string | null
        client_id: string
        currency: string
        status: string
        planned_pay_date: string | null
        paid_date: string | null
        total_amount: number | string | null
        remark: string | null
        created_at: string
        updated_at: string
        created_by: string | null
        updated_by: string | null
    }
    gov_payments: {
        id: number
        pay_list_id: number
        case_id: string
        case_no?: string | null
        fee_item_id: string | null
        status: string
        currency: string
        paid_date: string | null
        paid_amount: number | string | null
        official_receipt_no: string | null
        remark: string | null
    }[]
    export_artifacts?: PayListExportArtifactInfo[]
    official_workbook?: PayListOfficialWorkbookInfo
}

interface BackendHistoricalPayListCreateResult {
    id: number
    pay_list_no: string | null
    client_id: string
    currency: string
    status: string
    planned_pay_date: string | null
    paid_date: string | null
    total_amount: number | string | null
    remark: string | null
}

interface BackendPayListMarkPaidResult {
    pay_list: {
        id: number
        pay_list_no: string | null
        client_id: string
        currency: string
        status: string
        planned_pay_date?: string | null
        paid_date: string | null
        total_amount: number | string | null
        remark: string | null
        updated_by: string | null
    }
}

interface BackendManualGovPaymentCreateResult {
    gov_payment: {
        id: number
        pay_list_id: number
        case_id: string
        fee_item_id: string | null
        status: string
        currency: string
        paid_date: string | null
        paid_amount: number | string | null
        official_receipt_no: string | null
        remark: string | null
    }
    pay_list: {
        id: number
        pay_list_no: string | null
        client_id: string
        currency: string
        status: string
        planned_pay_date?: string | null
        paid_date: string | null
        total_amount: number | string | null
    }
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

function resolveGovPaymentsErrorCategory(status: number): GovPaymentsErrorCategory {
    if (status === 401) return 'unauthenticated'
    if (status === 403) return 'permission_denied'
    if (status === 422) return 'validation'
    if (status === 404) return 'not_found'
    if (status === 409) return 'conflict'
    if (status === 400) return 'business'
    return 'unknown'
}

function mapGovPaymentsErrorMessage(status: number, code: string): string {
    switch (code) {
        case 'FEE_ITEM_REQUIRED':
            return '系统未带入费用项编号，请从官费清单回执入口重新进入后再提交。'
        case 'PAY_LIST_SCOPE_INVALID':
            return '当前清单与费用项不匹配，请返回回执页重新选择。'
        case 'FEE_ITEM_NOT_FOUND':
            return '费用项不存在，请返回回执页后重试。'
        case 'PAY_LIST_NOT_FOUND':
            return '官费清单不存在，请返回回执页后重试。'
        case 'CASE_NOT_FOUND':
            return '案件不存在，请检查后重试。'
        case 'CASE_REQUIRED':
            return '案件编号为必填项。'
        case 'GOV_PAYMENT_INVALID':
            return '缴费金额必须大于 0，请检查后重试。'
        case 'GOV_PAYMENT_DUPLICATE':
            return '该费用项的官方缴费已经登记过，不能重复提交。'
        case 'PAY_LIST_STATE_CONFLICT':
            return '当前官费清单状态不允许执行此操作。'
        case 'VALIDATION_ERROR':
            return '请求参数校验失败，请检查自动带入信息后重试。'
        default:
            if (status === 400) return '业务校验失败，请检查输入后重试。'
            if (status === 401) return '登录已失效，请重新登录。'
            if (status === 403) return '无权限执行该操作。'
            if (status === 404) return '目标资源不存在，请确认后重试。'
            if (status === 409) return '数据冲突，当前请求无法完成。'
            if (status === 422) return '请求参数不符合要求，请检查后重试。'
            return '请求失败，请稍后重试。'
    }
}

export function mapGovPaymentsError(error: unknown): GovPaymentsApiError {
    if (!isApiError(error)) {
        return {
            status: 0,
            code: 'UNKNOWN_ERROR',
            message: '网络或服务异常，请稍后重试。',
            category: 'unknown',
        }
    }

    const category = resolveGovPaymentsErrorCategory(error.status)
    const mapped: GovPaymentsApiError = {
        status: error.status,
        code: error.code,
        message: mapGovPaymentsErrorMessage(error.status, error.code),
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

export async function createPayListFromFeeItems(
    payload: PayListCreatePayload,
): Promise<PayListCreateResult> {
    const response = await http.post<BackendPayListCreateResult>('/pay-lists/from-fee-items', {
        fee_item_ids: payload.fee_item_ids,
        planned_pay_date: payload.planned_pay_date,
        remark: payload.remark,
    })

    return {
        summary: response.data.summary,
        pay_list: response.data.pay_list
            ? {
                ...response.data.pay_list,
                total_amount: asNumber(response.data.pay_list.total_amount),
                paid_date: null,
            }
            : null,
        success: response.data.success.map((item) => ({
            ...item,
            amount: asNumber(item.amount),
        })),
        failed: response.data.failed,
    }
}

export async function registerGovPayment(
    payload: GovPaymentRegisterPayload,
): Promise<GovPaymentRegisterResult> {
    const response = await http.post<BackendGovPaymentRegisterResult>('/gov-payments', {
        pay_list_id: payload.pay_list_id,
        fee_item_id: payload.fee_item_id,
        paid_date: payload.paid_date,
        paid_amount: payload.paid_amount,
        official_receipt_no: payload.official_receipt_no,
        remark: payload.remark,
    })

    return {
        gov_payment: {
            ...response.data.gov_payment,
            paid_amount: asNumber(response.data.gov_payment.paid_amount),
        },
        pay_list: {
            ...response.data.pay_list,
            planned_pay_date: null,
            total_amount: asNumber(response.data.pay_list.total_amount),
        },
    }
}

export async function listPayLists(
    query: PayListQuery = {},
): Promise<PayListListResult> {
    const response = await http.get<BackendPayListListResult>('/pay-lists', {
        params: query,
    })

    return {
        ...response.data,
        items: response.data.items.map((item) => ({
            ...item,
            total_amount: asNumber(item.total_amount),
        })),
    }
}

export async function getPayListDetail(payListId: number): Promise<PayListDetailResult> {
    const response = await http.get<BackendPayListDetailResult>(`/pay-lists/${payListId}`)
    const payment = response.data.gov_payments.map((item) => ({
        ...item,
        paid_amount: asNumber(item.paid_amount),
    }))

    return {
        pay_list: {
            ...response.data.pay_list,
            total_amount: asNumber(response.data.pay_list.total_amount),
        },
        gov_payments: payment,
        payment,
        ...(response.data.export_artifacts === undefined
            ? {}
            : {
                  internal_artifacts: response.data.export_artifacts.filter(
                      (artifact): artifact is PayListInternalArtifactInfo =>
                          artifact.kind === 'INTERNAL_XLSX',
                  ),
                  official_evidence: response.data.export_artifacts.filter(
                      (artifact): artifact is PayListOfficialEvidenceInfo =>
                          artifact.kind === 'OFFICIAL_XLSM',
                  ),
              }),
        ...(response.data.official_workbook === undefined
            ? {}
            : { official_workbook: response.data.official_workbook }),
    }
}

export async function createHistoricalPayList(
    payload: HistoricalPayListCreatePayload,
): Promise<HistoricalPayListCreateResult> {
    const response = await http.post<BackendHistoricalPayListCreateResult>('/pay-lists', payload)

    return {
        ...response.data,
        total_amount: asNumber(response.data.total_amount),
    }
}

export async function exportPayList(payListId: number): Promise<Blob> {
    const response = await http.post<Blob>(`/pay-lists/${payListId}/export`, undefined, {
        responseType: 'blob',
    })
    return response.data
}

export async function markPayListPaid(
    payListId: number,
    payload: PayListMarkPaidPayload,
): Promise<PayListMarkPaidResult> {
    const response = await http.post<BackendPayListMarkPaidResult>(
        `/pay-lists/${payListId}/mark-paid`,
        payload,
    )

    return {
        pay_list: {
            ...response.data.pay_list,
            planned_pay_date: response.data.pay_list.planned_pay_date ?? null,
            total_amount: asNumber(response.data.pay_list.total_amount),
        },
    }
}

export async function addManualGovPayment(
    payListId: number,
    payload: ManualGovPaymentCreatePayload,
): Promise<ManualGovPaymentCreateResult> {
    const response = await http.post<BackendManualGovPaymentCreateResult>(
        `/pay-lists/${payListId}/manual-items`,
        {
            case_id: payload.case_id,
            fee_item_id: payload.fee_item_id ?? undefined,
            paid_date: payload.paid_date,
            paid_amount: payload.paid_amount,
            official_receipt_no: payload.official_receipt_no,
            remark: payload.remark,
        },
    )

    return {
        gov_payment: {
            ...response.data.gov_payment,
            paid_amount: asNumber(response.data.gov_payment.paid_amount),
        },
        pay_list: {
            ...response.data.pay_list,
            total_amount: asNumber(response.data.pay_list.total_amount),
            planned_pay_date: null,
        },
    }
}
