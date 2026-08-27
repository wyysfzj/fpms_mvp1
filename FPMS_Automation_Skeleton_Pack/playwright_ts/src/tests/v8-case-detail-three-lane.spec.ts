import { expect, test } from '@playwright/test'
import type { Page, Request, Route } from '@playwright/test'

const caseId = 'case-v8-three-lane'

test('案件详情首屏展示三轨当前摘要并按需展开完整历史', async ({ page }) => {
    const overlayRequests: Request[] = []
    const mutationRequests: string[] = []
    await mockCaseOverlay(page, completeOverlay(), overlayRequests, mutationRequests)
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-three-lane-token')
    })
    await page.setViewportSize({ width: 1024, height: 900 })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    const overlay = page.getByTestId('case-lifecycle-overlay')
    await expect(overlay.getByTestId('lifecycle-summary-grid')).toBeVisible()
    await expect.poll(() => overlayRequests.length).toBe(1)
    await expect(overlay.getByText('快照修订：7', { exact: true })).toBeVisible()

    const document = overlay.getByTestId('lifecycle-summary-document')
    const lifecycle = overlay.getByTestId('lifecycle-summary-lifecycle')
    const fee = overlay.getByTestId('lifecycle-summary-fee')
    await expect(document).toContainText('当前文件版本 2 份')
    await expect(document).toContainText('已复核 1、待复核 1')
    await expect(document).toContainText('审查意见答复已递交')
    await expect(document).toContainText('2026-08-20')
    await expect(document).toContainText('提交答复材料')
    await expect(document).toContainText('2026-09-10')
    await expect(lifecycle).toContainText('实质审查')
    await expect(lifecycle).toContainText('官方程序阶段：实质审查 → 审查意见答复')
    await expect(lifecycle).not.toContainText('未确认的更高序列变化')
    await expect(lifecycle).toContainText('提交答复材料')
    await expect(fee).toContainText('官费：CNY 1 项')
    await expect(fee).toContainText('服务费：CNY 1 项、USD 1 项')
    await expect(fee).toContainText('官费 · 授权登记官费义务')
    await expect(fee).toContainText('服务费 · 费用活动待确认')
    await expect(fee).toContainText('2026-08-22')
    await expect(fee).toContainText('核对官费缴费任务')
    await expect(fee).not.toContainText('提交答复材料')
    await expect(fee).toContainText('服务费余额以客户账单页为准')
    await expect(overlay.getByText('现在是什么状态', { exact: true })).toHaveCount(3)
    await expect(overlay.getByText('最近发生了什么', { exact: true })).toHaveCount(3)
    await expect(overlay.getByText('下一步是什么', { exact: true })).toHaveCount(3)
    await expect(overlay.getByTestId('lifecycle-history-details')).toHaveCount(0)
    await expect(overlay).not.toContainText('客户余额')
    await expect(overlay).not.toContainText('4050.00')
    for (const rawCode of [
        'UNKNOWN_DOCUMENT_ACTIVITY',
        'SUBSTANTIVE_EXAMINATION',
        'OFFICE_ACTION_RESPONSE',
        'GRANT_REGISTRATION_OFFICIAL_FEES',
        'UNRECOGNIZED_FEE_OBLIGATION',
    ]) {
        await expect(overlay.getByText(rawCode, { exact: false })).toHaveCount(0)
    }

    const desktopBoxes = await Promise.all([
        document.boundingBox(),
        lifecycle.boundingBox(),
        fee.boundingBox(),
    ])
    expect(desktopBoxes.every((box) => box !== null)).toBe(true)
    expect(new Set(desktopBoxes.map((box) => Math.round(box!.y))).size).toBe(1)

    await page.setViewportSize({ width: 860, height: 1000 })
    const mobileBoxes = await Promise.all([
        document.boundingBox(),
        lifecycle.boundingBox(),
        fee.boundingBox(),
    ])
    expect(mobileBoxes[0]!.y).toBeLessThan(mobileBoxes[1]!.y)
    expect(mobileBoxes[1]!.y).toBeLessThan(mobileBoxes[2]!.y)

    await page.setViewportSize({ width: 1200, height: 900 })
    const toggle = overlay.getByTestId('lifecycle-history-toggle')
    await expect(toggle).toHaveText('查看完整历史')
    await expect(toggle).toHaveAttribute('aria-expanded', 'false')
    await toggle.click()
    const details = overlay.getByTestId('lifecycle-history-details')
    await expect(details).toBeVisible()
    await expect(toggle).toHaveText('收起完整历史')
    await expect(toggle).toHaveAttribute('aria-expanded', 'true')
    expect(
        await details.locator('[data-overlay-lane]').evaluateAll((nodes) =>
            nodes.map((node) => node.getAttribute('data-overlay-lane')),
        ),
    ).toEqual(['document', 'lifecycle', 'fee'])
    expect(overlayRequests).toHaveLength(1)
    await toggle.click()
    await expect(details).toHaveCount(0)
    await expect(overlay.getByTestId('lifecycle-summary-grid')).toBeVisible()
    expect(overlayRequests).toHaveLength(1)
    expect(mutationRequests).toEqual([])
    await expect(page.locator('.case-stepper-section')).toHaveCount(0)
})

test('空 overlay 使用中性中文空态且不推断下一步', async ({ page }) => {
    const overlayRequests: Request[] = []
    const mutationRequests: string[] = []
    await mockCaseOverlay(page, emptyOverlay(), overlayRequests, mutationRequests)
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-three-lane-empty-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    const overlay = page.getByTestId('case-lifecycle-overlay')
    await expect(overlay.getByTestId('lifecycle-summary-document')).toContainText('暂无文件证据事实')
    await expect(overlay.getByTestId('lifecycle-summary-lifecycle')).toContainText('官方程序阶段：暂无')
    await expect(overlay.getByTestId('lifecycle-summary-fee')).toContainText('暂无费用义务事实')
    await expect(overlay.getByText('暂无明确下一步', { exact: true })).toHaveCount(3)
    expect(overlayRequests).toHaveLength(1)
    expect(mutationRequests).toEqual([])
})

async function mockCaseOverlay(
    page: Page,
    overlayBody: Record<string, unknown>,
    overlayRequests: Request[],
    mutationRequests: string[],
): Promise<void> {
    await page.route('**/api/v1/**', async (route) => {
        const request = route.request()
        const url = new URL(request.url())
        const apiPath = url.pathname.replace(/^\/api\/v1/, '')
        if (!['GET', 'HEAD', 'OPTIONS'].includes(request.method())) {
            mutationRequests.push(`${request.method()} ${apiPath}`)
        }
        if (request.method() === 'GET' && apiPath === '/auth/me') {
            return fulfillJson(route, { permissions: ['Case.Read', 'Doc.Read', 'Task.Read', 'Fee.Read'] })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}`) {
            return fulfillJson(route, backendCase())
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}/lifecycle-overlay`) {
            overlayRequests.push(request)
            return fulfillJson(route, overlayBody)
        }
        if (request.method() === 'GET' && apiPath === '/tasks') {
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        return fulfillJson(route, { detail: `未处理的三线布局模拟请求：${apiPath}` }, 404)
    })
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function backendCase() {
    return {
        id: caseId,
        case_no: 'V8-THREE-LANE-001',
        case_type: 'NORMAL',
        patent_category: 'INV',
        flow_dir: 'CN_DOMESTIC',
        title_cn: '三线案件详情测试',
        status: 'SUB_EXAM',
        applicants: [],
        inventors: [],
        priorities: [],
        bio_deposits: [],
        agent_splits: [],
    }
}

function baseMilestone(sequence: number, lane: 'DOCUMENT' | 'LIFECYCLE' | 'FEE') {
    return {
        sequence,
        activity_id: `activity-${sequence}`,
        lane,
        activity_type: 'UNKNOWN_DOCUMENT_ACTIVITY',
        source_activity_id: null,
        effective_at: `2026-08-${String(sequence).padStart(2, '0')}T10:00:00Z`,
        confirmation_status: 'CONFIRMED',
        center_changes: {},
        document_evidence: [],
        work_packages: [],
        tasks: [],
        fee_obligations: [],
        evidence_summary: [],
        warnings: [],
    }
}

function evidenceVersion(id: string, reviewState: 'APPROVED' | 'PENDING') {
    return {
        evidence_version_id: id,
        case_id: caseId,
        document_id: `document-${id}`,
        attachment_id: `attachment-${id}`,
        lineage_key: `lineage-${id}`,
        role: 'OFFICIAL_FINAL_PDF',
        version_number: 1,
        state: 'FINAL',
        creator_id: 'user-1',
        review_state: reviewState,
        reviewer_id: reviewState === 'APPROVED' ? 'reviewer-1' : null,
        reviewed_at: reviewState === 'APPROVED' ? '2026-08-18T10:00:00Z' : null,
        final_submitted_at: null,
        content_hash: `hash-${id}`,
        is_current: true,
        is_final: true,
    }
}

function task(taskId: string, title: string, dueDate: string) {
    return {
        task_id: taskId,
        document_id: null,
        task_template_id: null,
        title,
        due_date: dueDate,
        internal_due_date: null,
        status: 'OPEN',
        done_at: null,
    }
}

function feeObligation(
    obligationId: string,
    feeDomain: 'GOV' | 'SERVICE',
    currency: string,
    obligationType: string,
) {
    return {
        obligation_id: obligationId,
        source_activity_id: 'activity-70',
        source_document_id: null,
        source_status: 'VERIFIED',
        fee_domain: feeDomain,
        obligation_type: obligationType,
        due_date: null,
        currency,
        statuses: {
            estimate_status: null,
            obligation_status: 'RECOGNIZED',
            client_instruction_status: 'PENDING',
            draft_status: 'NOT_CREATED',
            pay_list_status: 'NOT_CREATED',
            payment_status: 'UNPAID',
            official_evidence_status: 'PENDING',
        },
        lines: [],
        related_facts: [],
        supersedes_obligation_id: null,
        supersede_reason: null,
    }
}

function completeOverlay(): Record<string, unknown> {
    const documentOlder = {
        ...baseMilestone(10, 'DOCUMENT'),
        document_evidence: [{ version: evidenceVersion('approved', 'APPROVED'), derivations: [] }],
        tasks: [task('task-global', '旧答复任务标题', '2026-09-12')],
    }
    const lifecycleOlder = {
        ...baseMilestone(20, 'LIFECYCLE'),
        center_changes: {
            OFFICIAL_PROCEDURE_STAGE: {
                previous_value: 'PUBLISHED',
                current_value: 'SUBSTANTIVE_EXAMINATION',
            },
        },
    }
    const feeOlder = {
        ...baseMilestone(30, 'FEE'),
        tasks: [task('task-fee', '旧官费任务标题', '2026-09-20')],
    }
    const lifecycleLatest = {
        ...baseMilestone(50, 'LIFECYCLE'),
        effective_at: '2026-08-19T10:00:00Z',
        center_changes: {
            OFFICIAL_PROCEDURE_STAGE: {
                previous_value: 'SUBSTANTIVE_EXAMINATION',
                current_value: 'OFFICE_ACTION_RESPONSE',
            },
        },
    }
    const documentLatest = {
        ...baseMilestone(60, 'DOCUMENT'),
        activity_type: 'OA_EXTERNAL_SUBMISSION_RECORDED',
        effective_at: '2026-08-20T10:00:00Z',
        document_evidence: [
            { version: evidenceVersion('approved', 'APPROVED'), derivations: [] },
            { version: evidenceVersion('pending', 'PENDING'), derivations: [] },
        ],
        tasks: [task('task-global', '提交答复材料', '2026-09-10')],
    }
    const feeLatest = {
        ...baseMilestone(70, 'FEE'),
        activity_type: 'FEE_OBLIGATION_RECOGNIZED',
        effective_at: '2026-08-22T10:00:00Z',
        tasks: [task('task-fee', '核对官费缴费任务', '2026-09-15')],
        fee_obligations: [
            feeObligation('gov-cny', 'GOV', 'CNY', 'GRANT_REGISTRATION_OFFICIAL_FEES'),
            feeObligation('service-cny', 'SERVICE', 'CNY', 'SERVICE_FEE'),
            feeObligation('service-usd', 'SERVICE', 'USD', 'UNRECOGNIZED_FEE_OBLIGATION'),
        ],
    }
    const lifecycleUnconfirmed = {
        ...baseMilestone(80, 'LIFECYCLE'),
        activity_type: 'UNCONFIRMED_HIGHER_CHANGE',
        confirmation_status: 'NEEDS_REVIEW',
        center_changes: {
            OFFICIAL_PROCEDURE_STAGE: {
                previous_value: 'OFFICE_ACTION_RESPONSE',
                current_value: 'GRANT_REGISTRATION',
            },
        },
    }
    return {
        case_id: caseId,
        lifecycle_revision: 7,
        generated_at: '2026-08-23T12:00:00Z',
        center_snapshot: {
            business_stage: 'PROSECUTION_MANAGEMENT',
            official_procedure_stage: 'SUBSTANTIVE_EXAMINATION',
            legal_status: 'APPLICATION_PENDING',
            effective_at: '2026-08-23T11:00:00Z',
            verification_status: 'CONFIRMED',
            source_event_id: 'activity-current',
        },
        milestones: [
            documentOlder,
            lifecycleOlder,
            feeOlder,
            lifecycleLatest,
            documentLatest,
            feeLatest,
            lifecycleUnconfirmed,
        ],
        decision_gates: [],
        warnings: [],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}

function emptyOverlay(): Record<string, unknown> {
    return {
        case_id: caseId,
        lifecycle_revision: 7,
        generated_at: '2026-08-09T12:00:00Z',
        center_snapshot: {
            business_stage: null,
            official_procedure_stage: null,
            legal_status: null,
            effective_at: null,
            verification_status: null,
            source_event_id: null,
        },
        milestones: [],
        decision_gates: [],
        warnings: [],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}
