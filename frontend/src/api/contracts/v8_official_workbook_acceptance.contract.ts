// Card runtime verification (run from frontend/; output stays outside the repository):
// npx esbuild src/api/contracts/v8_official_workbook_acceptance.contract.ts --bundle --platform=node --format=cjs --define:import.meta.env='{}' --outfile=/tmp/fpms-row221-contract.cjs && node /tmp/fpms-row221-contract.cjs

import { AxiosHeaders } from 'axios'

import { recordOfficialWorkbookAcceptance } from '../govPayments'
import type {
    OfficialWorkbookAcceptancePayload,
    OfficialWorkbookAcceptanceResult,
    OfficialWorkbookArtifact,
} from '../govPayments.types'
import { http } from '../http'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const payload: OfficialWorkbookAcceptancePayload = {
    artifact_id: '11111111-1111-4111-8111-111111111221',
    evidence_ref: 'official-site/acceptance/receipt-221',
    evidence_sha256: 'a'.repeat(64),
    accepted_at: '2026-08-13T17:00:00',
    idempotency_key: 'official-workbook-acceptance-fe-221',
}

const functionSignature: Exact<
    typeof recordOfficialWorkbookAcceptance,
    (
        payListId: number,
        payload: OfficialWorkbookAcceptancePayload
    ) => Promise<OfficialWorkbookAcceptanceResult>
> = true
const acceptedIsServerTrue: Exact<OfficialWorkbookAcceptanceResult['accepted'], true> = true
const paidIsServerFalse: Exact<OfficialWorkbookAcceptanceResult['paid'], false> = true
const ticketIsServerFalse: Exact<
    OfficialWorkbookAcceptanceResult['ticket_verified'],
    false
> = true
const acceptanceStatusIsExact: Exact<
    OfficialWorkbookAcceptanceResult['status'],
    'OFFICIAL_SITE_ACCEPTED'
> = true
const dispositionIsExact: Exact<
    OfficialWorkbookAcceptanceResult['disposition'],
    'CREATED' | 'REUSED'
> = true

function verifyTypeSeparation(
    acceptance: OfficialWorkbookAcceptanceResult,
    generation: OfficialWorkbookArtifact,
): void {
    // @ts-expect-error Acceptance evidence does not establish a generated workbook result.
    void acceptance.generated_status
    // @ts-expect-error Acceptance evidence does not carry downloadable workbook bytes.
    void acceptance.blob
    // @ts-expect-error Generation does not establish official-site acceptance.
    void generation.accepted
    // @ts-expect-error Generation does not establish payment.
    void generation.paid
    // @ts-expect-error Generation does not establish ticket verification.
    void generation.ticket_verified
}

const createdResult: OfficialWorkbookAcceptanceResult = {
    artifact_id: payload.artifact_id,
    pay_list_id: 7,
    evidence_ref: payload.evidence_ref,
    evidence_sha256: payload.evidence_sha256,
    accepted_at: payload.accepted_at,
    activity_id: '22222222-2222-4222-8222-222222222221',
    status: 'OFFICIAL_SITE_ACCEPTED',
    accepted: true,
    paid: false,
    ticket_verified: false,
    idempotency_key: payload.idempotency_key,
    disposition: 'CREATED',
}

function assert(condition: unknown, message: string): asserts condition {
    if (!condition) throw new Error(message)
}

function assertEqual(actual: unknown, expected: unknown, label: string): void {
    assert(Object.is(actual, expected), `${label}: expected ${String(expected)}, got ${String(actual)}`)
}

async function verifyRuntimeContract(): Promise<void> {
    const originalAdapter = http.defaults.adapter
    const requests: Array<{ method?: string; url?: string; data?: unknown }> = []
    try {
        Object.defineProperty(globalThis, 'localStorage', {
            configurable: true,
            value: { getItem: () => null },
        })
        http.defaults.adapter = async (config) => {
            requests.push({ method: config.method, url: config.url, data: config.data })
            const reused = requests.length === 2
            return {
                data: reused ? { ...createdResult, disposition: 'REUSED' } : createdResult,
                status: reused ? 200 : 201,
                statusText: reused ? 'OK' : 'Created',
                headers: new AxiosHeaders(),
                config,
            }
        }

        const created = await recordOfficialWorkbookAcceptance(7, payload)
        const reused = await recordOfficialWorkbookAcceptance(7, payload)

        assertEqual(requests[0].method, 'post', 'HTTP method')
        assertEqual(
            requests[0].url,
            '/pay-lists/7/official-workbook/acceptance',
            'HTTP path',
        )
        assertEqual(JSON.stringify(JSON.parse(String(requests[0].data))), JSON.stringify(payload), 'body')
        assertEqual(created, createdResult, 'CREATED response identity')
        assertEqual(reused.disposition, 'REUSED', 'REUSED disposition')
        assertEqual(reused.accepted, true, 'server accepted fact')
        assertEqual(reused.paid, false, 'server paid fact')
        assertEqual(reused.ticket_verified, false, 'server ticket fact')
        console.log('row221 official workbook acceptance contract: PASS')
    } finally {
        http.defaults.adapter = originalAdapter
    }
}

void [
    functionSignature,
    acceptedIsServerTrue,
    paidIsServerFalse,
    ticketIsServerFalse,
    acceptanceStatusIsExact,
    dispositionIsExact,
    verifyTypeSeparation,
]
verifyRuntimeContract().catch((error: unknown) => {
    console.error(error)
    process.exitCode = 1
})
