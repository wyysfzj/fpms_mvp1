/**
 * Document API Types
 */

export interface Document {
    id: string
    title: string
    direction: 'IN' | 'OUT'
    case_id?: string
    case_no?: string
    doc_template_id?: string | null
    doc_date?: string
    doc_type?: string
    description?: string
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
    direction?: 'IN' | 'OUT'
    doc_template_id?: string
    case_id?: string
    client_id?: string
    need_reply?: boolean
    replied?: boolean
    date_from?: string
    date_to?: string
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
