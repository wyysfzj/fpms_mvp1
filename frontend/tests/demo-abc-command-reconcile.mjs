import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { readFile } from 'node:fs/promises'
import ts from 'typescript'

const helperSource = await readFile(
  new URL('../src/modules/demo/command-reconcile.ts', import.meta.url),
  'utf8',
)
const compiled = ts.transpileModule(helperSource, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2022,
  },
}).outputText
const helper = await import(
  `data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`
)

assert.equal(
  helper.shouldReconcileUnknownCommand({ status: 0, code: 'UNKNOWN_ERROR' }),
  true,
)
assert.equal(
  helper.shouldReconcileUnknownCommand({ isAxiosError: true, response: undefined }),
  true,
)
for (const deterministic of [
  { status: 409, code: 'DEMO_FINANCE_IDEMPOTENCY_CONFLICT' },
  { status: 422, code: 'VALIDATION_ERROR' },
  { isAxiosError: true, response: { status: 409 } },
  new Error('ordinary programming error'),
]) {
  assert.equal(helper.shouldReconcileUnknownCommand(deterministic), false)
}

assert.equal(helper.classifyCommandReadStatus(200), 'COMPLETED')
assert.equal(helper.classifyCommandReadStatus(202), 'IN_PROGRESS')
assert.equal(helper.classifyCommandReadStatus(404), 'ABSENT')
assert.equal(helper.classifyCommandReadStatus(409), 'INVALID')

const api = await readFile(new URL('../src/modules/demo/demo.api.ts', import.meta.url), 'utf8')
for (const endpoint of [
  '/bills/from-drafts/idempotency/',
  '/payments/idempotency/',
  '/offsets/idempotency/',
]) {
  assert.ok(api.includes(endpoint), `missing durable command reconciliation ${endpoint}`)
}
assert.match(api, /if \(!shouldReconcileUnknownCommand\(error\)\) throw error/)
assert.match(api, /classification === 'IN_PROGRESS'/)
assert.match(api, /classification === 'ABSENT'/)

console.log('demo ABC command reconciliation behavior contract OK')
