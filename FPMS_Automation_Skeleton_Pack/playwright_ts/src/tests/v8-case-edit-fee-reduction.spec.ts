import { expect, test } from '@playwright/test'
import type { Page } from '@playwright/test'

const caseId = 'CASE-EDIT-FEE-REDUCTION'

const baseCase = {
    id: caseId,
    case_no: 'CN-EDIT-FEE-REDUCTION-001',
    case_type: 'NORMAL',
    patent_category: 'INV',
    title_cn: '编辑案件费用减免',
    status: 'NOT_FILED',
    flow_dir: 'CN_DOMESTIC',
    applicants: [],
    inventors: [],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
    discount_rate: null,
}

test('未知历史减免值保持警示且必须显式选择后才保存 canonical 比例', async ({ page }) => {
    let casePut: Record<string, unknown> | undefined

    await routeCaseEdit(page, {
        ...baseCase,
        fee_reduction: 'LEGACY_UNKNOWN',
    }, (payload) => {
        casePut = payload
    })

    await page.goto(`/cases/${caseId}/edit`)
    await expect(page.getByRole('heading', { name: '编辑案件' })).toBeVisible()
    await page.getByText('控制标记', { exact: true }).click()

    await expect(
        page.getByText('历史减免值“LEGACY_UNKNOWN”无法识别，请明确选择不减缴、70% 或 85% 后再保存。', {
            exact: true,
        }),
    ).toBeVisible()
    const selector = page.getByTestId('case-fee-reduction')
    await expect(selector.getByText('请选择费用减免比例', { exact: true })).toBeVisible()

    await page.getByRole('button', { name: '保存修改' }).click()
    await expect.poll(() => casePut, { timeout: 500 }).toBeUndefined()

    await selector.click()
    await page.getByRole('option', { name: '不减缴', exact: true }).click()
    await page.getByRole('button', { name: '保存修改' }).click()

    await expect.poll(() => casePut).toBeTruthy()
    expect(casePut?.fee_reduction).toBe('0')
})

test('缺失减免值不默认为零并要求显式选择', async ({ page }) => {
    let casePut: Record<string, unknown> | undefined

    await routeCaseEdit(page, {
        ...baseCase,
        fee_reduction: null,
    }, (payload) => {
        casePut = payload
    })

    await page.goto(`/cases/${caseId}/edit`)
    await expect(page.getByRole('heading', { name: '编辑案件' })).toBeVisible()
    await page.getByText('控制标记', { exact: true }).click()

    await expect(
        page.getByText('当前案件未设置费用减免比例，请明确选择后再保存。', { exact: true }),
    ).toBeVisible()
    const selector = page.getByTestId('case-fee-reduction')
    await expect(selector.getByText('请选择费用减免比例', { exact: true })).toBeVisible()
    await expect(selector.getByText('不减缴', { exact: true })).toHaveCount(0)

    await selector.click()
    await page.getByRole('option', { name: '不减缴', exact: true }).click()
    await page.getByRole('button', { name: '保存修改' }).click()

    await expect.poll(() => casePut).toBeTruthy()
    expect(casePut?.fee_reduction).toBe('0')
})

async function routeCaseEdit(
    page: Page,
    caseResponse: Record<string, unknown>,
    onPut: (payload: Record<string, unknown>) => void,
): Promise<void> {
    await page.route(`**/api/v1/cases/${caseId}`, async (route) => {
        if (route.request().method() === 'PUT') {
            onPut(route.request().postDataJSON() as Record<string, unknown>)
        }
        await route.fulfill({ contentType: 'application/json', json: caseResponse })
    })
    await page.route('**/api/v1/clients**', async (route) => {
        await route.fulfill({
            contentType: 'application/json',
            json: { items: [], page: 1, page_size: 100, total: 0 },
        })
    })
    await page.route(`**/api/v1/fees/cases/${caseId}/reduction-approvals`, async (route) => {
        await route.fulfill({ contentType: 'application/json', json: [] })
    })
}
