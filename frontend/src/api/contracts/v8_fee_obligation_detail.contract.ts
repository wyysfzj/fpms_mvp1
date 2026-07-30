/// <reference types="vite/client" />

import { getFeeObligation } from '../fees'
import type { FeeObligationDetail } from '../fees.types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const detailPromise: Promise<FeeObligationDetail> = getFeeObligation('obligation-1')

declare const detail: FeeObligationDetail

const obligationId: string = detail.id
const caseId: string = detail.case_id
const sourceActivityId: string = detail.source.source_activity_id
const sourceDocumentId: string | null = detail.source.source_document_id
const sourceStatus: Exact<
    FeeObligationDetail['source']['status'],
    'VERIFIED' | 'REVIEW_REQUIRED' | 'LEGACY_UNVERIFIED'
> = true
const feeDomain: Exact<FeeObligationDetail['fee_domain'], 'GOV' | 'SERVICE'> = true
const obligationType: string = detail.obligation_type
const dueDate: string | null = detail.due_date
const currency: string = detail.currency

const estimateStatus: Exact<
    FeeObligationDetail['statuses']['estimate_status'],
    'ESTIMATE' | null
> = true
const obligationStatus: Exact<
    FeeObligationDetail['statuses']['obligation_status'],
    'RECOGNIZED' | 'SUPERSEDED'
> = true
const clientInstructionStatus: Exact<
    FeeObligationDetail['statuses']['client_instruction_status'],
    'PENDING' | 'PAY' | 'HOLD' | 'ABANDON'
> = true
const draftStatus: Exact<
    FeeObligationDetail['statuses']['draft_status'],
    'NOT_CREATED' | 'CREATED'
> = true
const payListStatus: Exact<
    FeeObligationDetail['statuses']['pay_list_status'],
    'NOT_CREATED' | 'CREATED'
> = true
const paymentStatus: Exact<
    FeeObligationDetail['statuses']['payment_status'],
    'UNPAID' | 'PAID'
> = true
const officialEvidenceStatus: Exact<
    FeeObligationDetail['statuses']['official_evidence_status'],
    'PENDING' | 'VERIFIED' | 'NOT_APPLICABLE'
> = true

declare const line: FeeObligationDetail['lines'][number]

const lineId: string = line.id
const lineObligationId: string = line.obligation_id
const lineCaseId: string = line.case_id
const lineSourceActivityId: string = line.source_activity_id
const feeCode: string = line.fee_code
const feeName: string = line.fee_name
const feeYearKey: number = line.fee_year_key
const officialFullAmount: string | null = line.official_full_amount
const reductionRatio: string = line.reduction_ratio
const payableAmount: string = line.payable_amount
const sourceAmount: string | null = line.source_amount
const sourceDate: string | null = line.source_date
const differenceReviewState: Exact<
    FeeObligationDetail['lines'][number]['difference_review_state'],
    'MATCHED' | 'SOURCE_PENDING' | 'REVIEW_REQUIRED'
> = true
const currentIdentityKey: string | null = line.current_identity_key
const supersedesObligationId: string | null = detail.supersedes_obligation_id
const supersedeReason: string | null = detail.supersede_reason

const getFeeObligationSignature: Exact<
    typeof getFeeObligation,
    (id: string) => Promise<FeeObligationDetail>
> = true

void [
    detailPromise,
    obligationId,
    caseId,
    sourceActivityId,
    sourceDocumentId,
    sourceStatus,
    feeDomain,
    obligationType,
    dueDate,
    currency,
    estimateStatus,
    obligationStatus,
    clientInstructionStatus,
    draftStatus,
    payListStatus,
    paymentStatus,
    officialEvidenceStatus,
    lineId,
    lineObligationId,
    lineCaseId,
    lineSourceActivityId,
    feeCode,
    feeName,
    feeYearKey,
    officialFullAmount,
    reductionRatio,
    payableAmount,
    sourceAmount,
    sourceDate,
    differenceReviewState,
    currentIdentityKey,
    supersedesObligationId,
    supersedeReason,
    getFeeObligationSignature,
]
