/// <reference types="vite/client" />

import { getLifecycleOverlay, lifecycleOverlayGateKey } from '../lifecycleOverlay'
import type {
    LifecycleOverlay,
    LifecycleOverlayQuery,
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
} from '../lifecycleOverlay.types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

type PublicDtos = [
    LifecycleOverlayQuery,
    OverlayCenterSnapshot,
    OverlayCenterAxisChange,
    OverlayDocumentEvidence,
    OverlayWorkPackageReceipt,
    OverlayWorkPackage,
    OverlayTask,
    OverlayFeeLine,
    OverlayFeeRelatedFact,
    OverlayFeeObligation,
    OverlayWarning,
    OverlayDecisionGate,
    OverlayLegacyConflict,
    OverlayMilestone,
    LifecycleOverlay,
]

type FourUnions = [
    Exact<OverlayCenterAxis, 'BUSINESS_STAGE' | 'OFFICIAL_PROCEDURE_STAGE' | 'LEGAL_STATUS'>,
    Exact<
        OverlayWarningKind,
        'UNVERIFIED' | 'CUSTOMER_DECISION_GATE' | 'CONFLICT' | 'REFERENCE_ONLY'
    >,
    Exact<OverlayFeeRelatedFactKind, 'DRAFT' | 'PAY_LIST' | 'PAYMENT' | 'OFFICIAL_EVIDENCE'>,
    Exact<OverlayGateResolutionStatus, 'RESOLVED' | 'UNRESOLVED'>,
]

declare const overlay: LifecycleOverlay
declare const milestone: OverlayMilestone
declare const line: OverlayFeeLine

const query: LifecycleOverlayQuery = {
    afterSequence: 0,
    limit: 1,
    asOfRevision: null,
}
const overlayPromise: Promise<LifecycleOverlay> = getLifecycleOverlay('case-1', query)
const adapterSignature: Exact<
    typeof getLifecycleOverlay,
    (caseId: string, query: LifecycleOverlayQuery) => Promise<LifecycleOverlay>
> = true

const publicDtoCount: PublicDtos['length'] = 15
const unions: FourUnions = [true, true, true, true]
const dtoFields: [
    Exact<keyof LifecycleOverlayQuery, 'afterSequence' | 'limit' | 'asOfRevision'>,
    Exact<
        keyof OverlayCenterSnapshot,
        | 'businessStage'
        | 'officialProcedureStage'
        | 'legalStatus'
        | 'effectiveAt'
        | 'verificationStatus'
        | 'sourceEventId'
    >,
    Exact<keyof OverlayCenterAxisChange, 'previousValue' | 'currentValue'>,
    Exact<keyof OverlayDocumentEvidence, 'version' | 'derivations'>,
    Exact<
        keyof OverlayWorkPackageReceipt,
        | 'receiptId'
        | 'receiptKind'
        | 'receiptAttachmentId'
        | 'receivingCaseNo'
        | 'submitter'
        | 'receivedAt'
        | 'archiveStatus'
    >,
    Exact<
        keyof OverlayWorkPackage,
        | 'packageId'
        | 'packageKind'
        | 'status'
        | 'sourceDocumentId'
        | 'replyDocumentId'
        | 'manifestEvidenceVersionIds'
        | 'receipts'
        | 'missingGateCodes'
    >,
    Exact<
        keyof OverlayTask,
        | 'taskId'
        | 'documentId'
        | 'taskTemplateId'
        | 'title'
        | 'dueDate'
        | 'internalDueDate'
        | 'status'
        | 'doneAt'
    >,
    Exact<
        keyof OverlayFeeLine,
        | 'lineId'
        | 'feeCode'
        | 'feeName'
        | 'feeYearKey'
        | 'officialFullAmount'
        | 'reductionRatio'
        | 'payableAmount'
        | 'sourceAmount'
        | 'sourceDate'
        | 'differenceReviewState'
    >,
    Exact<keyof OverlayFeeRelatedFact, 'kind' | 'objectId' | 'status'>,
    Exact<
        keyof OverlayFeeObligation,
        | 'obligationId'
        | 'sourceActivityId'
        | 'sourceDocumentId'
        | 'sourceStatus'
        | 'feeDomain'
        | 'obligationType'
        | 'dueDate'
        | 'currency'
        | 'statuses'
        | 'lines'
        | 'relatedFacts'
        | 'supersedesObligationId'
        | 'supersedeReason'
    >,
    Exact<
        keyof OverlayWarning,
        'kind' | 'code' | 'message' | 'activityId' | 'sourceObjectType' | 'sourceObjectId'
    >,
    Exact<
        keyof OverlayDecisionGate,
        | 'gateCode'
        | 'requestedScopeKey'
        | 'resolutionStatus'
        | 'gateId'
        | 'resolvedScopeKey'
        | 'decisionValue'
        | 'sourceReference'
        | 'sourceVersion'
        | 'confirmedBy'
        | 'effectiveAt'
        | 'unresolvedReason'
    >,
    Exact<keyof OverlayLegacyConflict, 'code' | 'activityId' | 'message'>,
    Exact<
        keyof OverlayMilestone,
        | 'sequence'
        | 'activityId'
        | 'lane'
        | 'activityType'
        | 'sourceActivityId'
        | 'effectiveAt'
        | 'confirmationStatus'
        | 'centerChanges'
        | 'documentEvidence'
        | 'workPackages'
        | 'tasks'
        | 'feeObligations'
        | 'evidenceSummary'
        | 'warnings'
    >,
    Exact<
        keyof LifecycleOverlay,
        | 'caseId'
        | 'lifecycleRevision'
        | 'generatedAt'
        | 'centerSnapshot'
        | 'milestones'
        | 'decisionGates'
        | 'warnings'
        | 'legacyConflicts'
        | 'nextCursor'
        | 'hasMore'
    >,
] = [true, true, true, true, true, true, true, true, true, true, true, true, true, true, true]
const queryShape: [number, number, number | null] = [
    query.afterSequence,
    query.limit,
    query.asOfRevision,
]
const centerSnapshotShape: [
    string | null,
    string | null,
    string | null,
    string | null,
    string | null,
    string | null,
] = [
    overlay.centerSnapshot.businessStage,
    overlay.centerSnapshot.officialProcedureStage,
    overlay.centerSnapshot.legalStatus,
    overlay.centerSnapshot.effectiveAt,
    overlay.centerSnapshot.verificationStatus,
    overlay.centerSnapshot.sourceEventId,
]
const axisChangeShape: [string | null, string | null] = [
    milestone.centerChanges.BUSINESS_STAGE?.previousValue ?? null,
    milestone.centerChanges.BUSINESS_STAGE?.currentValue ?? null,
]
const nestedCollections: readonly (readonly unknown[])[] = [
    milestone.documentEvidence,
    milestone.workPackages,
    milestone.tasks,
    milestone.feeObligations,
    milestone.evidenceSummary,
    milestone.warnings,
    overlay.warnings,
    overlay.legacyConflicts,
]
const decimalStrings: [string | null, string, string, string | null, string | null] = [
    line.officialFullAmount,
    line.reductionRatio,
    line.payableAmount,
    line.sourceAmount,
    line.sourceDate,
]

function caseGate(gateCode: OverlayDecisionGate['gateCode']): OverlayDecisionGate {
    return {
        gateCode,
        requestedScopeKey: 'case:case-1',
        resolutionStatus: 'RESOLVED',
        gateId: `gate-${gateCode}`,
        resolvedScopeKey: 'case:case-1',
        decisionValue: 'CONFIRMED',
        sourceReference: 'source.docx',
        sourceVersion: 'v1',
        confirmedBy: 'operator-1',
        effectiveAt: '2026-07-14T09:30:00Z',
        unresolvedReason: null,
    }
}

function legacyGate(requestedScopeKey: `form-${string}`): OverlayDecisionGate {
    return {
        gateCode: 'DG-LEGACY-FORM-CLASS',
        requestedScopeKey,
        resolutionStatus: 'RESOLVED',
        gateId: `legacy-${requestedScopeKey}`,
        resolvedScopeKey: requestedScopeKey === 'form-022' ? 'ALL-22' : requestedScopeKey,
        decisionValue: requestedScopeKey === 'form-022' ? 'HISTORICAL' : 'CONFIRMED',
        sourceReference: `source-${requestedScopeKey}.docx`,
        sourceVersion: 'legacy-v1',
        confirmedBy: 'operator-1',
        effectiveAt: '2026-07-14T09:30:00Z',
        unresolvedReason: null,
    }
}

const decisionGates = [
    caseGate('DG-FEE-APPLICATION-DRAFT'),
    caseGate('DG-FEE-GRANT-YEAR-DRAFT'),
    caseGate('DG-FEE-FUTURE-ANNUITY'),
    caseGate('DG-GRANT-EVIDENCE-SOURCE'),
    caseGate('DG-GRANT-MANUAL-REVIEW'),
    caseGate('DG-PAYMENT-WORKBOOK'),
    caseGate('DG-SERVICE-RATE-VERSION'),
    legacyGate('form-001'),
    legacyGate('form-002'),
    legacyGate('form-003'),
    legacyGate('form-004'),
    legacyGate('form-005'),
    legacyGate('form-006'),
    legacyGate('form-007'),
    legacyGate('form-008'),
    legacyGate('form-009'),
    legacyGate('form-010'),
    legacyGate('form-011'),
    legacyGate('form-012'),
    legacyGate('form-013'),
    legacyGate('form-014'),
    legacyGate('form-015'),
    legacyGate('form-016'),
    legacyGate('form-017'),
    legacyGate('form-018'),
    legacyGate('form-019'),
    legacyGate('form-020'),
    legacyGate('form-021'),
    legacyGate('form-022'),
] as const satisfies readonly OverlayDecisionGate[]

const decisionGateCount: 29 = decisionGates.length
const compositeKeys = decisionGates.map(lifecycleOverlayGateKey)
const compositeKeyCount: number = compositeKeys.length
const codeOnlyKeys = new Set(decisionGates.map((gate) => gate.gateCode))
const codeOnlyKeyCount: number = codeOnlyKeys.size
const fallbackGate: OverlayDecisionGate = decisionGates[28]
const fallbackShape: [string, string, string | null, string | null] = [
    fallbackGate.requestedScopeKey,
    fallbackGate.resolvedScopeKey ?? '',
    fallbackGate.decisionValue,
    fallbackGate.sourceReference,
]

const firstPage: LifecycleOverlay = { ...overlay, milestones: [], decisionGates, nextCursor: 1, hasMore: true }
const middlePage: LifecycleOverlay = {
    ...overlay,
    milestones: [],
    decisionGates,
    nextCursor: 2,
    hasMore: true,
}
const finalPage: LifecycleOverlay = {
    ...overlay,
    milestones: [],
    decisionGates,
    nextCursor: null,
    hasMore: false,
}
const emptyMilestonePage: LifecycleOverlay = {
    ...overlay,
    milestones: [],
    decisionGates,
    nextCursor: null,
    hasMore: false,
}

// @ts-expect-error The aggregate fallback is resolved scope only, never requested scope.
legacyGate('ALL-22')
// @ts-expect-error Decimal amounts remain wire strings.
line.payableAmount = 100
// @ts-expect-error Reduction ratios remain wire strings.
line.reductionRatio = 0.85
// @ts-expect-error A gate requires its requested composite scope.
const missingRequestedScope: OverlayDecisionGate = { gateCode: 'DG-PAYMENT-WORKBOOK' }
// @ts-expect-error A code-indexed record cannot represent the repeated legacy gate entries.
const codeIndexedGates: Record<OverlayDecisionGate['gateCode'], OverlayDecisionGate> = decisionGates
// @ts-expect-error Flattening document evidence loses its required nested version association.
const flattenedEvidence: OverlayDocumentEvidence = { derivations: [] }

void [
    overlayPromise,
    adapterSignature,
    publicDtoCount,
    unions,
    dtoFields,
    queryShape,
    centerSnapshotShape,
    axisChangeShape,
    nestedCollections,
    decimalStrings,
    decisionGateCount,
    compositeKeyCount,
    codeOnlyKeyCount,
    fallbackShape,
    firstPage,
    middlePage,
    finalPage,
    emptyMilestonePage,
    missingRequestedScope,
    codeIndexedGates,
    flattenedEvidence,
]
