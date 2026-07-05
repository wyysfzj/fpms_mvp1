/**
 * Annuity API Types
 */

export interface AnnuityTask {
    id: number
    case_id: string
    case_no?: string | null
    client_id: string
    year_no: number
    due_date: string
    client_instruction?: string
    instruction_date?: string
    notice_status: string
    notice_sent_date?: string
    status: string
    remark?: string
    created_at?: string
    updated_at?: string
    gov_fee_amt?: number | null
    service_fee_amt?: number | null
    notify_count?: number | null
    pay_next_year?: boolean | null
    draft_generated?: boolean | null
    notice_sent?: boolean | null
    is_overdue?: boolean
    trigger_rule: string
    deadline_rule: string
    fee_basis: string
    fee_node_explanation: string
}

export type AnnuityPendingMode = 'pending' | 'processed'

export interface AnnuityTaskReportCount {
    key: string
    count: number
}

export interface AnnuityTaskGroupedAmount {
    key: string
    label: string
    task_count: number
    payable_amount: number
    official_paid_amount: number
    client_received_amount: number
}

export interface AnnuityTaskReportSummary {
    total_task_count: number
    open_task_count: number
    done_task_count: number
    overdue_task_count: number
    official_paid_task_count: number
    client_received_task_count: number
    collected_not_paid_task_count: number
    outstanding_task_count: number
    monitored_task_count: number
    on_time_paid_count: number
    late_paid_count: number
    success_rate: number | null
    status_counts: AnnuityTaskReportCount[]
    year_counts: AnnuityTaskReportCount[]
    client_amounts: AnnuityTaskGroupedAmount[]
    country_amounts: AnnuityTaskGroupedAmount[]
    year_amounts: AnnuityTaskGroupedAmount[]
}

export interface AnnuityTaskListResponse {
    items: AnnuityTask[]
    page: number
    page_size: number
    total: number
    summary: AnnuityTaskReportSummary
}

export interface AnnuityTaskListParams {
    due_from?: string
    due_to?: string
    date_from?: string
    date_to?: string
    status?: string
    task_status?: string
    pending_mode?: AnnuityPendingMode
    case_id?: string
    case_no?: string
    client_id?: string
    country?: string
    annuity_year?: number
    payment_status?: string
    notice_status?: string
    page?: number
    page_size?: number
}

export interface AnnuityInstructionUpdatePayload {
    instruction: string
    instruction_date?: string
}

export interface AnnuityGenerateDraftsPayload {
    task_ids: number[]
    pay_next_year?: boolean
    currency?: string
}

export interface AnnuityGenerateDraftSummary {
    requested: number
    targets: number
    success: number
    failed: number
    pay_next_year: boolean
}

export interface AnnuityGenerateDraftSuccessItem {
    source_task_id: number
    task_id: number
    year_no: number
    draft_id: string
    currency: string
    amount: number
    pay_next_year: boolean
}

export interface AnnuityGenerateDraftFailedItem {
    source_task_id: number
    task_id: number | null
    year_no: number
    pay_next_year: boolean
    code: string
    message: string
    status_code: number
}

export interface AnnuityGenerateDraftResult {
    summary: AnnuityGenerateDraftSummary
    success: AnnuityGenerateDraftSuccessItem[]
    failed: AnnuityGenerateDraftFailedItem[]
}

export interface AnnuityTaskGeneratePayload {
    case_id: string
}

export interface AnnuityTaskGenerateResult {
    case_id: string
    case_no?: string | null
    first_year: number
    last_year: number
    tasks_created: number
    tasks_skipped: number
}
