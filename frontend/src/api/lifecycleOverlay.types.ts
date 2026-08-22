export type OverlayCenterAxis =
    | 'BUSINESS_STAGE'
    | 'OFFICIAL_PROCEDURE_STAGE'
    | 'LEGAL_STATUS'

export type OverlayWarningKind =
    | 'UNVERIFIED'
    | 'CUSTOMER_DECISION_GATE'
    | 'CONFLICT'
    | 'REFERENCE_ONLY'

export type OverlayFeeRelatedFactKind =
    | 'DRAFT'
    | 'PAY_LIST'
    | 'PAYMENT'
    | 'OFFICIAL_EVIDENCE'

export type OverlayGateResolutionStatus = 'RESOLVED' | 'UNRESOLVED'

export type BusinessStage =
    | 'NEW_CASE'
    | 'FILING_PREPARATION'
    | 'WAITING_EXTERNAL_RECEIPT'
    | 'PROSECUTION_MANAGEMENT'
    | 'OA_REPLY_IN_PROGRESS'
    | 'GRANT_REGISTRATION_IN_PROGRESS'
    | 'POST_GRANT_MAINTENANCE'
    | 'CLOSED'

export type OfficialProcedureStage =
    | 'NOT_SUBMITTED'
    | 'SUBMITTED_WAITING_RECEIPT'
    | 'SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE'
    | 'ACCEPTED'
    | 'PRELIMINARY_EXAMINATION'
    | 'RECTIFICATION_RESPONSE'
    | 'PUBLISHED'
    | 'SUBSTANTIVE_EXAMINATION'
    | 'OFFICE_ACTION_RESPONSE'
    | 'REEXAMINATION'
    | 'GRANT_REGISTRATION'
    | 'GRANT_ANNOUNCED'
    | 'PROCEDURE_CLOSED'

export type LegalStatus =
    | 'NOT_ESTABLISHED'
    | 'APPLICATION_PENDING'
    | 'APPLICATION_REJECTED'
    | 'APPLICATION_WITHDRAWN'
    | 'APPLICATION_ABANDONED'
    | 'PATENT_IN_FORCE'
    | 'PATENT_TERMINATED'
    | 'PATENT_EXPIRED'
    | 'PATENT_INVALIDATED'
    | 'UNKNOWN'

export type ActivityLane = 'LIFECYCLE' | 'DOCUMENT' | 'FEE'

export type ConfirmationStatus = 'NEEDS_REVIEW' | 'CONFIRMED' | 'LEGACY_UNVERIFIED'

export type EvidenceRole =
    | 'FILING_FULL_WORD'
    | 'TRACKED_REVISED_WORD'
    | 'FILING_COMPONENT'
    | 'EXTERNAL_XML_PACKAGE'
    | 'OFFICIAL_SUBMISSION_LIST'
    | 'OFFICIAL_FINAL_PDF'
    | 'SUBMITTED_XML'
    | 'OFFICIAL_RECEIPT'
    | 'CLIENT_LETTER_WORD'
    | 'RAW_ATTACHMENT'
    | 'GENERATED_ATTACHMENT'
    | 'OA_STRUCTURED_ATTACHMENT'

export type EvidenceVersionState = 'DRAFT' | 'FINAL'
export type EvidenceReviewState = 'PENDING' | 'APPROVED' | 'REJECTED'
export type EvidenceDerivationType =
    | 'REVISION'
    | 'COMPONENT_EXTRACTION'
    | 'FORMAT_CONVERSION'
    | 'OFFICIAL_RECOGNITION'
    | 'EXTERNAL_SUBMISSION'
    | 'RECEIPT_LINK'
    | 'CUSTOMER_LETTER_RENDER'
    | 'OA_REPLY_PREPARATION'

export type FeeDifferenceReviewState = 'MATCHED' | 'SOURCE_PENDING' | 'REVIEW_REQUIRED'
export type FeeSourceStatus = 'VERIFIED' | 'REVIEW_REQUIRED' | 'LEGACY_UNVERIFIED'
export type FeeDomain = 'GOV' | 'SERVICE'
export type FeeEstimateStatus = 'ESTIMATE'
export type FeeObligationStatus = 'RECOGNIZED' | 'SUPERSEDED'
export type FeeClientInstructionStatus = 'PENDING' | 'PAY' | 'HOLD' | 'ABANDON'
export type FeeObligationDraftStatus = 'NOT_CREATED' | 'CREATED'
export type FeePayListStatus = 'NOT_CREATED' | 'CREATED'
export type FeePaymentStatus = 'UNPAID' | 'PAID'
export type FeeOfficialEvidenceStatus = 'PENDING' | 'VERIFIED' | 'NOT_APPLICABLE'
export type DecisionGateCode =
    | 'DG-FEE-APPLICATION-DRAFT'
    | 'DG-FEE-GRANT-YEAR-DRAFT'
    | 'DG-FEE-FUTURE-ANNUITY'
    | 'DG-GRANT-EVIDENCE-SOURCE'
    | 'DG-GRANT-MANUAL-REVIEW'
    | 'DG-PAYMENT-WORKBOOK'
    | 'DG-SERVICE-RATE-VERSION'
    | 'DG-LEGACY-FORM-CLASS'

export interface EvidenceReference {
    caseId: string
    evidenceKind: string
    objectType: string
    objectId: string
    contentHash: string
    capturedAt: string
}

export interface EvidenceVersionResult {
    evidenceVersionId: string
    caseId: string
    documentId: string
    attachmentId: string
    lineageKey: string
    role: EvidenceRole
    versionNumber: number
    state: EvidenceVersionState
    creatorId: string
    reviewState: EvidenceReviewState
    reviewerId: string | null
    reviewedAt: string | null
    finalSubmittedAt: string | null
    contentHash: string
    isCurrent: boolean
    isFinal: boolean
}

export interface EvidenceDerivationResult {
    evidenceDerivationId: string
    caseId: string
    parentEvidenceVersionId: string
    childEvidenceVersionId: string
    derivationType: EvidenceDerivationType
    actorId: string
    derivedAt: string
    sourceSnapshot: string
}

export interface FeeObligationStatuses {
    estimateStatus: FeeEstimateStatus | null
    obligationStatus: FeeObligationStatus
    clientInstructionStatus: FeeClientInstructionStatus
    draftStatus: FeeObligationDraftStatus
    payListStatus: FeePayListStatus
    paymentStatus: FeePaymentStatus
    officialEvidenceStatus: FeeOfficialEvidenceStatus
}

export interface LifecycleOverlayQuery {
    afterSequence: number
    limit: number
    asOfRevision: number | null
}

export interface OverlayCenterSnapshot {
    businessStage: BusinessStage | null
    officialProcedureStage: OfficialProcedureStage | null
    legalStatus: LegalStatus | null
    effectiveAt: string | null
    verificationStatus: ConfirmationStatus | null
    sourceEventId: string | null
}

export interface OverlayCenterAxisChange {
    previousValue: BusinessStage | OfficialProcedureStage | LegalStatus | null
    currentValue: BusinessStage | OfficialProcedureStage | LegalStatus | null
}

export interface OverlayDocumentEvidence {
    version: EvidenceVersionResult
    derivations: readonly EvidenceDerivationResult[]
}

export interface OverlayWorkPackageReceipt {
    receiptId: string
    receiptKind: string
    receiptAttachmentId: string | null
    receivingCaseNo: string | null
    submitter: string | null
    receivedAt: string | null
    archiveStatus: string
}

export interface OverlayWorkPackage {
    packageId: string
    packageKind: string
    status: string
    sourceDocumentId: string | null
    replyDocumentId: string | null
    manifestEvidenceVersionIds: readonly string[]
    receipts: readonly OverlayWorkPackageReceipt[]
    missingGateCodes: readonly string[]
}

export interface OverlayTask {
    taskId: string
    documentId: string | null
    taskTemplateId: string | null
    title: string | null
    dueDate: string | null
    internalDueDate: string | null
    status: string
    doneAt: string | null
}

export interface OverlayFeeLine {
    lineId: string
    feeCode: string
    feeName: string
    feeYearKey: number
    officialFullAmount: string | null
    reductionRatio: string
    payableAmount: string
    sourceAmount: string | null
    sourceDate: string | null
    differenceReviewState: FeeDifferenceReviewState
}

export interface OverlayFeeRelatedFact {
    kind: OverlayFeeRelatedFactKind
    objectId: string
    status: string
}

export interface OverlayFeeObligation {
    obligationId: string
    sourceActivityId: string
    sourceDocumentId: string | null
    sourceStatus: FeeSourceStatus
    feeDomain: FeeDomain
    obligationType: string
    dueDate: string | null
    currency: string
    statuses: FeeObligationStatuses
    lines: readonly OverlayFeeLine[]
    relatedFacts: readonly OverlayFeeRelatedFact[]
    supersedesObligationId: string | null
    supersedeReason: string | null
}

export interface OverlayWarning {
    kind: OverlayWarningKind
    code: string
    message: string
    activityId: string | null
    sourceObjectType: string | null
    sourceObjectId: string | null
}

export interface OverlayDecisionGate {
    gateCode: DecisionGateCode
    requestedScopeKey: string
    resolutionStatus: OverlayGateResolutionStatus
    gateId: string | null
    resolvedScopeKey: string | null
    decisionValue: string | null
    sourceReference: string | null
    sourceVersion: string | null
    confirmedBy: string | null
    effectiveAt: string | null
    unresolvedReason: string | null
}

export interface OverlayLegacyConflict {
    code: string
    activityId: string | null
    message: string | null
}

export interface OverlayMilestone {
    sequence: number
    activityId: string
    lane: ActivityLane
    activityType: string
    sourceActivityId: string | null
    effectiveAt: string
    confirmationStatus: ConfirmationStatus
    centerChanges: Readonly<Partial<Record<OverlayCenterAxis, OverlayCenterAxisChange>>>
    documentEvidence: readonly OverlayDocumentEvidence[]
    workPackages: readonly OverlayWorkPackage[]
    tasks: readonly OverlayTask[]
    feeObligations: readonly OverlayFeeObligation[]
    evidenceSummary: readonly EvidenceReference[]
    warnings: readonly OverlayWarning[]
}

export interface LifecycleOverlay {
    caseId: string
    lifecycleRevision: number
    generatedAt: string
    centerSnapshot: OverlayCenterSnapshot
    milestones: readonly OverlayMilestone[]
    decisionGates: readonly OverlayDecisionGate[]
    warnings: readonly OverlayWarning[]
    legacyConflicts: readonly OverlayLegacyConflict[]
    nextCursor: number | null
    hasMore: boolean
}
