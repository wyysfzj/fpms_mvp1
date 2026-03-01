import { mapFieldErrors } from './errors'
import { http } from './http'
import type {
    GovPaymentRegisterPayload,
    GovPaymentRegisterResult,
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
            return '请至少提供一条费用项编号。'
        case 'PAY_LIST_SCOPE_INVALID':
            return '费用项范围不合法，请确认客户与币种一致。'
        case 'FEE_ITEM_NOT_FOUND':
            return '费用项不存在，请检查后重试。'
        case 'PAY_LIST_NOT_FOUND':
            return '官费清单不存在，请检查后重试。'
        case 'GOV_PAYMENT_INVALID':
            return '缴费金额不合法，请输入大于 0 的金额。'
        case 'GOV_PAYMENT_DUPLICATE':
            return '该费用项已登记官方缴费，不能重复提交。'
        case 'VALIDATION_ERROR':
            return '参数校验失败，请检查输入后重试。'
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
