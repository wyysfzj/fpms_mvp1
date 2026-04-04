import { http } from './http'
import type {
    AnnuityGenerateDraftFailedItem,
    AnnuityGenerateDraftResult,
    AnnuityGenerateDraftSuccessItem,
    AnnuityInstructionUpdatePayload,
    AnnuityTask,
    AnnuityTaskListResponse,
    AnnuityTaskListParams,
    AnnuityTaskReportCount,
    AnnuityTaskReportSummary,
    AnnuityGenerateDraftsPayload,
    AnnuityTaskGeneratePayload,
    AnnuityTaskGenerateResult,
    AnnuityTaskGroupedAmount,
} from './annuity.types'

interface BackendAnnuityTask {
    id: number
    case_id: string
    client_id: string
    year_no: number
    due_date: string
    client_instruction?: string | null
    instruction_date?: string | null
    notice_status?: string | null
    notice_sent_date?: string | null
    status?: string | null
    remark?: string | null
    created_at?: string | null
    updated_at?: string | null
    gov_fee_amt?: number | string | null
    service_fee_amt?: number | string | null
    notify_count?: number | null
    pay_next_year?: boolean | null
    draft_generated?: boolean | null
    notice_sent?: boolean | null
    is_overdue?: boolean | null
}

interface BackendAnnuityTaskReportCount {
    key: string
    count: number
}

interface BackendAnnuityTaskReportSummary {
    total_task_count: number
    open_task_count: number
    done_task_count: number
    overdue_task_count: number
    status_counts: BackendAnnuityTaskReportCount[]
    year_counts: BackendAnnuityTaskReportCount[]
    client_amounts: BackendAnnuityTaskGroupedAmount[]
    country_amounts: BackendAnnuityTaskGroupedAmount[]
    year_amounts: BackendAnnuityTaskGroupedAmount[]
}

interface BackendAnnuityTaskGroupedAmount {
    key: string
    label: string
    task_count: number
    payable_amount: number | string
    official_paid_amount: number | string
    client_received_amount: number | string
}

interface BackendAnnuityTaskListResponse {
    items: BackendAnnuityTask[]
    page: number
    page_size: number
    total: number
    summary: BackendAnnuityTaskReportSummary
}

interface BackendAnnuityGenerateDraftSummary {
    requested: number
    targets: number
    success: number
    failed: number
    pay_next_year: boolean
}

interface BackendAnnuityGenerateDraftSuccessItem {
    source_task_id: number
    task_id: number
    year_no: number
    draft_id: string
    currency: string
    amount: number | string
    pay_next_year: boolean
}

interface BackendAnnuityGenerateDraftFailedItem {
    source_task_id: number
    task_id: number | null
    year_no: number
    pay_next_year: boolean
    code: string
    message: string
    status_code: number
}

interface BackendAnnuityGenerateDraftResult {
    summary: BackendAnnuityGenerateDraftSummary
    success: BackendAnnuityGenerateDraftSuccessItem[]
    failed: BackendAnnuityGenerateDraftFailedItem[]
}

function asNumber(input: number | string | null | undefined): number {
    if (input === null || input === undefined || input === '') return 0
    const parsed = Number(input)
    return Number.isFinite(parsed) ? parsed : 0
}

function mapAnnuityTask(input: BackendAnnuityTask): AnnuityTask {
    return {
        id: input.id,
        case_id: input.case_id,
        client_id: input.client_id,
        year_no: input.year_no,
        due_date: input.due_date,
        client_instruction: input.client_instruction || undefined,
        instruction_date: input.instruction_date || undefined,
        notice_status: input.notice_status || 'PENDING',
        notice_sent_date: input.notice_sent_date || undefined,
        status: input.status || 'OPEN',
        remark: input.remark || undefined,
        created_at: input.created_at || undefined,
        updated_at: input.updated_at || undefined,
        gov_fee_amt: input.gov_fee_amt != null ? asNumber(input.gov_fee_amt) : undefined,
        service_fee_amt: input.service_fee_amt != null ? asNumber(input.service_fee_amt) : undefined,
        notify_count: input.notify_count ?? undefined,
        pay_next_year: input.pay_next_year ?? undefined,
        draft_generated: input.draft_generated ?? undefined,
        notice_sent: input.notice_sent ?? undefined,
        is_overdue: input.is_overdue ?? false,
    }
}

function mapReportCount(input: BackendAnnuityTaskReportCount): AnnuityTaskReportCount {
    return {
        key: input.key,
        count: Number(input.count || 0),
    }
}

function mapGroupedAmount(input: BackendAnnuityTaskGroupedAmount): AnnuityTaskGroupedAmount {
    return {
        key: input.key,
        label: input.label,
        task_count: Number(input.task_count || 0),
        payable_amount: asNumber(input.payable_amount),
        official_paid_amount: asNumber(input.official_paid_amount),
        client_received_amount: asNumber(input.client_received_amount),
    }
}

function mapReportSummary(input: BackendAnnuityTaskReportSummary): AnnuityTaskReportSummary {
    return {
        total_task_count: Number(input.total_task_count || 0),
        open_task_count: Number(input.open_task_count || 0),
        done_task_count: Number(input.done_task_count || 0),
        overdue_task_count: Number(input.overdue_task_count || 0),
        status_counts: (input.status_counts || []).map(mapReportCount),
        year_counts: (input.year_counts || []).map(mapReportCount),
        client_amounts: (input.client_amounts || []).map(mapGroupedAmount),
        country_amounts: (input.country_amounts || []).map(mapGroupedAmount),
        year_amounts: (input.year_amounts || []).map(mapGroupedAmount),
    }
}

function mapGenerateSuccessItem(
    input: BackendAnnuityGenerateDraftSuccessItem,
): AnnuityGenerateDraftSuccessItem {
    return {
        source_task_id: input.source_task_id,
        task_id: input.task_id,
        year_no: input.year_no,
        draft_id: input.draft_id,
        currency: input.currency,
        amount: asNumber(input.amount),
        pay_next_year: input.pay_next_year,
    }
}

function mapGenerateFailedItem(
    input: BackendAnnuityGenerateDraftFailedItem,
): AnnuityGenerateDraftFailedItem {
    return {
        source_task_id: input.source_task_id,
        task_id: input.task_id,
        year_no: input.year_no,
        pay_next_year: input.pay_next_year,
        code: input.code,
        message: input.message,
        status_code: input.status_code,
    }
}

function normalizeDraftCurrency(input?: string): string {
    const normalized = (input || '').trim().toUpperCase()
    return normalized || 'CNY'
}

/**
 * Get paginated annuity task list
 */
export async function getAnnuityTasks(
    params: AnnuityTaskListParams = {},
): Promise<AnnuityTaskListResponse> {
    const {
        due_from,
        due_to,
        date_from,
        date_to,
        status,
        task_status,
        pending_mode,
        case_id,
        client_id,
        country,
        annuity_year,
        payment_status,
        notice_status,
        page = 1,
        page_size = 20,
    } = params

    const response = await http.get<BackendAnnuityTaskListResponse>('/annuity/tasks', {
        params: {
            page,
            page_size,
            ...(due_from ? { due_from } : {}),
            ...(due_to ? { due_to } : {}),
            ...(date_from ? { date_from } : {}),
            ...(date_to ? { date_to } : {}),
            ...(status ? { status } : {}),
            ...(task_status ? { task_status } : {}),
            ...(pending_mode ? { pending_mode } : {}),
            ...(case_id ? { case_id } : {}),
            ...(client_id ? { client_id } : {}),
            ...(country ? { country } : {}),
            ...(annuity_year ? { annuity_year } : {}),
            ...(payment_status ? { payment_status } : {}),
            ...(notice_status ? { notice_status } : {}),
        }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapAnnuityTask),
        summary: mapReportSummary(response.data.summary),
    }
}

/**
 * Update a task's client instruction
 */
export async function updateAnnuityTaskInstruction(
    taskId: number,
    payload: AnnuityInstructionUpdatePayload,
): Promise<AnnuityTask> {
    const response = await http.put<BackendAnnuityTask>(
        `/annuity/tasks/${taskId}/instruction`,
        {
            instruction: payload.instruction,
            instruction_date: payload.instruction_date || undefined,
        },
    )
    return mapAnnuityTask(response.data)
}

/**
 * Generate fee drafts from selected annuity tasks
 */
export async function generateAnnuityDrafts(
    payload: AnnuityGenerateDraftsPayload,
): Promise<AnnuityGenerateDraftResult> {
    const currency = normalizeDraftCurrency(payload.currency)
    const response = await http.post<BackendAnnuityGenerateDraftResult>(
        '/annuity/tasks/generate-drafts',
        {
            task_ids: payload.task_ids,
            pay_next_year: payload.pay_next_year,
            currency,
        },
    )

    return {
        summary: response.data.summary,
        success: response.data.success.map(mapGenerateSuccessItem),
        failed: response.data.failed.map(mapGenerateFailedItem),
    }
}

export async function generateAnnuityTasks(payload: AnnuityTaskGeneratePayload): Promise<AnnuityTaskGenerateResult> {
    const { data } = await http.post<AnnuityTaskGenerateResult>('/annuity/tasks/generate', payload)
    return data
}
