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
    ref_no?: string
    client_id?: string
    client_name?: string
    doc_template_id?: string | null
    doc_date?: string
    doc_type?: 'OFFICIAL_IN' | 'OFFICIAL_OUT' | 'CLIENT_IN' | 'CLIENT_OUT'
    description?: string
    outgoing_reg_no?: string | null
    forward_date?: string | null
    created_at?: string
    updated_at?: string
    attachments?: Attachment[]
    reply_to_id?: string
    need_reply?: boolean
    reply_date?: string
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | 'LEGACY_UNVERIFIED' | null
}

export interface DocumentListParams {
    page?: number
    page_size?: number
    q?: string
    doc_name?: string
    doc_type?: Array<'OFFICIAL_IN' | 'OFFICIAL_OUT' | 'CLIENT_IN' | 'CLIENT_OUT'>
    case_no?: string
    template_code?: string
    direction?: 'IN' | 'OUT'
    doc_template_id?: string
    case_id?: string
    client_id?: string
    need_reply?: boolean
    replied?: boolean
    has_attachment?: boolean
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
    doc_type?: 'OFFICIAL_IN' | 'OFFICIAL_OUT' | 'CLIENT_IN' | 'CLIENT_OUT'
    description?: string
    reply_to_id?: string | null
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | null
}

export interface DocumentImpactPreviewPayload {
    case_id: string
    doc_template_id?: string | null
    doc_type?: 'OFFICIAL_IN' | 'OFFICIAL_OUT' | 'CLIENT_IN' | 'CLIENT_OUT'
    direction: 'IN' | 'OUT'
    doc_date: string
    title: string
    ref_no?: string | null
    extra_data?: string | null
    reply_to_id?: string | null
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | null
    description?: string | null
}

export interface DocumentImpactItem {
    kind: string
    title: string
    effect?: string | null
    enabled: boolean
    requires_confirmation: boolean
    document_id?: string | null
    detail?: string | null
}

export interface DocumentImpactPreviewResult {
    case_id: string
    case_no?: string | null
    template_code?: string | null
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | 'LEGACY_UNVERIFIED' | null
    description?: string | null
    status_impacts: DocumentImpactItem[]
    deadline_impacts: DocumentImpactItem[]
    task_impacts: DocumentImpactItem[]
    fee_impacts: DocumentImpactItem[]
    file_status_impacts: DocumentImpactItem[]
    confirmation_required: boolean
    confirmation_items: string[]
    risk_tips: string[]
}

export interface DocumentUpdatePayload {
    title?: string
    direction?: 'IN' | 'OUT'
    case_id?: string
    doc_template_id?: string | null
    doc_date?: string
    doc_type?: 'OFFICIAL_IN' | 'OFFICIAL_OUT' | 'CLIENT_IN' | 'CLIENT_OUT'
    description?: string
    reply_to_id?: string | null
    need_reply?: boolean | null
    reply_date?: string | null
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | null
}

export interface Attachment {
    id: string
    filename: string
    file_size: number
    content_type?: string
    created_at: string
    document_id?: string
    official_file_role?: string | null
    source_role_alias?: string | null
    external_upload_position?: string | null
    content_hash?: string | null
    package_usage_hint?: string | null
    is_archive_evidence?: boolean
    is_receipt_evidence?: boolean
    evidence_version_id?: string | null
    role?: string | null
    creator_id?: string | null
    reviewer_id?: string | null
    review_state?: 'PENDING' | 'APPROVED' | 'REJECTED' | null
    is_current?: boolean
    is_final?: boolean
}

export interface AttachmentEvidenceProjection {
    evidence_version_id: string
    role: string
    creator_id: string
    reviewer_id: string | null
    review_state: 'PENDING' | 'APPROVED' | 'REJECTED'
    is_current: boolean
    is_final: boolean
}

export interface DocumentEvidenceReviewPayload {
    case_id: string
    decision: 'APPROVE' | 'REJECT'
    reviewed_at: string
    idempotency_key: string
}

export interface GrantEvidenceFact {
    name: string
    raw_value: string
}

export interface GrantEvidenceConflict {
    name: string
    raw_values: string[]
}

export interface GrantEvidenceCandidate {
    candidate_id: string
    case_id: string
    document_id: string
    evidence_version_id: string
    terminal_event_id: string
    source_config_id: string
    source_record_id: string
    source_version: string
    original_reference: string
    acquisition_method: string
    acquired_at: string
    evidence_scope: 'GRANT_ANNOUNCEMENT' | 'PATENT_REGISTER'
    proposal_role_config_id: string
    proposed_by: string
    proposed_at: string
    review_status: 'PENDING' | 'APPROVED' | 'REJECTED'
    reviewer_id: string | null
    reviewed_at: string | null
    review_reason: string | null
    acquisition_snapshot_hash: string
    candidate_snapshot_hash: string
    facts: GrantEvidenceFact[]
    conflicts: GrantEvidenceConflict[]
}

export interface GrantEvidenceReviewPayload {
    decision: 'APPROVE' | 'REJECT'
    reason: string
}

export interface GrantEvidenceReviewResult {
    candidate_id: string
    evidence_version_id: string
    review_status: 'APPROVED' | 'REJECTED'
    reviewer_id: string
    reviewed_at: string
    candidate_snapshot_hash: string
    review_role_config_id: string
    review_role_config_snapshot_hash: string
    disposition: 'CHANGED' | 'REUSED'
}

export interface AttachmentUploadMetadata {
    official_file_role?: string | null
    source_role_alias?: string | null
}

export interface AttachmentManifestItem {
    attachment_id: string
    document_id: string
    file_name: string
    official_file_role?: string | null
    source_role_alias?: string | null
    external_upload_position?: string | null
    content_hash?: string | null
    package_usage_hint?: string | null
    is_archive_evidence: boolean
    is_receipt_evidence: boolean
}

export interface AttachmentManifestSummary {
    intake_gate_roles: AttachmentManifestItem[]
    filing_roles: AttachmentManifestItem[]
    oa_roles: AttachmentManifestItem[]
    archive_roles: AttachmentManifestItem[]
    historical_alias_roles: AttachmentManifestItem[]
    missing_intake_gate_roles: string[]
}

export interface DocumentWizardBatchDefaults {
    direction: 'IN' | 'OUT'
    doc_date: string
    doc_template_id: string | null
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | null
}

export interface DocumentWizardBatchRowDraft {
    case_id: string
    title?: string
    doc_date?: string
    ref_no?: string
    need_reply?: boolean
    reply_to_id?: string
    extra_data?: string
    official_due_date?: string | null
    official_due_date_source?: 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE' | null
    official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | null
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
    fee_rows?: DocumentWizardFeeFinalRowDraft[]
    attachment_rows?: DocumentWizardAttachmentFinalRowDraft[]
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

export interface DocumentWizardFeePreviewFeeItem {
    fee_code?: string | null
    fee_name?: string | null
    fee_type: string
    quantity?: string | null
    unit_price?: string | null
    amount: string
    remark?: string | null
}

export interface DocumentWizardFeePreviewItem {
    row_index: number
    case_id: string
    case_no?: string
    source_title?: string
    document_title?: string
    fee_draft_type: string
    fee_items: DocumentWizardFeePreviewFeeItem[]
    skip_this_candidate: boolean
}

export interface DocumentWizardFeePreviewResult {
    total_candidates: number
    items: DocumentWizardFeePreviewItem[]
}

export interface DocumentWizardAttachmentPreviewItem {
    row_index: number
    case_id: string
    case_no?: string
    source_title?: string
    document_title?: string
    template_code: string
    template_name?: string
    output_name?: string | null
    output_file_name: string
    output_format: string
    candidate_source_kind: string
    generate_this_candidate: boolean
    remark?: string | null
}

export interface DocumentWizardAttachmentPreviewResult {
    total_candidates: number
    items: DocumentWizardAttachmentPreviewItem[]
}

export interface DocumentWizardAttachmentFinalRowDraft {
    row_index: number
    case_id: string
    template_code: string
    output_name?: string | null
    output_file_name: string
    output_format: string
    candidate_source_kind: string
    remark?: string | null
}

export interface DocumentWizardFeeFinalRowDraft {
    row_index: number
    case_id: string
    fee_draft_type: string
    skip_this_candidate?: boolean
    fee_items: DocumentWizardFeePreviewFeeItem[]
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
