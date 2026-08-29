import { expect, test } from '@playwright/test'
import type { Route } from '@playwright/test'

const firstClient = {
  id: '94f25864-ca5c-4fdf-bd2c-f7a80ce81464',
  name: '澄岳智造技术（苏州）有限公司',
}
const secondClient = {
  id: '37b85ef7-07dd-41c8-91df-7c24fd268b52',
  name: '云衡新材料（上海）有限公司',
}

test('客户详情面包屑显示客户名称并在离开页面时清理上下文', async ({ page }) => {
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, '')

    if (request.method() === 'GET' && apiPath === '/auth/me') {
      return fulfillJson(route, { permissions: ['*'] })
    }
    if (request.method() === 'GET' && apiPath === `/clients/${firstClient.id}`) {
      return fulfillJson(route, clientResponse(firstClient.id, firstClient.name))
    }
    if (request.method() === 'GET' && apiPath === `/clients/${secondClient.id}`) {
      return fulfillJson(route, clientResponse(secondClient.id, secondClient.name))
    }
    if (request.method() === 'GET' && apiPath === '/clients') {
      return fulfillJson(route, {
        items: [
          clientResponse(firstClient.id, firstClient.name),
          clientResponse(secondClient.id, secondClient.name),
        ],
        page: 1,
        page_size: 20,
        total: 2,
      })
    }
    if (request.method() === 'GET' && apiPath === '/cases') {
      return fulfillJson(route, { items: [], page: 1, page_size: 20, total: 0 })
    }

    return fulfillJson(route, { detail: `未处理的客户面包屑测试请求：${apiPath}` }, 404)
  })

  await page.addInitScript(() => {
    window.localStorage.setItem('fpms_token', 'client-breadcrumb-test-token')
  })

  const header = page.locator('.header-breadcrumb')

  await page.goto(`/clients/${firstClient.id}`, { waitUntil: 'domcontentloaded' })
  await expect(header).toHaveText(`客户管理 / 客户详情 / ${firstClient.name}`)
  await expect(header).not.toContainText(firstClient.id)

  await page.getByRole('button', { name: '返回' }).click()
  await page.waitForURL((url) => url.pathname === '/clients')
  await expect(header).toHaveText('客户列表')
  await expect(header).not.toContainText(firstClient.name)
  await expect(header).not.toContainText(firstClient.id)

  const secondClientRow = page.getByRole('row').filter({ hasText: secondClient.name })
  await secondClientRow.getByRole('button', { name: `打开客户操作：${secondClient.name}` }).click()
  await page.getByRole('menuitem', { name: '查看' }).click()
  await page.waitForURL((url) => url.pathname === `/clients/${secondClient.id}`)
  await expect(header).toHaveText(`客户管理 / 客户详情 / ${secondClient.name}`)
  await expect(header).not.toContainText(firstClient.name)
  await expect(header).not.toContainText(secondClient.id)
})

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

function clientResponse(id: string, name: string): Record<string, unknown> {
  return {
    id,
    client_code: `CLIENT-${id.slice(0, 8)}`,
    name_cn: name,
    name_en: null,
    email: 'service@example.test',
    client_type: '企业',
    default_currency: 'CNY',
    is_active: true,
  }
}
