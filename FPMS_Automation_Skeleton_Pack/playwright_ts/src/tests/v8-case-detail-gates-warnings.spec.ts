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

test('案件详情无损展示 29 个客户决策和两级警告且不发起写请求', async ({ page }) => {
    const mutationRequests: string[] = []
    let overlayGetCount = 0
    await mockCaseOverlay(page, mutationRequests, () => {
        overlayGetCount += 1
    })
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-gates-warnings-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    const gates = page.getByTestId('overlay-decision-gates')
    await expect(gates.getByRole('heading', { name: '客户决策' })).toBeVisible()
    const rows = gates.locator('[data-gate-key]')
    await expect(rows).toHaveCount(29)
    const identities = await rows.evaluateAll((nodes) =>
        nodes.map((node) => node.getAttribute('data-gate-key')),
    )
    expect(identities).toEqual([
        ...nonLegacyCodes.map((code) => `${code}:case:${caseId}`),
        ...Array.from(
            { length: 22 },
            (_, index) => `DG-LEGACY-FORM-CLASS:form-${String(index + 1).padStart(3, '0')}`,
        ),
    ])
    await expect(
        gates.getByText('门禁代码：DG-LEGACY-FORM-CLASS', { exact: true }),
    ).toHaveCount(22)
    for (let number = 1; number <= 22; number += 1) {
        await expect(
            gates.getByText(`请求范围：form-${String(number).padStart(3, '0')}`, { exact: true }),
        ).toBeVisible()
    }

    for (const [index, [code, chinese]] of unresolvedReasons.entries()) {
        await expect(gates.getByText(`${chinese}（${code}）`, { exact: true })).toHaveCount(
            index === 0 ? 2 : 1,
        )
    }
    await expect(gates.getByText('请求范围：ALL-22', { exact: true })).toHaveCount(0)
    const unresolvedLegacy = rows.filter({
        has: page.getByText('请求范围：form-003', { exact: true }),
    })
    await expect(
        unresolvedLegacy.getByText(
            '未找到适用的客户决策（DECISION_GATE_NOT_FOUND）',
            { exact: true },
        ),
    ).toBeVisible()
    const direct = rows.filter({ has: page.getByText('请求范围：form-004', { exact: true }) })
    await expect(direct.getByText('解析范围：form-004', { exact: true })).toBeVisible()
    await expect(direct.getByText('来源引用：source-form-004', { exact: true })).toBeVisible()
    await expect(direct.getByText('来源版本：v1', { exact: true })).toBeVisible()
    const fallback = rows.filter({ has: page.getByText('请求范围：form-022', { exact: true }) })
    await expect(fallback.getByText('解析范围：ALL-22', { exact: true })).toBeVisible()
    await expect(fallback.getByText('来源引用：source-all-22', { exact: true })).toBeVisible()
    await expect(fallback.getByText('来源版本：v22', { exact: true })).toBeVisible()

    const historical = rows.filter({ has: page.getByText('决策值：HISTORICAL', { exact: true }) })
    await expect(historical.getByText('仅供参考', { exact: true })).toBeVisible()
    await expect(historical.getByText('非激活', { exact: true })).toBeVisible()
    const internal = rows.filter({ has: page.getByText('决策值：INTERNAL_ONLY', { exact: true }) })
    await expect(internal.getByText('仅供参考', { exact: true })).toBeVisible()
    await expect(internal.getByText('非激活', { exact: true })).toBeVisible()
    await expect(fallback.getByText('可供后续激活', { exact: true })).toBeVisible()

    const snapshotWarnings = page.getByTestId('overlay-snapshot-warnings')
    const activityWarnings = page.getByTestId('overlay-activity-warnings-activity-warning')
    await expect(snapshotWarnings.getByText('快照层重复警告', { exact: true })).toBeVisible()
    await expect(snapshotWarnings.getByText('快照层客户警告', { exact: true })).toBeVisible()
    await expect(snapshotWarnings.getByText('未核验', { exact: true })).toBeVisible()
    await expect(snapshotWarnings.getByText('客户待确认', { exact: true })).toBeVisible()
    await expect(activityWarnings.getByText('活动层重复警告', { exact: true })).toBeVisible()
    await expect(activityWarnings.getByText('活动层参考警告', { exact: true })).toBeVisible()
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
        [
            '客户待确认',
            '快照层客户警告',
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

    expect(overlayGetCount).toBe(1)
    expect(mutationRequests).toEqual([])
    await expect(page.getByRole('button', { name: /激活|确认|撤销/ })).toHaveCount(0)
})

async function mockCaseOverlay(
    page: Page,
    mutationRequests: string[],
    onOverlayGet: () => void,
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
            onOverlayGet()
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

function warning(kind: string, message: string, activityId: string | null) {
    return {
        kind,
        code: 'DUPLICATE-WARNING-CODE',
        message,
        activity_id: activityId,
        source_object_type: activityId ? 'Document' : 'Case',
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
                ],
            },
        ],
        decision_gates: decisionGates(),
        warnings: [
            warning('UNVERIFIED', '快照层重复警告', null),
            warning('CUSTOMER_DECISION_GATE', '快照层客户警告', null),
        ],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}
