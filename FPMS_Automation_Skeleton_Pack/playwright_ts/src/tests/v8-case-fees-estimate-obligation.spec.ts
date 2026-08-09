import { expect, test } from '@playwright/test'
import type { Page, Request, Route } from '@playwright/test'

const caseId = 'case-v8-fees'

test('case fees keeps estimates, real obligations, and drafts independent', async ({ page }) => {
    const previewRequests: Request[] = []
    const overlayRequests: Request[] = []
    const mutationRequests: string[] = []

    await mockCaseFeesApi(page, {
        onPreview: async (route) => {
            previewRequests.push(route.request())
            await fulfillJson(route, estimate())
        },
        overlayRequests,
        mutationRequests,
    })
    await openCaseFees(page)

    expect(overlayRequests).toHaveLength(1)
    await expect(page.getByLabel('费率生效日')).toHaveValue('')
    expect(previewRequests).toHaveLength(0)
    await page.getByRole('button', { name: '估算官费' }).click()
    await expect(page.getByText('请选择费率生效日期', { exact: true })).toBeVisible()
    expect(previewRequests).toHaveLength(0)

    await expect(page.getByLabel('来源文档').locator('option')).toHaveText([
        '不选择来源文档',
        'document-approved',
        'document-second',
    ])
    await page.getByLabel('估算触发上下文').selectOption('FILING_ACCEPTED')
    await page.getByLabel('费率生效日').fill('2026-08-01')
    await page.getByRole('button', { name: '估算官费' }).click()

    await expect.poll(() => previewRequests.length).toBe(1)
    expect(previewRequests[0].postDataJSON()).toEqual({
        case_id: caseId,
        trigger_context: {
            trigger: 'FILING_ACCEPTED',
            source_document_id: null,
        },
        currency: 'CNY',
        rate_effective_on: '2026-08-01',
    })
    await expect(page.getByRole('heading', { name: '官费估算' })).toBeVisible()
    await expect(page.getByText('ESTIMATE', { exact: true })).toBeVisible()
    const estimateRegion = page.getByTestId('official-fee-estimate')
    await expect(estimateRegion.getByText('官方全额：100.00', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('费减比例：85.0000', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('应缴金额：85.00', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('费率标识：rate-approved', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('来源文件：reviewed-source.pdf', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('来源日期：2026-08-01', { exact: true })).toHaveCount(2)
    await expect(estimateRegion.getByText('差异复核：MATCHED', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('来源文档：document-approved', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('来源地址：https://example.test/rates', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('来源政策：official-policy', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('来源版本：2026.08', { exact: true })).toBeVisible()
    await expect(estimateRegion.getByText('来源状态：VERIFIED', { exact: true })).toBeVisible()
    await expect(estimateRegion.locator('.estimate-candidate strong')).toHaveText([
        '申请费（CN-APPLICATION）',
        '复审费（CN-REEXAM）',
    ])

    const obligations = page.getByTestId('real-fee-obligations')
    await expect(obligations.getByText('真实费用义务', { exact: true })).toBeVisible()
    await expect(obligations.getByText('obligation-real-1', { exact: true })).toBeVisible()
    await expect(obligations.getByText('来源活动：activity-real-1', { exact: true })).toBeVisible()
    await expect(obligations.getByText('来源文档：document-real-1', { exact: true })).toBeVisible()
    await expect(obligations.getByText('估算状态：', { exact: true })).toBeVisible()
    await expect(obligations.getByText('PAYMENT', { exact: true })).toBeVisible()
    await expect(obligations.getByText('替代义务：legacy-obligation-0', { exact: true })).toBeVisible()
    await expect(obligations.getByText('20.00', { exact: true })).toHaveCount(3)

    const drafts = page.getByTestId('persisted-fee-drafts')
    await expect(drafts.getByText('已保存费用草稿', { exact: true })).toBeVisible()
    await expect(drafts.getByText('draft-real-1', { exact: true })).toBeVisible()
    expect(mutationRequests).toEqual([])

    await page.getByLabel('来源文档').selectOption('document-approved')
    await expect(page.getByText('ESTIMATE', { exact: true })).toHaveCount(0)
    expect(previewRequests).toHaveLength(1)
    await page.getByRole('button', { name: '估算官费' }).click()
    await expect.poll(() => previewRequests.length).toBe(2)
    expect(previewRequests[1].postDataJSON()).toEqual({
        case_id: caseId,
        trigger_context: {
            trigger: 'FILING_ACCEPTED',
            source_document_id: 'document-approved',
        },
        currency: 'CNY',
        rate_effective_on: '2026-08-01',
    })
    await page.getByLabel('费率生效日').fill('2026-08-02')
    expect(previewRequests).toHaveLength(2)
    await page.getByRole('button', { name: '估算官费' }).click()
    await expect.poll(() => previewRequests.length).toBe(3)
    expect(previewRequests[2].postDataJSON()).toMatchObject({ rate_effective_on: '2026-08-02' })
})

test('a preview error leaves persisted obligations and drafts visible', async ({ page }) => {
    const mutationRequests: string[] = []
    await mockCaseFeesApi(page, {
        onPreview: async (route) => {
            await fulfillJson(
                route,
                {
                    error: {
                        code: 'OFFICIAL_RATE_CONFLICT',
                        message: '费率来源冲突',
                        details: { rate_id: 'rate-approved' },
                    },
                },
                409,
            )
        },
        mutationRequests,
    })
    await openCaseFees(page)
    await page.getByLabel('估算触发上下文').selectOption('REEXAM_REQUESTED')
    await page.getByLabel('费率生效日').fill('2026-08-03')
    await page.getByRole('button', { name: '估算官费' }).click()

    await expect(page.getByText('OFFICIAL_RATE_CONFLICT', { exact: true })).toBeVisible()
    await expect(page.getByText('费率来源冲突', { exact: true })).toBeVisible()
    await expect(page.getByTestId('real-fee-obligations').getByText('obligation-real-1')).toBeVisible()
    await expect(page.getByTestId('persisted-fee-drafts').getByText('draft-real-1')).toBeVisible()
    expect(mutationRequests).toEqual([])
})

test('an overlay load error is visible and is not treated as zero real obligations', async ({ page }) => {
    const overlayRequests: Request[] = []
    await mockCaseFeesApi(page, {
        onPreview: async (route) => fulfillJson(route, estimate()),
        onOverlay: async (route) =>
            fulfillJson(route, { error: { code: 'OVERLAY_UNAVAILABLE', message: '生命周期视图不可用' } }, 503),
        overlayRequests,
        mutationRequests: [],
    })
    await openCaseFees(page)

    const obligations = page.getByTestId('real-fee-obligations')
    await expect(obligations.getByText('OVERLAY_UNAVAILABLE', { exact: true })).toBeVisible()
    await expect(obligations.getByText('生命周期视图不可用', { exact: true })).toBeVisible()
    await expect(obligations.getByText('暂无真实费用义务', { exact: true })).toHaveCount(0)
    expect(overlayRequests).toHaveLength(1)
})

test('managed overlay shows loading until the parent supplies snapshot or error', async ({ page }) => {
    let releaseOverlay: (() => void) | undefined
    const overlayRequests: Request[] = []
    await mockCaseFeesApi(page, {
        onPreview: async (route) => fulfillJson(route, estimate()),
        onOverlay: async (route) => {
            await new Promise<void>((resolve) => {
                releaseOverlay = resolve
            })
            await fulfillJson(route, overlay(false))
        },
        overlayRequests,
        mutationRequests: [],
    })
    await openCaseFees(page)

    const obligations = page.getByTestId('real-fee-obligations')
    await expect(obligations.getByText('正在加载真实费用义务...', { exact: true })).toBeVisible()
    await expect(obligations.getByText('暂无真实费用义务', { exact: true })).toHaveCount(0)
    expect(overlayRequests).toHaveLength(1)

    releaseOverlay?.()
    await expect(obligations.getByText('暂无真实费用义务', { exact: true })).toBeVisible()
})

test('an estimate does not populate a zero-obligation overlay', async ({ page }) => {
    await mockCaseFeesApi(page, {
        onPreview: async (route) => fulfillJson(route, estimate()),
        onOverlay: async (route) => fulfillJson(route, overlay(false)),
        mutationRequests: [],
    })
    await openCaseFees(page)
    await page.getByLabel('估算触发上下文').selectOption('FILING_ACCEPTED')
    await page.getByLabel('费率生效日').fill('2026-08-04')
    await page.getByRole('button', { name: '估算官费' }).click()

    await expect(page.getByText('ESTIMATE', { exact: true })).toBeVisible()
    await expect(page.getByTestId('real-fee-obligations').getByText('暂无真实费用义务')).toBeVisible()
    await expect(page.getByTestId('real-fee-obligations').getByText('CN-APPLICATION')).toHaveCount(0)
})

async function mockCaseFeesApi(
    page: Page,
    options: {
        onPreview: (route: Route) => Promise<void>
        onOverlay?: (route: Route) => Promise<void>
        overlayRequests?: Request[]
        mutationRequests: string[]
    },
): Promise<void> {
    await page.route('**/api/v1/**', async (route) => {
        const request = route.request()
        const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, '')
        if (request.method() === 'GET' && apiPath === '/auth/me') {
            return fulfillJson(route, { permissions: ['Case.Read', 'Doc.Read', 'Task.Read', 'Fee.Read'] })
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}`) {
            return fulfillJson(route, caseDetail())
        }
        if (request.method() === 'GET' && apiPath === `/cases/${caseId}/lifecycle-overlay`) {
            options.overlayRequests?.push(request)
            return options.onOverlay ? options.onOverlay(route) : fulfillJson(route, overlay())
        }
        if (request.method() === 'GET' && apiPath === '/fees/drafts') {
            return fulfillJson(route, {
                items: [
                    {
                        id: 'draft-real-1',
                        case_id: caseId,
                        draft_type: 'MANUAL',
                        currency: 'CNY',
                        status: 'OPEN',
                        amount: '20.00',
                    },
                ],
                page: 1,
                page_size: 50,
                total: 1,
                summary: {
                    total_draft_count: 1,
                    service_fee_amount: '0.00',
                    government_fee_amount: '20.00',
                    income_amount: '20.00',
                },
            })
        }
        if (request.method() === 'POST' && apiPath === '/fees/official-fee-preview') {
            return options.onPreview(route)
        }
        if (
            request.method() !== 'GET'
            && (apiPath.includes('/fees') || apiPath.includes('/pay-lists') || apiPath.includes('/payments'))
        ) {
            options.mutationRequests.push(apiPath)
            return fulfillJson(route, { detail: '不应有费用状态变更' }, 500)
        }
        return fulfillJson(route, { detail: '未处理的案件费用界面模拟请求' }, 404)
    })
}

async function openCaseFees(page: Page): Promise<void> {
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-case-fees-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('tab', { name: '费用', exact: true })).toBeVisible()
    await page.getByRole('tab', { name: '费用', exact: true }).click()
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function caseDetail(): Record<string, unknown> {
    return {
        id: caseId,
        case_no: 'V8-FEES-001',
        client_id: 'client-v8-fees',
        title: '案件费用界面测试',
        status: 'NOT_FILED',
        applicants: [],
        inventors: [],
        priorities: [],
        bio_deposits: [],
        agent_splits: [],
        created_at: '2026-08-01T00:00:00Z',
        updated_at: '2026-08-01T00:00:00Z',
    }
}

function estimate(): Record<string, unknown> {
    return {
        case_id: caseId,
        estimate_status: 'ESTIMATE',
        trigger_context: { trigger: 'FILING_ACCEPTED', source_document_id: 'document-approved' },
        currency: 'CNY',
        total_payable_amount: '85.00',
        candidates: [
            {
                line: {
                    fee_code: 'CN-APPLICATION',
                    fee_name: '申请费',
                    fee_year_key: 2026,
                    official_full_amount: '100.00',
                    reduction_ratio: '85.0000',
                    payable_amount: '85.00',
                    source_amount: null,
                    source_date: '2026-08-01',
                    difference_review_state: 'MATCHED',
                },
                source: {
                    rate_id: 'rate-approved',
                    source_document_id: 'document-approved',
                    source_doc: 'reviewed-source.pdf',
                    source_url: 'https://example.test/rates',
                    source_policy: 'official-policy',
                    source_version: '2026.08',
                    status: 'VERIFIED',
                },
            },
            {
                line: {
                    fee_code: 'CN-REEXAM',
                    fee_name: '复审费',
                    fee_year_key: 2026,
                    official_full_amount: '50.00',
                    reduction_ratio: '1.0000',
                    payable_amount: '50.00',
                    source_amount: '50.00',
                    source_date: '2026-08-01',
                    difference_review_state: 'SOURCE_PENDING',
                },
                source: {
                    rate_id: null,
                    source_document_id: null,
                    source_doc: null,
                    source_url: null,
                    source_policy: null,
                    source_version: null,
                    status: 'REVIEW_REQUIRED',
                },
            },
        ],
    }
}

function overlay(withObligation = true): Record<string, unknown> {
    return {
        case_id: caseId,
        lifecycle_revision: 1,
        generated_at: '2026-08-01T00:00:00Z',
        center_snapshot: {
            business_stage: null,
            official_procedure_stage: null,
            legal_status: null,
            effective_at: null,
            verification_status: null,
            source_event_id: null,
        },
        milestones: [
            {
                sequence: 1,
                activity_id: 'activity-real-1',
                lane: 'DOCUMENT',
                activity_type: 'DOCUMENT_REVIEWED',
                source_activity_id: null,
                effective_at: '2026-08-01T00:00:00Z',
                confirmation_status: 'CONFIRMED',
                center_changes: {},
                document_evidence: [
                    documentEvidence('document-approved', 'APPROVED', 1),
                    documentEvidence('document-pending', 'PENDING', 2),
                    documentEvidence('document-approved', 'APPROVED', 3),
                    documentEvidence('document-second', 'APPROVED', 4),
                ],
                work_packages: [],
                tasks: [],
                fee_obligations: withObligation ? [
                    {
                        obligation_id: 'obligation-real-1',
                        source_activity_id: 'activity-real-1',
                        source_document_id: 'document-real-1',
                        source_status: 'VERIFIED',
                        fee_domain: 'GOV',
                        obligation_type: 'APPLICATION_FEE',
                        due_date: '2026-08-31',
                        currency: 'CNY',
                        statuses: {
                            estimate_status: null,
                            obligation_status: 'RECOGNIZED',
                            client_instruction_status: 'PAY',
                            draft_status: 'NOT_CREATED',
                            pay_list_status: 'NOT_CREATED',
                            payment_status: 'UNPAID',
                            official_evidence_status: 'PENDING',
                        },
                        lines: [
                            {
                                line_id: 'line-real-1',
                                fee_code: 'CN-APPLICATION',
                                fee_name: '申请费',
                                fee_year_key: 2026,
                                official_full_amount: '20.00',
                                reduction_ratio: '1.0000',
                                payable_amount: '20.00',
                                source_amount: '20.00',
                                source_date: '2026-08-01',
                                difference_review_state: 'MATCHED',
                            },
                        ],
                        related_facts: [{ kind: 'PAYMENT', object_id: 'payment-real-1', status: 'PAID' }],
                        supersedes_obligation_id: 'legacy-obligation-0',
                        supersede_reason: '官方费率更新',
                    },
                ] : [],
                evidence_summary: [],
                warnings: [],
            },
        ],
        decision_gates: [],
        warnings: [],
        legacy_conflicts: [],
        next_cursor: null,
        has_more: false,
    }
}

function documentEvidence(
    documentId: string,
    reviewState: 'APPROVED' | 'PENDING',
    versionNumber: number,
): Record<string, unknown> {
    return {
        version: {
            evidence_version_id: `evidence-${versionNumber}`,
            case_id: caseId,
            document_id: documentId,
            attachment_id: `attachment-${versionNumber}`,
            lineage_key: `lineage-${versionNumber}`,
            role: 'RAW_ATTACHMENT',
            version_number: versionNumber,
            state: 'FINAL',
            creator_id: 'creator-1',
            review_state: reviewState,
            reviewer_id: reviewState === 'APPROVED' ? 'reviewer-1' : null,
            reviewed_at: reviewState === 'APPROVED' ? '2026-08-01T00:00:00Z' : null,
            final_submitted_at: null,
            content_hash: `hash-${versionNumber}`,
            is_current: false,
            is_final: false,
        },
        derivations: [],
    }
}
