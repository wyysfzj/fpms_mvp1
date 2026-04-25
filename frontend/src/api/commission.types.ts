export interface CommissionListParams {
    agent_id?: string
    case_id?: string
    case_no?: string
    status?: string
    settleable_date_from?: string
    settleable_date_to?: string
    created_at_from?: string
    created_at_to?: string
    page?: number
    page_size?: number
}

export interface CommissionRecord {
    id: number
    case_id: string
    case_no?: string
    agent_id?: string
    rule_id?: number
    fee_type?: string
    base_fee: number
    s1_rate: number
    s1_amount: number
    s1_done: boolean
    s2_rate: number
    s2_amount: number
    s2_done: boolean
    wait_pay: boolean
    force_settle: boolean
    status: string
    is_settleable: boolean
    settleable_date?: string
    remark?: string
    created_at: string
    updated_at: string
}

export interface CommissionRule {
    id: number
    rule_name: string
    case_type?: string
    fee_type?: string
    flow_dir?: string
    patent_category?: string
    s1_rate: number
    s2_rate: number
    s1_fixed_amount: number
    s2_fixed_amount: number
    wait_pay: boolean
    force_settle: boolean
    enabled: boolean
    effective_from?: string
    effective_to?: string
    remark?: string
    created_at: string
    updated_at: string
}

export interface CommissionRuleCreatePayload {
    rule_name: string
    case_type?: string
    fee_type?: string
    flow_dir?: string
    patent_category?: string
    s1_rate: number
    s2_rate: number
    s1_fixed_amount?: number
    s2_fixed_amount?: number
    wait_pay: boolean
    force_settle: boolean
    enabled?: boolean
    effective_from?: string
    effective_to?: string
    remark?: string
}

export interface CommissionRuleUpdatePayload {
    rule_name?: string
    case_type?: string
    fee_type?: string
    flow_dir?: string
    patent_category?: string
    s1_rate?: number
    s2_rate?: number
    s1_fixed_amount?: number
    s2_fixed_amount?: number
    wait_pay?: boolean
    force_settle?: boolean
    enabled?: boolean
    effective_from?: string
    effective_to?: string
    remark?: string
}

export interface CommissionSettlement {
    id: number
    settlement_no?: string
    agent_id?: string
    status: string
    currency: string
    period_from?: string
    period_to?: string
    line_count: number
    total_amount: number
    remark?: string
    created_at: string
    updated_at: string
}

export interface CommissionSettlementCreatePayload {
    agent_id: string
    period_from?: string
    period_to?: string
    currency: string
    remark?: string
}

export interface CommissionSettlementGenerateLinesResult {
    settlement_id: number
    line_count: number
    total_amount: number
    created_count: number
    updated_count: number
    status: string
}

export interface CommissionSettlementReportParams {
    agent_id?: string
    case_id?: string
    currency?: string
    settlement_status?: string
    line_status?: string
    date_from?: string
    date_to?: string
    time_field?: 'line_created_at' | 'settleable_date' | 'settlement_period'
}

export interface CommissionSettlementReportResult {
    filters: {
        agent_id?: string
        case_id?: string
        currency?: string
        settlement_status?: string
        line_status?: string
        date_from?: string
        date_to?: string
        time_field: 'line_created_at' | 'settleable_date' | 'settlement_period'
    }
    summary: {
        line_count: number
        settlement_count: number
        agent_count: number
        case_count: number
        total_amount: number
    }
    totals: {
        line_count: number
        total_amount: number
    }
    by_agent: {
        agent_id?: string
        line_count: number
        total_amount: number
    }[]
    by_case: {
        case_id?: string
        line_count: number
        total_amount: number
    }[]
    by_time: {
        time_bucket: string
        line_count: number
        total_amount: number
    }[]
    details: {
        settlement_id: number
        settlement_no?: string
        commission_id: number
        agent_id?: string
        case_id: string
        amount: number
        currency?: string
        line_status?: string
        settlement_status?: string
        s1_done: boolean
        s2_done: boolean
        is_settleable: boolean
        settleable_date?: string
        period_from?: string
        period_to?: string
        created_at: string
    }[]
}
