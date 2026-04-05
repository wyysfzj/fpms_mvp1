/**
 * Grant Fee API Types
 */

export type GrantFeeMoney = number | string

export type GrantFeeTaskStatus = 'OPEN' | 'WAITING_CLIENT' | 'READY_TO_DRAFT' | 'DRAFT_GENERATED' | 'DONE'
export type GrantFeeTaskClientInstruction = 'NONE' | 'PAY' | 'ABANDON'
export type GrantFeeTaskStateAction =
    | 'mark_waiting_client'
    | 'record_pay_instruction'
    | 'record_abandon_instruction'
    | 'mark_draft_generated'
    | 'mark_done'

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
    billed: boolean
    linked_bill_id?: string
    linked_bill_no?: string
}

export interface GrantFeeTaskListResponse {
    items: GrantFeeTaskListItem[]
    page: number
    page_size: number
    total: number
}

export interface GrantFeeDraftGenerateResult {
    task_id: string
    case_id: string
    draft_id: string
    draft_type: string
    state: GrantFeeTaskStatus
    draft_generated: boolean
    currency: string
    amount: GrantFeeMoney
    item_count: number
    reused: boolean
}

export interface GrantFeeTaskStateResult {
    task_id: string
    case_id: string
    state: GrantFeeTaskStatus
    client_instruction: GrantFeeTaskClientInstruction
    notify_count: number
    draft_generated: boolean
    notice_sent: boolean
    is_overdue: boolean
    allowed_actions: GrantFeeTaskStateAction[]
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
