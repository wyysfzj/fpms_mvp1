/// <reference types="vite/client" />

import { reviewDocumentEvidence } from '../documents'
import type { EvidenceReviewExpectation } from '../documents'
import type {
    AttachmentEvidenceProjection,
    DocumentEvidenceReviewPayload,
} from '../documents.types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const payload: DocumentEvidenceReviewPayload = {
    case_id: 'case-1',
    decision: 'APPROVE',
    reviewed_at: '2026-07-20T10:00:00',
    idempotency_key: 'review-1',
}
const expectation: EvidenceReviewExpectation = {
    expectedReviewerId: 'reviewer-1',
    role: 'OA_NOTICE',
    isCurrent: true,
    isFinal: false,
}
const projectionPromise: Promise<AttachmentEvidenceProjection> = reviewDocumentEvidence(
    'document-1',
    'evidence-version-1',
    payload,
    expectation,
)

declare const projection: AttachmentEvidenceProjection

const evidenceVersionId: string = projection.evidence_version_id
const creatorId: string = projection.creator_id
const reviewerId: string | null = projection.reviewer_id
const reviewState: Exact<
    AttachmentEvidenceProjection['review_state'],
    'PENDING' | 'APPROVED' | 'REJECTED'
> = true
const isCurrent: boolean = projection.is_current
const isFinal: boolean = projection.is_final
const decision: Exact<
    DocumentEvidenceReviewPayload['decision'],
    'APPROVE' | 'REJECT'
> = true
const reviewSignature: Exact<
    typeof reviewDocumentEvidence,
    (
        documentId: string,
        evidenceVersionId: string,
        payload: DocumentEvidenceReviewPayload,
        expectation: EvidenceReviewExpectation
    ) => Promise<AttachmentEvidenceProjection>
> = true

// @ts-expect-error Review/current/final state must come from the server projection.
payload.review_state = 'APPROVED'
// @ts-expect-error Review/current/final state must come from the server projection.
payload.is_current = true
// @ts-expect-error Review/current/final state must come from the server projection.
payload.is_final = true

void [
    projectionPromise,
    evidenceVersionId,
    creatorId,
    reviewerId,
    reviewState,
    isCurrent,
    isFinal,
    decision,
    reviewSignature,
]
