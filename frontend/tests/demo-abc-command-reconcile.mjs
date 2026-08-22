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

let commandReads = 0
const completed = await helper.resolveCommandMutationResponse(
  { status: 202, data: { status: 'IN_PROGRESS' } },
  async () => {
    commandReads += 1
    return commandReads === 1
      ? { status: 202, data: { status: 'IN_PROGRESS' } }
      : { status: 200, data: { result: 'durable' } }
  },
  (value) => value.result,
  async () => {},
)
assert.equal(completed, 'durable')
assert.equal(commandReads, 2)

await assert.rejects(
  helper.resolveCommandMutationResponse(
    { status: 409, data: {} },
    async () => ({ status: 404, data: {} }),
    (value) => value,
    async () => {},
  ),
  (error) => error.message === '命令状态异常（409）。',
)
await assert.rejects(
  helper.resolveCommandMutationResponse(
    { status: 202, data: {} },
    async () => ({ status: 202, data: {} }),
    (value) => value,
    async () => {},
  ),
  (error) => error.message === '命令仍在处理中，请稍后重试。',
)

let lockReads = 0
await assert.rejects(
  helper.reconcileUnknownMutationResult(
    { isAxiosError: true, response: { status: 409 } },
    async () => {
      lockReads += 1
      return { status: 'LOCKED' }
    },
    (value) => value.status === 'LOCKED',
  ),
)
assert.equal(lockReads, 0)

const reconciledLock = await helper.reconcileUnknownMutationResult(
  { isAxiosError: true, response: undefined },
  async () => {
    lockReads += 1
    return { status: 'LOCKED' }
  },
  (value) => value.status === 'LOCKED',
)
assert.equal(reconciledLock.status, 'LOCKED')
assert.equal(lockReads, 1)

const api = await readFile(new URL('../src/modules/demo/demo.api.ts', import.meta.url), 'utf8')
for (const endpoint of [
  '/bills/from-drafts/idempotency/',
  '/payments/idempotency/',
  '/offsets/idempotency/',
]) {
  assert.ok(api.includes(endpoint), `missing durable command reconciliation ${endpoint}`)
}
assert.match(api, /if \(!shouldReconcileUnknownCommand\(error\)\) throw error/)
assert.match(api, /classification === 'ABSENT'/)
assert.match(api, /resolveCommandMutationResponse/)
assert.match(api, /reconcileUnknownMutationResult/)

console.log('demo ABC command reconciliation behavior contract OK')
