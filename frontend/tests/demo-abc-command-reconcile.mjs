import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const api = readFileSync(join(root, 'src/modules/demo/demo.api.ts'), 'utf8')

for (const endpoint of [
  '/demo/commands/bills/',
  '/demo/commands/payments/',
  '/demo/commands/offsets/',
]) {
  assert.ok(api.includes(endpoint), `missing durable command reconciliation ${endpoint}`)
}

for (const functionName of [
  'createDemoBill',
  'createDemoBankReceipt',
  'createDemoFullOffset',
]) {
  const start = api.indexOf(`export async function ${functionName}`)
  assert.ok(start >= 0, `missing ${functionName}`)
  const next = api.indexOf('\nexport async function ', start + 1)
  const body = api.slice(start, next < 0 ? api.length : next)
  assert.match(body, /catch \(error\)/, `${functionName} must handle unknown POST outcome`)
  assert.match(
    body,
    /reconcileUnknownCommand/,
    `${functionName} must reconcile through authoritative GET`,
  )
}

const lockStart = api.indexOf('export async function lockDemoDraft')
const lockEnd = api.indexOf('\nexport async function ', lockStart + 1)
const lockBody = api.slice(lockStart, lockEnd)
assert.match(lockBody, /catch \(error\)/)
assert.match(lockBody, /http\.get<DemoDraft>/)
assert.match(lockBody, /draft\.status === 'LOCKED'/)
assert.match(api, /async function reconcileUnknownCommand[\s\S]*http\.get/)
assert.match(api, /async function reconcileUnknownCommand[\s\S]*throw error/)

console.log('demo ABC command reconciliation source contract OK')
