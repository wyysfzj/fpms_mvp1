import { expect, test } from '@playwright/test'
import type { Page, Request, Route } from '@playwright/test'

const caseId = 'case-v8-fee-instruction'
const overlayObligationId = '6d4a2c24-be22-464d-a91b-9e818732b5f4'
const overlaySourceActivityId = '3e1f88a7-db5d-4355-a2b2-5e7ab1c9bcfe'
const overlaySourceDocumentId = '443e902e-7dc2-498e-99c6-a992d3d54168'
const idempotencyKeys = [
    '00000000-0000-4000-8000-000000000000',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000002',
    '00000000-0000-4000-8000-000000000003',
    '00000000-0000-4000-8000-000000000004',
]

test('real obligation customer projection is latest-only and raw audit facts stay collapsed', async ({ page }) => {
    const instructionRequests: Request[] = []
    const unexpectedMutations: string[] = []
    await mockCaseFeesApi(page, {
        instructionRequests,
        unexpectedMutations,
        onInstruction: async (route, requestIndex) => {
            const instruction = route.request().postDataJSON().instruction as 'PAY' | 'HOLD' | 'ABANDON'
            await fulfillJson(route, instructionResult(instruction, `server-obligation-${requestIndex + 1}`))
        },
    })
    await openCaseFees(page)
    const caseUrl = page.url()

    const obligations = page.getByTestId('real-fee-obligations')
    const obligation = obligations.locator('.obligation-card')
    await expect(obligation).toHaveCount(1)
    await expect(obligation.getByRole('button')).toHaveCount(3)
    await expect(obligation.getByRole('heading', { name: '授权登记官费义务', exact: true })).toBeVisible()
    await expect(obligation.getByText('费用域：官费', { exact: true })).toBeVisible()
    await expect(obligation.getByText('来源状态：已核验', { exact: true })).toBeVisible()
    await expect(obligation.getByText('币种：人民币（CNY）', { exact: true })).toBeVisible()
    await expect(obligation.getByText('估算状态：暂无', { exact: true })).toBeVisible()
    await expect(obligation.getByText('义务状态：已确认', { exact: true })).toBeVisible()
    await expect(obligation.getByText('客户指示状态：缴费', { exact: true })).toBeVisible()
    await expect(obligation.getByText('草单状态：已创建', { exact: true })).toBeVisible()
    await expect(obligation.getByText('缴费清单状态：已创建', { exact: true })).toBeVisible()
    await expect(obligation.getByText('付款状态：未缴费', { exact: true })).toBeVisible()
    await expect(obligation.getByText('官方证据状态：待处理', { exact: true })).toBeVisible()
    await expect(obligation.getByRole('heading', { name: '授权公告印刷费', exact: true })).toBeVisible()
    await expect(obligation.getByText('官费全额：50.00', { exact: true })).toBeVisible()
    await expect(obligation.getByText('应缴金额：50.00', { exact: true })).toBeVisible()
    await expect(obligation.getByText(new RegExp(overlayObligationId))).toBeHidden()
    await expect(obligation.getByText(/GRANT_REGISTRATION_OFFICIAL_FEES/)).toBeHidden()

    const obligationAudit = obligation.locator('details').filter({ hasText: '义务编号' })
    await obligationAudit.getByText('审计信息', { exact: true }).click()
    await expect(obligation.getByText(new RegExp(overlayObligationId))).toBeVisible()
    await expect(obligation.getByText(new RegExp(overlaySourceActivityId))).toBeVisible()
    await expect(obligation.getByText(new RegExp(overlaySourceDocumentId))).toBeVisible()
    await expect(obligation.getByText(/GRANT_REGISTRATION_OFFICIAL_FEES/)).toBeVisible()
    await obligationAudit.getByText('审计信息', { exact: true }).click()

    await obligation.getByRole('button', { name: '记录支付指示', exact: true }).click()
    await expect.poll(() => instructionRequests.length).toBe(1)
    expectInstructionRequest(instructionRequests[0], 'PAY', idempotencyKeys[1])

    const result = obligation.getByTestId('fee-instruction-result')
    await expect(result.getByText('支付指示已记录', { exact: true })).toBeVisible()
    await expect(result.getByText('服务端客户指示：PAY', { exact: true })).toBeHidden()
    await expect(result.getByText('服务端义务编号：server-obligation-1', { exact: true })).toBeHidden()
    const resultAudit = result.locator('details')
    await resultAudit.getByText('审计信息', { exact: true }).click()
    await expect(result.getByText('服务端客户指示：PAY', { exact: true })).toBeVisible()
    await expect(result.getByText('服务端义务编号：server-obligation-1', { exact: true })).toBeVisible()
    await resultAudit.getByText('审计信息', { exact: true }).click()
    const draftLink = result.getByRole('link', { name: '创建关联费用草稿', exact: true })
    await expect(draftLink).toHaveAttribute(
        'href',
        '/fees/drafts/new?obligation_id=server-obligation-1',
    )
    await expect(page).toHaveURL(caseUrl)

    await obligation.getByRole('button', { name: '记录支付指示', exact: true }).click()
    await expect.poll(() => instructionRequests.length).toBe(2)
    expectInstructionRequest(instructionRequests[1], 'PAY', idempotencyKeys[2])

    await obligation.getByRole('button', { name: '记录暂缓指示', exact: true }).click()
    await expect.poll(() => instructionRequests.length).toBe(3)
    expectInstructionRequest(instructionRequests[2], 'HOLD', idempotencyKeys[3])
    await expect(result.getByText('暂缓指示已记录', { exact: true })).toBeVisible()
    await expect(result.getByRole('link', { name: '创建关联费用草稿', exact: true })).toHaveCount(0)

    await obligation.getByRole('button', { name: '记录放弃指示', exact: true }).click()
    await expect.poll(() => instructionRequests.length).toBe(4)
    expectInstructionRequest(instructionRequests[3], 'ABANDON', idempotencyKeys[4])
    await expect(result.getByText('放弃指示已记录', { exact: true })).toBeVisible()
    await expect(obligation.getByText('客户指示状态：缴费', { exact: true })).toBeVisible()
    expect(unexpectedMutations).toEqual([])
    expect(await page.evaluate(() => (window as Window & { __uuidCallCount?: number }).__uuidCallCount)).toBe(5)
})

test('transport failure keeps one attempt key for explicit retry and never retries automatically', async ({ page }) => {
    const instructionRequests: Request[] = []
    const unexpectedMutations: string[] = []
    await mockCaseFeesApi(page, {
        instructionRequests,
        unexpectedMutations,
        onInstruction: async (route, requestIndex) => {
            if (requestIndex === 0) {
                await route.abort('failed')
                return
            }
            await fulfillJson(route, instructionResult('PAY', 'server-obligation-retried'))
        },
    })
    await openCaseFees(page)

    const obligation = page.getByTestId('real-fee-obligations').locator('.obligation-card')
    const payButton = obligation.getByRole('button', { name: '记录支付指示', exact: true })
    await payButton.click()
    await expect(obligation.getByText('UNKNOWN_ERROR', { exact: true })).toBeVisible()
    await page.waitForTimeout(250)
    expect(instructionRequests).toHaveLength(1)
    expectInstructionRequest(instructionRequests[0], 'PAY', idempotencyKeys[1])
    expect(await page.evaluate(() => (window as Window & { __uuidCallCount?: number }).__uuidCallCount)).toBe(2)

    await payButton.click()
    await expect.poll(() => instructionRequests.length).toBe(2)
    expectInstructionRequest(instructionRequests[1], 'PAY', idempotencyKeys[1])
    await expect(obligation.getByText('支付指示已记录', { exact: true })).toBeVisible()
    expect(await page.evaluate(() => (window as Window & { __uuidCallCount?: number }).__uuidCallCount)).toBe(2)

    await payButton.click()
    await expect.poll(() => instructionRequests.length).toBe(3)
    expectInstructionRequest(instructionRequests[2], 'PAY', idempotencyKeys[2])
    expect(await page.evaluate(() => (window as Window & { __uuidCallCount?: number }).__uuidCallCount)).toBe(3)
    expect(unexpectedMutations).toEqual([])
})

test('a received business error closes the attempt while preserving the server error', async ({ page }) => {
    const instructionRequests: Request[] = []
    const unexpectedMutations: string[] = []
    await mockCaseFeesApi(page, {
        instructionRequests,
        unexpectedMutations,
        onInstruction: async (route, requestIndex) => {
            if (requestIndex === 0) {
                await fulfillJson(
                    route,
                    {
                        error: {
                            code: 'FEE_INSTRUCTION_CONFLICT',
                            message: '费用指示已由其他操作更新',
                            details: { obligation_id: overlayObligationId },
                        },
                    },
                    409,
                    { 'x-request-id': 'request-business-error' },
                )
                return
            }
            const instruction = route.request().postDataJSON().instruction as 'PAY' | 'HOLD' | 'ABANDON'
            await fulfillJson(route, instructionResult(instruction, 'server-obligation-after-error'))
        },
    })
    await openCaseFees(page)

    const obligation = page.getByTestId('real-fee-obligations').locator('.obligation-card')
    await obligation.getByRole('button', { name: '记录支付指示', exact: true }).click()
    await expect(obligation.getByText('FEE_INSTRUCTION_CONFLICT', { exact: true })).toBeVisible()
    await expect(obligation.getByText('费用指示已由其他操作更新', { exact: true })).toBeVisible()
    expectInstructionRequest(instructionRequests[0], 'PAY', idempotencyKeys[1])

    await obligation.getByRole('button', { name: '记录支付指示', exact: true }).click()
    await expect.poll(() => instructionRequests.length).toBe(2)
    expectInstructionRequest(instructionRequests[1], 'PAY', idempotencyKeys[2])

    await obligation.getByRole('button', { name: '记录暂缓指示', exact: true }).click()
    await expect.poll(() => instructionRequests.length).toBe(3)
    expectInstructionRequest(instructionRequests[2], 'HOLD', idempotencyKeys[3])
    await expect(obligation.getByText('暂缓指示已记录', { exact: true })).toBeVisible()
    await expect(obligation.getByText('客户指示状态：缴费', { exact: true })).toBeVisible()
    expect(unexpectedMutations).toEqual([])
})

async function mockCaseFeesApi(
    page: Page,
    options: {
        instructionRequests: Request[]
        unexpectedMutations: string[]
        onInstruction: (route: Route, requestIndex: number) => Promise<void>
    },
): Promise<void> {
    await page.addInitScript((keys) => {
        let callCount = 0
        Object.defineProperty(window.crypto, 'randomUUID', {
            configurable: true,
            value: () => {
                const key = keys[callCount]
                callCount += 1
                ;(window as Window & { __uuidCallCount?: number }).__uuidCallCount = callCount
                return key
            },
        })
        window.localStorage.setItem('fpms_token', 'v8-case-fee-instruction-token')
    }, idempotencyKeys)

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
            return fulfillJson(route, overlay())
        }
        if (request.method() === 'GET' && apiPath === '/fees/drafts') {
            return fulfillJson(route, emptyDrafts())
        }
        if (
            request.method() === 'POST' &&
            apiPath === `/fees/obligations/${overlayObligationId}/instruction`
        ) {
            const requestIndex = options.instructionRequests.length
            options.instructionRequests.push(request)
            return options.onInstruction(route, requestIndex)
        }
        if (request.method() !== 'GET') {
            options.unexpectedMutations.push(apiPath)
        }
        return fulfillJson(route, { detail: '未处理的案件费用指示界面模拟请求' }, 404)
    })
}

async function openCaseFees(page: Page): Promise<void> {
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('tab', { name: '费用', exact: true })).toBeVisible()
    await page.getByRole('tab', { name: '费用', exact: true }).click()
    await expect(page.getByRole('heading', { name: '授权登记官费义务', exact: true })).toBeVisible()
}

function expectInstructionRequest(
    request: Request,
    instruction: 'PAY' | 'HOLD' | 'ABANDON',
    idempotencyKey: string,
): void {
    expect(new URL(request.url()).pathname).toBe(
        `/api/v1/fees/obligations/${overlayObligationId}/instruction`,
    )
    expect(request.postDataJSON()).toEqual({ instruction, idempotency_key: idempotencyKey })
}

async function fulfillJson(
    route: Route,
    body: unknown,
    status = 200,
    headers?: Record<string, string>,
): Promise<void> {
    await route.fulfill({ status, headers, contentType: 'application/json', body: JSON.stringify(body) })
}

function instructionResult(
    instruction: 'PAY' | 'HOLD' | 'ABANDON',
    obligationId: string,
): Record<string, unknown> {
    return {
        obligation_id: obligationId,
        client_instruction_status: instruction,
        activity_id: `activity-${instruction.toLowerCase()}`,
        idempotency_key: 'server-returned-key',
        reused: false,
    }
}

function caseDetail(): Record<string, unknown> {
    return {
        id: caseId,
        case_no: 'V8-FEE-INSTRUCTION-001',
        client_id: 'client-v8-fee-instruction',
        title: '案件费用指示界面测试',
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

function emptyDrafts(): Record<string, unknown> {
    return {
        items: [],
        page: 1,
        page_size: 50,
        total: 0,
        summary: {
            total_draft_count: 0,
            service_fee_amount: '0.00',
            government_fee_amount: '0.00',
            income_amount: '0.00',
        },
    }
}

function overlay(): Record<string, unknown> {
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
                activity_id: 'activity-overlay-old',
                lane: 'FEE',
                activity_type: 'FEE_OBLIGATION_RECOGNIZED',
                source_activity_id: null,
                effective_at: '2026-07-31T00:00:00Z',
                confirmation_status: 'CONFIRMED',
                center_changes: {},
                document_evidence: [],
                work_packages: [],
                tasks: [],
                fee_obligations: [
                    {
                        obligation_id: overlayObligationId,
                        source_activity_id: overlaySourceActivityId,
                        source_document_id: overlaySourceDocumentId,
                        source_status: 'REVIEW_REQUIRED',
                        fee_domain: 'GOV',
                        obligation_type: 'GRANT_REGISTRATION_OFFICIAL_FEES',
                        due_date: '2026-11-24',
                        currency: 'CNY',
                        statuses: {
                            estimate_status: 'ESTIMATE',
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
                    },
                ],
                evidence_summary: [],
                warnings: [],
            },
            {
                sequence: 2,
                activity_id: 'activity-overlay-1',
                lane: 'FEE',
                activity_type: 'FEE_OBLIGATION_RECOGNIZED',
                source_activity_id: null,
                effective_at: '2026-08-01T00:00:00Z',
                confirmation_status: 'CONFIRMED',
                center_changes: {},
                document_evidence: [],
                work_packages: [],
                tasks: [],
                fee_obligations: [
                    {
                        obligation_id: overlayObligationId,
                        source_activity_id: overlaySourceActivityId,
                        source_document_id: overlaySourceDocumentId,
                        source_status: 'VERIFIED',
                        fee_domain: 'GOV',
                        obligation_type: 'GRANT_REGISTRATION_OFFICIAL_FEES',
                        due_date: '2026-11-24',
                        currency: 'CNY',
                        statuses: {
                            estimate_status: null,
                            obligation_status: 'RECOGNIZED',
                            client_instruction_status: 'PAY',
                            draft_status: 'CREATED',
                            pay_list_status: 'CREATED',
                            payment_status: 'UNPAID',
                            official_evidence_status: 'PENDING',
                        },
                        lines: [
                            {
                                line_id: '018d816e-5fdc-7a15-96a7-83b95a0b2b73',
                                fee_code: 'CNIPA-GRANT-ANNOUNCEMENT',
                                fee_name: '授权公告印刷费',
                                fee_year_key: 0,
                                official_full_amount: '50.00',
                                reduction_ratio: '0.0000',
                                payable_amount: '50.00',
                                source_amount: '50.00',
                                source_date: '2026-03-30',
                                difference_review_state: 'MATCHED',
                            },
                        ],
                        related_facts: [],
                        supersedes_obligation_id: null,
                        supersede_reason: null,
                    },
                ],
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
