import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const api = readFileSync(join(root, 'src/modules/demo/demo.api.ts'), 'utf8')
const page = readFileSync(join(root, 'src/modules/demo/pages/DemoAbc.vue'), 'utf8')
const router = readFileSync(join(root, 'src/router/index.ts'), 'utf8')
const menu = readFileSync(join(root, 'src/constants/menu.ts'), 'utf8')

for (const endpoint of [
  '/fees/demo-service-item',
  '/fees/demo-service-obligations',
  '/bills/demo-from-draft',
  '/payments/demo-bank-receipts',
  '/offsets/demo-full',
]) {
  assert.ok(api.includes(endpoint), `missing exact demo endpoint ${endpoint}`)
}

for (const forbidden of [
  "'/bills/from-drafts'",
  "'/payments'",
  "'/offsets'",
  'page.route(',
  'route.fulfill(',
]) {
  assert.ok(!page.includes(forbidden) && !api.includes(forbidden), `forbidden demo seam ${forbidden}`)
}

assert.ok(router.includes("path: 'demo/abc'"))
assert.ok(menu.includes("route: '/demo/abc'"))
assert.ok(page.includes('DEMO_ONLY'))
assert.ok(page.includes('template_sha256'))
assert.ok(page.includes('manifest_sha256'))
assert.ok(page.includes('idempotencyKeys'))
assert.ok(!page.includes('amount || 0'))
assert.ok(!page.includes('Number('))
assert.match(
  api,
  /http\.post\(`\/fees\/drafts\/\$\{draftId\}\/lock`\)[\s\S]*http\.get<DemoDraft>\(`\/fees\/drafts\/\$\{draftId\}`\)/,
  'draft lock acknowledgement must be reconciled with the authoritative draft detail',
)

console.log('demo ABC frontend source contract OK')
