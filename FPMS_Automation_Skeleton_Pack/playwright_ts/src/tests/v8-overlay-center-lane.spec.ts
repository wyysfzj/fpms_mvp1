import { expect, test } from '@playwright/test'
import type { Page, Route } from '@playwright/test'

const caseId = 'case-v8-overlay-center'

test('中央案件生命周期只展示当前三轴状态和已确认的中心变化', async ({ page }) => {
    await mockCaseOverlay(page)

    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-overlay-center-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    const lane = page.getByTestId('lifecycle-center-lane')
    await expect(lane.getByRole('heading', { name: '案件生命周期' })).toBeVisible()
    await expect(lane.getByText('业务阶段：PROSECUTION_MANAGEMENT', { exact: true })).toBeVisible()
    await expect(lane.getByText('官方程序阶段：SUBSTANTIVE_EXAMINATION', { exact: true })).toBeVisible()
    await expect(lane.getByText('法律状态：APPLICATION_PENDING', { exact: true })).toBeVisible()
    await expect(lane.getByText('核验状态：CONFIRMED', { exact: true })).toBeVisible()

    const confirmed = lane.getByTestId('center-change-activity-confirmed')
    await expect(confirmed.getByText('事件类型：SUBSTANTIVE_EXAMINATION_STARTED', { exact: true })).toBeVisible()
    await expect(confirmed.getByText('官方程序阶段：PRELIMINARY_EXAMINATION → SUBSTANTIVE_EXAMINATION', { exact: true })).toBeVisible()
    await expect(lane.getByTestId('center-change-activity-review')).toHaveCount(0)
    await expect(lane.getByText('PATENT_IN_FORCE', { exact: false })).toHaveCount(0)
})

async function mockCaseOverlay(page: Page): Promise<void> {
    await page.route('**/api/v1/**', async (route) => {
        const request = route.request()
        const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, '')
        if (request.method() === 'GET' && apiPath === '/auth/me') {
            return fulfillJson(route, {
                permissions: ['Case.Read', 'Doc.Read', 'Task.Read', 'Fee.Read'],
            })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}`) {
            return fulfillJson(route, {
                id: caseId,
                case_no: 'V8-CENTER-001',
                case_type: 'NORMAL',
                patent_category: 'INV',
                flow_dir: 'CN_DOMESTIC',
                title_cn: '中央案件生命周期测试',
                status: 'SUB_EXAM',
                applicants: [],
                inventors: [],
                priorities: [],
                bio_deposits: [],
                agent_splits: [],
            })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}/lifecycle-overlay`) {
            return fulfillJson(route, overlayResponse())
        }
        if (request.method() === 'GET' && apiPath === '/tasks') {
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        return fulfillJson(route, { detail: `未处理的中央生命周期模拟请求：${apiPath}` }, 404)
    })
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function milestone(
    activityId: string,
    confirmationStatus: 'CONFIRMED' | 'NEEDS_REVIEW',
    centerChanges: Record<string, { previous_value: string | null; current_value: string | null }>,
) {
    return {
        sequence: confirmationStatus === 'CONFIRMED' ? 1 : 2,
        activity_id: activityId,
        lane: 'LIFECYCLE',
        activity_type:
            confirmationStatus === 'CONFIRMED'
                ? 'SUBSTANTIVE_EXAMINATION_STARTED'
                : 'UNVERIFIED_GRANT_IMPORT',
        source_activity_id: null,
        effective_at: '2026-08-09T09:00:00Z',
        confirmation_status: confirmationStatus,
        center_changes: centerChanges,
        document_evidence: [],
        work_packages: [],
        tasks: [],
        fee_obligations: [],
        evidence_summary: [],
        warnings: [],
    }
}

function overlayResponse() {
    return {
        case_id: caseId,
        lifecycle_revision: 2,
        generated_at: '2026-08-09T09:00:01Z',
        center_snapshot: {
            business_stage: 'PROSECUTION_MANAGEMENT',
            official_procedure_stage: 'SUBSTANTIVE_EXAMINATION',
            legal_status: 'APPLICATION_PENDING',
            effective_at: '2026-08-09T09:00:00Z',
            verification_status: 'CONFIRMED',
            source_event_id: 'activity-confirmed',
        },
        milestones: [
            milestone('activity-confirmed', 'CONFIRMED', {
                OFFICIAL_PROCEDURE_STAGE: {
                    previous_value: 'PRELIMINARY_EXAMINATION',
                    current_value: 'SUBSTANTIVE_EXAMINATION',
                },
            }),
            milestone('activity-review', 'NEEDS_REVIEW', {
                LEGAL_STATUS: {
                    previous_value: 'APPLICATION_PENDING',
                    current_value: 'PATENT_IN_FORCE',
                },
            }),
        ],
        decision_gates: [],
        warnings: [],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}
