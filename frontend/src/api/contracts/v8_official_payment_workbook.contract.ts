import { generateOfficialPaymentWorkbook } from '../govPayments'
import type { OfficialWorkbookArtifact } from '../govPayments.types'

const artifact: OfficialWorkbookArtifact = {
    artifact_id: 'artifact-217',
    content_sha256: 'a'.repeat(64),
    template_version: 'cnipa-v1',
    generated_status: 'GENERATED',
    blob: new Blob(),
}

const artifactId: string = artifact.artifact_id
const contentHash: string = artifact.content_sha256
const templateVersion: string = artifact.template_version
const generatedStatus: 'GENERATED' = artifact.generated_status
const blob: Blob = artifact.blob
const request: Promise<OfficialWorkbookArtifact> = generateOfficialPaymentWorkbook(7, {
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
})

void artifactId
void contentHash
void templateVersion
void generatedStatus
void blob
void request
