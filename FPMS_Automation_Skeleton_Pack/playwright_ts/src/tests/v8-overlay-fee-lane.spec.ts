import { expect, test } from '@playwright/test'
import type { Page, Route } from '@playwright/test'

const caseId = 'case-v8-overlay-fee'
const govObligationId = '6d4a2c24-be22-464d-a91b-9e818732b5f4'
const serviceObligationId = '9b8568be-4177-4f0b-9c8e-d1f915de26af'

test('费用节点线无损展示 GOV 和 SERVICE 义务的七个独立状态', async ({ page }) => {
    await mockCaseOverlay(page)
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-overlay-fee-token')
    })
    await page.goto(`/cases/${caseId}`, { waitUntil: 'domcontentloaded' })

    await page.getByTestId('lifecycle-history-toggle').click()
    await expect(page.getByTestId('lifecycle-history-details')).toBeVisible()
    const lane = page.getByTestId('fee-obligation-lane')
    await expect(lane.getByRole('heading', { name: '同案双轨费用概览' })).toBeVisible()
    await expect(lane.getByTestId(`fee-obligation-${govObligationId}`)).toHaveCount(1)
    const gov = lane.getByTestId(`fee-obligation-${govObligationId}`)
    await expect(gov.getByRole('heading', { name: '授权登记官费义务' })).toBeVisible()
    await expect(gov.getByText('费用域：官费', { exact: true })).toBeVisible()
    await expect(gov.getByText('币种：人民币（CNY）', { exact: true })).toBeVisible()
    await expect(gov.getByText('估算状态：估算', { exact: true })).toBeVisible()
    await expect(gov.getByText('义务状态：已确认', { exact: true })).toBeVisible()
    await expect(gov.getByText('客户指示状态：缴费', { exact: true })).toBeVisible()
    await expect(gov.getByText('草单状态：已创建', { exact: true })).toBeVisible()
    await expect(gov.getByText('缴费清单状态：已创建', { exact: true })).toBeVisible()
    await expect(gov.getByText('付款状态：已缴费', { exact: true })).toBeVisible()
    await expect(gov.getByText('官方证据状态：已核验', { exact: true })).toBeVisible()
    await expect(gov.getByText('应缴金额：1234.50', { exact: true })).toBeVisible()
    await expect(gov.getByText('减缴比例：0.8500', { exact: true })).toBeVisible()
    await expect(gov.getByText('关联事实：草单 / 已创建', { exact: true })).toBeVisible()
    await expect(gov.getByText('关联事实：付款记录 / 已缴费', { exact: true })).toBeVisible()
    await expect(gov.getByText('费种年度：0', { exact: true })).not.toBeVisible()
    await expect(gov.getByText(`义务编号：${govObligationId}`, { exact: true })).not.toBeVisible()
    await expect(gov.getByText('费用代码：GRANT_REGISTRATION_FEE', { exact: true })).not.toBeVisible()
    await expect(gov.getByText('原始义务状态：RECOGNIZED', { exact: true })).not.toBeVisible()
    await gov.locator('summary').click()
    await expect(gov.getByText(`义务编号：${govObligationId}`, { exact: true })).toBeVisible()
    await expect(gov.getByText('费用代码：GRANT_REGISTRATION_FEE', { exact: true })).toBeVisible()
    await expect(gov.getByText('原始义务状态：RECOGNIZED', { exact: true })).toBeVisible()
    await expect(gov.getByText('费种年度：0', { exact: true })).toBeVisible()

    const service = lane.getByTestId(`fee-obligation-${serviceObligationId}`)
    await expect(service.getByRole('heading', { name: '服务费应收义务' })).toBeVisible()
    await expect(service.getByText('费用域：服务费', { exact: true })).toBeVisible()
    await expect(service.getByText('来源状态：历史数据待核验', { exact: true })).toBeVisible()
    await expect(service.getByText('币种：币种待确认', { exact: true })).toBeVisible()
    await expect(service.getByText('原始来源状态：LEGACY_UNVERIFIED', { exact: true })).not.toBeVisible()
    await expect(service.getByText('原始币种：USD', { exact: true })).not.toBeVisible()
    await expect(service.getByText('估算状态：暂无', { exact: true })).toBeVisible()
    await service.locator('summary').click()
    await expect(service.getByText('原始来源状态：LEGACY_UNVERIFIED', { exact: true })).toBeVisible()
    await expect(service.getByText('原始币种：USD', { exact: true })).toBeVisible()
    await expect(lane.getByText('PATENT_IN_FORCE', { exact: false })).toHaveCount(0)
    await expect(lane.getByText('OFFICIAL_FINAL_PDF', { exact: false })).toHaveCount(0)
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
                case_no: 'V8-FEE-001',
                case_type: 'NORMAL',
                patent_category: 'INV',
                flow_dir: 'CN_DOMESTIC',
                title_cn: '费用节点线测试',
                status: 'GRANT_PENDING',
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
        return fulfillJson(route, { detail: `未处理的费用线模拟请求：${apiPath}` }, 404)
    })
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function statuses(overrides: Record<string, string | null> = {}) {
    return {
        estimate_status: null,
        obligation_status: 'RECOGNIZED',
        client_instruction_status: 'PENDING',
        draft_status: 'NOT_CREATED',
        pay_list_status: 'NOT_CREATED',
        payment_status: 'UNPAID',
        official_evidence_status: 'PENDING',
        ...overrides,
    }
}

function obligation(id: string, feeDomain: 'GOV' | 'SERVICE') {
    const isGov = feeDomain === 'GOV'
    return {
        obligation_id: id,
        source_activity_id: '3e1f88a7-db5d-4355-a2b2-5e7ab1c9bcfe',
        source_document_id: isGov ? '443e902e-7dc2-498e-99c6-a992d3d54168' : null,
        source_status: isGov ? 'VERIFIED' : 'LEGACY_UNVERIFIED',
        fee_domain: feeDomain,
        obligation_type: isGov ? 'GRANT_REGISTRATION_OFFICIAL_FEES' : 'SERVICE_FEE',
        due_date: isGov ? '2026-10-09' : null,
        currency: isGov ? 'CNY' : 'USD',
        statuses: statuses(
            isGov
                ? {
                      estimate_status: 'ESTIMATE',
                      client_instruction_status: 'PAY',
                      draft_status: 'CREATED',
                      pay_list_status: 'CREATED',
                      payment_status: 'PAID',
                      official_evidence_status: 'VERIFIED',
                  }
                : {},
        ),
        lines: [
            {
                line_id: `${id}-line`,
                fee_code: isGov ? 'GRANT_REGISTRATION_FEE' : 'AGENCY_SERVICE_FEE',
                fee_name: isGov ? '办理登记费' : '代理服务费',
                fee_year_key: 0,
                official_full_amount: isGov ? '1452.35' : null,
                reduction_ratio: isGov ? '0.8500' : '0.0000',
                payable_amount: isGov ? '1234.50' : '800.00',
                source_amount: isGov ? '1234.50' : null,
                source_date: isGov ? '2026-08-09' : null,
                difference_review_state: 'MATCHED',
            },
        ],
        related_facts: isGov
            ? [{ kind: 'PAYMENT', object_id: 'payment-1', status: 'PAID' }]
            : [],
        supersedes_obligation_id: null,
        supersede_reason: null,
    }
}

function overlayResponse() {
    return {
        case_id: caseId,
        lifecycle_revision: 5,
        generated_at: '2026-08-09T11:00:00Z',
        center_snapshot: {
            business_stage: 'GRANT_REGISTRATION_IN_PROGRESS',
            official_procedure_stage: 'GRANT_REGISTRATION',
            legal_status: 'PATENT_IN_FORCE',
            effective_at: '2026-08-09T10:00:00Z',
            verification_status: 'CONFIRMED',
            source_event_id: 'activity-lifecycle',
        },
        milestones: [
            {
                sequence: 4,
                activity_id: 'activity-fee-earlier',
                lane: 'FEE',
                activity_type: 'FEE_OBLIGATION_RECOGNIZED',
                source_activity_id: 'activity-lifecycle',
                effective_at: '2026-08-09T10:15:00Z',
                confirmation_status: 'CONFIRMED',
                center_changes: {},
                document_evidence: [],
                work_packages: [],
                tasks: [],
                fee_obligations: [
                    {
                        ...obligation(govObligationId, 'GOV'),
                        statuses: statuses(),
                        related_facts: [{ kind: 'DRAFT', object_id: 'draft-1', status: 'CREATED' }],
                    },
                ],
                evidence_summary: [],
                warnings: [],
            },
            {
                sequence: 5,
                activity_id: 'activity-fee',
                lane: 'FEE',
                activity_type: 'FEE_OBLIGATION_RECOGNIZED',
                source_activity_id: 'activity-lifecycle',
                effective_at: '2026-08-09T10:30:00Z',
                confirmation_status: 'CONFIRMED',
                center_changes: {},
                document_evidence: [],
                work_packages: [],
                tasks: [],
                fee_obligations: [
                    obligation(govObligationId, 'GOV'),
                    obligation(serviceObligationId, 'SERVICE'),
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
