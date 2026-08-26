import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { dirname, extname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const repoRoot = join(frontendRoot, '..')
const contractPath = join(frontendRoot, 'src/modules/demo/demo.contract.ts')
const sessionPath = join(frontendRoot, 'src/modules/demo/demoUiSession.ts')
const httpPath = join(frontendRoot, 'src/api/http.ts')
const appPath = join(frontendRoot, 'src/App.vue')
const inputsPath = join(frontendRoot, 'src/modules/demo/pages/DemoInputs.vue')
const bannerPath = join(frontendRoot, 'src/components/demo/DemoBoundaryBanner.vue')

function walk(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name)
    return entry.isDirectory() ? walk(path) : [path]
  })
}

function frozenBackendBusinessKeys() {
  const systemRuntimeKeys = new Set([
    't_user',
    't_role',
    't_role_perm',
    't_user_role',
    't_doc_template',
    't_task_template',
    't_fee_rate_book',
    't_fee_rate',
  ])
  const tableKeys = new Set()
  for (const path of walk(join(repoRoot, 'backend/app'))) {
    if (extname(path) !== '.py') continue
    for (const match of readFileSync(path, 'utf8').matchAll(/__tablename__\s*=\s*["']([^"']+)["']/g)) {
      tableKeys.add(match[1])
    }
  }
  return [...tableKeys].filter((key) => !systemRuntimeKeys.has(key)).sort()
}

function typeScriptDataUrl(path, replacements = {}) {
  let source = readFileSync(path, 'utf8')
  for (const [from, to] of Object.entries(replacements)) source = source.replaceAll(from, to)
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.ESNext,
      target: ts.ScriptTarget.ES2022,
    },
    fileName: path,
  }).outputText
  return `data:text/javascript;base64,${Buffer.from(output).toString('base64')}`
}

const contractUrl = typeScriptDataUrl(contractPath)
const contract = await import(contractUrl)
const expectedBusinessKeys = frozenBackendBusinessKeys()
assert.equal(
  contract.DEMO_UI_PARITY_SCHEMA_ID,
  'fpms.demo-v6-ui-parity/v1',
  'missing canonical UI-session schema parser',
)
assert.deepEqual(
  contract.DEMO_BUSINESS_COUNT_KEYS,
  expectedBusinessKeys,
  'missing exact complete Ordinal 02 business-count projection',
)

const zeroCounts = Object.fromEntries(expectedBusinessKeys.map((key) => [key, 0]))
const validPreflight = {
  classification: 'DEMO_ONLY',
  bundle_id: 'integrated-a',
  bundle_version: 'v2',
  manifest_sha256: '1'.repeat(64),
  template_code: 'DEMO',
  template_sha256: '2'.repeat(64),
  template_required_variables: [],
  item_code: 'SERVICE',
  name_zh_cn: '演示服务费',
  currency: 'CNY',
  amount: '1200.00',
  source_ref: 'synthetic',
  source_version: 'v1',
  source_sha256: '3'.repeat(64),
  disclaimer_zh_cn: '仅用于合成演示',
  authority_classification: 'SYNTHETIC_TEST_ONLY',
  customer_activation_eligible: false,
  readiness: 'READY',
  run_id: 'ui-human-contract',
  candidate_commit: '4'.repeat(40),
  candidate_tree: '5'.repeat(40),
  authority_sha256: '6'.repeat(64),
  contract_version: 'fpms.demo-v6-ui-parity/v1',
  business_counts: zeroCounts,
}

assert.equal(contract.parseDemoUiSessionPreflight(validPreflight).run_id, validPreflight.run_id)
for (const mutate of [
  (value) => { delete value.business_counts[expectedBusinessKeys[0]] },
  (value) => { value.business_counts.unfrozen_table = 0 },
  (value) => { value.business_counts[expectedBusinessKeys[0]] = 1 },
  (value) => { value.authority_classification = 'CUSTOMER_AUTHORIZED' },
  (value) => { value.contract_version = 'fpms.demo-v6-ui-parity/v0' },
  (value) => { value.candidate_commit = 'not-a-commit' },
]) {
  const changed = structuredClone(validPreflight)
  mutate(changed)
  assert.throws(() => contract.parseDemoUiSessionPreflight(changed), /FinanceContractError/)
}

const defaultAPreflight = structuredClone(validPreflight)
defaultAPreflight.authority_classification = 'CUSTOMER_AUTHORIZED'
defaultAPreflight.customer_activation_eligible = true
defaultAPreflight.run_id = null
defaultAPreflight.candidate_commit = null
defaultAPreflight.candidate_tree = null
defaultAPreflight.contract_version = null
assert.equal(
  contract.parseDemoPreflight(defaultAPreflight).authority_classification,
  'CUSTOMER_AUTHORIZED',
  'the V6-only decoder must not absorb /demo/abc',
)

const session = await import(typeScriptDataUrl(sessionPath, {
  "'./demo.contract'": `'${contractUrl}'`,
}))

class MemoryStorage {
  values = new Map()
  getItem(key) { return this.values.get(key) ?? null }
  setItem(key, value) { this.values.set(key, value) }
  removeItem(key) { this.values.delete(key) }
}

const storage = new MemoryStorage()
assert.equal(
  session.configureDemoObserverBinding(
    'http://127.0.0.1:5173/demo/inputs?fpmsObserverBinding=http%3A%2F%2F127.0.0.1%3A43123%2Fobserver-artifact',
  ),
  true,
)
assert.equal(session.activateDemoUiSession(validPreflight, storage), true)
const persisted = JSON.parse(storage.getItem(session.DEMO_UI_SESSION_STORAGE_KEY))
assert.deepEqual(Object.keys(persisted).sort(), [
  'authority_classification',
  'authority_sha256',
  'candidate_commit',
  'candidate_tree',
  'contract_version',
  'run_id',
])
assert.equal(session.restoreDemoUiSession(validPreflight, storage), true)

const drifted = structuredClone(validPreflight)
drifted.candidate_tree = '7'.repeat(40)
assert.equal(session.restoreDemoUiSession(drifted, storage), false)
assert.equal(storage.getItem(session.DEMO_UI_SESSION_STORAGE_KEY), null)
assert.equal(session.isDemoUiSessionActive(), false)
assert.equal(session.getDemoObserverLedger().at(-1).kind, 'STOP')

assert.equal(session.activateDemoUiSession(validPreflight, storage), true)
const actionId = session.recordVisibleAction({
  route: '/clients/new',
  role: 'button',
  label_or_testid: '保存',
})
const requestConfig = {
  method: 'post',
  url: '/clients?leak=customer@example.test',
  baseURL: 'http://127.0.0.1:8000/api/v1',
  data: {
    customer_name: '应被摘要',
    password: 'never-store-this',
    nested: { token: 'never-store-this-either', value: 3 },
  },
}
assert.equal(
  session.observeMutationRequest(requestConfig),
  requestConfig,
  'passive observer must return the identical Axios config synchronously',
)
await session.waitForObserverDigests()
session.observeMutationResponse(requestConfig, 201)
const mutation = session.getDemoObserverLedger().find((entry) => entry.kind === 'mutation')
assert.equal(mutation.action_id, actionId, 'mutation must correlate the immediately preceding action')
assert.equal(mutation.method, 'POST')
assert.equal(mutation.path, '/clients')
assert.equal(mutation.status, 201)
assert.match(mutation.payload_sha256, /^[0-9a-f]{64}$/)
const serializedLedger = JSON.stringify(session.getDemoObserverLedger())
for (const forbidden of [
  '应被摘要',
  'never-store-this',
  'customer@example.test',
  'password',
  'token',
]) {
  assert.ok(!serializedLedger.includes(forbidden), `observer leaked ${forbidden}`)
}

const handlers = { request: [], response: [] }
const fakeAxios = {
  interceptors: {
    request: { use(onFulfilled, onRejected) { handlers.request.push({ onFulfilled, onRejected }) } },
    response: { use(onFulfilled, onRejected) { handlers.response.push({ onFulfilled, onRejected }) } },
  },
}
session.installDemoUiObserver(fakeAxios)
assert.equal(handlers.request.length, 1)
assert.equal(handlers.response.length, 1)
assert.equal(handlers.request[0].onFulfilled({ method: 'get', url: '/cases' }).method, 'get')
assert.equal(fakeAxios.request, undefined, 'installing the observer must not issue a request')

const observerWrites = []
await session.finalizeDemoUiSessionEvidence(async (url, init) => {
  observerWrites.push({ url, init })
  return { ok: true, status: 201 }
})
assert.equal(observerWrites.length, 1)
assert.equal(observerWrites[0].url, 'http://127.0.0.1:43123/observer-artifact')
assert.equal(observerWrites[0].init.method, 'POST')
const observerBody = JSON.parse(observerWrites[0].init.body)
assert.equal(observerBody.filename, 'observer-ui-ledger.json')
assert.equal(observerBody.encoding, 'json')
assert.ok(Array.isArray(observerBody.content.events))

const httpSource = readFileSync(httpPath, 'utf8')
const appSource = readFileSync(appPath, 'utf8')
const inputsSource = readFileSync(inputsPath, 'utf8')
const bannerSource = readFileSync(bannerPath, 'utf8')
assert.ok(httpSource.includes('installDemoUiObserver(http)'))
assert.ok(appSource.includes('<DemoBoundaryBanner'))
assert.ok(bannerSource.includes('合成演示数据｜仅用于技术展示，非客户、生产或官方事实'))
assert.ok(inputsSource.includes('完成并导出本轮证据'))
assert.ok(inputsSource.includes('finalizeDemoUiSessionEvidence'))
assert.ok(!inputsSource.includes("http.post"))
assert.ok(!inputsSource.includes("http.put"))
assert.ok(!inputsSource.includes("http.patch"))
assert.ok(!inputsSource.includes("http.delete"))

console.log('demo V6 UI session contract: PASS')
