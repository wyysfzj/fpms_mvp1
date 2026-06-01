/**
 * Official workflow API Types
 */

export type OfficialMoney = string | number

export type OfficialWorkPackageKind = 'FILING_PREP' | 'OA_REPLY'

export type OfficialWorkPackageStatus =
    | 'PREPARING'
    | 'NEEDS_MAINTENANCE'
    | 'NEEDS_CONFIRMATION'
    | 'READY_FOR_EXTERNAL_SUBMIT'
    | 'SUBMITTED'
    | 'WAITING_RECEIPT'
    | 'ARCHIVED'
    | 'EXCEPTION'
    | 'OVERRIDE'

export interface OfficialWorkPackage {
    id: string
    case_id: string
    package_kind: OfficialWorkPackageKind | string
    status: OfficialWorkPackageStatus | string
    source_document_id?: string | null
    reply_document_id?: string | null
    external_system?: string | null
    remark?: string | null
}

export interface OfficialWorkPackageChecklist {
    id: string
    package_id: string
    section_code: string
    item_code: string
    item_label: string
    status: string
    required: boolean
    sort_order?: number | null
    evidence_note?: string | null
}

export interface OfficialWorkPackageManifest {
    id: string
    package_id: string
    attachment_id?: string | null
    official_file_role?: string | null
    source_role_alias?: string | null
    external_upload_position?: string | null
    content_hash?: string | null
    required: boolean
    present: boolean
    sort_order?: number | null
    note?: string | null
}

export interface OfficialWorkPackageReceipt {
    id: string
    package_id: string
    receipt_kind: string
    receipt_attachment_id?: string | null
    receiving_case_no?: string | null
    submitter?: string | null
    received_at?: string | null
    received_file_list?: string | null
    archive_status: string
    note?: string | null
}

export interface OfficialWorkPackageReceiptCreatePayload {
    receipt_kind?: string
    receipt_attachment_id?: string | null
    receiving_case_no?: string | null
    submitter?: string | null
    received_at?: string | null
    received_file_list?: string | null
    archive_status?: string
    note?: string | null
}

export interface OfficialWorkPackageArchivePayload {
    override_reason?: string | null
    follow_up_owner?: string | null
    follow_up_due_date?: string | null
    follow_up_note?: string | null
}

export interface OfficialWorkPackageBlocker {
    blocker_type: string
    item_code?: string | null
    item_label?: string | null
    status: string
    message: string
}

export interface OfficialWorkPackageStatusEvaluation {
    package_id: string
    status: string
    can_archive: boolean
    receipt_hard_gate_satisfied: boolean
    blockers: OfficialWorkPackageBlocker[]
}

export interface OfficialWorkPackageArchiveResult {
    package: OfficialWorkPackage
    evaluation: OfficialWorkPackageStatusEvaluation
}

export interface OfficialFieldCheck {
    code: string
    label: string
    status: string
    message?: string | null
}

export interface OfficialFieldSummary {
    status: string
    missing_codes: string[]
    items: OfficialFieldCheck[]
}

export interface FilingPackageGate {
    role: string
    required: boolean
    status: string
    attachment_id?: string | null
    file_name?: string | null
}

export interface FilingPackageXmlZip {
    status: string
    attachment_id?: string | null
    file_name?: string | null
    placeholder?: string | null
}

export interface FilingPackageFeeSummary {
    draft_count: number
    pay_list_count: number
    official_template_ready: boolean
    blocker_count: number
}

export interface FilingPreparationRefreshPayload {
    require_commission_instruction?: boolean
}

export interface OfficialChecklistUpdatePayload {
    status: string
    evidence_note?: string | null
}

export interface FilingPreparationExternalOperationPayload {
    operation_code: string
    occurred_at: string
    note?: string | null
}

export interface FilingPreparationPackage {
    package: OfficialWorkPackage
    official_field_summary: OfficialFieldSummary
    technical_disclosure_gate: FilingPackageGate
    commission_instruction_gate: FilingPackageGate
    filing_file_roles: OfficialWorkPackageManifest[]
    official_page_checklist: OfficialWorkPackageChecklist[]
    xml_zip: FilingPackageXmlZip
    merged_pdf_archive_status: string
    fee_summary: FilingPackageFeeSummary
}

export interface FilingPreparationChecklistResult {
    package_id: string
    checklist_item: OfficialWorkPackageChecklist
}

export interface OaReplyDocument {
    id: string
    title?: string | null
    template_code?: string | null
    direction: string
    doc_date?: string | null
    ref_no?: string | null
    reply_to_id?: string | null
    need_reply?: boolean | null
    reply_date?: string | null
}

export interface OaReplyAttachment {
    role: string
    status: string
    attachment_id?: string | null
    file_name?: string | null
    external_upload_position?: string | null
}

export interface OaReplyRefreshPayload {
    experiment_data_submitted?: boolean | null
}

export interface OaReplyLinkDocumentPayload {
    reply_document_id: string
}

export interface OaReplyPackage {
    package: OfficialWorkPackage
    source_document?: OaReplyDocument | null
    reply_document?: OaReplyDocument | null
    application_no?: string | null
    applicant_display?: string | null
    notice_code?: string | null
    notice_name?: string | null
    issue_sequence?: string | null
    issue_date?: string | null
    official_due_date?: string | null
    internal_due_date?: string | null
    reply_status: string
    statement_text?: string | null
    statement_word: OaReplyAttachment
    statement_pdf: OaReplyAttachment
    modified_claim_files: OaReplyAttachment[]
    comparison_page: OaReplyAttachment
    proof_files: OaReplyAttachment[]
    experiment_data_submitted: boolean
    official_page_checklist: OfficialWorkPackageChecklist[]
    oa_file_roles: OfficialWorkPackageManifest[]
}

export interface OaReplyChecklistResult {
    package_id: string
    checklist_item: OfficialWorkPackageChecklist
}

export interface LetterHandoffMapping {
    id?: string | null
    format_letter_template_id?: string | null
    format_letter_template_code?: string | null
    output_name_rule?: string | null
    contact_rule_code?: string | null
    salutation_rule_code?: string | null
}

export interface LetterHandoffContact {
    id: string
    contact_name: string
    title?: string | null
    email?: string | null
}

export interface LetterHandoffPreviewAttachment {
    attachment_id?: string | null
    file_name: string
    file_path?: string | null
    attachment_role: string
    required: boolean
    included: boolean
    sort_order?: number | null
}

export interface LetterHandoffPreview {
    source_document_id: string
    case_id: string
    case_no: string
    mapping?: LetterHandoffMapping | null
    template_status: string
    client_contact_id?: string | null
    contact?: LetterHandoffContact | null
    contact_selection_source: string
    salutation_source: string
    salutation_text: string
    generated_word_path?: string | null
    mail_subject: string
    mail_body_draft: string
    attachments: LetterHandoffPreviewAttachment[]
}

export interface LetterHandoffCreatePayload {
    remark?: string | null
}

export interface LetterHandoffStatusUpdatePayload {
    longxia_handoff_status: string
    longxia_handoff_payload?: string | null
    handoff_at?: string | null
}

export interface LetterHandoffAttachment {
    id: string
    handoff_id: string
    attachment_id?: string | null
    file_name: string
    file_path?: string | null
    attachment_role?: string | null
    required: boolean
    included: boolean
    sort_order?: number | null
}

export interface LetterHandoff {
    id: string
    source_document_id: string
    generated_document_id?: string | null
    format_letter_mapping_id?: string | null
    format_letter_template_id?: string | null
    client_contact_id?: string | null
    contact_selection_source?: string | null
    salutation_source?: string | null
    salutation_text?: string | null
    generated_word_path?: string | null
    mail_subject?: string | null
    mail_body_draft?: string | null
    longxia_handoff_status: string
    longxia_handoff_payload?: string | null
    handoff_at?: string | null
    remark?: string | null
    attachments: LetterHandoffAttachment[]
}

export interface LetterHandoffResult {
    preview?: LetterHandoffPreview | null
    handoff: LetterHandoff
}

export interface OfficialFeeDraftLink {
    id: string
    draft_type: string
    status: string
    currency: string
    total_gov: OfficialMoney
    total_service: OfficialMoney
    total_misc: OfficialMoney
    amount: OfficialMoney
    official_fee_reduction_note?: string | null
    official_template_status?: string | null
    official_template_version?: string | null
    official_template_note?: string | null
}

export interface OfficialPayListLink {
    id: number
    pay_list_no?: string | null
    status: string
    currency: string
    planned_pay_date?: string | null
    paid_date?: string | null
    total_amount: OfficialMoney
    official_upload_template_status?: string | null
    official_upload_template_name?: string | null
    official_upload_batch_limit?: number | null
    official_pay_list_boundary_note?: string | null
    manual_payment_status: string
    gov_payment_statuses: string[]
}

export interface OfficialFeeLinkageBlocker {
    blocker_code: string
    blocker_label: string
    source_type: string
    source_id?: string | null
    status: string
    message: string
}

export interface OfficialFeeChecklist {
    id: string
    fee_draft_id?: string | null
    pay_list_id?: number | null
    checklist_code: string
    checklist_label: string
    status: string
    required: boolean
    blocker_reason?: string | null
    sort_order?: number | null
}

export interface OfficialFeeLinkage {
    package_id: string
    case_id: string
    payment_execution_mode: string
    official_excel_template_ready: boolean
    official_excel_generation_allowed: boolean
    fee_drafts: OfficialFeeDraftLink[]
    pay_lists: OfficialPayListLink[]
    checklist: OfficialFeeChecklist[]
    customer_confirmation_blockers: OfficialFeeLinkageBlocker[]
}
