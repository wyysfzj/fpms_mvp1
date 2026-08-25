import './demo-integrated-a.live-backend.spec'
import { test, expect, type APIRequestContext, type Page } from '@playwright/test'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'

type Json = Record<string, any>

const baseUrl = process.env.FPMS_BASE_URL || 'http://127.0.0.1:5173'
const apiBase = process.env.FPMS_API_URL || 'http://127.0.0.1:8000/api/v1'
const evidenceDir = process.env.FPMS_DEMO_EVIDENCE_DIR
const adminUsername = process.env.FPMS_ADMIN_USERNAME
const adminPassword = process.env.FPMS_ADMIN_PASSWORD
const expectedStageOrder = process.env.FPMS_DEMO_V6_STAGE_ORDER

const v6Stages = [
  ['01', '客户与案件'],
  ['02', '文件与递交准备'],
  ['03', '受理与审查'],
  ['04', '第一轮 OA'],
  ['05', '第二轮 OA'],
  ['06', '授权登记准备'],
  ['07', '生效官费预览'],
  ['08', '双草单与服务费调整'],
  ['09', '官费清单与待凭证登记'],
  ['10', '两次客户回款与核销'],
  ['11', '同案双轨汇总'],
] as const

async function login(page: Page): Promise<string> {
  await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
  await page.locator('.el-form-item:has-text("用户名") input').fill(adminUsername!)
  await page.locator('.el-form-item:has-text("密码") input').fill(adminPassword!)
  const responsePromise = page.waitForResponse((response) => (
    response.status() === 200 && response.url().includes('/auth/login')
  ))
  await page.getByRole('button', { name: '登 录' }).click()
  const response = await responsePromise
  const body = await response.json() as Json
  expect(body.access_token).toMatch(/^\S+$/)
  return body.access_token
}

async function api(
  request: APIRequestContext,
  token: string,
  method: 'GET' | 'POST',
  route: string,
  data?: Json,
  expected: readonly number[] = [200, 201],
): Promise<Json> {
  const response = await request.fetch(`${apiBase}${route}`, {
    method,
    data,
    headers: { Authorization: `Bearer ${token}` },
  })
  expect(expected, `${method} ${route}: ${await response.text()}`).toContain(response.status())
  return await response.json() as Json
}

function checkpoint(ledger: Json, identity: string): Json {
  const row = (ledger.checkpoints as Json[]).find((item) => item.checkpoint === identity)
  expect(row).toBeDefined()
  return row!.result as Json
}

async function expectNormalPage(page: Page, route: string, visibleText: string): Promise<void> {
  await page.goto(`${baseUrl}${route}`, { waitUntil: 'domcontentloaded' })
  await expect(page).toHaveURL(new RegExp(route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
  await expect(page.getByText(visibleText, { exact: false }).first()).toBeVisible()
}

test('V6 appends authoritative dual-track fee stages on normal customer pages', async ({ page, request }) => {
  expect(evidenceDir).toBeTruthy()
  expect(adminUsername).toBeTruthy()
  expect(adminPassword).toBeTruthy()
  expect(expectedStageOrder).toBe('01,02,03,04,05,06,07,08,09,10,11')

  const consoleErrors: string[] = []
  const networkErrors: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })
  page.on('requestfailed', (requestFailure) => {
    networkErrors.push(`${requestFailure.method()} ${requestFailure.url()}: ${requestFailure.failure()?.errorText || ''}`)
  })

  const token = await login(page)
  const legacyLedger = JSON.parse(
    await readFile(path.join(evidenceDir!, 'task9-checkpoints.json'), 'utf8'),
  ) as Json
  const clientId = checkpoint(legacyLedger, 'IA-01').client_id as string
  const caseResult = checkpoint(legacyLedger, 'IA-02')
  const caseId = caseResult.case_id as string
  const caseNo = caseResult.case_no as string
  const grantTaskId = checkpoint(legacyLedger, 'IA-11').replacement_task_id as string
  const runSuffix = Date.now().toString()
  const results: Json[] = v6Stages.slice(0, 6).map(([stage, label]) => ({
    stage,
    label,
    result: 'PASS_FROM_CANONICAL_V5',
  }))

  await test.step('07 生效官费预览', async () => {
    const preview = await api(
      request,
      token,
      'GET',
      `/grant-fee-tasks/${encodeURIComponent(grantTaskId)}/official-fee-preview`,
    )
    expect(preview.lines.length).toBeGreaterThanOrEqual(2)
    expect(preview.preview_digest).toMatch(/^sha256:[0-9a-f]{64}$/)
    await expectNormalPage(page, '/grant-fee/tasks', caseNo)
    await expect(page.getByRole('button', { name: '预览官费' }).first()).toBeVisible()
    const confirmation = await api(
      request,
      token,
      'POST',
      `/grant-fee-tasks/${encodeURIComponent(grantTaskId)}/official-fee-confirmation`,
      {
        preview_digest: preview.preview_digest,
        reviewed_evidence_version_id: preview.reviewed_evidence_version_id,
        expected_content_hash: preview.reviewed_evidence_content_hash,
        confirmed_at: new Date().toISOString().slice(0, 19),
        idempotency_key: `v6-gov-confirm-${runSuffix}`,
        lines: preview.lines.map((line: Json) => ({
          fee_code: line.fee_code,
          quantity: line.quantity,
          confirmed_payable_amount: line.payable_amount,
        })),
      },
    )
    const govDraftId = confirmation.draft_id as string
    const govSourceFacts = await api(request, token, 'GET', `/fees/drafts/${govDraftId}/source-facts`)
    expect(govSourceFacts.fee_domain).toBe('GOV')
    expect(govSourceFacts.lines.every((line: Json) => line.adjustable === false)).toBe(true)
    results.push({
      stage: '07',
      label: '生效官费预览',
      preview_digest: preview.preview_digest,
      rate_book_sha256: preview.rate_book_sha256,
      line_count: preview.lines.length,
      total_payable_amount: preview.total_payable_amount,
      gov_draft_id: govDraftId,
    })
  })

  let serviceDraftId = ''
  let govDraftId = results.find((item) => item.stage === '07')!.gov_draft_id as string
  await test.step('08 双草单与服务费调整', async () => {
    const obligation = await api(request, token, 'POST', '/fees/demo-service-obligations', {
      case_id: caseId,
      idempotency_key: `v6-service-obligation-${runSuffix}`,
    })
    const obligationId = obligation.obligation.id as string
    await api(request, token, 'POST', `/fees/obligations/${obligationId}/instruction`, {
      instruction: 'PAY',
      idempotency_key: `v6-service-pay-${runSuffix}`,
    })
    const serviceDraft = await api(request, token, 'POST', '/fees/drafts', {
      case_id: caseId,
      client_id: clientId,
      draft_type: 'GENERIC',
      currency: 'CNY',
      obligation_id: obligationId,
    })
    serviceDraftId = serviceDraft.id as string
    const before = await api(request, token, 'GET', `/fees/drafts/${serviceDraftId}/source-facts`)
    const adjustable = (before.lines as Json[]).find((line) => line.adjustable === true)
    expect(adjustable).toBeDefined()
    const adjusted = await api(request, token, 'POST', `/fees/drafts/${serviceDraftId}/demo-service-adjustment`, {
      item_id: adjustable!.current_item_id,
      expected_quantity: adjustable!.quantity,
      new_quantity: adjustable!.quantity + 1,
      reason: '客户确认增加一份附加文件处理',
      idempotency_key: `v6-service-adjustment-${runSuffix}`,
    })
    await api(request, token, 'POST', `/fees/drafts/${govDraftId}/lock`)
    await api(request, token, 'POST', `/fees/drafts/${serviceDraftId}/lock`)
    await expectNormalPage(page, `/fees/drafts/${govDraftId}`, '此草稿已锁定，解锁后方可编辑。')
    await page.getByRole('tab', { name: '概览' }).click()
    await expect(page.getByText('官费草单：全部明细只读')).toBeVisible()
    await expect(page.getByText('计算与来源', { exact: true })).toBeVisible()
    await expectNormalPage(page, `/fees/drafts/${serviceDraftId}`, '此草稿已锁定，解锁后方可编辑。')
    await page.getByRole('tab', { name: '概览' }).click()
    const serviceSourceFacts = page.getByTestId('draft-source-facts')
    await expect(serviceSourceFacts.getByText('服务费草单：仅授权项目可调整一次')).toBeVisible()
    await expect(serviceSourceFacts.getByText('客户确认增加一份附加文件处理')).toBeVisible()
    const after = await api(request, token, 'GET', `/fees/drafts/${serviceDraftId}/source-facts`)
    expect(after.draft_status).toBe('LOCKED')
    expect(after.lines.some((line: Json) => Boolean(line.adjustment_activity_id))).toBe(true)
    results.push({
      stage: '08',
      label: '双草单与服务费调整',
      gov_draft_id: govDraftId,
      service_draft_id: serviceDraftId,
      adjustment_activity_id: adjusted.adjustment_activity_id,
      before_total: adjusted.before_total,
      after_total: adjusted.after_total,
      gov_status: 'LOCKED',
      service_status: after.draft_status,
    })
  })

  await test.step('09 官费清单与待凭证登记', async () => {
    const govItems = await api(request, token, 'GET', `/fees/drafts/${govDraftId}/items`)
    const payListResult = await api(request, token, 'POST', '/pay-lists/from-fee-items', {
      fee_item_ids: (govItems as unknown as Json[]).map((item) => item.id),
      planned_pay_date: '2026-08-25',
      remark: '授权登记官费清单',
    })
    const payListId = payListResult.pay_list.id as number
    const govPaymentIds: number[] = []
    for (const line of payListResult.success as Json[]) {
      const registered = await api(request, token, 'POST', '/gov-payments/demo-command', {
        pay_list_id: payListId,
        fee_item_id: line.fee_item_id,
        paid_date: '2026-08-25',
        paid_amount: line.amount,
        official_receipt_no: null,
        voucher_no: null,
        invoice_no: null,
        remark: '已登记，待官方凭证核验',
        idempotency_key: `v6-gov-payment-${runSuffix}-${line.fee_item_id}`,
      })
      expect(registered.fact_status).toBe('REGISTERED_PENDING_OFFICIAL_EVIDENCE')
      govPaymentIds.push(registered.gov_payment.id as number)
    }
    await expectNormalPage(page, `/annuity/pay-lists/${payListId}`, '已登记，待官方凭证核验')
    results.push({
      stage: '09',
      label: '官费清单与待凭证登记',
      pay_list_id: payListId,
      gov_payment_ids: govPaymentIds,
      fact_status: 'REGISTERED_PENDING_OFFICIAL_EVIDENCE',
      official_evidence_fields: { official_receipt_no: null, voucher_no: null, invoice_no: null },
    })
  })

  let billId = ''
  await test.step('10 两次客户回款与核销', async () => {
    const billResult = await api(request, token, 'POST', '/bills/demo-from-draft', {
      draft_id: serviceDraftId,
      bill_no: `AR-CYZN-${runSuffix}`,
      bill_date: '2026-08-25',
      due_date: '2026-09-24',
      idempotency_key: `v6-bill-${runSuffix}`,
    })
    billId = billResult.bill.id as string
    const firstReceipt = await api(request, token, 'POST', '/payments/demo-bank-receipts', {
      target_bill_id: billId,
      amount: '1200.00',
      pay_no: `RCPT-CYZN-${runSuffix}-01`,
      pay_date: '2026-08-25',
      currency: 'CNY',
      pay_method: 'BANK_TRANSFER',
      bank_ref_no: `BTR-CYZN-${runSuffix}-01`,
      remark: '澄岳智造技术（苏州）有限公司第一笔客户回款',
      idempotency_key: `v6-receipt-${runSuffix}-01`,
    })
    const firstOffset = await api(request, token, 'POST', '/offsets/demo-full', {
      payment_line_id: firstReceipt.line.id,
      bill_id: billId,
      offset_amt: firstReceipt.line.balance_amt,
      offset_date: '2026-08-25',
      idempotency_key: `v6-offset-${runSuffix}-01`,
    })
    expect(firstOffset.bill.status).toBe('PARTIALLY_SETTLED')
    await expectNormalPage(page, `/billing/bills/${billId}`, '部分结清')
    const authoritativePartialBill = await api(request, token, 'GET', `/bills/${billId}`)
    const secondAmount = authoritativePartialBill.balance as string
    const secondReceipt = await api(request, token, 'POST', '/payments/demo-bank-receipts', {
      target_bill_id: billId,
      amount: secondAmount,
      pay_no: `RCPT-CYZN-${runSuffix}-02`,
      pay_date: '2026-08-26',
      currency: 'CNY',
      pay_method: 'BANK_TRANSFER',
      bank_ref_no: `BTR-CYZN-${runSuffix}-02`,
      remark: '澄岳智造技术（苏州）有限公司第二笔客户回款',
      idempotency_key: `v6-receipt-${runSuffix}-02`,
    })
    const secondOffset = await api(request, token, 'POST', '/offsets/demo-full', {
      payment_line_id: secondReceipt.line.id,
      bill_id: billId,
      offset_amt: secondReceipt.line.balance_amt,
      offset_date: '2026-08-26',
      idempotency_key: `v6-offset-${runSuffix}-02`,
    })
    expect(secondOffset.bill.status).toBe('SETTLED')
    expect(secondOffset.bill.balance).toBe('0.00')
    await expectNormalPage(page, `/billing/bills/${billId}`, '已结清')
    await expectNormalPage(page, `/billing/payments?bill_id=${billId}`, '登记回款不等于账单核销')
    await expectNormalPage(page, `/billing/offsets?bill_id=${billId}`, '核销记录与客户回款是不同业务对象')
    results.push({
      stage: '10',
      label: '两次客户回款与核销',
      bill_id: billId,
      first_payment_id: firstReceipt.payment.id,
      first_offset_id: firstOffset.offset.id,
      partial_status: firstOffset.bill.status,
      partial_balance: firstOffset.bill.balance,
      second_payment_id: secondReceipt.payment.id,
      second_offset_id: secondOffset.offset.id,
      final_status: secondOffset.bill.status,
      final_balance: secondOffset.bill.balance,
      amount_equation: `${firstReceipt.payment.amount} + ${secondReceipt.payment.amount} = ${secondOffset.bill.amount}`,
    })
  })

  await test.step('11 同案双轨汇总', async () => {
    await expectNormalPage(page, `/cases/${caseId}`, '同案双轨费用概览')
    await expect(page.getByText('官费轨：', { exact: false })).toBeVisible()
    await expect(page.getByText('服务费轨：', { exact: false })).toBeVisible()
    const finalBill = await api(request, token, 'GET', `/bills/${billId}`)
    expect(finalBill.status).toBe('SETTLED')
    expect(finalBill.balance).toBe('0.00')
    results.push({
      stage: '11',
      label: '同案双轨汇总',
      case_id: caseId,
      gov_draft_id: govDraftId,
      service_draft_id: serviceDraftId,
      bill_id: billId,
      bill_status: finalBill.status,
      bill_balance: finalBill.balance,
      console_errors: consoleErrors,
      network_errors: networkErrors,
    })
  })

  expect(results.map((item) => item.stage)).toEqual(v6Stages.map(([stage]) => stage))
  expect(consoleErrors).toEqual([])
  expect(networkErrors).toEqual([])
  await mkdir(evidenceDir!, { recursive: true })
  await page.screenshot({ path: path.join(evidenceDir!, 'v6-final.png'), fullPage: true })
  await writeFile(
    path.join(evidenceDir!, 'v6-stages.json'),
    JSON.stringify({ stages: results, network_errors: networkErrors, console_errors: consoleErrors }, null, 2),
  )
})
