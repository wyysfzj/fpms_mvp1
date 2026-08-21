import { test, expect, type BrowserContext, type Page } from '@playwright/test'
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

const baseUrl = process.env.FPMS_BASE_URL || 'http://127.0.0.1:5173'
const apiBase = process.env.FPMS_API_URL || 'http://127.0.0.1:8000/api/v1'
const evidenceDir = process.env.FPMS_DEMO_EVIDENCE_DIR
const bundlePath = process.env.FPMS_DEMO_BUNDLE_PATH
const adminUsername = process.env.FPMS_ADMIN_USERNAME
const adminPassword = process.env.FPMS_ADMIN_PASSWORD
const reviewerUsername = process.env.FPMS_REVIEWER_USERNAME
const reviewerPassword = process.env.FPMS_REVIEWER_PASSWORD
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

async function login(page: Page, username: string, password: string): Promise<void> {
  await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
  await page.getByPlaceholder('用户名').fill(username)
  await page.getByPlaceholder('密码').fill(password)
  await page.getByRole('button', { name: '登录' }).click()
  await expect(page).not.toHaveURL(/\/login$/)
}

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

function recordLifecycleConsumer(
  evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
  binding: EvidenceBinding,
  consumer: string,
  payload: Json,
  result: Json,
): EvidenceBinding {
  expect(payload.evidence_version_id).toBe(binding.evidenceVersionId)
  expect(result.consumed_evidence_version_id).toBe(binding.evidenceVersionId)
  expect(result.consumed_content_hash).toBe(binding.contentHash)
  const updated = { ...binding, consumer, consumerResultId: String(result.id || result.activity_id || result.task_id) }
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
  expect(payload.reviewed_evidence_version_id).toBe(binding.evidenceVersionId)
  expect(payload.expected_content_hash).toBe(binding.contentHash)
  expect(result.consumed_evidence_version_id).toBe(binding.evidenceVersionId)
  expect(result.consumed_content_hash).toBe(binding.contentHash)
  const updated = { ...binding, consumer, consumerResultId: String(result.id || result.task_id) }
  evidenceRoleMap.set(binding.role, updated)
  return updated
}

function recordFilingSubmission(
  evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
  binding: EvidenceBinding,
  result: Json,
): EvidenceBinding {
  expect(result.reviewed_final_submission_version_id).toBe(binding.evidenceVersionId)
  expect(result.reviewed_final_submission_content_hash).toBe(binding.contentHash)
  expect(typeof result.external_submission_activity_id).toBe('string')
  const updated = { ...binding, consumer: 'filing-external-submission', consumerResultId: result.external_submission_activity_id }
  evidenceRoleMap.set(binding.role, updated)
  return updated
}

class IntegratedJourneyDriver {
  constructor(
    readonly operatorPage: Page,
    readonly reviewerPage: Page,
    readonly evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
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
  async preflight(): Promise<Json> { return this.red('IA-00') }

  async uploadRole(documentId: string, descriptor: { role: EvidenceRole; path: string; sha256: string; metadata: Json }): Promise<EvidenceBinding> {
    const binding = await uploadAndReviewEvidenceViaVisibleUi(this.operatorPage, this.reviewerPage, documentId, descriptor)
    this.evidenceRoleMap.set(descriptor.role, binding)
    return binding
  }
}

test('Integrated Scheme A executes prior lifecycle and new finance on one case', async ({ browser, page }) => {
  test.setTimeout(240_000)
  for (const required of [adminUsername, adminPassword, reviewerUsername, reviewerPassword, evidenceDir, bundlePath]) expect(typeof required).toBe('string')

  await login(page, adminUsername!, adminPassword!)
  const reviewerContext: BrowserContext = await browser.newContext()
  const reviewerPage = await reviewerContext.newPage()
  await login(reviewerPage, reviewerUsername!, reviewerPassword!)
  const evidenceRoleMap = new Map<EvidenceRole, EvidenceBinding>()
  const journey = new IntegratedJourneyDriver(page, reviewerPage, evidenceRoleMap)
  const suffix = `${Date.now()}`
  const clientCode = `IA-${suffix}`
  const caseNo = `IA-CASE-${suffix}`
  let clientId = ''; let caseId = ''; let filingPackageId = ''; let oa1SourceId = ''; let oa1PackageId = ''; let oa1TaskId = ''; let grantOriginalTaskId = ''; let grantReplacementTaskId = ''; let draftId = ''; let billId = ''; let paymentLineId = ''
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
    await page.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('演示输入已校验')).toBeVisible()
    await expect(page.getByText(manifestSha256)).toBeVisible()
    await expect(page.getByText('SYNTHETIC_TEST_ONLY')).toBeVisible()
    await expect(page.getByText(/模板代码/)).toBeVisible()
    await expect(page.getByText(/模板文件 SHA-256/)).toBeVisible()
    await expect(page.getByText(/费率来源/)).toBeVisible()
    await expect(page.getByText(/费率来源 SHA-256/)).toBeVisible()
    await expect(page.getByText('未配置')).toBeVisible()
    for (const value of Object.values(expectedProvenance)) await expect(page.getByText(value!, { exact: false })).toBeVisible()
    await expect(page.getByText(/虚构演示输入.*不是客户授权费率.*不是官方费用/)).toBeVisible()
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
    expect(recordFilingSubmission(evidenceRoleMap, filingBinding, x.filing_result).consumerResultId).toBe(x.filing_result.external_submission_activity_id)
    for (const consumption of x.lifecycle_consumptions as Array<{ role: EvidenceRole; consumer: string; payload: Json; result: Json }>) {
      recordLifecycleConsumer(evidenceRoleMap, evidenceRoleMap.get(consumption.role)!, consumption.consumer, consumption.payload, consumption.result)
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
    for (const consumption of x.lifecycle_consumptions as Array<{ role: EvidenceRole; consumer: string; payload: Json; result: Json }>) recordLifecycleConsumer(evidenceRoleMap, evidenceRoleMap.get(consumption.role)!, consumption.consumer, consumption.payload, consumption.result)
    expect(evidenceRoleMap.size).toBe(10); expect(x.source_id).not.toBe(oa1SourceId); expect(x.package_id).not.toBe(oa1PackageId); expect(x.task_id).not.toBe(oa1TaskId); expect(x.oa_out_id).not.toBe(x.oa1_oa_out_id); expect(x.receipt_id).not.toBe(x.oa1_receipt_id); expect(x.oa_sequence).toBe(2); expect(x.notice_role).toBe('OA_NOTICE_2'); expect(x.receipt_role).toBe('OA_RECEIPT_2')
    expect(x.deadline_surfaces).toEqual({ create: x.deadline, read: x.deadline, edit: x.deadline, impact_preview: x.deadline, wizard: x.deadline }); expect(typeof x.deadline.official_due_date).toBe('string'); expect(['MANUAL_OFFICIAL_NOTICE', 'IMPORTED_OFFICIAL_NOTICE']).toContain(x.deadline.official_due_date_source); expect(x.deadline.official_due_date_status).toBe('CONFIRMED'); expect(x.sequence1_reuse_no_write).toBe(true); expect(x.incomplete_deadline_no_write).toBe(true)
    expect(x.closed_task_ids).toEqual([x.task_id]); expect(x.oa1_history_after).toEqual(x.oa1_history_before); expect(x.projection).toEqual(['PROSECUTION_MANAGEMENT', 'SUBSTANTIVE_EXAMINATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.legacy_display).toBe('SUB_EXAM')
  })
  await test.step(checkpointContract[10], async () => {
    const x = await journey.createGrantOriginal(caseId)
    const binding = await journey.uploadRole(x.document_id, x.descriptor); grantOriginalTaskId = x.task_id
    recordGrantConsumer(evidenceRoleMap, binding, 'grant-original-dispatch', x.payload, x.result)
    expect(evidenceRoleMap.size).toBe(11); expect(x.projection).toEqual(['GRANT_REGISTRATION_IN_PROGRESS', 'GRANT_REGISTRATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.official_fee_carriers).toEqual({ item: 0, obligation: 0, draft: 0, payable: 0 })
  })
  await test.step(checkpointContract[11], async () => {
    const x = await journey.replaceGrant(grantOriginalTaskId)
    const binding = await journey.uploadRole(x.document_id, x.descriptor); grantReplacementTaskId = x.replacement_task_id
    recordGrantConsumer(evidenceRoleMap, binding, 'grant-replacement-dispatch', x.payload, x.result)
    expect(evidenceRoleMap.size).toBe(12)
    expect(grantReplacementTaskId).not.toBe(grantOriginalTaskId); expect(x.superseded_task_id).toBe(grantOriginalTaskId); expect(x.actionable_task_ids).toEqual([grantReplacementTaskId]); expect(x.original_hash).not.toBe(x.replacement_hash); expect(x.projection).toEqual(['GRANT_REGISTRATION_IN_PROGRESS', 'GRANT_REGISTRATION', 'APPLICATION_PENDING', 'CONFIRMED'])
  })
  await test.step(checkpointContract[12], async () => {
    const x = await journey.exerciseGrantGatesAndPay(grantOriginalTaskId, grantReplacementTaskId)
    expect(x.blocked_mutations).toEqual(['generate-draft', 'batch-instruction', 'generate-notices', 'mark_waiting_client']); expect(x.blocked_statuses).toEqual([409, 409, 409, 409]); expect(x.before_snapshot).toEqual(x.after_snapshot); expect(x.current_instruction).toBe('PAY'); expect(x.current_instruction_count).toBe(1); expect(x.official_fee_carriers).toEqual({ item: 0, obligation: 0, draft: 0, payable: 0 })
  })
  await test.step(checkpointContract[13], async () => {
    const x = await journey.createServiceDraft(caseId); draftId = x.draft_id
    expect(x.case_id).toBe(caseId); expect(x.provenance).toEqual(expectedProvenance); expect(x.disclaimer).toMatch(/虚构演示输入.*不是客户授权费率.*不是官方费用/); expect(x.obligation_count).toBe(1); expect(x.draft_count).toBe(1); expect(x.draft_status).toBe('LOCKED'); expect(x.service_amount).toBe(x.bundle_amount); expect(x.official_fee_display).toBe('未配置'); expect(x.official_fee_in_total).toBe(false)
  })
  await test.step(checkpointContract[14], async () => {
    const x = await journey.createBill(draftId); billId = x.bill_id
    expect(x.replayed_bill_id).toBe(billId); expect(x.bill_count).toBe(1); expect(x.source_draft_ids).toEqual([draftId]); expect(x.consumed_draft_ids).toEqual([draftId]); expect(x.source_item_ids).toEqual(x.bill_item_source_ids); expect(x.source_item_ids).toHaveLength(1); expect(x.status).toBe('UNSETTLED'); expect(x.balance).toBe(x.bundle_amount); expect(x.currency).toBe('CNY')
  })
  await test.step(checkpointContract[15], async () => {
    const x = await journey.createPayment(clientId, billId); paymentLineId = x.payment_line_id
    expect(x.replayed_payment_id).toBe(x.payment_id); expect(x.payment_count).toBe(1); expect(x.payment_line_count).toBe(1); expect(x.amount).toBe(x.bundle_amount); expect(x.currency).toBe('CNY'); expect(x.status).toBe('UNALLOCATED'); expect(x.applied_bill_ids).toEqual([]); expect(x.suggested_bill_id).toBe(billId)
  })
  await test.step(checkpointContract[16], async () => {
    const x = await journey.createOffset(paymentLineId, billId); expect(x.active_offset_count).toBe(1); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.bill_balance).toBe('0.00'); expect(x.payment_unapplied).toBe('0.00'); expect(x.currency).toBe('CNY'); expect(x.case_receipt_received).toBe(x.bundle_amount)
  })
  await test.step(checkpointContract[17], async () => {
    const x = await journey.reloadSummary(caseId); expect(x.case_id).toBe(caseId); expect(x.route_object_ids).toEqual(x.authoritative_object_ids); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.synthetic_zero_count).toBe(0)
  })
  await test.step(checkpointContract[18], async () => {
    const x = await journey.reloadSummary(caseId)
    expect(x.lifecycle_status).toBe('GRANT_REGISTRATION_IN_PROGRESS'); expect(x.lifecycle_stage).toBe('GRANT_REGISTRATION'); expect(x.application_status).toBe('APPLICATION_PENDING'); expect(x.source_state).toBe('CONFIRMED'); expect(x.legacy_display).toBe('GRANT_PENDING'); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.bill_balance).toBe('0.00'); expect(x.payment_unapplied).toBe('0.00'); expect(x.currency).toBe('CNY'); expect(x.checkpoints_passed).toBe(19); expect(evidenceRoleMap.size).toBe(12)
  })

  await mkdir(evidenceDir!, { recursive: true })
  await writeFile(path.join(evidenceDir!, 'evidence-role-map.json'), JSON.stringify([...evidenceRoleMap.values()], null, 2))
  await reviewerContext.close()
})
