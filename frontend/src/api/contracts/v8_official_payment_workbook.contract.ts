// Card runtime verification (run from frontend/; output stays outside the repository):
// npx esbuild src/api/contracts/v8_official_payment_workbook.contract.ts --bundle --platform=node --format=cjs --define:import.meta.env='{}' --outfile=/tmp/fpms-row217-contract.cjs && node /tmp/fpms-row217-contract.cjs

import {
    generateOfficialPaymentWorkbook,
    normalizeOfficialPaymentWorkbookRequestError,
    parseOfficialPaymentWorkbookResponse,
} from '../govPayments'
import type {
    OfficialPaymentWorkbookGeneratePayload,
    OfficialWorkbookArtifact,
} from '../govPayments.types'
import type { ApiError } from '../types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const payload: OfficialPaymentWorkbookGeneratePayload = {
    idempotency_key: 'official-workbook-217',
    rows: [
        {
            sequence_number: 1,
            application_number: 'CN2026000001',
            business_type: '发明专利',
            invoice_title: '测试申请人有限公司',
            unified_social_credit_code: '91110000TEST000001',
            fee_type: '申请费',
            foreign_currency_amount: null,
            amount_cny: 900,
            remark: 'TEST_ONLY',
        },
    ],
}
const functionSignature: Exact<
    typeof generateOfficialPaymentWorkbook,
    (
        payListId: number,
        payload: OfficialPaymentWorkbookGeneratePayload
    ) => Promise<OfficialWorkbookArtifact>
> = true
const generatedStatusIsServerOptional: undefined extends OfficialWorkbookArtifact['generated_status']
    ? true
    : false = true

function assert(condition: unknown, message: string): asserts condition {
    if (!condition) throw new Error(message)
}

function assertEqual(actual: unknown, expected: unknown, label: string): void {
    assert(Object.is(actual, expected), `${label}: expected ${String(expected)}, got ${String(actual)}`)
}

function assertApiError(error: unknown, label: string): asserts error is ApiError {
    assert(typeof error === 'object' && error !== null, `${label}: expected object`)
    const candidate = error as Partial<ApiError>
    assert(typeof candidate.status === 'number', `${label}: missing status`)
    assert(typeof candidate.code === 'string', `${label}: missing code`)
    assert(typeof candidate.message === 'string', `${label}: missing message`)
}

async function expectAdapterError(
    action: () => Promise<unknown>,
    reason: string,
): Promise<void> {
    try {
        await action()
    } catch (error) {
        assertApiError(error, reason)
        assertEqual(error.code, 'OFFICIAL_WORKBOOK_RESPONSE_INVALID', `${reason} code`)
        assertEqual(error.details?.reason, reason, `${reason} reason`)
        return
    }
    throw new Error(`${reason}: expected rejection`)
}

const artifactId = '11111111-1111-4111-8111-111111111217'
const workbookInputVersionId = '22222222-2222-4222-8222-222222222217'
const outputHash = 'a'.repeat(64)
const templateHash = 'b'.repeat(64)
const baseHeaders = {
    'content-disposition':
        "attachment; filename*=UTF-8''%E7%BC%B4%E8%B4%B9%E6%B8%85%E5%8D%95-%E7%89%88%E6%9C%AC2026.xlsm",
    'x-fpms-artifact-id': artifactId,
    'x-fpms-content-sha256': outputHash,
    'x-fpms-template-version': '%E7%89%88%E6%9C%AC2026',
    'x-fpms-template-content-sha256': templateHash,
    'x-fpms-workbook-input-version-id': workbookInputVersionId,
}

async function verifySuccessContracts(): Promise<void> {
    const createdBlob = new Blob(['created-xlsm'])
    const created = await parseOfficialPaymentWorkbookResponse({
        status: 201,
        data: createdBlob,
        headers: {
            ...baseHeaders,
            'x-fpms-workbook-disposition': 'CREATED',
            'x-fpms-generated-status': 'GENERATED',
        },
    })
    assertEqual(created.filename, '缴费清单-版本2026.xlsm', 'CREATED filename')
    assertEqual(created.artifact_id, artifactId, 'CREATED artifact ID')
    assertEqual(created.content_sha256, outputHash, 'CREATED output hash')
    assertEqual(created.template_version, '版本2026', 'CREATED template version')
    assertEqual(created.template_content_sha256, templateHash, 'CREATED template hash')
    assertEqual(
        created.workbook_input_version_id,
        workbookInputVersionId,
        'CREATED workbook input version',
    )
    assertEqual(created.disposition, 'CREATED', 'CREATED disposition')
    assertEqual(created.generated_status, 'GENERATED', 'CREATED server generated status')
    assertEqual(created.blob, createdBlob, 'CREATED blob identity')

    const reusedBlob = new Blob(['reused-xlsm'])
    const reused = await parseOfficialPaymentWorkbookResponse({
        status: 200,
        data: reusedBlob,
        headers: { ...baseHeaders, 'x-fpms-workbook-disposition': 'REUSED' },
    })
    assertEqual(reused.filename, '缴费清单-版本2026.xlsm', 'REUSED filename')
    assertEqual(reused.artifact_id, artifactId, 'REUSED artifact ID')
    assertEqual(reused.content_sha256, outputHash, 'REUSED output hash')
    assertEqual(reused.template_version, '版本2026', 'REUSED template version')
    assertEqual(reused.template_content_sha256, templateHash, 'REUSED template hash')
    assertEqual(
        reused.workbook_input_version_id,
        workbookInputVersionId,
        'REUSED workbook input version',
    )
    assertEqual(reused.disposition, 'REUSED', 'REUSED disposition')
    assert(!('generated_status' in reused), 'REUSED must not derive generated status')
    assertEqual(reused.blob, reusedBlob, 'REUSED blob identity')

    // @ts-expect-error Generation does not establish official-site acceptance.
    const prohibitedAccepted = reused.accepted
    // @ts-expect-error Generation does not establish payment.
    const prohibitedPaid = reused.paid
    // @ts-expect-error Generation does not establish ticket verification.
    const prohibitedTicketVerified = reused.ticket_verified
    void prohibitedAccepted
    void prohibitedPaid
    void prohibitedTicketVerified
}

async function verifyMalformedResponseContracts(): Promise<void> {
    const response = (headers: Record<string, unknown>) => ({
        status: 201,
        data: new Blob(['xlsm']),
        headers,
    })
    const createdHeaders = { ...baseHeaders, 'x-fpms-workbook-disposition': 'CREATED' }

    await expectAdapterError(
        () => parseOfficialPaymentWorkbookResponse(response({
            ...createdHeaders,
            'x-fpms-template-content-sha256': undefined,
        })),
        'missing',
    )
    await expectAdapterError(
        () => parseOfficialPaymentWorkbookResponse(response({
            ...createdHeaders,
            'content-disposition': 'attachment; filename=unsafe.xlsm',
        })),
        'invalid_rfc5987_value',
    )
    await expectAdapterError(
        () => parseOfficialPaymentWorkbookResponse(response({
            ...createdHeaders,
            'x-fpms-template-version': '%ZZ',
        })),
        'invalid_percent_encoding',
    )
    await expectAdapterError(
        () => parseOfficialPaymentWorkbookResponse(response({
            ...createdHeaders,
            'x-fpms-artifact-id': 'not-a-uuid',
        })),
        'invalid_uuid',
    )
    await expectAdapterError(
        () => parseOfficialPaymentWorkbookResponse(response({
            ...createdHeaders,
            'x-fpms-workbook-disposition': 'GENERATED',
        })),
        'invalid_status_disposition',
    )
}

async function verifyErrorContracts(): Promise<void> {
    for (const status of [400, 404, 409, 422]) {
        const details = { gate_code: 'DG-PAYMENT-WORKBOOK', status }
        const requestId = `request-row217-${status}`
        try {
            await parseOfficialPaymentWorkbookResponse({
                status,
                data: new Blob([JSON.stringify({
                    error: {
                        code: `ROW217_${status}`,
                        message: `row217 error ${status}`,
                        details,
                    },
                })]),
                headers: { 'x-request-id': requestId },
            })
        } catch (error) {
            assertApiError(error, `HTTP ${status}`)
            assertEqual(error.status, status, `HTTP ${status} status`)
            assertEqual(error.code, `ROW217_${status}`, `HTTP ${status} code`)
            assertEqual(error.message, `row217 error ${status}`, `HTTP ${status} message`)
            assertEqual(JSON.stringify(error.details), JSON.stringify(details), `HTTP ${status} details`)
            assertEqual(error.requestId, requestId, `HTTP ${status} request ID`)
            continue
        }
        throw new Error(`HTTP ${status}: expected rejection`)
    }

    for (const status of [401, 403]) {
        const normalized: ApiError = {
            status,
            code: status === 401 ? 'UNAUTHENTICATED' : 'PERMISSION_DENIED',
            message: `normalized ${status}`,
            details: { required_perm: 'PayList.Export' },
            requestId: `request-row217-${status}`,
        }
        assertEqual(
            normalizeOfficialPaymentWorkbookRequestError(normalized),
            normalized,
            `HTTP ${status} normalized error identity`,
        )
    }
}

async function verifyOfficialPaymentWorkbookContract(): Promise<void> {
    await verifySuccessContracts()
    await verifyMalformedResponseContracts()
    await verifyErrorContracts()
    console.log('row217 official payment workbook contract: PASS')
}

void payload
void functionSignature
void generatedStatusIsServerOptional
verifyOfficialPaymentWorkbookContract().catch((error: unknown) => {
    console.error(error)
    process.exitCode = 1
})
