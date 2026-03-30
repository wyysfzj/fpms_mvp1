import { http } from './http'
import type {
    GrantFeeMoney,
    GrantFeeTaskClientInstruction,
    GrantFeeTaskListItem,
    GrantFeeTaskListParams,
    GrantFeeTaskListResponse,
    GrantFeeTaskStatus,
} from './grantFees.types'

interface BackendGrantFeeTaskListItem {
    task_id: string
    case_id: string
    status: string
    due_date: string
    client_instruction: string
    gov_fee_amt: GrantFeeMoney
    service_fee_amt: GrantFeeMoney
    currency: string
    draft_generated: boolean
    notice_sent: boolean
    is_overdue: boolean
}

interface BackendGrantFeeTaskListResponse {
    items: BackendGrantFeeTaskListItem[]
    page: number
    page_size: number
    total: number
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
        status: normalizeStatus(input.status),
        due_date: input.due_date,
        client_instruction: normalizeInstruction(input.client_instruction),
        gov_fee_amt: input.gov_fee_amt,
        service_fee_amt: input.service_fee_amt,
        currency: input.currency,
        draft_generated: Boolean(input.draft_generated),
        notice_sent: Boolean(input.notice_sent),
        is_overdue: Boolean(input.is_overdue),
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
            ...(date_from ? { date_from } : {}),
            ...(date_to ? { date_to } : {}),
        },
    })

    return {
        ...response.data,
        items: response.data.items.map(mapGrantFeeTask),
    }
}
