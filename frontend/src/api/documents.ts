import { http } from './http'
import type { Pagination } from './types'
import type {
    Attachment,
    DocTemplate,
    DocTemplateCreatePayload,
    DocTemplateListParams,
    DocTemplateUpdatePayload,
    Document,
    DocumentCreatePayload,
    DocumentListParams,
    DocumentUpdatePayload,
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
    doc_template_id?: string | null
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
        doc_template_id: input.doc_template_id,
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

/**
 * Get paginated list of documents
 */
export async function getDocuments(params: DocumentListParams = {}): Promise<Pagination<Document>> {
    const { page = 1, page_size = 20, direction, case_id, client_id } = params
    const response = await http.get<Pagination<BackendDocument>>('/documents', {
        params: { page, page_size, ...(direction ? { direction } : {}), ...(case_id ? { case_id } : {}), ...(client_id ? { client_id } : {}) }
    })

    return {
        ...response.data,
        items: response.data.items.map(mapDocument),
    }
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
