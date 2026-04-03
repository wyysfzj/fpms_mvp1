/**
 * Document API Types
 */

export interface Document {
    id: string
    title: string
    direction: 'IN' | 'OUT'
    case_id?: string
    case_no?: string
    template_code?: string
    client_id?: string
    client_name?: string
    doc_template_id?: string | null
    doc_date?: string
    doc_type?: string
    description?: string
    outgoing_reg_no?: string | null
    forward_date?: string | null
    created_at?: string
    updated_at?: string
    attachments?: Attachment[]
    reply_to_id?: string
    need_reply?: boolean
    reply_date?: string
}

export interface DocumentListParams {
    page?: number
    page_size?: number
    q?: string
    doc_name?: string
    case_no?: string
    template_code?: string
    direction?: 'IN' | 'OUT'
    doc_template_id?: string
    case_id?: string
    client_id?: string
    need_reply?: boolean
    replied?: boolean
    date_from?: string
    date_to?: string
}

export interface DocumentDispatchMailingListParams {
    page?: number
    page_size?: number
    q?: string
    client_id?: string
    doc_template_id?: string
    date_from?: string
    date_to?: string
}

export interface DocumentMailingBatchIn {
    selected_document_ids: string[]
    outgoing_reg_no: string
    forward_date?: string | null
}

export interface DocumentMailingBatchItemOut {
    document_id: string
    case_id: string
    case_no?: string
    outgoing_reg_no?: string | null
    forward_date?: string | null
}

export interface DocumentMailingBatchOut {
    success_count: number
    failure_count: number
    items: DocumentMailingBatchItemOut[]
}

export interface DocumentDispatchCreateIn {
    client_id: string
    dispatch_date: string
    selected_document_ids: string[]
    remark?: string | null
}

export interface DocumentDispatchLineOut {
    id: string
    dispatch_id: string
    document_id: string
    case_id: string
    case_no?: string
    doc_name: string
    outgoing_reg_no?: string | null
}

export interface DocumentDispatchOut {
    id: string
    client_id: string
    client_name?: string | null
    dispatch_date: string
    remark?: string | null
    created_at: string
    updated_at: string
    lines: DocumentDispatchLineOut[]
}

export interface DocumentEnvelopePreviewOut {
    document_id: string
    case_id: string
    case_no?: string
    client_id?: string | null
    client_name?: string | null
    recipient_name?: string | null
    recipient_address?: string | null
    address_source: string
}

export interface DocumentCreatePayload {
    title: string
    direction: 'IN' | 'OUT'
    case_id: string
    doc_template_id?: string | null
    doc_date: string
    doc_type?: string
    description?: string
    reply_to_id?: string | null
}

export interface DocumentUpdatePayload {
    title?: string
    direction?: 'IN' | 'OUT'
    case_id?: string
    doc_template_id?: string | null
    doc_date?: string
    doc_type?: string
    description?: string
    reply_to_id?: string | null
    need_reply?: boolean | null
    reply_date?: string | null
}

export interface Attachment {
    id: string
    filename: string
    file_size: number
    content_type?: string
    created_at: string
}

export interface DocumentWizardBatchDefaults {
    direction: 'IN' | 'OUT'
    doc_date: string
    doc_template_id: string | null
}

export interface DocumentWizardBatchRowDraft {
    case_id: string
    title?: string
    doc_date?: string
    ref_no?: string
    need_reply?: boolean
    reply_to_id?: string
    extra_data?: string
}

export interface DocumentWizardTaskFinalRowDraft {
    row_index: number
    case_id: string
    task_template_code: string
    title?: string
    base_date?: string | null
    due_date?: string | null
    internal_due_date?: string | null
    remind1?: string | null
    remind2?: string | null
    remind3?: string | null
    daily_remind_from?: string | null
    daily_remind?: boolean
}

export interface DocumentWizardBatchCreatePayload {
    defaults: DocumentWizardBatchDefaults
    rows: DocumentWizardBatchRowDraft[]
    task_rows?: DocumentWizardTaskFinalRowDraft[]
}

export interface DocumentWizardBatchCreatedRow {
    row_index: number
    document: Document
}

export interface DocumentWizardBatchCreateResult {
    created: number
    total: number
    items: DocumentWizardBatchCreatedRow[]
}

export interface DocumentWizardTaskPreviewItem {
    row_index: number
    case_id: string
    case_no?: string
    source_title?: string
    document_title?: string
    task_template_code: string
    task_template_name?: string
    title?: string
    base_date?: string | null
    due_date?: string | null
    internal_due_date?: string | null
    remind1?: string | null
    remind2?: string | null
    remind3?: string | null
    daily_remind_from?: string | null
    daily_remind: boolean
}

export interface DocumentWizardTaskPreviewResult {
    total_candidates: number
    items: DocumentWizardTaskPreviewItem[]
}

export interface DocumentWizardBatchRowError {
    row_index: number
    field: string
    code: string
    message: string
    case_id?: string
}

export interface DocumentWizardParsedCase {
    id: string
    case_no: string
    app_no?: string
    title?: string
}

export type DocumentWizardCaseRowStatus = 'idle' | 'loading' | 'success' | 'error'

export interface DocumentWizardCaseRow {
    id: string
    input: string
    status: DocumentWizardCaseRowStatus
    matched_case?: DocumentWizardParsedCase
    error_message?: string
}

export interface DocumentWizardStep1State {
    rows: DocumentWizardCaseRow[]
}

export interface DocumentWizardState {
    activeStep: 1 | 2 | 3 | 4 | 5
    defaults: DocumentWizardBatchDefaults
    step1: DocumentWizardStep1State
}

// DocTemplate types (FC1)

export interface DocTemplate {
    id: string
    code: string
    name: string
    direction: 'IN' | 'OUT'
    enabled: boolean
    status_effect: string | null
    status_restore: string | null
    deadline_template_code: string | null
    fee_draft_type: string | null
    fee_item_list: string | null
    need_reply: boolean | null
    reply_to_template_code: string | null
    input_fields: string | null
    created_at: string
    updated_at: string
}

export interface DocTemplateListParams {
    page?: number
    page_size?: number
    q?: string
    direction?: 'IN' | 'OUT'
    enabled?: boolean
}

export interface DocTemplateCreatePayload {
    code: string
    name: string
    direction?: 'IN' | 'OUT'
    enabled?: boolean
    status_effect?: string | null
    status_restore?: string | null
    deadline_template_code?: string | null
    fee_draft_type?: string | null
    fee_item_list?: string | null
    need_reply?: boolean | null
    reply_to_template_code?: string | null
    input_fields?: string | null
}

export interface DocTemplateUpdatePayload {
    name?: string | null
    direction?: 'IN' | 'OUT' | null
    enabled?: boolean | null
    status_effect?: string | null
    status_restore?: string | null
    deadline_template_code?: string | null
    fee_draft_type?: string | null
    fee_item_list?: string | null
    need_reply?: boolean | null
    reply_to_template_code?: string | null
    input_fields?: string | null
}
