/**
 * Grant Fee API Types
 */

export type GrantFeeMoney = number | string

export type GrantFeeTaskStatus = 'OPEN' | 'WAITING_CLIENT' | 'READY_TO_DRAFT' | 'DRAFT_GENERATED' | 'DONE'
export type GrantFeeTaskLineageStatus = 'CONFIRMED' | 'LEGACY_UNVERIFIED' | 'SUPERSEDED'
export type GrantFeeTaskClientInstruction = 'NONE' | 'PAY' | 'ABANDON'
export type GrantFeeTaskStateAction =
    | 'mark_waiting_client'
    | 'record_pay_instruction'
    | 'record_abandon_instruction'
    | 'mark_draft_generated'
    | 'mark_done'

export type GrantFeeTaskBatchInstructionAction =
    | 'record_pay_instruction'
    | 'record_abandon_instruction'

export interface GrantFeeTaskBatchNoticeGeneratePayload {
    task_ids: string[]
}

export interface GrantFeeTaskBatchNoticeGenerateItem {
    task_id: string
    case_id: string
    document_id: string
    attachment_id: string
    file_name: string
    notify_count: number
}

export interface GrantFeeTaskBatchNoticeGenerateResult {
    success_count: number
    failure_count: number
    generated_document_ids: string[]
    items: GrantFeeTaskBatchNoticeGenerateItem[]
}

export interface GrantFeeTaskReplacementDocumentPayload {
    doc_template_id: string
    doc_date: string
    title: string
    ref_no: string
    official_due_date: string
    official_due_date_source: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE'
    official_due_date_status: 'CONFIRMED'
    description?: string
}

export interface GrantFeeTaskReplacementNoticePayload {
    idempotency_key: string
    reason: string
    document: GrantFeeTaskReplacementDocumentPayload
}

export interface GrantFeeTaskListItem {
    task_id: string
    case_id: string
    case_no?: string
    status: GrantFeeTaskStatus
    due_date: string
    client_instruction: GrantFeeTaskClientInstruction
    gov_fee_amt: GrantFeeMoney
    service_fee_amt: GrantFeeMoney
    currency: string
    draft_generated: boolean
    notice_sent: boolean
    notify_count: number
    is_overdue: boolean
    billed: boolean
    linked_bill_id?: string
    linked_bill_no?: string
    trigger_rule: string
    deadline_rule: string
    fee_basis: string
    fee_node_explanation: string
    lineage_status: GrantFeeTaskLineageStatus
    source_document_id: string | null
    deadline_source: string | null
    deadline_confirmed_at: string | null
}

export interface GrantFeeTaskListResponse {
    items: GrantFeeTaskListItem[]
    page: number
    page_size: number
    total: number
}

export interface GrantFeeTaskReplacementNoticeResult {
    document: { id: string }
    replacement_task: GrantFeeTaskListItem
    superseded_task_id: string
    reused: boolean
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
    trigger_rule: string
    deadline_rule: string
    fee_basis: string
    fee_node_explanation: string
    lineage_status: GrantFeeTaskLineageStatus
    source_document_id: string | null
    deadline_source: string | null
    deadline_confirmed_at: string | null
}

export interface GrantFeeTaskBatchInstructionPayload {
    task_ids: string[]
    action: GrantFeeTaskBatchInstructionAction
}

export interface GrantFeeTaskBatchInstructionResult {
    success_count: number
    failure_count: number
    updated_task_ids: string[]
}

export interface GrantFeeTaskListParams {
    status?: GrantFeeTaskStatus
    client_instruction?: GrantFeeTaskClientInstruction
    draft_generated?: boolean
    is_overdue?: boolean
    case_id?: string
    case_no?: string
    date_from?: string
    date_to?: string
    page?: number
    page_size?: number
}
