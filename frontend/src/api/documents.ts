import { reactive } from 'vue'
import { http } from './http'
import type { Pagination } from './types'
import type {
    Attachment,
    AttachmentEvidenceProjection,
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
    DocumentEvidenceReviewPayload,
    DocumentLifecycleActionCode,
    DocumentLifecycleEvidenceResult,
    DocumentLifecycleEvidenceTiming,
    DocumentImpactPreviewPayload,
    DocumentImpactPreviewResult,
    DocumentListParams,
    DocumentUpdatePayload,
    AttachmentUploadMetadata,
    DocumentWizardAttachmentPreviewResult,
    DocumentWizardBatchCreatePayload,
    DocumentWizardBatchCreateResult,
    DocumentWizardBatchDefaults,
    DocumentWizardFeePreviewResult,
    DocumentWizardTaskPreviewResult,
    DocumentWizardStep1State,
    DocumentWizardState,
    GrantEvidenceCandidate,
    GrantEvidenceReviewPayload,
    GrantEvidenceReviewResult,
    ReviewedDocumentEvidenceOption,
    ReviewedReplyDocumentOption,
} from './documents.types'

interface BackendAttachment {
    id: string
    document_id?: string
    file_name: string
    file_size: number
    mime_type?: string
    uploaded_at: string
    official_file_role?: string | null
    source_role_alias?: string | null
    external_upload_position?: string | null
    content_hash?: string | null
    package_usage_hint?: string | null
    is_archive_evidence?: boolean
    is_receipt_evidence?: boolean
    evidence_version_id: string | null
    role: string | null
    creator_id: string | null
    reviewer_id: string | null
    review_state: 'PENDING' | 'APPROVED' | 'REJECTED' | null
    is_current: boolean
    is_final: boolean
}

interface BackendDocument {
    id: string
    case_id?: string | null
    client_id?: string | null
    client_name?: string | null
    doc_template_id?: string | null
    template_code?: string | null
    direction: 'IN' | 'OUT'
    doc_type?: 'OFFICIAL_IN' | 'OFFICIAL_OUT' | 'CLIENT_IN' | 'CLIENT_OUT' | null
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
    description?: string | null
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | 'LEGACY_UNVERIFIED' | null
}

interface BackendEvidenceReviewResult {
    case_id: string
    evidence_version_id: string
    creator_id: string
    reviewer_id: string
    decision: 'APPROVE' | 'REJECT'
    review_state: 'APPROVED' | 'REJECTED'
    reviewed_at: string
    idempotency_key: string
}

export interface EvidenceReviewExpectation {
    expectedReviewerId: string
    role: string
    isCurrent: boolean
    isFinal: boolean
}

function mapAttachment(input: BackendAttachment): Attachment {
    return {
        id: input.id,
        filename: input.file_name,
        file_size: Number(input.file_size || 0),
        content_type: input.mime_type,
        created_at: input.uploaded_at,
        document_id: input.document_id,
        official_file_role: input.official_file_role ?? null,
        source_role_alias: input.source_role_alias ?? null,
        external_upload_position: input.external_upload_position ?? null,
        content_hash: input.content_hash ?? null,
        package_usage_hint: input.package_usage_hint ?? null,
        is_archive_evidence: input.is_archive_evidence ?? false,
        is_receipt_evidence: input.is_receipt_evidence ?? false,
        evidence_version_id: input.evidence_version_id,
        role: input.role,
        creator_id: input.creator_id,
        reviewer_id: input.reviewer_id,
        review_state: input.review_state,
        is_current: input.is_current,
        is_final: input.is_final,
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
        ref_no: input.ref_no || undefined,
        direction: input.direction,
        doc_date: input.doc_date || undefined,
        title: input.title || 'Untitled Document',
        doc_type: input.doc_type || undefined,
        description: input.description ?? input.extra_data ?? undefined,
        created_at: input.created_at,
        updated_at: input.updated_at,
        reply_to_id: input.reply_to_id || undefined,
        need_reply: input.need_reply ?? undefined,
        reply_date: input.reply_date || undefined,
        case_no: input.case_no || undefined,
        outgoing_reg_no: input.outgoing_reg_no || undefined,
        forward_date: input.forward_date || undefined,
        official_due_date: input.official_due_date ?? null,
        official_due_date_source: input.official_due_date_source ?? null,
        official_due_date_status: input.official_due_date_status ?? null,
        attachments: (input.attachments || []).map(mapAttachment),
    }
}

export function selectReviewedEvidenceOptions(
    documents: Document[],
    caseId: string,
): ReviewedDocumentEvidenceOption[] {
    if (!caseId.trim()) return []
    const options = documents.flatMap((document) => {
        if (document.case_id !== caseId) return []
        return (document.attachments || []).flatMap((attachment) => {
            const role = String(attachment.role || attachment.official_file_role || '').trim()
            if (
                attachment.document_id && attachment.document_id !== document.id
                || attachment.review_state !== 'APPROVED'
                || attachment.is_current !== true
                || attachment.is_final !== true
                || !attachment.evidence_version_id
                || !attachment.content_hash
                || !/^sha256:[0-9a-f]{64}$/.test(attachment.content_hash)
                || !role
            ) return []
            return [{
                document_id: document.id,
                case_id: caseId,
                title: document.title,
                attachment_id: attachment.id,
                filename: attachment.filename,
                role,
                evidence_version_id: attachment.evidence_version_id,
                content_hash: attachment.content_hash,
            }]
        })
    })
    const identityCounts = new Map<string, number>()
    for (const option of options) {
        const identity = JSON.stringify([
            option.document_id,
            option.evidence_version_id,
            option.content_hash,
        ])
        identityCounts.set(identity, (identityCounts.get(identity) || 0) + 1)
    }
    return options.filter((option) => identityCounts.get(JSON.stringify([
        option.document_id,
        option.evidence_version_id,
        option.content_hash,
    ])) === 1)
}

export function selectReviewedReplyDocumentOptions(
    documents: Document[],
    caseId: string,
    sourceDocumentId: string,
): ReviewedReplyDocumentOption[] {
    if (!sourceDocumentId.trim()) return []
    const byDocument = new Map(documents.map((document) => [document.id, document]))
    return selectReviewedEvidenceOptions(documents, caseId).flatMap((option) => {
        const document = byDocument.get(option.document_id)
        if (!document || document.direction !== 'OUT' || document.reply_to_id !== sourceDocumentId) return []
        return [{ ...option, ref_no: document.ref_no, doc_date: document.doc_date }]
    })
}

export function selectReviewedReceiptEvidenceOptions(
    documents: Document[],
    caseId: string,
): ReviewedDocumentEvidenceOption[] {
    if (!caseId.trim()) return []
    const receiptRoles = new Set(['ELECTRONIC_RECEIPT', 'RECEIPT_PDF', 'MERGED_PDF'])
    const options = documents.flatMap((document) => {
        if (document.case_id !== caseId) return []
        return (document.attachments || []).flatMap((attachment) => {
            const role = String(attachment.role || attachment.official_file_role || '').trim()
            if (
                attachment.document_id && attachment.document_id !== document.id
                || attachment.review_state !== 'APPROVED'
                || attachment.is_current !== true
                || !attachment.evidence_version_id
                || !attachment.content_hash
                || !/^sha256:[0-9a-f]{64}$/.test(attachment.content_hash)
                || !role
                || !(
                    attachment.is_receipt_evidence
                    || attachment.is_archive_evidence
                    || receiptRoles.has(role)
                )
            ) return []
            return [{
                document_id: document.id,
                case_id: caseId,
                title: document.title,
                attachment_id: attachment.id,
                filename: attachment.filename,
                role,
                evidence_version_id: attachment.evidence_version_id,
                content_hash: attachment.content_hash,
            }]
        })
    })
    const identityCounts = new Map<string, number>()
    for (const option of options) {
        const identity = JSON.stringify([
            option.document_id,
            option.evidence_version_id,
            option.content_hash,
        ])
        identityCounts.set(identity, (identityCounts.get(identity) || 0) + 1)
    }
    return options.filter((option) => identityCounts.get(JSON.stringify([
        option.document_id,
        option.evidence_version_id,
        option.content_hash,
    ])) === 1)
}

export async function getCaseDocumentsWithEvidence(caseId: string): Promise<Document[]> {
    if (!caseId.trim()) return []
    const page = await getDocuments({ case_id: caseId, page: 1, page_size: 100 })
    const documents = await Promise.all(page.items.map((document) => getDocument(document.id)))
    return documents.filter((document) => document.case_id === caseId)
}

export async function recordDocumentLifecycleEvidence(
    action: DocumentLifecycleActionCode,
    caseId: string,
    evidence: ReviewedDocumentEvidenceOption,
    timing: DocumentLifecycleEvidenceTiming,
): Promise<DocumentLifecycleEvidenceResult> {
    const paths: Record<DocumentLifecycleActionCode, string> = {
        ACCEPTANCE_NOTICE: 'acceptance-notice',
        PRELIMINARY_START: 'preliminary-start',
        PRELIMINARY_PASS: 'preliminary-pass',
        PUBLICATION_NOTICE: 'publication-notice',
        SUBSTANTIVE_START: 'substantive-start',
    }
    if (
        evidence.case_id !== caseId
        || !evidence.document_id
        || !evidence.evidence_version_id
        || !/^sha256:[0-9a-f]{64}$/.test(evidence.content_hash)
        || !timing.effective_at
        || !timing.idempotency_key
    ) throw new Error('请选择当前案件已复核证据')
    const response = await http.post<DocumentLifecycleEvidenceResult>(
        `/documents/${evidence.document_id}/lifecycle/${paths[action]}`,
        {
            evidence_version_id: evidence.evidence_version_id,
            effective_at: timing.effective_at,
            occurred_at: timing.occurred_at,
            idempotency_key: timing.idempotency_key,
        },
    )
    return response.data
}

function toCreatePayload(data: DocumentCreatePayload): Record<string, unknown> {
    return {
        case_id: String(data.case_id),
        doc_template_id: data.doc_template_id ?? null,
        doc_type: data.doc_type ?? null,
        direction: data.direction,
        doc_date: data.doc_date,
        title: data.title,
        extra_data: data.description || null,
        reply_to_id: data.reply_to_id || null,
        official_due_date: data.official_due_date || null,
        official_due_date_source: data.official_due_date_source || null,
        official_due_date_status: data.official_due_date_status || null,
    }
}

function toUpdatePayload(data: DocumentUpdatePayload): Record<string, unknown> {
    const payload: Record<string, unknown> = {}

    if (data.case_id !== undefined) payload.case_id = data.case_id || null
    if (data.doc_template_id !== undefined) payload.doc_template_id = data.doc_template_id
    if (data.doc_type !== undefined) payload.doc_type = data.doc_type || null
    if (data.direction !== undefined) payload.direction = data.direction
    if (data.doc_date !== undefined) payload.doc_date = data.doc_date || null
    if (data.title !== undefined) payload.title = data.title || null
    if (data.description !== undefined) payload.description = data.description || null
    if (data.reply_to_id !== undefined) payload.reply_to_id = data.reply_to_id || null
    if (data.need_reply !== undefined) payload.need_reply = data.need_reply
    if (data.reply_date !== undefined) payload.reply_date = data.reply_date || null
    if (data.official_due_date !== undefined) {
        payload.official_due_date = data.official_due_date || null
    }
    if (data.official_due_date_source !== undefined) {
        payload.official_due_date_source = data.official_due_date_source || null
    }
    if (data.official_due_date_status !== undefined) {
        payload.official_due_date_status = data.official_due_date_status || null
    }

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
            ...(trimToUndefined(data.defaults.official_due_date ?? undefined)
                ? { official_due_date: trimToUndefined(data.defaults.official_due_date ?? undefined) }
                : {}),
            ...(data.defaults.official_due_date_source
                ? { official_due_date_source: data.defaults.official_due_date_source }
                : {}),
            ...(data.defaults.official_due_date_status
                ? { official_due_date_status: data.defaults.official_due_date_status }
                : {}),
        },
        rows: data.rows.map((row) => ({
            case_id: row.case_id,
            ...(trimToUndefined(row.title) ? { title: trimToUndefined(row.title) } : {}),
            ...(trimToUndefined(row.doc_date) ? { doc_date: trimToUndefined(row.doc_date) } : {}),
            ...(trimToUndefined(row.ref_no) ? { ref_no: trimToUndefined(row.ref_no) } : {}),
            ...(row.need_reply !== undefined ? { need_reply: row.need_reply } : {}),
            ...(trimToUndefined(row.reply_to_id) ? { reply_to_id: trimToUndefined(row.reply_to_id) } : {}),
            ...(trimToUndefined(row.extra_data) ? { extra_data: trimToUndefined(row.extra_data) } : {}),
            ...(trimToUndefined(row.official_due_date ?? undefined)
                ? { official_due_date: trimToUndefined(row.official_due_date ?? undefined) }
                : {}),
            ...(row.official_due_date_source
                ? { official_due_date_source: row.official_due_date_source }
                : {}),
            ...(row.official_due_date_status
                ? { official_due_date_status: row.official_due_date_status }
                : {}),
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
        attachment_rows: data.attachment_rows?.map((row) => ({
                row_index: row.row_index,
                case_id: row.case_id,
                template_code: row.template_code,
                ...(trimToUndefined(row.output_name ?? undefined) ? { output_name: trimToUndefined(row.output_name ?? undefined) } : {}),
                output_file_name: row.output_file_name,
                output_format: row.output_format,
                candidate_source_kind: row.candidate_source_kind,
                ...(trimToUndefined(row.remark ?? undefined) ? { remark: trimToUndefined(row.remark ?? undefined) } : {}),
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
        doc_type,
        case_no,
        template_code,
        direction,
        doc_template_id,
        case_id,
        client_id,
        need_reply,
        replied,
        has_attachment,
        date_from,
        date_to,
    } = params
    const query = new URLSearchParams()
    query.set('page', String(page))
    query.set('page_size', String(page_size))
    if (q) query.set('q', q)
    if (doc_name) query.set('doc_name', doc_name)
    if (case_no) query.set('case_no', case_no)
    if (template_code) query.set('template_code', template_code)
    if (direction) query.set('direction', direction)
    if (doc_template_id) query.set('doc_template_id', doc_template_id)
    if (case_id) query.set('case_id', case_id)
    if (client_id) query.set('client_id', client_id)
    if (need_reply !== undefined) query.set('need_reply', String(need_reply))
    if (replied !== undefined) query.set('replied', String(replied))
    if (has_attachment !== undefined) query.set('has_attachment', String(has_attachment))
    if (date_from) query.set('date_from', date_from)
    if (date_to) query.set('date_to', date_to)
    for (const value of doc_type || []) {
        query.append('doc_type', value)
    }

    const response = await http.get<Pagination<BackendDocument>>('/documents', {
        params: query,
    })

    return {
        ...response.data,
        items: response.data.items.map(mapDocument),
    }
}

/**
 * Export the filtered document list as an Excel blob (US-WD-06)
 */
export async function exportDocuments(
    params: Omit<DocumentListParams, 'page' | 'page_size'> = {},
): Promise<Blob> {
    const {
        q,
        doc_name,
        doc_type,
        case_no,
        template_code,
        direction,
        doc_template_id,
        case_id,
        client_id,
        need_reply,
        replied,
        has_attachment,
        date_from,
        date_to,
    } = params
    const query = new URLSearchParams()
    if (q) query.set('q', q)
    if (doc_name) query.set('doc_name', doc_name)
    if (case_no) query.set('case_no', case_no)
    if (template_code) query.set('template_code', template_code)
    if (direction) query.set('direction', direction)
    if (doc_template_id) query.set('doc_template_id', doc_template_id)
    if (case_id) query.set('case_id', case_id)
    if (client_id) query.set('client_id', client_id)
    if (need_reply !== undefined) query.set('need_reply', String(need_reply))
    if (replied !== undefined) query.set('replied', String(replied))
    if (has_attachment !== undefined) query.set('has_attachment', String(has_attachment))
    if (date_from) query.set('date_from', date_from)
    if (date_to) query.set('date_to', date_to)
    for (const value of doc_type || []) {
        query.append('doc_type', value)
    }

    const response = await http.get<Blob>('/documents/export', {
        params: query,
        responseType: 'blob',
    })
    return response.data
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

export async function reviewDocumentEvidence(
    documentId: string,
    evidenceVersionId: string,
    payload: DocumentEvidenceReviewPayload,
    expectation: EvidenceReviewExpectation,
): Promise<AttachmentEvidenceProjection> {
    const expectedReviewState = payload.decision === 'APPROVE' ? 'APPROVED' : 'REJECTED'
    return executeEvidenceReviewCommand(
        async () => {
            const response = await http.post<BackendEvidenceReviewResult>(
                `/documents/evidence-versions/${evidenceVersionId}/review`,
                payload,
            )
            return mapEvidenceReviewResult(
                response.data,
                evidenceVersionId,
                payload,
                expectation,
            )
        },
        async () => {
            const document = await getDocument(documentId)
            const attachment = document.attachments?.find(
                (item) => item.evidence_version_id === evidenceVersionId
            )
            if (
                attachment?.evidence_version_id === evidenceVersionId &&
                attachment.role === expectation.role &&
                attachment.creator_id &&
                attachment.reviewer_id === expectation.expectedReviewerId &&
                attachment.review_state === expectedReviewState &&
                typeof attachment.is_current === 'boolean' &&
                typeof attachment.is_final === 'boolean'
            ) {
                return {
                    evidence_version_id: attachment.evidence_version_id,
                    role: attachment.role,
                    creator_id: attachment.creator_id,
                    reviewer_id: attachment.reviewer_id,
                    review_state: attachment.review_state,
                    is_current: attachment.is_current,
                    is_final: attachment.is_final,
                }
            }
            throw new Error('未找到与复核命令完全一致的持久状态')
        },
    )
}

export function shouldReconcileEvidenceReview(error: unknown): boolean {
    if (typeof error !== 'object' || error === null) return false
    const candidate = error as { status?: unknown; code?: unknown }
    return candidate.status === 0 && candidate.code === 'UNKNOWN_ERROR'
}

export async function executeEvidenceReviewCommand<T>(
    postReview: () => Promise<T>,
    reconcileDocument: () => Promise<T>,
): Promise<T> {
    try {
        return await postReview()
    } catch (error) {
        if (!shouldReconcileEvidenceReview(error)) throw error
        try {
            return await reconcileDocument()
        } catch {
            // Preserve the original unknown mutation outcome when reconciliation cannot prove it.
            throw error
        }
    }
}

function mapEvidenceReviewResult(
    result: BackendEvidenceReviewResult,
    evidenceVersionId: string,
    payload: DocumentEvidenceReviewPayload,
    expectation: EvidenceReviewExpectation,
): AttachmentEvidenceProjection {
    const expectedReviewState = payload.decision === 'APPROVE' ? 'APPROVED' : 'REJECTED'
    requireEqual(result.case_id, payload.case_id)
    requireEqual(result.decision, payload.decision)
    requireEqual(result.reviewed_at, payload.reviewed_at)
    requireEqual(result.idempotency_key, payload.idempotency_key)
    return {
        evidence_version_id: requireEqual(result.evidence_version_id, evidenceVersionId),
        role: requireText(expectation.role),
        creator_id: requireText(result.creator_id),
        reviewer_id: requireEqual(result.reviewer_id, expectation.expectedReviewerId),
        review_state: requireEqual(result.review_state, expectedReviewState),
        is_current: requireBoolean(expectation.isCurrent),
        is_final: requireBoolean(expectation.isFinal),
    }
}

function requireText(value: unknown): string {
    if (typeof value !== 'string' || !value.trim()) throw new Error('证据复核响应不一致')
    return value
}

function requireEqual<T extends string>(value: unknown, expected: T | undefined): T {
    if (expected === undefined || value !== expected) throw new Error('证据复核响应不一致')
    return expected
}

function requireBoolean(value: unknown): boolean {
    if (typeof value !== 'boolean') throw new Error('证据复核响应不一致')
    return value
}

export async function listGrantEvidenceCandidates(
    documentId: string
): Promise<GrantEvidenceCandidate[]> {
    const response = await http.get<GrantEvidenceCandidate[]>(
        `/documents/${documentId}/grant-evidence-candidates`
    )
    return response.data
}

export async function reviewGrantEvidence(
    candidateId: string,
    payload: GrantEvidenceReviewPayload
): Promise<GrantEvidenceReviewResult> {
    const response = await http.post<GrantEvidenceReviewResult>(
        `/documents/grant-evidence-candidates/${candidateId}/review`,
        {
            decision: payload.decision === 'APPROVE' ? 'APPROVED' : 'REJECTED',
            reason: payload.reason,
        }
    )
    return response.data
}

/**
 * Create a new document
 */
export async function createDocument(data: DocumentCreatePayload): Promise<Document> {
    const response = await http.post<BackendDocument>('/documents', toCreatePayload(data))
    return mapDocument(response.data)
}

export async function previewDocumentImpact(
    data: DocumentImpactPreviewPayload
): Promise<DocumentImpactPreviewResult> {
    const response = await http.post<DocumentImpactPreviewResult>('/documents/impact-preview', data)
    return response.data
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
export async function uploadAttachment(
    docId: string | number,
    file: File,
    metadata: AttachmentUploadMetadata = {}
): Promise<Attachment> {
    const formData = new FormData()
    formData.append('file', file)
    if (metadata.official_file_role) {
        formData.append('official_file_role', metadata.official_file_role)
    }
    if (metadata.source_role_alias) {
        formData.append('source_role_alias', metadata.source_role_alias)
    }
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
