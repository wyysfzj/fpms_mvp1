import { generateOfficialPaymentWorkbook } from '../govPayments'
import type {
    OfficialPaymentWorkbookGeneratePayload,
    OfficialWorkbookArtifact,
} from '../govPayments.types'

type Exact<Actual, Expected> = [Actual] extends [Expected]
    ? [Expected] extends [Actual]
        ? true
        : false
    : false

const artifact: OfficialWorkbookArtifact = {
    filename: '缴费清单-版本2026.xlsm',
    artifact_id: 'artifact-217',
    content_sha256: 'a'.repeat(64),
    template_version: 'cnipa-v1',
    template_content_sha256: 'b'.repeat(64),
    workbook_input_version_id: 'input-version-217',
    disposition: 'CREATED',
    generated_status: 'GENERATED',
    blob: new Blob(),
}

const filename: string = artifact.filename
const artifactId: string = artifact.artifact_id
const contentHash: string = artifact.content_sha256
const templateVersion: string = artifact.template_version
const templateContentHash: string = artifact.template_content_sha256
const workbookInputVersionId: string = artifact.workbook_input_version_id
const disposition: 'CREATED' | 'REUSED' = artifact.disposition
const generatedStatus: 'GENERATED' | undefined = artifact.generated_status
const blob: Blob = artifact.blob
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
const request: Promise<OfficialWorkbookArtifact> = generateOfficialPaymentWorkbook(7, payload)
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

// @ts-expect-error Generation does not establish official-site acceptance.
const prohibitedAccepted = artifact.accepted
// @ts-expect-error Generation does not establish payment.
const prohibitedPaid = artifact.paid
// @ts-expect-error Generation does not establish ticket verification.
const prohibitedTicketVerified = artifact.ticket_verified

void filename
void artifactId
void contentHash
void templateVersion
void templateContentHash
void workbookInputVersionId
void disposition
void generatedStatus
void blob
void request
void functionSignature
void generatedStatusIsServerOptional
void prohibitedAccepted
void prohibitedPaid
void prohibitedTicketVerified
