/// <reference types="vite/client" />

import { createFeeDraft } from '../fees'
import type { FeeDraftCreatePayload, FeeDraftDetail } from '../fees.types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const linkedPayload: FeeDraftCreatePayload = {
    case_id: 'case-1',
    currency: 'CNY',
    obligation_id: 'obligation-1',
}

const explicitlyUnlinkedPayload: FeeDraftCreatePayload = {
    case_id: 'case-1',
    currency: 'CNY',
    obligation_id: null,
}

const omittedLinkagePayload: FeeDraftCreatePayload = {
    case_id: 'case-1',
    currency: 'CNY',
}

const draftPromise: Promise<FeeDraftDetail> = createFeeDraft(linkedPayload)
const nullableOptionalLinkage: Exact<
    FeeDraftCreatePayload['obligation_id'],
    string | null | undefined
> = true
const createSignature: Exact<
    typeof createFeeDraft,
    (data: FeeDraftCreatePayload) => Promise<FeeDraftDetail>
> = true

createFeeDraft({
    case_id: 'case-1',
    currency: 'CNY',
    // @ts-expect-error Obligation source remains server-owned.
    source_document_id: 'document-1',
})

createFeeDraft({
    case_id: 'case-1',
    currency: 'CNY',
    // @ts-expect-error Draft amount remains server-owned.
    amount: '100.00',
})

void [
    explicitlyUnlinkedPayload,
    omittedLinkagePayload,
    draftPromise,
    nullableOptionalLinkage,
    createSignature,
]
