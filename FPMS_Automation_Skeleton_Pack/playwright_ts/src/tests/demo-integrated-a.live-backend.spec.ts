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
  private clientName = ''
  private caseId = ''
  private caseNo = ''
  private filingPackageId = ''
  private oa1SourceTitle = ''

  constructor(
    readonly operatorPage: Page,
    readonly reviewerPage: Page,
    readonly evidenceRoleMap: Map<EvidenceRole, EvidenceBinding>,
    readonly apiRequest: APIRequestContext,
    readonly accessToken: string,
    readonly evidenceDescriptorsByRole: Map<EvidenceRole, { role: EvidenceRole; path: string; sha256: string; metadata: Json }>,
  ) {}

  private red(checkpoint: string): never {
    throw new Error(`${checkpoint} action RED: implement through its public UI/API owner`)
  }

  async createClientAndContact(code: string): Promise<Json> {
    this.clientName = `虚构集成演示客户-${code}`
    await this.operatorPage.goto(`${baseUrl}/clients/new`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '新建客户' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入客户名称').fill(this.clientName)
    await this.operatorPage.getByPlaceholder('请输入客户代码（可选）').fill(code)
    await this.operatorPage.getByPlaceholder('请输入邮箱地址').fill(`${code.toLowerCase()}@example.test`)
    const clientResponse = this.operatorPage.waitForResponse((response) => response.status() === 201 && new URL(response.url()).pathname.endsWith('/api/v1/clients'))
    await this.operatorPage.getByRole('button', { name: '创建客户' }).click()
    const client = await (await clientResponse).json() as Json
    expect(client.client_code).toBe(code)

    await this.operatorPage.goto(`${baseUrl}/clients/${client.id}`, { waitUntil: 'domcontentloaded' })
    await this.operatorPage.getByRole('tab', { name: '联系人' }).click()
    await this.operatorPage.getByRole('button', { name: '新增联系人' }).click()
    const dialog = this.operatorPage.getByRole('dialog', { name: '新增联系人' })
    await dialog.locator('.el-form-item').filter({ hasText: '姓名' }).getByRole('textbox').fill('虚构主联系人')
    await dialog.locator('.el-form-item').filter({ hasText: '职务' }).getByRole('textbox').fill('知识产权负责人')
    await dialog.locator('.el-form-item').filter({ hasText: '邮箱' }).getByRole('textbox').fill(`${code.toLowerCase()}-contact@example.test`)
    await dialog.locator('.el-form-item').filter({ hasText: '主联系人' }).locator('.el-switch').click()
    const contactResponse = this.operatorPage.waitForResponse((response) => response.status() === 201 && new URL(response.url()).pathname.endsWith(`/api/v1/clients/${client.id}/contacts`))
    const contactListResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/clients/${client.id}/contacts`))
    await dialog.getByRole('button', { name: '确定' }).click()
    const contact = await (await contactResponse).json() as Json
    const contactList = await (await contactListResponse).json() as Json[]
    expect(contact.client_id).toBe(client.id)
    expect(contact.is_primary).toBe(true)
    await expect(this.operatorPage.getByText('虚构主联系人', { exact: true })).toBeVisible()
    const clientListResponse = this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/clients') && url.searchParams.get('page_size') === '20'
    })
    await this.operatorPage.goto(`${baseUrl}/clients`, { waitUntil: 'domcontentloaded' })
    const clientList = await (await clientListResponse).json() as Json
    const clientMatches = (clientList.items as Json[]).filter((item) => item.client_code === code && item.name_cn === this.clientName)
    const contactMatches = contactList.filter((item) => item.client_id === client.id && item.contact_name === '虚构主联系人' && item.is_primary === true)
    return { client_id: client.id, contact_id: contact.id, client_count: clientMatches.length, contact_count: contactMatches.length, primary_contact_client_id: contact.client_id }
  }

  async createCase(clientId: string, caseNo: string): Promise<Json> {
    this.caseId = ''
    this.caseNo = caseNo
    await this.operatorPage.goto(`${baseUrl}/cases/new`, { waitUntil: 'domcontentloaded' })
    await expect(this.operatorPage.getByRole('heading', { name: '新建案件' })).toBeVisible()
    await this.operatorPage.getByPlaceholder('请输入案号（例如：P2024-001）').fill(caseNo)
    await this.operatorPage.getByPlaceholder('请输入案件标题').fill('虚构集成演示发明案件')
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

    const billPagePromise = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/bills')).then((response) => response.json() as Promise<Json>)
    await this.operatorPage.goto(`${baseUrl}/billing/bills`, { waitUntil: 'domcontentloaded' })
    const billPage = await billPagePromise
    const paymentPagePromise = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/payments')).then((response) => response.json() as Promise<Json>)
    await this.operatorPage.goto(`${baseUrl}/billing/payments`, { waitUntil: 'domcontentloaded' })
    const paymentPage = await paymentPagePromise
    const offsetPagePromise = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/offsets')).then((response) => response.json() as Promise<Json>)
    await this.operatorPage.goto(`${baseUrl}/billing/offsets`, { waitUntil: 'domcontentloaded' })
    const offsetPage = await offsetPagePromise
    return {
      case_id: created.id,
      case_no: created.case_no,
      projection: [center.business_stage, center.official_procedure_stage, center.legal_status, center.verification_status],
      legacy_display: created.status,
      business_counts: {
        package: packages.length,
        task: (taskPage.items as Json[]).length,
        draft: (draftPage.items as Json[]).length,
        bill: (billPage.items as Json[]).length,
        payment: (paymentPage.items as Json[]).length,
        offset: (offsetPage.items as Json[]).length,
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
    const typeField = this.operatorPage.locator('.el-form-item').filter({ hasText: '文件类型' }).first()
    await typeField.locator('.el-select__wrapper').click()
    await this.operatorPage.getByRole('option', { name: direction === 'IN' ? '官方来文' : '官方去文', exact: true }).click()
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
      await this.operatorPage.getByRole('option', { name: '人工核对官方通知', exact: true }).click()
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
    const overlay = await this.loadLifecycleOverlay(caseId)
    return {
      document_ids: documents.map((item) => item.id).sort(),
      document_titles: documents.map((item) => item.title).sort(),
      document_deadlines: documents.map((item) => [item.id, item.official_due_date, item.official_due_date_source, item.official_due_date_status]).sort(),
      task_ids: tasks.map((item) => item.id).sort(),
      task_states: tasks.map((item) => [item.id, item.status]).sort(),
      package_ids: observedOverlayPackages(overlay).map((item) => item.package_id),
      package_states: observedOverlayPackages(overlay).map((item) => [item.package_id, item.package_kind, item.status, item.source_document_id, item.reply_document_id]),
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

  private async verifyMissingDeadlineNoWrite(caseId: string): Promise<Json> {
    const title = `虚构缺失期限审查意见-${this.caseNo}`
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
    await this.operatorPage.getByRole('option').filter({ hasText: 'OFFICIAL_NOTICE_003' }).first().click()
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
    await this.operatorPage.getByPlaceholder('请输入文档内容或说明').fill('Integrated A 现场已复核')
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
    const filingCreated = await this.createDocumentViaVisibleUi(caseId, '虚构最终递交文件', '2026-08-02')
    const filingBinding = await this.uploadRole(filingCreated.document.id, filingDescriptor)
    await this.operatorPage.goto(`${baseUrl}/official-workflows/filing-preparation?package_id=${this.filingPackageId}`, { waitUntil: 'domcontentloaded' })
    const refreshResponse = this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/official-work-packages/${this.filingPackageId}/filing-preparation/refresh`))
    await this.operatorPage.getByRole('button', { name: '刷新工作包' }).click()
    await refreshResponse
    const externalPayload = { operation_code: 'EXTERNAL_SUBMISSION_RECORDED', occurred_at: filingDescriptor.metadata.effective_at, note: '本地虚构演示人工递交记录' }
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
      receiving_case_no: `FILING-${this.caseNo}`,
      submitter: '虚构演示操作员',
      received_at: filingReceiptDescriptor.metadata.received_at,
      received_file_list: '虚构最终递交文件',
      archive_status: 'ARCHIVED',
      note: '本地虚构演示递交回执',
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
      { role: 'ACCEPTANCE_NOTICE', title: '虚构受理通知书', template: 'OFFICIAL_NOTICE_001', consumer: 'acceptance-notice' },
      { role: 'PRELIMINARY_EXAMINATION_SOURCE', title: '虚构初步审查来源', consumer: 'preliminary-examination' },
      { role: 'PUBLICATION_NOTICE', title: '虚构公布通知书', consumer: 'publication-notice' },
      { role: 'SUBSTANTIVE_EXAMINATION_SOURCE', title: '虚构进入实审通知', consumer: 'substantive-examination' },
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
    this.oa1SourceTitle = `虚构第一次审查意见通知书-${this.caseNo}`
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

  async createOaOut(sourceId: string, packageId: string): Promise<Json> {
    const created = await this.createDocumentViaVisibleUi(this.caseId, `虚构第一次审查意见答复-${this.caseNo}`, '2026-08-09', 'OA_OUT', undefined, this.oa1SourceTitle, 'OUT')
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
    return { linked_source_id: linked.body.package.source_document_id, linked_package_id: linked.body.package.id, link_count: links.length, linked_reply_ids: links.map((item) => item.id).sort(), replayed_reply_id: replayed.body.reply_document.id, task_status: (taskSnapshot.states as string[])[0], task_count: taskSnapshot.count, package_status: packageResult.body.package.status, oa_out_id: created.document.id }
  }
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
  for (const required of [adminUsername, adminPassword, reviewerUsername, reviewerPassword, evidenceDir, bundlePath, expectedDisclaimer, integratedEvidenceJson]) expect(typeof required).toBe('string')

  const operatorToken = await login(page, adminUsername!, adminPassword!)
  const reviewerContext: BrowserContext = await browser.newContext()
  const reviewerPage = await reviewerContext.newPage()
  page.setDefaultTimeout(10_000)
  reviewerPage.setDefaultTimeout(10_000)
  await login(reviewerPage, reviewerUsername!, reviewerPassword!)
  const evidenceRoleMap = new Map<EvidenceRole, EvidenceBinding>()
  const journey = new IntegratedJourneyDriver(page, reviewerPage, evidenceRoleMap, request, operatorToken, evidenceDescriptors())
  const task5Checkpoints: Json[] = []
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
    task5Checkpoints.push({ checkpoint: 'IA-01', result: x })
  })
  await test.step(checkpointContract[2], async () => {
    const x = await journey.createCase(clientId, caseNo); caseId = x.case_id
    expect(x.case_no).toBe(caseNo); expect(x.projection).toEqual(['NEW_CASE', 'NOT_SUBMITTED', 'NOT_ESTABLISHED', 'CONFIRMED']); expect(x.legacy_display).toBe('NOT_FILED')
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
