import { expect, test } from '@playwright/test'

const caseId = 'CASE-FEE-REDUCTION-APPROVAL'
const applicantId = 'APPLICANT-001'

const caseResponse = {
    id: caseId,
    case_no: 'CN-FEE-APPROVAL-001',
    case_type: 'NORMAL',
    patent_category: 'INV',
    title_cn: '费用减缴审批案件',
    status: 'NOT_FILED',
    flow_dir: 'CN_DOMESTIC',
    applicants: [],
    inventors: [],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
    fee_reduction: '0',
    discount_rate: null,
}

const futureApproval = {
    approval_id: 'APPROVAL-FUTURE',
    scope_type: 'APPLICANT_SET',
    case_id: null,
    applicant_set_key: 'APPLICANT-SET-FUTURE',
    reduction_ratio: '0.7000',
    fee_codes: ['ANNUITY_FEE'],
    fee_year_from: 2,
    fee_year_to: 4,
    effective_from: '2099-01-01',
    effective_to: '2099-12-31',
    source_evidence_version_id: 'EVIDENCE-FUTURE',
    confirmation_status: 'CONFIRMED',
    confirmed_at: '2026-07-21T09:00:00',
    confirmed_by: 'reviewer-future',
    is_current: false,
}

const createdApproval = {
    approval_id: 'APPROVAL-085',
    scope_type: 'CASE',
    case_id: caseId,
    applicant_set_key: null,
    reduction_ratio: '0.8500',
    fee_codes: ['APPLICATION_FEE'],
    fee_year_from: null,
    fee_year_to: null,
    effective_from: '2026-07-01',
    effective_to: null,
    source_evidence_version_id: 'EVIDENCE-VERSION-001',
    confirmation_status: 'CONFIRMED',
    confirmed_at: '2026-07-22T10:30:00',
    confirmed_by: 'reviewer-001',
    is_current: true,
}

test('案件编辑记录并选择减缴审批证据，锁定比例且保存时不伪造关联', async ({ page }) => {
    let approvals = [futureApproval]
    let approvalPost: Record<string, unknown> | undefined
    let casePut: Record<string, unknown> | undefined

    await page.route(`**/api/v1/cases/${caseId}`, async (route) => {
        if (route.request().method() === 'PUT') {
            casePut = route.request().postDataJSON() as Record<string, unknown>
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
        if (route.request().method() === 'POST') {
            approvalPost = route.request().postDataJSON() as Record<string, unknown>
            approvals = [futureApproval, createdApproval]
            await route.fulfill({ status: 201, contentType: 'application/json', json: { approval_id: createdApproval.approval_id } })
            return
        }
        await route.fulfill({ contentType: 'application/json', json: approvals })
    })

    await page.goto(`/cases/${caseId}/edit`)
    await expect(page.getByRole('heading', { name: '编辑案件' })).toBeVisible()
    await page.getByText('控制标记', { exact: true }).click()

    const serviceDiscountInput = page.getByPlaceholder('请输入 0 到 1 之间的小数')
    await expect(serviceDiscountInput).toBeEditable()
    await serviceDiscountInput.fill('0.6')
    await expect(page.getByText('选择审批依据仅解锁同一比例选项，不自动写入案件减缴字段。', { exact: true })).toBeVisible()
    await expect(page.getByText(/当前有效/)).toHaveCount(0)
    const canonicalReduction = page.getByTestId('case-fee-reduction')
    await canonicalReduction.click()
    await expect(page.getByRole('option', { name: '70%', exact: true })).toHaveAttribute('aria-disabled', 'true')
    await expect(page.getByRole('option', { name: '85%', exact: true })).toHaveAttribute('aria-disabled', 'true')
    await page.keyboard.press('Escape')

    await page.getByText('请选择后端返回的减缴审批依据', { exact: true }).click()
    await page.getByRole('option', { name: '70% · 申请人集合 · EVIDENCE-FUTURE' }).click()
    await expect(page.getByText('后端当前标记：否', { exact: true })).toBeVisible()
    await expect(canonicalReduction.getByText('不减缴', { exact: true })).toBeVisible()
    await canonicalReduction.click()
    await expect(page.getByRole('option', { name: '70%', exact: true })).not.toHaveAttribute('aria-disabled', 'true')
    await expect(page.getByRole('option', { name: '85%', exact: true })).toHaveAttribute('aria-disabled', 'true')
    await page.keyboard.press('Escape')

    await page.getByRole('button', { name: '记录减缴审批证据' }).click()
    const dialog = page.getByRole('dialog', { name: '记录减缴审批证据' })
    await dialog.getByText('请选择审批范围', { exact: true }).click()
    await page.getByText('案件', { exact: true }).last().click()
    await dialog.getByPlaceholder('请输入申请人标识，多个用逗号分隔').fill(applicantId)
    await dialog.getByPlaceholder('请输入资格属性版本').fill('eligibility-v1')
    await dialog.getByPlaceholder('请输入资格属性 JSON').fill(`{"${applicantId}":{"kind":"个人"}}`)
    await dialog.getByText('请选择减缴比例', { exact: true }).click()
    await page.getByText('85%', { exact: true }).last().click()
    await dialog.getByPlaceholder('请输入费用代码，多个用逗号分隔').fill('APPLICATION_FEE')
    await dialog.getByPlaceholder('请选择生效起始日').fill('2026-07-01')
    await dialog.getByPlaceholder('请输入来源证据版本标识').fill('EVIDENCE-VERSION-001')
    await dialog.getByPlaceholder('请输入来源内容哈希').fill('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    await dialog.getByPlaceholder('请选择确认时间').fill('2026-07-22T10:30:00')
    await dialog.getByRole('button', { name: '确认记录' }).click()

    await expect.poll(() => approvalPost).toEqual({
        case_id: caseId,
        scope_type: 'CASE',
        applicant_ids: [applicantId],
        eligibility_attributes_version: 'eligibility-v1',
        eligibility_attributes_json: `{"${applicantId}":{"kind":"个人"}}`,
        reduction_ratio: '0.85',
        fee_codes: ['APPLICATION_FEE'],
        fee_year_from: null,
        fee_year_to: null,
        effective_from: '2026-07-01',
        effective_to: null,
        source_evidence_version_id: 'EVIDENCE-VERSION-001',
        expected_source_content_hash: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        confirmed_at: '2026-07-22T10:30:00',
    })

    await expect(page.getByText('来源证据：EVIDENCE-VERSION-001', { exact: true })).toBeVisible()
    await expect(page.getByText('适用范围：案件', { exact: true })).toBeVisible()
    await expect(page.getByText('费用代码：APPLICATION_FEE', { exact: true })).toBeVisible()
    await expect(page.getByText('费用年度：不限', { exact: true })).toBeVisible()
    await expect(page.getByText('生效区间：2026-07-01 至 无截止日', { exact: true })).toBeVisible()
    await expect(page.getByText('申请人集合：不适用', { exact: true })).toBeVisible()
    await expect(page.getByText('后端当前标记：是', { exact: true })).toBeVisible()
    await expect(canonicalReduction.getByText('不减缴', { exact: true })).toBeVisible()
    await canonicalReduction.click()
    await expect(page.getByRole('option', { name: '70%', exact: true })).toHaveAttribute('aria-disabled', 'true')
    await expect(page.getByRole('option', { name: '85%', exact: true })).not.toHaveAttribute('aria-disabled', 'true')
    await page.getByRole('option', { name: '85%', exact: true }).click()
    await expect(canonicalReduction.getByText('85%', { exact: true })).toBeVisible()
    await expect(serviceDiscountInput).toHaveValue('0.6')

    await page.getByRole('button', { name: '保存修改' }).click()
    await expect.poll(() => casePut).toBeTruthy()
    expect(casePut).not.toHaveProperty('approval_id')
    expect(casePut).not.toHaveProperty('fee_reduction_approval_id')
    expect(casePut?.fee_reduction).toBe('0.85')
    expect(casePut?.discount_rate).toBe('0.6')
})

test('减缴审批列表失败时案件仍完成加载并锁定减缴比例', async ({ page }) => {
    await page.route(`**/api/v1/cases/${caseId}`, async (route) => {
        await route.fulfill({
            contentType: 'application/json',
            json: { ...caseResponse, case_no: '', fee_reduction: '0.7' },
        })
    })
    await page.route('**/api/v1/clients**', async (route) => {
        await route.fulfill({
            contentType: 'application/json',
            json: { items: [], page: 1, page_size: 100, total: 0 },
        })
    })
    await page.route(`**/api/v1/fees/cases/${caseId}/reduction-approvals`, async (route) => {
        await route.fulfill({
            status: 503,
            contentType: 'application/json',
            json: { detail: 'approval service unavailable' },
        })
    })

    await page.goto(`/cases/${caseId}/edit`)

    await expect(page.getByPlaceholder('请输入案件标题')).toHaveValue('费用减缴审批案件')
    await page.getByText('控制标记', { exact: true }).click()
    await expect(page.getByText('减缴审批依据加载失败，减缴比例已锁定，请稍后重试。', { exact: true })).toBeVisible()
    await expect(page.getByTestId('case-fee-reduction').locator('input')).toBeDisabled()
    await expect(page.getByRole('button', { name: '保存修改' })).toBeEnabled()
})
