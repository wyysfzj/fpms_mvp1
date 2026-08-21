import { test, expect, type APIRequestContext, type BrowserContext, type Page } from '@playwright/test'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

type Json = Record<string, any>
type EvidenceRole =
  | 'FILING_FINAL_SUBMISSION'
  | 'FILING_RECEIPT'
  | 'ACCEPTANCE_NOTICE'
  | 'PRELIMINARY_EXAMINATION_SOURCE'
  | 'PUBLICATION_NOTICE'
  | 'SUBSTANTIVE_EXAMINATION_SOURCE'
  | 'OA_NOTICE_1'
  | 'OA_RECEIPT_1'
  | 'OA_NOTICE_2'
  | 'OA_RECEIPT_2'
  | 'GRANT_NOTICE_ORIGINAL'
  | 'GRANT_NOTICE_REPLACEMENT'

type EvidenceBinding = {
  role: EvidenceRole
  manifestPath: string
  manifestSha256: string
  metadata: Json
  attachmentId: string
  evidenceVersionId: string
  contentHash: string
  reviewState: 'APPROVED'
  consumer: string
  consumerResultId: string
}

type PublicLifecycleOperation =
  | 'ARCHIVE_PACKAGE'
  | 'GET_FILING_PACKAGE'
  | 'GET_GRANT_TASK'
  | 'GET_OA_PACKAGE'
  | 'GRANT_BATCH_INSTRUCTION'
  | 'GRANT_GENERATE_DRAFT'
  | 'GRANT_GENERATE_NOTICES'
  | 'GRANT_NOTICE'
  | 'GRANT_REPLACEMENT'
  | 'GRANT_TASK_STATE'
  | 'LINK_OA_REPLY'
  | 'RECORD_ACCEPTANCE'
  | 'RECORD_FILING_EXTERNAL'
  | 'RECORD_OA_NOTICE'
  | 'RECORD_PACKAGE_RECEIPT'
  | 'RECORD_PRELIMINARY_PASS'
  | 'RECORD_PRELIMINARY_START'
  | 'RECORD_PUBLICATION'
  | 'RECORD_SUBSTANTIVE_START'
  | 'RESOLVE_FILING'
  | 'RESOLVE_OA'

const baseUrl = process.env.FPMS_BASE_URL || 'http://127.0.0.1:5173'
const apiBase = process.env.FPMS_API_URL || 'http://127.0.0.1:8000/api/v1'
const evidenceDir = process.env.FPMS_DEMO_EVIDENCE_DIR
const bundlePath = process.env.FPMS_DEMO_BUNDLE_PATH
const adminUsername = process.env.FPMS_ADMIN_USERNAME
const adminPassword = process.env.FPMS_ADMIN_PASSWORD
const reviewerUsername = process.env.FPMS_REVIEWER_USERNAME
const reviewerPassword = process.env.FPMS_REVIEWER_PASSWORD
const expectedDisclaimer = process.env.FPMS_DEMO_EXPECTED_DISCLAIMER_ZH_CN
const expectedProvenance = {
  bundle_id: process.env.FPMS_DEMO_EXPECTED_BUNDLE_ID,
  bundle_version: process.env.FPMS_DEMO_EXPECTED_BUNDLE_VERSION,
  manifest_sha256: process.env.FPMS_DEMO_EXPECTED_MANIFEST_SHA256,
  template_code: process.env.FPMS_DEMO_EXPECTED_TEMPLATE_CODE,
  template_sha256: process.env.FPMS_DEMO_EXPECTED_TEMPLATE_SHA256,
  rate_item_code: process.env.FPMS_DEMO_EXPECTED_RATE_ITEM_CODE,
  rate_source_ref: process.env.FPMS_DEMO_EXPECTED_RATE_SOURCE_REF,
  rate_source_version: process.env.FPMS_DEMO_EXPECTED_RATE_SOURCE_VERSION,
  rate_source_sha256: process.env.FPMS_DEMO_EXPECTED_RATE_SOURCE_SHA256,
}

// BEGIN EXACT PUBLIC LIFECYCLE API ALLOWLIST
const publicLifecycleApiAllowlist = {
  ARCHIVE_PACKAGE: { method: 'POST', path: '/official-work-packages/{package_id}/archive' },
  GET_FILING_PACKAGE: { method: 'GET', path: '/official-work-packages/{package_id}/filing-preparation' },
  GET_GRANT_TASK: { method: 'GET', path: '/grant-fee-tasks/{task_id}/state' },
  GET_OA_PACKAGE: { method: 'GET', path: '/official-work-packages/{package_id}/oa-reply' },
  GRANT_BATCH_INSTRUCTION: { method: 'POST', path: '/grant-fee-tasks/batch-instruction' },
  GRANT_GENERATE_DRAFT: { method: 'POST', path: '/grant-fee-tasks/{task_id}/generate-draft' },
  GRANT_GENERATE_NOTICES: { method: 'POST', path: '/grant-fee-tasks/generate-notices' },
  GRANT_NOTICE: { method: 'POST', path: '/grant-fee-tasks/{grant_fee_task_id}/lifecycle/grant-notice' },
  GRANT_REPLACEMENT: { method: 'POST', path: '/grant-fee-tasks/{task_id}/replacement-notice' },
  GRANT_TASK_STATE: { method: 'PUT', path: '/grant-fee-tasks/{task_id}/state' },
  LINK_OA_REPLY: { method: 'POST', path: '/official-work-packages/{package_id}/oa-reply/reply-document' },
  RECORD_ACCEPTANCE: { method: 'POST', path: '/documents/{document_id}/lifecycle/acceptance-notice' },
  RECORD_FILING_EXTERNAL: { method: 'POST', path: '/official-work-packages/{package_id}/filing-preparation/external-operations' },
  RECORD_OA_NOTICE: { method: 'POST', path: '/documents/{document_id}/lifecycle/oa-notice' },
  RECORD_PACKAGE_RECEIPT: { method: 'POST', path: '/official-work-packages/{package_id}/receipts' },
  RECORD_PRELIMINARY_PASS: { method: 'POST', path: '/documents/{document_id}/lifecycle/preliminary-pass' },
  RECORD_PRELIMINARY_START: { method: 'POST', path: '/documents/{document_id}/lifecycle/preliminary-start' },
  RECORD_PUBLICATION: { method: 'POST', path: '/documents/{document_id}/lifecycle/publication-notice' },
  RECORD_SUBSTANTIVE_START: { method: 'POST', path: '/documents/{document_id}/lifecycle/substantive-start' },
  RESOLVE_FILING: { method: 'POST', path: '/cases/{case_id}/official-work-packages/filing-preparation/resolve' },
  RESOLVE_OA: { method: 'POST', path: '/official-documents/{document_id}/official-work-packages/oa-reply/resolve' },
} as const satisfies Record<PublicLifecycleOperation, { method: 'GET' | 'POST' | 'PUT'; path: string }>
// END EXACT PUBLIC LIFECYCLE API ALLOWLIST

const orderedRoles: EvidenceRole[] = [
  'FILING_FINAL_SUBMISSION',
  'FILING_RECEIPT',
  'ACCEPTANCE_NOTICE',
  'PRELIMINARY_EXAMINATION_SOURCE',
  'PUBLICATION_NOTICE',
  'SUBSTANTIVE_EXAMINATION_SOURCE',
  'OA_NOTICE_1',
  'OA_RECEIPT_1',
  'OA_NOTICE_2',
  'OA_RECEIPT_2',
  'GRANT_NOTICE_ORIGINAL',
  'GRANT_NOTICE_REPLACEMENT',
]

const checkpointContract = [
  'IA-00 preflight and provenance',
  'IA-01 client and contact',
  'IA-02 one case and initial projection',
  'IA-03 60-row wizard catalog',
  'IA-04 filing preparation reuse',
  'IA-05 reviewed filing ladder and OA1 deadline',
  'IA-06 OA_OUT unique link and OPEN task',
  'IA-07 invalid receipt no-write',
  'IA-08 valid OA1 receipt archive',
  'IA-09 independent OA2 and receipt',
  'IA-10 original grant notice',
  'IA-11 grant replacement lineage',
  'IA-12 superseded task gates and PAY',
  'IA-13 runtime SERVICE obligation and LOCKED draft',
  'IA-14 unique AR bill',
  'IA-15 unique bank payment',
  'IA-16 full offset',
  'IA-17 reload consistency',
  'IA-18 final summary and cleanup',
] as const

async function login(page: Page, username: string, password: string): Promise<string> {
  await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
  await page.locator('.el-form-item:has-text("用户名") input').fill(username)
  await page.locator('.el-form-item:has-text("密码") input').fill(password)
  const loginResponse = page.waitForResponse((response) => response.status() === 200 && response.url().includes('/auth/login'))
  await page.getByRole('button', { name: '登 录' }).click()
  const loginResult = await (await loginResponse).json() as Json
  expect(typeof loginResult.access_token).toBe('string')
  expect(loginResult.access_token.length).toBeGreaterThan(0)
  await expect(page).not.toHaveURL(/\/login$/)
  return loginResult.access_token
}

// BEGIN AUDITED PUBLIC API HELPER
async function callPublicLifecycleApi(
  apiRequest: APIRequestContext,
  accessToken: string,
  operation: PublicLifecycleOperation,
  pathParameters: Record<string, string>,
  data?: Json,
): Promise<{ status: number; body: Json }> {
  const contract = publicLifecycleApiAllowlist[operation]
  let route: string = contract.path
  for (const [name, value] of Object.entries(pathParameters)) {
    expect(value).toMatch(/^\S(?:.*\S)?$/)
    route = route.replace(`{${name}}`, encodeURIComponent(value))
  }
  expect(route).not.toMatch(/\{[^}]+\}/)
  expect(route).not.toMatch(/attachments|evidence-versions|\/review/)
  const response = await apiRequest.fetch(`${apiBase}${route}`, {
    method: contract.method,
    headers: { Authorization: `Bearer ${accessToken}` },
    data,
  })
  const body = await response.json() as Json
  return { status: response.status(), body }
}
// END AUDITED PUBLIC API HELPER

async function uploadAndReviewEvidenceViaVisibleUi(
  operatorPage: Page,
  reviewerPage: Page,
  documentId: string,
  descriptor: { role: EvidenceRole; path: string; sha256: string; metadata: Json },
): Promise<EvidenceBinding> {
  await operatorPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
  await operatorPage.getByTestId('attachment-open-upload').click()
  await operatorPage.getByTestId('attachment-file-picker').locator('input[type=file]').setInputFiles(descriptor.path)
  const uploadResponse = operatorPage.waitForResponse((response) => response.status() === 201 && response.url().includes('/attachments'))
  await operatorPage.getByRole('button', { name: '确认上传' }).click()
  const uploaded = await (await uploadResponse).json() as Json
  expect(uploaded.content_hash).toBe(descriptor.sha256)

  await reviewerPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
  const reviewResponse = reviewerPage.waitForResponse((response) => response.status() === 200 && response.url().includes('/review'))
  await reviewerPage.getByTestId(`attachment-${uploaded.evidence_version_id}`).getByRole('button', { name: '通过' }).click()
  const reviewed = await (await reviewResponse).json() as Json
  expect(reviewed.review_state).toBe('APPROVED')
  expect(reviewed.content_hash).toBe(descriptor.sha256)
  return {
    role: descriptor.role,
    manifestPath: descriptor.path,
    manifestSha256: descriptor.sha256,
    metadata: descriptor.metadata,
    attachmentId: uploaded.id,
    evidenceVersionId: reviewed.evidence_version_id,
    contentHash: reviewed.content_hash,
    reviewState: 'APPROVED',
    consumer: '',
    consumerResultId: '',
  }
}

function recordDocumentLifecycleConsumer(
  evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
  binding: EvidenceBinding,
  consumer: string,
  payload: Json,
  result: Json,
): EvidenceBinding {
  expect(binding.contentHash).toBe(binding.manifestSha256)
  expect(payload.evidence_version_id).toBe(binding.evidenceVersionId)
  expect(result.evidence_version_id).toBe(binding.evidenceVersionId)
  expect(typeof result.activity_id).toBe('string')
  expect(result.activity_id.length).toBeGreaterThan(0)
  const updated = { ...binding, consumer, consumerResultId: result.activity_id }
  evidenceRoleMap.set(binding.role, updated)
  return updated
}

function recordReceiptConsumer(
  evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
  binding: EvidenceBinding,
  consumer: string,
  payload: Json,
  result: Json,
): EvidenceBinding {
  expect(binding.contentHash).toBe(binding.manifestSha256)
  expect(payload.receipt_attachment_id).toBe(binding.attachmentId)
  expect(result.receipt_attachment_id).toBe(binding.attachmentId)
  expect(typeof result.id).toBe('string')
  expect(result.id.length).toBeGreaterThan(0)
  const updated = { ...binding, consumer, consumerResultId: result.id }
  evidenceRoleMap.set(binding.role, updated)
  return updated
}

function recordGrantConsumer(
  evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
  binding: EvidenceBinding,
  consumer: string,
  payload: Json,
  result: Json,
): EvidenceBinding {
  expect(binding.contentHash).toBe(binding.manifestSha256)
  expect(payload.reviewed_evidence_version_id).toBe(binding.evidenceVersionId)
  expect(payload.expected_content_hash).toBe(binding.contentHash)
  expect(typeof result.activity_id).toBe('string')
  expect(result.activity_id.length).toBeGreaterThan(0)
  expect(result.event_type).toBe('GRANT_REGISTRATION_NOTICE_RECORDED')
  const updated = { ...binding, consumer, consumerResultId: result.activity_id }
  evidenceRoleMap.set(binding.role, updated)
  return updated
}

function recordFilingSubmission(
  evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
  binding: EvidenceBinding,
  commandResult: Json,
  packageResult: Json,
  activityResult: Json,
): EvidenceBinding {
  expect(binding.contentHash).toBe(binding.manifestSha256)
  expect(commandResult.package_id).toBe(packageResult.package.id)
  expect(commandResult.checklist_item.item_code).toBe('EXTERNAL_SUBMISSION_RECORDED')
  expect(commandResult.checklist_item.status).toBe('DONE')
  const manifest = (packageResult.filing_file_roles as Json[]).find(
    (item) => item.evidence_version_id === binding.evidenceVersionId,
  )
  expect(manifest).toBeDefined()
  expect(manifest!.content_hash).toBe(binding.contentHash)
  expect(activityResult.event_type).toBe('FILING_EXTERNAL_SUBMISSION_RECORDED')
  expect(activityResult.confirmation_status).toBe('CONFIRMED')
  expect(activityResult.evidence_refs).toContainEqual(expect.objectContaining({
    evidence_kind: 'FINAL_SUBMISSION_VERSION',
    object_id: binding.evidenceVersionId,
    content_hash: binding.contentHash,
  }))
  expect(typeof activityResult.id).toBe('string')
  expect(activityResult.id.length).toBeGreaterThan(0)
  const updated = { ...binding, consumer: 'filing-external-submission', consumerResultId: activityResult.id }
  evidenceRoleMap.set(binding.role, updated)
  return updated
}

const expectedConsumerByRole: Record<EvidenceRole, string> = {
  FILING_FINAL_SUBMISSION: 'filing-external-submission',
  FILING_RECEIPT: 'filing-receipt',
  ACCEPTANCE_NOTICE: 'acceptance-notice',
  PRELIMINARY_EXAMINATION_SOURCE: 'preliminary-examination',
  PUBLICATION_NOTICE: 'publication-notice',
  SUBSTANTIVE_EXAMINATION_SOURCE: 'substantive-examination',
  OA_NOTICE_1: 'oa1-notice',
  OA_RECEIPT_1: 'oa1-receipt',
  OA_NOTICE_2: 'oa2-notice',
  OA_RECEIPT_2: 'oa2-receipt',
  GRANT_NOTICE_ORIGINAL: 'grant-original-dispatch',
  GRANT_NOTICE_REPLACEMENT: 'grant-replacement-dispatch',
}

function assertCompleteEvidenceLedger(
  evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
): EvidenceBinding[] {
  expect([...evidenceRoleMap.keys()]).toEqual(orderedRoles)
  const ledger = orderedRoles.map((role) => {
    const binding = evidenceRoleMap.get(role)
    expect(binding).toBeDefined()
    expect(binding!.role).toBe(role)
    expect(binding!.manifestPath.length).toBeGreaterThan(0)
    expect(binding!.manifestSha256).toBe(binding!.contentHash)
    expect(binding!.metadata.role).toBe(role)
    expect(Object.keys(binding!.metadata).length).toBeGreaterThan(1)
    expect(binding!.attachmentId.length).toBeGreaterThan(0)
    expect(binding!.evidenceVersionId.length).toBeGreaterThan(0)
    expect(binding!.reviewState).toBe('APPROVED')
    expect(binding!.consumer).toBe(expectedConsumerByRole[role])
    expect(binding!.consumerResultId.length).toBeGreaterThan(0)
    return binding!
  })
  expect(new Set(ledger.map((item) => item.manifestPath)).size).toBe(12)
  expect(new Set(ledger.map((item) => item.manifestSha256)).size).toBe(12)
  expect(new Set(ledger.map((item) => item.attachmentId)).size).toBe(12)
  expect(new Set(ledger.map((item) => item.evidenceVersionId)).size).toBe(12)
  expect(new Set(ledger.map((item) => item.consumerResultId)).size).toBe(12)
  return ledger
}

class IntegratedJourneyDriver {
  constructor(
    readonly operatorPage: Page,
    readonly reviewerPage: Page,
    readonly evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
    readonly apiRequest: APIRequestContext,
    readonly accessToken: string,
  ) {}

  private red(checkpoint: string): never {
    throw new Error(`${checkpoint} action RED: implement through its public UI/API owner`)
  }

  async createClientAndContact(_code: string): Promise<Json> { return this.red('IA-01') }
  async createCase(_clientId: string, _caseNo: string): Promise<Json> { return this.red('IA-02') }
  async inspectCatalog(_caseId: string): Promise<Json> { return this.red('IA-03') }
  async resolveFiling(_caseId: string): Promise<Json> { return this.red('IA-04') }
  async completeFilingAndOa1(_caseId: string): Promise<Json> { return this.red('IA-05') }
  async createOaOut(_sourceId: string, _packageId: string): Promise<Json> { return this.red('IA-06') }
  async rejectInvalidReceipts(_caseId: string, _packageId: string): Promise<Json> { return this.red('IA-07') }
  async archiveOa1(_packageId: string): Promise<Json> { return this.red('IA-08') }
  async completeOa2(_caseId: string): Promise<Json> { return this.red('IA-09') }
  async createGrantOriginal(_caseId: string): Promise<Json> { return this.red('IA-10') }
  async replaceGrant(_taskId: string): Promise<Json> { return this.red('IA-11') }
  async exerciseGrantGatesAndPay(_oldId: string, _newId: string): Promise<Json> { return this.red('IA-12') }
  async createServiceDraft(_caseId: string): Promise<Json> { return this.red('IA-13') }
  async createBill(_draftId: string): Promise<Json> { return this.red('IA-14') }
  async createPayment(_clientId: string, _billId: string): Promise<Json> { return this.red('IA-15') }
  async createOffset(_lineId: string, _billId: string): Promise<Json> { return this.red('IA-16') }
  async reloadSummary(_caseId: string): Promise<Json> { return this.red('IA-17') }
  async preflight(): Promise<Json> {
    await this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    const responsePromise = this.operatorPage.waitForResponse((response) => response.status() === 200 && response.url().includes('/fees/demo-preflight'))
    await this.operatorPage.getByTestId('demo-preflight').click()
    const item = await (await responsePromise).json() as Json
    return {
      provenance: {
        bundle_id: item.bundle_id,
        bundle_version: item.bundle_version,
        manifest_sha256: item.manifest_sha256,
        template_code: item.template_code,
        template_sha256: item.template_sha256,
        rate_item_code: item.item_code,
        rate_source_ref: item.source_ref,
        rate_source_version: item.source_version,
        rate_source_sha256: item.source_sha256,
      },
      business_counts: item.business_counts,
      readiness: item.readiness,
      classification: item.authority_classification,
      customer_activation_eligible: item.customer_activation_eligible,
    }
  }

  async publicLifecycleApi(
    operation: PublicLifecycleOperation,
    pathParameters: Record<string, string>,
    data?: Json,
  ): Promise<{ status: number; body: Json }> {
    return callPublicLifecycleApi(this.apiRequest, this.accessToken, operation, pathParameters, data)
  }

  async uploadRole(documentId: string, descriptor: { role: EvidenceRole; path: string; sha256: string; metadata: Json }): Promise<EvidenceBinding> {
    const binding = await uploadAndReviewEvidenceViaVisibleUi(this.operatorPage, this.reviewerPage, documentId, descriptor)
    this.evidenceRoleMap.set(descriptor.role, binding)
    return binding
  }
}

test('Integrated Scheme A executes prior lifecycle and new finance on one case', async ({ browser, page, request }) => {
  test.setTimeout(240_000)
  for (const required of [adminUsername, adminPassword, reviewerUsername, reviewerPassword, evidenceDir, bundlePath, expectedDisclaimer]) expect(typeof required).toBe('string')

  const operatorToken = await login(page, adminUsername!, adminPassword!)
  const reviewerContext: BrowserContext = await browser.newContext()
  const reviewerPage = await reviewerContext.newPage()
  await login(reviewerPage, reviewerUsername!, reviewerPassword!)
  const evidenceRoleMap = new Map<EvidenceRole, EvidenceBinding>()
  const journey = new IntegratedJourneyDriver(page, reviewerPage, evidenceRoleMap, request, operatorToken)
  const suffix = `${Date.now()}`
  const clientCode = `IA-${suffix}`
  const caseNo = `IA-CASE-${suffix}`
  let clientId = ''; let caseId = ''; let filingPackageId = ''; let oa1SourceId = ''; let oa1PackageId = ''; let oa1TaskId = ''; let grantOriginalTaskId = ''; let grantReplacementTaskId = ''; let draftId = ''; let billId = ''; let paymentId = ''; let paymentLineId = ''; let offsetId = ''
  const manifestSha256 = process.env.FPMS_DEMO_EXPECTED_MANIFEST_SHA256 || ''

  await test.step(checkpointContract[0], async () => {
    expect(orderedRoles).toHaveLength(12)
    expect(manifestSha256).toMatch(/^[0-9a-f]{64}$/)
    for (const value of Object.values(expectedProvenance)) expect(typeof value).toBe('string')
    const snapshot = await journey.preflight()
    expect(snapshot.provenance).toEqual(expectedProvenance)
    expect(snapshot.business_counts).toEqual({ client: 0, contact: 0, case: 0, package: 0, task: 0, obligation: 0, draft: 0, bill: 0, payment: 0, offset: 0 })
    expect(snapshot.readiness).toBe('READY')
    expect(snapshot.classification).toBe('SYNTHETIC_TEST_ONLY')
    expect(snapshot.customer_activation_eligible).toBe(false)
    await expect(page.getByText('演示输入已校验')).toBeVisible()
    await expect(page.getByText(manifestSha256)).toBeVisible()
    await expect(page.getByText('SYNTHETIC_TEST_ONLY')).toBeVisible()
    await expect(page.getByText('模板代码', { exact: true })).toBeVisible()
    await expect(page.getByText('模板文件 SHA-256', { exact: true })).toBeVisible()
    await expect(page.getByText('费率来源', { exact: true })).toBeVisible()
    await expect(page.getByText('费率来源 SHA-256', { exact: true })).toBeVisible()
    await expect(page.getByText('官方费用：未配置（不计入总额）', { exact: true })).toBeVisible()
    await expect(page.getByTestId('bundle-id')).toHaveText(expectedProvenance.bundle_id!)
    await expect(page.getByTestId('bundle-version')).toHaveText(expectedProvenance.bundle_version!)
    await expect(page.getByTestId('manifest-sha256')).toHaveText(expectedProvenance.manifest_sha256!)
    await expect(page.getByTestId('template-code')).toHaveText(expectedProvenance.template_code!)
    await expect(page.getByTestId('template-sha256')).toHaveText(expectedProvenance.template_sha256!)
    await expect(page.getByTestId('rate-item-code')).toHaveText(expectedProvenance.rate_item_code!)
    await expect(page.getByTestId('rate-source-ref')).toHaveText(expectedProvenance.rate_source_ref!)
    await expect(page.getByTestId('rate-source-version')).toHaveText(expectedProvenance.rate_source_version!)
    await expect(page.getByTestId('rate-source-sha256')).toHaveText(expectedProvenance.rate_source_sha256!)
    await expect(page.getByTestId('demo-disclaimer')).toHaveText(expectedDisclaimer!)
  })

  await test.step(checkpointContract[1], async () => {
    const x = await journey.createClientAndContact(clientCode); clientId = x.client_id
    expect(x.client_count).toBe(1); expect(x.contact_count).toBe(1); expect(x.primary_contact_client_id).toBe(clientId)
  })
  await test.step(checkpointContract[2], async () => {
    const x = await journey.createCase(clientId, caseNo); caseId = x.case_id
    expect(x.case_no).toBe(caseNo); expect(x.projection).toEqual(['NEW_CASE', 'NOT_SUBMITTED', 'NOT_ESTABLISHED', 'CONFIRMED']); expect(x.legacy_display).toBe('NOT_FILED')
    expect(x.business_counts).toEqual({ package: 0, task: 0, draft: 0, bill: 0, payment: 0, offset: 0 })
  })
  await test.step(checkpointContract[3], async () => {
    const x = await journey.inspectCatalog(caseId); expect(x.row_count).toBe(60); expect(x.executable_enabled).toBe(true); expect(x.reference_only_disabled).toBe(true); expect(x.request_status).not.toBe(422)
  })
  await test.step(checkpointContract[4], async () => {
    const x = await journey.resolveFiling(caseId); filingPackageId = x.package_id
    expect(x.replayed_package_id).toBe(filingPackageId); expect(x.package_kind).toBe('FILING_PREP'); expect(x.projection).toEqual(['FILING_PREPARATION', 'NOT_SUBMITTED', 'NOT_ESTABLISHED', 'CONFIRMED'])
  })
  await test.step(checkpointContract[5], async () => {
    const x = await journey.completeFilingAndOa1(caseId); oa1SourceId = x.source_id; oa1PackageId = x.package_id; oa1TaskId = x.task_id
    for (const target of x.upload_targets as Array<{ document_id: string; descriptor: { role: EvidenceRole; path: string; sha256: string; metadata: Json } }>) await journey.uploadRole(target.document_id, target.descriptor)
    expect(x.filing_package_id).toBe(filingPackageId); expect(evidenceRoleMap.size).toBe(8)
    const filingBinding = evidenceRoleMap.get('FILING_FINAL_SUBMISSION')!
    const filingRecord = recordFilingSubmission(
      evidenceRoleMap,
      filingBinding,
      x.filing_command_result,
      x.filing_package_result,
      x.filing_activity_result,
    )
    expect(filingRecord.consumerResultId).toBe(x.filing_activity_result.id)
    for (const consumption of x.lifecycle_consumptions as Array<{ kind: 'document-lifecycle' | 'receipt'; role: EvidenceRole; consumer: string; payload: Json; result: Json }>) {
      if (consumption.kind === 'receipt') {
        recordReceiptConsumer(evidenceRoleMap, evidenceRoleMap.get(consumption.role)!, consumption.consumer, consumption.payload, consumption.result)
      } else {
        recordDocumentLifecycleConsumer(evidenceRoleMap, evidenceRoleMap.get(consumption.role)!, consumption.consumer, consumption.payload, consumption.result)
      }
    }
    expect(evidenceRoleMap.get('OA_NOTICE_1')!.consumer).toBe('oa1-notice')
    expect(x.deadline_surfaces).toEqual({ create: x.deadline, read: x.deadline, edit: x.deadline, impact_preview: x.deadline, wizard: x.deadline })
    expect(typeof x.deadline.official_due_date).toBe('string'); expect(['MANUAL_OFFICIAL_NOTICE', 'IMPORTED_OFFICIAL_NOTICE']).toContain(x.deadline.official_due_date_source); expect(x.deadline.official_due_date_status).toBe('CONFIRMED'); expect(x.replayed_package_id).toBe(oa1PackageId); expect(x.replayed_task_id).toBe(oa1TaskId); expect(x.invalid_deadline_no_write).toBe(true)
  })
  await test.step(checkpointContract[6], async () => {
    const x = await journey.createOaOut(oa1SourceId, oa1PackageId); expect(x.linked_source_id).toBe(oa1SourceId); expect(x.linked_package_id).toBe(oa1PackageId); expect(x.link_count).toBe(1); expect(x.task_status).toBe('OPEN'); expect(x.package_status).toBe('WAITING_RECEIPT')
  })
  await test.step(checkpointContract[7], async () => {
    const x = await journey.rejectInvalidReceipts(caseId, oa1PackageId); expect(x.cross_case_status).toBeGreaterThanOrEqual(400); expect(x.same_case_wrong_source_status).toBeGreaterThanOrEqual(400); expect(x.before_snapshot).toEqual(x.after_snapshot)
  })
  await test.step(checkpointContract[8], async () => {
    const x = await journey.archiveOa1(oa1PackageId); expect(x.package_status).toBe('ARCHIVED'); expect(x.closed_task_ids).toEqual([oa1TaskId]); expect(x.projection).toEqual(['PROSECUTION_MANAGEMENT', 'SUBSTANTIVE_EXAMINATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.legacy_display).toBe('SUB_EXAM')
  })
  await test.step(checkpointContract[9], async () => {
    const x = await journey.completeOa2(caseId)
    for (const target of x.upload_targets as Array<{ document_id: string; descriptor: { role: EvidenceRole; path: string; sha256: string; metadata: Json } }>) await journey.uploadRole(target.document_id, target.descriptor)
    for (const consumption of x.lifecycle_consumptions as Array<{ kind: 'document-lifecycle' | 'receipt'; role: EvidenceRole; consumer: string; payload: Json; result: Json }>) {
      if (consumption.kind === 'receipt') {
        recordReceiptConsumer(evidenceRoleMap, evidenceRoleMap.get(consumption.role)!, consumption.consumer, consumption.payload, consumption.result)
      } else {
        recordDocumentLifecycleConsumer(evidenceRoleMap, evidenceRoleMap.get(consumption.role)!, consumption.consumer, consumption.payload, consumption.result)
      }
    }
    expect(evidenceRoleMap.size).toBe(10); expect(x.source_id).not.toBe(oa1SourceId); expect(x.package_id).not.toBe(oa1PackageId); expect(x.task_id).not.toBe(oa1TaskId); expect(x.oa_out_id).not.toBe(x.oa1_oa_out_id); expect(x.receipt_id).not.toBe(x.oa1_receipt_id); expect(x.oa_sequence).toBe(2); expect(x.notice_role).toBe('OA_NOTICE_2'); expect(x.receipt_role).toBe('OA_RECEIPT_2')
    expect(x.deadline_surfaces).toEqual({ create: x.deadline, read: x.deadline, edit: x.deadline, impact_preview: x.deadline, wizard: x.deadline }); expect(typeof x.deadline.official_due_date).toBe('string'); expect(['MANUAL_OFFICIAL_NOTICE', 'IMPORTED_OFFICIAL_NOTICE']).toContain(x.deadline.official_due_date_source); expect(x.deadline.official_due_date_status).toBe('CONFIRMED'); expect(x.sequence1_reuse_no_write).toBe(true); expect(x.incomplete_deadline_no_write).toBe(true)
    expect(x.closed_task_ids).toEqual([x.task_id]); expect(x.oa1_history_after).toEqual(x.oa1_history_before); expect(x.projection).toEqual(['PROSECUTION_MANAGEMENT', 'SUBSTANTIVE_EXAMINATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.legacy_display).toBe('SUB_EXAM')
  })
  await test.step(checkpointContract[10], async () => {
    const x = await journey.createGrantOriginal(caseId)
    const binding = await journey.uploadRole(x.document_id, x.descriptor); grantOriginalTaskId = x.task_id
    recordGrantConsumer(evidenceRoleMap, binding, 'grant-original-dispatch', x.payload, x.result)
    expect(evidenceRoleMap.size).toBe(11); expect(x.source_document_id).toBe(x.document_id); expect(x.source_document_date).toBe(x.expected_source_document_date); expect(x.source_evidence_version_id).toBe(binding.evidenceVersionId); expect(x.source_content_hash).toBe(binding.contentHash); expect(x.actionable_task_ids).toEqual([grantOriginalTaskId]); expect(x.projection).toEqual(['GRANT_REGISTRATION_IN_PROGRESS', 'GRANT_REGISTRATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.official_fee_carriers).toEqual({ item: 0, obligation: 0, draft: 0, payable: 0 })
  })
  await test.step(checkpointContract[11], async () => {
    const x = await journey.replaceGrant(grantOriginalTaskId)
    const binding = await journey.uploadRole(x.document_id, x.descriptor); grantReplacementTaskId = x.replacement_task_id
    recordGrantConsumer(evidenceRoleMap, binding, 'grant-replacement-dispatch', x.payload, x.result)
    expect(evidenceRoleMap.size).toBe(12)
    expect(grantReplacementTaskId).not.toBe(grantOriginalTaskId); expect(x.original_document_id).not.toBe(x.replacement_document_id); expect(x.replacement_document_id).toBe(x.document_id); expect(x.superseded_task_id).toBe(grantOriginalTaskId); expect(x.replacement_predecessor_task_id).toBe(grantOriginalTaskId); expect(x.original_source_evidence_version_id).toBe(evidenceRoleMap.get('GRANT_NOTICE_ORIGINAL')!.evidenceVersionId); expect(x.replacement_source_evidence_version_id).toBe(binding.evidenceVersionId); expect(x.replacement_source_content_hash).toBe(binding.contentHash); expect(x.replacement_metadata).toEqual(binding.metadata); expect(x.actionable_task_ids).toEqual([grantReplacementTaskId]); expect(x.original_hash).not.toBe(x.replacement_hash); expect(x.projection).toEqual(['GRANT_REGISTRATION_IN_PROGRESS', 'GRANT_REGISTRATION', 'APPLICATION_PENDING', 'CONFIRMED'])
  })
  await test.step(checkpointContract[12], async () => {
    const x = await journey.exerciseGrantGatesAndPay(grantOriginalTaskId, grantReplacementTaskId)
    expect(x.blocked_mutations).toEqual(['generate-draft', 'batch-instruction', 'generate-notices', 'mark_waiting_client']); expect(x.blocked_statuses).toEqual([409, 409, 409, 409]); expect(x.before_snapshot).toEqual(x.after_snapshot); expect(x.current_instruction).toBe('PAY'); expect(x.current_instruction_count).toBe(1); expect(x.official_fee_carriers).toEqual({ item: 0, obligation: 0, draft: 0, payable: 0 })
  })
  await test.step(checkpointContract[13], async () => {
    const x = await journey.createServiceDraft(caseId); draftId = x.draft_id
    expect(x.case_id).toBe(caseId); expect(x.provenance).toEqual(expectedProvenance); expect(x.disclaimer).toMatch(/虚构演示输入.*不是客户授权费率.*不是官方费用/); expect(x.obligation_count).toBe(1); expect(x.draft_count).toBe(1); expect(x.draft_status).toBe('LOCKED'); expect(x.service_amount).toBe(x.bundle_amount); expect(x.official_fee_display).toBe('未配置'); expect(x.official_fee_in_total).toBe(false)
    await page.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByText(draftId, { exact: false })).toBeVisible()
    await expect(page.getByText(x.bundle_amount, { exact: false })).toBeVisible()
    await expect(page.getByText(x.disclaimer, { exact: false })).toBeVisible()
    for (const value of Object.values(expectedProvenance)) await expect(page.getByText(value!, { exact: false })).toBeVisible()
  })
  await test.step(checkpointContract[14], async () => {
    const x = await journey.createBill(draftId); billId = x.bill_id
    expect(x.replayed_bill_id).toBe(billId); expect(x.bill_count).toBe(1); expect(x.source_draft_ids).toEqual([draftId]); expect(x.consumed_draft_ids).toEqual([draftId]); expect(x.source_item_ids).toEqual(x.bill_item_source_ids); expect(x.source_item_ids).toHaveLength(1); expect(x.status).toBe('UNSETTLED'); expect(x.balance).toBe(x.bundle_amount); expect(x.currency).toBe('CNY')
  })
  await test.step(checkpointContract[15], async () => {
    const x = await journey.createPayment(clientId, billId); paymentId = x.payment_id; paymentLineId = x.payment_line_id
    expect(x.replayed_payment_id).toBe(x.payment_id); expect(x.payment_count).toBe(1); expect(x.payment_line_count).toBe(1); expect(x.amount).toBe(x.bundle_amount); expect(x.currency).toBe('CNY'); expect(x.status).toBe('UNALLOCATED'); expect(x.applied_bill_ids).toEqual([]); expect(x.suggested_bill_id).toBe(billId)
  })
  await test.step(checkpointContract[16], async () => {
    const x = await journey.createOffset(paymentLineId, billId); offsetId = x.offset_id; expect(x.active_offset_count).toBe(1); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.bill_balance).toBe('0.00'); expect(x.payment_unapplied).toBe('0.00'); expect(x.currency).toBe('CNY'); expect(x.case_receipt_received).toBe(x.bundle_amount)
  })
  await test.step(checkpointContract[17], async () => {
    const x = await journey.reloadSummary(caseId); expect(x.case_id).toBe(caseId); expect(x.route_object_ids).toEqual(x.authoritative_object_ids); expect(x.surfaces).toEqual({ case: { id: caseId, business_stage: 'GRANT_REGISTRATION_IN_PROGRESS', official_procedure_stage: 'GRANT_REGISTRATION', legal_status: 'APPLICATION_PENDING', confirmation_status: 'CONFIRMED' }, draft: { id: draftId, status: 'LOCKED', amount: x.bundle_amount, currency: 'CNY' }, bill: { id: billId, status: 'SETTLED', balance: '0.00', currency: 'CNY' }, payment: { id: paymentId, status: 'FULLY_ALLOCATED', unapplied: '0.00', currency: 'CNY' }, offset: { id: offsetId, active: true, amount: x.bundle_amount, currency: 'CNY' } }); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.synthetic_zero_count).toBe(0)
  })
  await test.step(checkpointContract[18], async () => {
    const x = await journey.reloadSummary(caseId)
    expect(x.lifecycle_status).toBe('GRANT_REGISTRATION_IN_PROGRESS'); expect(x.lifecycle_stage).toBe('GRANT_REGISTRATION'); expect(x.application_status).toBe('APPLICATION_PENDING'); expect(x.source_state).toBe('CONFIRMED'); expect(x.legacy_display).toBe('GRANT_PENDING'); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.bill_balance).toBe('0.00'); expect(x.payment_unapplied).toBe('0.00'); expect(x.currency).toBe('CNY'); expect(x.checkpoints_passed).toBe(19); expect(evidenceRoleMap.size).toBe(12)
  })

  const orderedEvidenceLedger = assertCompleteEvidenceLedger(evidenceRoleMap)
  await mkdir(evidenceDir!, { recursive: true })
  await writeFile(path.join(evidenceDir!, 'evidence-role-map.json'), JSON.stringify(orderedEvidenceLedger, null, 2))
  await reviewerContext.close()
})
