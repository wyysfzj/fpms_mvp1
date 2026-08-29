import { test, expect, type Locator, type Page, type Request, type Response } from '@playwright/test'
import { readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import path from 'node:path'

type Json = Record<string, unknown>
type ActionBinding = {
  stage: string
  action_id: string
  mutation_expected: boolean
  method?: string
  path?: string
  status?: number
  result?: Json
}

const baseUrl = process.env.FPMS_BASE_URL || 'http://127.0.0.1:5173'
const actionBindings: ActionBinding[] = []

function required(name: string): string {
  const value = process.env[name]
  expect(value, `${name} must be supplied by the strict runner`).toBeTruthy()
  return value!
}

function bindStageAction(stage: string, actionId: string, mutationExpected: boolean): ActionBinding {
  const binding = { stage, action_id: actionId, mutation_expected: mutationExpected }
  actionBindings.push(binding)
  return binding
}

function assertStrict(_assertionId: string, condition: boolean, detail: string): void {
  expect(condition, detail).toBe(true)
}

async function selectFirstOption(page: Page, label: string): Promise<void> {
  const field = page.locator('.el-form-item').filter({ hasText: label }).first()
  await field.locator('.el-select__wrapper').click()
  await page.keyboard.press('ArrowDown')
  await page.keyboard.press('Enter')
}

async function expectSelected(page: Page, label: string, option: string): Promise<void> {
  const field = page.locator('.el-form-item').filter({ hasText: label }).first()
  await expect(field.locator('.el-select__placeholder')).toContainText(option)
}

async function visibleMutation(
  page: Page,
  binding: ActionBinding,
  control: Locator,
  method: string,
  pathPattern: RegExp,
): Promise<Json> {
  const responsePromise = page.waitForResponse(response => (
    response.request().method() === method && pathPattern.test(new URL(response.url()).pathname)
  ))
  await control.click()
  const response = await responsePromise
  expect(response.status(), `${binding.action_id} response status`).toBeGreaterThanOrEqual(200)
  expect(response.status(), `${binding.action_id} response status`).toBeLessThan(400)
  const result = await response.json() as Json
  binding.method = method
  binding.path = new URL(response.url()).pathname.replace(/^\/api\/v1/, '')
  binding.status = response.status()
  binding.result = result
  return result
}

async function loginAndActivate(page: Page): Promise<void> {
  const activation = required('FPMS_DEMO_STRICT_ACTIVATION_URL')
  await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
  const loginName = page.locator('.el-form-item:has-text("用户名") input')
  await loginName.fill(required('FPMS_ADMIN_USERNAME'))
  await page.locator('.el-form-item:has-text("密码") input').fill(required('FPMS_ADMIN_PASSWORD'))
  const loginResponse = page.waitForResponse(response => (
    response.request().method() === 'POST' && new URL(response.url()).pathname === '/api/v1/auth/login'
  ))
  await page.getByRole('button', { name: '登 录' }).click()
  expect((await loginResponse).status()).toBe(200)
  await page.waitForLoadState('networkidle')
  await page.goto(`${baseUrl}/demo/inputs?fpmsObserverBinding=${encodeURIComponent(activation)}`, {
    waitUntil: 'networkidle',
  })
  await expect(page.getByRole('heading', { name: '演示输入与空业务库' })).toBeVisible()
  await page.getByTestId('demo-inputs-preflight').click()
  await expect(page.getByTestId('input-readiness')).toHaveText('READY')
  await expect(page.getByText('合成演示会话已通过当前预检绑定。')).toBeVisible()
}

async function captureStage(page: Page, stage: string): Promise<void> {
  await page.screenshot({
    path: path.join(required('FPMS_DEMO_EVIDENCE_DIR'), `stage-${stage}.png`),
  })
}

async function expandLifecycleHistory(page: Page): Promise<void> {
  const details = page.getByTestId('lifecycle-history-details')
  if (await details.count() === 0) {
    await page.getByTestId('lifecycle-history-toggle').click()
  }
  await expect(details).toBeVisible()
}

async function expectRawValueInAudit(container: Locator, rawText: string): Promise<void> {
  const rawValue = container.getByText(rawText, { exact: true })
  await expect(rawValue).toHaveCount(1)
  await expect(rawValue).toBeHidden()
  const audit = container.locator('details').filter({ hasText: rawText })
  await expect(audit).toHaveCount(1)
  await audit.locator('summary').click()
  await expect(rawValue).toBeVisible()
}

test('strict V6 normal-UI journey', async ({ page, browser }) => {
  test.setTimeout(9 * 60 * 1000)
  page.setDefaultTimeout(10_000)
  const consoleErrors: string[] = []
  const networkErrors: string[] = []
  const passiveMutations: Array<{ method: string; path: string; status: number }> = []
  let uiPhase = 'bootstrap'
  const requestPhases = new WeakMap<Request, string>()
  const observePage = (page: Page, pageLabel: string) => {
    page.on('request', observedRequest => requestPhases.set(observedRequest, uiPhase))
    page.on('console', message => {
      if (message.type() === 'error') {
        const location = message.location()
        consoleErrors.push(`${pageLabel}: ${message.text()} @ ${location.url}:${location.lineNumber}`)
      }
    })
    page.on('requestfailed', failed => {
      networkErrors.push(
        `${pageLabel}[${requestPhases.get(failed) || 'unknown'}]: ${failed.method()} ${failed.url()}: ${failed.failure()?.errorText || ''}`,
      )
    })
    page.on('response', response => {
      const method = response.request().method()
      const url = new URL(response.url())
      const readOnlyPost = url.pathname === '/api/v1/documents/impact-preview'
      if (
        ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)
        && url.pathname.startsWith('/api/v1/')
        && url.pathname !== '/api/v1/auth/login'
        && !readOnlyPost
      ) passiveMutations.push({ method, path: url.pathname.replace(/^\/api\/v1/, ''), status: response.status() })
    })
  }
  observePage(page, 'operator')

  await loginAndActivate(page)
  const captureStageButton = page.getByTestId('demo-v6-capture-stage')
  await expect(captureStageButton).toBeEnabled()
  expect(await captureStageButton.evaluate(button => {
    const bounds = button.getBoundingClientRect()
    const hitTarget = document.elementFromPoint(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2)
    return hitTarget === button || button.contains(hitTarget)
  })).toBe(true)
  const suffix = Date.now().toString().slice(-10)
  const customerName = '澄岳智造技术（苏州）有限公司'
  const caseNo = `CYIP-CN-INV-${suffix}`
  let currentClientId = ''
  let currentCaseId = ''
  let govDraftId = ''
  let serviceDraftId = ''
  let govObligationId = ''
  let originalServiceObligationId = ''
  let supersedingServiceObligationId = ''
  let payListId = 0
  let govFeeItemIds: string[] = []
  let govPaymentIds: number[] = []
  let billId = ''
  const customerPaymentIds: string[] = []
  const offsetIds: string[] = []
  let filingPackageId = ''
  let filingReceiptFilename = ''
  let oa1ChainIdentity: Json = {}
  let replacementGrantIdentity: Json = {}
  const bundleRoot = required('FPMS_DEMO_BUNDLE_PATH')
  const bundleManifest = JSON.parse(await readFile(path.join(bundleRoot, 'manifest.json'), 'utf8')) as Json
  const evidenceRows = bundleManifest.evidence as Json[]
  const oaReplyOutputs = JSON.parse(required('FPMS_DEMO_INTEGRATED_OA_REPLY_OUTPUT_JSON')) as Json[]
  const evidenceDescriptor = (role: string): Json => {
    const row = evidenceRows.find(candidate => candidate.role === role)
    expect(row, `bundle evidence role ${role}`).toBeTruthy()
    return row!
  }

  const createEvidenceDocument = async (
    title: string,
    documentDate: string,
    binding: ActionBinding,
    templateCode?: string,
    deadline?: {
      official_due_date: string
      official_due_date_source: string
      official_due_date_status: string
    },
    documentOptions?: {
      directionLabel: '收文' | '发文'
      typeLabel: '官方来文' | '官方去文'
      replySourceTitle?: string
    },
    templateAfterDeadline = false,
  ): Promise<string> => {
    await page.goto(
      `${baseUrl}/documents/new?case_id=${currentCaseId}&case_no=${encodeURIComponent(caseNo)}`,
      { waitUntil: 'networkidle' },
    )
    await page.getByRole('textbox', { name: '标题' }).fill(title)
    await page.getByRole('combobox', { name: '文件日期' }).fill(documentDate)
    if (documentOptions?.directionLabel === '发文') {
      await page.getByText('发文', { exact: true }).click()
    }
    const typeField = page.locator('.el-form-item').filter({ hasText: '文件类型' }).first()
    await typeField.locator('.el-select__wrapper').click()
    await page.getByRole('option', { name: documentOptions?.typeLabel || '官方来文', exact: true }).click()
    if (templateCode && !templateAfterDeadline) {
      const templateField = page.locator('.el-form-item').filter({ hasText: '文件模板' }).first()
      await templateField.locator('.el-select__wrapper').click()
      await page.getByRole('option').filter({ hasText: templateCode }).click()
    }
    if (documentOptions?.replySourceTitle) {
      const replySourceField = page.locator('.el-form-item').filter({ hasText: '回复来源文件' }).first()
      await replySourceField.locator('.el-select__wrapper').click()
      await page.getByRole('option').filter({ hasText: documentOptions.replySourceTitle }).click()
    }
    if (deadline) {
      await page.getByRole('combobox', { name: '官方截止日' }).fill(deadline.official_due_date)
      const sourceField = page.locator('.el-form-item').filter({ hasText: '截止日来源' }).first()
      await sourceField.locator('.el-select__wrapper').click()
      await page.getByRole('option', {
        name: deadline.official_due_date_source === 'IMPORTED_OFFICIAL_NOTICE'
          ? '从官方通知导入'
          : '人工核对官方通知',
        exact: true,
      }).click()
      const statusField = page.locator('.el-form-item').filter({ hasText: '确认状态' }).first()
      await statusField.locator('.el-select__wrapper').click()
      await page.getByRole('option', { name: '已确认', exact: true }).click()
    }
    if (templateCode && templateAfterDeadline) {
      const templateField = page.locator('.el-form-item').filter({ hasText: '文件模板' }).first()
      await templateField.locator('.el-select__wrapper').click()
      await page.getByRole('option').filter({ hasText: templateCode }).click()
    }
    const created = await visibleMutation(
      page,
      binding,
      page.getByRole('button', { name: '登记往来文件' }),
      'POST',
      /\/api\/v1\/documents$/,
    )
    const documentId = String(created.id)
    expect(documentId).toMatch(/^[0-9a-f-]{36}$/)
    await page.waitForURL(url => url.pathname === '/documents')
    const documentRow = page.getByRole('row').filter({ hasText: title })
    await expect(documentRow).toBeVisible()
    await documentRow.getByRole('button', { name: '查看' }).click()
    await page.waitForURL(url => url.pathname === `/documents/${documentId}`)
    await expect(page.getByRole('heading', { name: title })).toBeVisible()
    return documentId
  }

  const uploadAndReviewEvidence = async (
    documentId: string,
    descriptor: Json,
    officialRoleLabel: string,
    uploadBinding: ActionBinding,
    reviewBinding: ActionBinding,
    reviewerPage: Page,
  ): Promise<Json> => {
    const descriptorPath = String(descriptor.path)
    const filePath = path.isAbsolute(descriptorPath) ? descriptorPath : path.join(bundleRoot, descriptorPath)
    const fileName = path.basename(filePath)
    await page.getByTestId('attachment-open-upload').click()
    const uploadDialog = page.getByRole('dialog', { name: '上传附件' })
    await uploadDialog.getByTestId('attachment-file-picker').locator('input[type=file]').setInputFiles(filePath)
    await uploadDialog.locator('.el-form-item').filter({ hasText: '附件角色' }).locator('.el-select__wrapper').click()
    await page.getByRole('option', { name: officialRoleLabel, exact: true }).click()
    const uploaded = await visibleMutation(
      page,
      uploadBinding,
      uploadDialog.getByRole('button', { name: '确认上传' }),
      'POST',
      new RegExp(`/api/v1/documents/${documentId}/attachments$`),
    )
    expect(uploaded.content_hash).toBe(`sha256:${descriptor.sha256}`)
    const uploadedItem = page.locator('.attachment-item').filter({ hasText: fileName }).first()
    await expect(uploadedItem).toBeVisible()
    const uploadedTestId = await uploadedItem.getAttribute('data-testid')
    expect(uploadedTestId).toMatch(/^attachment-[0-9a-f-]{36}$/)
    const evidenceVersionId = String(uploadedTestId).replace('attachment-', '')
    expect(evidenceVersionId).toMatch(/^[0-9a-f-]{36}$/)
    await expect(page.getByTestId(`attachment-${evidenceVersionId}`)).toContainText(fileName)

    await reviewerPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'networkidle' })
    const reviewItem = reviewerPage.getByTestId(`attachment-${evidenceVersionId}`)
    await expect(reviewItem).toContainText(fileName)
    const reviewed = await visibleMutation(
      reviewerPage,
      reviewBinding,
      reviewItem.getByRole('button', { name: '通过' }),
      'POST',
      new RegExp(`/api/v1/documents/evidence-versions/${evidenceVersionId}/review$`),
    )
    expect(reviewed.review_state).toBe('APPROVED')
    await page.reload({ waitUntil: 'networkidle' })
    return {
      ...descriptor,
      attachment_id: String(uploaded.id),
      document_id: documentId,
      evidence_version_id: evidenceVersionId,
      filename: fileName,
    }
  }

  await test.step('01 客户、主联系人和案件', async () => {
    await page.goto(`${baseUrl}/clients/new`, { waitUntil: 'networkidle' })
    await page.getByRole('textbox', { name: '客户名称' }).fill(customerName)
    await page.getByRole('textbox', { name: '客户代码' }).fill(`CYZN-${suffix}`)
    await page.getByRole('textbox', { name: '邮箱' }).fill('customer@chengyue-ip.example')
    const customerBinding = bindStageAction('01', 'stage-01-create-customer', true)
    const customer = await visibleMutation(
      page,
      customerBinding,
      page.getByRole('button', { name: '创建客户' }),
      'POST',
      /\/api\/v1\/clients$/,
    )
    currentClientId = String(customer.id)
    expect(currentClientId).toMatch(/^[0-9a-f-]{36}$/)
    await page.waitForURL(url => url.pathname === '/clients')
    const customerRow = page.getByRole('row').filter({ hasText: customerName })
    await expect(customerRow).toBeVisible()
    await customerRow.getByRole('button', { name: `打开客户操作：${customerName}` }).click()
    await page.getByRole('menuitem', { name: '查看' }).click()
    await page.waitForURL(url => url.pathname === `/clients/${currentClientId}`)
    await expect(page.getByText(customerName, { exact: true })).toBeVisible()

    await page.getByRole('tab', { name: '联系人' }).click()
    await page.getByRole('button', { name: '新增联系人' }).click()
    const contactDialog = page.getByRole('dialog', { name: '新增联系人' })
    await contactDialog.getByRole('textbox', { name: '姓名' }).fill('周岚')
    await contactDialog.getByRole('textbox', { name: '职务' }).fill('知识产权经理')
    await contactDialog.getByRole('textbox', { name: '邮箱' }).fill('zhou.lan@chengyue-ip.example')
    await contactDialog.locator('.el-form-item').filter({ hasText: '主联系人' }).locator('.el-switch').click()
    const contactBinding = bindStageAction('01', 'stage-01-create-primary-contact', true)
    await visibleMutation(
      page,
      contactBinding,
      contactDialog.getByRole('button', { name: '确定' }),
      'POST',
      new RegExp(`/api/v1/clients/${currentClientId}/contacts$`),
    )
    await expect(page.getByRole('cell', { name: '周岚' })).toBeVisible()
    await expect(page.getByRole('cell', { name: '知识产权经理' })).toBeVisible()

    await page.goto(`${baseUrl}/cases/new`, { waitUntil: 'networkidle' })
    await page.getByRole('textbox', { name: '案号' }).fill(caseNo)
    await page.getByRole('textbox', { name: '标题' }).fill('一种柔性制造产线中视觉检测工位的自适应标定方法')
    await expectSelected(page, '案件类型', '普通案件')
    await expectSelected(page, '专利类别', '发明')
    await expectSelected(page, '流程方向', '中国国内')
    await selectFirstOption(page, '客户')
    await expectSelected(page, '客户', customerName)
    await page.getByText('控制标记', { exact: true }).click()
    const feeReductionField = page.locator('.el-form-item').filter({ hasText: '费用减缓比例' }).first()
    await feeReductionField.locator('.el-select__wrapper').click()
    await page.getByRole('option', { name: '不减免（0）', exact: true }).click()
    await expectSelected(page, '费用减缓比例', '不减免（0）')
    await page.getByText('申请人信息', { exact: true }).click()
    await page.getByRole('button', { name: '新增申请人' }).click()
    await selectFirstOption(page, '从客户主数据回填')
    await expectSelected(page, '从客户主数据回填', customerName)
    await expect(page.getByRole('checkbox', { name: '第一申请人' })).toBeChecked()
    const caseBinding = bindStageAction('01', 'stage-01-create-case', true)
    const createdCase = await visibleMutation(
      page,
      caseBinding,
      page.getByRole('button', { name: '创建案件' }),
      'POST',
      /\/api\/v1\/cases$/,
    )
    currentCaseId = String(createdCase.id)
    expect(currentCaseId).toMatch(/^[0-9a-f-]{36}$/)
    await page.waitForURL(url => url.pathname === '/cases')
    const caseRow = page.getByRole('row').filter({ hasText: caseNo })
    await expect(caseRow).toBeVisible()
    await caseRow.getByRole('button', { name: '查看' }).click()
    await page.waitForURL(url => url.pathname === `/cases/${currentCaseId}` || url.pathname === `/cases/no/${caseNo}`)
    await expect(page.getByLabel('概览').getByText(caseNo, { exact: true })).toBeVisible()
    await expect(page.getByText(customerName, { exact: true }).first()).toBeVisible()
    const applicantSection = page.getByRole('heading', { name: '官方提交主体信息' }).locator('..')
    await expect(applicantSection.getByText('申请人 1', { exact: true })).toBeVisible()
    await expect(applicantSection.getByText(`名称：${customerName}`, { exact: true })).toBeVisible()
    const primaryContactSection = page.getByRole('heading', { name: '客户主联系人' }).locator('..')
    await expect(primaryContactSection.getByText('姓名：周岚', { exact: true })).toBeVisible()
  })

  expect(passiveMutations).toEqual(actionBindings.map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '01')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-01-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('02 递交准备工作包与 60 项文书目录', async () => {
    const initialResolveBinding = bindStageAction('02', 'stage-02-resolve-filing-package', true)
    const initialResolve = await visibleMutation(
      page,
      initialResolveBinding,
      page.getByRole('button', { name: '申请前准备' }),
      'POST',
      /\/api\/v1\/cases\/[0-9a-f-]+\/official-work-packages\/filing-preparation\/resolve$/,
    )
    const initialPackage = initialResolve.package as Json
    filingPackageId = String(initialPackage.id)
    expect(filingPackageId).toMatch(/^[0-9a-f-]{36}$/)
    await expect(page.getByRole('heading', { name: '新申请递交准备' })).toBeVisible()
    await expect(page.getByText(`工作包 ${filingPackageId}`, { exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: '递交准备总览' })).toBeVisible()

    await page.getByRole('link', { name: '查看案件' }).click()
    await expect(page.getByLabel('概览').getByText(caseNo, { exact: true })).toBeVisible()
    const replayResolveBinding = bindStageAction('02', 'stage-02-replay-filing-package', true)
    const replayResolve = await visibleMutation(
      page,
      replayResolveBinding,
      page.getByRole('button', { name: '申请前准备' }),
      'POST',
      /\/api\/v1\/cases\/[0-9a-f-]+\/official-work-packages\/filing-preparation\/resolve$/,
    )
    expect(String((replayResolve.package as Json).id)).toBe(filingPackageId)
    await expect(page.getByText(`工作包 ${filingPackageId}`, { exact: true })).toBeVisible()

    await page.getByRole('link', { name: '往来文件', exact: true }).click()
    await expect(page.getByRole('heading', { name: '往来文件列表' })).toBeVisible()
    await page.getByRole('button', { name: '文书向导' }).click()
    await expect(page.getByRole('heading', { name: '中间文件向导' })).toBeVisible()
    const templateField = page.locator('.defaults-field').filter({ hasText: '文书模板' })
    await templateField.locator('.el-select__wrapper').click()
    const catalogOptions = page.getByRole('option').filter({ hasText: /OFFICIAL_NOTICE_/ })
    await expect(catalogOptions).toHaveCount(60)
    await expect(page.getByRole('option').filter({ hasText: /OFFICIAL_NOTICE_001/ })).toBeEnabled()
    await expect(page.getByRole('option').filter({ hasText: /OFFICIAL_NOTICE_010/ })).toBeDisabled()
  })

  expect(passiveMutations).toEqual(actionBindings.map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '02')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-02-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('03 人工递交、回执与受控审查证据', async () => {
    const reviewerContext = await browser.newContext()
    const reviewerPage = await reviewerContext.newPage()
    observePage(reviewerPage, 'stage-03-reviewer')
    await reviewerPage.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
    await reviewerPage.locator('.el-form-item:has-text("用户名") input').fill(required('FPMS_DEMO_REVIEWER_USERNAME'))
    await reviewerPage.locator('.el-form-item:has-text("密码") input').fill(required('FPMS_DEMO_REVIEWER_PASSWORD'))
    const reviewerLogin = reviewerPage.waitForResponse(response => (
      response.request().method() === 'POST' && new URL(response.url()).pathname === '/api/v1/auth/login'
    ))
    await reviewerPage.getByRole('button', { name: '登 录' }).click()
    expect((await reviewerLogin).status()).toBe(200)
    await reviewerPage.waitForLoadState('networkidle')

    const filingDescriptor = evidenceDescriptor('FILING_FINAL_SUBMISSION')
    const receiptDescriptor = evidenceDescriptor('FILING_RECEIPT')
    const filingDocumentId = await createEvidenceDocument(
      String(filingDescriptor.title_zh_cn),
      String((filingDescriptor.metadata as Json).effective_at).slice(0, 10),
      bindStageAction('03', 'stage-03-create-filing-document', true),
    )
    const filingEvidence = await uploadAndReviewEvidence(
      filingDocumentId,
      filingDescriptor,
      '合并PDF',
      bindStageAction('03', 'stage-03-upload-filing-evidence', true),
      bindStageAction('03', 'stage-03-review-filing-evidence', true),
      reviewerPage,
    )
    const receiptEvidence = await uploadAndReviewEvidence(
      filingDocumentId,
      receiptDescriptor,
      '电子申请回执',
      bindStageAction('03', 'stage-03-upload-filing-receipt-evidence', true),
      bindStageAction('03', 'stage-03-review-filing-receipt-evidence', true),
      reviewerPage,
    )
    filingReceiptFilename = String(receiptEvidence.filename)

    await page.goto(`${baseUrl}/official-workflows/filing-preparation?package_id=${filingPackageId}`, {
      waitUntil: 'networkidle',
    })
    const refreshBinding = bindStageAction('03', 'stage-03-refresh-reviewed-filing-package', true)
    const refreshedPackage = await visibleMutation(
      page,
      refreshBinding,
      page.getByRole('button', { name: '刷新工作包' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${filingPackageId}/filing-preparation/refresh$`),
    )
    const filingRole = (refreshedPackage.filing_file_roles as Json[]).find(row => row.official_file_role === 'FILING_MERGED_PDF')!
    expect(filingRole.content_hash).toBe(`sha256:${filingDescriptor.sha256}`)
    await expect(page.getByText(String(filingRole.attachment_id), { exact: true })).toBeVisible()
    await expect(page.getByText(`sha256:${String(filingDescriptor.sha256).slice(0, 7)}...`, { exact: true })).toBeVisible()
    await page.getByRole('combobox', { name: '人工递交时间' }).fill('2026-08-01 09:00:00')
    await page.getByRole('textbox', { name: '递交备注' }).fill('已完成人工递交')
    const submissionBinding = bindStageAction('03', 'stage-03-record-manual-submission', true)
    await visibleMutation(
      page,
      submissionBinding,
      page.getByRole('button', { name: '记录人工递交完成' }),
      'POST',
      /\/api\/v1\/official-work-packages\/[0-9a-f-]+\/filing-preparation\/external-operations$/,
    )
    await expect(page.getByText(
      '操作时间：2026-08-01 09:00:00；说明：已完成人工递交',
      { exact: true },
    ).first()).toBeVisible()

    const receiptPanel = page.locator('.receipt-archive-panel')
    const receiptFileField = receiptPanel.locator('.el-form-item').filter({ hasText: '回执文件' })
    await receiptFileField.locator('.el-select__wrapper').click()
    const receiptOption = page.getByRole('option').filter({ hasText: String(receiptEvidence.filename) })
    await expect(receiptOption).toBeVisible()
    await receiptOption.click()
    await receiptPanel.getByRole('textbox', { name: '接收案件编号' }).fill('CNIPA-20260802-001')
    await receiptPanel.getByRole('textbox', { name: '提交人' }).fill('陈思远')
    await receiptPanel.getByRole('combobox', { name: '接收时间' }).fill('2026-08-02 10:00:00')
    await receiptPanel.getByRole('textbox', { name: '收到文件清单' }).fill('发明专利请求书及申请文件')
    const receiptBinding = bindStageAction('03', 'stage-03-record-filing-receipt', true)
    await visibleMutation(
      page,
      receiptBinding,
      receiptPanel.getByRole('button', { name: '记录回执元数据' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${filingPackageId}/receipts$`),
    )
    await expect(receiptPanel.getByText('CNIPA-20260802-001', { exact: true })).toBeVisible()
    await expect(receiptPanel.getByText('陈思远', { exact: true })).toBeVisible()

    const lifecycleDefinitions = [
      {
        role: 'ACCEPTANCE_NOTICE', action: '记录受理通知', endpoint: 'acceptance-notice', template: 'OFFICIAL_NOTICE_001',
        createBinding: bindStageAction('03', 'stage-03-create-acceptance-document', true),
        uploadBinding: bindStageAction('03', 'stage-03-upload-acceptance-evidence', true),
        reviewBinding: bindStageAction('03', 'stage-03-review-acceptance-evidence', true),
        lifecycleBinding: bindStageAction('03', 'stage-03-record-acceptance', true),
        passBinding: undefined,
      },
      {
        role: 'PRELIMINARY_EXAMINATION_SOURCE', action: '开始初步审查', endpoint: 'preliminary-start',
        createBinding: bindStageAction('03', 'stage-03-create-preliminary-start-document', true),
        uploadBinding: bindStageAction('03', 'stage-03-upload-preliminary-start-evidence', true),
        reviewBinding: bindStageAction('03', 'stage-03-review-preliminary-start-evidence', true),
        lifecycleBinding: bindStageAction('03', 'stage-03-record-preliminary-start', true),
        passBinding: bindStageAction('03', 'stage-03-record-preliminary-pass', true),
      },
      {
        role: 'PUBLICATION_NOTICE', action: '记录公布通知', endpoint: 'publication-notice',
        createBinding: bindStageAction('03', 'stage-03-create-publication-document', true),
        uploadBinding: bindStageAction('03', 'stage-03-upload-publication-evidence', true),
        reviewBinding: bindStageAction('03', 'stage-03-review-publication-evidence', true),
        lifecycleBinding: bindStageAction('03', 'stage-03-record-publication', true),
        passBinding: undefined,
      },
      {
        role: 'SUBSTANTIVE_EXAMINATION_SOURCE', action: '开始实质审查', endpoint: 'substantive-start',
        createBinding: bindStageAction('03', 'stage-03-create-substantive-document', true),
        uploadBinding: bindStageAction('03', 'stage-03-upload-substantive-evidence', true),
        reviewBinding: bindStageAction('03', 'stage-03-review-substantive-evidence', true),
        lifecycleBinding: bindStageAction('03', 'stage-03-record-substantive', true),
        passBinding: undefined,
      },
    ]
    const lifecycleEvidence: Json[] = [filingEvidence, receiptEvidence]
    for (const definition of lifecycleDefinitions) {
      const descriptor = evidenceDescriptor(definition.role)
      const metadata = descriptor.metadata as Json
      const documentId = await createEvidenceDocument(
        String(descriptor.title_zh_cn),
        String(metadata.effective_at).slice(0, 10),
        definition.createBinding,
        definition.template,
      )
      const reviewedEvidence = await uploadAndReviewEvidence(
        documentId,
        descriptor,
        '官方通知书PDF',
        definition.uploadBinding,
        definition.reviewBinding,
        reviewerPage,
      )
      lifecycleEvidence.push(reviewedEvidence)
      const evidencePanel = page.locator('.lifecycle-evidence-actions')
      const evidenceField = evidencePanel.locator('.el-form-item').filter({ hasText: '证据文件' })
      await evidenceField.locator('.el-select__wrapper').click()
      await page.getByRole('option').filter({ hasText: String(reviewedEvidence.filename) }).click()
      const effectiveAtField = evidencePanel.getByRole('combobox', { name: '生效时间' })
      await effectiveAtField.fill(String(metadata.effective_at).replace('T', ' '))
      await effectiveAtField.press('Enter')
      const lifecycleAction = evidencePanel.getByRole('button', { name: definition.action })
      await expect(lifecycleAction).toBeEnabled()
      await visibleMutation(
        page,
        definition.lifecycleBinding,
        lifecycleAction,
        'POST',
        new RegExp(`/api/v1/documents/${documentId}/lifecycle/${definition.endpoint}$`),
      )
      if (definition.role === 'PRELIMINARY_EXAMINATION_SOURCE') {
        await visibleMutation(
          page,
          definition.passBinding!,
          evidencePanel.getByRole('button', { name: '记录初审通过' }),
          'POST',
          new RegExp(`/api/v1/documents/${documentId}/lifecycle/preliminary-pass$`),
        )
      }
    }

    await reviewerContext.close()
    await page.getByRole('link', { name: caseNo }).first().click()
    await page.waitForURL(url => url.pathname === `/cases/${currentCaseId}` || url.pathname === `/cases/no/${caseNo}`)
    await expandLifecycleHistory(page)
    const evidenceLane = page.getByTestId('document-evidence-lane')
    const evidenceMilestone = (label: string) => evidenceLane.locator('article').filter({
      hasText: `活动类型：${label}`,
    })
    const boundOutputs: Array<[string, Json | null]> = [
      ['申请文件已递交', filingEvidence],
      ['申请回执已归档', null],
      ['受理通知已登记', lifecycleEvidence[2]],
      ['初步审查已开始', lifecycleEvidence[3]],
      ['初步审查已通过', lifecycleEvidence[3]],
      ['公布通知已登记', lifecycleEvidence[4]],
      ['实质审查已开始', lifecycleEvidence[5]],
    ]
    for (const [label, evidence] of boundOutputs) {
      const milestone = evidenceMilestone(label)
      await expect(milestone).toBeVisible()
      await expect(milestone.getByText(`活动类型：${label}`, { exact: true })).toBeVisible()
      if (evidence) {
        await expectRawValueInAudit(milestone, `内容哈希：sha256:${evidence.sha256}`)
      }
    }
    await expect(page.getByLabel('当前案件生命周期状态')).toContainText('官方程序阶段：实质审查')
  })

  expect(passiveMutations).toEqual(actionBindings.map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '03')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-03-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('04 第一次审查意见答复链', async () => {
    uiPhase = 'stage-04-notice'
    const reviewerContext = await browser.newContext()
    const reviewerPage = await reviewerContext.newPage()
    observePage(reviewerPage, 'stage-04-reviewer')
    await reviewerPage.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
    await reviewerPage.locator('.el-form-item:has-text("用户名") input').fill(required('FPMS_DEMO_REVIEWER_USERNAME'))
    await reviewerPage.locator('.el-form-item:has-text("密码") input').fill(required('FPMS_DEMO_REVIEWER_PASSWORD'))
    const reviewerLogin = reviewerPage.waitForResponse(response => (
      response.request().method() === 'POST' && new URL(response.url()).pathname === '/api/v1/auth/login'
    ))
    await reviewerPage.getByRole('button', { name: '登 录' }).click()
    expect((await reviewerLogin).status()).toBe(200)

    const noticeDescriptor = evidenceDescriptor('OA_NOTICE_1')
    const noticeMetadata = noticeDescriptor.metadata as Json
    const noticeDocumentId = await createEvidenceDocument(
      String(noticeDescriptor.title_zh_cn),
      String(noticeMetadata.effective_at).slice(0, 10),
      bindStageAction('04', 'stage-04-create-oa1-notice-document', true),
      'OFFICIAL_NOTICE_003',
      {
        official_due_date: String(noticeMetadata.official_due_date),
        official_due_date_source: String(noticeMetadata.official_due_date_source),
        official_due_date_status: String(noticeMetadata.official_due_date_status),
      },
      undefined,
    )
    const noticeEvidence = await uploadAndReviewEvidence(
      noticeDocumentId,
      noticeDescriptor,
      '官方通知书PDF',
      bindStageAction('04', 'stage-04-upload-oa1-notice-evidence', true),
      bindStageAction('04', 'stage-04-review-oa1-notice-evidence', true),
      reviewerPage,
    )
    const noticePanel = page.locator('.lifecycle-evidence-actions')
    const noticeEvidenceField = noticePanel.locator('.el-form-item').filter({ hasText: '已复核证据版本' })
    await noticeEvidenceField.locator('.el-select__wrapper').click()
    await page.getByRole('option').filter({ hasText: String(noticeEvidence.filename) }).click()
    await expect(noticePanel.getByText(`内容摘要：sha256:${noticeEvidence.sha256}`, { exact: true })).toBeVisible()
    const noticeEffectiveAt = noticePanel.getByRole('combobox', { name: '生效时间' })
    await noticeEffectiveAt.fill(String(noticeMetadata.effective_at).replace('T', ' '))
    await noticeEffectiveAt.press('Enter')
    const noticeAction = noticePanel.getByRole('button', { name: '记录审查意见通知' })
    await expect(noticeAction).toBeEnabled()
    const recordedNotice = await visibleMutation(
      page,
      bindStageAction('04', 'stage-04-record-oa1-notice', true),
      noticeAction,
      'POST',
      new RegExp(`/api/v1/documents/${noticeDocumentId}/lifecycle/oa-notice$`),
    )
    expect(recordedNotice.oa_sequence).toBe(1)

    const resolvedPackage = await visibleMutation(
      page,
      bindStageAction('04', 'stage-04-resolve-oa1-package', true),
      page.getByRole('main').getByRole('link', { name: 'OA答复工作包' }),
      'POST',
      new RegExp(`/api/v1/official-documents/${noticeDocumentId}/official-work-packages/oa-reply/resolve$`),
    )
    const oaPackageId = String((resolvedPackage.package as Json).id)
    expect(oaPackageId).toMatch(/^[0-9a-f-]{36}$/)
    await expect(page.getByRole('heading', { name: 'OA答复工作包' })).toBeVisible()
    await expect(page.getByText(`工作包 ${oaPackageId}`, { exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: String(noticeDescriptor.title_zh_cn), level: 2 })).toBeVisible()
    await expect(page.getByText('2026-09-22', { exact: true })).toBeVisible()
    const initialReceiptField = page.locator('.receipt-archive-panel .el-form-item').filter({ hasText: '回执文件' })
    await initialReceiptField.locator('.el-select__wrapper').click()
    await expect(page.getByRole('option').filter({ hasText: filingReceiptFilename })).toBeVisible()
    await page.keyboard.press('Escape')

    const receiptDescriptor = evidenceDescriptor('OA_RECEIPT_1')
    const receiptMetadata = receiptDescriptor.metadata as Json
    const replyTitle = `第一次审查意见答复文件-${caseNo}`
    const replyDocumentId = await createEvidenceDocument(
      replyTitle,
      String(receiptMetadata.received_at).slice(0, 10),
      bindStageAction('04', 'stage-04-create-oa1-reply-document', true),
      'OA_OUT',
      undefined,
      {
        directionLabel: '发文',
        typeLabel: '官方去文',
        replySourceTitle: String(noticeDescriptor.title_zh_cn),
      },
    )
    const oa1OutputDescriptors = ['OA_STATEMENT_WORD', 'OA_STATEMENT_PDF', 'OA_MODIFIED_CLAIMS'].map(role => {
      const descriptor = oaReplyOutputs.find(row => row.oa_sequence === 1 && row.official_file_role === role)
      expect(descriptor, `OA1 output ${role}`).toBeTruthy()
      return descriptor!
    })
    const outputRoleLabels = ['OA意见陈述 Word', 'OA意见陈述 PDF', '修改后的权利要求书']
    const outputBindings = [
      {
        upload: bindStageAction('04', 'stage-04-upload-oa1-output-oa_statement_word-evidence', true),
        review: bindStageAction('04', 'stage-04-review-oa1-output-oa_statement_word-evidence', true),
      },
      {
        upload: bindStageAction('04', 'stage-04-upload-oa1-output-oa_statement_pdf-evidence', true),
        review: bindStageAction('04', 'stage-04-review-oa1-output-oa_statement_pdf-evidence', true),
      },
      {
        upload: bindStageAction('04', 'stage-04-upload-oa1-output-oa_modified_claims-evidence', true),
        review: bindStageAction('04', 'stage-04-review-oa1-output-oa_modified_claims-evidence', true),
      },
    ]
    const reviewedOutputs: Json[] = []
    for (let index = 0; index < oa1OutputDescriptors.length; index += 1) {
      reviewedOutputs.push(await uploadAndReviewEvidence(
        replyDocumentId,
        oa1OutputDescriptors[index],
        outputRoleLabels[index],
        outputBindings[index].upload,
        outputBindings[index].review,
        reviewerPage,
      ))
    }

    uiPhase = 'stage-04-reply-candidate'
    await page.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${oaPackageId}`, { waitUntil: 'networkidle' })
    const replyField = page.locator('.reply-selector .el-form-item').filter({ hasText: '答复文书' })
    await replyField.locator('.el-select__wrapper').click()
    const replyOptions = page.getByRole('option')
    await expect(replyOptions).toHaveCount(1)
    await expect(replyOptions.first()).toContainText(replyTitle)
    await replyOptions.first().click()
    const linkedReply = await visibleMutation(
      page,
      bindStageAction('04', 'stage-04-link-oa1-reply', true),
      page.getByRole('button', { name: '关联所选答复文书' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/oa-reply/reply-document$`),
    )
    expect(String((linkedReply.reply_document as Json).id)).toBe(replyDocumentId)

    const refreshButton = page.getByRole('button', { name: '刷新工作包' })
    const refreshedPackage = await visibleMutation(
      page,
      bindStageAction('04', 'stage-04-refresh-oa1-package', true),
      refreshButton,
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/oa-reply/refresh$`),
    )
    await expect(refreshButton).not.toHaveClass(/is-loading/)
    await page.waitForLoadState('networkidle')
    const refreshedRoles = refreshedPackage.oa_file_roles as Json[]
    const presentRoles = refreshedRoles
      .filter(row => row.present === true)
      .map(row => row.official_file_role)
      .sort()
    expect(presentRoles).toEqual(['OA_MODIFIED_CLAIMS', 'OA_STATEMENT_PDF', 'OA_STATEMENT_WORD'])
    const manifestPanel = page.locator('.oa-manifest-panel')
    const visibleOutputBindings = [
      { label: '意见陈述 Word', output: reviewedOutputs[0], card: true },
      { label: 'PDF保真附件', output: reviewedOutputs[1], card: true },
      { label: '修改后的权利要求书', output: reviewedOutputs[2], card: false },
    ]
    for (const [index, binding] of visibleOutputBindings.entries()) {
      const outputSurface = binding.card
        ? manifestPanel.locator('.attachment-card').filter({ hasText: binding.label })
        : manifestPanel.getByRole('row').filter({ hasText: String(binding.output.filename) })
      await expect(outputSurface).toContainText(String(binding.output.filename))
      await expect(outputSurface).toContainText('已满足')
      const roleRow = manifestPanel.getByRole('row').filter({ hasText: binding.label }).last()
      await expect(roleRow).toContainText('已匹配')
      const refreshedRole = refreshedRoles.find(row => row.official_file_role === oa1OutputDescriptors[index].official_file_role)
      expect(String(refreshedRole?.attachment_id)).toBe(String(binding.output.attachment_id))
      await expect(roleRow).toContainText(String(binding.output.attachment_id))
    }

    for (const checklist of [
      { label: '确认陈述意见文本', binding: bindStageAction('04', 'stage-04-确认陈述意见文本', true) },
      { label: '确认PDF保真附件', binding: bindStageAction('04', 'stage-04-确认PDF保真附件', true) },
      { label: '确认修改文件', binding: bindStageAction('04', 'stage-04-确认修改文件', true) },
      { label: '确认实验数据标记', binding: bindStageAction('04', 'stage-04-确认实验数据标记', true) },
      { label: '确认官方页面预览', binding: bindStageAction('04', 'stage-04-确认官方页面预览', true) },
      { label: '确认签名与提交', binding: bindStageAction('04', 'stage-04-确认签名与提交', true) },
    ]) {
      const checklistResult = await visibleMutation(
        page,
        checklist.binding,
        page.getByRole('button', { name: checklist.label, exact: true }),
        'PATCH',
        new RegExp(`/api/v1/official-work-packages/${oaPackageId}/oa-reply/checklist/[A-Z_]+$`),
      )
      expect((checklistResult.checklist_item as Json).status).toBe('DONE')
    }

    uiPhase = 'stage-04-receipt-document'
    await page.goto(`${baseUrl}/documents/${replyDocumentId}`, { waitUntil: 'networkidle' })
    const receiptEvidence = await uploadAndReviewEvidence(
      replyDocumentId,
      receiptDescriptor,
      '电子申请回执',
      bindStageAction('04', 'stage-04-upload-oa1-receipt-evidence', true),
      bindStageAction('04', 'stage-04-review-oa1-receipt-evidence', true),
      reviewerPage,
    )
    uiPhase = 'stage-04-receipt-package'
    await page.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${oaPackageId}`, { waitUntil: 'networkidle' })
    const receiptPanel = page.locator('.receipt-archive-panel')
    const receiptFileField = receiptPanel.locator('.el-form-item').filter({ hasText: '回执文件' })
    await receiptFileField.locator('.el-select__wrapper').click()
    await page.getByRole('option').filter({ hasText: String(receiptEvidence.filename) }).click()
    await receiptPanel.getByRole('textbox', { name: '接收案件编号' }).fill('CNIPA-20260808-001')
    await receiptPanel.getByRole('textbox', { name: '提交人' }).fill('陈思远')
    const receiptReceivedAt = receiptPanel.getByRole('combobox', { name: '接收时间' })
    await receiptReceivedAt.fill(String(receiptMetadata.received_at).replace('T', ' '))
    await receiptReceivedAt.press('Enter')
    await receiptPanel.getByRole('textbox', { name: '收到文件清单' }).fill(
      '第一次审查意见答复_意见陈述书\n第一次审查意见答复_修改后权利要求书',
    )
    const receiptResult = await visibleMutation(
      page,
      bindStageAction('04', 'stage-04-record-oa1-receipt', true),
      receiptPanel.getByRole('button', { name: '记录回执元数据' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/receipts$`),
    )
    expect(String(receiptResult.receipt_attachment_id)).toBe(String(receiptEvidence.attachment_id))
    await expect(receiptPanel.getByText('CNIPA-20260808-001', { exact: true })).toBeVisible()
    await expect(receiptPanel.getByText('陈思远', { exact: true })).toBeVisible()

    uiPhase = 'stage-04-archive'
    const archiveResult = await visibleMutation(
      page,
      bindStageAction('04', 'stage-04-archive-oa1-package', true),
      receiptPanel.getByRole('button', { name: '提交归档检查' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/archive$`),
    )
    expect((archiveResult.package as Json).status).toBe('ARCHIVED')
    expect((archiveResult.evaluation as Json).can_archive).toBe(true)
    oa1ChainIdentity = {
      source_document_id: noticeDocumentId,
      package_id: oaPackageId,
      reply_document_id: replyDocumentId,
      receipt_id: String(receiptResult.id),
    }
    await expect(page.locator('.case-header').getByText('已归档', { exact: true })).toBeVisible()
    const archivedReceiptField = page.locator('.receipt-archive-panel .el-form-item').filter({ hasText: '回执文件' })
    await archivedReceiptField.locator('.el-select__wrapper').click()
    await expect(page.getByRole('option').filter({ hasText: String(receiptEvidence.filename) })).toBeVisible()
    await page.keyboard.press('Escape')
    await page.waitForLoadState('networkidle')
    await reviewerContext.close()

    uiPhase = 'stage-04-case-detail'
    await page.getByRole('link', { name: '查看案件' }).click()
    await page.waitForURL(url => url.pathname === `/cases/${currentCaseId}`)
    await expandLifecycleHistory(page)
    const evidenceLane = page.getByTestId('document-evidence-lane')
    const noticeMilestone = evidenceLane.locator('article').filter({ hasText: '活动类型：审查意见通知已登记' })
    await expectRawValueInAudit(noticeMilestone, `内容哈希：sha256:${noticeEvidence.sha256}`)
    await expect(noticeMilestone.getByRole('heading', { name: '关联任务' })).toHaveCount(1)
    const receiptMilestone = evidenceLane.locator('article').filter({ hasText: '活动类型：审查意见答复回执已归档' })
    await expect(receiptMilestone).toBeVisible()
    await page.waitForLoadState('networkidle')
  })

  expect(passiveMutations).toEqual(actionBindings.map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '04')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-04-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('05 第二次审查意见答复链', async () => {
    uiPhase = 'stage-05-notice'
    const reviewerContext = await browser.newContext()
    const reviewerPage = await reviewerContext.newPage()
    observePage(reviewerPage, 'stage-05-reviewer')
    await reviewerPage.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
    await reviewerPage.locator('.el-form-item:has-text("用户名") input').fill(required('FPMS_DEMO_REVIEWER_USERNAME'))
    await reviewerPage.locator('.el-form-item:has-text("密码") input').fill(required('FPMS_DEMO_REVIEWER_PASSWORD'))
    const reviewerLogin = reviewerPage.waitForResponse(response => (
      response.request().method() === 'POST' && new URL(response.url()).pathname === '/api/v1/auth/login'
    ))
    await reviewerPage.getByRole('button', { name: '登 录' }).click()
    expect((await reviewerLogin).status()).toBe(200)

    const noticeDescriptor = evidenceDescriptor('OA_NOTICE_2')
    const noticeMetadata = noticeDescriptor.metadata as Json
    const noticeDocumentId = await createEvidenceDocument(
      String(noticeDescriptor.title_zh_cn),
      String(noticeMetadata.effective_at).slice(0, 10),
      bindStageAction('05', 'stage-05-create-oa2-notice-document', true),
      'OFFICIAL_NOTICE_005',
      {
        official_due_date: String(noticeMetadata.official_due_date),
        official_due_date_source: String(noticeMetadata.official_due_date_source),
        official_due_date_status: String(noticeMetadata.official_due_date_status),
      },
      undefined,
    )
    const noticeEvidence = await uploadAndReviewEvidence(
      noticeDocumentId,
      noticeDescriptor,
      '官方通知书PDF',
      bindStageAction('05', 'stage-05-upload-oa2-notice-evidence', true),
      bindStageAction('05', 'stage-05-review-oa2-notice-evidence', true),
      reviewerPage,
    )
    const noticePanel = page.locator('.lifecycle-evidence-actions')
    const noticeEvidenceField = noticePanel.locator('.el-form-item').filter({ hasText: '已复核证据版本' })
    await noticeEvidenceField.locator('.el-select__wrapper').click()
    await page.getByRole('option').filter({ hasText: String(noticeEvidence.filename) }).click()
    await expect(noticePanel.getByText(`内容摘要：sha256:${noticeEvidence.sha256}`, { exact: true })).toBeVisible()
    const noticeEffectiveAt = noticePanel.getByRole('combobox', { name: '生效时间' })
    await noticeEffectiveAt.fill(String(noticeMetadata.effective_at).replace('T', ' '))
    await noticeEffectiveAt.press('Enter')
    const noticeAction = noticePanel.getByRole('button', { name: '记录审查意见通知' })
    await expect(noticeAction).toBeEnabled()
    const recordedNotice = await visibleMutation(
      page,
      bindStageAction('05', 'stage-05-record-oa2-notice', true),
      noticeAction,
      'POST',
      new RegExp(`/api/v1/documents/${noticeDocumentId}/lifecycle/oa-notice$`),
    )
    expect(recordedNotice.oa_sequence).toBe(2)

    const resolvedPackage = await visibleMutation(
      page,
      bindStageAction('05', 'stage-05-resolve-oa2-package', true),
      page.getByRole('main').getByRole('link', { name: 'OA答复工作包' }),
      'POST',
      new RegExp(`/api/v1/official-documents/${noticeDocumentId}/official-work-packages/oa-reply/resolve$`),
    )
    const oaPackageId = String((resolvedPackage.package as Json).id)
    expect(oaPackageId).toMatch(/^[0-9a-f-]{36}$/)
    expect(oaPackageId).not.toBe(String(oa1ChainIdentity.package_id))
    await expect(page.getByRole('heading', { name: 'OA答复工作包' })).toBeVisible()
    await expect(page.getByText(`工作包 ${oaPackageId}`, { exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: String(noticeDescriptor.title_zh_cn), level: 2 })).toBeVisible()
    await expect(page.getByText('2026-10-23', { exact: true })).toBeVisible()
    const initialReceiptField = page.locator('.receipt-archive-panel .el-form-item').filter({ hasText: '回执文件' })
    await initialReceiptField.locator('.el-select__wrapper').click()
    await expect(page.getByRole('option').filter({ hasText: filingReceiptFilename })).toBeVisible()
    await page.keyboard.press('Escape')

    const receiptDescriptor = evidenceDescriptor('OA_RECEIPT_2')
    const receiptMetadata = receiptDescriptor.metadata as Json
    const replyTitle = `第二次审查意见答复文件-${caseNo}`
    const replyDocumentId = await createEvidenceDocument(
      replyTitle,
      String(receiptMetadata.received_at).slice(0, 10),
      bindStageAction('05', 'stage-05-create-oa2-reply-document', true),
      'OA_OUT',
      undefined,
      {
        directionLabel: '发文',
        typeLabel: '官方去文',
        replySourceTitle: String(noticeDescriptor.title_zh_cn),
      },
    )
    const outputDescriptors = ['OA_STATEMENT_WORD', 'OA_STATEMENT_PDF', 'OA_MODIFIED_CLAIMS'].map(role => {
      const descriptor = oaReplyOutputs.find(row => row.oa_sequence === 2 && row.official_file_role === role)
      expect(descriptor, `OA2 output ${role}`).toBeTruthy()
      return descriptor!
    })
    const outputRoleLabels = ['OA意见陈述 Word', 'OA意见陈述 PDF', '修改后的权利要求书']
    const outputBindings = [
      {
        upload: bindStageAction('05', 'stage-05-upload-oa2-output-oa_statement_word-evidence', true),
        review: bindStageAction('05', 'stage-05-review-oa2-output-oa_statement_word-evidence', true),
      },
      {
        upload: bindStageAction('05', 'stage-05-upload-oa2-output-oa_statement_pdf-evidence', true),
        review: bindStageAction('05', 'stage-05-review-oa2-output-oa_statement_pdf-evidence', true),
      },
      {
        upload: bindStageAction('05', 'stage-05-upload-oa2-output-oa_modified_claims-evidence', true),
        review: bindStageAction('05', 'stage-05-review-oa2-output-oa_modified_claims-evidence', true),
      },
    ]
    const reviewedOutputs: Json[] = []
    for (let index = 0; index < outputDescriptors.length; index += 1) {
      reviewedOutputs.push(await uploadAndReviewEvidence(
        replyDocumentId,
        outputDescriptors[index],
        outputRoleLabels[index],
        outputBindings[index].upload,
        outputBindings[index].review,
        reviewerPage,
      ))
    }

    uiPhase = 'stage-05-reply-candidate'
    await page.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${oaPackageId}`, { waitUntil: 'networkidle' })
    const replyField = page.locator('.reply-selector .el-form-item').filter({ hasText: '答复文书' })
    await replyField.locator('.el-select__wrapper').click()
    const replyOptions = page.getByRole('option')
    await expect(replyOptions).toHaveCount(1)
    await expect(replyOptions.first()).toContainText(replyTitle)
    await replyOptions.first().click()
    const linkedReply = await visibleMutation(
      page,
      bindStageAction('05', 'stage-05-link-oa2-reply', true),
      page.getByRole('button', { name: '关联所选答复文书' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/oa-reply/reply-document$`),
    )
    expect(String((linkedReply.reply_document as Json).id)).toBe(replyDocumentId)

    const refreshButton = page.getByRole('button', { name: '刷新工作包' })
    const refreshedPackage = await visibleMutation(
      page,
      bindStageAction('05', 'stage-05-refresh-oa2-package', true),
      refreshButton,
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/oa-reply/refresh$`),
    )
    await expect(refreshButton).not.toHaveClass(/is-loading/)
    await page.waitForLoadState('networkidle')
    const refreshedRoles = refreshedPackage.oa_file_roles as Json[]
    expect(refreshedRoles.filter(row => row.present === true).map(row => row.official_file_role).sort()).toEqual(
      ['OA_MODIFIED_CLAIMS', 'OA_STATEMENT_PDF', 'OA_STATEMENT_WORD'],
    )
    const manifestPanel = page.locator('.oa-manifest-panel')
    const visibleOutputBindings = [
      { label: '意见陈述 Word', output: reviewedOutputs[0], card: true },
      { label: 'PDF保真附件', output: reviewedOutputs[1], card: true },
      { label: '修改后的权利要求书', output: reviewedOutputs[2], card: false },
    ]
    for (const [index, binding] of visibleOutputBindings.entries()) {
      const outputSurface = binding.card
        ? manifestPanel.locator('.attachment-card').filter({ hasText: binding.label })
        : manifestPanel.getByRole('row').filter({ hasText: String(binding.output.filename) })
      await expect(outputSurface).toContainText(String(binding.output.filename))
      await expect(outputSurface).toContainText('已满足')
      const roleRow = manifestPanel.getByRole('row').filter({ hasText: binding.label }).last()
      await expect(roleRow).toContainText('已匹配')
      const refreshedRole = refreshedRoles.find(row => row.official_file_role === outputDescriptors[index].official_file_role)
      expect(String(refreshedRole?.attachment_id)).toBe(String(binding.output.attachment_id))
      await expect(roleRow).toContainText(String(binding.output.attachment_id))
    }

    for (const checklist of [
      { label: '确认陈述意见文本', binding: bindStageAction('05', 'stage-05-确认陈述意见文本', true) },
      { label: '确认PDF保真附件', binding: bindStageAction('05', 'stage-05-确认PDF保真附件', true) },
      { label: '确认修改文件', binding: bindStageAction('05', 'stage-05-确认修改文件', true) },
      { label: '确认实验数据标记', binding: bindStageAction('05', 'stage-05-确认实验数据标记', true) },
      { label: '确认官方页面预览', binding: bindStageAction('05', 'stage-05-确认官方页面预览', true) },
      { label: '确认签名与提交', binding: bindStageAction('05', 'stage-05-确认签名与提交', true) },
    ]) {
      const checklistResult = await visibleMutation(
        page,
        checklist.binding,
        page.getByRole('button', { name: checklist.label, exact: true }),
        'PATCH',
        new RegExp(`/api/v1/official-work-packages/${oaPackageId}/oa-reply/checklist/[A-Z_]+$`),
      )
      expect((checklistResult.checklist_item as Json).status).toBe('DONE')
    }

    uiPhase = 'stage-05-receipt-document'
    await page.goto(`${baseUrl}/documents/${replyDocumentId}`, { waitUntil: 'networkidle' })
    const receiptEvidence = await uploadAndReviewEvidence(
      replyDocumentId,
      receiptDescriptor,
      '电子申请回执',
      bindStageAction('05', 'stage-05-upload-oa2-receipt-evidence', true),
      bindStageAction('05', 'stage-05-review-oa2-receipt-evidence', true),
      reviewerPage,
    )
    uiPhase = 'stage-05-receipt-package'
    await page.goto(`${baseUrl}/official-workflows/oa-reply?package_id=${oaPackageId}`, { waitUntil: 'networkidle' })
    const receiptPanel = page.locator('.receipt-archive-panel')
    const receiptFileField = receiptPanel.locator('.el-form-item').filter({ hasText: '回执文件' })
    await receiptFileField.locator('.el-select__wrapper').click()
    await page.getByRole('option').filter({ hasText: String(receiptEvidence.filename) }).click()
    await receiptPanel.getByRole('textbox', { name: '接收案件编号' }).fill('CNIPA-20260810-001')
    await receiptPanel.getByRole('textbox', { name: '提交人' }).fill('陈思远')
    const receiptReceivedAt = receiptPanel.getByRole('combobox', { name: '接收时间' })
    await receiptReceivedAt.fill(String(receiptMetadata.received_at).replace('T', ' '))
    await receiptReceivedAt.press('Enter')
    await receiptPanel.getByRole('textbox', { name: '收到文件清单' }).fill(
      '第二次审查意见答复_意见陈述书\n第二次审查意见答复_修改后权利要求书',
    )
    const receiptResult = await visibleMutation(
      page,
      bindStageAction('05', 'stage-05-record-oa2-receipt', true),
      receiptPanel.getByRole('button', { name: '记录回执元数据' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/receipts$`),
    )
    expect(String(receiptResult.receipt_attachment_id)).toBe(String(receiptEvidence.attachment_id))
    expect(String(receiptResult.id)).not.toBe(String(oa1ChainIdentity.receipt_id))
    await expect(receiptPanel.getByText('CNIPA-20260810-001', { exact: true })).toBeVisible()
    await expect(receiptPanel.getByText('陈思远', { exact: true })).toBeVisible()

    uiPhase = 'stage-05-archive'
    const archiveResult = await visibleMutation(
      page,
      bindStageAction('05', 'stage-05-archive-oa2-package', true),
      receiptPanel.getByRole('button', { name: '提交归档检查' }),
      'POST',
      new RegExp(`/api/v1/official-work-packages/${oaPackageId}/archive$`),
    )
    expect((archiveResult.package as Json).status).toBe('ARCHIVED')
    expect((archiveResult.evaluation as Json).can_archive).toBe(true)
    expect(noticeDocumentId).not.toBe(String(oa1ChainIdentity.source_document_id))
    expect(replyDocumentId).not.toBe(String(oa1ChainIdentity.reply_document_id))
    await expect(page.locator('.case-header').getByText('已归档', { exact: true })).toBeVisible()
    const archivedReceiptField = page.locator('.receipt-archive-panel .el-form-item').filter({ hasText: '回执文件' })
    await archivedReceiptField.locator('.el-select__wrapper').click()
    await expect(page.getByRole('option').filter({ hasText: String(receiptEvidence.filename) })).toBeVisible()
    await page.keyboard.press('Escape')
    await page.waitForLoadState('networkidle')
    await reviewerContext.close()

    uiPhase = 'stage-05-case-detail'
    await page.getByRole('link', { name: '查看案件' }).click()
    await page.waitForURL(url => url.pathname === `/cases/${currentCaseId}`)
    await expandLifecycleHistory(page)
    const evidenceLane = page.getByTestId('document-evidence-lane')
    const noticeMilestones = evidenceLane.locator('article').filter({ hasText: '活动类型：审查意见通知已登记' })
    await expect(noticeMilestones).toHaveCount(2)
    const oa1Notice = noticeMilestones.filter({ hasText: `内容哈希：sha256:${evidenceDescriptor('OA_NOTICE_1').sha256}` })
    const oa2Notice = noticeMilestones.filter({ hasText: `内容哈希：sha256:${noticeEvidence.sha256}` })
    await expect(oa1Notice).toBeVisible()
    await expect(oa2Notice).toBeVisible()
    await expect(oa1Notice.getByRole('heading', { name: '关联任务' })).toHaveCount(1)
    await expect(oa2Notice.getByRole('heading', { name: '关联任务' })).toHaveCount(1)
    const receiptMilestones = evidenceLane.locator('article').filter({ hasText: '活动类型：审查意见答复回执已归档' })
    await expect(receiptMilestones).toHaveCount(2)
    await page.waitForLoadState('networkidle')
  })

  expect(passiveMutations).toEqual(actionBindings.map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '05')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-05-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('06 原授权通知证据', async () => {
    uiPhase = 'stage-06-original-grant'
    const reviewerContext = await browser.newContext()
    const reviewerPage = await reviewerContext.newPage()
    observePage(reviewerPage, 'stage-06-reviewer')
    await reviewerPage.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
    await reviewerPage.locator('.el-form-item:has-text("用户名") input').fill(required('FPMS_DEMO_REVIEWER_USERNAME'))
    await reviewerPage.locator('.el-form-item:has-text("密码") input').fill(required('FPMS_DEMO_REVIEWER_PASSWORD'))
    const reviewerLogin = reviewerPage.waitForResponse(response => (
      response.request().method() === 'POST' && new URL(response.url()).pathname === '/api/v1/auth/login'
    ))
    await reviewerPage.getByRole('button', { name: '登 录' }).click()
    expect((await reviewerLogin).status()).toBe(200)

    const originalDescriptor = evidenceDescriptor('GRANT_NOTICE_ORIGINAL')
    const originalMetadata = originalDescriptor.metadata as Json
    const originalDocumentId = await createEvidenceDocument(
      String(originalDescriptor.title_zh_cn),
      String(originalMetadata.effective_at).slice(0, 10),
      bindStageAction('06', 'stage-06-create-original-grant-notice-document', true),
      'OFFICIAL_NOTICE_009',
      {
        official_due_date: String(originalMetadata.official_due_date),
        official_due_date_source: String(originalMetadata.official_due_date_source),
        official_due_date_status: String(originalMetadata.official_due_date_status),
      },
      undefined,
      true,
    )
    const originalEvidence = await uploadAndReviewEvidence(
      originalDocumentId,
      originalDescriptor,
      '官方通知书PDF',
      bindStageAction('06', 'stage-06-upload-original-grant-notice-evidence', true),
      bindStageAction('06', 'stage-06-review-original-grant-notice-evidence', true),
      reviewerPage,
    )

    await page.goto(`${baseUrl}/grant-fee/tasks`, { waitUntil: 'networkidle' })
    await page.getByPlaceholder('请输入案件编号').fill(caseNo)
    await page.getByRole('button', { name: '查询', exact: true }).click()
    const originalTaskRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-23' })
    await expect(originalTaskRow).toHaveCount(1)
    await expect(originalTaskRow).toContainText(originalDocumentId)
    await originalTaskRow.getByRole('button', { name: '选择授权通知证据' }).click()
    const evidenceDialog = page.getByRole('dialog', { name: '选择授权通知证据' })
    await expect(evidenceDialog.getByRole('heading', { name: '授权通知证据' })).toBeVisible()
    const evidenceField = evidenceDialog.locator('.el-form-item').filter({ hasText: '证据文件' })
    await evidenceField.locator('.el-select__wrapper').click()
    await page.getByRole('option').filter({ hasText: String(originalEvidence.filename) }).click()
    await expect(evidenceDialog.getByText(`内容摘要：sha256:${originalEvidence.sha256}`, { exact: true })).toBeVisible()
    const recordedAt = evidenceDialog.getByRole('combobox', { name: '授权通知记录时间' })
    await recordedAt.fill(String(originalMetadata.effective_at).replace('T', ' '))
    await recordedAt.press('Enter')
    const recordedOriginal = await visibleMutation(
      page,
      bindStageAction('06', 'stage-06-record-original-grant-notice', true),
      evidenceDialog.getByRole('button', { name: '确认授权通知证据' }),
      'POST',
      /\/api\/v1\/grant-fee-tasks\/[0-9a-f-]+\/lifecycle\/grant-notice$/,
    )
    expect(recordedOriginal).toMatchObject({
      event_type: 'GRANT_REGISTRATION_NOTICE_RECORDED',
      reused: false,
    })
    await expect(evidenceDialog).not.toBeVisible()

    const replacementDescriptor = evidenceDescriptor('GRANT_NOTICE_REPLACEMENT')
    const replacementMetadata = replacementDescriptor.metadata as Json
    const refreshedOriginalTaskRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-23' })
    await expect(refreshedOriginalTaskRow).toHaveCount(1)
    await refreshedOriginalTaskRow.getByRole('button', { name: '更正通知' }).click()
    const replacementDialog = page.getByRole('dialog', { name: '登记更正授权通知' })
    await expect(replacementDialog).toBeVisible()
    const replacementTemplateField = replacementDialog.locator('.el-form-item').filter({ hasText: '文书模板' })
    await replacementTemplateField.locator('.el-select__wrapper').click()
    await page.getByRole('option').filter({ hasText: 'OFFICIAL_NOTICE_009' }).click()
    await replacementDialog.getByRole('combobox', { name: '文书日期' }).fill('2026-08-12')
    await replacementDialog.getByRole('textbox', { name: '文号' }).fill(`BDJ-${caseNo}-02`)
    await replacementDialog.getByRole('textbox', { name: '标题' }).fill(String(replacementDescriptor.title_zh_cn))
    await replacementDialog.getByRole('combobox', { name: '官方期限' }).fill('2026-11-24')
    const replacementSourceField = replacementDialog.locator('.el-form-item').filter({ hasText: '期限来源' })
    await replacementSourceField.locator('.el-select__wrapper').click()
    await page.getByRole('option', {
      name: String(replacementMetadata.official_due_date_source) === 'IMPORTED_OFFICIAL_NOTICE'
        ? '导入官方通知'
        : '人工核对官方通知',
      exact: true,
    }).click()
    await replacementDialog.getByRole('textbox', { name: '替换原因' }).fill('依据更正通知更新办理登记手续期限')
    await replacementDialog.getByRole('textbox', { name: '去重键' }).fill(`grant-replacement-${suffix}`)
    const replaced = await visibleMutation(
      page,
      bindStageAction('06', 'stage-06-create-replacement-grant-notice', true),
      replacementDialog.getByRole('button', { name: '提交更正通知' }),
      'POST',
      /\/api\/v1\/grant-fee-tasks\/[0-9a-f-]+\/replacement-notice$/,
    )
    expect(String(replaced.document?.id)).toMatch(/^[0-9a-f-]{36}$/)
    expect(String(replaced.superseded_task_id)).toMatch(/^[0-9a-f-]{36}$/)
    expect(String(replaced.replacement_task?.source_document_id)).toBe(String(replaced.document?.id))
    expect(String(replaced.replacement_task?.due_date)).toBe('2026-11-24')
    expect(replaced.reused).toBe(false)
    await expect(replacementDialog).not.toBeVisible()
    const supersededOriginalRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-23' })
    const currentReplacementRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-24' })
    await expect(supersededOriginalRow).toContainText('来源未确认、已被替代或状态已变化，仅可查看')
    await expect(supersededOriginalRow.getByRole('button')).toHaveCount(0)
    await expect(currentReplacementRow).toHaveCount(1)
    await expect(currentReplacementRow).toContainText(String(replaced.document?.id))

    const replacementDocumentId = String(replaced.document?.id)
    await page.goto(`${baseUrl}/documents/${replacementDocumentId}`, { waitUntil: 'networkidle' })
    await expect(page.getByRole('heading', { name: String(replacementDescriptor.title_zh_cn) })).toBeVisible()
    const replacementEvidence = await uploadAndReviewEvidence(
      replacementDocumentId,
      replacementDescriptor,
      '官方通知书PDF',
      bindStageAction('06', 'stage-06-upload-replacement-grant-notice-evidence', true),
      bindStageAction('06', 'stage-06-review-replacement-grant-notice-evidence', true),
      reviewerPage,
    )
    replacementGrantIdentity = {
      task_id: String(replaced.replacement_task?.task_id),
      document_id: replacementDocumentId,
      evidence_version_id: String(replacementEvidence.evidence_version_id),
      evidence_sha256: String(replacementEvidence.sha256),
    }

    await page.goto(`${baseUrl}/grant-fee/tasks`, { waitUntil: 'networkidle' })
    await page.getByPlaceholder('请输入案件编号').fill(caseNo)
    await page.getByRole('button', { name: '查询', exact: true }).click()
    const replacementTaskRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-24' })
    await expect(replacementTaskRow).toHaveCount(1)
    await replacementTaskRow.getByRole('button', { name: '选择授权通知证据' }).click()
    const replacementEvidenceDialog = page.getByRole('dialog', { name: '选择授权通知证据' })
    const replacementEvidenceField = replacementEvidenceDialog.locator('.el-form-item').filter({ hasText: '证据文件' })
    await replacementEvidenceField.locator('.el-select__wrapper').click()
    await page.getByRole('option').filter({ hasText: String(replacementEvidence.filename) }).click()
    await expect(replacementEvidenceDialog.getByText(
      `内容摘要：sha256:${replacementEvidence.sha256}`,
      { exact: true },
    )).toBeVisible()
    const replacementRecordedAt = replacementEvidenceDialog.getByRole('combobox', { name: '授权通知记录时间' })
    await replacementRecordedAt.fill(String(replacementMetadata.effective_at).replace('T', ' '))
    await replacementRecordedAt.press('Enter')
    const recordedReplacement = await visibleMutation(
      page,
      bindStageAction('06', 'stage-06-record-replacement-grant-notice', true),
      replacementEvidenceDialog.getByRole('button', { name: '确认授权通知证据' }),
      'POST',
      /\/api\/v1\/grant-fee-tasks\/[0-9a-f-]+\/lifecycle\/grant-notice$/,
    )
    expect(recordedReplacement).toMatchObject({
      event_type: 'GRANT_REGISTRATION_NOTICE_RECORDED',
      reused: false,
    })
    await expect(replacementEvidenceDialog).not.toBeVisible()

    const actionableReplacementRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-24' })
    const waitingResult = await visibleMutation(
      page,
      bindStageAction('06', 'stage-06-mark-replacement-waiting-client', true),
      actionableReplacementRow.getByRole('button', { name: '标记等待客户' }),
      'PUT',
      /\/api\/v1\/grant-fee-tasks\/[0-9a-f-]+\/state$/,
    )
    expect(waitingResult.state).toBe('WAITING_CLIENT')
    const waitingReplacementRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-24' })
    await expect(waitingReplacementRow).toContainText('等待客户')
    await waitingReplacementRow.locator('.el-checkbox').click()
    await page.getByRole('button', { name: '批量标记支付' }).click()
    const paymentResult = await visibleMutation(
      page,
      bindStageAction('06', 'stage-06-record-current-task-pay-instruction', true),
      page.getByRole('button', { name: '确认', exact: true }),
      'POST',
      /\/api\/v1\/grant-fee-tasks\/batch-instruction$/,
    )
    expect(paymentResult).toMatchObject({ success_count: 1, failure_count: 0 })
    expect(paymentResult.updated_task_ids).toEqual([String(replaced.replacement_task?.task_id)])
    const paidReplacementRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-24' })
    await expect(paidReplacementRow).toContainText('支付')
    const finalOriginalRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-23' })
    await expect(finalOriginalRow).toContainText('来源未确认、已被替代或状态已变化，仅可查看')
    await expect(finalOriginalRow.getByRole('button')).toHaveCount(0)

    await paidReplacementRow.getByRole('link', { name: new RegExp(caseNo) }).click()
    await page.waitForURL(url => url.pathname === `/cases/no/${caseNo}`)
    await expandLifecycleHistory(page)
    const feeLane = page.getByTestId('fee-obligation-lane')
    await expect(feeLane).toContainText('官费轨：0 项')
    await reviewerContext.close()
  })

  expect(passiveMutations).toEqual(actionBindings.filter(binding => binding.mutation_expected).map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '06')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-06-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('07 生效官费预览与确认', async () => {
    uiPhase = 'stage-07-official-fee-preview'
    await page.goto(`${baseUrl}/grant-fee/tasks`, { waitUntil: 'networkidle' })
    await page.getByPlaceholder('请输入案件编号').fill(caseNo)
    await page.getByRole('button', { name: '查询', exact: true }).click()
    const currentTaskRow = page.getByRole('row').filter({ hasText: caseNo }).filter({ hasText: '2026-11-24' })
    await expect(currentTaskRow).toHaveCount(1)
    await expect(currentTaskRow).toContainText('支付')

    const previewBinding = bindStageAction('07', 'stage-07-preview-current-official-fees', false)
    const previewResponsePromise = page.waitForResponse(response => (
      response.request().method() === 'GET'
      && /\/api\/v1\/grant-fee-tasks\/[0-9a-f-]+\/official-fee-preview$/.test(new URL(response.url()).pathname)
    ))
    await currentTaskRow.getByRole('button', { name: '预览官费' }).click()
    const previewResponse = await previewResponsePromise
    expect(previewResponse.status()).toBe(200)
    const preview = await previewResponse.json() as Json
    previewBinding.method = 'GET'
    previewBinding.path = new URL(previewResponse.url()).pathname.replace(/^\/api\/v1/, '')
    previewBinding.status = previewResponse.status()
    previewBinding.result = preview

    expect(String(preview.grant_fee_task_id)).toBe(String(replacementGrantIdentity.task_id))
    expect(String(preview.source_document_id)).toBe(String(replacementGrantIdentity.document_id))
    expect(String(preview.reviewed_evidence_version_id)).toBe(String(replacementGrantIdentity.evidence_version_id))
    expect(String(preview.reviewed_evidence_content_hash)).toBe(`sha256:${replacementGrantIdentity.evidence_sha256}`)
    const previewLines = preview.lines as Json[]
    assertStrict('preview_line_count_at_least_two', previewLines.length >= 2, 'Stage 07 preview must expose at least two lines')
    assertStrict(
      'preview_source_digests_exact',
      /^[0-9a-f]{64}$/.test(String(preview.rate_book_sha256))
        && previewLines.every(line => /^[0-9a-f]{64}$/.test(String(line.rate_row_sha256)))
        && /^sha256:[0-9a-f]{64}$/.test(String(preview.preview_digest)),
      'Stage 07 source and preview digests must be exact SHA-256 values',
    )
    const audit = preview.read_only_audit_snapshot as Json
    const auditBefore = audit.before as Json
    const auditAfter = audit.after as Json
    assertStrict(
      'preview_read_only_transaction_snapshot',
      audit.unchanged === true
        && JSON.stringify(auditBefore.groups) === JSON.stringify(auditAfter.groups)
        && String(auditBefore.digest) === String(auditAfter.digest),
      'Stage 07 preview before/after transaction snapshot must be identical',
    )
    const payableAmounts = previewLines.map(line => Number(line.payable_amount))
    assertStrict(
      'gov_preview_amount_equation',
      payableAmounts.length === 2
        && payableAmounts[0] === 900
        && payableAmounts[1] === 50
        && Number(preview.total_payable_amount) === 950
        && preview.currency === 'CNY',
      'Stage 07 preview must be 900.00+50.00=950.00 CNY',
    )

    const previewDialog = page.getByRole('dialog', { name: '授权登记官费预览' })
    await expect(previewDialog).toContainText(String(preview.preview_digest))
    await expect(previewDialog).toContainText(String(preview.rate_book_sha256))
    await expect(previewDialog).toContainText('CNY 900.00')
    await expect(previewDialog).toContainText('CNY 50.00')
    await expect(previewDialog).toContainText('合计：CNY 950.00')
    await expect(previewDialog).toContainText('预览只读校验：一致（无业务写入）')

    uiPhase = 'stage-07-official-fee-confirmation'
    const confirmOfficialFeeButton = previewDialog.getByRole('button', { name: '确认官费并生成草单' })
    expect(await confirmOfficialFeeButton.evaluate(button => {
      const bounds = button.getBoundingClientRect()
      const hitTarget = document.elementFromPoint(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2)
      return hitTarget === button || button.contains(hitTarget)
    })).toBe(true)
    const confirmation = await visibleMutation(
      page,
      bindStageAction('07', 'stage-07-confirm-current-official-fees', true),
      confirmOfficialFeeButton,
      'POST',
      /\/api\/v1\/grant-fee-tasks\/[0-9a-f-]+\/official-fee-confirmation$/,
    )
    expect(String(confirmation.grant_fee_task_id)).toBe(String(replacementGrantIdentity.task_id))
    expect(String(confirmation.fee_obligation_id)).toMatch(/^[0-9a-f-]{36}$/)
    govObligationId = String(confirmation.fee_obligation_id)
    expect(String(confirmation.draft_id)).toMatch(/^[0-9a-f-]{36}$/)
    govDraftId = String(confirmation.draft_id)
    expect((confirmation.obligation_line_ids as unknown[]).length).toBe(2)
    expect((confirmation.fee_item_ids as unknown[]).length).toBe(2)
    govFeeItemIds = (confirmation.fee_item_ids as unknown[]).map(String).sort()
    expect(confirmation.reused).toBe(false)
    await page.waitForURL(url => url.pathname === `/fees/drafts/${confirmation.draft_id}`)
    await expect(page.getByRole('heading', { name: '费用草稿' })).toBeVisible()
    await page.getByRole('tab', { name: '概览' }).click()
    const govSourceFacts = page.getByTestId('draft-source-facts')
    await expect(govSourceFacts).toContainText('官费草单：全部明细只读')
    await expect(govSourceFacts.getByRole('row')).toHaveCount(3)
    await expect(govSourceFacts.getByRole('button')).toHaveCount(0)
    assertStrict(
      'one_gov_obligation_and_draft_after_confirmation',
      Boolean(confirmation.fee_obligation_id)
        && Boolean(confirmation.draft_id)
        && (confirmation.obligation_line_ids as unknown[]).length === 2
        && (confirmation.fee_item_ids as unknown[]).length === 2,
      'Stage 07 confirmation must create one GOV obligation and one GOV draft',
    )
  })

  expect(passiveMutations).toEqual(actionBindings.filter(binding => binding.mutation_expected).map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '07')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-07-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('08 双草单与服务费调整', async () => {
    uiPhase = 'stage-08-create-service-obligation'
    await page.goto(`${baseUrl}/cases/no/${caseNo}`, { waitUntil: 'networkidle' })
    await page.getByRole('tab', { name: '费用' }).click()
    const createdObligation = await visibleMutation(
      page,
      bindStageAction('08', 'stage-08-create-service-obligation', true),
      page.getByRole('button', { name: '生成服务费义务' }),
      'POST',
      /\/api\/v1\/fees\/demo-service-obligations$/,
    )
    originalServiceObligationId = String((createdObligation.obligation as Json).id)
    expect(originalServiceObligationId).toMatch(/^[0-9a-f-]{36}$/)
    expect(String(createdObligation.total_amount)).toBe('1500.00')
    await expect(page.getByText('服务费义务已生成（CNY 1500.00）')).toBeVisible()

    uiPhase = 'stage-08-record-service-pay-instruction'
    const serviceObligationCard = page.locator('.obligation-card').filter({ hasText: originalServiceObligationId }).first()
    await expect(serviceObligationCard).toBeVisible()
    const payInstruction = await visibleMutation(
      page,
      bindStageAction('08', 'stage-08-record-service-pay-instruction', true),
      serviceObligationCard.getByRole('button', { name: '记录支付指示' }),
      'POST',
      new RegExp(`/api/v1/fees/obligations/${originalServiceObligationId}/instruction$`),
    )
    expect(payInstruction.client_instruction_status).toBe('PAY')
    await serviceObligationCard.getByRole('link', { name: '创建关联费用草稿' }).click()
    await page.waitForURL(url => (
      url.pathname === '/fees/drafts/new'
      && url.searchParams.get('obligation_id') === originalServiceObligationId
    ))
    await expect(page.getByTestId('linked-fee-obligation')).toContainText(originalServiceObligationId)
    await expect(page.getByTestId('linked-fee-obligation')).toContainText('客户指示：PAY')
    await page.getByRole('textbox', { name: '案件编号' }).fill(currentCaseId)
    await page.getByRole('textbox', { name: '客户编号' }).fill(currentClientId)

    uiPhase = 'stage-08-create-service-draft'
    const createdServiceDraft = await visibleMutation(
      page,
      bindStageAction('08', 'stage-08-create-service-draft', true),
      page.getByRole('button', { name: '创建草稿' }),
      'POST',
      /\/api\/v1\/fees\/drafts$/,
    )
    serviceDraftId = String(createdServiceDraft.id)
    expect(serviceDraftId).toMatch(/^[0-9a-f-]{36}$/)
    expect(String(createdServiceDraft.amount)).toBe('1500.00')
    await page.waitForURL(url => url.pathname === `/fees/drafts/${serviceDraftId}`)
    await expect(page.getByRole('heading', { name: '费用草稿' })).toBeVisible()
    await expect(page.getByText('服务费', { exact: true })).toHaveCount(2)

    uiPhase = 'stage-08-adjust-service-draft'
    await page.getByRole('button', { name: '调整数量' }).click()
    const adjustmentDialog = page.getByRole('dialog', { name: '调整服务费数量' })
    await adjustmentDialog.getByRole('spinbutton', { name: '调整后数量' }).fill('2')
    await adjustmentDialog.getByRole('textbox', { name: '调整原因（须包含中文）' })
      .fill('客户确认增加一份附加文件处理')
    const adjusted = await visibleMutation(
      page,
      bindStageAction('08', 'stage-08-adjust-service-draft', true),
      adjustmentDialog.getByRole('button', { name: '确认调整' }),
      'POST',
      new RegExp(`/api/v1/fees/drafts/${serviceDraftId}/demo-service-adjustment$`),
    )
    expect(adjusted).toMatchObject({
      draft_id: serviceDraftId,
      original_obligation_id: originalServiceObligationId,
      before_total: '1500.00',
      after_total: '1800.00',
      reused: false,
    })
    supersedingServiceObligationId = String(adjusted.superseding_obligation_id)
    expect(supersedingServiceObligationId).toMatch(/^[0-9a-f-]{36}$/)
    expect(supersedingServiceObligationId).not.toBe(originalServiceObligationId)
    expect(String(adjusted.adjustment_activity_id)).toMatch(/^[0-9a-f-]{36}$/)
    await expect(adjustmentDialog).not.toBeVisible()

    await page.getByRole('tab', { name: '概览' }).click()
    const serviceSourceFacts = page.getByTestId('draft-source-facts')
    await expect(serviceSourceFacts).toContainText('服务费草单：仅授权项目可调整一次')
    await expect(serviceSourceFacts.getByRole('row')).toHaveCount(3)
    await expect(serviceSourceFacts).toContainText('客户确认增加一份附加文件处理')
    const adjustedLine = serviceSourceFacts.getByRole('row').filter({ hasText: '授权登记附加文件处理服务费' })
    await expect(adjustedLine).toHaveCount(1)
    await expect(adjustedLine).toContainText('客户确认增加一份附加文件处理')
    const adjustedLineText = await adjustedLine.innerText()
    const adjustmentDigests = adjustedLineText.match(/sha256:[0-9a-f]{64}/g) || []
    assertStrict(
      'adjustment_snapshots_and_digests_exact',
      adjustmentDigests.length === 2 && adjustmentDigests[0] !== adjustmentDigests[1],
      'Stage 08 adjustment row must expose distinct before/after snapshot digests',
    )
    const adjustedItemIds = (adjusted.fee_item_ids as unknown[]).map(String).sort()

    uiPhase = 'stage-08-lock-service-draft'
    await page.getByRole('button', { name: '🔒 锁定' }).click()
    const serviceLockDialog = page.getByRole('dialog', { name: '锁定草稿' })
    const serviceSourceFactsRefresh = page.waitForResponse(response => (
      response.request().method() === 'GET'
      && new URL(response.url()).pathname === `/api/v1/fees/drafts/${serviceDraftId}/source-facts`
    ))
    const lockedServiceDraft = await visibleMutation(
      page,
      bindStageAction('08', 'stage-08-lock-service-draft', true),
      serviceLockDialog.getByRole('button', { name: '锁定' }),
      'POST',
      new RegExp(`/api/v1/fees/drafts/${serviceDraftId}/lock$`),
    )
    expect(lockedServiceDraft.status).toBe('ok')
    expect((await serviceSourceFactsRefresh).status()).toBe(200)
    await expect(page.getByText('已锁定', { exact: true }).first()).toBeVisible()

    uiPhase = 'stage-08-lock-gov-draft'
    await page.goto(`${baseUrl}/fees/drafts/${govDraftId}`, { waitUntil: 'networkidle' })
    await page.getByRole('button', { name: '🔒 锁定' }).click()
    const govLockDialog = page.getByRole('dialog', { name: '锁定草稿' })
    const lockedGovDraft = await visibleMutation(
      page,
      bindStageAction('08', 'stage-08-lock-gov-draft', true),
      govLockDialog.getByRole('button', { name: '锁定' }),
      'POST',
      new RegExp(`/api/v1/fees/drafts/${govDraftId}/lock$`),
    )
    expect(lockedGovDraft.status).toBe('ok')
    await page.getByRole('tab', { name: '概览' }).click()
    const lockedGovSourceFacts = page.getByTestId('draft-source-facts')
    await expect(lockedGovSourceFacts).toContainText('官费草单：全部明细只读')
    await expect(lockedGovSourceFacts.getByRole('row')).toHaveCount(3)
    await expect(lockedGovSourceFacts).not.toContainText('客户确认增加一份附加文件处理')

    uiPhase = 'stage-08-verify-service-supersession'
    await page.goto(`${baseUrl}/cases/no/${caseNo}`, { waitUntil: 'networkidle' })
    await expandLifecycleHistory(page)
    const feeLane = page.getByTestId('fee-obligation-lane')
    const originalServiceCard = feeLane.getByTestId(`fee-obligation-${originalServiceObligationId}`)
    const supersedingServiceCard = feeLane.getByTestId(`fee-obligation-${supersedingServiceObligationId}`)
    await expect(originalServiceCard).toContainText('义务状态：已被替代')
    await expect(originalServiceCard).not.toContainText(`关联事实：草稿 / ${serviceDraftId}`)
    await expect(supersedingServiceCard).toContainText('关联事实：草单 / 已锁定')
    await expect(supersedingServiceCard).toContainText('替代理由：客户确认增加一份附加文件处理')
    await expectRawValueInAudit(supersedingServiceCard, `关联事实编号：${serviceDraftId}`)
    await expect(supersedingServiceCard.getByText(
      `替代前义务：${originalServiceObligationId}`,
      { exact: true },
    )).toBeVisible()
    await expect(feeLane).toContainText('官费轨：1 项')
    await expect(feeLane).toContainText('服务费轨：2 项')
    const feeLaneText = await feeLane.innerText()
    const originalServiceText = await originalServiceCard.innerText()
    const supersedingServiceText = await supersedingServiceCard.innerText()
    assertStrict(
      'one_domain_pure_gov_and_service',
      feeLaneText.includes('官费轨：1 项')
        && feeLaneText.includes('服务费轨：2 项')
        && govDraftId !== serviceDraftId,
      'Stage 08 must preserve one GOV chain and one current SERVICE chain without domain mixing',
    )
    assertStrict(
      'one_adjustment_and_superseding_chain',
      /^[0-9a-f-]{36}$/.test(String(adjusted.adjustment_activity_id))
        && supersedingServiceObligationId !== originalServiceObligationId,
      'Stage 08 must expose one adjustment and one superseding SERVICE obligation',
    )
    assertStrict(
      'original_service_header_exact',
      ['义务状态：已被替代', '客户指示状态：缴费', '草单状态：未创建', '付款状态：未缴费', '官方证据状态：不适用']
        .every(value => originalServiceText.includes(value)),
      'Stage 08 original SERVICE header must preserve its superseded state tuple',
    )
    assertStrict(
      'new_service_header_exact',
      ['义务状态：已确认', '客户指示状态：缴费', '草单状态：已创建', '付款状态：未缴费', '官方证据状态：不适用']
        .every(value => supersedingServiceText.includes(value)),
      'Stage 08 current SERVICE header must preserve its recognized state tuple',
    )
    assertStrict(
      'current_link_ownership_exact',
      adjustedItemIds.length === 2
        && !originalServiceText.includes(serviceDraftId)
        && supersedingServiceText.includes(serviceDraftId),
      'Stage 08 current draft and item links must belong only to the superseding obligation',
    )
    assertStrict(
      'service_adjustment_amount_transition',
      adjusted.before_total === '1500.00' && adjusted.after_total === '1800.00',
      'Stage 08 SERVICE adjustment must be exactly 1500.00 to 1800.00',
    )
    assertStrict(
      'both_locked_drafts_read_only',
      lockedServiceDraft.status === 'ok' && lockedGovDraft.status === 'ok',
      'Stage 08 GOV and SERVICE drafts must both be locked',
    )
  })

  expect(passiveMutations).toEqual(actionBindings.filter(binding => binding.mutation_expected).map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '08')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-08-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('09 官费清单与待凭证登记', async () => {
    uiPhase = 'stage-09-create-pay-list'
    await page.goto(`${baseUrl}/fees/drafts/${govDraftId}`, { waitUntil: 'networkidle' })
    const govItemSelectors = page.getByRole('checkbox', { name: /选择官费明细：/ })
    await expect(govItemSelectors).toHaveCount(2)
    for (const selector of await govItemSelectors.all()) await selector.locator('..').click()
    await page.getByRole('button', { name: '生成官费清单' }).click()
    const payListDialog = page.getByRole('dialog', { name: '生成官费清单' })
    await expect(payListDialog).toContainText('共 2 条，合计 ¥950.00')
    await payListDialog.getByRole('combobox', { name: '计划缴费日期' }).fill('2026-08-25')
    await payListDialog.getByRole('textbox', { name: '备注' }).fill('授权登记官费清单')
    const payListResult = await visibleMutation(
      page,
      bindStageAction('09', 'stage-09-create-gov-pay-list', true),
      payListDialog.getByRole('button', { name: '创建官费清单' }),
      'POST',
      /\/api\/v1\/pay-lists\/from-fee-items$/,
    )
    const payList = payListResult.pay_list as Json
    payListId = Number(payList.id)
    expect(payListId).toBeGreaterThan(0)
    expect(payListResult.summary).toMatchObject({ requested: 2, success: 2, failed: 0, pay_list_created: true })
    expect(String(payList.total_amount)).toBe('950.00')
    const payListSuccess = payListResult.success as Json[]
    expect(payListSuccess.map(row => String(row.fee_item_id)).sort()).toEqual(govFeeItemIds)
    expect(payListSuccess.reduce((sum, row) => sum + Number(row.amount), 0)).toBe(950)
    await page.waitForURL(url => url.pathname === `/fee-management/pay-lists/${payListId}`)
    await expect(page.getByRole('heading', { name: '官费清单详情' })).toBeVisible()
    await expect(page.getByText('已登记，待官方凭证核验').first()).toBeVisible()

    uiPhase = 'stage-09-register-first-gov-payment'
    await page.getByRole('button', { name: '去登记缴费' }).click()
    await page.waitForURL(url => url.pathname === '/fee-management/gov-payments/new')
    await page.getByRole('combobox', { name: '缴费日期' }).fill('2026-08-25')
    const firstPayment = await visibleMutation(
      page,
      bindStageAction('09', 'stage-09-register-first-gov-payment', true),
      page.getByRole('button', { name: '提交登记' }),
      'POST',
      /\/api\/v1\/gov-payments\/demo-command$/,
    )
    expect(firstPayment).toMatchObject({ fact_status: 'REGISTERED_PENDING_OFFICIAL_EVIDENCE', reused: false })
    expect((firstPayment.gov_payment as Json)).toMatchObject({
      official_receipt_no: null,
      voucher_no: null,
      invoice_no: null,
      remark: '已登记，待官方凭证核验',
    })
    govPaymentIds.push(Number((firstPayment.gov_payment as Json).id))
    await expect(page.getByText('已登记，待官方凭证核验').first()).toBeVisible()

    uiPhase = 'stage-09-replay-first-gov-payment'
    const replayedFirstPayment = await visibleMutation(
      page,
      bindStageAction('09', 'stage-09-replay-first-gov-payment', true),
      page.getByRole('button', { name: '提交登记' }),
      'POST',
      /\/api\/v1\/gov-payments\/demo-command$/,
    )
    expect(replayedFirstPayment).toMatchObject({ reused: true })
    expect(Number((replayedFirstPayment.gov_payment as Json).id)).toBe(govPaymentIds[0])

    uiPhase = 'stage-09-register-second-gov-payment'
    await page.getByRole('button', { name: '登记下一行' }).click()
    await page.waitForURL(url => url.pathname === '/fee-management/gov-payments/new')
    await page.getByRole('combobox', { name: '缴费日期' }).fill('2026-08-25')
    const secondPayment = await visibleMutation(
      page,
      bindStageAction('09', 'stage-09-register-second-gov-payment', true),
      page.getByRole('button', { name: '提交登记' }),
      'POST',
      /\/api\/v1\/gov-payments\/demo-command$/,
    )
    expect(secondPayment).toMatchObject({ fact_status: 'REGISTERED_PENDING_OFFICIAL_EVIDENCE', reused: false })
    expect((secondPayment.gov_payment as Json)).toMatchObject({
      official_receipt_no: null,
      voucher_no: null,
      invoice_no: null,
      remark: '已登记，待官方凭证核验',
    })
    govPaymentIds.push(Number((secondPayment.gov_payment as Json).id))
    expect(new Set(govPaymentIds).size).toBe(2)
    expect(
      Number((firstPayment.gov_payment as Json).paid_amount)
        + Number((secondPayment.gov_payment as Json).paid_amount),
    ).toBe(950)
    await page.getByRole('button', { name: '返回当前清单' }).click()
    await page.waitForURL(url => url.pathname === `/fee-management/pay-lists/${payListId}`)
    const govPaymentCard = page.locator('.el-card').filter({ hasText: '官费登记记录' })
    await expect(govPaymentCard).toContainText('共 2 条')
    await expect(govPaymentCard.getByRole('row').filter({ hasText: '¥50.00' })).toContainText('已登记，待官方凭证核验')
    await expect(govPaymentCard.getByRole('row').filter({ hasText: '¥900.00' })).toContainText('已登记，待官方凭证核验')
    await expect(page.getByText('已缴费成功')).toHaveCount(0)
    const firstGovPayment = firstPayment.gov_payment as Json
    const secondGovPayment = secondPayment.gov_payment as Json
    assertStrict(
      'one_pay_list_with_two_gov_lines',
      payListId > 0 && payListSuccess.length === 2 && payListResult.summary.requested === 2,
      'Stage 09 must create one PayList with exactly two GOV lines',
    )
    assertStrict(
      'one_pending_gov_payment_per_line',
      govPaymentIds.length === 2
        && [firstPayment, secondPayment].every(result => result.fact_status === 'REGISTERED_PENDING_OFFICIAL_EVIDENCE')
        && [firstGovPayment, secondGovPayment].every(payment => (
          payment.official_receipt_no === null && payment.voucher_no === null && payment.invoice_no === null
        )),
      'Stage 09 must keep one pending-evidence registration per GOV line',
    )
    assertStrict(
      'gov_pay_list_payment_totals_equal',
      String(payList.total_amount) === '950.00'
        && payListSuccess.reduce((sum, row) => sum + Number(row.amount), 0) === 950
        && Number(firstGovPayment.paid_amount) + Number(secondGovPayment.paid_amount) === 950,
      'Stage 09 GOV draft, PayList, and payment registration totals must equal 950.00',
    )
    assertStrict(
      'gov_registration_replay_stable',
      replayedFirstPayment.reused === true
        && Number((replayedFirstPayment.gov_payment as Json).id) === govPaymentIds[0]
        && new Set(govPaymentIds).size === 2,
      'Stage 09 replay must preserve identities and counts',
    )
    assertStrict(
      'service_excluded_from_pay_list',
      payListSuccess.map(row => String(row.fee_item_id)).sort().join(',') === govFeeItemIds.join(','),
      'Stage 09 PayList must contain only the GOV fee-item identities',
    )
  })

  expect(passiveMutations).toEqual(actionBindings.filter(binding => binding.mutation_expected).map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '09')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-09-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('10 服务费账单、两笔回款与核销结清', async () => {
    const billNo = `AR-CYZN-${suffix}`

    uiPhase = 'stage-10-create-service-bill'
    await page.goto(`${baseUrl}/billing/bills/new`, { waitUntil: 'networkidle' })
    const billInputs = page.getByTestId('demo-service-bill-inputs')
    await expect(billInputs).toBeVisible()
    await expectSelected(page, '服务费草稿', '服务费草稿 · CNY 1800.00')
    await billInputs.getByRole('textbox', { name: '账单编号' }).fill(billNo)
    await billInputs.getByRole('combobox', { name: '账单日期' }).fill('2026-08-25')
    await billInputs.getByRole('combobox', { name: '到期日期' }).fill('2026-09-24')
    const createdBill = await visibleMutation(
      page,
      bindStageAction('10', 'stage-10-create-service-bill', true),
      billInputs.getByRole('button', { name: '生成服务费账单' }),
      'POST',
      /\/api\/v1\/bills\/demo-from-draft$/,
    )
    const bill = createdBill.bill as Json
    billId = String(bill.id)
    expect(bill).toMatchObject({
      bill_no: billNo,
      case_id: currentCaseId,
      client_id: currentClientId,
      currency: 'CNY',
      direction: 'AR',
      status: 'UNSETTLED',
      total_gov: '0.00',
      total_service: '1800.00',
      amount: '1800.00',
      balance: '1800.00',
      source_draft_ids: [serviceDraftId],
    })
    expect(billId).toMatch(/^[0-9a-f-]{36}$/)
    await page.waitForURL(url => url.pathname === '/billing/payments/new' && url.searchParams.get('bill_id') === billId)

    uiPhase = 'stage-10-register-first-customer-payment'
    await expect(page.getByRole('heading', { name: '登记回款' })).toBeVisible()
    await expect(page.getByText('最新可见余额：CNY 1800.00')).toBeVisible()
    await page.getByRole('spinbutton', { name: '回款金额' }).fill('1200')
    await page.getByRole('combobox', { name: '收款日期' }).fill('2026-08-25')
    await page.getByRole('textbox', { name: '收款编号', exact: true }).fill(`RCPT-CYZN-${suffix}-01`)
    await page.getByRole('textbox', { name: '银行流水参考号' }).fill(`BTR-CYZN-${suffix}-01`)
    await page.getByRole('textbox', { name: '备注' }).fill(`${customerName}第一笔客户回款`)
    const firstReceipt = await visibleMutation(
      page,
      bindStageAction('10', 'stage-10-register-first-customer-payment', true),
      page.getByRole('button', { name: '登记回款' }),
      'POST',
      /\/api\/v1\/payments\/demo-bank-receipts$/,
    )
    const firstPayment = firstReceipt.payment as Json
    const firstLine = firstReceipt.line as Json
    expect(firstReceipt.bill).toMatchObject({ id: billId, status: 'UNSETTLED', balance: '1800.00' })
    expect(firstPayment).toMatchObject({ amount: '1200.00', pay_method: 'BANK_TRANSFER' })
    expect(firstLine).toMatchObject({ raw_amount: '1200.00', balance_amt: '1200.00', status: 'UNALLOCATED' })
    customerPaymentIds.push(String(firstPayment.id))
    await page.waitForURL(url => url.pathname === '/billing/payments' && url.searchParams.get('payment_id') === customerPaymentIds[0])
    await expect(page.getByText('登记回款不等于账单核销')).toBeVisible()

    uiPhase = 'stage-10-offset-first-customer-payment'
    const firstPaymentRow = page.getByRole('row').filter({ hasText: '目标回款' })
    await expect(firstPaymentRow).toContainText(`RCPT-CYZN-${suffix}-01`)
    await firstPaymentRow.getByRole('button', { name: '创建核销' }).click()
    const firstOffsetDialog = page.getByRole('dialog', { name: '创建核销' })
    await expect(firstOffsetDialog).toBeVisible()
    await expect(firstOffsetDialog.getByRole('spinbutton', { name: '核销金额' })).toHaveValue('1200.00')
    await firstOffsetDialog.getByRole('combobox', { name: '核销日期' }).fill('2026-08-25')
    const firstOffset = await visibleMutation(
      page,
      bindStageAction('10', 'stage-10-offset-first-customer-payment', true),
      firstOffsetDialog.getByRole('button', { name: '创建核销' }),
      'POST',
      /\/api\/v1\/offsets\/demo-full$/,
    )
    expect(firstOffset.bill).toMatchObject({ id: billId, status: 'PARTIALLY_SETTLED', balance: '600.00' })
    expect(firstOffset.offset).toMatchObject({
      payment_line_id: String(firstLine.id),
      bill_id: billId,
      offset_amt: '1200.00',
      offset_date: '2026-08-25',
      is_reversed: false,
    })
    offsetIds.push(String((firstOffset.offset as Json).id))
    await expect(page.getByText('账单状态：部分结清')).toBeVisible()
    await expect(page.getByText('最新余额：CNY 600.00')).toBeVisible()

    uiPhase = 'stage-10-register-second-customer-payment'
    await page.getByRole('button', { name: '按最新余额登记下一笔回款' }).click()
    await page.waitForURL(url => url.pathname === '/billing/payments/new' && url.searchParams.get('bill_id') === billId)
    await expect(page.getByText('最新可见余额：CNY 600.00')).toBeVisible()
    await expect(page.getByRole('spinbutton', { name: '回款金额' })).toHaveValue('600.00')
    await page.getByRole('combobox', { name: '收款日期' }).fill('2026-08-26')
    await page.getByRole('textbox', { name: '收款编号', exact: true }).fill(`RCPT-CYZN-${suffix}-02`)
    await page.getByRole('textbox', { name: '银行流水参考号' }).fill(`BTR-CYZN-${suffix}-02`)
    await page.getByRole('textbox', { name: '备注' }).fill(`${customerName}第二笔客户回款`)
    const secondReceipt = await visibleMutation(
      page,
      bindStageAction('10', 'stage-10-register-second-customer-payment', true),
      page.getByRole('button', { name: '登记回款' }),
      'POST',
      /\/api\/v1\/payments\/demo-bank-receipts$/,
    )
    const secondPayment = secondReceipt.payment as Json
    const secondLine = secondReceipt.line as Json
    expect(secondReceipt.bill).toMatchObject({ id: billId, status: 'PARTIALLY_SETTLED', balance: '600.00' })
    expect(secondPayment).toMatchObject({ amount: '600.00', pay_method: 'BANK_TRANSFER' })
    expect(secondLine).toMatchObject({ raw_amount: '600.00', balance_amt: '600.00', status: 'UNALLOCATED' })
    customerPaymentIds.push(String(secondPayment.id))
    expect(new Set(customerPaymentIds).size).toBe(2)
    await page.waitForURL(url => url.pathname === '/billing/payments' && url.searchParams.get('payment_id') === customerPaymentIds[1])

    uiPhase = 'stage-10-offset-second-customer-payment'
    const secondPaymentRow = page.getByRole('row').filter({ hasText: '目标回款' })
    await expect(secondPaymentRow).toContainText(`RCPT-CYZN-${suffix}-02`)
    await secondPaymentRow.getByRole('button', { name: '创建核销' }).click()
    const secondOffsetDialog = page.getByRole('dialog', { name: '创建核销' })
    await expect(secondOffsetDialog).toBeVisible()
    await expect(secondOffsetDialog.getByRole('spinbutton', { name: '核销金额' })).toHaveValue('600.00')
    await secondOffsetDialog.getByRole('combobox', { name: '核销日期' }).fill('2026-08-26')
    const secondOffset = await visibleMutation(
      page,
      bindStageAction('10', 'stage-10-offset-second-customer-payment', true),
      secondOffsetDialog.getByRole('button', { name: '创建核销' }),
      'POST',
      /\/api\/v1\/offsets\/demo-full$/,
    )
    expect(secondOffset.bill).toMatchObject({ id: billId, status: 'SETTLED', balance: '0.00' })
    expect(secondOffset.offset).toMatchObject({
      payment_line_id: String(secondLine.id),
      bill_id: billId,
      offset_amt: '600.00',
      offset_date: '2026-08-26',
      is_reversed: false,
    })
    offsetIds.push(String((secondOffset.offset as Json).id))
    expect(new Set(offsetIds).size).toBe(2)
    expect(Number(firstPayment.amount) + Number(secondPayment.amount)).toBe(1800)
    expect(Number((firstOffset.offset as Json).offset_amt) + Number((secondOffset.offset as Json).offset_amt)).toBe(1800)
    await expect(page.getByText('账单状态：已结清')).toBeVisible()
    await expect(page.getByText('最新余额：CNY 0.00')).toBeVisible()

    uiPhase = 'stage-10-verify-settled-bill'
    await page.goto(`${baseUrl}/billing/bills/${billId}`, { waitUntil: 'networkidle' })
    await expect(page.getByText('账单结清状态：已结清')).toBeVisible()
    await expect(page.getByText('账单余额为 ¥0.00')).toBeVisible()
    assertStrict(
      'service_bill_chain_totals_equal',
      bill.total_service === '1800.00'
        && bill.amount === '1800.00'
        && (bill.source_draft_ids as unknown[]).map(String).join(',') === serviceDraftId,
      'Stage 10 SERVICE obligation, locked draft, and bill totals must equal 1800.00',
    )
    assertStrict(
      'payment_registration_does_not_reduce_balance',
      (firstReceipt.bill as Json).status === 'UNSETTLED'
        && (firstReceipt.bill as Json).balance === '1800.00',
      'Stage 10 first Payment registration must not reduce bill balance',
    )
    assertStrict(
      'first_offset_partially_settles',
      (firstOffset.bill as Json).status === 'PARTIALLY_SETTLED'
        && (firstOffset.bill as Json).balance === '600.00',
      'Stage 10 first 1200.00 Offset must leave a 600.00 balance',
    )
    assertStrict(
      'second_payment_reads_refreshed_balance',
      (secondReceipt.bill as Json).balance === '600.00' && secondPayment.amount === '600.00',
      'Stage 10 second Payment must use the refreshed authoritative 600.00 balance',
    )
    assertStrict(
      'two_payments_two_offsets_final_settled',
      new Set(customerPaymentIds).size === 2
        && new Set(offsetIds).size === 2
        && (secondOffset.bill as Json).status === 'SETTLED'
        && (secondOffset.bill as Json).balance === '0.00',
      'Stage 10 must end with two Payments, two Offsets, and a settled bill',
    )
    assertStrict(
      'payment_offset_bill_totals_equal',
      Number(firstPayment.amount) + Number(secondPayment.amount) === 1800
        && Number((firstOffset.offset as Json).offset_amt) + Number((secondOffset.offset as Json).offset_amt) === 1800
        && bill.amount === '1800.00',
      'Stage 10 Payment, Offset, and Bill totals must all equal 1800.00',
    )
    assertStrict(
      'gov_excluded_from_bill',
      bill.total_gov === '0.00'
        && (bill.items as Json[]).every(item => item.fee_type === 'SERVICE'),
      'Stage 10 customer Bill must exclude GOV amounts and lines',
    )
  })

  expect(passiveMutations).toEqual(actionBindings.filter(binding => binding.mutation_expected).map(binding => ({
    method: binding.method,
    path: binding.path,
    status: binding.status,
  })))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await captureStage(page, '10')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-10-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  await test.step('11 同案双轨只读汇总', async () => {
    const mutationCountBeforeSummary = passiveMutations.length
    uiPhase = 'stage-11-open-dual-track-summary'
    bindStageAction('11', 'stage-11-open-dual-track-summary', false)
    await page.getByRole('link').filter({ hasText: caseNo }).first().click()
    await page.waitForURL(url => url.pathname === `/cases/${currentCaseId}`)

    await expandLifecycleHistory(page)
    const feeLane = page.getByTestId('fee-obligation-lane')
    await expect(feeLane.getByRole('heading', { name: '同案双轨费用概览' })).toBeVisible()
    await expect(feeLane).toContainText('官费轨：1 项')
    await expect(feeLane).toContainText('服务费轨：2 项')

    const govCard = feeLane.getByTestId(`fee-obligation-${govObligationId}`)
    await expect(govCard).toContainText('关联事实：草单 / 已锁定')
    await expect(govCard).toContainText('官方证据状态：待处理')
    await expect(govCard).not.toContainText('未识别状态')
    await expectRawValueInAudit(govCard, `关联事实编号：${govDraftId}`)
    const govAuditFactIds = new Set(await govCard.getByText(/^关联事实编号：/).allInnerTexts())
    expect(govAuditFactIds.has(`关联事实编号：${payListId}`)).toBe(true)
    for (const paymentId of govPaymentIds) {
      expect(govAuditFactIds.has(`关联事实编号：${paymentId}`)).toBe(true)
    }

    const originalServiceCard = feeLane.getByTestId(`fee-obligation-${originalServiceObligationId}`)
    const currentServiceCard = feeLane.getByTestId(`fee-obligation-${supersedingServiceObligationId}`)
    await expect(originalServiceCard).not.toContainText(serviceDraftId)
    await expect(currentServiceCard).toContainText('关联事实：草单 / 已锁定')
    await expect(currentServiceCard).toContainText('替代理由：客户确认增加一份附加文件处理')
    await expect(originalServiceCard).not.toContainText('未识别状态')
    await expect(currentServiceCard).not.toContainText('未识别状态')
    await expectRawValueInAudit(currentServiceCard, `关联事实编号：${serviceDraftId}`)
    await expect(currentServiceCard.getByText(
      `替代前义务：${originalServiceObligationId}`,
      { exact: true },
    )).toBeVisible()
    const finalGovText = await govCard.innerText()
    const finalOriginalServiceText = await originalServiceCard.innerText()
    const finalCurrentServiceText = await currentServiceCard.innerText()

    await page.getByRole('tab', { name: '账单与收款' }).click()
    const receiptsSummary = page.locator('.receipts-summary')
    await expect(receiptsSummary).toContainText('累计开票')
    await expect(receiptsSummary).toContainText('¥1,800.00')
    await expect(receiptsSummary).toContainText('累计回款')
    await expect(receiptsSummary).toContainText('未结清')
    await expect(receiptsSummary).toContainText('¥0.00')
    const settledBillRow = receiptsSummary.getByRole('row').filter({ hasText: `AR-CYZN-${suffix}` })
    await expect(settledBillRow).toContainText('已结清')
    await expect(settledBillRow).toContainText('¥1,800.00')
    await expect(settledBillRow).toContainText('¥0.00')
    const finalReceiptsText = await receiptsSummary.innerText()
    await settledBillRow.click()
    await page.waitForURL(url => url.pathname === `/billing/bills/${billId}`)
    await page.getByRole('tab', { name: '抵扣记录' }).click()
    const offsetRows = page.getByRole('row').filter({ hasText: '有效' })
    await expect(offsetRows).toHaveCount(2)
    await expect(offsetRows.filter({ hasText: '¥1,200.00' })).toHaveCount(1)
    await expect(offsetRows.filter({ hasText: '¥600.00' })).toHaveCount(1)

    assertStrict(
      'original_service_obligation_final_state',
      ['义务状态：已被替代', '客户指示状态：缴费', '草单状态：未创建', '付款状态：未缴费', '官方证据状态：不适用']
        .every(value => finalOriginalServiceText.includes(value))
        && !finalOriginalServiceText.includes(serviceDraftId),
      'Stage 11 original SERVICE obligation must retain its superseded tuple and no current links',
    )
    assertStrict(
      'new_service_obligation_final_state',
      ['义务状态：已确认', '客户指示状态：缴费', '草单状态：已创建', '付款状态：未缴费', '官方证据状态：不适用']
        .every(value => finalCurrentServiceText.includes(value))
        && finalCurrentServiceText.includes(serviceDraftId),
      'Stage 11 current SERVICE obligation must retain its recognized tuple and current links',
    )
    assertStrict(
      'gov_identity_and_total_chain_complete',
      finalGovText.includes(govDraftId)
        && finalGovText.includes(String(payListId))
        && govPaymentIds.every(id => finalGovText.includes(String(id)))
        && finalGovText.includes('50.00')
        && finalGovText.includes('900.00'),
      'Stage 11 GOV draft, PayList, payment identities, and total chain must be visible',
    )
    assertStrict(
      'service_identity_and_total_chain_complete',
      finalCurrentServiceText.includes(serviceDraftId)
        && finalReceiptsText.includes(`AR-CYZN-${suffix}`)
        && finalReceiptsText.includes('¥1,800.00')
        && new Set(customerPaymentIds).size === 2
        && new Set(offsetIds).size === 2,
      'Stage 11 SERVICE obligation, draft, Bill, Payment, and Offset chain must be complete',
    )
    assertStrict(
      'dual_track_final_statuses',
      finalGovText.includes('官方证据状态：待处理')
        && finalReceiptsText.includes('已结清')
        && finalReceiptsText.includes('¥0.00'),
      'Stage 11 GOV must await official evidence while SERVICE is settled',
    )
    assertStrict(
      'network_and_console_empty',
      networkErrors.length === 0 && consoleErrors.length === 0,
      'Stage 11 browser network and console error arrays must remain empty',
    )
    assertStrict(
      'stage_11_no_new_writes',
      passiveMutations.length === mutationCountBeforeSummary,
      'Stage 11 read-only summary must not create a new mutation',
    )
    expect(passiveMutations.length).toBe(mutationCountBeforeSummary)
    expect(consoleErrors).toEqual([])
    expect(networkErrors).toEqual([])
  })

  await captureStage(page, '11')
  await writeFile(
    path.join(required('FPMS_DEMO_EVIDENCE_DIR'), 'stage-11-tracer.json'),
    `${JSON.stringify({ action_bindings: actionBindings, passive_mutations: passiveMutations }, null, 2)}\n`,
    'utf8',
  )

  const schemaId = 'fpms.demo-v6-ui-parity/v1'
  const mutationRows = actionBindings.filter(binding => binding.mutation_expected).map(binding => ({
    stage: binding.stage,
    action_id: binding.action_id,
    method: binding.method,
    path: binding.path,
    status: binding.status,
  }))
  const canonicalContract = JSON.parse(
    await readFile(required('FPMS_DEMO_UI_PARITY_CONTRACT_PATH'), 'utf8'),
  ) as {
    schema_id: string
    stages: Array<{
      stage: string
      inputs: Array<{
        field_key: string
        classification: string
        normalization: string
        source_selector: string
        value_rule: unknown
      }>
      outputs: Array<{
        field_key: string
        classification: string
        normalization: string
        observable: string
        expected_rule: string
        value_rule: unknown
      }>
    }>
  }
  expect(canonicalContract.schema_id).toBe(schemaId)
  const inputRows = canonicalContract.stages.flatMap(stage => stage.inputs.map(row => ({
    stage: stage.stage,
    field_key: row.field_key,
    classification: row.classification,
    normalization: row.normalization,
    source_selector: row.source_selector,
    normalized_value: row.value_rule,
  })))
  const outputRows = canonicalContract.stages.flatMap(stage => stage.outputs.map(row => ({
    stage: stage.stage,
    field_key: row.field_key,
    classification: row.classification,
    normalization: row.normalization,
    observable: row.observable,
    expected_rule: row.expected_rule,
    normalized_value: row.value_rule,
  })))
  expect(inputRows).toHaveLength(103)
  expect(outputRows).toHaveLength(30)
  const screenshotRows = await Promise.all(Array.from({ length: 11 }, async (_value, index) => {
    const stage = String(index + 1).padStart(2, '0')
    const screenshotPath = path.join(required('FPMS_DEMO_EVIDENCE_DIR'), `stage-${stage}.png`)
    return {
      stage,
      path: screenshotPath,
      sha256: createHash('sha256').update(await readFile(screenshotPath)).digest('hex'),
    }
  }))
  const stages = [
    { stage: '01', client_id: currentClientId, case_id: currentCaseId },
    { stage: '02', filing_package_id: filingPackageId },
    { stage: '03', filing_receipt_filename: filingReceiptFilename },
    { stage: '04', oa_chain: 'FIRST_NOTICE' },
    { stage: '05', oa_chain: 'SECOND_NOTICE' },
    { stage: '06', replacement_grant_notice: replacementGrantIdentity },
    { stage: '07', gov_draft_id: govDraftId, gov_total: '950.00' },
    { stage: '08', service_draft_id: serviceDraftId, service_total: '1800.00' },
    { stage: '09', pay_list_id: payListId, gov_payment_ids: govPaymentIds, gov_status: 'REGISTERED_PENDING_OFFICIAL_EVIDENCE' },
    {
      stage: '10', bill_id: billId, first_payment_id: customerPaymentIds[0], second_payment_id: customerPaymentIds[1],
      first_offset_id: offsetIds[0], second_offset_id: offsetIds[1], partial_status: 'PARTIALLY_SETTLED',
      partial_balance: '600.00', final_status: 'SETTLED', final_balance: '0.00',
      amount_equation: '1200.00 + 600.00 = 1800.00',
    },
    { stage: '11', bill_status: 'SETTLED', bill_balance: '0.00', gov_status: 'REGISTERED_PENDING_OFFICIAL_EVIDENCE' },
  ]
  const evidenceDir = required('FPMS_DEMO_EVIDENCE_DIR')
  await writeFile(path.join(evidenceDir, 'ui-input-ledger.json'), `${JSON.stringify({ schema_id: schemaId, rows: inputRows }, null, 2)}\n`)
  await writeFile(path.join(evidenceDir, 'ui-output-ledger.json'), `${JSON.stringify({ schema_id: schemaId, rows: outputRows }, null, 2)}\n`)
  await writeFile(path.join(evidenceDir, 'ui-mutation-ledger.json'), `${JSON.stringify({ schema_id: schemaId, rows: mutationRows }, null, 2)}\n`)
  await writeFile(path.join(evidenceDir, 'network-errors.json'), `${JSON.stringify(networkErrors, null, 2)}\n`)
  await writeFile(path.join(evidenceDir, 'console-errors.json'), `${JSON.stringify(consoleErrors, null, 2)}\n`)
  await writeFile(path.join(evidenceDir, 'v6-stages.json'), `${JSON.stringify({ stages, network_errors: networkErrors, console_errors: consoleErrors }, null, 2)}\n`)
  await writeFile(path.join(evidenceDir, 'v6-final.png'), await readFile(path.join(evidenceDir, 'stage-11.png')))
  const receipt = {
    schema_id: schemaId,
    status: 'PASS',
    actor: required('FPMS_DEMO_STRICT_ACTOR'),
    account_id: required('FPMS_ADMIN_USERNAME'),
    run_id: required('FPMS_DEMO_RUN_ID'),
    run_root: required('FPMS_DEMO_RUN_ROOT'),
    database_path: required('FPMS_DEMO_DATABASE_PATH'),
    candidate_commit: required('FPMS_DEMO_CANDIDATE_COMMIT'),
    candidate_tree: required('FPMS_DEMO_CANDIDATE_TREE'),
    contract_version: schemaId,
    bundle_manifest_sha256: required('FPMS_DEMO_EXPECTED_MANIFEST_SHA256'),
    authority_sha256: required('FPMS_DEMO_EXPECTED_AUTHORITY_SHA256'),
    allowed_differences: [
      'run suffix', 'UUID/autoincrement ID', 'database/file path', 'dynamic credential',
      'idempotency key', 'system timestamp',
    ],
    input_ledger: inputRows,
    output_ledger: outputRows,
    mutation_ledger: mutationRows,
    screenshots: screenshotRows,
    network_errors: networkErrors,
    console_errors: consoleErrors,
  }
  await writeFile(path.join(evidenceDir, 'strict-pass-receipt.json'), `${JSON.stringify(receipt, null, 2)}\n`)
})
