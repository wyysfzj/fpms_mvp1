import { expect, test } from '@playwright/test'
import type { Page, Route } from '@playwright/test'

const caseId = 'case-v8-document-gate-applicability'

type Scenario = {
    name: string
    businessStage?: string
    officialStage?: string
    mode: 'current' | 'historical' | 'unknown'
}

const scenarios: readonly Scenario[] = [
    {
        name: '当前首次申请递交阶段保留阻断结论和动作',
        businessStage: 'FILING_PREPARATION',
        officialStage: 'NOT_SUBMITTED',
        mode: 'current',
    },
    {
        name: '授权登记阶段只展示历史首次申请核验',
        businessStage: 'GRANT_REGISTRATION_IN_PROGRESS',
        officialStage: 'GRANT_REGISTRATION',
        mode: 'historical',
    },
    {
        name: '缺失业务阶段时不推断门禁适用性',
        officialStage: 'GRANT_REGISTRATION',
        mode: 'unknown',
    },
    {
        name: '业务阶段与官方阶段冲突时不推断门禁适用性',
        businessStage: 'FILING_PREPARATION',
        officialStage: 'GRANT_REGISTRATION',
        mode: 'unknown',
    },
    {
        name: '未来未知阶段时不暴露原始阶段码或伪造结论',
        businessStage: 'FUTURE_BUSINESS_STAGE',
        officialStage: 'FUTURE_OFFICIAL_STAGE',
        mode: 'unknown',
    },
]

test.describe.serial('案件文件门禁阶段适用性', () => {
    for (const scenario of scenarios) {
        test(scenario.name, async ({ page }) => {
            const requests = await mockCaseDocumentGate(page, scenario)
            await openDocumentsTab(page)

            const panel = page.locator('.case-document-gate-panel')
            await expect(panel.getByRole('button', { name: '登记往来文件' }).first()).toBeVisible()

            if (scenario.mode === 'current') {
                await expect(panel.getByRole('heading', { name: '当前首次申请递交门禁' })).toBeVisible()
                await expect(panel.getByText('门禁结论', { exact: true })).toBeVisible()
                await expect(panel.getByText(/阻止/).last()).toBeVisible()
                await expect(panel.getByRole('button', { name: '登记往来文件' })).toHaveCount(2)
            } else if (scenario.mode === 'historical') {
                await expect(panel.getByText('当前阶段：授权登记', { exact: true })).toBeVisible()
                await expect(panel.getByRole('heading', { name: '历史首次申请递交材料核验' })).toBeVisible()
                await expect(panel.getByText('历史已匹配材料 0', { exact: true })).toBeVisible()
                await expect(panel.getByText('历史未匹配材料 2', { exact: true })).toBeVisible()
                await expect(panel.getByText('首次申请规则硬性缺失 是', { exact: true })).toBeVisible()
                await expect(panel.getByText('历史后补审计 不需要', { exact: true })).toBeVisible()
                await expect(panel.getByText('首次申请递交规则未满足（历史核验）', { exact: true })).toBeVisible()
                await expect(panel.getByText('历史核验说明', { exact: true })).toBeVisible()
                await expect(
                    panel.getByText('该结果用于追溯首次申请递交材料，不作为当前“授权登记”的阻断结论。', {
                        exact: true,
                    }),
                ).toBeVisible()
                await expect(panel.getByText('当前建议动作', { exact: true })).toHaveCount(0)
                await expect(panel.getByRole('button', { name: '登记往来文件' })).toHaveCount(1)
            } else {
                await expect(panel.getByRole('heading', { name: '适用阶段待确认' })).toBeVisible()
                await expect(panel.getByText(/不能将该规则标记为当前门禁或历史门禁/)).toBeVisible()
                await expect(panel.getByText('门禁结论', { exact: true })).toHaveCount(0)
                await expect(panel.getByText('历史规则结论', { exact: true })).toHaveCount(0)
                await expect(panel.getByRole('button', { name: '登记往来文件' })).toHaveCount(1)
            }

            await expect(panel.getByText('FUTURE_BUSINESS_STAGE', { exact: false })).toHaveCount(0)
            await expect(panel.getByText('FUTURE_OFFICIAL_STAGE', { exact: false })).toHaveCount(0)
            expect(requests.caseGets).toBe(2)
            expect(requests.gateGets).toBe(1)
            expect(requests.documentGets).toBe(1)
            expect(requests.mutations).toBe(0)
        })
    }

    test('案件元数据加载失败时使用中性适用性且保留门禁事实', async ({ page }) => {
        const requests = await mockCaseDocumentGate(page, {
            name: 'metadata-failure',
            businessStage: 'FILING_PREPARATION',
            officialStage: 'NOT_SUBMITTED',
            mode: 'unknown',
        }, true)
        await openDocumentsTab(page)

        const panel = page.locator('.case-document-gate-panel')
        await expect(panel.getByRole('heading', { name: '适用阶段待确认' })).toBeVisible()
        await expect(panel.getByText('案件阶段信息加载失败', { exact: true })).toBeVisible()
        await expect(panel.getByText('缺失材料 2', { exact: true })).toBeVisible()
        await expect(panel.getByText('门禁结论', { exact: true })).toHaveCount(0)
        expect(requests.caseGets).toBe(2)
        expect(requests.gateGets).toBe(1)
        expect(requests.documentGets).toBe(1)
        expect(requests.mutations).toBe(0)
    })
})

async function openDocumentsTab(page: Page): Promise<void> {
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-document-gate-applicability-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    await page.getByRole('tab', { name: '往来文件' }).click()
    await expect(page.locator('.case-document-gate-panel')).toBeVisible()
}

async function mockCaseDocumentGate(
    page: Page,
    scenario: Scenario,
    failChildCaseMetadata = false,
): Promise<{ caseGets: number; gateGets: number; documentGets: number; mutations: number }> {
    const requests = { caseGets: 0, gateGets: 0, documentGets: 0, mutations: 0 }
    await page.route('**/api/v1/**', async (route) => {
        const request = route.request()
        const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, '')
        if (request.method() !== 'GET') {
            requests.mutations += 1
        }
        if (request.method() === 'GET' && apiPath === '/auth/me') {
            return fulfillJson(route, {
                permissions: ['Case.Read', 'Doc.Read', 'Task.Read', 'Fee.Read'],
            })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}`) {
            requests.caseGets += 1
            if (failChildCaseMetadata && requests.caseGets === 2) {
                return fulfillJson(route, { code: 'CASE_METADATA_UNAVAILABLE', message: '案件阶段信息加载失败' }, 500)
            }
            return fulfillJson(route, caseResponse(scenario))
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}/document-gate`) {
            requests.gateGets += 1
            return fulfillJson(route, blockedGateResponse())
        }
        if (request.method() === 'GET' && apiPath === '/documents') {
            requests.documentGets += 1
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        if (request.method() === 'GET' && apiPath === `/clients/client-gate/contacts`) {
            return fulfillJson(route, [])
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}/lifecycle-overlay`) {
            return fulfillJson(route, emptyOverlayResponse())
        }
        if (request.method() === 'GET' && apiPath === '/tasks') {
            return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 })
        }
        return fulfillJson(route, { detail: `未处理的案件门禁适用性模拟请求：${apiPath}` }, 404)
    })
    return requests
}

function caseResponse(scenario: Scenario): Record<string, unknown> {
    return {
        id: caseId,
        case_no: 'CYIP-CN-INV-7906842426',
        case_type: 'NORMAL',
        patent_category: 'INV',
        flow_dir: 'CN_DOMESTIC',
        title_cn: '一种柔性制造产线中视觉检测工位的自适应标定方法',
        client_id: 'client-gate',
        status: 'GRANT_PENDING',
        business_stage: scenario.businessStage,
        official_procedure_stage: scenario.officialStage,
        applicants: [],
        inventors: [],
        priorities: [],
        bio_deposits: [],
        agent_splits: [],
        created_at: '2026-08-01T09:00:00',
        updated_at: '2026-08-12T09:00:00',
    }
}

function blockedGateResponse(): Record<string, unknown> {
    const missing = [
        {
            requirement_code: 'APPLICATION_REQUEST',
            requirement_name: '申请请求书',
            role: '递交主文件',
            blocks_submission: true,
            afterfill_allowed: false,
            status: 'MISSING',
            matched_documents: [],
        },
        {
            requirement_code: 'DESCRIPTION',
            requirement_name: '说明书',
            role: '技术文件',
            blocks_submission: true,
            afterfill_allowed: false,
            status: 'MISSING',
            matched_documents: [],
        },
    ]
    return {
        case_type: 'NORMAL',
        patent_category: 'INV',
        flow_dir: 'CN_DOMESTIC',
        conclusion: 'BLOCKED',
        hard_block: true,
        afterfill_audit_required: false,
        material_count: 0,
        checks: missing,
        missing_items: missing,
        file_events: [],
        suggested_actions: ['补齐硬性递交材料后再递交'],
    }
}

function emptyOverlayResponse(): Record<string, unknown> {
    return {
        case_id: caseId,
        case_revision: 1,
        as_of_revision: 1,
        latest_sequence: 0,
        center: {
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

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(body),
    })
}
