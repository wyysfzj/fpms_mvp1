import { test, expect, type APIRequestContext, type BrowserContext, type Page } from '@playwright/test'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

type Json = Record<string, any>

function observedOverlayPackages(overlay: Json): Json[] {
  const byId = new Map<string, Json>()
  for (const milestone of overlay.milestones as Json[]) {
    for (const item of (milestone.work_packages || []) as Json[]) {
      if (typeof item.package_id === 'string' && item.package_id.length > 0) byId.set(item.package_id, item)
    }
  }
  return [...byId.values()]
}

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

type OaReplyOutputDescriptor = {
  oa_sequence: 1 | 2
  official_file_role: 'OA_STATEMENT_WORD' | 'OA_STATEMENT_PDF' | 'OA_MODIFIED_CLAIMS' | 'ELECTRONIC_RECEIPT'
  title_zh_cn: string
  classification: 'SYNTHETIC_TEST_OUTPUT'
  path: string
  media_type: string
  sha256: string
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
const integratedEvidenceJson = process.env.FPMS_DEMO_INTEGRATED_EVIDENCE_JSON
const oaReplyOutputJson = process.env.FPMS_DEMO_INTEGRATED_OA_REPLY_OUTPUT_JSON
const expectedScenario = {
  customerName: process.env.FPMS_DEMO_CUSTOMER_NAME,
  customerCodePrefix: process.env.FPMS_DEMO_CUSTOMER_CODE_PREFIX,
  contactName: process.env.FPMS_DEMO_CONTACT_NAME,
  contactTitle: process.env.FPMS_DEMO_CONTACT_TITLE,
  contactEmail: process.env.FPMS_DEMO_CONTACT_EMAIL,
  caseNoPrefix: process.env.FPMS_DEMO_CASE_NO_PREFIX,
  caseTitle: process.env.FPMS_DEMO_CASE_TITLE,
  serviceItemName: process.env.FPMS_DEMO_SERVICE_ITEM_NAME,
  billNoPrefix: process.env.FPMS_DEMO_BILL_NO_PREFIX,
  paymentNoPrefix: process.env.FPMS_DEMO_PAYMENT_NO_PREFIX,
  bankRefPrefix: process.env.FPMS_DEMO_BANK_REF_PREFIX,
  stageOrder: process.env.FPMS_DEMO_CUSTOMER_STAGE_ORDER,
}
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

function evidenceDescriptors(): Map<EvidenceRole, { role: EvidenceRole; path: string; sha256: string; metadata: Json }> {
  expect(typeof integratedEvidenceJson).toBe('string')
  const rows = JSON.parse(integratedEvidenceJson!) as Array<{ role: EvidenceRole; path: string; sha256: string; metadata: Json }>
  expect(rows.map((row) => row.role)).toEqual(orderedRoles)
  expect(new Set(rows.map((row) => row.path)).size).toBe(12)
  expect(new Set(rows.map((row) => row.sha256)).size).toBe(12)
  for (const row of rows) {
    expect(row.path).toMatch(/^\//)
    expect(row.sha256).toMatch(/^[0-9a-f]{64}$/)
    expect(row.metadata.role ?? row.role).toBe(row.role)
  }
  return new Map(rows.map((row) => [row.role, row]))
}

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
  const officialRole = descriptor.role === 'FILING_FINAL_SUBMISSION'
    ? '合并PDF'
    : descriptor.role.includes('RECEIPT')
      ? '电子申请回执'
      : '官方通知书PDF'
  await operatorPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
  await operatorPage.getByTestId('attachment-open-upload').click()
  await operatorPage.getByTestId('attachment-file-picker').locator('input[type=file]').setInputFiles(descriptor.path)
  const uploadDialog = operatorPage.getByRole('dialog', { name: '上传附件' })
  await uploadDialog.locator('.el-form-item').filter({ hasText: '附件角色' }).locator('.el-select__wrapper').click()
  await operatorPage.getByRole('option', { name: officialRole, exact: true }).click()
  const uploadResponse = operatorPage.waitForResponse((response) => response.status() === 201 && response.url().includes('/attachments'))
  await operatorPage.getByRole('button', { name: '确认上传' }).click()
  const uploaded = await (await uploadResponse).json() as Json
  expect(uploaded.content_hash).toBe(`sha256:${descriptor.sha256}`)
  const uploadedFileName = descriptor.path.replace(/^.*\//, '')
  const uploadedItem = operatorPage.locator('.attachment-item').filter({ hasText: uploadedFileName }).first()
  await expect(uploadedItem).toBeVisible()
  const uploadedTestId = await uploadedItem.getAttribute('data-testid')
  expect(uploadedTestId).toMatch(/^attachment-\S+$/)
  const evidenceVersionId = uploadedTestId!.replace('attachment-', '')

  await reviewerPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
  const reviewResponse = reviewerPage.waitForResponse((response) => response.status() === 200 && response.url().includes('/review'))
  await reviewerPage.getByTestId(`attachment-${evidenceVersionId}`).getByRole('button', { name: '通过' }).click()
  const reviewed = await (await reviewResponse).json() as Json
  expect(reviewed.review_state).toBe('APPROVED')
  expect(reviewed.evidence_version_id).toBe(evidenceVersionId)
  return {
    role: descriptor.role,
    manifestPath: descriptor.path,
    manifestSha256: descriptor.sha256,
    metadata: descriptor.metadata,
    attachmentId: uploaded.id,
    evidenceVersionId,
    contentHash: uploaded.content_hash,
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
  expect(binding.contentHash).toBe(`sha256:${binding.manifestSha256}`)
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
  expect(binding.contentHash).toBe(`sha256:${binding.manifestSha256}`)
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
  expect(binding.contentHash).toBe(`sha256:${binding.manifestSha256}`)
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
  expect(binding.contentHash).toBe(`sha256:${binding.manifestSha256}`)
  expect(commandResult.package_id).toBe(packageResult.package.id)
  expect(commandResult.checklist_item.item_code).toBe('EXTERNAL_SUBMISSION_RECORDED')
  expect(commandResult.checklist_item.status).toBe('DONE')
  const manifest = (packageResult.filing_file_roles as Json[]).find(
    (item) => item.evidence_version_id === binding.evidenceVersionId,
  )
  expect(manifest).toBeDefined()
  expect(manifest!.content_hash).toBe(binding.contentHash)
  expect(activityResult.activity_type).toBe('FILING_EXTERNAL_SUBMISSION_RECORDED')
  expect(activityResult.confirmation_status).toBe('CONFIRMED')
  expect(activityResult.evidence_summary).toContainEqual(expect.objectContaining({
    evidence_kind: 'FINAL_SUBMISSION_VERSION',
    object_id: binding.evidenceVersionId,
    content_hash: binding.contentHash,
  }))
  expect(typeof activityResult.activity_id).toBe('string')
  expect(activityResult.activity_id.length).toBeGreaterThan(0)
  const updated = { ...binding, consumer: 'filing-external-submission', consumerResultId: activityResult.activity_id }
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
    expect(binding!.contentHash).toBe(`sha256:${binding!.manifestSha256}`)
    expect(binding!.metadata.role ?? binding!.role).toBe(role)
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
  private clientId = ''
  private clientName = ''
  private caseId = ''
  private caseNo = ''
  private filingPackageId = ''
  private oa1SourceTitle = ''
  private oa1SourceId = ''
  private oa1ReplyId = ''
  private oa1ReceiptId = ''
  private oa1History: Json = {}
  private grantTemplateId = ''
  private grantOriginalDocumentId = ''
  private draftId = ''
  private billId = ''
  private paymentId = ''
  private paymentLineId = ''
  private offsetId = ''
  private bundleAmount = ''

  constructor(
    readonly operatorPage: Page,
    readonly reviewerPage: Page,
    readonly evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
    readonly apiRequest: APIRequestContext,
    readonly accessToken: string,
    readonly evidenceDescriptorsByRole: Map<EvidenceRole, { role: EvidenceRole; path: string; sha256: string; metadata: Json }>,
    readonly oaReplyOutputs: Map<string, OaReplyOutputDescriptor>,
  ) {}

  private red(checkpoint: string): never {
    throw new Error(`${checkpoint} action RED: implement through its public UI/API owner`)
  }

  async createClientAndContact(code: string): Promise<Json> {
    this.clientName = expectedScenario.customerName!
    await this.operatorPage.goto(`${baseUrl}/clients/new`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '新建客户' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入客户名称').fill(this.clientName)
    await this.operatorPage.getByPlaceholder('请输入客户代码（可选）').fill(code)
    await this.operatorPage.getByPlaceholder('请输入邮箱地址').fill('service@chengyue-ip.example')
    const clientResponse = this.operatorPage.waitForResponse((response) => response.status() === 201 && new URL(response.url()).pathname.endsWith('/api/v1/clients'))
    await this.operatorPage.getByRole('button', { name: '创建客户' }).click()
    const client = await (await clientResponse).json() as Json
    expect(client.client_code).toBe(code)
    this.clientId = client.id

    await this.operatorPage.goto(`${baseUrl}/clients/${client.id}`, { waitUntil: 'domcontentloaded' })
    await this.operatorPage.getByRole('tab', { name: '联系人' }).click()
    await this.operatorPage.getByRole('button', { name: '新增联系人' }).click()
    const dialog = this.operatorPage.getByRole('dialog', { name: '新增联系人' })
    await dialog.locator('.el-form-item').filter({ hasText: '姓名' }).getByRole('textbox').fill(expectedScenario.contactName!)
    await dialog.locator('.el-form-item').filter({ hasText: '职务' }).getByRole('textbox').fill(expectedScenario.contactTitle!)
    await dialog.locator('.el-form-item').filter({ hasText: '邮箱' }).getByRole('textbox').fill(expectedScenario.contactEmail!)
    await dialog.locator('.el-form-item').filter({ hasText: '主联系人' }).locator('.el-switch').click()
    const contactResponse = this.operatorPage.waitForResponse((response) => response.status() === 201 && new URL(response.url()).pathname.endsWith(`/api/v1/clients/${client.id}/contacts`))
    const contactListResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/clients/${client.id}/contacts`))
    await dialog.getByRole('button', { name: '确定' }).click()
    const contact = await (await contactResponse).json() as Json
    const contactList = await (await contactListResponse).json() as Json[]
    expect(contact.client_id).toBe(client.id)
    expect(contact.is_primary).toBe(true)
    await expect(this.operatorPage.getByText(expectedScenario.contactName!, { exact: true })).toBeVisible()
    const clientListResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/clients') && url.searchParams.get('page_size') === '20'
    })
    await this.operatorPage.goto(`${baseUrl}/clients`, { waitUntil: 'domcontentloaded' })
    const clientList = await (await clientListResponse).json() as Json
    const clientMatches = (clientList.items as Json[]).filter((item) => item.client_code === code && item.name_cn === this.clientName)
    const contactMatches = contactList.filter((item) => item.client_id === client.id && item.contact_name === expectedScenario.contactName && item.is_primary === true)
    return { client_id: client.id, contact_id: contact.id, client_code: code, client_name: this.clientName, contact_name: contact.contact_name, contact_title: contact.title, contact_email: contact.email, client_count: clientMatches.length, contact_count: contactMatches.length, primary_contact_client_id: contact.client_id }
  }

  async createCase(clientId: string, caseNo: string): Promise<Json> {
    this.caseId = ''
    this.caseNo = caseNo
    await this.operatorPage.goto(`${baseUrl}/cases/new`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '新建案件' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入案号（例如：P2024-001）').fill(caseNo)
    await this.operatorPage.getByPlaceholder('请输入案件标题').fill(expectedScenario.caseTitle!)
    const clientField = this.operatorPage.locator('.el-form-item').filter({ hasText: '客户' }).first()
    await clientField.getByRole('combobox').click()
    await this.operatorPage.getByRole('option', { name: this.clientName }).click()
    await this.operatorPage.locator('.el-collapse-item__header').filter({ hasText: '申请人信息' }).click()
    await this.operatorPage.getByRole('button', { name: '新增申请人', exact: true }).click()
    const applicantField = this.operatorPage.locator('.el-form-item').filter({ hasText: '从客户主数据回填' }).first()
    await applicantField.getByRole('combobox').click()
    await this.operatorPage.getByRole('option', { name: this.clientName }).last().click()
    await expect(this.operatorPage.getByPlaceholder('申请人中文名称')).toHaveValue(this.clientName)
    await this.operatorPage.getByText('控制标记', { exact: true }).click()
    const reductionField = this.operatorPage.locator('.el-form-item').filter({ hasText: '费用减缓比例' }).first()
    await reductionField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option', { name: '不减免（0）' }).click()
    const caseResponse = this.operatorPage.waitForResponse((response) => new URL(response.url()).pathname.endsWith('/api/v1/cases'))
    await this.operatorPage.getByRole('button', { name: '创建案件' }).click()
    const created = await (await caseResponse).json() as Json
    expect((await caseResponse).status(), JSON.stringify(created)).toBe(201)
    this.caseId = created.id
    expect(created.client_id).toBe(clientId)
    expect(created.status).toBe('NOT_FILED')

    const overlayResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/cases/${created.id}/lifecycle-overlay`))
    const taskResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/tasks') && url.searchParams.get('case_id') === created.id
    })
    const draftResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/fees/drafts') && url.searchParams.get('case_id') === created.id
    })
    await this.operatorPage.goto(`${baseUrl}/cases/${created.id}`, { waitUntil: 'domcontentloaded' })
    const overlay = await (await overlayResponse).json() as Json
    const taskPage = await (await taskResponse).json() as Json
    const draftPage = await (await draftResponse).json() as Json
    const center = overlay.center_snapshot
    const packages = observedOverlayPackages(overlay)

    const billResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/bills'))
    await this.operatorPage.goto(`${baseUrl}/billing/bills`, { waitUntil: 'domcontentloaded' })
    expect((await billResponse).status()).toBe(200)
    await expect(this.operatorPage.getByText('暂无账单', { exact: true })).toBeVisible()
    const billCount = await this.operatorPage.locator('.el-table__row').count()
    const paymentResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/payments'))
    await this.operatorPage.goto(`${baseUrl}/billing/payments`, { waitUntil: 'domcontentloaded' })
    expect((await paymentResponse).status()).toBe(200)
    await expect(this.operatorPage.getByText('暂无预收款记录', { exact: true })).toBeVisible()
    const paymentCount = await this.operatorPage.locator('.el-table__row').count()
    const offsetResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/offsets'))
    await this.operatorPage.goto(`${baseUrl}/billing/offsets`, { waitUntil: 'domcontentloaded' })
    expect((await offsetResponse).status()).toBe(200)
    await expect(this.operatorPage.getByText('暂无数据', { exact: true })).toBeVisible()
    const offsetCount = await this.operatorPage.locator('.el-table__row').count()
    return {
      case_id: created.id,
      case_no: created.case_no,
      case_title: created.title_cn,
      projection: [center.business_stage, center.official_procedure_stage, center.legal_status, center.verification_status],
      legacy_display: created.status,
      business_counts: {
        package: packages.length,
        task: (taskPage.items as Json[]).length,
        draft: (draftPage.items as Json[]).length,
        bill: billCount,
        payment: paymentCount,
        offset: offsetCount,
      },
    }
  }

  async inspectCatalog(caseId: string): Promise<Json> {
    const templateResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/doc-templates'))
    await this.operatorPage.goto(`${baseUrl}/documents/wizard`, { waitUntil: 'domcontentloaded' })
    const requestStatus = (await templateResponse).status()
    await expect(this.operatorPage.getByRole('heading', { name: '中间文件向导' })).toBeVisible()
    await this.operatorPage.getByText('收文', { exact: true }).first().click()
    const templateField = this.operatorPage.locator('.defaults-field').filter({ hasText: '文书模板' }).first()
    await templateField.locator('.el-select__wrapper').click()
    const rows = this.operatorPage.getByRole('option').filter({ hasText: 'OFFICIAL_NOTICE_' })
    await expect(rows).toHaveCount(60)
    const executable = this.operatorPage.getByRole('option', { name: /OFFICIAL_NOTICE_001.*可执行/ })
    const reference = this.operatorPage.getByRole('option', { name: /OFFICIAL_NOTICE_010.*仅供参考/ })
    await expect(executable).toBeEnabled()
    await expect(reference).toBeDisabled()
    await this.operatorPage.keyboard.press('Escape')
    return { row_count: await rows.count(), executable_enabled: await executable.isEnabled(), reference_only_disabled: await reference.isDisabled(), request_status: requestStatus }
  }

  async resolveFiling(caseId: string): Promise<Json> {
    const created = await this.publicLifecycleApi('RESOLVE_FILING', { case_id: caseId })
    expect(created.status).toBe(200)
    const replayed = await this.publicLifecycleApi('RESOLVE_FILING', { case_id: caseId })
    expect(replayed.status).toBe(200)
    const packageId = created.body.package.id as string
    this.filingPackageId = packageId
    expect(replayed.body.package.id).toBe(packageId)
    await this.operatorPage.goto(`${baseUrl}/official-workflows/filing-preparation?package_id=${packageId}`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '新申请递交准备' })).toBeVisible()
    const overlayResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/cases/${caseId}/lifecycle-overlay`))
    await this.operatorPage.goto(`${baseUrl}/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    const overlay = await (await overlayResponse).json() as Json
    const center = overlay.center_snapshot
    return { package_id: packageId, replayed_package_id: replayed.body.package.id, package_kind: created.body.package.package_kind, projection: [center.business_stage, center.official_procedure_stage, center.legal_status, center.verification_status] }
  }

  private async createDocumentViaVisibleUi(
    caseId: string,
    title: string,
    documentDate: string,
    templateCode?: string,
    deadline?: { official_due_date: string; official_due_date_source: string; official_due_date_status: string },
    replyToTitle?: string,
    direction: 'IN' | 'OUT' = 'IN',
  ): Promise<{ document: Json; impact: Json | null }> {
    await this.operatorPage.goto(`${baseUrl}/documents/new?case_id=${caseId}`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '登记往来文件' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入文件标题').fill(title)
    await this.operatorPage.getByText(direction === 'IN' ? '收文' : '发文', { exact: true }).click()
    await this.operatorPage.getByPlaceholder('请选择日期').fill(documentDate)
    const typeField = this.operatorPage.locator('.el-form-item').filter({
      has: this.operatorPage.locator('.el-form-item__label').filter({ hasText: /^文件类型$/ }),
    })
    await expect(typeField).toHaveCount(1)
    const typeSelect = typeField.locator('.el-select__wrapper')
    await expect(typeSelect).toBeVisible()
    await typeSelect.click()
    const typeOption = this.operatorPage.getByRole('option', { name: direction === 'IN' ? '官方来文' : '官方去文', exact: true })
    await expect(typeOption).toBeVisible()
    await typeOption.click()
    if (templateCode) {
      const templateField = this.operatorPage.locator('.el-form-item').filter({ hasText: '文件模板' }).first()
      await templateField.locator('.el-select__wrapper').click()
      await this.operatorPage.getByRole('option').filter({ hasText: templateCode }).first().click()
    }
    if (replyToTitle) {
      const replyField = this.operatorPage.locator('.el-form-item').filter({ hasText: '回复来源文件' }).first()
      await replyField.locator('.el-select__wrapper').click()
      await this.operatorPage.getByRole('option').filter({ hasText: replyToTitle }).first().click()
    }
    let impact: Json | null = null
    if (deadline) {
      await this.operatorPage.getByPlaceholder('请选择官方截止日').fill(deadline.official_due_date)
      const sourceField = this.operatorPage.locator('.el-form-item').filter({ hasText: '截止日来源' }).first()
      await sourceField.locator('.el-select__wrapper').click()
      const sourceLabel = deadline.official_due_date_source === 'IMPORTED_OFFICIAL_NOTICE'
        ? '从官方通知导入'
        : '人工核对官方通知'
      await this.operatorPage.getByRole('option', { name: sourceLabel, exact: true }).click()
      const impactResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/documents/impact-preview'))
      const statusField = this.operatorPage.locator('.el-form-item').filter({ hasText: '确认状态' }).first()
      await statusField.locator('.el-select__wrapper').click()
      await this.operatorPage.getByRole('option', { name: '已确认', exact: true }).click()
      impact = await (await impactResponse).json() as Json
    }
    await expect(this.operatorPage.getByPlaceholder('请输入文件标题')).toHaveValue(title)
    await expect(this.operatorPage.getByPlaceholder('请选择日期')).toHaveValue(documentDate)
    await expect(typeField).toContainText(direction === 'IN' ? '官方来文' : '官方去文')
    await expect(this.operatorPage.getByPlaceholder('案件编号已自动带入')).toHaveValue(this.caseNo)
    const submitButton = this.operatorPage.getByRole('button', { name: '登记往来文件', exact: true })
    await expect(submitButton).toBeEnabled()
    const createResponse = this.operatorPage.waitForResponse(
      (response) => new URL(response.url()).pathname.endsWith('/api/v1/documents'),
      { timeout: 5_000 },
    )
    await submitButton.click({ force: true })
    await this.operatorPage.waitForTimeout(250)
    expect(await this.operatorPage.locator('.el-form-item__error').count()).toBe(0)
    const document = await (await createResponse).json() as Json
    expect((await createResponse).status(), JSON.stringify(document)).toBe(201)
    return { document, impact }
  }

  private async loadLifecycleOverlay(caseId: string): Promise<Json> {
    const response = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/cases/${caseId}/lifecycle-overlay`))
    await this.operatorPage.goto(`${baseUrl}/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    return await (await response).json() as Json
  }

  private async visibleCaseSnapshot(caseId: string): Promise<Json> {
    const documentsResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/documents') && url.searchParams.get('page_size') === '20'
    })
    await this.operatorPage.goto(`${baseUrl}/documents`, { waitUntil: 'domcontentloaded' })
    const documentPage = await (await documentsResponse).json() as Json
    const documents = (documentPage.items as Json[]).filter((item) => item.case_id === caseId)

    const tasksResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/tasks') && url.searchParams.get('page_size') === '20' && url.searchParams.get('status') === null
    })
    await this.operatorPage.goto(`${baseUrl}/tasks`, { waitUntil: 'domcontentloaded' })
    const taskPage = await (await tasksResponse).json() as Json
    const tasks = (taskPage.items as Json[]).filter((item) => item.case_id === caseId)
    const draftResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/fees/drafts') && url.searchParams.get('case_id') === caseId
    })
    const overlay = await this.loadLifecycleOverlay(caseId)
    const draftPage = await (await draftResponse).json() as Json
    const grantResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/grant-fee-tasks/list'))
    await this.operatorPage.goto(`${baseUrl}/grant-fee/tasks`, { waitUntil: 'domcontentloaded' })
    const grantPage = await (await grantResponse).json() as Json
    const grantTasks = (grantPage.items as Json[]).filter((item) => item.case_id === caseId)
    const byObligation = new Map<string, Json>()
    for (const milestone of overlay.milestones as Json[]) {
      for (const obligation of (milestone.fee_obligations || []) as Json[]) {
        if (obligation.fee_domain === 'GOV' && typeof obligation.obligation_id === 'string') byObligation.set(obligation.obligation_id, obligation)
      }
    }
    const obligations = [...byObligation.values()]
    const lineIds = new Set(obligations.flatMap((item) => (item.lines as Json[]).map((line) => line.line_id as string)))
    const payableIds = new Set(obligations.flatMap((item) => (item.lines as Json[])
      .filter((line) => typeof line.payable_amount === 'string' && line.payable_amount !== '0.00')
      .map((line) => line.line_id as string)))
    const grantDrafts = (draftPage.items as Json[]).filter((item) => item.draft_type === 'GRANT_FEE')
    return {
      document_ids: documents.map((item) => item.id).sort(),
      document_titles: documents.map((item) => item.title).sort(),
      document_deadlines: documents.map((item) => [item.id, item.official_due_date, item.official_due_date_source, item.official_due_date_status]).sort(),
      task_ids: tasks.map((item) => item.id).sort(),
      task_states: tasks.map((item) => [item.id, item.status]).sort(),
      package_ids: observedOverlayPackages(overlay).map((item) => item.package_id),
      package_states: observedOverlayPackages(overlay).map((item) => [item.package_id, item.package_kind, item.status, item.source_document_id, item.reply_document_id]),
      grant_tasks: grantTasks,
      official_fee_carriers: { item: lineIds.size, obligation: obligations.length, draft: grantDrafts.length, payable: payableIds.size },
      center_snapshot: overlay.center_snapshot,
    }
  }

  private async visibleOaTasks(caseId: string, documentId: string): Promise<Json> {
    const tasksResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/tasks') && url.searchParams.get('page_size') === '20' && url.searchParams.get('status') === null
    })
    await this.operatorPage.goto(`${baseUrl}/tasks`, { waitUntil: 'domcontentloaded' })
    const taskPage = await (await tasksResponse).json() as Json
    const matches = (taskPage.items as Json[]).filter((item) => item.case_id === caseId && item.document_id === documentId)
    return { count: matches.length, ids: matches.map((item) => item.id).sort(), states: matches.map((item) => item.status).sort() }
  }

  private async verifyMissingDeadlineNoWrite(caseId: string, templateCode = 'OFFICIAL_NOTICE_003', label = '第一次'): Promise<Json> {
    const title = `${label}审查意见通知书（补录）-${this.caseNo}`
    const before = await this.visibleCaseSnapshot(caseId)
    await this.operatorPage.goto(`${baseUrl}/documents/new?case_id=${caseId}`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '登记往来文件' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入文件标题').fill(title)
    await this.operatorPage.getByText('收文', { exact: true }).first().click()
    await this.operatorPage.getByPlaceholder('请选择日期').fill('2026-08-08')
    const typeField = this.operatorPage.locator('.el-form-item').filter({ hasText: '文件类型' }).first()
    await typeField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option', { name: '官方来文', exact: true }).click()
    const templateField = this.operatorPage.locator('.el-form-item').filter({ hasText: '文件模板' }).first()
    await templateField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option').filter({ hasText: templateCode }).first().click()
    const rejectedResponse = this.operatorPage.waitForResponse(
      (response) => response.status() >= 400 && new URL(response.url()).pathname.endsWith('/api/v1/documents'),
    )
    await this.operatorPage.getByRole('button', { name: '登记往来文件', exact: true }).click({ force: true })
    const rejected = await rejectedResponse
    const after = await this.visibleCaseSnapshot(caseId)
    expect(after).toEqual(before)
    return { status: rejected.status(), title_absent: !(after.document_titles as string[]).includes(title), before, after }
  }

  private async verifyContentEdit(documentId: string, deadline: Json): Promise<Json> {
    const lockedBefore = await this.visibleCaseSnapshot(this.caseId)
    const readResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/documents/${documentId}`))
    await this.operatorPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
    const read = await (await readResponse).json() as Json
    await this.operatorPage.getByRole('button', { name: '编辑往来文件' }).first().click()
    await expect(this.operatorPage.getByRole('heading', { name: '编辑文档' })).toBeVisible()
    await expect(this.operatorPage.getByPlaceholder('请选择官方截止日')).toBeDisabled()
    const sourceField = this.operatorPage.locator('.el-form-item').filter({ hasText: '截止日来源' }).first()
    await expect(sourceField.getByRole('combobox')).toBeDisabled()
    await expect(this.operatorPage.locator('.deadline-lineage-card').getByText('已确认', { exact: true })).toBeVisible()
    const lockedAfter = await this.visibleCaseSnapshot(this.caseId)
    expect(lockedAfter).toEqual(lockedBefore)
    const rereadResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/documents/${documentId}`))
    await this.operatorPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
    await rereadResponse
    await this.operatorPage.getByRole('button', { name: '编辑往来文件' }).first().click()
    await expect(this.operatorPage.getByRole('heading', { name: '编辑文档' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入文档内容或说明').fill('已核对通知书内容及官方截止日')
    const updateResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/documents/${documentId}`))
    await this.operatorPage.getByRole('button', { name: '保存修改' }).click()
    const edited = await (await updateResponse).json() as Json
    for (const current of [read, edited]) {
      const currentDeadline = {
        official_due_date: current.official_due_date,
        official_due_date_source: current.official_due_date_source,
        official_due_date_status: current.official_due_date_status,
      }
      expect(currentDeadline).toEqual(deadline)
    }
    return {
      read_deadline: { official_due_date: read.official_due_date, official_due_date_source: read.official_due_date_source, official_due_date_status: read.official_due_date_status },
      edit_deadline: { official_due_date: edited.official_due_date, official_due_date_source: edited.official_due_date_source, official_due_date_status: edited.official_due_date_status },
      changed_deadline_gate: { date_disabled: true, source_disabled: true, status_visible: true, before: lockedBefore, after: lockedAfter },
    }
  }

  private async verifyWizardDeadline(caseNo: string, templateCode: string, deadline: Json): Promise<Json> {
    await this.operatorPage.goto(`${baseUrl}/documents/wizard`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '中间文件向导' })).toBeVisible()
    await this.operatorPage.getByText('收文', { exact: true }).first().click()
    const templateField = this.operatorPage.locator('.defaults-field').filter({ hasText: '文书模板' }).first()
    await templateField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option').filter({ hasText: templateCode }).first().click()
    await this.operatorPage.getByPlaceholder('请选择发文日期').fill('2026-08-08')
    await this.operatorPage.getByPlaceholder(/请输入案卷号或申请号，每行一条/).fill(caseNo)
    await this.operatorPage.getByRole('button', { name: '拆分为逐行列表' }).click()
    await this.operatorPage.getByRole('button', { name: '解析全部' }).click()
    await expect(this.operatorPage.getByText('已解析', { exact: true })).toBeVisible()
    await this.operatorPage.getByRole('button', { name: '下一步' }).click()
    await this.operatorPage.getByPlaceholder('请选择官方截止日').fill(deadline.official_due_date)
    const deadlineSourceField = this.operatorPage.locator('.step2-field').filter({ hasText: '截止日来源' }).first()
    await deadlineSourceField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option', { name: '人工核对官方通知', exact: true }).click()
    const deadlineStatusField = this.operatorPage.locator('.step2-field').filter({ hasText: '确认状态' }).first()
    await deadlineStatusField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option', { name: '已确认', exact: true }).click()
    const retainedDate = await this.operatorPage.getByPlaceholder('请选择官方截止日').inputValue()
    const retainedSource = (await deadlineSourceField.locator('.el-select__placeholder').textContent())?.trim()
    const retainedStatus = (await deadlineStatusField.locator('.el-select__placeholder').textContent())?.trim()
    const previewResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/documents/wizard/task-preview'))
    await this.operatorPage.getByRole('button', { name: '继续预览联动内容' }).click()
    const preview = await (await previewResponse).json() as Json
    const candidate = (preview.items as Json[])[0]
    await expect(this.operatorPage.getByText(candidate.due_date, { exact: true })).toBeVisible()
    await this.operatorPage.getByRole('button', { name: '上一步' }).click()
    await expect(this.operatorPage.getByPlaceholder('请选择官方截止日')).toHaveValue(retainedDate)
    return {
      official_due_date: retainedDate,
      official_due_date_source: retainedSource === '人工核对官方通知' ? 'MANUAL_OFFICIAL_NOTICE' : retainedSource,
      official_due_date_status: retainedStatus === '已确认' ? 'CONFIRMED' : retainedStatus,
      preview_due_date: candidate.due_date,
    }
  }

  async completeFilingAndOa1(caseId: string): Promise<Json> {
    const filingDescriptor = this.evidenceDescriptorsByRole.get('FILING_FINAL_SUBMISSION')!
    const filingCreated = await this.createDocumentViaVisibleUi(caseId, '发明专利请求书及申请文件', '2026-08-02')
    const filingBinding = await this.uploadRole(filingCreated.document.id, filingDescriptor)
    await this.operatorPage.goto(`${baseUrl}/official-workflows/filing-preparation?package_id=${this.filingPackageId}`, { waitUntil: 'domcontentloaded' })
    const refreshResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/official-work-packages/${this.filingPackageId}/filing-preparation/refresh`))
    await this.operatorPage.getByRole('button', { name: '刷新工作包' }).click()
    await refreshResponse
    const externalPayload = { operation_code: 'EXTERNAL_SUBMISSION_RECORDED', occurred_at: filingDescriptor.metadata.effective_at, note: '已于 2026-08-01 完成人工递交' }
    const filingCommand = await this.publicLifecycleApi('RECORD_FILING_EXTERNAL', { package_id: this.filingPackageId }, externalPayload)
    expect(filingCommand.status).toBe(200)
    const filingPackage = await this.publicLifecycleApi('GET_FILING_PACKAGE', { package_id: this.filingPackageId })
    expect(filingPackage.status).toBe(200)
    const filingOverlay = await this.loadLifecycleOverlay(caseId)
    const filingActivity = (filingOverlay.milestones as Json[]).find((item) => item.activity_type === 'FILING_EXTERNAL_SUBMISSION_RECORDED')!
    recordFilingSubmission(this.evidenceRoleMap, filingBinding, filingCommand.body, filingPackage.body, filingActivity)

    const filingReceiptDescriptor = this.evidenceDescriptorsByRole.get('FILING_RECEIPT')!
    const filingReceiptBinding = await this.uploadRole(filingCreated.document.id, filingReceiptDescriptor)
    const filingReceiptPayload = {
      receipt_kind: filingReceiptDescriptor.metadata.receipt_kind,
      receipt_attachment_id: filingReceiptBinding.attachmentId,
      receiving_case_no: 'CNIPA-20260802-001',
      submitter: '陈思远',
      received_at: filingReceiptDescriptor.metadata.received_at,
      received_file_list: '发明专利请求书及申请文件',
      archive_status: 'ARCHIVED',
      note: '已核对电子申请回执及收到文件清单',
    }
    const filingReceipt = await this.publicLifecycleApi('RECORD_PACKAGE_RECEIPT', { package_id: this.filingPackageId }, filingReceiptPayload)
    expect(filingReceipt.status, JSON.stringify(filingReceipt.body)).toBe(201)
    recordReceiptConsumer(this.evidenceRoleMap, filingReceiptBinding, 'filing-receipt', filingReceiptPayload, filingReceipt.body)
    const filingReceiptOverlay = await this.loadLifecycleOverlay(caseId)
    const filingReceiptCenter = filingReceiptOverlay.center_snapshot
    const filingReceiptProjection = [
      filingReceiptCenter.business_stage,
      filingReceiptCenter.official_procedure_stage,
      filingReceiptCenter.legal_status,
      filingReceiptCenter.verification_status,
    ]

    const lifecycleConsumptions: Array<{ kind: 'document-lifecycle'; role: EvidenceRole; consumer: string; payload: Json; result: Json }> = []
    const lifecycleSteps: Array<{ role: EvidenceRole; title: string; template?: string; consumer: string }> = [
      { role: 'ACCEPTANCE_NOTICE', title: '发明专利申请受理通知书', template: 'OFFICIAL_NOTICE_001', consumer: 'acceptance-notice' },
      { role: 'PRELIMINARY_EXAMINATION_SOURCE', title: '发明专利申请初步审查合格通知书', consumer: 'preliminary-examination' },
      { role: 'PUBLICATION_NOTICE', title: '发明专利申请公布通知书', consumer: 'publication-notice' },
      { role: 'SUBSTANTIVE_EXAMINATION_SOURCE', title: '发明专利申请进入实质审查阶段通知书', consumer: 'substantive-examination' },
    ]
    for (const step of lifecycleSteps) {
      const descriptor = this.evidenceDescriptorsByRole.get(step.role)!
      const created = await this.createDocumentViaVisibleUi(caseId, step.title, descriptor.metadata.effective_at.slice(0, 10), step.template)
      const binding = await this.uploadRole(created.document.id, descriptor)
      const payload = { evidence_version_id: binding.evidenceVersionId, effective_at: descriptor.metadata.effective_at, idempotency_key: `${step.role.toLowerCase()}-${caseId}` }
      const result = step.role === 'ACCEPTANCE_NOTICE'
        ? await this.publicLifecycleApi('RECORD_ACCEPTANCE', { document_id: created.document.id }, payload)
        : step.role === 'PRELIMINARY_EXAMINATION_SOURCE'
          ? await this.publicLifecycleApi('RECORD_PRELIMINARY_START', { document_id: created.document.id }, payload)
          : step.role === 'PUBLICATION_NOTICE'
            ? await this.publicLifecycleApi('RECORD_PUBLICATION', { document_id: created.document.id }, payload)
            : await this.publicLifecycleApi('RECORD_SUBSTANTIVE_START', { document_id: created.document.id }, payload)
      expect(result.status).toBe(200)
      recordDocumentLifecycleConsumer(this.evidenceRoleMap, binding, step.consumer, payload, result.body)
      lifecycleConsumptions.push({ kind: 'document-lifecycle', role: step.role, consumer: step.consumer, payload, result: result.body })
      if (step.role === 'PRELIMINARY_EXAMINATION_SOURCE') {
        const passed = await this.publicLifecycleApi('RECORD_PRELIMINARY_PASS', { document_id: created.document.id }, { ...payload, idempotency_key: `preliminary-pass-${caseId}` })
        expect(passed.status).toBe(200)
        recordDocumentLifecycleConsumer(this.evidenceRoleMap, binding, step.consumer, { ...payload, idempotency_key: `preliminary-pass-${caseId}` }, passed.body)
      }
    }

    const oaDescriptor = this.evidenceDescriptorsByRole.get('OA_NOTICE_1')!
    const deadline = {
      official_due_date: oaDescriptor.metadata.official_due_date,
      official_due_date_source: oaDescriptor.metadata.official_due_date_source,
      official_due_date_status: oaDescriptor.metadata.official_due_date_status,
    }
    this.oa1SourceTitle = `第一次审查意见通知书-${this.caseNo}`
    const oaCreated = await this.createDocumentViaVisibleUi(caseId, this.oa1SourceTitle, oaDescriptor.metadata.effective_at.slice(0, 10), 'OFFICIAL_NOTICE_003', deadline)
    const createDeadline = { official_due_date: oaCreated.document.official_due_date, official_due_date_source: oaCreated.document.official_due_date_source, official_due_date_status: oaCreated.document.official_due_date_status }
    const impactDeadline = { official_due_date: oaCreated.impact!.official_due_date, official_due_date_source: oaCreated.impact!.official_due_date_source, official_due_date_status: oaCreated.impact!.official_due_date_status }
    expect(createDeadline).toEqual(deadline)
    expect(impactDeadline).toEqual(deadline)
    const oaBinding = await this.uploadRole(oaCreated.document.id, oaDescriptor)
    const oaPayload = { evidence_version_id: oaBinding.evidenceVersionId, effective_at: oaDescriptor.metadata.effective_at, idempotency_key: `oa1-notice-${caseId}` }
    const oaRecorded = await this.publicLifecycleApi('RECORD_OA_NOTICE', { document_id: oaCreated.document.id }, oaPayload)
    expect(oaRecorded.status).toBe(200)
    recordDocumentLifecycleConsumer(this.evidenceRoleMap, oaBinding, 'oa1-notice', oaPayload, oaRecorded.body)
    const edited = await this.verifyContentEdit(oaCreated.document.id, deadline)
    const wizard = await this.verifyWizardDeadline(this.caseNo, 'OFFICIAL_NOTICE_003', deadline)
    const invalidDeadline = await this.verifyMissingDeadlineNoWrite(caseId)
    const resolved = await this.publicLifecycleApi('RESOLVE_OA', { document_id: oaCreated.document.id })
    expect(resolved.status).toBe(200)
    const firstTaskSnapshot = await this.visibleOaTasks(caseId, oaCreated.document.id)
    expect(firstTaskSnapshot.count).toBe(1)
    const replayed = await this.publicLifecycleApi('RESOLVE_OA', { document_id: oaCreated.document.id })
    expect(replayed.status).toBe(200)
    const replayTaskSnapshot = await this.visibleOaTasks(caseId, oaCreated.document.id)
    expect(replayTaskSnapshot).toEqual(firstTaskSnapshot)
    return {
      filing_package_id: this.filingPackageId,
      filing_command_result: filingCommand.body,
      filing_package_result: filingPackage.body,
      filing_activity_result: filingActivity,
      filing_receipt_projection: filingReceiptProjection,
      lifecycle_consumptions: lifecycleConsumptions,
      source_id: oaCreated.document.id,
      package_id: resolved.body.package.id,
      task_id: (firstTaskSnapshot.ids as string[])[0],
      replayed_package_id: replayed.body.package.id,
      replayed_task_id: (replayTaskSnapshot.ids as string[])[0],
      task_identity_snapshots: { first: firstTaskSnapshot, replay: replayTaskSnapshot },
      deadline,
      deadline_surfaces: { create: createDeadline, read: edited.read_deadline, edit: edited.edit_deadline, impact_preview: impactDeadline, wizard: { official_due_date: wizard.official_due_date, official_due_date_source: wizard.official_due_date_source, official_due_date_status: wizard.official_due_date_status } },
      wizard_preview_due_date: wizard.preview_due_date,
      missing_deadline_no_write: invalidDeadline,
      changed_deadline_no_write: edited.changed_deadline_gate,
    }
  }

  async createOaOut(sourceId: string, packageId: string, sequence: 1 | 2 = 1, sourceTitle = this.oa1SourceTitle): Promise<Json> {
    const created = await this.createDocumentViaVisibleUi(this.caseId, `第${sequence === 1 ? '一' : '二'}次审查意见答复文件-${this.caseNo}`, sequence === 1 ? '2026-08-09' : '2026-10-09', 'OA_OUT', undefined, sourceTitle, 'OUT')
    const linked = await this.publicLifecycleApi('LINK_OA_REPLY', { package_id: packageId }, { reply_document_id: created.document.id })
    expect(linked.status).toBe(200)
    const replayed = await this.publicLifecycleApi('LINK_OA_REPLY', { package_id: packageId }, { reply_document_id: created.document.id })
    expect(replayed.status).toBe(200)
    const packageResult = await this.publicLifecycleApi('GET_OA_PACKAGE', { package_id: packageId })
    expect(packageResult.status).toBe(200)
    const taskSnapshot = await this.visibleOaTasks(created.document.case_id, sourceId)
    const documentsResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/documents') && url.searchParams.get('page_size') === '20'
    })
    await this.operatorPage.goto(`${baseUrl}/documents`, { waitUntil: 'domcontentloaded' })
    const documentPage = await (await documentsResponse).json() as Json
    const links = (documentPage.items as Json[]).filter((item) => item.case_id === created.document.case_id && item.reply_to_id === sourceId)
    if (sequence === 1) {
      this.oa1SourceId = sourceId
      this.oa1ReplyId = created.document.id
    }
    return { linked_source_id: linked.body.package.source_document_id, linked_package_id: linked.body.package.id, link_count: links.length, linked_reply_ids: links.map((item) => item.id).sort(), replayed_reply_id: replayed.body.reply_document.id, task_status: (taskSnapshot.states as string[])[0], task_count: taskSnapshot.count, package_status: packageResult.body.package.status, oa_out_id: created.document.id }
  }
  async rejectInvalidReceipts(caseId: string, packageId: string): Promise<Json> {
    expect(this.oa1ReplyId.length).toBeGreaterThan(0)
    const output = this.oaReplyOutputs.get('1:OA_STATEMENT_PDF')!
    const invalidReceipt = { ...output, official_file_role: 'ELECTRONIC_RECEIPT' as const }
    const mainCaseId = this.caseId
    const mainCaseNo = this.caseNo

    this.caseId = ''
    this.caseNo = `${mainCaseNo}-02`
    await this.operatorPage.goto(`${baseUrl}/cases/new`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '新建案件' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入案号（例如：P2024-001）').fill(this.caseNo)
    await this.operatorPage.getByPlaceholder('请输入案件标题').fill('一种工业机器人末端执行器的力控校准方法')
    const clientField = this.operatorPage.locator('.el-form-item').filter({ hasText: '客户' }).first()
    await clientField.getByRole('combobox').click()
    await this.operatorPage.getByRole('option', { name: this.clientName }).click()
    await this.operatorPage.locator('.el-collapse-item__header').filter({ hasText: '申请人信息' }).click()
    await this.operatorPage.getByRole('button', { name: '新增申请人', exact: true }).click()
    const applicantField = this.operatorPage.locator('.el-form-item').filter({ hasText: '从客户主数据回填' }).first()
    await applicantField.getByRole('combobox').click()
    await this.operatorPage.getByRole('option', { name: this.clientName }).last().click()
    await expect(this.operatorPage.getByPlaceholder('申请人中文名称')).toHaveValue(this.clientName)
    await this.operatorPage.getByText('控制标记', { exact: true }).click()
    const reductionField = this.operatorPage.locator('.el-form-item').filter({ hasText: '费用减缓比例' }).first()
    await reductionField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option', { name: '不减免（0）' }).click()
    const auxiliaryResponse = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/cases'))
    await this.operatorPage.getByRole('button', { name: '创建案件' }).click()
    const auxiliary = await (await auxiliaryResponse).json() as Json
    expect(auxiliary.client_id).toBe(this.clientId)
    expect(auxiliary.status).toBe('NOT_FILED')
    this.caseId = auxiliary.id
    const crossDocument = await this.createDocumentViaVisibleUi(auxiliary.id, `发明专利申请递交回执-${auxiliary.case_no}`, '2026-08-10')
    const crossAttachment = await this.uploadRole(crossDocument.document.id, invalidReceipt)
    this.caseId = mainCaseId
    this.caseNo = mainCaseNo

    const wrongSourceDocument = await this.createDocumentViaVisibleUi(caseId, `第一次审查意见答复递交回执（补充件）-${mainCaseNo}`, '2026-08-10')
    const wrongSourceAttachment = await this.uploadRole(wrongSourceDocument.document.id, invalidReceipt)
    const crossPackageBefore = await this.publicLifecycleApi('GET_OA_PACKAGE', { package_id: packageId })
    expect(crossPackageBefore.status).toBe(200)
    expect(crossPackageBefore.body.package.id).toBe(packageId)
    const crossCaseBefore = {
      case_snapshot: await this.visibleCaseSnapshot(caseId),
      target_package: crossPackageBefore.body,
    }

    await this.operatorPage.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${packageId}`, { waitUntil: 'domcontentloaded' })
    await this.operatorPage.getByPlaceholder('引用已上传附件ID').fill(crossAttachment.id)
    await this.operatorPage.getByPlaceholder('请输入官方接收案件编号').fill('CNIPA-20260810-001')
    await this.operatorPage.getByPlaceholder('请输入提交人').fill('陈思远')
    await this.operatorPage.getByPlaceholder('请选择接收时间').fill('2026-08-10T10:00:00')
    await this.operatorPage.getByPlaceholder('逐行记录官方回执中的收到文件清单').fill('发明专利请求书及申请文件')
    const crossResponse = this.operatorPage.waitForResponse((item) => item.status() >= 400 && item.url().includes(`/official-work-packages/${packageId}/receipts`))
    await this.operatorPage.getByRole('button', { name: '记录回执元数据' }).click()
    const crossRejected = await crossResponse
    const crossError = await crossRejected.json() as Json
    expect(crossError.error.code).toBe('OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH')
    const crossPackageAfter = await this.publicLifecycleApi('GET_OA_PACKAGE', { package_id: packageId })
    expect(crossPackageAfter.status).toBe(200)
    const crossCaseAfter = {
      case_snapshot: await this.visibleCaseSnapshot(caseId),
      target_package: crossPackageAfter.body,
    }
    expect(crossCaseAfter).toEqual(crossCaseBefore)

    const wrongSourcePackageBefore = await this.publicLifecycleApi('GET_OA_PACKAGE', { package_id: packageId })
    expect(wrongSourcePackageBefore.status).toBe(200)
    expect(wrongSourcePackageBefore.body.package.id).toBe(packageId)
    const wrongSourceBefore = {
      case_snapshot: await this.visibleCaseSnapshot(caseId),
      target_package: wrongSourcePackageBefore.body,
    }
    await this.operatorPage.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${packageId}`, { waitUntil: 'domcontentloaded' })
    await this.operatorPage.getByPlaceholder('引用已上传附件ID').fill(wrongSourceAttachment.id)
    await this.operatorPage.getByPlaceholder('请输入官方接收案件编号').fill('CNIPA-20260810-002')
    await this.operatorPage.getByPlaceholder('请输入提交人').fill('陈思远')
    await this.operatorPage.getByPlaceholder('请选择接收时间').fill('2026-08-10T10:00:00')
    await this.operatorPage.getByPlaceholder('逐行记录官方回执中的收到文件清单').fill('第一次审查意见答复_意见陈述书\n第一次审查意见答复_修改后权利要求书')
    const wrongSourceResponse = this.operatorPage.waitForResponse((item) => item.status() >= 400 && item.url().includes(`/official-work-packages/${packageId}/receipts`))
    await this.operatorPage.getByRole('button', { name: '记录回执元数据' }).click()
    const wrongSourceRejected = await wrongSourceResponse
    const wrongSourceError = await wrongSourceRejected.json() as Json
    expect(wrongSourceError.error.code).toBe('OA_RECEIPT_ATTACHMENT_SOURCE_INVALID')
    const wrongSourcePackageAfter = await this.publicLifecycleApi('GET_OA_PACKAGE', { package_id: packageId })
    expect(wrongSourcePackageAfter.status).toBe(200)
    const wrongSourceAfter = {
      case_snapshot: await this.visibleCaseSnapshot(caseId),
      target_package: wrongSourcePackageAfter.body,
    }
    expect(wrongSourceAfter).toEqual(wrongSourceBefore)
    return {
      cross_case_status: crossRejected.status(),
      same_case_wrong_source_status: wrongSourceRejected.status(),
      cross_case_before_snapshot: crossCaseBefore,
      cross_case_after_snapshot: crossCaseAfter,
      wrong_source_before_snapshot: wrongSourceBefore,
      wrong_source_after_snapshot: wrongSourceAfter,
    }
  }

  async archiveOa1(
    packageId: string,
    sequence: 1 | 2 = 1,
    sourceId = this.oa1SourceId,
    replyId = this.oa1ReplyId,
  ): Promise<Json> {
    const outputRoles = ['OA_STATEMENT_WORD', 'OA_STATEMENT_PDF', 'OA_MODIFIED_CLAIMS'] as const
    const uploadedOutputs: Json[] = []
    for (const role of outputRoles) {
      const descriptor = this.oaReplyOutputs.get(`${sequence}:${role}`)!
      expect(descriptor.oa_sequence).toBe(sequence)
      uploadedOutputs.push(await this.uploadRole(replyId, descriptor))
    }

    await this.operatorPage.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${packageId}`, { waitUntil: 'domcontentloaded' })
    const refreshResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && item.url().endsWith(`/official-work-packages/${packageId}/oa-reply/refresh`))
    await this.operatorPage.getByRole('button', { name: '刷新工作包' }).click()
    const refreshed = await (await refreshResponse).json() as Json
    expect((refreshed.oa_file_roles as Json[]).filter((item) => item.present === true).length).toBeGreaterThanOrEqual(3)

    const checklistLabels = [
      '确认陈述意见文本',
      '确认PDF保真附件',
      '确认修改文件',
      '确认实验数据标记',
      '确认官方页面预览',
      '确认签名与提交',
    ]
    for (const label of checklistLabels) {
      const checklistResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && item.url().includes(`/official-work-packages/${packageId}/oa-reply/checklist/`))
      await this.operatorPage.getByRole('button', { name: label, exact: true }).click()
      const checklist = await (await checklistResponse).json() as Json
      expect(checklist.checklist_item.status).toBe('DONE')
    }

    const receiptRole: EvidenceRole = sequence === 1 ? 'OA_RECEIPT_1' : 'OA_RECEIPT_2'
    const receiptDescriptor = this.evidenceDescriptorsByRole.get(receiptRole)!
    const receiptBinding = await this.uploadRole(replyId, receiptDescriptor)
    await this.operatorPage.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${packageId}`, { waitUntil: 'domcontentloaded' })
    await this.operatorPage.getByPlaceholder('引用已上传附件ID').fill(receiptBinding.attachmentId)
    await this.operatorPage.getByPlaceholder('请输入官方接收案件编号').fill(sequence === 1 ? 'CNIPA-20260808-001' : 'CNIPA-20260810-003')
    await this.operatorPage.getByPlaceholder('请输入提交人').fill('陈思远')
    await this.operatorPage.getByPlaceholder('请选择接收时间').fill(receiptDescriptor.metadata.received_at.slice(0, 19))
    await this.operatorPage.getByPlaceholder('逐行记录官方回执中的收到文件清单').fill(sequence === 1
      ? '第一次审查意见答复_意见陈述书\n第一次审查意见答复_修改后权利要求书'
      : '第二次审查意见答复_意见陈述书\n第二次审查意见答复_修改后权利要求书')
    const receiptResponse = this.operatorPage.waitForResponse((item) => item.status() === 201 && item.url().endsWith(`/official-work-packages/${packageId}/receipts`))
    await this.operatorPage.getByRole('button', { name: '记录回执元数据' }).click()
    const receipt = await (await receiptResponse).json() as Json
    const receiptPayload = {
      receipt_attachment_id: receiptBinding.attachmentId,
    }
    recordReceiptConsumer(this.evidenceRoleMap, receiptBinding, sequence === 1 ? 'oa1-receipt' : 'oa2-receipt', receiptPayload, receipt)

    const archiveResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && item.url().endsWith(`/official-work-packages/${packageId}/archive`))
    await this.operatorPage.getByRole('button', { name: '提交归档检查' }).click()
    const archived = await (await archiveResponse).json() as Json
    expect(archived.package.status).toBe('ARCHIVED')
    const tasks = await this.visibleOaTasks(this.caseId, sourceId)
    expect(tasks.count).toBe(1)
    expect(tasks.states).toEqual(['DONE'])
    const caseDetailPromise = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/cases/${this.caseId}`)).then((item) => item.json() as Promise<Json>)
    const overlay = await this.loadLifecycleOverlay(this.caseId)
    const caseDetail = await caseDetailPromise
    const center = overlay.center_snapshot
    const projection = [center.business_stage, center.official_procedure_stage, center.legal_status, center.verification_status]
    const history = {
      source_id: sourceId,
      reply_id: replyId,
      package_id: packageId,
      receipt_id: receipt.id,
      task_ids: tasks.ids,
      task_states: tasks.states,
      package_status: archived.package.status,
    }
    if (sequence === 1) {
      this.oa1ReceiptId = receipt.id
      this.oa1History = history
    }
    return { package_status: archived.package.status, closed_task_ids: tasks.ids, projection, legacy_display: caseDetail.status, receipt_id: receipt.id, uploaded_outputs: uploadedOutputs, history }
  }

  async completeOa2(caseId: string): Promise<Json> {
    const oa1HistoryBefore = JSON.parse(JSON.stringify(this.oa1History)) as Json
    const noticeDescriptor = this.evidenceDescriptorsByRole.get('OA_NOTICE_2')!
    const deadline = {
      official_due_date: noticeDescriptor.metadata.official_due_date,
      official_due_date_source: noticeDescriptor.metadata.official_due_date_source,
      official_due_date_status: noticeDescriptor.metadata.official_due_date_status,
    }
    const sourceTitle = `第二次审查意见通知书-${this.caseNo}`
    const created = await this.createDocumentViaVisibleUi(caseId, sourceTitle, noticeDescriptor.metadata.effective_at.slice(0, 10), 'OFFICIAL_NOTICE_005', deadline)
    const createDeadline = { official_due_date: created.document.official_due_date, official_due_date_source: created.document.official_due_date_source, official_due_date_status: created.document.official_due_date_status }
    const impactDeadline = { official_due_date: created.impact!.official_due_date, official_due_date_source: created.impact!.official_due_date_source, official_due_date_status: created.impact!.official_due_date_status }
    const reuseBefore = await this.visibleCaseSnapshot(caseId)
    const oa1Binding = this.evidenceRoleMap.get('OA_NOTICE_1')!
    const reusedSequence = await this.publicLifecycleApi('RECORD_OA_NOTICE', { document_id: created.document.id }, {
      evidence_version_id: oa1Binding.evidenceVersionId,
      effective_at: noticeDescriptor.metadata.effective_at,
      idempotency_key: `oa2-sequence1-reuse-${caseId}`,
    })
    expect(reusedSequence.status).toBeGreaterThanOrEqual(400)
    const reuseAfter = await this.visibleCaseSnapshot(caseId)
    expect(reuseAfter).toEqual(reuseBefore)

    const noticeBinding = await this.uploadRole(created.document.id, noticeDescriptor)
    const noticePayload = { evidence_version_id: noticeBinding.evidenceVersionId, effective_at: noticeDescriptor.metadata.effective_at, idempotency_key: `oa2-notice-${caseId}` }
    const recorded = await this.publicLifecycleApi('RECORD_OA_NOTICE', { document_id: created.document.id }, noticePayload)
    expect(recorded.status).toBe(200)
    expect(recorded.body.oa_sequence).toBe(2)
    recordDocumentLifecycleConsumer(this.evidenceRoleMap, noticeBinding, 'oa2-notice', noticePayload, recorded.body)
    const edited = await this.verifyContentEdit(created.document.id, deadline)
    const wizard = await this.verifyWizardDeadline(this.caseNo, 'OFFICIAL_NOTICE_005', deadline)
    const incompleteDeadline = await this.verifyMissingDeadlineNoWrite(caseId, 'OFFICIAL_NOTICE_005', '第二次')
    const resolved = await this.publicLifecycleApi('RESOLVE_OA', { document_id: created.document.id })
    expect(resolved.status).toBe(200)
    const tasks = await this.visibleOaTasks(caseId, created.document.id)
    expect(tasks.count).toBe(1)
    const taskId = (tasks.ids as string[])[0]
    const oaOut = await this.createOaOut(created.document.id, resolved.body.package.id, 2, sourceTitle)
    const archived = await this.archiveOa1(resolved.body.package.id, 2, created.document.id, oaOut.oa_out_id)

    const oa1Package = await this.publicLifecycleApi('GET_OA_PACKAGE', { package_id: this.oa1History.package_id })
    expect(oa1Package.status).toBe(200)
    const oa1Tasks = await this.visibleOaTasks(caseId, this.oa1SourceId)
    const oa1HistoryAfter = {
      source_id: this.oa1SourceId,
      reply_id: this.oa1ReplyId,
      package_id: this.oa1History.package_id,
      receipt_id: this.oa1ReceiptId,
      task_ids: oa1Tasks.ids,
      task_states: oa1Tasks.states,
      package_status: oa1Package.body.package.status,
    }
    return {
      source_id: created.document.id,
      package_id: resolved.body.package.id,
      task_id: taskId,
      oa_out_id: oaOut.oa_out_id,
      oa1_oa_out_id: this.oa1ReplyId,
      receipt_id: archived.receipt_id,
      oa1_receipt_id: this.oa1ReceiptId,
      oa_sequence: recorded.body.oa_sequence,
      notice_role: 'OA_NOTICE_2',
      receipt_role: 'OA_RECEIPT_2',
      deadline,
      deadline_surfaces: {
        create: createDeadline,
        read: edited.read_deadline,
        edit: edited.edit_deadline,
        impact_preview: impactDeadline,
        wizard: { official_due_date: wizard.official_due_date, official_due_date_source: wizard.official_due_date_source, official_due_date_status: wizard.official_due_date_status },
      },
      sequence1_reuse_no_write: reusedSequence.status >= 400 && JSON.stringify(reuseBefore) === JSON.stringify(reuseAfter),
      incomplete_deadline_no_write: incompleteDeadline.status >= 400 && JSON.stringify(incompleteDeadline.before) === JSON.stringify(incompleteDeadline.after),
      changed_deadline_no_write: edited.changed_deadline_gate.before && JSON.stringify(edited.changed_deadline_gate.before) === JSON.stringify(edited.changed_deadline_gate.after),
      closed_task_ids: archived.closed_task_ids,
      oa1_history_before: oa1HistoryBefore,
      oa1_history_after: oa1HistoryAfter,
      projection: archived.projection,
      legacy_display: archived.legacy_display,
    }
  }
  async createGrantOriginal(caseId: string): Promise<Json> {
    const descriptor = this.evidenceDescriptorsByRole.get('GRANT_NOTICE_ORIGINAL')!
    expect(descriptor.metadata.source_template_code).toBe('DEMO_GRANT_NOTICE_1')
    expect(descriptor.metadata.supersedes_role).toBe(null)
    const sourceDocumentDate = (descriptor.metadata.effective_at as string).slice(0, 10)
    const deadline = {
      official_due_date: descriptor.metadata.official_due_date as string,
      official_due_date_source: descriptor.metadata.official_due_date_source as string,
      official_due_date_status: descriptor.metadata.official_due_date_status as string,
    }
    expect(deadline.official_due_date_source).toBe('IMPORTED_OFFICIAL_NOTICE')
    expect(deadline.official_due_date_status).toBe('CONFIRMED')
    const created = await this.createDocumentViaVisibleUi(
      caseId,
      `办理登记手续通知书-${this.caseNo}`,
      sourceDocumentDate,
      'OFFICIAL_NOTICE_009',
      deadline,
    )
    this.grantOriginalDocumentId = created.document.id
    this.grantTemplateId = created.document.doc_template_id
    const createdSnapshot = await this.visibleCaseSnapshot(caseId)
    const tasks = createdSnapshot.grant_tasks as Json[]
    const sourceTasks = tasks.filter((item) => item.source_document_id === created.document.id)
    expect(sourceTasks).toHaveLength(1)
    const taskId = sourceTasks[0].task_id as string
    const binding = await this.uploadRole(created.document.id, descriptor) as EvidenceBinding
    const payload = {
      reviewed_evidence_version_id: binding.evidenceVersionId,
      expected_content_hash: binding.contentHash,
      recorded_at: descriptor.metadata.effective_at,
      idempotency_key: `integrated-grant-original-${taskId.slice(0, 8)}`,
    }
    const dispatched = await this.publicLifecycleApi('GRANT_NOTICE', { grant_fee_task_id: taskId }, payload)
    expect(dispatched.status, JSON.stringify(dispatched.body)).toBe(200)
    recordGrantConsumer(this.evidenceRoleMap, binding, 'grant-original-dispatch', payload, dispatched.body)
    const overlay = await this.loadLifecycleOverlay(caseId)
    const center = overlay.center_snapshot
    const afterSnapshot = await this.visibleCaseSnapshot(caseId)
    const afterTasks = afterSnapshot.grant_tasks as Json[]
    const actionable = afterTasks.filter((item) => item.lineage_status === 'CONFIRMED')
    return {
      document_id: created.document.id,
      task_id: taskId,
      source_document_id: sourceTasks[0].source_document_id,
      source_document_date: created.document.doc_date,
      expected_source_document_date: sourceDocumentDate,
      source_deadline: {
        official_due_date: created.document.official_due_date,
        official_due_date_source: created.document.official_due_date_source,
        official_due_date_status: created.document.official_due_date_status,
      },
      expected_deadline: deadline,
      source_evidence_version_id: binding.evidenceVersionId,
      source_content_hash: binding.contentHash,
      original_activity_id: dispatched.body.activity_id,
      actionable_task_ids: actionable.map((item) => item.task_id),
      projection: [center.business_stage, center.official_procedure_stage, center.legal_status, center.verification_status],
      official_fee_carriers: afterSnapshot.official_fee_carriers,
      payload,
      result: dispatched.body,
    }
  }

  async replaceGrant(taskId: string): Promise<Json> {
    const descriptor = this.evidenceDescriptorsByRole.get('GRANT_NOTICE_REPLACEMENT')!
    expect(descriptor.metadata.source_template_code).toBe('DEMO_GRANT_NOTICE_2')
    expect(descriptor.metadata.supersedes_role).toBe('GRANT_NOTICE_ORIGINAL')
    const sourceDocumentDate = (descriptor.metadata.effective_at as string).slice(0, 10)
    const replacementPayload = {
      idempotency_key: `integrated-grant-replace-${taskId.slice(0, 8)}`,
      reason: '更新来源替换原授权登记通知',
      document: {
        doc_template_id: this.grantTemplateId,
        doc_date: sourceDocumentDate,
        title: `办理登记手续更正通知书-${this.caseNo}`,
        ref_no: `BDJ-${this.caseNo}-02`,
        official_due_date: descriptor.metadata.official_due_date,
        official_due_date_source: descriptor.metadata.official_due_date_source,
        official_due_date_status: descriptor.metadata.official_due_date_status,
        description: '依据更正通知更新办理登记手续期限',
      },
    }
    const replaced = await this.publicLifecycleApi('GRANT_REPLACEMENT', { task_id: taskId }, replacementPayload)
    expect(replaced.status).toBe(200)
    expect(replaced.body.superseded_task_id).toBe(taskId)
    const replacementTaskId = replaced.body.replacement_task.task_id as string
    const replacementDocumentId = replaced.body.document.id as string
    const binding = await this.uploadRole(replacementDocumentId, descriptor) as EvidenceBinding
    const lifecyclePayload = {
      reviewed_evidence_version_id: binding.evidenceVersionId,
      expected_content_hash: binding.contentHash,
      recorded_at: descriptor.metadata.effective_at,
      idempotency_key: `integrated-grant-replacement-${replacementTaskId.slice(0, 8)}`,
    }
    const dispatched = await this.publicLifecycleApi('GRANT_NOTICE', { grant_fee_task_id: replacementTaskId }, lifecyclePayload)
    expect(dispatched.status, JSON.stringify(dispatched.body)).toBe(200)
    recordGrantConsumer(this.evidenceRoleMap, binding, 'grant-replacement-dispatch', lifecyclePayload, dispatched.body)
    const originalState = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: taskId })
    const replacementState = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: replacementTaskId })
    expect(originalState.status).toBe(200)
    expect(replacementState.status).toBe(200)
    expect(originalState.body.lineage_status).toBe('SUPERSEDED')
    expect(replacementState.body.lineage_status).toBe('CONFIRMED')
    const replacementSnapshot = await this.visibleCaseSnapshot(this.caseId)
    const tasks = replacementSnapshot.grant_tasks as Json[]
    const actionable = tasks.filter((item) => item.lineage_status === 'CONFIRMED')
    const overlay = await this.loadLifecycleOverlay(this.caseId)
    const center = overlay.center_snapshot
    return {
      document_id: replacementDocumentId,
      replacement_document_id: replacementDocumentId,
      original_document_id: this.grantOriginalDocumentId,
      replacement_task_id: replacementTaskId,
      superseded_task_id: replaced.body.superseded_task_id,
      replacement_predecessor_task_id: replaced.body.superseded_task_id,
      original_source_evidence_version_id: this.evidenceRoleMap.get('GRANT_NOTICE_ORIGINAL')!.evidenceVersionId,
      replacement_source_evidence_version_id: binding.evidenceVersionId,
      replacement_source_content_hash: binding.contentHash,
      replacement_metadata: binding.metadata,
      original_activity_id: originalState.body.lifecycle_activity_id,
      replacement_activity_id: replacementState.body.lifecycle_activity_id,
      supersedes_activity_id: replacementState.body.supersedes_activity_id,
      actionable_task_ids: actionable.map((item) => item.task_id),
      original_hash: this.evidenceRoleMap.get('GRANT_NOTICE_ORIGINAL')!.contentHash,
      replacement_hash: binding.contentHash,
      projection: [center.business_stage, center.official_procedure_stage, center.legal_status, center.verification_status],
      payload: lifecyclePayload,
      result: dispatched.body,
    }
  }

  async exerciseGrantGatesAndPay(oldTaskId: string, newTaskId: string): Promise<Json> {
    const blockedObservations: Json[] = []
    {
      const beforeOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const beforeCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const beforeVisible = await this.visibleCaseSnapshot(this.caseId)
      const beforeSnapshot = { old_task: beforeOld.body, current_task: beforeCurrent.body, official_fee_carriers: beforeVisible.official_fee_carriers }
      const response = await this.publicLifecycleApi('GRANT_GENERATE_DRAFT', { task_id: oldTaskId })
      expect(response.status).toBe(409)
      const afterOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const afterCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const afterVisible = await this.visibleCaseSnapshot(this.caseId)
      const afterSnapshot = { old_task: afterOld.body, current_task: afterCurrent.body, official_fee_carriers: afterVisible.official_fee_carriers }
      expect(afterSnapshot).toEqual(beforeSnapshot)
      blockedObservations.push({ operation: 'generate-draft', status: response.status, before_snapshot: beforeSnapshot, after_snapshot: afterSnapshot })
    }
    {
      const beforeOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const beforeCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const beforeVisible = await this.visibleCaseSnapshot(this.caseId)
      const beforeSnapshot = { old_task: beforeOld.body, current_task: beforeCurrent.body, official_fee_carriers: beforeVisible.official_fee_carriers }
      const response = await this.publicLifecycleApi('GRANT_BATCH_INSTRUCTION', {}, { task_ids: [oldTaskId], action: 'record_pay_instruction' })
      expect(response.status).toBe(409)
      const afterOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const afterCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const afterVisible = await this.visibleCaseSnapshot(this.caseId)
      const afterSnapshot = { old_task: afterOld.body, current_task: afterCurrent.body, official_fee_carriers: afterVisible.official_fee_carriers }
      expect(afterSnapshot).toEqual(beforeSnapshot)
      blockedObservations.push({ operation: 'batch-instruction', status: response.status, before_snapshot: beforeSnapshot, after_snapshot: afterSnapshot })
    }
    {
      const beforeOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const beforeCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const beforeVisible = await this.visibleCaseSnapshot(this.caseId)
      const beforeSnapshot = { old_task: beforeOld.body, current_task: beforeCurrent.body, official_fee_carriers: beforeVisible.official_fee_carriers }
      const response = await this.publicLifecycleApi('GRANT_GENERATE_NOTICES', {}, { task_ids: [oldTaskId] })
      expect(response.status).toBe(409)
      const afterOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const afterCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const afterVisible = await this.visibleCaseSnapshot(this.caseId)
      const afterSnapshot = { old_task: afterOld.body, current_task: afterCurrent.body, official_fee_carriers: afterVisible.official_fee_carriers }
      expect(afterSnapshot).toEqual(beforeSnapshot)
      blockedObservations.push({ operation: 'generate-notices', status: response.status, before_snapshot: beforeSnapshot, after_snapshot: afterSnapshot })
    }
    {
      const beforeOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const beforeCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const beforeVisible = await this.visibleCaseSnapshot(this.caseId)
      const beforeSnapshot = { old_task: beforeOld.body, current_task: beforeCurrent.body, official_fee_carriers: beforeVisible.official_fee_carriers }
      const response = await this.publicLifecycleApi('GRANT_TASK_STATE', { task_id: oldTaskId }, { action: 'mark_waiting_client' })
      expect(response.status).toBe(409)
      const afterOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
      const afterCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
      const afterVisible = await this.visibleCaseSnapshot(this.caseId)
      const afterSnapshot = { old_task: afterOld.body, current_task: afterCurrent.body, official_fee_carriers: afterVisible.official_fee_carriers }
      expect(afterSnapshot).toEqual(beforeSnapshot)
      blockedObservations.push({ operation: 'mark_waiting_client', status: response.status, before_snapshot: beforeSnapshot, after_snapshot: afterSnapshot })
    }

    const waiting = await this.publicLifecycleApi('GRANT_TASK_STATE', { task_id: newTaskId }, { action: 'mark_waiting_client' })
    expect(waiting.status).toBe(200)
    expect(waiting.body.state).toBe('WAITING_CLIENT')
    const paid = await this.publicLifecycleApi('GRANT_BATCH_INSTRUCTION', {}, { task_ids: [newTaskId], action: 'record_pay_instruction' })
    expect(paid.status).toBe(200)
    expect(paid.body.updated_task_ids).toEqual([newTaskId])
    const paidState = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
    expect(paidState.status).toBe(200)
    expect(paidState.body.client_instruction).toBe('PAY')

    const missingBeforeOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
    const missingBeforeCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
    const missingBeforeVisible = await this.visibleCaseSnapshot(this.caseId)
    const missingAuthorityBefore = { old_task: missingBeforeOld.body, current_task: missingBeforeCurrent.body, official_fee_carriers: missingBeforeVisible.official_fee_carriers }
    const missingAuthority = await this.publicLifecycleApi('GRANT_GENERATE_DRAFT', { task_id: newTaskId })
    expect(missingAuthority.status).toBe(409)
    expect(missingAuthority.body.error.code).toBe('DEMO_OFFICIAL_FEE_CONFIG_REQUIRED')
    const missingAfterOld = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: oldTaskId })
    const missingAfterCurrent = await this.publicLifecycleApi('GET_GRANT_TASK', { task_id: newTaskId })
    const missingAfterVisible = await this.visibleCaseSnapshot(this.caseId)
    const missingAuthorityAfter = { old_task: missingAfterOld.body, current_task: missingAfterCurrent.body, official_fee_carriers: missingAfterVisible.official_fee_carriers }
    expect(missingAuthorityAfter).toEqual(missingAuthorityBefore)
    const tasks = missingAfterVisible.grant_tasks as Json[]
    const currentPayRows = tasks.filter((item) => item.task_id === newTaskId && item.client_instruction === 'PAY')
    return {
      blocked_mutations: ['generate-draft', 'batch-instruction', 'generate-notices', 'mark_waiting_client'],
      blocked_statuses: blockedObservations.map((item) => item.status),
      blocked_observations: blockedObservations,
      current_instruction: paidState.body.client_instruction,
      current_instruction_count: currentPayRows.length,
      missing_authority_status: missingAuthority.status,
      missing_authority_code: missingAuthority.body.error.code,
      missing_authority_before: missingAuthorityBefore,
      missing_authority_after: missingAuthorityAfter,
      official_fee_carriers: missingAuthorityAfter.official_fee_carriers,
    }
  }
  async createServiceDraft(caseId: string): Promise<Json> {
    expect(caseId).toBe(this.caseId)
    await this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByText('演示输入已校验', { exact: false })).toBeVisible()
    await this.operatorPage.getByTestId('demo-case-no').fill(this.caseNo)
    await this.operatorPage.getByRole('button', { name: '加载案件' }).click()
    await expect(this.operatorPage.getByText(`已选择 ${this.caseNo}`, { exact: false })).toBeVisible()

    const obligationCreated = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/fees/demo-service-obligations'))
    await this.operatorPage.getByTestId('create-obligation').click()
    const created = await (await obligationCreated).json() as Json
    const primaryCreatedItem = (created.items as Json[])[0]
    const obligationReplayed = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/fees/demo-service-obligations'))
    await this.operatorPage.getByTestId('create-obligation').click()
    const replayed = await (await obligationReplayed).json() as Json
    expect(replayed.obligation.id).toBe(created.obligation.id)
    expect(replayed.reused).toBe(true)

    await this.operatorPage.goto(`${baseUrl}/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    await this.operatorPage.getByRole('tab', { name: '费用', exact: true }).click()
    const obligationCard = this.operatorPage.getByTestId('real-fee-obligations').locator('.obligation-card').filter({ hasText: created.obligation.id })
    await expect(obligationCard).toHaveCount(1)
    const instructionResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/fees/obligations/${created.obligation.id}/instruction`))
    await obligationCard.getByRole('button', { name: '记录支付指示', exact: true }).click()
    const instruction = await (await instructionResponse).json() as Json
    expect(instruction.obligation_id).toBe(created.obligation.id)
    expect(instruction.client_instruction_status).toBe('PAY')
    const draftLink = obligationCard.getByRole('link', { name: '创建关联费用草稿', exact: true })
    expect(await draftLink.getAttribute('href')).toBe(`/fees/drafts/new?obligation_id=${created.obligation.id}`)
    await obligationCard.getByRole('link', { name: '创建关联费用草稿', exact: true }).click()
    const linkedObligation = this.operatorPage.getByTestId('linked-fee-obligation')
    await expect(linkedObligation.getByText(`义务编号：${created.obligation.id}`, { exact: true })).toBeVisible()
    await expect(linkedObligation.getByText('客户指示：PAY', { exact: true })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入案件编号').fill(caseId)
    await this.operatorPage.getByPlaceholder('可选客户编号').fill(this.clientId)
    const draftCreated = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/fees/drafts'))
    await this.operatorPage.getByRole('button', { name: '创建草稿', exact: true }).click()
    const openDraft = await (await draftCreated).json() as Json
    await expect(this.operatorPage).toHaveURL(`${baseUrl}/fees/drafts/${openDraft.id}`)
    await this.operatorPage.getByRole('button', { name: /锁定$/ }).click()
    const lockDialog = this.operatorPage.getByRole('dialog', { name: '锁定草稿' })
    await expect(lockDialog).toBeVisible()
    const lockResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/fees/drafts/${openDraft.id}/lock`))
    const lockedDraftResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/fees/drafts/${openDraft.id}`))
    await lockDialog.getByRole('button', { name: '锁定', exact: true }).click()
    const lockedAck = await (await lockResponse).json() as Json
    expect(lockedAck.status).toBe('ok')
    const lockedDraft = await (await lockedDraftResponse).json() as Json
    expect(lockedDraft.id).toBe(openDraft.id)
    expect(lockedDraft.status).toBe('LOCKED')
    await expect(this.operatorPage.getByText('🔒 已锁定', { exact: true })).toBeVisible()
    this.draftId = lockedDraft.id
    this.bundleAmount = created.total_amount

    const overlayResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/cases/${caseId}/lifecycle-overlay`))
    const draftListResponse = this.operatorPage.waitForResponse((item) => {
      const url = new URL(item.url())
      return item.status() === 200 && url.pathname.endsWith('/api/v1/fees/drafts') && url.searchParams.get('case_id') === caseId
    })
    await this.operatorPage.goto(`${baseUrl}/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    const overlay = await (await overlayResponse).json() as Json
    const draftPage = await (await draftListResponse).json() as Json
    const serviceObligations = (overlay.milestones as Json[]).flatMap((milestone) => (milestone.fee_obligations || []) as Json[])
      .filter((item) => item.fee_domain === 'SERVICE' && item.obligation_id === created.obligation.id)
    const serviceObligationIds = new Set(serviceObligations.map((item) => item.obligation_id))
    expect(serviceObligations.length).toBeGreaterThan(0)
    expect([...serviceObligationIds]).toEqual([created.obligation.id])
    const serviceDrafts = (draftPage.items as Json[]).filter((item) => item.id === lockedDraft.id && item.status === 'LOCKED')
    const visible = await this.visibleCaseSnapshot(caseId)
    await this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByText(lockedDraft.id, { exact: false })).toBeVisible()
    return {
      case_id: caseId,
      draft_id: lockedDraft.id,
      provenance: {
        bundle_id: created.bundle_id,
        bundle_version: created.bundle_version,
        manifest_sha256: created.manifest_sha256,
        template_code: created.template_code,
        template_sha256: created.template_sha256,
        rate_item_code: primaryCreatedItem.item_code,
        rate_source_ref: primaryCreatedItem.source_ref,
        rate_source_version: primaryCreatedItem.source_version,
        rate_source_sha256: primaryCreatedItem.source_sha256,
      },
      disclaimer: primaryCreatedItem.disclaimer_zh_cn,
      obligation_count: serviceObligationIds.size,
      draft_count: serviceDrafts.length,
      draft_status: lockedDraft.status,
      service_amount: lockedDraft.total_service,
      bundle_amount: created.total_amount,
      official_fee_display: '未配置',
      official_fee_in_total: lockedDraft.total_gov !== '0.00',
      official_fee_carriers: visible.official_fee_carriers,
    }
  }

  async createBill(draftId: string): Promise<Json> {
    expect(draftId).toBe(this.draftId)
    await this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByText(draftId, { exact: false })).toBeVisible()
    const createdResponse = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/bills/demo-from-draft'))
    await this.operatorPage.getByTestId('create-bill').click()
    const created = await (await createdResponse).json() as Json
    const replayedResponse = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/bills/demo-from-draft'))
    await this.operatorPage.getByTestId('create-bill').click()
    const replayed = await (await replayedResponse).json() as Json
    expect(replayed.reused).toBe(true)
    expect(replayed.bill.id).toBe(created.bill.id)
    this.billId = created.bill.id

    const listResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/bills'))
    await this.operatorPage.goto(`${baseUrl}/billing/bills`, { waitUntil: 'domcontentloaded' })
    const billPage = await (await listResponse).json() as Json
    const billMatches = (billPage.items as Json[]).filter((item) => item.id === created.bill.id)
    const detailResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/bills/${created.bill.id}`))
    await this.operatorPage.goto(`${baseUrl}/billing/bills/${created.bill.id}`, { waitUntil: 'domcontentloaded' })
    const detail = await (await detailResponse).json() as Json
    expect(expectedScenario.billNoPrefix).toBe('AR-CYZN')
    expect(detail.bill_no).toMatch(/^AR-CYZN-/)
    await expect(this.operatorPage.getByRole('heading', { name: `账单号 ${detail.bill_no}`, exact: true })).toBeVisible()
    return {
      bill_id: detail.id,
      bill_no: detail.bill_no,
      replayed_bill_id: replayed.bill.id,
      bill_count: billMatches.length,
      source_draft_ids: detail.source_draft_ids,
      consumed_draft_ids: detail.source_draft_ids,
      bill_item_ids: (detail.items as Json[]).map((item) => item.id),
      bill_item_draft_ids: (detail.items as Json[]).map((item) => item.draft_id),
      status: detail.status,
      balance: detail.balance,
      bundle_amount: this.bundleAmount,
      currency: detail.currency,
    }
  }

  async createPayment(clientId: string, billId: string): Promise<Json> {
    expect(clientId).toBe(this.clientId)
    expect(billId).toBe(this.billId)
    await this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByText(this.bundleAmount, { exact: false }).first()).toBeVisible()
    const createdResponse = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/payments/demo-bank-receipts'))
    await this.operatorPage.getByTestId('create-payment').click()
    const created = await (await createdResponse).json() as Json
    const replayedResponse = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/payments/demo-bank-receipts'))
    await this.operatorPage.getByTestId('create-payment').click()
    const replayed = await (await replayedResponse).json() as Json
    expect(replayed.reused).toBe(true)
    expect(replayed.payment.id).toBe(created.payment.id)
    expect(replayed.line.id).toBe(created.line.id)
    expect(expectedScenario.paymentNoPrefix).toBe('RCPT-CYZN')
    expect(expectedScenario.bankRefPrefix).toBe('BTR-CYZN')
    expect(created.payment.pay_no).toMatch(/^RCPT-CYZN-/)
    expect(created.payment.bank_ref_no).toMatch(/^BTR-CYZN-/)
    this.paymentId = created.payment.id
    this.paymentLineId = created.line.id

    const paymentListResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/payments'))
    await this.operatorPage.goto(`${baseUrl}/billing/payments`, { waitUntil: 'domcontentloaded' })
    const paymentPage = await (await paymentListResponse).json() as Json
    const paymentMatches = (paymentPage.items as Json[]).filter((item) => item.id === created.payment.id)
    const offsetListResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/offsets'))
    await this.operatorPage.goto(`${baseUrl}/billing/offsets`, { waitUntil: 'domcontentloaded' })
    const offsetPage = await (await offsetListResponse).json() as Json
    const applied = (offsetPage.items as Json[]).filter((item) => item.bill_id === billId && item.is_reversed === false)
    return {
      payment_id: created.payment.id,
      payment_no: created.payment.pay_no,
      bank_ref_no: created.payment.bank_ref_no,
      replayed_payment_id: replayed.payment.id,
      payment_line_id: created.line.id,
      payment_count: paymentMatches.length,
      payment_line_count: paymentMatches[0].line_count,
      amount: created.payment.amount,
      bundle_amount: this.bundleAmount,
      currency: created.payment.currency,
      status: created.line.status,
      applied_bill_ids: applied.map((item) => item.bill_id),
      suggested_bill_id: created.target_bill_id,
    }
  }

  async createOffset(lineId: string, billId: string): Promise<Json> {
    expect(lineId).toBe(this.paymentLineId)
    expect(billId).toBe(this.billId)
    await this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    const createdResponse = this.operatorPage.waitForResponse((item) => item.status() === 201 && new URL(item.url()).pathname.endsWith('/api/v1/offsets/demo-full'))
    await this.operatorPage.getByTestId('create-offset').click()
    const created = await (await createdResponse).json() as Json
    this.offsetId = created.offset.id
    const offsetListResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/offsets'))
    await this.operatorPage.goto(`${baseUrl}/billing/offsets`, { waitUntil: 'domcontentloaded' })
    const offsetPage = await (await offsetListResponse).json() as Json
    const active = (offsetPage.items as Json[]).filter((item) => item.id === created.offset.id && item.bill_id === billId && item.is_reversed === false)
    return {
      offset_id: created.offset.id,
      active_offset_count: active.length,
      bill_status: created.bill.status,
      payment_status: created.line.status,
      bill_balance: created.bill.balance,
      payment_unapplied: created.line.balance_amt,
      bundle_amount: this.bundleAmount,
      currency: created.bill.currency,
      case_receipt_received: created.case_receipt.received_amt,
    }
  }

  async reloadSummary(caseId: string): Promise<Json> {
    expect(caseId).toBe(this.caseId)
    const caseResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/cases/${caseId}`))
    const overlayResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/cases/${caseId}/lifecycle-overlay`))
    await this.operatorPage.goto(`${baseUrl}/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    const caseDetail = await (await caseResponse).json() as Json
    const overlay = await (await overlayResponse).json() as Json
    const center = overlay.center_snapshot
    await expect(this.operatorPage.getByText(caseDetail.case_no, { exact: true }).first()).toBeVisible()
    const lifecycleState = this.operatorPage.locator('[aria-label="当前案件生命周期状态"]')
    await expect(lifecycleState).toContainText('业务阶段：授权登记中')
    await expect(lifecycleState).toContainText('官方程序阶段：授权登记')
    await expect(lifecycleState).toContainText('法律状态：申请审理中')
    await expect(lifecycleState).toContainText('核验状态：已确认')
    for (const rawValue of [
      center.business_stage,
      center.official_procedure_stage,
      center.legal_status,
      center.verification_status,
    ]) {
      await expect(lifecycleState).not.toContainText(rawValue)
    }

    const groupedAmount = this.bundleAmount.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    const amountLabel = `¥${groupedAmount}`
    const zeroLabel = '¥0.00'

    const draftResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/fees/drafts/${this.draftId}`))
    await this.operatorPage.goto(`${baseUrl}/fees/drafts/${this.draftId}`, { waitUntil: 'domcontentloaded' })
    const draft = await (await draftResponse).json() as Json
    await expect(this.operatorPage).toHaveURL(`${baseUrl}/fees/drafts/${this.draftId}`)
    const draftHeader = this.operatorPage.locator('.case-header')
    await expect(draftHeader).toContainText(draft.id)
    await expect(draftHeader).toContainText('已锁定')
    await expect(draftHeader).toContainText(`币种: ${draft.currency}`)
    await this.operatorPage.getByRole('tab', { name: '概览', exact: true }).click()
    await expect(this.operatorPage.locator('.info-item').filter({ hasText: '服务费合计' })).toContainText(amountLabel)

    const billResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/bills/${this.billId}`))
    await this.operatorPage.goto(`${baseUrl}/billing/bills/${this.billId}`, { waitUntil: 'domcontentloaded' })
    const bill = await (await billResponse).json() as Json
    await expect(this.operatorPage).toHaveURL(`${baseUrl}/billing/bills/${this.billId}`)
    await expect(this.operatorPage.getByRole('heading', { name: `账单号 ${bill.bill_no}`, exact: true })).toBeVisible()
    const billHeader = this.operatorPage.locator('.case-header')
    await expect(billHeader).toContainText('已结清')
    await expect(billHeader).toContainText(bill.currency)
    await this.operatorPage.getByRole('tab', { name: '概览', exact: true }).click()
    await expect(this.operatorPage.locator('.amount-row').filter({ hasText: '余额' })).toContainText(zeroLabel)

    const paymentResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/payments'))
    await this.operatorPage.goto(`${baseUrl}/billing/payments`, { waitUntil: 'domcontentloaded' })
    const paymentPage = await (await paymentResponse).json() as Json
    const payment = (paymentPage.items as Json[]).find((item) => item.id === this.paymentId)
    expect(payment).toBeDefined()
    const paymentRow = this.operatorPage.locator('.el-table__row').filter({ hasText: payment.pay_no })
    await expect(paymentRow).toHaveCount(1)
    await expect(paymentRow).toContainText(amountLabel)
    await expect(paymentRow).toContainText(zeroLabel)
    await expect(paymentRow).toContainText('已核销')

    const offsetResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/offsets'))
    await this.operatorPage.goto(`${baseUrl}/billing/offsets`, { waitUntil: 'domcontentloaded' })
    const offsetPage = await (await offsetResponse).json() as Json
    const offset = (offsetPage.items as Json[]).find((item) => item.id === this.offsetId)
    expect(offset).toBeDefined()
    const offsetRow = this.operatorPage.locator('.el-table__row').filter({ hasText: bill.bill_no })
    await expect(offsetRow).toHaveCount(1)
    await expect(offsetRow).toContainText(groupedAmount)
    await expect(offsetRow).toContainText('正常')

    const receiptResponse = this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith('/api/v1/case-receipts'))
    await this.operatorPage.goto(`${baseUrl}/billing/case-receipts`, { waitUntil: 'domcontentloaded' })
    const receiptPage = await (await receiptResponse).json() as Json
    const receipt = (receiptPage.items as Json[]).find((item) => item.case_id === caseId && item.fee_type === 'SERVICE')
    expect(receipt).toBeDefined()
    const receiptRow = this.operatorPage.locator('.el-table__row').filter({ hasText: caseDetail.case_no })
    await expect(receiptRow).toHaveCount(1)
    await expect(receiptRow).toContainText(receipt.fee_code)
    await expect(receiptRow).toContainText('服务费')
    await expect(receiptRow).toContainText(this.bundleAmount)
    await expect(receiptRow).toContainText(receipt.currency)
    return {
      case_id: caseId,
      route_object_ids: { case: caseId, draft: this.draftId, bill: this.billId },
      authoritative_object_ids: { case: caseDetail.id, draft: draft.id, bill: bill.id },
      surfaces: {
        case: { id: caseDetail.id, business_stage: center.business_stage, official_procedure_stage: center.official_procedure_stage, legal_status: center.legal_status, confirmation_status: center.verification_status },
        draft: { id: draft.id, status: draft.status, amount: draft.amount, currency: draft.currency },
        bill: { id: bill.id, status: bill.status, balance: bill.balance, currency: bill.currency },
        payment: { id: payment.id, status: payment.prepayment_status, unapplied: payment.unapplied_amt, currency: payment.currency },
        offset: { id: offset.id, active: offset.is_reversed === false, amount: offset.offset_amt, currency: bill.currency },
      },
      lifecycle_status: center.business_stage,
      lifecycle_stage: center.official_procedure_stage,
      application_status: center.legal_status,
      source_state: center.verification_status,
      legacy_display: caseDetail.status,
      bill_status: bill.status,
      payment_status: payment.prepayment_status,
      bill_balance: bill.balance,
      payment_unapplied: payment.unapplied_amt,
      bundle_amount: this.bundleAmount,
      currency: bill.currency,
      checkpoints_passed: checkpointContract.length,
      visible_surfaces: {
        case: { case_no: caseDetail.case_no, lifecycle_tuple: [center.business_stage, center.official_procedure_stage, center.legal_status, center.verification_status] },
        draft: { id: draft.id, status: '已锁定', amount: amountLabel, currency: draft.currency },
        bill: { bill_no: bill.bill_no, status: '已结清', balance: zeroLabel, currency: bill.currency },
        payment: { pay_no: payment.pay_no, status: '已核销', amount: amountLabel, unapplied: zeroLabel },
        offset: { bill_no: bill.bill_no, status: '正常', amount: this.bundleAmount },
        receipt: { case_no: caseDetail.case_no, fee_code: receipt.fee_code, fee_type: '服务费', amount: this.bundleAmount, currency: receipt.currency },
      },
      synthetic_zero_count: [draft.total_service, bill.amount, receipt.receivable_amt, receipt.received_amt].filter((value) => value === '0.00').length,
    }
  }
  async preflight(): Promise<Json> {
    await this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    const responsePromise = this.operatorPage.waitForResponse((response) => response.status() === 200 && response.url().includes('/fees/demo-preflight'))
    await this.operatorPage.getByTestId('demo-preflight').click()
    const item = await (await responsePromise).json() as Json
    const primaryItem = (item.items as Json[])[0]
    return {
      provenance: {
        bundle_id: item.bundle_id,
        bundle_version: item.bundle_version,
        manifest_sha256: item.manifest_sha256,
        template_code: item.template_code,
        template_sha256: item.template_sha256,
        rate_item_code: primaryItem.item_code,
        rate_source_ref: primaryItem.source_ref,
        rate_source_version: primaryItem.source_version,
        rate_source_sha256: primaryItem.source_sha256,
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

  async uploadRole(documentId: string, descriptor: { role: EvidenceRole; path: string; sha256: string; metadata: Json }): Promise<EvidenceBinding>
  async uploadRole(documentId: string, descriptor: OaReplyOutputDescriptor): Promise<Json>
  async uploadRole(
    documentId: string,
    descriptor: { role: EvidenceRole; path: string; sha256: string; metadata: Json } | OaReplyOutputDescriptor,
  ): Promise<EvidenceBinding | Json> {
    if ('classification' in descriptor) {
      expect(descriptor.classification).toBe('SYNTHETIC_TEST_OUTPUT')
      const roleLabel = descriptor.official_file_role === 'OA_STATEMENT_WORD'
        ? 'OA意见陈述 Word'
        : descriptor.official_file_role === 'OA_STATEMENT_PDF'
          ? 'OA意见陈述 PDF'
          : descriptor.official_file_role === 'OA_MODIFIED_CLAIMS'
            ? '修改后的权利要求书'
            : '电子申请回执'
      await this.operatorPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
      await this.operatorPage.getByTestId('attachment-open-upload').click()
      await this.operatorPage.getByTestId('attachment-file-picker').locator('input[type=file]').setInputFiles(descriptor.path)
      const dialog = this.operatorPage.getByRole('dialog', { name: '上传附件' })
      await dialog.locator('.el-form-item').filter({ hasText: '附件角色' }).locator('.el-select__wrapper').click()
      await this.operatorPage.getByRole('option', { name: roleLabel, exact: true }).click()
      const response = this.operatorPage.waitForResponse((item) => item.status() === 201 && item.url().includes('/attachments'))
      await dialog.getByRole('button', { name: '确认上传' }).click()
      const uploaded = await (await response).json() as Json
      expect(uploaded.content_hash).toBe(`sha256:${descriptor.sha256}`)
      return { ...uploaded, output_role: descriptor.official_file_role, oa_sequence: descriptor.oa_sequence }
    }
    const binding = await uploadAndReviewEvidenceViaVisibleUi(this.operatorPage, this.reviewerPage, documentId, descriptor)
    this.evidenceRoleMap.set(descriptor.role, binding)
    return binding
  }
}

test('Integrated Scheme A executes prior lifecycle and new finance on one case', async ({ browser, page, request }) => {
  test.setTimeout(240_000)
  for (const required of [adminUsername, adminPassword, reviewerUsername, reviewerPassword, evidenceDir, bundlePath, expectedDisclaimer, integratedEvidenceJson, oaReplyOutputJson]) expect(typeof required).toBe('string')

  const operatorToken = await login(page, adminUsername!, adminPassword!)
  const reviewerContext: BrowserContext = await browser.newContext()
  const reviewerPage = await reviewerContext.newPage()
  page.setDefaultTimeout(10_000)
  reviewerPage.setDefaultTimeout(10_000)
  await login(reviewerPage, reviewerUsername!, reviewerPassword!)
  const evidenceRoleMap = new Map<EvidenceRole, EvidenceBinding>()
  const outputRows = JSON.parse(oaReplyOutputJson!) as OaReplyOutputDescriptor[]
  expect(outputRows).toHaveLength(6)
  expect(new Set(outputRows.map((item) => item.path)).size).toBe(6)
  expect(new Set(outputRows.map((item) => item.sha256)).size).toBe(6)
  for (const item of outputRows) {
    expect(item.classification).toBe('SYNTHETIC_TEST_OUTPUT')
    expect(item.sha256).toMatch(/^[0-9a-f]{64}$/)
  }
  const outputMap = new Map(outputRows.map((item) => [`${item.oa_sequence}:${item.official_file_role}`, item]))
  const journey = new IntegratedJourneyDriver(page, reviewerPage, evidenceRoleMap, request, operatorToken, evidenceDescriptors(), outputMap)
  const task0Checkpoints: Json[] = []
  const task5Checkpoints: Json[] = []
  const task6Checkpoints: Json[] = []
  const task7Checkpoints: Json[] = []
  const task8Checkpoints: Json[] = []
  const task9Checkpoints: Json[] = []
  const suffix = `${Date.now()}`
  const clientCode = `${expectedScenario.customerCodePrefix}-${suffix}`
  const caseNo = `${expectedScenario.caseNoPrefix}-${suffix}`
  let clientId = ''; let caseId = ''; let filingPackageId = ''; let oa1SourceId = ''; let oa1PackageId = ''; let oa1TaskId = ''; let grantOriginalTaskId = ''; let grantReplacementTaskId = ''; let draftId = ''; let billId = ''; let paymentId = ''; let paymentLineId = ''; let offsetId = ''
  const manifestSha256 = process.env.FPMS_DEMO_EXPECTED_MANIFEST_SHA256 || ''

  await test.step(checkpointContract[0], async () => {
    for (const [key, value] of Object.entries(expectedScenario)) {
      if (key !== 'stageOrder') expect(typeof value).toBe('string')
    }
    expect(expectedScenario.stageOrder).toBe('01,02,03,04,05,06,07,08,09')
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
    await expect(page.getByText(expectedScenario.serviceItemName!, { exact: true })).toBeVisible()
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
    task0Checkpoints.push({ checkpoint: 'IA-00', result: snapshot })
  })

  await test.step(checkpointContract[1], async () => {
    const x = await journey.createClientAndContact(clientCode); clientId = x.client_id
    expect(x.client_code).toBe(clientCode); expect(x.client_name).toBe(expectedScenario.customerName); expect(x.contact_name).toBe(expectedScenario.contactName); expect(x.contact_title).toBe(expectedScenario.contactTitle); expect(x.contact_email).toBe(expectedScenario.contactEmail); expect(x.client_count).toBe(1); expect(x.contact_count).toBe(1); expect(x.primary_contact_client_id).toBe(clientId)
    task5Checkpoints.push({ checkpoint: 'IA-01', result: x })
  })
  await test.step(checkpointContract[2], async () => {
    const x = await journey.createCase(clientId, caseNo); caseId = x.case_id
    expect(x.case_no).toBe(caseNo); expect(x.case_title).toBe(expectedScenario.caseTitle); expect(x.projection).toEqual(['NEW_CASE', 'NOT_SUBMITTED', 'NOT_ESTABLISHED', 'CONFIRMED']); expect(x.legacy_display).toBe('NOT_FILED')
    expect(x.business_counts).toEqual({ package: 0, task: 0, draft: 0, bill: 0, payment: 0, offset: 0 })
    task5Checkpoints.push({ checkpoint: 'IA-02', result: x })
  })
  await test.step(checkpointContract[3], async () => {
    const x = await journey.inspectCatalog(caseId); expect(x.row_count).toBe(60); expect(x.executable_enabled).toBe(true); expect(x.reference_only_disabled).toBe(true); expect(x.request_status).not.toBe(422)
    task5Checkpoints.push({ checkpoint: 'IA-03', result: x })
  })
  await test.step(checkpointContract[4], async () => {
    const x = await journey.resolveFiling(caseId); filingPackageId = x.package_id
    expect(x.replayed_package_id).toBe(filingPackageId); expect(x.package_kind).toBe('FILING_PREP'); expect(x.projection).toEqual(['FILING_PREPARATION', 'NOT_SUBMITTED', 'NOT_ESTABLISHED', 'CONFIRMED'])
    task5Checkpoints.push({ checkpoint: 'IA-04', result: x })
  })
  await test.step(checkpointContract[5], async () => {
    const x = await journey.completeFilingAndOa1(caseId); oa1SourceId = x.source_id; oa1PackageId = x.package_id; oa1TaskId = x.task_id
    expect(x.filing_package_id).toBe(filingPackageId); expect(evidenceRoleMap.size).toBe(7)
    const filingBinding = evidenceRoleMap.get('FILING_FINAL_SUBMISSION')!
    const filingRecord = recordFilingSubmission(
      evidenceRoleMap,
      filingBinding,
      x.filing_command_result,
      x.filing_package_result,
      x.filing_activity_result,
    )
    expect(filingRecord.consumerResultId).toBe(x.filing_activity_result.activity_id)
    expect(x.filing_receipt_projection).toEqual(['PROSECUTION_MANAGEMENT', 'SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE', 'APPLICATION_PENDING', 'CONFIRMED'])
    expect(evidenceRoleMap.get('OA_NOTICE_1')!.consumer).toBe('oa1-notice')
    expect(x.deadline_surfaces).toEqual({ create: x.deadline, read: x.deadline, edit: x.deadline, impact_preview: x.deadline, wizard: x.deadline })
    expect(typeof x.deadline.official_due_date).toBe('string'); expect(['MANUAL_OFFICIAL_NOTICE', 'IMPORTED_OFFICIAL_NOTICE']).toContain(x.deadline.official_due_date_source); expect(x.deadline.official_due_date_status).toBe('CONFIRMED'); expect(x.wizard_preview_due_date).toBe(x.deadline.official_due_date); expect(x.replayed_package_id).toBe(oa1PackageId); expect(typeof x.task_id).toBe('string'); expect(x.task_id.length).toBeGreaterThan(0); expect(x.replayed_task_id).toBe(oa1TaskId)
    expect(x.task_identity_snapshots.first).toEqual(x.task_identity_snapshots.replay); expect(x.task_identity_snapshots.first.count).toBe(1)
    expect(x.missing_deadline_no_write.status).toBeGreaterThanOrEqual(400); expect(x.missing_deadline_no_write.title_absent).toBe(true); expect(x.missing_deadline_no_write.before.package_states.length).toBeGreaterThan(0); expect(x.missing_deadline_no_write.before).toEqual(x.missing_deadline_no_write.after)
    expect(x.changed_deadline_no_write.date_disabled).toBe(true); expect(x.changed_deadline_no_write.source_disabled).toBe(true); expect(x.changed_deadline_no_write.status_visible).toBe(true); expect(x.changed_deadline_no_write.before.package_states.length).toBeGreaterThan(0); expect(x.changed_deadline_no_write.before).toEqual(x.changed_deadline_no_write.after)
    task5Checkpoints.push({ checkpoint: 'IA-05', result: x })
  })
  await test.step(checkpointContract[6], async () => {
    const x = await journey.createOaOut(oa1SourceId, oa1PackageId); expect(x.linked_source_id).toBe(oa1SourceId); expect(x.linked_package_id).toBe(oa1PackageId); expect(x.link_count).toBe(1); expect(x.linked_reply_ids).toEqual([x.oa_out_id]); expect(x.replayed_reply_id).toBe(x.oa_out_id); expect(x.task_count).toBe(1); expect(x.task_status).toBe('OPEN'); expect(x.package_status).toBe('WAITING_RECEIPT')
    task5Checkpoints.push({ checkpoint: 'IA-06', result: x })
    await mkdir(evidenceDir!, { recursive: true })
    await writeFile(path.join(evidenceDir!, 'task5-checkpoints.json'), JSON.stringify({ checkpoints: task5Checkpoints, evidence_bindings: [...evidenceRoleMap.values()] }, null, 2))
  })
  await test.step(checkpointContract[7], async () => {
    const x = await journey.rejectInvalidReceipts(caseId, oa1PackageId); expect(x.cross_case_status).toBeGreaterThanOrEqual(400); expect(x.same_case_wrong_source_status).toBeGreaterThanOrEqual(400); expect(x.cross_case_before_snapshot).toEqual(x.cross_case_after_snapshot); expect(x.wrong_source_before_snapshot).toEqual(x.wrong_source_after_snapshot); expect(x.cross_case_before_snapshot.target_package.package.id).toBe(oa1PackageId); expect(x.wrong_source_before_snapshot.target_package.package.id).toBe(oa1PackageId)
    task6Checkpoints.push({ checkpoint: 'IA-07', result: x })
  })
  await test.step(checkpointContract[8], async () => {
    const x = await journey.archiveOa1(oa1PackageId); expect(x.package_status).toBe('ARCHIVED'); expect(x.closed_task_ids).toEqual([oa1TaskId]); expect(x.projection).toEqual(['PROSECUTION_MANAGEMENT', 'SUBSTANTIVE_EXAMINATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.legacy_display).toBe('SUB_EXAM')
    task6Checkpoints.push({ checkpoint: 'IA-08', result: x })
  })
  await test.step(checkpointContract[9], async () => {
    const x = await journey.completeOa2(caseId)
    expect(evidenceRoleMap.size).toBe(10); expect(x.source_id).not.toBe(oa1SourceId); expect(x.package_id).not.toBe(oa1PackageId); expect(x.task_id).not.toBe(oa1TaskId); expect(x.oa_out_id).not.toBe(x.oa1_oa_out_id); expect(x.receipt_id).not.toBe(x.oa1_receipt_id); expect(x.oa_sequence).toBe(2); expect(x.notice_role).toBe('OA_NOTICE_2'); expect(x.receipt_role).toBe('OA_RECEIPT_2')
    expect(x.deadline_surfaces).toEqual({ create: x.deadline, read: x.deadline, edit: x.deadline, impact_preview: x.deadline, wizard: x.deadline }); expect(typeof x.deadline.official_due_date).toBe('string'); expect(['MANUAL_OFFICIAL_NOTICE', 'IMPORTED_OFFICIAL_NOTICE']).toContain(x.deadline.official_due_date_source); expect(x.deadline.official_due_date_status).toBe('CONFIRMED'); expect(x.sequence1_reuse_no_write).toBe(true); expect(x.incomplete_deadline_no_write).toBe(true)
    expect(x.closed_task_ids).toEqual([x.task_id]); expect(x.oa1_history_after).toEqual(x.oa1_history_before); expect(x.projection).toEqual(['PROSECUTION_MANAGEMENT', 'SUBSTANTIVE_EXAMINATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.legacy_display).toBe('SUB_EXAM')
    task6Checkpoints.push({ checkpoint: 'IA-09', result: x })
    await mkdir(evidenceDir!, { recursive: true })
    await writeFile(path.join(evidenceDir!, 'task6-checkpoints.json'), JSON.stringify({ checkpoints: [...task5Checkpoints, ...task6Checkpoints], evidence_bindings: [...evidenceRoleMap.values()] }, null, 2))
  })
  await test.step(checkpointContract[10], async () => {
    const x = await journey.createGrantOriginal(caseId)
    const binding = evidenceRoleMap.get('GRANT_NOTICE_ORIGINAL')!; grantOriginalTaskId = x.task_id
    expect(evidenceRoleMap.size).toBe(11); expect(x.source_document_id).toBe(x.document_id); expect(x.source_document_date).toBe(x.expected_source_document_date); expect(x.source_deadline).toEqual(x.expected_deadline); expect(x.source_evidence_version_id).toBe(binding.evidenceVersionId); expect(x.source_content_hash).toBe(binding.contentHash); expect(x.original_activity_id).toBe(evidenceRoleMap.get('GRANT_NOTICE_ORIGINAL')!.consumerResultId); expect(x.actionable_task_ids).toEqual([grantOriginalTaskId]); expect(x.projection).toEqual(['GRANT_REGISTRATION_IN_PROGRESS', 'GRANT_REGISTRATION', 'APPLICATION_PENDING', 'CONFIRMED']); expect(x.official_fee_carriers).toEqual({ item: 0, obligation: 0, draft: 0, payable: 0 })
    task7Checkpoints.push({ checkpoint: 'IA-10', result: x })
  })
  await test.step(checkpointContract[11], async () => {
    const x = await journey.replaceGrant(grantOriginalTaskId)
    const binding = evidenceRoleMap.get('GRANT_NOTICE_REPLACEMENT')!; grantReplacementTaskId = x.replacement_task_id
    expect(evidenceRoleMap.size).toBe(12)
    expect(grantReplacementTaskId).not.toBe(grantOriginalTaskId); expect(x.original_document_id).not.toBe(x.replacement_document_id); expect(x.replacement_document_id).toBe(x.document_id); expect(x.superseded_task_id).toBe(grantOriginalTaskId); expect(x.replacement_predecessor_task_id).toBe(grantOriginalTaskId); expect(x.original_activity_id).toBe(evidenceRoleMap.get('GRANT_NOTICE_ORIGINAL')!.consumerResultId); expect(x.replacement_activity_id).toBe(evidenceRoleMap.get('GRANT_NOTICE_REPLACEMENT')!.consumerResultId); expect(x.replacement_activity_id).not.toBe(x.original_activity_id); expect(x.supersedes_activity_id).toBe(x.original_activity_id); expect(x.original_source_evidence_version_id).toBe(evidenceRoleMap.get('GRANT_NOTICE_ORIGINAL')!.evidenceVersionId); expect(x.replacement_source_evidence_version_id).toBe(binding.evidenceVersionId); expect(x.replacement_source_content_hash).toBe(binding.contentHash); expect(x.replacement_metadata).toEqual(binding.metadata); expect(x.actionable_task_ids).toEqual([grantReplacementTaskId]); expect(x.original_hash).not.toBe(x.replacement_hash); expect(x.projection).toEqual(['GRANT_REGISTRATION_IN_PROGRESS', 'GRANT_REGISTRATION', 'APPLICATION_PENDING', 'CONFIRMED'])
    task7Checkpoints.push({ checkpoint: 'IA-11', result: x })
  })
  await test.step(checkpointContract[12], async () => {
    const x = await journey.exerciseGrantGatesAndPay(grantOriginalTaskId, grantReplacementTaskId)
    expect(x.blocked_mutations).toEqual(['generate-draft', 'batch-instruction', 'generate-notices', 'mark_waiting_client']); expect(x.blocked_statuses).toEqual([409, 409, 409, 409]); expect(x.blocked_observations).toHaveLength(4); for (const observation of x.blocked_observations as Json[]) expect(observation.after_snapshot).toEqual(observation.before_snapshot); expect(x.current_instruction).toBe('PAY'); expect(x.current_instruction_count).toBe(1); expect(x.missing_authority_status).toBe(409); expect(x.missing_authority_code).toBe('DEMO_OFFICIAL_FEE_CONFIG_REQUIRED'); expect(x.missing_authority_before).toEqual(x.missing_authority_after); expect(x.official_fee_carriers).toEqual({ item: 0, obligation: 0, draft: 0, payable: 0 })
    task7Checkpoints.push({ checkpoint: 'IA-12', result: x })
    await mkdir(evidenceDir!, { recursive: true })
    await writeFile(path.join(evidenceDir!, 'task7-checkpoints.json'), JSON.stringify({ checkpoints: [...task5Checkpoints, ...task6Checkpoints, ...task7Checkpoints], evidence_bindings: [...evidenceRoleMap.values()] }, null, 2))
  })
  await test.step(checkpointContract[13], async () => {
    const x = await journey.createServiceDraft(caseId); draftId = x.draft_id
    expect(x.case_id).toBe(caseId); expect(x.provenance).toEqual(expectedProvenance); expect(x.disclaimer).toBe(expectedDisclaimer); expect(x.obligation_count).toBe(1); expect(x.draft_count).toBe(1); expect(x.draft_status).toBe('LOCKED'); expect(x.service_amount).toBe(x.bundle_amount); expect(x.official_fee_display).toBe('未配置'); expect(x.official_fee_in_total).toBe(false); expect(x.official_fee_carriers).toEqual({ item: 0, obligation: 0, draft: 0, payable: 0 })
    await page.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByText(draftId, { exact: false })).toBeVisible()
    await expect(page.getByText(`${x.bundle_amount} CNY`, { exact: true })).toBeVisible()
    await expect(page.getByText(x.disclaimer, { exact: false })).toBeVisible()
    const visibleProvenance = {
      'bundle-id': expectedProvenance.bundle_id,
      'bundle-version': expectedProvenance.bundle_version,
      'manifest-sha256': expectedProvenance.manifest_sha256,
      'template-code': expectedProvenance.template_code,
      'template-sha256': expectedProvenance.template_sha256,
      'rate-item-code': expectedProvenance.rate_item_code,
      'rate-source-ref': expectedProvenance.rate_source_ref,
      'rate-source-version': expectedProvenance.rate_source_version,
      'rate-source-sha256': expectedProvenance.rate_source_sha256,
    }
    for (const [testId, value] of Object.entries(visibleProvenance)) {
      await expect(page.getByTestId(testId)).toHaveText(value!)
    }
    task8Checkpoints.push({ checkpoint: 'IA-13', result: x })
  })
  await test.step(checkpointContract[14], async () => {
    const x = await journey.createBill(draftId); billId = x.bill_id
    expect(x.bill_no).toMatch(/^AR-CYZN-/); expect(x.replayed_bill_id).toBe(billId); expect(x.bill_count).toBe(1); expect(x.source_draft_ids).toEqual([draftId]); expect(x.consumed_draft_ids).toEqual([draftId]); expect(x.bill_item_ids).toHaveLength(1); expect(x.bill_item_draft_ids).toEqual([draftId]); expect(x.status).toBe('UNSETTLED'); expect(x.balance).toBe(x.bundle_amount); expect(x.currency).toBe('CNY')
    task8Checkpoints.push({ checkpoint: 'IA-14', result: x })
  })
  await test.step(checkpointContract[15], async () => {
    const x = await journey.createPayment(clientId, billId); paymentId = x.payment_id; paymentLineId = x.payment_line_id
    expect(x.payment_no).toMatch(/^RCPT-CYZN-/); expect(x.bank_ref_no).toMatch(/^BTR-CYZN-/); expect(x.replayed_payment_id).toBe(x.payment_id); expect(x.payment_count).toBe(1); expect(x.payment_line_count).toBe(1); expect(x.amount).toBe(x.bundle_amount); expect(x.currency).toBe('CNY'); expect(x.status).toBe('UNALLOCATED'); expect(x.applied_bill_ids).toEqual([]); expect(x.suggested_bill_id).toBe(billId)
    task8Checkpoints.push({ checkpoint: 'IA-15', result: x })
  })
  await test.step(checkpointContract[16], async () => {
    const x = await journey.createOffset(paymentLineId, billId); offsetId = x.offset_id; expect(x.active_offset_count).toBe(1); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.bill_balance).toBe('0.00'); expect(x.payment_unapplied).toBe('0.00'); expect(x.currency).toBe('CNY'); expect(x.case_receipt_received).toBe(x.bundle_amount)
    task8Checkpoints.push({ checkpoint: 'IA-16', result: x })
  })
  await test.step(checkpointContract[17], async () => {
    const x = await journey.reloadSummary(caseId); expect(x.case_id).toBe(caseId); expect(x.route_object_ids).toEqual(x.authoritative_object_ids); expect(x.surfaces).toEqual({ case: { id: caseId, business_stage: 'GRANT_REGISTRATION_IN_PROGRESS', official_procedure_stage: 'GRANT_REGISTRATION', legal_status: 'APPLICATION_PENDING', confirmation_status: 'CONFIRMED' }, draft: { id: draftId, status: 'LOCKED', amount: x.bundle_amount, currency: 'CNY' }, bill: { id: billId, status: 'SETTLED', balance: '0.00', currency: 'CNY' }, payment: { id: paymentId, status: 'FULLY_ALLOCATED', unapplied: '0.00', currency: 'CNY' }, offset: { id: offsetId, active: true, amount: x.bundle_amount, currency: 'CNY' } }); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.synthetic_zero_count).toBe(0)
    task8Checkpoints.push({ checkpoint: 'IA-17', result: x })
    await mkdir(evidenceDir!, { recursive: true })
    await writeFile(path.join(evidenceDir!, 'task8-checkpoints.json'), JSON.stringify({ checkpoints: [...task5Checkpoints, ...task6Checkpoints, ...task7Checkpoints, ...task8Checkpoints], evidence_bindings: [...evidenceRoleMap.values()] }, null, 2))
  })
  await test.step(checkpointContract[18], async () => {
    const x = await journey.reloadSummary(caseId)
    expect(x.lifecycle_status).toBe('GRANT_REGISTRATION_IN_PROGRESS'); expect(x.lifecycle_stage).toBe('GRANT_REGISTRATION'); expect(x.application_status).toBe('APPLICATION_PENDING'); expect(x.source_state).toBe('CONFIRMED'); expect(x.legacy_display).toBe('GRANT_PENDING'); expect(x.bill_status).toBe('SETTLED'); expect(x.payment_status).toBe('FULLY_ALLOCATED'); expect(x.bill_balance).toBe('0.00'); expect(x.payment_unapplied).toBe('0.00'); expect(x.currency).toBe('CNY'); expect(x.checkpoints_passed).toBe(19); expect(evidenceRoleMap.size).toBe(12)
    task9Checkpoints.push({ checkpoint: 'IA-18', result: x })
    await page.screenshot({ path: path.join(evidenceDir!, 'integrated-final.png'), fullPage: true })
    await writeFile(path.join(evidenceDir!, 'task9-checkpoints.json'), JSON.stringify({ checkpoints: [...task0Checkpoints, ...task5Checkpoints, ...task6Checkpoints, ...task7Checkpoints, ...task8Checkpoints, ...task9Checkpoints], evidence_bindings: [...evidenceRoleMap.values()], final_summary: x }, null, 2))
  })

  const orderedEvidenceLedger = assertCompleteEvidenceLedger(evidenceRoleMap)
  await mkdir(evidenceDir!, { recursive: true })
  await writeFile(path.join(evidenceDir!, 'evidence-role-map.json'), JSON.stringify(orderedEvidenceLedger, null, 2))
  await reviewerContext.close()
})
