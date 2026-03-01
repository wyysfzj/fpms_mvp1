/**
 * Annuity API Types
 */

export interface AnnuityTask {
    id: number
    case_id: string
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
}

export type AnnuityPendingMode = 'pending' | 'processed'

export interface AnnuityTaskListParams {
    due_from?: string
    due_to?: string
    status?: string
    pending_mode?: AnnuityPendingMode
    case_id?: string
    client_id?: string
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
