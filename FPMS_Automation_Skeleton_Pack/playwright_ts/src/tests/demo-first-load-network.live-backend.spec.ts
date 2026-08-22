import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import {
  expect,
  test,
  type APIRequestContext,
  type Browser,
  type Page,
  type Request,
  type Response,
} from '@playwright/test'

const baseUrl = process.env.FPMS_BASE_URL || 'http://127.0.0.1:5173'
const apiBaseUrl = process.env.FPMS_API_URL || 'http://127.0.0.1:8000/api/v1'
const adminUsername = process.env.FPMS_ADMIN_USERNAME || process.env.FPMS_DEMO_ADMIN_USERNAME || ''
const adminPassword = process.env.FPMS_ADMIN_PASSWORD || process.env.FPMS_DEMO_ADMIN_PASSWORD || ''

type RequestObservation = {
  method: string
  url: string
}

type ResponseObservation = RequestObservation & {
  status: number
  from_service_worker: boolean
}

type FailureObservation = RequestObservation & {
  error_text: string
}

type ContextObservation = {
  ordinal: number
  document_paths: string[]
  api_requests: RequestObservation[]
  api_options: RequestObservation[]
  request_failures: FailureObservation[]
  api_responses: ResponseObservation[]
}

type Evidence = {
  schema_version: 'fpms.demo-first-load-network/v1'
  frontend_origin: string
  case_id: string | null
  case_no: string | null
  contexts: ContextObservation[]
}

async function login(page: Page): Promise<void> {
  await page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })
  await page.locator('.el-form-item').nth(0).locator('input').fill(adminUsername)
  await page.locator('.el-form-item').nth(1).locator('input').fill(adminPassword)
  await page.getByRole('button', { name: '登 录' }).click()
  await expect(page).toHaveURL(/\/dashboard$/)
  await page.waitForLoadState('networkidle')
}

async function jsonBody<T>(
  response: Awaited<ReturnType<APIRequestContext['post']>>,
  status: number,
  label: string,
): Promise<T> {
  const body = await response.text()
  expect(response.status(), label).toBe(status)
  return JSON.parse(body) as T
}

async function seedCaseFixture(request: APIRequestContext): Promise<{ caseId: string; caseNo: string }> {
  const loginResponse = await request.post(`${apiBaseUrl}/auth/login`, {
    data: { username: adminUsername, password: adminPassword },
  })
  const loginResult = await jsonBody<{ access_token: string }>(loginResponse, 200, 'demo API login')
  const authorization = { Authorization: `Bearer ${loginResult.access_token}` }
  const suffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`.toUpperCase()
  const clientResponse = await request.post(`${apiBaseUrl}/clients`, {
    headers: authorization,
    data: {
      client_code: `CYZN-NET-${suffix}`,
      name_cn: `澄岳智造技术（苏州）有限公司-${suffix}`,
      default_currency: 'CNY',
    },
  })
  const client = await jsonBody<{ id: string }>(clientResponse, 201, 'demo client seed')
  const caseNo = `CYIP-NET-${suffix}`
  const caseResponse = await request.post(`${apiBaseUrl}/cases`, {
    headers: authorization,
    data: {
      case_no: caseNo,
      case_type: 'NORMAL',
      patent_category: 'INV',
      flow_dir: 'CN_DOMESTIC',
      client_id: client.id,
      title_cn: '一种柔性制造产线中视觉检测工位的自适应标定方法',
      fee_reduction: '0',
    },
  })
  const createdCase = await jsonBody<{ id: string }>(caseResponse, 201, 'demo case seed')
  return { caseId: createdCase.id, caseNo }
}

function isApiUrl(url: string): boolean {
  const parsed = new URL(url)
  return parsed.pathname === '/api/v1' || parsed.pathname.startsWith('/api/v1/')
}

function isSameOriginApiUrl(url: string): boolean {
  return isApiUrl(url) && new URL(url).origin === new URL(baseUrl).origin
}

function waitForApiResponse(page: Page, predicate: (url: URL) => boolean): Promise<Response> {
  return page.waitForResponse((response) => {
    const url = new URL(response.url())
    return response.request().method() === 'GET' && isSameOriginApiUrl(response.url()) && predicate(url)
  })
}

async function verifyFirstLoads(
  browser: Browser,
  caseId: string,
  caseNo: string,
  ordinal: number,
  evidence: Evidence,
): Promise<void> {
  const context = await browser.newContext()
  const page = await context.newPage()
  const observation: ContextObservation = {
    ordinal,
    document_paths: [],
    api_requests: [],
    api_options: [],
    request_failures: [],
    api_responses: [],
  }
  evidence.contexts.push(observation)

  page.on('requestfailed', (request: Request) => {
    observation.request_failures.push({
      method: request.method(),
      url: request.url(),
      error_text: request.failure()?.errorText || 'UNKNOWN',
    })
  })
  page.on('request', (request: Request) => {
    if (request.isNavigationRequest() && request.frame() === page.mainFrame()) {
      observation.document_paths.push(new URL(request.url()).pathname)
    }
    if (isApiUrl(request.url())) {
      const item = { method: request.method(), url: request.url() }
      observation.api_requests.push(item)
      if (request.method() === 'OPTIONS') observation.api_options.push(item)
    }
  })
  page.on('response', (response: Response) => {
    if (isApiUrl(response.url())) {
      observation.api_responses.push({
        method: response.request().method(),
        status: response.status(),
        url: response.url(),
        from_service_worker: response.fromServiceWorker(),
      })
    }
  })

  try {
    await login(page)
    const caseResponses = [
      waitForApiResponse(
        page,
        (url) => url.pathname === '/api/v1/cases' && url.searchParams.get('case_no') === caseNo,
      ),
      waitForApiResponse(page, (url) => url.pathname === `/api/v1/cases/${caseId}`),
      waitForApiResponse(
        page,
        (url) => url.pathname === `/api/v1/cases/${caseId}/lifecycle-overlay`,
      ),
    ]
    await page.goto(`${baseUrl}/cases/no/${caseNo}`, { waitUntil: 'domcontentloaded' })
    for (const response of await Promise.all(caseResponses)) expect(response.status()).toBe(200)
    await page.waitForLoadState('networkidle')
    await expect(page.getByText(caseNo, { exact: true }).first()).toBeVisible()
    await expect(
      page.getByText('一种柔性制造产线中视觉检测工位的自适应标定方法').first(),
    ).toBeVisible()
    const lifecycleState = page.getByLabel('当前案件生命周期状态')
    await expect(lifecycleState.getByText('业务阶段：新建案件')).toBeVisible()
    await expect(lifecycleState.getByText('官方程序阶段：尚未递交')).toBeVisible()
    await expect(lifecycleState.getByText('法律状态：权利尚未成立')).toBeVisible()
    await expect(lifecycleState.getByText('核验状态：已确认')).toBeVisible()
    await expect(page.getByText('Network Error')).toHaveCount(0)

    const paymentResponses = ['/payments', '/offsets', '/clients', '/bills'].map((suffix) =>
      waitForApiResponse(page, (url) => url.pathname === `/api/v1${suffix}`),
    )
    await page.goto(`${baseUrl}/billing/payments`, { waitUntil: 'domcontentloaded' })
    for (const response of await Promise.all(paymentResponses)) expect(response.status()).toBe(200)
    await page.waitForLoadState('networkidle')
    await expect(page.getByRole('heading', { name: '预收款管理报表' })).toBeVisible()
    await expect(page.getByRole('heading', { name: '暂无预收款记录' })).toBeVisible()
    await expect(page.getByText('暂无核销记录。')).toBeVisible()
    await expect(page.getByText('Network Error')).toHaveCount(0)

    const frontendOrigin = new URL(baseUrl).origin
    const apiFailures = observation.request_failures.filter((item) => isApiUrl(item.url))
    expect(apiFailures, `clean context ${ordinal} must have no failed API requests`).toEqual([])
    expect(observation.api_requests.length).toBeGreaterThan(0)
    expect(observation.api_requests.map((item) => new URL(item.url).origin)).toEqual(
      observation.api_requests.map(() => frontendOrigin),
    )
    expect(observation.api_options).toEqual([])
    expect(observation.document_paths).toEqual([
      '/login',
      `/cases/no/${caseNo}`,
      '/billing/payments',
    ])
  } finally {
    await context.close()
  }
}

test('@demo-first-load case detail and payments never depend on CORS preflight', async ({ browser, request }, testInfo) => {
  test.setTimeout(180_000)
  expect(adminUsername).toBeTruthy()
  expect(adminPassword).toBeTruthy()
  const evidence: Evidence = {
    schema_version: 'fpms.demo-first-load-network/v1',
    frontend_origin: new URL(baseUrl).origin,
    case_id: null,
    case_no: null,
    contexts: [],
  }

  try {
    const fixture = await seedCaseFixture(request)
    evidence.case_id = fixture.caseId
    evidence.case_no = fixture.caseNo
    for (let ordinal = 1; ordinal <= 3; ordinal += 1) {
      await verifyFirstLoads(browser, fixture.caseId, fixture.caseNo, ordinal, evidence)
    }
  } finally {
    const body = `${JSON.stringify(evidence, null, 2)}\n`
    await testInfo.attach('first-load-network-observations', {
      body: Buffer.from(body),
      contentType: 'application/json',
    })
    const evidenceDir = process.env.FPMS_DEMO_EVIDENCE_DIR
    if (evidenceDir) {
      await mkdir(evidenceDir, { recursive: true })
      await writeFile(path.join(evidenceDir, 'first-load-network-observations.json'), body)
    }
  }
})
