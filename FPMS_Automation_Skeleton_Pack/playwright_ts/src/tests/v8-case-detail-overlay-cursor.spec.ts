import { expect, test } from '@playwright/test'
import type { Page, Request, Route } from '@playwright/test'

const caseId = 'case-v8-overlay-cursor'
const firstRevision = 41
const nonLegacyCodes = [
    'DG-FEE-APPLICATION-DRAFT',
    'DG-FEE-GRANT-YEAR-DRAFT',
    'DG-FEE-FUTURE-ANNUITY',
    'DG-GRANT-EVIDENCE-SOURCE',
    'DG-GRANT-MANUAL-REVIEW',
    'DG-PAYMENT-WORKBOOK',
    'DG-SERVICE-RATE-VERSION',
] as const

test('case overlay traverses one frozen revision with milestone dedupe and hidden gate diagnostics', async ({ page }) => {
    const overlayRequests: Request[] = []
    const mutationRequests: string[] = []
    await mockCaseOverlay(page, overlayRequests, mutationRequests)
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-overlay-cursor-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    await expect.poll(() => overlayRequests.length).toBe(1)
    expectOverlayQuery(overlayRequests[0], '0', null)
    await expect(page.getByText(`快照修订：${firstRevision}`, { exact: true })).toBeVisible()
    await expect(page.getByTestId('lifecycle-summary-document')).toBeVisible()
    await expect(page.getByTestId('lifecycle-summary-lifecycle')).toContainText('官方程序阶段：实质审查')
    await expect(page.getByTestId('lifecycle-summary-fee')).toBeVisible()
    await expect(page.getByText('尚有历史未加载，完整状态待确认', { exact: true })).toHaveCount(8)
    await expect(page.getByTestId('lifecycle-history-details')).toHaveCount(0)
    await expect(page.getByRole('button', { name: '加载更多生命周期记录', exact: true })).toHaveCount(0)

    await page.getByTestId('lifecycle-history-toggle').click()
    await expect(page.getByTestId('lifecycle-history-details')).toBeVisible()
    await expectMilestoneActivities(page, ['activity-010', 'activity-020', 'activity-030'])
    await expectGateDiagnosticsHidden(page)
    await expectProjectionLabels(page)

    const loadMore = page.getByRole('button', { name: '加载更多生命周期记录', exact: true })
    await expect(loadMore).toBeVisible()
    await expect(page.getByText('已加载全部生命周期记录', { exact: true })).toHaveCount(0)
    await loadMore.click()

    await expect.poll(() => overlayRequests.length).toBe(2)
    expectOverlayQuery(overlayRequests[1], '37', String(firstRevision))
    await expectMilestoneActivities(page, [
        'activity-010',
        'activity-020',
        'activity-030',
        'activity-040',
        'activity-050',
    ])
    await expect(page.getByTestId('center-change-activity-replayed-030')).toHaveCount(0)
    await expectGateDiagnosticsHidden(page)
    await expectProjectionLabels(page)
    await expect(page.getByText(`快照修订：${firstRevision}`, { exact: true })).toBeVisible()
    await expect(loadMore).toBeVisible()
    await expect(page.getByText('已加载全部生命周期记录', { exact: true })).toHaveCount(0)
    await loadMore.click()

    await expect.poll(() => overlayRequests.length).toBe(3)
    expectOverlayQuery(overlayRequests[2], '88', String(firstRevision))
    await expectMilestoneActivities(page, [
        'activity-010',
        'activity-020',
        'activity-030',
        'activity-040',
        'activity-050',
        'activity-060',
        'activity-070',
    ])
    await expect(page.getByTestId('center-change-activity-replayed-020')).toHaveCount(0)
    await expect(page.getByTestId('center-change-activity-replayed-050')).toHaveCount(0)
    await expectGateDiagnosticsHidden(page)
    await expectProjectionLabels(page)
    await expect(page.getByText(`快照修订：${firstRevision}`, { exact: true })).toBeVisible()
    await expect(loadMore).toHaveCount(0)
    await expect(page.getByText('已加载全部生命周期记录', { exact: true })).toBeVisible()
    await expect(page.getByText('尚有历史未加载，完整状态待确认', { exact: true })).toHaveCount(0)
    await expect(page.getByTestId('lifecycle-summary-lifecycle')).toContainText('2026-08-10T07:00:00Z')
    await page.waitForTimeout(250)
    expect(overlayRequests).toHaveLength(3)
    expect(mutationRequests).toEqual([])
})

test('invalid pages keep the accepted snapshot and retry the same cursor and revision', async ({ page }) => {
    const overlayRequests: Request[] = []
    const mutationRequests: string[] = []
    const invalidMessages = [
        '分页响应修订与首次修订不一致',
        '分页里程碑序列必须严格递增',
        '分页新增里程碑会破坏累计顺序',
        '分页响应缺少下一游标',
        '分页响应下一游标未前进',
    ]
    const terminalPage = {
        ...overlayPage(2),
        lifecycle_revision: firstRevision,
        milestones: [milestone(30, true), milestone(40)],
        next_cursor: null,
        has_more: false,
    }
    const responses = [
        overlayPage(1),
        { ...overlayPage(2), lifecycle_revision: firstRevision + 1 },
        {
            ...overlayPage(2),
            lifecycle_revision: firstRevision,
            milestones: [milestone(40), milestone(30)],
        },
        {
            ...overlayPage(2),
            lifecycle_revision: firstRevision,
            milestones: [milestone(25), milestone(30, true), milestone(40)],
        },
        {
            ...overlayPage(2),
            lifecycle_revision: firstRevision,
            milestones: [milestone(40)],
            next_cursor: null,
            has_more: true,
        },
        {
            ...overlayPage(2),
            lifecycle_revision: firstRevision,
            milestones: [milestone(40)],
            next_cursor: 37,
            has_more: true,
        },
        terminalPage,
    ]
    await mockCaseOverlay(page, overlayRequests, mutationRequests, (requestIndex) => responses[requestIndex])
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-overlay-cursor-invalid-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    await page.getByTestId('lifecycle-history-toggle').click()
    await expect(page.getByTestId('lifecycle-history-details')).toBeVisible()
    const loadMore = page.getByRole('button', { name: '加载更多生命周期记录', exact: true })
    await expect(loadMore).toBeVisible()
    for (const [index, message] of invalidMessages.entries()) {
        await loadMore.click()
        await expect.poll(() => overlayRequests.length).toBe(index + 2)
        expectOverlayQuery(overlayRequests[index + 1], '37', String(firstRevision))
        await expect(page.getByText(message, { exact: true })).toBeVisible()
        await expectMilestoneActivities(page, ['activity-010', 'activity-020', 'activity-030'])
        await expectGateDiagnosticsHidden(page)
        await expect(page.getByText('已加载全部生命周期记录', { exact: true })).toHaveCount(0)
        await expect(loadMore).toBeVisible()
    }

    await loadMore.click()
    await expect.poll(() => overlayRequests.length).toBe(7)
    expectOverlayQuery(overlayRequests[6], '37', String(firstRevision))
    await expectMilestoneActivities(page, [
        'activity-010',
        'activity-020',
        'activity-030',
        'activity-040',
    ])
    await expectGateDiagnosticsHidden(page)
    await expect(loadMore).toHaveCount(0)
    await expect(page.getByText('已加载全部生命周期记录', { exact: true })).toBeVisible()
    expect(mutationRequests).toEqual([])
})

async function expectMilestoneActivities(page: Page, activityIds: string[]): Promise<void> {
    const changes = page.getByTestId('lifecycle-center-lane').locator('.change-card')
    await expect(changes).toHaveCount(activityIds.length)
    expect(await changes.evaluateAll((nodes) => nodes.map((node) => node.getAttribute('data-testid')))).toEqual(
        activityIds.map((activityId) => `center-change-${activityId}`),
    )
}

async function expectGateDiagnosticsHidden(page: Page): Promise<void> {
    await expect(page.getByTestId('overlay-decision-gates')).toHaveCount(0)
    await expect(page.locator('[data-gate-key]')).toHaveCount(0)
    await expect(page.getByText('客户决策', { exact: true })).toHaveCount(0)
    await expect(page.getByText('DG-LEGACY-FORM-CLASS', { exact: false })).toHaveCount(0)
}

async function expectProjectionLabels(page: Page): Promise<void> {
    const center = page.getByLabel('当前案件生命周期状态')
    await expect(center.getByText('业务阶段：流程管理', { exact: true })).toBeVisible()
    await expect(center.getByText('官方程序阶段：实质审查', { exact: true })).toBeVisible()
    await expect(center.getByText('法律状态：申请审理中', { exact: true })).toBeVisible()
    await expect(center.getByText('核验状态：已确认', { exact: true })).toBeVisible()
    for (const rawValue of [
        'PROSECUTION_MANAGEMENT',
        'SUBSTANTIVE_EXAMINATION',
        'APPLICATION_PENDING',
        'CONFIRMED',
    ]) {
        await expect(center.getByText(rawValue, { exact: false })).toHaveCount(0)
    }
}

function expectOverlayQuery(request: Request, afterSequence: string, asOfRevision: string | null): void {
    const url = new URL(request.url())
    expect(url.searchParams.get('after_sequence')).toBe(afterSequence)
    expect(url.searchParams.get('limit')).toBe('200')
    expect(url.searchParams.get('as_of_revision')).toBe(asOfRevision)
}

async function mockCaseOverlay(
    page: Page,
    overlayRequests: Request[],
    mutationRequests: string[],
    responseForRequest: (requestIndex: number) => Record<string, unknown> = (requestIndex) =>
        overlayPage(requestIndex + 1),
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
            const requestIndex = overlayRequests.length
            overlayRequests.push(request)
            return fulfillJson(route, responseForRequest(requestIndex))
        }
        return fulfillJson(route, { detail: `未处理的游标界面模拟请求：${apiPath}` }, 404)
    })
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function backendCase(): Record<string, unknown> {
    return {
        id: caseId,
        case_no: 'V8-OVERLAY-CURSOR-001',
        case_type: 'NORMAL',
        patent_category: 'INV',
        flow_dir: 'CN_DOMESTIC',
        title_cn: '生命周期游标测试',
        status: 'SUB_EXAM',
        applicants: [],
        inventors: [],
        priorities: [],
        bio_deposits: [],
        agent_splits: [],
    }
}

function overlayPage(pageNumber: number): Record<string, unknown> {
    const pages = {
        1: {
            revision: firstRevision,
            milestones: [milestone(10), milestone(20), milestone(30)],
            nextCursor: 37,
            hasMore: true,
        },
        2: {
            revision: firstRevision,
            milestones: [milestone(30, true), milestone(40), milestone(50)],
            nextCursor: 88,
            hasMore: true,
        },
        3: {
            revision: firstRevision,
            milestones: [milestone(20, true), milestone(50, true), milestone(60), milestone(70)],
            nextCursor: null,
            hasMore: false,
        },
    } as const
    const current = pages[pageNumber as keyof typeof pages]
    return {
        case_id: caseId,
        lifecycle_revision: current.revision,
        generated_at: `2026-08-10T0${pageNumber}:00:00Z`,
        center_snapshot: {
            business_stage: 'PROSECUTION_MANAGEMENT',
            official_procedure_stage: 'SUBSTANTIVE_EXAMINATION',
            legal_status: 'APPLICATION_PENDING',
            effective_at: '2026-08-10T00:00:00Z',
            verification_status: 'CONFIRMED',
            source_event_id: 'activity-070',
        },
        milestones: current.milestones,
        decision_gates: decisionGates(pageNumber),
        warnings: [],
        legacy_conflicts: [],
        next_cursor: current.nextCursor,
        has_more: current.hasMore,
    }
}

function milestone(sequence: number, replayed = false): Record<string, unknown> {
    const suffix = String(sequence).padStart(3, '0')
    return {
        sequence,
        activity_id: replayed ? `activity-replayed-${suffix}` : `activity-${suffix}`,
        lane: 'LIFECYCLE',
        activity_type: replayed ? `REPLAYED_${suffix}` : `MILESTONE_${suffix}`,
        source_activity_id: null,
        effective_at: `2026-08-10T${String(Math.ceil(sequence / 10)).padStart(2, '0')}:00:00Z`,
        confirmation_status: 'CONFIRMED',
        center_changes: {
            BUSINESS_STAGE: {
                previous_value: 'INTAKE',
                current_value: 'PROSECUTION_MANAGEMENT',
            },
        },
        document_evidence: [],
        work_packages: [],
        tasks: [],
        fee_obligations: [],
        evidence_summary: [],
        warnings: [],
    }
}

function decisionGates(pageNumber: number): Record<string, unknown>[] {
    const nonLegacy = nonLegacyCodes.map((gateCode, index) => ({
        gate_code: gateCode,
        requested_scope_key: `case:${caseId}`,
        resolution_status: 'RESOLVED',
        gate_id: `gate-case-${index + 1}`,
        resolved_scope_key: `case:${caseId}`,
        decision_value: index === 0 ? `PAGE_${pageNumber}` : 'UNCHANGED',
        source_reference: index === 0 ? `case-source-page-${pageNumber}` : `case-source-${index + 1}`,
        source_version: `case-v${pageNumber}`,
        confirmed_by: 'reviewer-cursor',
        effective_at: '2026-08-10T00:00:00Z',
        unresolved_reason: null,
    }))
    const legacy = Array.from({ length: 22 }, (_, index) => {
        const requestedScope = `form-${String(index + 1).padStart(3, '0')}`
        const fallback = index === 21
        return {
            gate_code: 'DG-LEGACY-FORM-CLASS',
            requested_scope_key: requestedScope,
            resolution_status: 'RESOLVED',
            gate_id: `gate-${requestedScope}`,
            resolved_scope_key: fallback ? 'ALL-22' : requestedScope,
            decision_value: 'CURRENT_OFFICIAL',
            source_reference: fallback ? `fallback-source-page-${pageNumber}` : `source-${requestedScope}`,
            source_version: fallback ? `fallback-v${pageNumber}` : 'legacy-v1',
            confirmed_by: 'reviewer-cursor',
            effective_at: '2026-08-10T00:00:00Z',
            unresolved_reason: null,
        }
    })
    return [...nonLegacy, ...legacy]
}
