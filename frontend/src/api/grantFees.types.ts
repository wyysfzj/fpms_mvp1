/**
 * Grant Fee API Types
 */

export type GrantFeeMoney = number | string

export type GrantFeeTaskStatus = 'OPEN' | 'WAITING_CLIENT' | 'READY_TO_DRAFT' | 'DRAFT_GENERATED' | 'DONE'
export type GrantFeeTaskClientInstruction = 'NONE' | 'PAY' | 'ABANDON'

export interface GrantFeeTaskListItem {
    task_id: string
    case_id: string
    status: GrantFeeTaskStatus
    due_date: string
    client_instruction: GrantFeeTaskClientInstruction
    gov_fee_amt: GrantFeeMoney
    service_fee_amt: GrantFeeMoney
    currency: string
    draft_generated: boolean
    notice_sent: boolean
    is_overdue: boolean
}

export interface GrantFeeTaskListResponse {
    items: GrantFeeTaskListItem[]
    page: number
    page_size: number
    total: number
}

export interface GrantFeeTaskListParams {
    status?: GrantFeeTaskStatus
    client_instruction?: GrantFeeTaskClientInstruction
    draft_generated?: boolean
    is_overdue?: boolean
    case_id?: string
    date_from?: string
    date_to?: string
    page?: number
    page_size?: number
}
