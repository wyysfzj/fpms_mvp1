import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

// TypeScript's parser supplies the same syntax-tree gate for this TS source that Acorn supplies for JS.
const here = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(here, '../../../..')
const specPath = path.join(here, 'demo-integrated-v6.live-backend.spec.ts')
const lifecyclePath = path.join(repoRoot, 'docs/postdemo/demo-lifecycle-customer-v6.html')
const runbookPath = path.join(repoRoot, 'docs/postdemo/demo-lifecycle-customer-v6-runbook.md')

for (const required of [specPath, lifecyclePath, runbookPath]) {
  assert.ok(fs.existsSync(required), `missing V6 artifact: ${required}`)
}

const source = fs.readFileSync(specPath, 'utf8')
const lifecycle = fs.readFileSync(lifecyclePath, 'utf8')
const runbook = fs.readFileSync(runbookPath, 'utf8')
const ast = ts.createSourceFile(specPath, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
assert.equal(ast.parseDiagnostics.length, 0, 'V6 live spec must parse without diagnostics')

const stages = Array.from({ length: 11 }, (_, index) => String(index + 1).padStart(2, '0'))
assert.deepEqual(
  [...lifecycle.matchAll(/data-stage="(\d{2})"/g)].map((match) => match[1]),
  stages,
  'lifecycle must contain exact stages 01 through 11',
)
assert.deepEqual(
  [...runbook.matchAll(/^## 阶段 (\d{2})/gm)].map((match) => match[1]),
  stages,
  'runbook must contain exact stages 01 through 11',
)

const requiredFields = ['演示话术', 'UI/操作', '输入', '屏幕输出', '期待结果', '验证方法', '事实边界', '停止条件', '最近新增']
for (let index = 0; index < stages.length; index += 1) {
  const start = runbook.indexOf(`## 阶段 ${stages[index]}`)
  const end = index + 1 < stages.length ? runbook.indexOf(`## 阶段 ${stages[index + 1]}`) : runbook.length
  const body = runbook.slice(start, end)
  for (const field of requiredFields) assert.ok(body.includes(`**${field}**`), `stage ${stages[index]} missing ${field}`)
}

for (const token of [
  "import './demo-integrated-a.live-backend.spec'",
  "test.step('07 生效官费预览'",
  "test.step('08 双草单与服务费调整'",
  "test.step('09 官费清单与待凭证登记'",
  "test.step('10 两次客户回款与核销'",
  "test.step('11 同案双轨汇总'",
  'official-fee-preview',
  'official-fee-confirmation',
  'demo-service-adjustment',
  'REGISTERED_PENDING_OFFICIAL_EVIDENCE',
  'PARTIALLY_SETTLED',
  'SETTLED',
  'authoritativePartialBill.balance',
  'consoleErrors',
  'networkErrors',
  'v6-stages.json',
]) assert.ok(source.includes(token), `V6 spec missing ${token}`)

for (const forbidden of ['page.route(', 'route.fulfill(', 'test.skip(', '/demo/abc']) {
  assert.ok(!source.includes(forbidden), `V6 shared route contains forbidden token ${forbidden}`)
}

for (const token of ['SYNTHETIC_TEST_ONLY', '非客户授权', '候选预览，尚未形成缴费义务', '已登记，待官方凭证核验']) {
  assert.ok(lifecycle.includes(token) && runbook.includes(token), `V6 customer materials missing ${token}`)
}

console.log('demo-integrated-v6 static contract: PASS')
