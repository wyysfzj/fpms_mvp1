import { http } from './http'
import type { Pagination } from './types'
import type {
    CommissionListParams,
    CommissionRecord,
    CommissionRule,
    CommissionRuleCreatePayload,
    CommissionRuleUpdatePayload,
    CommissionSettlement,
    CommissionSettlementCreatePayload,
    CommissionSettlementGenerateLinesResult,
    CommissionSettlementReportParams,
    CommissionSettlementReportResult,
} from './commission.types'

interface BackendCommissionRecord {
    id: number
    case_id: string
    agent_id?: string | null
    rule_id?: number | null
    fee_type?: string | null
    base_fee?: number | string | null
    s1_rate?: number | string | null
    s1_amount?: number | string | null
    s1_done?: boolean
    s2_rate?: number | string | null
    s2_amount?: number | string | null
    s2_done?: boolean
    wait_pay?: boolean
    force_settle?: boolean
    status?: string | null
    is_settleable?: boolean
    settleable_date?: string | null
    remark?: string | null
    created_at: string
    updated_at: string
}

interface BackendCommissionRule {
    id: number
    rule_name: string
    case_type?: string | null
    fee_type?: string | null
    flow_dir?: string | null
    patent_category?: string | null
    s1_rate?: number | string | null
    s2_rate?: number | string | null
    s1_fixed_amount?: number | string | null
    s2_fixed_amount?: number | string | null
    wait_pay?: boolean
    force_settle?: boolean
    enabled?: boolean
    effective_from?: string | null
    effective_to?: string | null
    remark?: string | null
    created_at: string
    updated_at: string
}

interface BackendCommissionSettlement {
    id: number
    settlement_no?: string | null
    agent_id?: string | null
    status?: string | null
    currency?: string | null
    period_from?: string | null
    period_to?: string | null
    line_count?: number | null
    total_amount?: number | string | null
    remark?: string | null
    created_at: string
    updated_at: string
}

interface BackendCommissionSettlementGenerateLinesResult {
    settlement_id: number
    line_count?: number | null
    total_amount?: number | string | null
    created_count?: number | null
    updated_count?: number | null
    status?: string | null
}

interface BackendCommissionSettlementReportResult {
    filters: {
        agent_id?: string | null
        case_id?: string | null
        currency?: string | null
        settlement_status?: string | null
        line_status?: string | null
        date_from?: string | null
        date_to?: string | null
        time_field?: 'line_created_at' | 'settleable_date' | 'settlement_period' | null
    }
    totals: {
        line_count?: number | null
        total_amount?: number | string | null
    }
    by_agent?: {
        agent_id?: string | null
        line_count?: number | null
        total_amount?: number | string | null
    }[]
    by_case?: {
        case_id?: string | null
        line_count?: number | null
        total_amount?: number | string | null
    }[]
    by_time?: {
        time_bucket?: string | null
        line_count?: number | null
        total_amount?: number | string | null
    }[]
    details?: {
        settlement_id: number
        settlement_no?: string | null
        commission_id: number
        agent_id?: string | null
        case_id: string
        amount?: number | string | null
        currency?: string | null
        line_status?: string | null
        settlement_status?: string | null
        s1_done?: boolean
        s2_done?: boolean
        is_settleable?: boolean
        settleable_date?: string | null
        period_from?: string | null
        period_to?: string | null
        created_at: string
    }[]
}

function asNumber(input: number | string | null | undefined): number {
    if (input === null || input === undefined || input === '') return 0
    const parsed = Number(input)
    return Number.isFinite(parsed) ? parsed : 0
}

function mapCommissionRecord(input: BackendCommissionRecord): CommissionRecord {
    return {
        id: input.id,
        case_id: input.case_id,
        agent_id: input.agent_id ?? undefined,
        rule_id: input.rule_id ?? undefined,
        fee_type: input.fee_type ?? undefined,
        base_fee: asNumber(input.base_fee),
        s1_rate: asNumber(input.s1_rate),
        s1_amount: asNumber(input.s1_amount),
        s1_done: input.s1_done ?? false,
        s2_rate: asNumber(input.s2_rate),
        s2_amount: asNumber(input.s2_amount),
        s2_done: input.s2_done ?? false,
        wait_pay: input.wait_pay ?? false,
        force_settle: input.force_settle ?? false,
        status: input.status ?? '',
        is_settleable: input.is_settleable ?? false,
        settleable_date: input.settleable_date ?? undefined,
        remark: input.remark ?? undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapCommissionRule(input: BackendCommissionRule): CommissionRule {
    return {
        id: input.id,
        rule_name: input.rule_name,
        case_type: input.case_type ?? undefined,
        fee_type: input.fee_type ?? undefined,
        flow_dir: input.flow_dir ?? undefined,
        patent_category: input.patent_category ?? undefined,
        s1_rate: asNumber(input.s1_rate),
        s2_rate: asNumber(input.s2_rate),
        s1_fixed_amount: asNumber(input.s1_fixed_amount),
        s2_fixed_amount: asNumber(input.s2_fixed_amount),
        wait_pay: input.wait_pay ?? false,
        force_settle: input.force_settle ?? false,
        enabled: input.enabled ?? true,
        effective_from: input.effective_from ?? undefined,
        effective_to: input.effective_to ?? undefined,
        remark: input.remark ?? undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapCommissionSettlement(input: BackendCommissionSettlement): CommissionSettlement {
    return {
        id: input.id,
        settlement_no: input.settlement_no ?? undefined,
        agent_id: input.agent_id ?? undefined,
        status: input.status ?? 'DRAFT',
        currency: input.currency ?? 'CNY',
        period_from: input.period_from ?? undefined,
        period_to: input.period_to ?? undefined,
        line_count: input.line_count ?? 0,
        total_amount: asNumber(input.total_amount),
        remark: input.remark ?? undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
    }
}

function mapCommissionSettlementReport(
    input: BackendCommissionSettlementReportResult,
): CommissionSettlementReportResult {
    return {
        filters: {
            agent_id: input.filters.agent_id ?? undefined,
            case_id: input.filters.case_id ?? undefined,
            currency: input.filters.currency ?? undefined,
            settlement_status: input.filters.settlement_status ?? undefined,
            line_status: input.filters.line_status ?? undefined,
            date_from: input.filters.date_from ?? undefined,
            date_to: input.filters.date_to ?? undefined,
            time_field: input.filters.time_field ?? 'line_created_at',
        },
        totals: {
            line_count: input.totals.line_count ?? 0,
            total_amount: asNumber(input.totals.total_amount),
        },
        by_agent: (input.by_agent || []).map((item) => ({
            agent_id: item.agent_id ?? undefined,
            line_count: item.line_count ?? 0,
            total_amount: asNumber(item.total_amount),
        })),
        by_case: (input.by_case || []).map((item) => ({
            case_id: item.case_id ?? undefined,
            line_count: item.line_count ?? 0,
            total_amount: asNumber(item.total_amount),
        })),
        by_time: (input.by_time || []).map((item) => ({
            time_bucket: item.time_bucket ?? 'UNKNOWN',
            line_count: item.line_count ?? 0,
            total_amount: asNumber(item.total_amount),
        })),
        details: (input.details || []).map((item) => ({
            settlement_id: item.settlement_id,
            settlement_no: item.settlement_no ?? undefined,
            commission_id: item.commission_id,
            agent_id: item.agent_id ?? undefined,
            case_id: item.case_id,
            amount: asNumber(item.amount),
            currency: item.currency ?? undefined,
            line_status: item.line_status ?? undefined,
            settlement_status: item.settlement_status ?? undefined,
            s1_done: item.s1_done ?? false,
            s2_done: item.s2_done ?? false,
            is_settleable: item.is_settleable ?? false,
            settleable_date: item.settleable_date ?? undefined,
            period_from: item.period_from ?? undefined,
            period_to: item.period_to ?? undefined,
            created_at: item.created_at,
        })),
    }
}

export async function getCommission(
    params: CommissionListParams = {},
): Promise<Pagination<CommissionRecord>> {
    const response = await http.get<Pagination<BackendCommissionRecord>>('/commission', { params })

    return {
        ...response.data,
        items: response.data.items.map(mapCommissionRecord),
    }
}

export async function getCommissionRules(
    params: {
        enabled?: boolean
        case_type?: string
        fee_type?: string
        q?: string
        page?: number
        page_size?: number
    } = {},
): Promise<Pagination<CommissionRule>> {
    const response = await http.get<Pagination<BackendCommissionRule>>('/commission/rules', { params })

    return {
        ...response.data,
        items: response.data.items.map(mapCommissionRule),
    }
}

export async function createCommissionRule(
    payload: CommissionRuleCreatePayload,
): Promise<CommissionRule> {
    const response = await http.post<BackendCommissionRule>('/commission/rules', payload)
    return mapCommissionRule(response.data)
}

export async function updateCommissionRule(
    ruleId: number,
    payload: CommissionRuleUpdatePayload,
): Promise<CommissionRule> {
    const response = await http.put<BackendCommissionRule>(`/commission/rules/${ruleId}`, payload)
    return mapCommissionRule(response.data)
}

export async function createCommissionSettlement(
    payload: CommissionSettlementCreatePayload,
): Promise<CommissionSettlement> {
    const response = await http.post<BackendCommissionSettlement>('/commission/settlements', payload)
    return mapCommissionSettlement(response.data)
}

export async function generateCommissionSettlementLines(
    id: number,
): Promise<CommissionSettlementGenerateLinesResult> {
    const response = await http.post<BackendCommissionSettlementGenerateLinesResult>(
        `/commission/settlements/${id}/generate-lines`,
    )

    return {
        settlement_id: response.data.settlement_id,
        line_count: response.data.line_count ?? 0,
        total_amount: asNumber(response.data.total_amount),
        created_count: response.data.created_count ?? 0,
        updated_count: response.data.updated_count ?? 0,
        status: response.data.status ?? 'DRAFT',
    }
}

export async function getCommissionSettlementReport(
    params: CommissionSettlementReportParams = {},
): Promise<CommissionSettlementReportResult> {
    const response = await http.get<BackendCommissionSettlementReportResult>(
        '/commission/reports/settlement',
        { params },
    )
    return mapCommissionSettlementReport(response.data)
}
