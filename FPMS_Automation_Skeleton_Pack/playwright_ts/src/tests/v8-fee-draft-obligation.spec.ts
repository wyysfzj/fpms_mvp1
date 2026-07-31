import { expect, test } from '@playwright/test'
import type { Page, Route } from '@playwright/test'

const obligationId = 'obligation-v8-draft'

const payableObligation = {
    id: obligationId,
    case_id: 'case-v8-draft',
    source: {
        source_activity_id: 'activity-v8-draft',
        source_document_id: 'document-v8-draft',
        status: 'VERIFIED',
    },
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
    lines: [],
    supersedes_obligation_id: null,
    supersede_reason: null,
}

test('显式 PAY 义务展示后端来源和指示事实，并仅提交同一义务标识', async ({ page }) => {
    let requestedObligationId: string | undefined
    let draftPayload: Record<string, unknown> | undefined

    await mockFeeDraftApi(page, async (route, apiPath) => {
        if (route.request().method() === 'GET' && apiPath.startsWith('/fees/obligations/')) {
            requestedObligationId = decodeURIComponent(apiPath.slice('/fees/obligations/'.length))
            return fulfillJson(route, payableObligation)
        }
        if (route.request().method() === 'POST' && apiPath === '/fees/drafts') {
            draftPayload = route.request().postDataJSON() as Record<string, unknown>
            return fulfillJson(route, createdDraft(draftPayload), 201)
        }
        if (route.request().method() === 'GET' && apiPath === '/fees/drafts/draft-v8-obligation') {
            return fulfillJson(route, createdDraft(draftPayload ?? {}))
        }
        return fulfillJson(route, { detail: '未处理的费用草稿义务模拟请求' }, 404)
    })

    await openFeeDraftCreate(page, `?obligation_id=${obligationId}`)

    await expect.poll(() => requestedObligationId).toBe(obligationId)
    const obligation = page.getByTestId('linked-fee-obligation')
    await expect(obligation.getByText(`义务编号：${obligationId}`, { exact: true })).toBeVisible()
    await expect(obligation.getByText('来源活动：activity-v8-draft', { exact: true })).toBeVisible()
    await expect(obligation.getByText('来源文档：document-v8-draft', { exact: true })).toBeVisible()
    await expect(obligation.getByText('来源状态：VERIFIED', { exact: true })).toBeVisible()
    await expect(obligation.getByText('客户指示：PAY', { exact: true })).toBeVisible()

    await page.getByPlaceholder('请输入案件编号').fill('case-v8-draft')
    await page.getByRole('button', { name: '创建草稿' }).click()

    await expect.poll(() => draftPayload).toEqual({
        case_id: 'case-v8-draft',
        currency: 'CNY',
        obligation_id: obligationId,
    })
})

test('非 PAY 义务保持可见但阻止关联草稿提交', async ({ page }) => {
    let draftPostCount = 0

    await mockFeeDraftApi(page, async (route, apiPath) => {
        if (route.request().method() === 'GET' && apiPath === `/fees/obligations/${obligationId}`) {
            return fulfillJson(route, {
                ...payableObligation,
                statuses: {
                    ...payableObligation.statuses,
                    client_instruction_status: 'HOLD',
                },
            })
        }
        if (route.request().method() === 'POST' && apiPath === '/fees/drafts') {
            draftPostCount += 1
            return fulfillJson(route, createdDraft({}), 201)
        }
        return fulfillJson(route, { detail: '未处理的费用草稿义务模拟请求' }, 404)
    })

    await openFeeDraftCreate(page, `?obligation_id=${obligationId}`)

    const obligation = page.getByTestId('linked-fee-obligation')
    await expect(obligation.getByText('客户指示：HOLD', { exact: true })).toBeVisible()
    await expect(
        obligation.getByText('仅当客户指示为 PAY 时才可创建关联草稿。', { exact: true }),
    ).toBeVisible()
    await expect(page.getByRole('button', { name: '创建草稿' })).toBeDisabled()
    expect(draftPostCount).toBe(0)
})

test('未提供义务标识时不猜测义务并保留未关联草稿创建', async ({ page }) => {
    let obligationGetCount = 0
    let draftPayload: Record<string, unknown> | undefined

    await mockFeeDraftApi(page, async (route, apiPath) => {
        if (route.request().method() === 'GET' && apiPath.startsWith('/fees/obligations/')) {
            obligationGetCount += 1
        }
        if (route.request().method() === 'POST' && apiPath === '/fees/drafts') {
            draftPayload = route.request().postDataJSON() as Record<string, unknown>
            return fulfillJson(route, createdDraft(draftPayload), 201)
        }
        if (route.request().method() === 'GET' && apiPath === '/fees/drafts/draft-v8-obligation') {
            return fulfillJson(route, createdDraft(draftPayload ?? {}))
        }
        return fulfillJson(route, { detail: '未处理的费用草稿义务模拟请求' }, 404)
    })

    await openFeeDraftCreate(page)
    await page.getByPlaceholder('请输入案件编号').fill('case-unlinked')
    await page.getByRole('button', { name: '创建草稿' }).click()

    await expect.poll(() => draftPayload).toEqual({
        case_id: 'case-unlinked',
        currency: 'CNY',
    })
    expect(obligationGetCount).toBe(0)
})

async function mockFeeDraftApi(
    page: Page,
    handler: (route: Route, apiPath: string) => Promise<void>,
): Promise<void> {
    await page.route('**/api/v1/**', async (route) => {
        const apiPath = new URL(route.request().url()).pathname.replace(/^\/api\/v1/, '')
        if (route.request().method() === 'GET' && apiPath === '/auth/me') {
            return fulfillJson(route, { permissions: ['Fee.Read', 'Fee.Create'] })
        }
        await handler(route, apiPath)
    })
}

async function openFeeDraftCreate(page: Page, query = ''): Promise<void> {
    await page.addInitScript(() => {
        window.localStorage.setItem('fpms_token', 'v8-fee-draft-obligation-token')
    })
    await page.goto(`/fees/drafts/new${query}`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('草稿基础信息', { exact: true })).toBeVisible()
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
    await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function createdDraft(payload: Record<string, unknown>): Record<string, unknown> {
    return {
        id: 'draft-v8-obligation',
        case_id: payload.case_id ?? 'case-v8-draft',
        client_id: null,
        draft_type: 'MANUAL',
        currency: payload.currency ?? 'CNY',
        status: 'OPEN',
        amount: '0.00',
    }
}
