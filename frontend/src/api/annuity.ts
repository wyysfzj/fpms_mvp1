import { http } from './http'
import type { Pagination } from './types'
import type {
    AnnuityGenerateDraftFailedItem,
    AnnuityGenerateDraftResult,
    AnnuityGenerateDraftSuccessItem,
    AnnuityInstructionUpdatePayload,
    AnnuityTask,
    AnnuityTaskListParams,
    AnnuityGenerateDraftsPayload,
    AnnuityTaskGeneratePayload,
    AnnuityTaskGenerateResult,
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
): Promise<Pagination<AnnuityTask>> {
    const {
        due_from,
        due_to,
        status,
        pending_mode,
        case_id,
        client_id,
        notice_status,
        page = 1,
        page_size = 20,
    } = params

    const response = await http.get<Pagination<BackendAnnuityTask>>('/annuity/tasks', {
        params: {
            page,
            page_size,
            ...(due_from ? { due_from } : {}),
            ...(due_to ? { due_to } : {}),
            ...(status ? { status } : {}),
            ...(pending_mode ? { pending_mode } : {}),
            ...(case_id ? { case_id } : {}),
            ...(client_id ? { client_id } : {}),
            ...(notice_status ? { notice_status } : {}),
        }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapAnnuityTask),
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
