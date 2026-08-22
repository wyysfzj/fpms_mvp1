import { getPayListDetail } from '../govPayments'
import type {
    PayListDetailResult,
    PayListExportArtifactInfo,
    PayListInternalArtifactInfo,
    PayListOfficialEvidenceInfo,
    PayListOfficialWorkbookInfo,
} from '../govPayments.types'

const artifact: PayListExportArtifactInfo = {
    id: 'artifact-1',
    pay_list_id: 7,
    kind: 'OFFICIAL_XLSM',
    status: 'OFFICIAL_SITE_ACCEPTED',
    content_sha256: 'a'.repeat(64),
    managed_storage_path: 'pay-lists/7/artifact-1.xlsm',
    template_version: 'cnipa-v1',
    generated_by: 'user-1',
    generated_at: '2026-07-21T12:00:00',
    idempotency_key: 'export-artifact-1',
    official_acceptance_evidence_ref: 'receipt-1',
    official_acceptance_evidence_hash: 'f'.repeat(64),
    official_accepted_at: '2026-07-21T13:00:00',
    updated_at: '2026-07-21T13:00:00',
}

const officialWorkbook: PayListOfficialWorkbookInfo = {
    official_upload_template_status: 'READY',
    official_upload_template_name: 'CNIPA-2026.xlsm',
    official_upload_batch_limit: 500,
    official_pay_list_boundary_note: '仅为上传载体',
}

const detail: PayListDetailResult = {} as PayListDetailResult
const optionalInternalArtifacts: PayListInternalArtifactInfo[] | undefined =
    detail.internal_artifacts
const optionalOfficialWorkbook: PayListOfficialWorkbookInfo | undefined = detail.official_workbook
const payment: PayListDetailResult['gov_payments'] = detail.payment
const optionalOfficialEvidence: PayListOfficialEvidenceInfo[] | undefined =
    detail.official_evidence
const request: Promise<PayListDetailResult> = getPayListDetail(7)

void artifact
void officialWorkbook
void optionalInternalArtifacts
void optionalOfficialWorkbook
void payment
void optionalOfficialEvidence
void request
