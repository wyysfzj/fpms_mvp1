/// <reference types="vite/client" />

import { listGrantEvidenceCandidates, reviewGrantEvidence } from '../documents'
import type {
    GrantEvidenceCandidate,
    GrantEvidenceReviewPayload,
    GrantEvidenceReviewResult,
} from '../documents.types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const reviewPayload: GrantEvidenceReviewPayload = {
    decision: 'APPROVE',
    reason: 'independent review complete',
}
const candidatePromise: Promise<GrantEvidenceCandidate[]> =
    listGrantEvidenceCandidates('document-1')
const reviewPromise: Promise<GrantEvidenceReviewResult> = reviewGrantEvidence(
    'candidate-1',
    reviewPayload
)

declare const candidate: GrantEvidenceCandidate
declare const result: GrantEvidenceReviewResult

const candidateIdentity: string = candidate.candidate_id
const evidenceIdentity: string = candidate.evidence_version_id
const sourceIdentity: string = candidate.source_config_id
const sourceRecordIdentity: string = candidate.source_record_id
const sourceVersion: string = candidate.source_version
const originalReference: string = candidate.original_reference
const acquisitionMethod: string = candidate.acquisition_method
const acquiredAt: string = candidate.acquired_at
const proposalRoleConfigId: string = candidate.proposal_role_config_id
const proposerId: string = candidate.proposed_by
const proposedAt: string = candidate.proposed_at
const reviewerId: string | null = candidate.reviewer_id
const reviewedAt: string | null = candidate.reviewed_at
const reviewReason: string | null = candidate.review_reason
const factName: string = candidate.facts[0].name
const factRawValue: string = candidate.facts[0].raw_value
const conflictName: string = candidate.conflicts[0].name
const conflictRawValues: string[] = candidate.conflicts[0].raw_values
const reviewDecision: Exact<
    GrantEvidenceReviewPayload['decision'],
    'APPROVE' | 'REJECT'
> = true
const reviewStatus: Exact<
    GrantEvidenceCandidate['review_status'],
    'PENDING' | 'APPROVED' | 'REJECTED'
> = true
const evidenceScope: Exact<
    GrantEvidenceCandidate['evidence_scope'],
    'GRANT_ANNOUNCEMENT' | 'PATENT_REGISTER'
> = true
const reviewDisposition: Exact<
    GrantEvidenceReviewResult['disposition'],
    'CHANGED' | 'REUSED'
> = true
const resultReviewerId: string = result.reviewer_id
const resultReviewedAt: string = result.reviewed_at
const listSignature: Exact<
    typeof listGrantEvidenceCandidates,
    (documentId: string) => Promise<GrantEvidenceCandidate[]>
> = true
const reviewSignature: Exact<
    typeof reviewGrantEvidence,
    (
        candidateId: string,
        payload: GrantEvidenceReviewPayload
    ) => Promise<GrantEvidenceReviewResult>
> = true

// @ts-expect-error Reviewer identity must come from the authenticated server actor.
reviewPayload.reviewer_id = 'reviewer-1'
// @ts-expect-error Review time must come from the server clock.
reviewPayload.reviewed_at = '2026-08-11T12:00:00'
// @ts-expect-error Evidence review does not derive legal status on the client.
const prohibitedLegalStatus = candidate.legal_status
// @ts-expect-error Evidence review does not derive case lifecycle state on the client.
const prohibitedCaseStatus = result.case_status

void [
    candidatePromise,
    reviewPromise,
    candidateIdentity,
    evidenceIdentity,
    sourceIdentity,
    sourceRecordIdentity,
    sourceVersion,
    originalReference,
    acquisitionMethod,
    acquiredAt,
    proposalRoleConfigId,
    proposerId,
    proposedAt,
    reviewerId,
    reviewedAt,
    reviewReason,
    factName,
    factRawValue,
    conflictName,
    conflictRawValues,
    reviewDecision,
    reviewStatus,
    evidenceScope,
    reviewDisposition,
    resultReviewerId,
    resultReviewedAt,
    listSignature,
    reviewSignature,
    prohibitedLegalStatus,
    prohibitedCaseStatus,
]
