import { expect, test } from '@playwright/test'
import type { Page, Route } from '@playwright/test'

const caseId = 'case-v8-three-lane'

test('案件详情按文件、生命周期、费用顺序展示同一 overlay 快照', async ({ page }) => {
    const overlayQueries: URLSearchParams[] = []
    await page.route('**/api/v1/**', async (route) => {
        const request = route.request()
        const url = new URL(request.url())
        const apiPath = url.pathname.replace(/^\/api\/v1/, '')
        if (request.method() === 'GET' && apiPath === '/auth/me') {
            return fulfillJson(route, {
                permissions: ['Case.Read', 'Doc.Read', 'Task.Read', 'Fee.Read'],
            })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}`) {
            return fulfillJson(route, backendCase())
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}/lifecycle-overlay`) {
            overlayQueries.push(url.searchParams)
            return fulfillJson(route, emptyOverlay())
        }
        if (request.method() === 'GET' && apiPath === '/tasks') {
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        return fulfillJson(route, { detail: `未处理的三线布局模拟请求：${apiPath}` }, 404)
    })

    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-three-lane-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    const overlay = page.getByTestId('case-lifecycle-overlay')
    await expect(overlay).toBeVisible()
    await expect
        .poll(() =>
            overlayQueries.some(
                (query) => query.get('after_sequence') === '0' && query.get('limit') === '200',
            ),
        )
        .toBe(true)
    expect(overlayQueries).toHaveLength(1)
    await expect(overlay.getByText('快照修订：7', { exact: true })).toBeVisible()

    const laneOrder = await overlay.locator('[data-overlay-lane]').evaluateAll((nodes) =>
        nodes.map((node) => node.getAttribute('data-overlay-lane')),
    )
    expect(laneOrder).toEqual(['document', 'lifecycle', 'fee'])
    await expect(page.locator('.case-stepper-section')).toHaveCount(0)
})

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

function emptyOverlay() {
    return {
        case_id: caseId,
        lifecycle_revision: 7,
        generated_at: '2026-08-09T12:00:00Z',
        center_snapshot: {
            business_stage: 'PROSECUTION_MANAGEMENT',
            official_procedure_stage: 'SUBSTANTIVE_EXAMINATION',
            legal_status: 'APPLICATION_PENDING',
            effective_at: '2026-08-09T11:00:00Z',
            verification_status: 'CONFIRMED',
            source_event_id: 'activity-current',
        },
        milestones: [],
        decision_gates: [],
        warnings: [],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}
