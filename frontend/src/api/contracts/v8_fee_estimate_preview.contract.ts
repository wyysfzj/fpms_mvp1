/// <reference types="vite/client" />

import { previewOfficialFeeCandidates } from '../fees'
import type { OfficialFeeEstimateContext, OfficialFeeEstimateResult } from '../fees.types'

declare module 'axios' {
    interface FeeEstimateContractResponse<T = unknown> {
        data: T
    }

    interface FeeEstimateContractRequestConfig {
        headers?: Record<string, string>
    }

    interface FeeEstimateContractInterceptor<V> {
        use(
            onFulfilled?: (value: V) => V | Promise<V>,
            onRejected?: (error: unknown) => unknown,
        ): number
    }

    interface FeeEstimateContractHttp {
        interceptors: {
            request: FeeEstimateContractInterceptor<FeeEstimateContractRequestConfig>
            response: FeeEstimateContractInterceptor<FeeEstimateContractResponse>
        }
        get<T>(url: string, config?: unknown): Promise<FeeEstimateContractResponse<T>>
        post<T>(url: string, data?: unknown, config?: unknown): Promise<FeeEstimateContractResponse<T>>
        put<T>(url: string, data?: unknown, config?: unknown): Promise<FeeEstimateContractResponse<T>>
        delete<T>(url: string, config?: unknown): Promise<FeeEstimateContractResponse<T>>
    }

    interface AxiosStatic {
        create(config?: unknown): FeeEstimateContractHttp
    }
}

const estimateContext: OfficialFeeEstimateContext = {
    case_id: 'case-1',
    trigger_context: {
        trigger: 'FILING_ACCEPTED',
        source_document_id: null,
    },
    currency: 'CNY',
    rate_effective_on: '2026-07-15',
}

const estimatePromise: Promise<OfficialFeeEstimateResult> =
    previewOfficialFeeCandidates(estimateContext)

declare const estimateResult: OfficialFeeEstimateResult

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const estimateStatus: 'ESTIMATE' = estimateResult.estimate_status
const resultCurrency: 'CNY' = estimateResult.currency
const requestCurrency: 'CNY' = estimateContext.currency
const candidate = estimateResult.candidates[0]
const officialFullAmount: string | null = candidate.line.official_full_amount
const reductionRatio: string = candidate.line.reduction_ratio
const payableAmount: string = candidate.line.payable_amount
const sourceAmount: string | null = candidate.line.source_amount
const sourceDate: string | null = candidate.line.source_date
const totalPayableAmount: string = estimateResult.total_payable_amount
const sourceRateId: string | null = candidate.source.rate_id
const sourceDocumentId: string | null = candidate.source.source_document_id
const sourceDoc: string | null = candidate.source.source_doc
const sourceUrl: string | null = candidate.source.source_url
const sourcePolicy: string | null = candidate.source.source_policy
const sourceVersion: string | null = candidate.source.source_version
const sourceStatus: 'VERIFIED' | 'REVIEW_REQUIRED' | 'LEGACY_UNVERIFIED' = candidate.source.status
const differenceReviewState: 'MATCHED' | 'SOURCE_PENDING' | 'REVIEW_REQUIRED' =
    candidate.line.difference_review_state
const nullableWireAssertions: [
    Exact<OfficialFeeEstimateContext['trigger_context']['source_document_id'], string | null>,
    Exact<OfficialFeeEstimateResult['trigger_context']['source_document_id'], string | null>,
    Exact<typeof candidate.line.official_full_amount, string | null>,
    Exact<typeof candidate.line.source_amount, string | null>,
    Exact<typeof candidate.line.source_date, string | null>,
    Exact<typeof candidate.source.rate_id, string | null>,
    Exact<typeof candidate.source.source_document_id, string | null>,
    Exact<typeof candidate.source.source_doc, string | null>,
    Exact<typeof candidate.source.source_url, string | null>,
    Exact<typeof candidate.source.source_policy, string | null>,
    Exact<typeof candidate.source.source_version, string | null>,
] = [true, true, true, true, true, true, true, true, true, true, true]

previewOfficialFeeCandidates({
    case_id: 'case-1',
    // @ts-expect-error Legacy top-level trigger_event input is prohibited.
    trigger_event: 'FILING_ACCEPTED',
    currency: 'CNY',
    rate_effective_on: '2026-07-15',
})

// @ts-expect-error The caller must provide rate_effective_on.
const missingEffectiveDate: OfficialFeeEstimateContext = {
    case_id: 'case-1',
    trigger_context: { trigger: 'FILING_ACCEPTED', source_document_id: null },
    currency: 'CNY',
}

const missingSourceDocument: OfficialFeeEstimateContext = {
    case_id: 'case-1',
    // @ts-expect-error source_document_id is required even when its value is null.
    trigger_context: { trigger: 'FILING_ACCEPTED' },
    currency: 'CNY',
    rate_effective_on: '2026-07-15',
}

const invalidCurrency: OfficialFeeEstimateContext = {
    case_id: 'case-1',
    trigger_context: { trigger: 'FILING_ACCEPTED', source_document_id: null },
    // @ts-expect-error Only CNY is accepted.
    currency: 'USD',
    rate_effective_on: '2026-07-15',
}

// @ts-expect-error Money remains a decimal string.
estimateResult.total_payable_amount = 100
// @ts-expect-error Money remains a nullable decimal string.
candidate.line.official_full_amount = 100
// @ts-expect-error Reduction ratio remains a decimal string.
candidate.line.reduction_ratio = 0.85
// @ts-expect-error An estimate has no obligation identity.
const prohibitedObligationId = estimateResult.obligation_id
// @ts-expect-error An estimate has no draft identity.
const prohibitedDraftId = estimateResult.draft_id
// @ts-expect-error An estimate has no activity identity.
const prohibitedActivityId = estimateResult.activity_id
// @ts-expect-error An estimate has no export identity.
const prohibitedExportId = estimateResult.pay_list_export_id
// @ts-expect-error An estimate has no payment identity.
const prohibitedPaymentId = estimateResult.payment_id
// @ts-expect-error An estimate has no idempotency key.
const prohibitedIdempotencyKey = estimateResult.idempotency_key
// @ts-expect-error An estimate has no generated preview identity.
const prohibitedPreviewId = estimateResult.preview_id
// @ts-expect-error An estimate does not expose a legacy trigger_event.
const prohibitedTriggerEvent = estimateResult.trigger_event
// @ts-expect-error An estimate does not expose a draft type.
const prohibitedDraftType = estimateResult.draft_type
// @ts-expect-error An estimate does not expose a preview-only flag.
const prohibitedPreviewOnly = estimateResult.preview_only
// @ts-expect-error An estimate does not expose a legacy total_gov.
const prohibitedTotalGov = estimateResult.total_gov
// @ts-expect-error An estimate line does not expose quantity.
const prohibitedQuantity = candidate.line.quantity
// @ts-expect-error An estimate line does not expose unit price.
const prohibitedUnitPrice = candidate.line.unit_price

void [
    estimatePromise,
    estimateStatus,
    resultCurrency,
    requestCurrency,
    officialFullAmount,
    reductionRatio,
    payableAmount,
    sourceAmount,
    sourceDate,
    totalPayableAmount,
    sourceRateId,
    sourceDocumentId,
    sourceDoc,
    sourceUrl,
    sourcePolicy,
    sourceVersion,
    sourceStatus,
    differenceReviewState,
    nullableWireAssertions,
    missingEffectiveDate,
    missingSourceDocument,
    invalidCurrency,
    prohibitedObligationId,
    prohibitedDraftId,
    prohibitedActivityId,
    prohibitedExportId,
    prohibitedPaymentId,
    prohibitedIdempotencyKey,
    prohibitedPreviewId,
    prohibitedTriggerEvent,
    prohibitedDraftType,
    prohibitedPreviewOnly,
    prohibitedTotalGov,
    prohibitedQuantity,
    prohibitedUnitPrice,
]
