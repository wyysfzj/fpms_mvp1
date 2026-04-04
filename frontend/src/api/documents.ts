import { reactive } from 'vue'
import { http } from './http'
import type { Pagination } from './types'
import type {
    Attachment,
    DocTemplate,
    DocTemplateCreatePayload,
    DocTemplateListParams,
    DocTemplateUpdatePayload,
    Document,
    DocumentDispatchCreateIn,
    DocumentDispatchOut,
    DocumentDispatchMailingListParams,
    DocumentEnvelopePreviewOut,
    DocumentMailingBatchIn,
    DocumentMailingBatchOut,
    DocumentCreatePayload,
    DocumentListParams,
    DocumentUpdatePayload,
    DocumentWizardAttachmentPreviewResult,
    DocumentWizardBatchCreatePayload,
    DocumentWizardBatchCreateResult,
    DocumentWizardBatchDefaults,
    DocumentWizardFeePreviewResult,
    DocumentWizardTaskPreviewResult,
    DocumentWizardStep1State,
    DocumentWizardState,
} from './documents.types'

interface BackendAttachment {
    id: string
    file_name: string
    file_size: number
    mime_type?: string
    uploaded_at: string
}

interface BackendDocument {
    id: string
    case_id?: string | null
    client_id?: string | null
    client_name?: string | null
    doc_template_id?: string | null
    template_code?: string | null
    direction: 'IN' | 'OUT'
    doc_date?: string | null
    title?: string | null
    ref_no?: string | null
    extra_data?: string | null
    created_at?: string
    updated_at?: string
    attachments?: BackendAttachment[]
    reply_to_id?: string | null
    need_reply?: boolean | null
    reply_date?: string | null
    case_no?: string | null
    outgoing_reg_no?: string | null
    forward_date?: string | null
}

function mapAttachment(input: BackendAttachment): Attachment {
    return {
        id: input.id,
        filename: input.file_name,
        file_size: Number(input.file_size || 0),
        content_type: input.mime_type,
        created_at: input.uploaded_at,
    }
}

function mapDocument(input: BackendDocument): Document {
    return {
        id: input.id,
        case_id: input.case_id || undefined,
        client_id: input.client_id || undefined,
        client_name: input.client_name || undefined,
        doc_template_id: input.doc_template_id,
        template_code: input.template_code || undefined,
        direction: input.direction,
        doc_date: input.doc_date || undefined,
        title: input.title || 'Untitled Document',
        doc_type: input.ref_no || undefined,
        description: input.extra_data || undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
        reply_to_id: input.reply_to_id || undefined,
        need_reply: input.need_reply ?? undefined,
        reply_date: input.reply_date || undefined,
        case_no: input.case_no || undefined,
        outgoing_reg_no: input.outgoing_reg_no || undefined,
        forward_date: input.forward_date || undefined,
        attachments: (input.attachments || []).map(mapAttachment),
    }
}

function toCreatePayload(data: DocumentCreatePayload): Record<string, unknown> {
    return {
        case_id: String(data.case_id),
        doc_template_id: data.doc_template_id ?? null,
        direction: data.direction,
        doc_date: data.doc_date,
        title: data.title,
        ref_no: data.doc_type || null,
        extra_data: data.description || null,
        reply_to_id: data.reply_to_id || null,
    }
}

function toUpdatePayload(data: DocumentUpdatePayload): Record<string, unknown> {
    const payload: Record<string, unknown> = {}

    if (data.case_id !== undefined) payload.case_id = data.case_id || null
    if (data.doc_template_id !== undefined) payload.doc_template_id = data.doc_template_id
    if (data.direction !== undefined) payload.direction = data.direction
    if (data.doc_date !== undefined) payload.doc_date = data.doc_date || null
    if (data.title !== undefined) payload.title = data.title || null
    if (data.doc_type !== undefined) payload.ref_no = data.doc_type || null
    if (data.description !== undefined) payload.extra_data = data.description || null
    if (data.reply_to_id !== undefined) payload.reply_to_id = data.reply_to_id || null
    if (data.need_reply !== undefined) payload.need_reply = data.need_reply
    if (data.reply_date !== undefined) payload.reply_date = data.reply_date || null

    return payload
}

function trimToUndefined(value: string | undefined): string | undefined {
    if (value === undefined) return undefined
    const normalized = value.trim()
    return normalized ? normalized : undefined
}

function toWizardBatchPayload(data: DocumentWizardBatchCreatePayload): Record<string, unknown> {
    return {
        defaults: {
            doc_template_id: data.defaults.doc_template_id,
            direction: data.defaults.direction,
            doc_date: data.defaults.doc_date,
        },
        rows: data.rows.map((row) => ({
            case_id: row.case_id,
            ...(trimToUndefined(row.title) ? { title: trimToUndefined(row.title) } : {}),
            ...(trimToUndefined(row.doc_date) ? { doc_date: trimToUndefined(row.doc_date) } : {}),
            ...(trimToUndefined(row.ref_no) ? { ref_no: trimToUndefined(row.ref_no) } : {}),
            ...(row.need_reply !== undefined ? { need_reply: row.need_reply } : {}),
            ...(trimToUndefined(row.reply_to_id) ? { reply_to_id: trimToUndefined(row.reply_to_id) } : {}),
            ...(trimToUndefined(row.extra_data) ? { extra_data: trimToUndefined(row.extra_data) } : {}),
        })),
        task_rows: (data.task_rows || []).map((row) => ({
            row_index: row.row_index,
            case_id: row.case_id,
            task_template_code: row.task_template_code,
            ...(trimToUndefined(row.title) ? { title: trimToUndefined(row.title) } : {}),
            ...(trimToUndefined(row.base_date ?? undefined) ? { base_date: trimToUndefined(row.base_date ?? undefined) } : {}),
            ...(trimToUndefined(row.due_date ?? undefined) ? { due_date: trimToUndefined(row.due_date ?? undefined) } : {}),
            ...(trimToUndefined(row.internal_due_date ?? undefined)
                ? { internal_due_date: trimToUndefined(row.internal_due_date ?? undefined) }
                : {}),
            ...(trimToUndefined(row.remind1 ?? undefined) ? { remind1: trimToUndefined(row.remind1 ?? undefined) } : {}),
            ...(trimToUndefined(row.remind2 ?? undefined) ? { remind2: trimToUndefined(row.remind2 ?? undefined) } : {}),
            ...(trimToUndefined(row.remind3 ?? undefined) ? { remind3: trimToUndefined(row.remind3 ?? undefined) } : {}),
            ...(trimToUndefined(row.daily_remind_from ?? undefined)
                ? { daily_remind_from: trimToUndefined(row.daily_remind_from ?? undefined) }
                : {}),
            ...(row.daily_remind !== undefined ? { daily_remind: row.daily_remind } : {}),
        })),
        fee_rows: data.fee_rows?.map((row) => ({
                row_index: row.row_index,
                case_id: row.case_id,
                fee_draft_type: row.fee_draft_type,
                ...(row.skip_this_candidate !== undefined ? { skip_this_candidate: row.skip_this_candidate } : {}),
                fee_items: row.fee_items.map((item) => ({
                    ...(trimToUndefined(item.fee_code ?? undefined) ? { fee_code: trimToUndefined(item.fee_code ?? undefined) } : {}),
                    ...(trimToUndefined(item.fee_name ?? undefined) ? { fee_name: trimToUndefined(item.fee_name ?? undefined) } : {}),
                    fee_type: item.fee_type,
                    ...(trimToUndefined(item.quantity ?? undefined) ? { quantity: trimToUndefined(item.quantity ?? undefined) } : {}),
                    ...(trimToUndefined(item.unit_price ?? undefined) ? { unit_price: trimToUndefined(item.unit_price ?? undefined) } : {}),
                    amount: item.amount,
                    ...(trimToUndefined(item.remark ?? undefined) ? { remark: trimToUndefined(item.remark ?? undefined) } : {}),
                })),
            })) || [],
    }
}

/**
 * Get paginated list of documents
 */
export async function getDocuments(params: DocumentListParams = {}): Promise<Pagination<Document>> {
    const {
        page = 1,
        page_size = 20,
        q,
        doc_name,
        case_no,
        template_code,
        direction,
        doc_template_id,
        case_id,
        client_id,
        need_reply,
        replied,
        date_from,
        date_to,
    } = params
    const response = await http.get<Pagination<BackendDocument>>('/documents', {
        params: {
            page,
            page_size,
            ...(q ? { q } : {}),
            ...(doc_name ? { doc_name } : {}),
            ...(case_no ? { case_no } : {}),
            ...(template_code ? { template_code } : {}),
            ...(direction ? { direction } : {}),
            ...(doc_template_id ? { doc_template_id } : {}),
            ...(case_id ? { case_id } : {}),
            ...(client_id ? { client_id } : {}),
            ...(need_reply !== undefined ? { need_reply } : {}),
            ...(replied !== undefined ? { replied } : {}),
            ...(date_from ? { date_from } : {}),
            ...(date_to ? { date_to } : {}),
        }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapDocument),
    }
}

/**
 * Get candidate outgoing documents for mailing registration workflow
 */
export async function getDocumentDispatchMailingCandidates(
    params: DocumentDispatchMailingListParams = {}
): Promise<Pagination<Document>> {
    const { page = 1, page_size = 20, q, client_id, doc_template_id, date_from, date_to } = params
    return getDocuments({
        page,
        page_size,
        q: q?.trim() || undefined,
        direction: 'OUT',
        client_id,
        doc_template_id,
        date_from,
        date_to,
    })
}

/**
 * Batch register outgoing mailing info for selected documents
 */
export async function batchRegisterDocumentMailing(
    data: DocumentMailingBatchIn
): Promise<DocumentMailingBatchOut> {
    const response = await http.post<DocumentMailingBatchOut>('/documents/dispatch/mailing/batch-register', data)
    return response.data
}

export async function createDocumentDispatch(
    data: DocumentDispatchCreateIn
): Promise<DocumentDispatchOut> {
    const response = await http.post<DocumentDispatchOut>('/documents/dispatches', data)
    return response.data
}

export async function getDocumentDispatch(dispatchId: string): Promise<DocumentDispatchOut> {
    const response = await http.get<DocumentDispatchOut>(`/documents/dispatches/${dispatchId}`)
    return response.data
}

export async function getDocumentEnvelopePreview(documentId: string): Promise<DocumentEnvelopePreviewOut> {
    const response = await http.get<DocumentEnvelopePreviewOut>(`/documents/${documentId}/envelope-preview`)
    return response.data
}

/**
 * Get a single document by ID
 */
export async function getDocument(id: string | number): Promise<Document> {
    const response = await http.get<BackendDocument>(`/documents/${id}`)
    return mapDocument(response.data)
}

/**
 * Create a new document
 */
export async function createDocument(data: DocumentCreatePayload): Promise<Document> {
    const response = await http.post<BackendDocument>('/documents', toCreatePayload(data))
    return mapDocument(response.data)
}

/**
 * Update an existing document
 */
export async function updateDocument(id: string | number, data: DocumentUpdatePayload): Promise<Document> {
    const response = await http.put<BackendDocument>(`/documents/${id}`, toUpdatePayload(data))
    return mapDocument(response.data)
}

/**
 * Get attachments for a document
 * Backend exposes attachments in document detail response; there is no GET attachments endpoint.
 */
export async function getAttachments(docId: string | number): Promise<Attachment[]> {
    const response = await http.get<BackendDocument>(`/documents/${docId}`)
    return (response.data.attachments || []).map(mapAttachment)
}

/**
 * Upload an attachment to a document (multipart/form-data)
 */
export async function uploadAttachment(docId: string | number, file: File): Promise<Attachment> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await http.post<BackendAttachment>(`/documents/${docId}/attachments`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
    return mapAttachment(response.data)
}

/**
 * Download an attachment (returns blob)
 */
export async function downloadAttachment(docId: string | number, attId: string | number): Promise<Blob> {
    const response = await http.get<Blob>(`/documents/${docId}/attachments/${attId}/download`, {
        responseType: 'blob'
    })
    return response.data
}

// ── DocTemplate CRUD (FC1) ─────────────────────────────

export async function getDocTemplates(
    params: DocTemplateListParams = {}
): Promise<Pagination<DocTemplate>> {
    const { page = 1, page_size = 20, q, direction, enabled } = params
    const response = await http.get<Pagination<DocTemplate>>('/doc-templates', {
        params: {
            page,
            page_size,
            ...(q ? { q } : {}),
            ...(direction ? { direction } : {}),
            ...(enabled !== undefined ? { enabled } : {}),
        },
    })
    return response.data
}

export async function getDocTemplate(id: string): Promise<DocTemplate> {
    const response = await http.get<DocTemplate>(`/doc-templates/${id}`)
    return response.data
}

export async function createDocTemplate(
    data: DocTemplateCreatePayload
): Promise<DocTemplate> {
    const response = await http.post<DocTemplate>('/doc-templates', data)
    return response.data
}

export async function updateDocTemplate(
    id: string,
    data: DocTemplateUpdatePayload
): Promise<DocTemplate> {
    const response = await http.put<DocTemplate>(`/doc-templates/${id}`, data)
    return response.data
}

export async function createDocumentWizardBatch(
    data: DocumentWizardBatchCreatePayload
): Promise<DocumentWizardBatchCreateResult> {
    const response = await http.post<DocumentWizardBatchCreateResult>(
        '/documents/wizard/batch-create',
        toWizardBatchPayload(data)
    )
    return {
        ...response.data,
        items: response.data.items.map((item) => ({
            ...item,
            document: mapDocument(item.document as BackendDocument),
        })),
    }
}

export async function createDocumentWizardTaskPreview(
    data: DocumentWizardBatchCreatePayload
): Promise<DocumentWizardTaskPreviewResult> {
    const response = await http.post<DocumentWizardTaskPreviewResult>(
        '/documents/wizard/task-preview',
        toWizardBatchPayload(data)
    )
    return response.data
}

export async function createDocumentWizardFeePreview(
    data: DocumentWizardBatchCreatePayload
): Promise<DocumentWizardFeePreviewResult> {
    const response = await http.post<DocumentWizardFeePreviewResult>(
        '/documents/wizard/fee-preview',
        toWizardBatchPayload(data)
    )
    return response.data
}

export async function createDocumentWizardAttachmentPreview(
    data: DocumentWizardBatchCreatePayload
): Promise<DocumentWizardAttachmentPreviewResult> {
    const response = await http.post<DocumentWizardAttachmentPreviewResult>(
        '/documents/wizard/attachment-preview',
        toWizardBatchPayload(data)
    )
    return response.data
}

function createDocumentWizardDefaults(): DocumentWizardBatchDefaults {
    return {
        direction: 'IN',
        doc_date: new Date().toISOString().slice(0, 10),
        doc_template_id: null,
    }
}

function createDocumentWizardStep1State(): DocumentWizardStep1State {
    return {
        rows: [],
    }
}

export const documentWizardState = reactive<DocumentWizardState>({
    activeStep: 1,
    defaults: createDocumentWizardDefaults(),
    step1: createDocumentWizardStep1State(),
})

export function resetDocumentWizardState(): void {
    documentWizardState.activeStep = 1
    Object.assign(documentWizardState.defaults, createDocumentWizardDefaults())
    Object.assign(documentWizardState.step1, createDocumentWizardStep1State())
}
