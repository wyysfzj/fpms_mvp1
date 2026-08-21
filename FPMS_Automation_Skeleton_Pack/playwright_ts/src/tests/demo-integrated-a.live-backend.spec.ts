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
  const uploadResponse = operatorPage.waitForResponse((response) => response.request().method() === 'POST' && response.status() === 201)
  await operatorPage.getByRole('button', { name: '确认上传' }).click()
  const uploaded = await (await uploadResponse).json() as Json
  expect(uploaded.content_hash).toBe(descriptor.sha256)

  await reviewerPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })
  const reviewResponse = reviewerPage.waitForResponse((response) => response.request().method() === 'POST' && response.status() === 200)
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

function bindConsumer(
  binding: EvidenceBinding,
  consumer: string,
  result: Json,
  payload: Json,
): EvidenceBinding {
  expect(payload.reviewed_evidence_version_id).toBe(binding.evidenceVersionId)
  expect(payload.expected_content_hash).toBe(binding.contentHash)
  return { ...binding, consumer, consumerResultId: String(result.id || result.activity_id || result.task_id) }
}

function contractRed(checkpoint: string): never {
  throw new Error(`${checkpoint} contract RED: implementation belongs to its later atomic ordinal`)
}

test('Integrated Scheme A executes prior lifecycle and new finance on one case', async ({ browser, page }) => {
  test.setTimeout(240_000)
  expect(adminUsername && adminPassword && reviewerUsername && reviewerPassword && evidenceDir && bundlePath).toBeTruthy()

  await login(page, adminUsername!, adminPassword!)
  const reviewerContext: BrowserContext = await browser.newContext()
  const reviewerPage = await reviewerContext.newPage()
  await login(reviewerPage, reviewerUsername!, reviewerPassword!)

  const evidenceRoleMap = new Map<EvidenceRole, EvidenceBinding>()
  const suffix = `${Date.now()}`
  const clientCode = `IA-${suffix}`
  const caseNo = `IA-CASE-${suffix}`
  let clientId = ''
  let caseId = ''
  let oa1SourceId = ''
  let oa2SourceId = ''
  let grantOriginalTaskId = ''
  let grantReplacementTaskId = ''
  const manifestSha256 = process.env.FPMS_DEMO_EXPECTED_MANIFEST_SHA256 || ''

  await test.step(checkpointContract[0], async () => {
    expect(orderedRoles).toHaveLength(12)
    expect(manifestSha256).toMatch(/^[0-9a-f]{64}$/)
    await page.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('演示输入已校验')).toBeVisible()
    await expect(page.getByText(manifestSha256)).toBeVisible()
    await expect(page.getByText('SYNTHETIC_TEST_ONLY')).toBeVisible()
  })

  await test.step(checkpointContract[1], async () => { contractRed('IA-01') })
  await test.step(checkpointContract[2], async () => { clientId = clientCode; caseId = caseNo; contractRed('IA-02') })
  await test.step(checkpointContract[3], async () => { contractRed('IA-03') })
  await test.step(checkpointContract[4], async () => { contractRed('IA-04') })
  await test.step(checkpointContract[5], async () => {
    const payload = { reviewed_evidence_version_id: '', expected_content_hash: '', official_due_date: '', official_due_date_source: '', official_due_date_status: 'CONFIRMED' }
    oa1SourceId = bindConsumer({} as EvidenceBinding, 'filing external submission OA1', {}, payload).consumerResultId
  })
  await test.step(checkpointContract[6], async () => { contractRed('IA-06') })
  await test.step(checkpointContract[7], async () => { contractRed('IA-07') })
  await test.step(checkpointContract[8], async () => { contractRed('IA-08') })
  await test.step(checkpointContract[9], async () => { oa2SourceId = oa1SourceId; contractRed('IA-09') })
  await test.step(checkpointContract[10], async () => { grantOriginalTaskId = 'dynamic'; contractRed('IA-10') })
  await test.step(checkpointContract[11], async () => { grantReplacementTaskId = grantOriginalTaskId; contractRed('IA-11') })
  await test.step(checkpointContract[12], async () => {
    const mutationContracts = ['generate-draft', 'batch-instruction', 'generate-notices', 'mark_waiting_client']
    expect(mutationContracts).toHaveLength(4)
    contractRed('IA-12')
  })
  await test.step(checkpointContract[13], async () => { contractRed('IA-13 LOCKED SERVICE') })
  await test.step(checkpointContract[14], async () => { contractRed('IA-14 UNSETTLED') })
  await test.step(checkpointContract[15], async () => { contractRed('IA-15 UNALLOCATED') })
  await test.step(checkpointContract[16], async () => { contractRed('IA-16 SETTLED FULLY_ALLOCATED 0.00') })
  await test.step(checkpointContract[17], async () => { contractRed('IA-17') })
  await test.step(checkpointContract[18], async () => {
    expect({ lifecycle_status: 'GRANT_REGISTRATION_IN_PROGRESS', lifecycle_stage: 'GRANT_REGISTRATION', application_status: 'APPLICATION_PENDING', source_state: 'CONFIRMED', legacy_display: 'GRANT_PENDING' }).toBeTruthy()
  })

  await mkdir(evidenceDir!, { recursive: true })
  await writeFile(path.join(evidenceDir!, 'evidence-role-map.json'), JSON.stringify([...evidenceRoleMap.values()], null, 2))
  await reviewerContext.close()
  expect({ clientId, caseId, oa1SourceId, oa2SourceId, grantOriginalTaskId, grantReplacementTaskId, apiBase }).toBeTruthy()
})
