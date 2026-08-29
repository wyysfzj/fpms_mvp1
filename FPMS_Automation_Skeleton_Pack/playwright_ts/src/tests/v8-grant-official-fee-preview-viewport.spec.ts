import { expect, test } from '@playwright/test'
import type { Route } from '@playwright/test'

test.use({ viewport: { width: 1280, height: 720 } })

test('官费预览在标准演示视口中保留可点击确认动作', async ({ page }) => {
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, '')

    if (request.method() === 'GET' && apiPath === '/auth/me') {
      return fulfillJson(route, {
        id: 'viewport-user',
        username: 'viewport-user',
        permissions: ['GrantFeeTask.Read', 'GrantFeeTask.Write', 'Doc.Create'],
      })
    }
    if (request.method() === 'GET' && apiPath === '/grant-fee-tasks/list') {
      return fulfillJson(route, { items: [grantFeeTask()], page: 1, page_size: 20, total: 1 })
    }
    if (request.method() === 'GET' && apiPath === '/grant-fee-tasks/task-viewport/state') {
      return fulfillJson(route, grantFeeTaskState())
    }
    if (request.method() === 'GET' && apiPath === '/grant-fee-tasks/task-viewport/official-fee-preview') {
      return fulfillJson(route, officialFeePreview())
    }

    return fulfillJson(route, { detail: `未处理的视口测试请求：${apiPath}` }, 404)
  })

  await page.addInitScript(() => {
    window.localStorage.setItem('fpms_token', 'grant-preview-viewport-test-token')
  })

  await page.goto('/grant-fee/tasks', { waitUntil: 'domcontentloaded' })
  const taskRow = page.getByRole('row').filter({ hasText: 'VIEWPORT-GRANT-001' })
  await expect(taskRow).toContainText('可生成草单')
  await taskRow.getByRole('button', { name: '预览官费' }).click()

  const dialog = page.getByRole('dialog', { name: '授权登记官费预览' })
  const confirmButton = dialog.getByRole('button', { name: '确认官费并生成草单' })
  await expect(dialog).toBeVisible()

  const geometry = await confirmButton.evaluate((buttonElement) => {
    const dialogPanel = buttonElement.closest<HTMLElement>('.official-fee-preview-dialog')
    if (!dialogPanel) throw new Error('官费预览弹窗面板不存在')
    const dialogBounds = dialogPanel.getBoundingClientRect()
    const buttonBounds = buttonElement.getBoundingClientRect()
    const body = dialogPanel.querySelector<HTMLElement>('.el-dialog__body')
    const hitTarget = document.elementFromPoint(
      buttonBounds.x + buttonBounds.width / 2,
      buttonBounds.y + buttonBounds.height / 2,
    )
    return {
      dialogTopInViewport: dialogBounds.top >= 0,
      dialogBottomInViewport: dialogBounds.bottom <= window.innerHeight,
      buttonFullyVisible: buttonBounds.top >= 0 && buttonBounds.bottom <= window.innerHeight,
      buttonHitTarget: hitTarget === buttonElement || buttonElement.contains(hitTarget),
      bodyScrollable: Boolean(body && body.scrollHeight > body.clientHeight),
      bodyOverflowY: body ? getComputedStyle(body).overflowY : '',
    }
  })

  expect(geometry).toMatchObject({
    dialogTopInViewport: true,
    dialogBottomInViewport: true,
    buttonFullyVisible: true,
    buttonHitTarget: true,
    bodyScrollable: true,
    bodyOverflowY: 'auto',
  })
})

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function grantFeeTask(): Record<string, unknown> {
  return {
    task_id: 'task-viewport',
    case_id: 'case-viewport',
    case_no: 'VIEWPORT-GRANT-001',
    status: 'READY_TO_DRAFT',
    due_date: '2026-11-24',
    client_instruction: 'PAY',
    gov_fee_amt: 950,
    service_fee_amt: 0,
    currency: 'CNY',
    draft_generated: false,
    notice_sent: true,
    notify_count: 1,
    is_overdue: false,
    billed: false,
    linked_bill_id: null,
    linked_bill_no: null,
    trigger_rule: '收到授权通知',
    deadline_rule: '以办理登记手续通知书载明期限为准',
    fee_basis: '授权阶段官费',
    fee_node_explanation: '确认后生成只读官费草单',
    lineage_status: 'CONFIRMED',
    source_document_id: 'document-viewport',
    deadline_source: 'IMPORTED_OFFICIAL_NOTICE',
    deadline_confirmed_at: '2026-08-29T10:00:00',
    allowed_actions: [],
    state_binding_current: false,
    projection_valid: true,
  }
}

function grantFeeTaskState(): Record<string, unknown> {
  return {
    task_id: 'task-viewport',
    case_id: 'case-viewport',
    state: 'READY_TO_DRAFT',
    client_instruction: 'PAY',
    notify_count: 1,
    draft_generated: false,
    notice_sent: true,
    is_overdue: false,
    allowed_actions: ['mark_draft_generated'],
    trigger_rule: '收到授权通知',
    deadline_rule: '以办理登记手续通知书载明期限为准',
    fee_basis: '授权阶段官费',
    fee_node_explanation: '确认后生成只读官费草单',
    lineage_status: 'CONFIRMED',
    source_document_id: 'document-viewport',
    deadline_source: 'IMPORTED_OFFICIAL_NOTICE',
    deadline_confirmed_at: '2026-08-29T10:00:00',
    projection_valid: true,
  }
}

function officialFeePreview(): Record<string, unknown> {
  const digest = `sha256:${'a'.repeat(64)}`
  const line = (feeCode: string, feeName: string, amount: number) => ({
    fee_code: feeCode,
    fee_name: feeName,
    quantity: 1,
    unit_price: amount,
    calculation_mode: 'FIXED',
    candidate_amount: amount,
    official_full_amount: amount,
    payable_amount: amount,
    currency: 'CNY',
    source_reference: 'CNIPA',
    source_version: '2026-03-30',
    source_sha256: digest,
    rate_row_sha256: digest,
    effective_from: '2026-03-30',
    effective_to: null,
  })
  const state = {
    groups: [{ name: 'FeeObligation', identity_count: 1, identities: ['obligation-1'] }],
    digest,
  }
  return {
    grant_fee_task_id: 'task-viewport',
    case_id: 'case-viewport',
    source_document_id: 'document-viewport',
    reviewed_evidence_version_id: 'evidence-viewport',
    reviewed_evidence_content_hash: digest,
    source_authority: '国家知识产权局',
    rate_book_version: '2026-03-30',
    rate_book_sha256: digest,
    effective_from: '2026-03-30',
    effective_to: null,
    currency: 'CNY',
    lines: [
      line('CNIPA-GRANT-REGISTRATION', '授权登记费', 900),
      line('CNIPA-GRANT-ANNOUNCEMENT', '授权公告印刷费', 50),
    ],
    total_payable_amount: 950,
    preview_digest: digest,
    read_only_audit_snapshot: {
      schema_version: 'fpms.demo-read-only-audit-snapshot/v1',
      tracked_group_count: 1,
      total_identity_count: 1,
      before: state,
      after: state,
      unchanged: true,
    },
  }
}
