import { http } from './http'
import type {
    ActivityLane,
    BusinessStage,
    ConfirmationStatus,
    DecisionGateCode,
    EvidenceDerivationResult,
    EvidenceDerivationType,
    EvidenceReference,
    EvidenceReviewState,
    EvidenceRole,
    EvidenceVersionResult,
    EvidenceVersionState,
    FeeClientInstructionStatus,
    FeeDifferenceReviewState,
    FeeDomain,
    FeeEstimateStatus,
    FeeObligationDraftStatus,
    FeeObligationStatus,
    FeeObligationStatuses,
    FeeOfficialEvidenceStatus,
    FeePayListStatus,
    FeePaymentStatus,
    FeeSourceStatus,
    LegalStatus,
    LifecycleOverlay,
    LifecycleOverlayQuery,
    OfficialProcedureStage,
    OverlayCenterAxis,
    OverlayCenterAxisChange,
    OverlayCenterSnapshot,
    OverlayDecisionGate,
    OverlayDocumentEvidence,
    OverlayFeeLine,
    OverlayFeeObligation,
    OverlayFeeRelatedFact,
    OverlayFeeRelatedFactKind,
    OverlayGateResolutionStatus,
    OverlayLegacyConflict,
    OverlayMilestone,
    OverlayTask,
    OverlayWarning,
    OverlayWarningKind,
    OverlayWorkPackage,
    OverlayWorkPackageReceipt,
} from './lifecycleOverlay.types'

interface EvidenceReferenceWire {
    case_id: string
    evidence_kind: string
    object_type: string
    object_id: string
    content_hash: string
    captured_at: string
}

interface EvidenceVersionResultWire {
    evidence_version_id: string
    case_id: string
    document_id: string
    attachment_id: string
    lineage_key: string
    role: EvidenceRole
    version_number: number
    state: EvidenceVersionState
    creator_id: string
    review_state: EvidenceReviewState
    reviewer_id: string | null
    reviewed_at: string | null
    final_submitted_at: string | null
    content_hash: string
    is_current: boolean
    is_final: boolean
}

interface EvidenceDerivationResultWire {
    evidence_derivation_id: string
    case_id: string
    parent_evidence_version_id: string
    child_evidence_version_id: string
    derivation_type: EvidenceDerivationType
    actor_id: string
    derived_at: string
    source_snapshot: string
}

interface FeeObligationStatusesWire {
    estimate_status: FeeEstimateStatus | null
    obligation_status: FeeObligationStatus
    client_instruction_status: FeeClientInstructionStatus
    draft_status: FeeObligationDraftStatus
    pay_list_status: FeePayListStatus
    payment_status: FeePaymentStatus
    official_evidence_status: FeeOfficialEvidenceStatus
}

interface OverlayCenterSnapshotWire {
    business_stage: BusinessStage | null
    official_procedure_stage: OfficialProcedureStage | null
    legal_status: LegalStatus | null
    effective_at: string | null
    verification_status: ConfirmationStatus | null
    source_event_id: string | null
}

interface OverlayCenterAxisChangeWire {
    previous_value: BusinessStage | OfficialProcedureStage | LegalStatus | null
    current_value: BusinessStage | OfficialProcedureStage | LegalStatus | null
}

interface OverlayDocumentEvidenceWire {
    version: EvidenceVersionResultWire
    derivations: readonly EvidenceDerivationResultWire[]
}

interface OverlayWorkPackageReceiptWire {
    receipt_id: string
    receipt_kind: string
    receipt_attachment_id: string | null
    receiving_case_no: string | null
    submitter: string | null
    received_at: string | null
    archive_status: string
}

interface OverlayWorkPackageWire {
    package_id: string
    package_kind: string
    status: string
    source_document_id: string | null
    reply_document_id: string | null
    manifest_evidence_version_ids: readonly string[]
    receipts: readonly OverlayWorkPackageReceiptWire[]
    missing_gate_codes: readonly string[]
}

interface OverlayTaskWire {
    task_id: string
    document_id: string | null
    task_template_id: string | null
    title: string | null
    due_date: string | null
    internal_due_date: string | null
    status: string
    done_at: string | null
}

interface OverlayFeeLineWire {
    line_id: string
    fee_code: string
    fee_name: string
    fee_year_key: number
    official_full_amount: string | null
    reduction_ratio: string
    payable_amount: string
    source_amount: string | null
    source_date: string | null
    difference_review_state: FeeDifferenceReviewState
}

interface OverlayFeeRelatedFactWire {
    kind: OverlayFeeRelatedFactKind
    object_id: string
    status: string
}

interface OverlayFeeObligationWire {
    obligation_id: string
    source_activity_id: string
    source_document_id: string | null
    source_status: FeeSourceStatus
    fee_domain: FeeDomain
    obligation_type: string
    due_date: string | null
    currency: string
    statuses: FeeObligationStatusesWire
    lines: readonly OverlayFeeLineWire[]
    related_facts: readonly OverlayFeeRelatedFactWire[]
    supersedes_obligation_id: string | null
    supersede_reason: string | null
}

interface OverlayWarningWire {
    kind: OverlayWarningKind
    code: string
    message: string
    activity_id: string | null
    source_object_type: string | null
    source_object_id: string | null
}

interface OverlayDecisionGateWire {
    gate_code: DecisionGateCode
    requested_scope_key: string
    resolution_status: OverlayGateResolutionStatus
    gate_id: string | null
    resolved_scope_key: string | null
    decision_value: string | null
    source_reference: string | null
    source_version: string | null
    confirmed_by: string | null
    effective_at: string | null
    unresolved_reason: string | null
}

interface OverlayLegacyConflictWire {
    code: string
    activity_id: string | null
    message: string | null
}

interface OverlayMilestoneWire {
    sequence: number
    activity_id: string
    lane: ActivityLane
    activity_type: string
    source_activity_id: string | null
    effective_at: string
    confirmation_status: ConfirmationStatus
    center_changes: Partial<Record<OverlayCenterAxis, OverlayCenterAxisChangeWire>>
    document_evidence: readonly OverlayDocumentEvidenceWire[]
    work_packages: readonly OverlayWorkPackageWire[]
    tasks: readonly OverlayTaskWire[]
    fee_obligations: readonly OverlayFeeObligationWire[]
    evidence_summary: readonly EvidenceReferenceWire[]
    warnings: readonly OverlayWarningWire[]
}

interface LifecycleOverlayWire {
    case_id: string
    lifecycle_revision: number
    generated_at: string
    center_snapshot: OverlayCenterSnapshotWire
    milestones: readonly OverlayMilestoneWire[]
    decision_gates: readonly OverlayDecisionGateWire[]
    warnings: readonly OverlayWarningWire[]
    legacy_conflicts: readonly OverlayLegacyConflictWire[]
    next_cursor: number | null
    has_more: boolean
}

function mapEvidenceReference(wire: EvidenceReferenceWire): EvidenceReference {
    return {
        caseId: wire.case_id,
        evidenceKind: wire.evidence_kind,
        objectType: wire.object_type,
        objectId: wire.object_id,
        contentHash: wire.content_hash,
        capturedAt: wire.captured_at,
    }
}

function mapEvidenceVersion(wire: EvidenceVersionResultWire): EvidenceVersionResult {
    return {
        evidenceVersionId: wire.evidence_version_id,
        caseId: wire.case_id,
        documentId: wire.document_id,
        attachmentId: wire.attachment_id,
        lineageKey: wire.lineage_key,
        role: wire.role,
        versionNumber: wire.version_number,
        state: wire.state,
        creatorId: wire.creator_id,
        reviewState: wire.review_state,
        reviewerId: wire.reviewer_id,
        reviewedAt: wire.reviewed_at,
        finalSubmittedAt: wire.final_submitted_at,
        contentHash: wire.content_hash,
        isCurrent: wire.is_current,
        isFinal: wire.is_final,
    }
}

function mapEvidenceDerivation(wire: EvidenceDerivationResultWire): EvidenceDerivationResult {
    return {
        evidenceDerivationId: wire.evidence_derivation_id,
        caseId: wire.case_id,
        parentEvidenceVersionId: wire.parent_evidence_version_id,
        childEvidenceVersionId: wire.child_evidence_version_id,
        derivationType: wire.derivation_type,
        actorId: wire.actor_id,
        derivedAt: wire.derived_at,
        sourceSnapshot: wire.source_snapshot,
    }
}

function mapStatuses(wire: FeeObligationStatusesWire): FeeObligationStatuses {
    return {
        estimateStatus: wire.estimate_status,
        obligationStatus: wire.obligation_status,
        clientInstructionStatus: wire.client_instruction_status,
        draftStatus: wire.draft_status,
        payListStatus: wire.pay_list_status,
        paymentStatus: wire.payment_status,
        officialEvidenceStatus: wire.official_evidence_status,
    }
}

function mapCenterSnapshot(wire: OverlayCenterSnapshotWire): OverlayCenterSnapshot {
    return {
        businessStage: wire.business_stage,
        officialProcedureStage: wire.official_procedure_stage,
        legalStatus: wire.legal_status,
        effectiveAt: wire.effective_at,
        verificationStatus: wire.verification_status,
        sourceEventId: wire.source_event_id,
    }
}

function mapCenterAxisChange(wire: OverlayCenterAxisChangeWire): OverlayCenterAxisChange {
    return {
        previousValue: wire.previous_value,
        currentValue: wire.current_value,
    }
}

function mapCenterChanges(
    wire: Partial<Record<OverlayCenterAxis, OverlayCenterAxisChangeWire>>
): Readonly<Partial<Record<OverlayCenterAxis, OverlayCenterAxisChange>>> {
    return {
        ...(wire.BUSINESS_STAGE === undefined
            ? {}
            : { BUSINESS_STAGE: mapCenterAxisChange(wire.BUSINESS_STAGE) }),
        ...(wire.OFFICIAL_PROCEDURE_STAGE === undefined
            ? {}
            : { OFFICIAL_PROCEDURE_STAGE: mapCenterAxisChange(wire.OFFICIAL_PROCEDURE_STAGE) }),
        ...(wire.LEGAL_STATUS === undefined
            ? {}
            : { LEGAL_STATUS: mapCenterAxisChange(wire.LEGAL_STATUS) }),
    }
}

function mapDocumentEvidence(wire: OverlayDocumentEvidenceWire): OverlayDocumentEvidence {
    return {
        version: mapEvidenceVersion(wire.version),
        derivations: wire.derivations.map(mapEvidenceDerivation),
    }
}

function mapWorkPackageReceipt(wire: OverlayWorkPackageReceiptWire): OverlayWorkPackageReceipt {
    return {
        receiptId: wire.receipt_id,
        receiptKind: wire.receipt_kind,
        receiptAttachmentId: wire.receipt_attachment_id,
        receivingCaseNo: wire.receiving_case_no,
        submitter: wire.submitter,
        receivedAt: wire.received_at,
        archiveStatus: wire.archive_status,
    }
}

function mapWorkPackage(wire: OverlayWorkPackageWire): OverlayWorkPackage {
    return {
        packageId: wire.package_id,
        packageKind: wire.package_kind,
        status: wire.status,
        sourceDocumentId: wire.source_document_id,
        replyDocumentId: wire.reply_document_id,
        manifestEvidenceVersionIds: wire.manifest_evidence_version_ids,
        receipts: wire.receipts.map(mapWorkPackageReceipt),
        missingGateCodes: wire.missing_gate_codes,
    }
}

function mapTask(wire: OverlayTaskWire): OverlayTask {
    return {
        taskId: wire.task_id,
        documentId: wire.document_id,
        taskTemplateId: wire.task_template_id,
        title: wire.title,
        dueDate: wire.due_date,
        internalDueDate: wire.internal_due_date,
        status: wire.status,
        doneAt: wire.done_at,
    }
}

function mapFeeLine(wire: OverlayFeeLineWire): OverlayFeeLine {
    return {
        lineId: wire.line_id,
        feeCode: wire.fee_code,
        feeName: wire.fee_name,
        feeYearKey: wire.fee_year_key,
        officialFullAmount: wire.official_full_amount,
        reductionRatio: wire.reduction_ratio,
        payableAmount: wire.payable_amount,
        sourceAmount: wire.source_amount,
        sourceDate: wire.source_date,
        differenceReviewState: wire.difference_review_state,
    }
}

function mapFeeRelatedFact(wire: OverlayFeeRelatedFactWire): OverlayFeeRelatedFact {
    return {
        kind: wire.kind,
        objectId: wire.object_id,
        status: wire.status,
    }
}

function mapFeeObligation(wire: OverlayFeeObligationWire): OverlayFeeObligation {
    return {
        obligationId: wire.obligation_id,
        sourceActivityId: wire.source_activity_id,
        sourceDocumentId: wire.source_document_id,
        sourceStatus: wire.source_status,
        feeDomain: wire.fee_domain,
        obligationType: wire.obligation_type,
        dueDate: wire.due_date,
        currency: wire.currency,
        statuses: mapStatuses(wire.statuses),
        lines: wire.lines.map(mapFeeLine),
        relatedFacts: wire.related_facts.map(mapFeeRelatedFact),
        supersedesObligationId: wire.supersedes_obligation_id,
        supersedeReason: wire.supersede_reason,
    }
}

function mapWarning(wire: OverlayWarningWire): OverlayWarning {
    return {
        kind: wire.kind,
        code: wire.code,
        message: wire.message,
        activityId: wire.activity_id,
        sourceObjectType: wire.source_object_type,
        sourceObjectId: wire.source_object_id,
    }
}

function mapDecisionGate(wire: OverlayDecisionGateWire): OverlayDecisionGate {
    return {
        gateCode: wire.gate_code,
        requestedScopeKey: wire.requested_scope_key,
        resolutionStatus: wire.resolution_status,
        gateId: wire.gate_id,
        resolvedScopeKey: wire.resolved_scope_key,
        decisionValue: wire.decision_value,
        sourceReference: wire.source_reference,
        sourceVersion: wire.source_version,
        confirmedBy: wire.confirmed_by,
        effectiveAt: wire.effective_at,
        unresolvedReason: wire.unresolved_reason,
    }
}

function mapLegacyConflict(wire: OverlayLegacyConflictWire): OverlayLegacyConflict {
    return {
        code: wire.code,
        activityId: wire.activity_id,
        message: wire.message,
    }
}

function mapMilestone(wire: OverlayMilestoneWire): OverlayMilestone {
    return {
        sequence: wire.sequence,
        activityId: wire.activity_id,
        lane: wire.lane,
        activityType: wire.activity_type,
        sourceActivityId: wire.source_activity_id,
        effectiveAt: wire.effective_at,
        confirmationStatus: wire.confirmation_status,
        centerChanges: mapCenterChanges(wire.center_changes),
        documentEvidence: wire.document_evidence.map(mapDocumentEvidence),
        workPackages: wire.work_packages.map(mapWorkPackage),
        tasks: wire.tasks.map(mapTask),
        feeObligations: wire.fee_obligations.map(mapFeeObligation),
        evidenceSummary: wire.evidence_summary.map(mapEvidenceReference),
        warnings: wire.warnings.map(mapWarning),
    }
}

function mapLifecycleOverlay(wire: LifecycleOverlayWire): LifecycleOverlay {
    return {
        caseId: wire.case_id,
        lifecycleRevision: wire.lifecycle_revision,
        generatedAt: wire.generated_at,
        centerSnapshot: mapCenterSnapshot(wire.center_snapshot),
        milestones: wire.milestones.map(mapMilestone),
        decisionGates: wire.decision_gates.map(mapDecisionGate),
        warnings: wire.warnings.map(mapWarning),
        legacyConflicts: wire.legacy_conflicts.map(mapLegacyConflict),
        nextCursor: wire.next_cursor,
        hasMore: wire.has_more,
    }
}

export function lifecycleOverlayGateKey(
    gate: Pick<OverlayDecisionGate, 'gateCode' | 'requestedScopeKey'>
): `${DecisionGateCode}:${string}` {
    return `${gate.gateCode}:${gate.requestedScopeKey}`
}

export async function getLifecycleOverlay(
    caseId: string,
    query: LifecycleOverlayQuery
): Promise<LifecycleOverlay> {
    const response = await http.get<LifecycleOverlayWire>(`/cases/${caseId}/lifecycle-overlay`, {
        params: {
            after_sequence: query.afterSequence,
            limit: query.limit,
            as_of_revision: query.asOfRevision,
        },
    })
    return mapLifecycleOverlay(response.data)
}
