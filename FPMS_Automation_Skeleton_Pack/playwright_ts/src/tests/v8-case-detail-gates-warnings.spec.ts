import { expect, test } from '@playwright/test'
import type { Page, Route } from '@playwright/test'

const caseId = 'case-v8-gates-warnings'
const nonLegacyCodes = [
    'DG-FEE-APPLICATION-DRAFT',
    'DG-FEE-GRANT-YEAR-DRAFT',
    'DG-FEE-FUTURE-ANNUITY',
    'DG-GRANT-EVIDENCE-SOURCE',
    'DG-GRANT-MANUAL-REVIEW',
    'DG-PAYMENT-WORKBOOK',
    'DG-SERVICE-RATE-VERSION',
] as const
const unresolvedReasons = [
    ['DECISION_GATE_NOT_FOUND', '未找到适用的客户决策'],
    ['DECISION_GATE_REVOKED', '客户决策已撤销'],
    ['DECISION_GATE_NOT_EFFECTIVE', '客户决策尚未生效'],
    ['DECISION_GATE_CANDIDATE_MULTIPLICITY', '存在多个候选客户决策'],
    ['DECISION_GATE_CURRENT_IDENTITY_CONFLICT', '当前客户决策标识冲突'],
    ['DECISION_GATE_CURRENT_ROW_CORRUPT', '当前客户决策记录损坏'],
    ['DECISION_GATE_LEGACY_MAP_CORRUPT', '历史表单分类映射损坏'],
] as const

test('案件详情隐藏 29 个内部客户决策及其警告，保留普通警告且不发起写请求', async ({ page }) => {
    const mutationRequests: string[] = []
    const overlayGetUrls: string[] = []
    await mockCaseOverlay(page, mutationRequests, (url) => {
        overlayGetUrls.push(url)
    })
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-gates-warnings-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    await expect(page.getByTestId('overlay-decision-gates')).toHaveCount(0)
    await expect(page.getByRole('heading', { name: '客户决策' })).toHaveCount(0)
    await expect(page.locator('[data-gate-key]')).toHaveCount(0)
    await expect(page.getByText('DG-FEE-APPLICATION-DRAFT', { exact: false })).toHaveCount(0)
    await expect(page.getByText('DG-LEGACY-FORM-CLASS', { exact: false })).toHaveCount(0)
    await expect(page.getByTestId('lifecycle-history-details')).toHaveCount(0)
    await expect(page.getByTestId('lifecycle-history-toggle')).toBeVisible()

    const snapshotWarnings = page.getByTestId('overlay-snapshot-warnings')
    const activityWarnings = page.getByTestId('overlay-activity-warnings-activity-warning')
    await expect(page.getByText('活动层重复警告', { exact: true })).toHaveCount(1)
    await expect(snapshotWarnings.getByText('快照层重复警告', { exact: true })).toBeVisible()
    await expect(snapshotWarnings.getByText('快照层客户警告', { exact: true })).toHaveCount(0)
    await expect(snapshotWarnings.getByText('快照层客户来源警告', { exact: true })).toHaveCount(0)
    await expect(snapshotWarnings.getByText('未核验', { exact: true })).toBeVisible()
    await expect(activityWarnings.getByText('活动层重复警告', { exact: true })).toBeVisible()
    await expect(activityWarnings.getByText('活动层参考警告', { exact: true })).toBeVisible()
    await expect(activityWarnings.getByText('活动层客户来源警告', { exact: true })).toHaveCount(0)
    await expect(activityWarnings.getByText('来源冲突', { exact: true })).toBeVisible()
    await expect(activityWarnings.getByText('仅供参考', { exact: true })).toBeVisible()
    await expect(
        activityWarnings.getByText('来源对象：Document / document-warning', { exact: true }),
    ).toHaveCount(2)
    expect(
        await snapshotWarnings.locator('.warning-row').evaluateAll((nodes) =>
            nodes.map((node) =>
                Array.from(node.querySelectorAll('p')).map((value) => value.textContent?.trim()),
            ),
        ),
    ).toEqual([
        [
            '未核验',
            '快照层重复警告',
            '警告代码：DUPLICATE-WARNING-CODE',
            '关联活动：-',
            '来源对象：Case / case-v8-gates-warnings',
        ],
    ])
    expect(
        await activityWarnings.locator('.warning-row').evaluateAll((nodes) =>
            nodes.map((node) =>
                Array.from(node.querySelectorAll('p')).map((value) => value.textContent?.trim()),
            ),
        ),
    ).toEqual([
        [
            '来源冲突',
            '活动层重复警告',
            '警告代码：DUPLICATE-WARNING-CODE',
            '关联活动：activity-warning',
            '来源对象：Document / document-warning',
        ],
        [
            '仅供参考',
            '活动层参考警告',
            '警告代码：DUPLICATE-WARNING-CODE',
            '关联活动：activity-warning',
            '来源对象：Document / document-warning',
        ],
    ])

    expect(overlayGetUrls).toHaveLength(1)
    const overlayUrl = new URL(overlayGetUrls[0])
    expect(overlayUrl.searchParams.get('after_sequence')).toBe('0')
    expect(overlayUrl.searchParams.get('limit')).toBe('200')
    expect(overlayUrl.searchParams.get('as_of_revision')).toBeNull()
    expect(mutationRequests).toEqual([])
    await expect(page.getByRole('button', { name: /激活|确认|撤销/ })).toHaveCount(0)
})

async function mockCaseOverlay(
    page: Page,
    mutationRequests: string[],
    onOverlayGet: (url: string) => void,
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
            onOverlayGet(request.url())
            return fulfillJson(route, overlayResponse())
        }
        if (request.method() === 'GET' && apiPath === '/tasks') {
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        if (request.method() === 'GET' && apiPath === '/fees/drafts') {
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        return fulfillJson(route, { detail: `未处理的门禁警告模拟请求：${apiPath}` }, 404)
    })
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function backendCase() {
    return {
        id: caseId,
        case_no: 'V8-GATES-WARNINGS-001',
        case_type: 'NORMAL',
        patent_category: 'INV',
        flow_dir: 'CN_DOMESTIC',
        title_cn: '客户决策与警告测试',
        status: 'SUB_EXAM',
        applicants: [],
        inventors: [],
        priorities: [],
        bio_deposits: [],
        agent_splits: [],
    }
}

function decisionGates() {
    const unresolved = nonLegacyCodes.map((gateCode, index) => ({
        gate_code: gateCode,
        requested_scope_key: `case:${caseId}`,
        resolution_status: 'UNRESOLVED',
        gate_id: null,
        resolved_scope_key: null,
        decision_value: null,
        source_reference: null,
        source_version: null,
        confirmed_by: null,
        effective_at: null,
        unresolved_reason: unresolvedReasons[index][0],
    }))
    const legacy = Array.from({ length: 22 }, (_, index) => {
        const number = index + 1
        const requested = `form-${String(number).padStart(3, '0')}`
        if (number === 3) {
            return {
                gate_code: 'DG-LEGACY-FORM-CLASS',
                requested_scope_key: requested,
                resolution_status: 'UNRESOLVED',
                gate_id: null,
                resolved_scope_key: null,
                decision_value: null,
                source_reference: null,
                source_version: null,
                confirmed_by: null,
                effective_at: null,
                unresolved_reason: 'DECISION_GATE_NOT_FOUND',
            }
        }
        const decisionValue = number === 1 ? 'HISTORICAL' : number === 2 ? 'INTERNAL_ONLY' : 'CURRENT_OFFICIAL'
        return {
            gate_code: 'DG-LEGACY-FORM-CLASS',
            requested_scope_key: requested,
            resolution_status: 'RESOLVED',
            gate_id: `gate-${requested}`,
            resolved_scope_key: number === 22 ? 'ALL-22' : requested,
            decision_value: decisionValue,
            source_reference: number === 22 ? 'source-all-22' : `source-${requested}`,
            source_version: number === 22 ? 'v22' : 'v1',
            confirmed_by: 'reviewer-1',
            effective_at: '2026-08-09T12:00:00Z',
            unresolved_reason: null,
        }
    })
    return [...unresolved, ...legacy]
}

function warning(
    kind: string,
    message: string,
    activityId: string | null,
    sourceObjectType = activityId ? 'Document' : 'Case',
) {
    return {
        kind,
        code: 'DUPLICATE-WARNING-CODE',
        message,
        activity_id: activityId,
        source_object_type: sourceObjectType,
        source_object_id: activityId ? 'document-warning' : caseId,
    }
}

function overlayResponse() {
    return {
        case_id: caseId,
        lifecycle_revision: 8,
        generated_at: '2026-08-09T12:30:00Z',
        center_snapshot: {
            business_stage: 'PROSECUTION_MANAGEMENT',
            official_procedure_stage: 'SUBSTANTIVE_EXAMINATION',
            legal_status: 'APPLICATION_PENDING',
            effective_at: '2026-08-09T12:00:00Z',
            verification_status: 'CONFIRMED',
            source_event_id: 'activity-warning',
        },
        milestones: [
            {
                sequence: 8,
                activity_id: 'activity-warning',
                lane: 'DOCUMENT',
                activity_type: 'DOCUMENT_WARNING_RECORDED',
                source_activity_id: null,
                effective_at: '2026-08-09T12:00:00Z',
                confirmation_status: 'CONFIRMED',
                center_changes: {},
                document_evidence: [],
                work_packages: [],
                tasks: [],
                fee_obligations: [],
                evidence_summary: [],
                warnings: [
                    warning('CONFLICT', '活动层重复警告', 'activity-warning'),
                    warning('REFERENCE_ONLY', '活动层参考警告', 'activity-warning'),
                    warning(
                        'CONFLICT',
                        '活动层客户来源警告',
                        'activity-warning',
                        'CUSTOMER_DECISION_GATE',
                    ),
                ],
            },
        ],
        decision_gates: decisionGates(),
        warnings: [
            warning('CONFLICT', '活动层重复警告', 'activity-warning'),
            warning('UNVERIFIED', '快照层重复警告', null),
            warning('CUSTOMER_DECISION_GATE', '快照层客户警告', null),
            warning(
                'REFERENCE_ONLY',
                '快照层客户来源警告',
                null,
                'CUSTOMER_DECISION_GATE',
            ),
        ],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}
