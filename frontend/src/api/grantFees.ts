import { http } from './http'
import type {
    GrantFeeTaskBatchInstructionAction,
    GrantFeeTaskBatchInstructionPayload,
    GrantFeeTaskBatchInstructionResult,
    GrantFeeTaskBatchNoticeGeneratePayload,
    GrantFeeTaskBatchNoticeGenerateResult,
    GrantFeeMoney,
    GrantFeeDraftGenerateResult,
    GrantFeeTaskClientInstruction,
    GrantFeeTaskListItem,
    GrantFeeTaskListParams,
    GrantFeeTaskListResponse,
    GrantFeeTaskStateAction,
    GrantFeeTaskStateResult,
    GrantFeeTaskStatus,
} from './grantFees.types'

interface BackendGrantFeeTaskListItem {
    task_id: string
    case_id: string
    case_no?: string | null
    status: string
    due_date: string
    client_instruction: string
    gov_fee_amt: GrantFeeMoney
    service_fee_amt: GrantFeeMoney
    currency: string
    draft_generated: boolean
    notice_sent: boolean
    notify_count: number
    is_overdue: boolean
    billed?: boolean
    linked_bill_id?: string | null
    linked_bill_no?: string | null
    trigger_rule?: string | null
    deadline_rule?: string | null
    fee_basis?: string | null
    fee_node_explanation?: string | null
}

interface BackendGrantFeeTaskListResponse {
    items: BackendGrantFeeTaskListItem[]
    page: number
    page_size: number
    total: number
}

interface BackendGrantFeeDraftGenerateResponse {
    task_id: string
    case_id: string
    draft_id: string
    draft_type: string
    state: string
    draft_generated: boolean
    currency: string
    amount: GrantFeeMoney
    item_count: number
    reused: boolean
}

interface BackendGrantFeeTaskStateResponse {
    task_id: string
    case_id: string
    state: string
    client_instruction: string
    notify_count: number
    draft_generated: boolean
    notice_sent: boolean
    is_overdue: boolean
    allowed_actions: string[]
    trigger_rule?: string | null
    deadline_rule?: string | null
    fee_basis?: string | null
    fee_node_explanation?: string | null
}

interface BackendGrantFeeTaskBatchInstructionResponse {
    success_count: number
    failure_count: number
    updated_task_ids: string[]
}

interface BackendGrantFeeTaskBatchNoticeGenerateItemResponse {
    task_id: string
    case_id: string
    document_id: string
    attachment_id: string
    file_name: string
    notify_count: number
}

interface BackendGrantFeeTaskBatchNoticeGenerateResponse {
    success_count: number
    failure_count: number
    generated_document_ids: string[]
    items: BackendGrantFeeTaskBatchNoticeGenerateItemResponse[]
}

function normalizeBoolean(input: boolean | undefined): boolean | undefined {
    return input === undefined ? undefined : Boolean(input)
}

function normalizeStatus(input: string): GrantFeeTaskStatus {
    const normalized = (input || '').trim().toUpperCase()
    const valid: GrantFeeTaskStatus[] = ['OPEN', 'WAITING_CLIENT', 'READY_TO_DRAFT', 'DRAFT_GENERATED', 'DONE']
    return valid.includes(normalized as GrantFeeTaskStatus) ? (normalized as GrantFeeTaskStatus) : 'OPEN'
}

function normalizeInstruction(input: string): GrantFeeTaskClientInstruction {
    const normalized = (input || '').trim().toUpperCase()
    const valid: GrantFeeTaskClientInstruction[] = ['NONE', 'PAY', 'ABANDON']
    return valid.includes(normalized as GrantFeeTaskClientInstruction)
        ? (normalized as GrantFeeTaskClientInstruction)
        : 'NONE'
}

function mapGrantFeeTask(input: BackendGrantFeeTaskListItem): GrantFeeTaskListItem {
    return {
        task_id: input.task_id,
        case_id: input.case_id,
        case_no: input.case_no || undefined,
        status: normalizeStatus(input.status),
        due_date: input.due_date,
        client_instruction: normalizeInstruction(input.client_instruction),
        gov_fee_amt: input.gov_fee_amt,
        service_fee_amt: input.service_fee_amt,
        currency: input.currency,
        draft_generated: Boolean(input.draft_generated),
        notice_sent: Boolean(input.notice_sent),
        notify_count: Number(input.notify_count || 0),
        is_overdue: Boolean(input.is_overdue),
        billed: Boolean(input.billed),
        linked_bill_id: input.linked_bill_id || undefined,
        linked_bill_no: input.linked_bill_no || undefined,
        trigger_rule: input.trigger_rule || '收到办理登记手续通知书/授权通知书',
        deadline_rule: input.deadline_rule || '以办理登记手续通知书/授权通知书载明期限为准',
        fee_basis: input.fee_basis || '授权阶段官费按授权费任务金额展示',
        fee_node_explanation: input.fee_node_explanation || '授权费用节点：客户确认缴费后生成官费草单。',
    }
}

function mapGrantFeeDraftGenerateResult(
    input: BackendGrantFeeDraftGenerateResponse,
): GrantFeeDraftGenerateResult {
    return {
        task_id: input.task_id,
        case_id: input.case_id,
        draft_id: input.draft_id,
        draft_type: input.draft_type,
        state: normalizeStatus(input.state),
        draft_generated: Boolean(input.draft_generated),
        currency: input.currency,
        amount: input.amount,
        item_count: input.item_count,
        reused: Boolean(input.reused),
    }
}

function normalizeAction(input: string): GrantFeeTaskStateAction {
    const normalized = (input || '').trim()
    const valid: GrantFeeTaskStateAction[] = [
        'mark_waiting_client',
        'record_pay_instruction',
        'record_abandon_instruction',
        'mark_draft_generated',
        'mark_done',
    ]
    return valid.includes(normalized as GrantFeeTaskStateAction)
        ? (normalized as GrantFeeTaskStateAction)
        : 'mark_done'
}

function mapGrantFeeTaskStateResult(
    input: BackendGrantFeeTaskStateResponse,
): GrantFeeTaskStateResult {
    return {
        task_id: input.task_id,
        case_id: input.case_id,
        state: normalizeStatus(input.state),
        client_instruction: normalizeInstruction(input.client_instruction),
        notify_count: Number(input.notify_count || 0),
        draft_generated: Boolean(input.draft_generated),
        notice_sent: Boolean(input.notice_sent),
        is_overdue: Boolean(input.is_overdue),
        allowed_actions: Array.isArray(input.allowed_actions)
            ? input.allowed_actions.map(normalizeAction)
            : [],
        trigger_rule: input.trigger_rule || '收到办理登记手续通知书/授权通知书',
        deadline_rule: input.deadline_rule || '以办理登记手续通知书/授权通知书载明期限为准',
        fee_basis: input.fee_basis || '授权阶段官费按授权费任务金额展示',
        fee_node_explanation: input.fee_node_explanation || '授权费用节点：客户确认缴费后生成官费草单。',
    }
}

/**
 * Get paginated grant-fee task list
 */
export async function getGrantFeeTasks(
    params: GrantFeeTaskListParams = {},
): Promise<GrantFeeTaskListResponse> {
    const {
        status,
        client_instruction,
        draft_generated,
        is_overdue,
        case_id,
        case_no,
        date_from,
        date_to,
        page = 1,
        page_size = 20,
    } = params

    const response = await http.get<BackendGrantFeeTaskListResponse>('/grant-fee-tasks/list', {
        params: {
            page,
            page_size,
            ...(status ? { status } : {}),
            ...(client_instruction ? { client_instruction } : {}),
            ...(draft_generated !== undefined ? { draft_generated: normalizeBoolean(draft_generated) } : {}),
            ...(is_overdue !== undefined ? { is_overdue: normalizeBoolean(is_overdue) } : {}),
            ...(case_id ? { case_id } : {}),
            ...(case_no ? { case_no } : {}),
            ...(date_from ? { date_from } : {}),
            ...(date_to ? { date_to } : {}),
        },
    })

    return {
        ...response.data,
        items: response.data.items.map(mapGrantFeeTask),
    }
}

/**
 * Generate a grant-fee draft from one task row
 */
export async function generateGrantFeeDraft(taskId: string): Promise<GrantFeeDraftGenerateResult> {
    const response = await http.post<BackendGrantFeeDraftGenerateResponse>(`/grant-fee-tasks/${taskId}/generate-draft`)
    return mapGrantFeeDraftGenerateResult(response.data)
}

/**
 * Apply a grant-fee task state action
 */
export async function applyGrantFeeTaskAction(
    taskId: string,
    action: GrantFeeTaskStateAction,
): Promise<GrantFeeTaskStateResult> {
    const response = await http.put<BackendGrantFeeTaskStateResponse>(`/grant-fee-tasks/${taskId}/state`, {
        action,
    })
    return mapGrantFeeTaskStateResult(response.data)
}

/**
 * Apply a batch grant-fee client instruction
 */
export async function applyGrantFeeBatchInstruction(
    payload: GrantFeeTaskBatchInstructionPayload,
): Promise<GrantFeeTaskBatchInstructionResult> {
    const response = await http.post<BackendGrantFeeTaskBatchInstructionResponse>(
        '/grant-fee-tasks/batch-instruction',
        {
            task_ids: payload.task_ids,
            action: payload.action as GrantFeeTaskBatchInstructionAction,
        },
    )
    return {
        success_count: Number(response.data.success_count || 0),
        failure_count: Number(response.data.failure_count || 0),
        updated_task_ids: Array.isArray(response.data.updated_task_ids)
            ? response.data.updated_task_ids
            : [],
    }
}

/**
 * Batch generate real grant-fee notice documents
 */
export async function generateGrantFeeNoticeDocuments(
    payload: GrantFeeTaskBatchNoticeGeneratePayload,
): Promise<GrantFeeTaskBatchNoticeGenerateResult> {
    const response = await http.post<BackendGrantFeeTaskBatchNoticeGenerateResponse>(
        '/grant-fee-tasks/generate-notices',
        {
            task_ids: payload.task_ids,
        },
    )
    return {
        success_count: Number(response.data.success_count || 0),
        failure_count: Number(response.data.failure_count || 0),
        generated_document_ids: Array.isArray(response.data.generated_document_ids)
            ? response.data.generated_document_ids
            : [],
        items: Array.isArray(response.data.items)
            ? response.data.items.map((item) => ({
                task_id: item.task_id,
                case_id: item.case_id,
                document_id: item.document_id,
                attachment_id: item.attachment_id,
                file_name: item.file_name,
                notify_count: Number(item.notify_count || 0),
            }))
            : [],
    }
}
