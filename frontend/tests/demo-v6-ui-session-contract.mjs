import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync, readdirSync } from 'node:fs'
import { dirname, extname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { deflateSync } from 'node:zlib'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const repoRoot = join(frontendRoot, '..')
const contractPath = join(frontendRoot, 'src/modules/demo/demo.contract.ts')
const sessionPath = join(frontendRoot, 'src/modules/demo/demoUiSession.ts')
const httpPath = join(frontendRoot, 'src/api/http.ts')
const appPath = join(frontendRoot, 'src/App.vue')
const apiPath = join(frontendRoot, 'src/modules/demo/demo.api.ts')
const inputsPath = join(frontendRoot, 'src/modules/demo/pages/DemoInputs.vue')
const bannerPath = join(frontendRoot, 'src/components/demo/DemoBoundaryBanner.vue')

function walk(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name)
    return entry.isDirectory() ? walk(path) : [path]
  })
}

function frozenBackendBusinessKeys() {
  const runtime = new Set(['t_user', 't_role', 't_role_perm', 't_user_role', 't_doc_template', 't_task_template', 't_fee_rate_book', 't_fee_rate'])
  const keys = new Set()
  for (const path of walk(join(repoRoot, 'backend/app'))) {
    if (extname(path) !== '.py') continue
    for (const match of readFileSync(path, 'utf8').matchAll(/__tablename__\s*=\s*["']([^"']+)["']/g)) keys.add(match[1])
  }
  return [...keys].filter((key) => !runtime.has(key)).sort()
}

function tsUrl(path, replacements = {}) {
  let source = readFileSync(path, 'utf8')
  for (const [from, to] of Object.entries(replacements)) source = source.replaceAll(from, to)
  const js = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
    fileName: path,
  }).outputText
  return `data:text/javascript;base64,${Buffer.from(js).toString('base64')}#${Math.random()}`
}

const contractUrl = tsUrl(contractPath)
const contract = await import(contractUrl)
const exactKeys = frozenBackendBusinessKeys()
assert.deepEqual(contract.DEMO_BUSINESS_COUNT_KEYS, exactKeys)

const preflight = {
  classification: 'DEMO_ONLY', bundle_id: 'integrated-a', bundle_version: 'v2',
  manifest_sha256: '1'.repeat(64), template_code: 'DEMO', template_sha256: '2'.repeat(64),
  template_required_variables: [], item_code: 'SERVICE', name_zh_cn: '演示服务费', currency: 'CNY',
  amount: '1200.00', source_ref: 'synthetic', source_version: 'v1', source_sha256: '3'.repeat(64),
  disclaimer_zh_cn: '仅用于合成演示', authority_classification: 'SYNTHETIC_TEST_ONLY',
  customer_activation_eligible: false, readiness: 'READY', run_id: 'ui-human-contract',
  candidate_commit: '4'.repeat(40), candidate_tree: '5'.repeat(40), authority_sha256: '6'.repeat(64),
  contract_version: 'fpms.demo-v6-ui-parity/v1',
  business_counts: Object.fromEntries(exactKeys.map((key) => [key, 0])),
}
assert.equal(contract.parseDemoUiSessionPreflight(preflight).run_id, preflight.run_id)
for (const mutate of [
  (row) => { delete row.business_counts[exactKeys[0]] },
  (row) => { row.business_counts.extra = 0 },
  (row) => { row.business_counts[exactKeys[0]] = 1 },
  (row) => { row.authority_classification = 'CUSTOMER_AUTHORIZED' },
  (row) => { row.contract_version = 'fpms.demo-v6-ui-parity/v0' },
]) {
  const row = structuredClone(preflight); mutate(row)
  assert.throws(() => contract.parseDemoUiSessionPreflight(row), /FinanceContractError/)
}
const defaultA = structuredClone(preflight)
Object.assign(defaultA, { authority_classification: 'CUSTOMER_AUTHORIZED', customer_activation_eligible: true, run_id: null, candidate_commit: null, candidate_tree: null, contract_version: null })
assert.equal(contract.parseDemoPreflight(defaultA).authority_classification, 'CUSTOMER_AUTHORIZED')

const sessionImport = () => import(tsUrl(sessionPath, { "'./demo.contract'": `'${contractUrl}'` }))
const session = await sessionImport()

class MemoryStorage {
  values = new Map()
  getItem(key) { return this.values.get(key) ?? null }
  setItem(key, value) { this.values.set(key, value) }
  removeItem(key) { this.values.delete(key) }
}
class MemoryStages {
  rows = []
  async put(runId, stage, png) { this.rows.push({ runId, stage, png }) }
  async list(runId) { return this.rows.filter((row) => row.runId === runId).map(({ stage, png }) => ({ stage, png })).sort((a, b) => a.stage - b.stage) }
  async clear(runId) { this.rows = this.rows.filter((row) => row.runId !== runId) }
}

const tuple = {
  contract_version: preflight.contract_version, run_id: preflight.run_id,
  candidate_commit: preflight.candidate_commit, candidate_tree: preflight.candidate_tree,
  authority_sha256: preflight.authority_sha256, actor: 'HUMAN',
}
const capability = 'unguessable_test_capability_0123456789ABCDEF'
const binding = `http://127.0.0.1:43123/observer-artifact?capability=${capability}&actor=HUMAN`
const pageUrl = `http://127.0.0.1:5173/?fpmsObserverBinding=${encodeURIComponent(binding)}`
assert.equal(session.configureDemoObserverBinding(pageUrl), true)
for (const bad of [
  'http://example.test/?fpmsObserverBinding=x',
  `http://127.0.0.1:5173/?fpmsObserverBinding=${encodeURIComponent('http://127.0.0.1:43123/observer-artifact?actor=HUMAN')}`,
  `http://127.0.0.1:5173/?fpmsObserverBinding=${encodeURIComponent(`http://127.0.0.1:43123/observer-artifact?capability=${capability}&actor=ROBOT`)}`,
]) assert.equal(session.configureDemoObserverBinding(bad), false)
assert.equal(session.configureDemoObserverBinding(pageUrl), true)

const requests = []
function hostResponse(status, body) {
  return { ok: status >= 200 && status < 300, status, json: async () => body }
}
const hostFetch = async (url, init) => {
  const body = JSON.parse(init.body)
  requests.push({ url, body })
  for (const [key, value] of Object.entries(tuple)) assert.equal(body[key], value, `host tuple ${key}`)
  const pathname = new URL(url).pathname
  assert.equal(new URL(url).searchParams.get('capability'), capability)
  assert.equal(new URL(url).searchParams.has('actor'), false)
  if (pathname === '/revalidate') return hostResponse(200, { status: 'VALID' })
  if (pathname === '/observer-artifact') return hostResponse(201, { filename: body.filename })
  if (pathname === '/stop') return hostResponse(200, { status: 'STOPPED' })
  if (pathname === '/finalize') return hostResponse(200, { status: 'FINALIZED' })
  return hostResponse(404, { error: 'NOT_FOUND' })
}
const storage = new MemoryStorage()
assert.equal(await session.activateDemoUiSession(preflight, storage, hostFetch), true)
assert.deepEqual(requests[0], { url: `http://127.0.0.1:43123/revalidate?capability=${capability}`, body: tuple })
const stored = JSON.parse(storage.getItem(session.DEMO_UI_SESSION_STORAGE_KEY))
assert.equal(stored.binding, binding)
assert.deepEqual(stored.tuple, tuple)
assert.ok(!JSON.stringify(session.getDemoObserverLedger()).includes(capability))

const reloaded = await sessionImport()
assert.equal(await reloaded.restoreDemoUiSession(storage, hostFetch), true)
assert.equal(requests.filter((entry) => new URL(entry.url).pathname === '/revalidate').length, 2)
assert.ok(!readFileSync(appPath, 'utf8').includes('readDemoPreflight'))

function crc32(bytes) {
  let crc = 0xffffffff
  for (const byte of bytes) { crc ^= byte; for (let bit = 0; bit < 8; bit += 1) crc = (crc >>> 1) ^ ((crc & 1) ? 0xedb88320 : 0) }
  return (crc ^ 0xffffffff) >>> 0
}
function chunk(name, data) {
  const type = Buffer.from(name)
  const length = Buffer.alloc(4); length.writeUInt32BE(data.length)
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([type, data])))
  return Buffer.concat([length, type, data, crc])
}
function png(stage) {
  const width = 640; const height = 360
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(width, 0); ihdr.writeUInt32BE(height, 4); ihdr[8] = 8; ihdr[9] = 2
  const row = Buffer.alloc(1 + width * 3); row[0] = 0
  for (let x = 0; x < width; x += 1) { row[1 + x * 3] = stage * 17; row[2 + x * 3] = x % 251; row[3 + x * 3] = (stage * 29 + x) % 251 }
  const raw = Buffer.concat(Array.from({ length: height }, () => row))
  return new Blob([Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw)), chunk('IEND', Buffer.alloc(0))])], { type: 'image/png' })
}

const stageStore = new MemoryStages()
let stage = 0
reloaded.setDemoStageEvidenceAdaptersForTest(stageStore, async () => png(++stage))
for (let value = 1; value <= 11; value += 1) await reloaded.captureDemoStageScreenshot(value)
assert.equal(await reloaded.getNextDemoScreenshotStage(), null)
assert.equal(new Set(await Promise.all(stageStore.rows.map(async (row) => createHash('sha256').update(Buffer.from(await row.png.arrayBuffer())).digest('hex')))).size, 11)
await reloaded.finalizeDemoUiSessionEvidence(hostFetch)
const finalPaths = requests.slice(2).map((entry) => new URL(entry.url).pathname)
assert.deepEqual(finalPaths, ['/observer-artifact', ...Array(11).fill('/observer-artifact'), '/finalize'])
assert.equal(requests.at(-13).body.filename, 'observer-ui-ledger.json')
for (let value = 1; value <= 11; value += 1) assert.equal(requests.at(-13 + value).body.filename, `observer-stage-${String(value).padStart(2, '0')}.png`)
assert.equal(storage.getItem(reloaded.DEMO_UI_SESSION_STORAGE_KEY), null)

const stopped = await sessionImport()
const stopStorage = new MemoryStorage()
assert.equal(stopped.configureDemoObserverBinding(pageUrl), true)
assert.equal(await stopped.activateDemoUiSession(preflight, stopStorage, hostFetch), true)
await stopped.handleDemoUiRoute('/demo/abc', stopStorage, hostFetch)
assert.equal(stopped.isDemoUiSessionActive(), false)
assert.equal(stopped.getDemoObserverLedger().at(-1).kind, 'STOP')
assert.equal(new URL(requests.at(-1).url).pathname, '/stop')
assert.equal(requests.at(-1).body.ledger.events.at(-1).kind, 'STOP')

for (const [reason, trigger] of [
  ['manual preflight', async (module, localStorage) => {
    const invalid = structuredClone(preflight)
    invalid.business_counts[exactKeys[0]] = 1
    assert.equal(await module.activateDemoUiSession(invalid, localStorage, hostFetch), false)
  }],
  ['unmatched mutation', async (module) => {
    module.observeMutationRequest({ method: 'patch', url: '/cases/1', data: { value: 1 } })
  }],
]) {
  const module = await sessionImport()
  const localStorage = new MemoryStorage()
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  if (reason !== 'manual preflight') assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
  const beforeStop = requests.length
  await trigger(module, localStorage)
  await module.waitForObserverDigests()
  await new Promise((resolve) => setTimeout(resolve, 0))
  assert.equal(module.isDemoUiSessionActive(), false, `${reason} must STOP`)
  assert.equal(module.getDemoObserverLedger().at(-1).kind, 'STOP', `${reason} must be auditable`)
  const stopExport = requests.slice(beforeStop).findLast((entry) => new URL(entry.url).pathname === '/stop')
  assert.equal(stopExport?.body.ledger.events.at(-1).kind, 'STOP', `${reason} must export STOP`)
}

const revalidationSession = await sessionImport()
const revalidationStorage = new MemoryStorage()
assert.equal(revalidationSession.configureDemoObserverBinding(pageUrl), true)
assert.equal(await revalidationSession.activateDemoUiSession(preflight, revalidationStorage, hostFetch), true)
const rejectRevalidationFetch = async (url, init) => {
  if (new URL(url).pathname === '/revalidate') return hostResponse(409, { error: 'SESSION_TUPLE_CONFLICT' })
  return hostFetch(url, init)
}
const revalidationReload = await sessionImport()
assert.equal(await revalidationReload.restoreDemoUiSession(revalidationStorage, rejectRevalidationFetch), false)
await new Promise((resolve) => setTimeout(resolve, 0))
assert.equal(revalidationReload.getDemoObserverLedger().at(-1).kind, 'STOP')

const rejectedFinalize = await sessionImport()
const rejectedStorage = new MemoryStorage()
const rejectedStages = new MemoryStages()
let rejectedStage = 0
assert.equal(rejectedFinalize.configureDemoObserverBinding(pageUrl), true)
assert.equal(await rejectedFinalize.activateDemoUiSession(preflight, rejectedStorage, hostFetch), true)
rejectedFinalize.setDemoStageEvidenceAdaptersForTest(rejectedStages, async () => png(++rejectedStage))
for (let value = 1; value <= 11; value += 1) await rejectedFinalize.captureDemoStageScreenshot(value)
const rejectedCalls = []
const rejectPngFetch = async (url, init) => {
  const body = JSON.parse(init.body)
  rejectedCalls.push({ url, body })
  if (body.filename === 'observer-stage-01.png') return hostResponse(409, { error: 'OBSERVER_EVIDENCE_CONFLICT' })
  if (new URL(url).pathname === '/stop') return hostResponse(200, { status: 'STOPPED' })
  return hostResponse(201, { filename: body.filename })
}
await assert.rejects(rejectedFinalize.finalizeDemoUiSessionEvidence(rejectPngFetch), /OBSERVER_STATUS_409/)
assert.equal(rejectedFinalize.getDemoObserverLedger().at(-1).kind, 'STOP')
assert.equal(rejectedStorage.getItem(rejectedFinalize.DEMO_UI_SESSION_STORAGE_KEY), null)
assert.equal(rejectedStages.rows.length, 11)
assert.deepEqual(rejectedCalls.map((entry) => entry.body.filename ?? new URL(entry.url).pathname), ['observer-ui-ledger.json', 'observer-stage-01.png', '/stop'])

const interceptorState = { request: new Map(), response: new Map(), requestEjects: 0, responseEjects: 0, next: 0 }
const fakeAxios = { interceptors: {
  request: { use(ok, bad) { const id = interceptorState.next++; interceptorState.request.set(id, { ok, bad }); return id }, eject(id) { interceptorState.request.delete(id); interceptorState.requestEjects++ } },
  response: { use(ok, bad) { const id = interceptorState.next++; interceptorState.response.set(id, { ok, bad }); return id }, eject(id) { interceptorState.response.delete(id); interceptorState.responseEjects++ } },
} }

const readOnlyPreviewSession = await sessionImport()
assert.equal(readOnlyPreviewSession.configureDemoObserverBinding(pageUrl), true)
assert.equal(await readOnlyPreviewSession.activateDemoUiSession(preflight, new MemoryStorage(), hostFetch), true)
const retainedActionId = readOnlyPreviewSession.recordVisibleAction({
  route: '/documents/new', role: 'button', label_or_testid: '预览文书影响',
})
readOnlyPreviewSession.observeMutationRequest({
  method: 'post', url: '/documents/impact-preview', data: { case_id: 'case-1' },
})
assert.equal(readOnlyPreviewSession.getDemoObserverLedger().some((event) => event.kind === 'mutation'), false)
assert.equal(readOnlyPreviewSession.isDemoUiSessionActive(), true)
readOnlyPreviewSession.observeMutationRequest({
  method: 'post', url: '/documents', data: { title: '客户来文' },
})
assert.equal(readOnlyPreviewSession.getDemoObserverLedger().find((event) => event.kind === 'mutation')?.action_id, retainedActionId)
assert.equal(readOnlyPreviewSession.isDemoUiSessionActive(), true)

const axiosSession = await sessionImport()
assert.equal(axiosSession.configureDemoObserverBinding(pageUrl), true)
assert.equal(await axiosSession.activateDemoUiSession(preflight, new MemoryStorage(), hostFetch), true)
let dispose = axiosSession.installDemoUiObserver(fakeAxios)
assert.deepEqual([interceptorState.request.size, interceptorState.response.size], [1, 1])
dispose = axiosSession.installDemoUiObserver(fakeAxios)
assert.deepEqual([interceptorState.request.size, interceptorState.response.size, interceptorState.requestEjects, interceptorState.responseEjects], [1, 1, 1, 1])
const requestConfig = { method: 'post', url: '/clients', data: { password: 'secret', customer_name: '张三' } }
axiosSession.recordVisibleAction({ route: '/clients', role: 'button', label_or_testid: '保存' })
interceptorState.request.values().next().value.ok(requestConfig)
const responseHandler = interceptorState.response.values().next().value
const conflict = { config: requestConfig, response: { status: 409 }, name: 'AxiosError', code: 'ERR_BAD_RESPONSE' }
await assert.rejects(responseHandler.bad(conflict), (error) => error === conflict)
assert.equal(axiosSession.getDemoObserverLedger().find((event) => event.kind === 'mutation').status, 409)
assert.equal(axiosSession.isDemoUiSessionActive(), true)
axiosSession.recordVisibleAction({ route: '/clients', role: 'button', label_or_testid: '保存' })
const transportConfig = { method: 'delete', url: '/clients/1', data: null }
interceptorState.request.values().next().value.ok(transportConfig)
const transport = { config: transportConfig, name: 'AxiosError', code: 'ERR_NETWORK' }
await assert.rejects(responseHandler.bad(transport), (error) => error === transport)
assert.equal(axiosSession.getDemoObserverLedger().findLast((event) => event.kind === 'mutation').status, 0)
assert.equal(axiosSession.isDemoUiSessionActive(), false)
dispose()
assert.deepEqual([interceptorState.request.size, interceptorState.response.size], [0, 0])

class FakeTarget {
  listeners = new Map()
  addEventListener(name, handler) { this.listeners.set(`${name}:${String(handler)}`, { name, handler }) }
  removeEventListener(name, handler) { this.listeners.delete(`${name}:${String(handler)}`) }
  dispatchEvent(event) {
    for (const entry of this.listeners.values()) if (entry.name === event.type) entry.handler(event)
    return true
  }
  count(name) { return [...this.listeners.values()].filter((entry) => entry.name === name).length }
}
const savedWindow = globalThis.window
const savedDocument = globalThis.document
const savedCustomEvent = globalThis.CustomEvent
const savedFetch = globalThis.fetch
const fakeWindow = new FakeTarget()
fakeWindow.location = { pathname: '/', href: pageUrl, origin: 'http://127.0.0.1:5173' }
fakeWindow.history = { state: null, replaceState() {} }
const fakeDocument = new FakeTarget()
globalThis.window = fakeWindow
globalThis.document = fakeDocument
globalThis.CustomEvent = class { constructor(type) { this.type = type } }
globalThis.fetch = hostFetch
const domSession = await sessionImport()
assert.equal(domSession.configureDemoObserverBinding(pageUrl), true)
assert.equal(await domSession.activateDemoUiSession(preflight, new MemoryStorage(), hostFetch), true)
const originalConsoleError = console.error
let disposeDom = domSession.installDemoUiDomObserver()
assert.notEqual(console.error, originalConsoleError)
assert.deepEqual([fakeDocument.count('click'), fakeDocument.count('submit'), fakeWindow.count('error'), fakeWindow.count('unhandledrejection')], [1, 1, 1, 1])
fakeWindow.location.pathname = '/login'
fakeWindow.dispatchEvent({ type: 'error', message: 'ignored login error', error: new Error('ignored login error') })
assert.equal(domSession.isDemoUiSessionActive(), true, '/login must not be observed')
fakeWindow.location.pathname = '/'
disposeDom()
assert.equal(console.error, originalConsoleError)
assert.deepEqual([fakeDocument.count('click'), fakeDocument.count('submit'), fakeWindow.count('error'), fakeWindow.count('unhandledrejection')], [0, 0, 0, 0])
disposeDom = domSession.installDemoUiDomObserver()
assert.deepEqual([fakeDocument.count('click'), fakeWindow.count('error')], [1, 1])
disposeDom()

for (const [source, fire] of [
  ['console error', () => console.error('dynamic observer failure')],
  ['window error', () => fakeWindow.dispatchEvent({ type: 'error', message: 'window failure', error: new Error('window failure') })],
  ['unhandled rejection', () => fakeWindow.dispatchEvent({ type: 'unhandledrejection', reason: new Error('rejection failure') })],
]) {
  const module = await sessionImport()
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await module.activateDemoUiSession(preflight, new MemoryStorage(), hostFetch), true)
  const realConsoleError = console.error
  if (source === 'console error') console.error = () => undefined
  const beforeInstall = console.error
  const disposeFailureObserver = module.installDemoUiDomObserver()
  fire()
  await module.exportStopDemoUiSession(hostFetch)
  assert.equal(module.isDemoUiSessionActive(), false, `${source} must STOP`)
  assert.equal(module.getDemoObserverLedger().at(-1).kind, 'STOP')
  assert.equal(requests.at(-1).body.ledger.events.at(-1).kind, 'STOP')
  disposeFailureObserver()
  assert.equal(console.error, beforeInstall, `${source} disposer restores console`)
  console.error = realConsoleError
}
globalThis.window = savedWindow
globalThis.document = savedDocument
globalThis.CustomEvent = savedCustomEvent
globalThis.fetch = savedFetch

const sessionSource = readFileSync(sessionPath, 'utf8')
const sources = {
  session: sessionSource, http: readFileSync(httpPath, 'utf8'), app: readFileSync(appPath, 'utf8'),
  api: readFileSync(apiPath, 'utf8'), inputs: readFileSync(inputsPath, 'utf8'), banner: readFileSync(bannerPath, 'utf8'),
}
assert.match(sources.api, /import type \{[\s\S]*DemoPreflight/)
assert.match(sources.session, /console\.error = originalConsoleError/)
assert.match(sources.session, /removeEventListener\('click'/)
assert.match(sources.session, /getDisplayMedia/)
assert.match(sources.session, /stream\.getTracks\(\)\.forEach\(\(track\) => track\.stop\(\)\)/)
assert.match(sources.app, /\/demo\/abc/)
assert.match(sources.app, /\/login/)
assert.ok(sources.http.includes('installDemoUiObserver(http)'))
assert.ok(sources.banner.includes('合成演示数据｜仅用于技术展示，非客户、生产或官方事实'))
assert.ok(sources.banner.includes('记录阶段'))
assert.match(sources.banner, /z-index:\s*1900/)
assert.match(sources.banner, /\.demo-boundary-banner\s*\{[\s\S]*?pointer-events:\s*none/)
assert.match(sources.banner, /\.demo-boundary-banner button\s*\{[\s\S]*?pointer-events:\s*auto/)
assert.ok(sources.inputs.includes('完成并导出本轮证据'))
assert.ok(!/http\.(post|put|patch|delete)/.test(sources.inputs))

const remediationFindings = []
async function proveFinding(name, proof) {
  try { await proof() } catch (error) { remediationFindings.push(`${name}: ${error instanceof Error ? error.message : String(error)}`) }
}

await proveFinding('ledger hydrates across real module reload without capability persistence', async () => {
  const first = await sessionImport()
  const localStorage = new MemoryStorage()
  assert.equal(first.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await first.activateDemoUiSession(preflight, localStorage, hostFetch), true)
  first.recordVisibleAction({ route: '/cases', role: 'button', label_or_testid: '查看案件' })
  const second = await sessionImport()
  assert.equal(await second.restoreDemoUiSession(localStorage, hostFetch), true)
  assert.equal(second.getDemoObserverLedger().some((event) => event.label_or_testid === '查看案件'), true)
  for (const [key, value] of localStorage.values) if (key !== second.DEMO_UI_SESSION_STORAGE_KEY) assert.ok(!value.includes(capability))
})

await proveFinding('cold /demo/abc exports exact STOP without observer install', async () => {
  const hot = await sessionImport()
  const localStorage = new MemoryStorage()
  assert.equal(hot.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await hot.activateDemoUiSession(preflight, localStorage, hostFetch), true)
  const cold = await sessionImport()
  const before = requests.length
  assert.equal(await cold.handleDemoUiRoute('/demo/abc', localStorage, hostFetch), true)
  assert.equal(new URL(requests.at(-1).url).pathname, '/stop')
  assert.equal(requests.at(-1).body.ledger.events.at(-1).kind, 'STOP')
  assert.equal(localStorage.getItem(cold.DEMO_UI_SESSION_STORAGE_KEY), null)
  assert.equal(requests.length, before + 1)
})

await proveFinding('terminal STOP prevents same-run reactivation', async () => {
  const module = await sessionImport()
  const localStorage = new MemoryStorage()
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
  module.stopDemoUiSession('TERMINAL_TEST', localStorage, hostFetch)
  await module.exportStopDemoUiSession(hostFetch)
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), false)
})

await proveFinding('loopback success bodies are exact', async () => {
  const module = await sessionImport()
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  const wrongValid = async () => ({ ok: true, status: 200, json: async () => ({ status: 'WRONG' }) })
  assert.equal(await module.activateDemoUiSession(preflight, new MemoryStorage(), wrongValid), false)
})

await proveFinding('partial finalization exports corrected STOP ledger', async () => {
  const module = await sessionImport()
  const localStorage = new MemoryStorage()
  const localStages = new MemoryStages()
  let value = 0
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
  module.setDemoStageEvidenceAdaptersForTest(localStages, async () => png(++value))
  for (let ordinal = 1; ordinal <= 11; ordinal += 1) await module.captureDemoStageScreenshot(ordinal)
  const calls = []
  const rejectPartial = async (url, init) => {
    const body = JSON.parse(init.body); calls.push({ url, body })
    if (body.filename === 'observer-stage-01.png') return { ok: false, status: 409, json: async () => ({ error: 'CONFLICT' }) }
    if (new URL(url).pathname === '/stop') return { ok: true, status: 200, json: async () => ({ status: 'STOPPED' }) }
    return { ok: true, status: 201, json: async () => ({ filename: body.filename }) }
  }
  await assert.rejects(module.finalizeDemoUiSessionEvidence(rejectPartial))
  assert.equal(new URL(calls.at(-1).url).pathname, '/stop')
  assert.equal(calls.at(-1).body.ledger.events.at(-1).kind, 'STOP')
  assert.equal(calls.at(-1).body.ledger.events.some((event) => event.kind === 'FINALIZED'), false)
})

await proveFinding('artifact echo and finalize body are exact', async () => {
  for (const fault of ['artifact-echo', 'finalize-body']) {
    const module = await sessionImport()
    const localStorage = new MemoryStorage()
    const localStages = new MemoryStages()
    let value = 0
    const calls = []
    assert.equal(module.configureDemoObserverBinding(pageUrl), true)
    assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
    module.setDemoStageEvidenceAdaptersForTest(localStages, async () => png(++value))
    for (let ordinal = 1; ordinal <= 11; ordinal += 1) await module.captureDemoStageScreenshot(ordinal)
    const strictFetch = async (url, init) => {
      const body = JSON.parse(init.body); const pathname = new URL(url).pathname
      calls.push({ url, body })
      if (pathname === '/stop') return hostResponse(200, { status: 'STOPPED' })
      if (pathname === '/finalize') return hostResponse(200, { status: fault === 'finalize-body' ? 'WRONG' : 'FINALIZED' })
      if (fault === 'artifact-echo' && body.filename === 'observer-ui-ledger.json') return hostResponse(201, { filename: 'wrong.json' })
      return hostResponse(201, { filename: body.filename })
    }
    await assert.rejects(module.finalizeDemoUiSessionEvidence(strictFetch), /OBSERVER_RESPONSE_INVALID/)
    assert.equal(new URL(calls.at(-1).url).pathname, '/stop')
    assert.equal(calls.at(-1).body.ledger.events.at(-1).kind, 'STOP')
    assert.equal(calls.at(-1).body.ledger.events.some((event) => event.kind === 'FINALIZED'), false)
  }
})

await proveFinding('display capture starts before first IndexedDB await', async () => {
  const module = await sessionImport()
  const order = []
  const localStorage = new MemoryStorage()
  const localStages = {
    async put() {}, async clear() {},
    async list() { order.push('idb'); return [] },
  }
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
  module.setDemoStageEvidenceAdaptersForTest(localStages, async () => { order.push('capture'); return png(1) })
  await module.captureDemoStageScreenshot(1)
  assert.deepEqual(order.slice(0, 2), ['capture', 'idb'])
})

await proveFinding('native media capture stops tracks on success and encoding failure', async () => {
  const savedNavigatorDescriptor = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  const savedDocumentValue = globalThis.document
  const savedWindowValue = globalThis.window
  try {
    for (const encode of [png(1), null]) {
      const module = await sessionImport()
      const localStorage = new MemoryStorage()
      const order = []
      let stops = 0
      assert.equal(module.configureDemoObserverBinding(pageUrl), true)
      assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
      const stream = { getTracks: () => [{ stop: () => { stops += 1 } }] }
      Object.defineProperty(globalThis, 'navigator', {
        configurable: true,
        value: { mediaDevices: { getDisplayMedia: () => { order.push('media'); return Promise.resolve(stream) } } },
      })
      globalThis.window = {
        location: { pathname: '/', origin: 'http://127.0.0.1:5173' },
        history: { state: null, replaceState() {} },
        dispatchEvent() {},
      }
      globalThis.document = {
        createElement(name) {
          if (name === 'video') return {
            videoWidth: 640, videoHeight: 360, srcObject: null,
            set onloadedmetadata(handler) { queueMicrotask(handler) },
            set onerror(_handler) {},
            async play() {},
          }
          return {
            width: 0, height: 0,
            getContext: () => ({ drawImage() {} }),
            toBlob: (resolve) => resolve(encode),
          }
        },
      }
      const localStages = {
        async put() {}, async clear() {},
        async list() { order.push('idb'); return [] },
      }
      module.setDemoStageEvidenceAdaptersForTest(localStages, null)
      if (encode) await module.captureDemoStageScreenshot(1)
      else await assert.rejects(module.captureDemoStageScreenshot(1), /阶段截图编码失败/)
      assert.deepEqual(order.slice(0, 2), ['media', 'idb'])
      assert.equal(stops, 1)
    }
  } finally {
    if (savedNavigatorDescriptor) Object.defineProperty(globalThis, 'navigator', savedNavigatorDescriptor)
    else delete globalThis.navigator
    globalThis.document = savedDocumentValue
    globalThis.window = savedWindowValue
  }
})

await proveFinding('activation binding is scrubbed from URL/history', async () => {
  const savedWindowValue = globalThis.window
  const historyCalls = []
  globalThis.window = {
    location: { href: pageUrl, pathname: '/', origin: 'http://127.0.0.1:5173' },
    history: { state: null, replaceState: (...args) => historyCalls.push(args) },
    dispatchEvent() {},
  }
  try {
    const module = await sessionImport()
    const localStorage = new MemoryStorage()
    const localStages = new MemoryStages()
    assert.equal(module.configureDemoObserverBinding(pageUrl), true)
    assert.equal(historyCalls.length, 1)
    assert.ok(!historyCalls[0][2].includes('fpmsObserverBinding'))
    assert.ok(!historyCalls[0][2].includes(capability))
    assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
    module.setDemoStageEvidenceAdaptersForTest(localStages, async () => png(1))
    await module.captureDemoStageScreenshot(1)
    assert.ok(localStorage.getItem(module.DEMO_UI_SESSION_STORAGE_KEY).includes(capability))
    assert.ok(!localStorage.getItem(`${module.DEMO_UI_LEDGER_STORAGE_KEY}:${preflight.run_id}`).includes(capability))
    assert.ok(!JSON.stringify(localStages.rows).includes(capability))
    assert.ok(!JSON.stringify(module.getDemoObserverLedger()).includes(capability))
    module.recordVisibleAction({ route: '/cases', role: 'button', label_or_testid: capability })
    await module.exportStopDemoUiSession(hostFetch)
    assert.equal(module.getDemoObserverLedger().at(-1).kind, 'STOP')
    assert.ok(!JSON.stringify(module.getDemoObserverLedger()).includes(capability))
  } finally {
    globalThis.window = savedWindowValue
  }
})

assert.deepEqual(remediationFindings, [], `Ordinal 03R remediation gaps:\n- ${remediationFindings.join('\n- ')}`)

const terminalHardeningFindings = []
async function proveTerminalFinding(name, proof) {
  try { await proof() } catch (error) { terminalHardeningFindings.push(`${name}: ${error instanceof Error ? error.message : String(error)}`) }
}
await proveTerminalFinding('console sink receives only fixed capability redaction', async () => {
  const savedWindowValue = globalThis.window
  const savedDocumentValue = globalThis.document
  const savedConsoleError = console.error
  const sinkArguments = []
  const fakeConsoleWindow = new FakeTarget()
  fakeConsoleWindow.location = { href: pageUrl, pathname: '/', origin: 'http://127.0.0.1:5173' }
  fakeConsoleWindow.history = { state: null, replaceState() {} }
  globalThis.window = fakeConsoleWindow
  globalThis.document = new FakeTarget()
  console.error = (...args) => sinkArguments.push(args)
  try {
    const module = await sessionImport()
    assert.equal(module.configureDemoObserverBinding(pageUrl), true)
    assert.equal(await module.activateDemoUiSession(preflight, new MemoryStorage(), hostFetch), true)
    const disposeConsoleObserver = module.installDemoUiDomObserver()
    console.error('safe', { nested: [capability] }, `prefix-${capability}-suffix`)
    await module.exportStopDemoUiSession(hostFetch)
    disposeConsoleObserver()
    assert.deepEqual(sinkArguments, [[
      'safe',
      '[FPMS_DEMO_REDACTED]',
      '[FPMS_DEMO_REDACTED]',
    ]])
    assert.equal(module.getDemoObserverLedger().at(-1).kind, 'STOP')
    assert.ok(!JSON.stringify(module.getDemoObserverLedger()).includes(capability))
  } finally {
    console.error = savedConsoleError
    globalThis.window = savedWindowValue
    globalThis.document = savedDocumentValue
  }
})

await proveTerminalFinding('deferred old STOP cannot clear genuine new run', async () => {
  const module = await sessionImport()
  const localStorage = new MemoryStorage()
  assert.equal(module.configureDemoObserverBinding(pageUrl), true)
  assert.equal(await module.activateDemoUiSession(preflight, localStorage, hostFetch), true)
  module.recordVisibleAction({ route: '/cases', role: 'button', label_or_testid: '停止旧轮次' })
  let releaseStop
  let signalStopStarted
  const stopStarted = new Promise((resolve) => { signalStopStarted = resolve })
  const oldRequests = []
  const deferredStopFetch = async (url, init) => {
    oldRequests.push({ url, body: JSON.parse(init.body) })
    signalStopStarted()
    return new Promise((resolve) => { releaseStop = () => resolve(hostResponse(200, { status: 'STOPPED' })) })
  }
  module.stopDemoUiSession('OLD_RUN_STOP', localStorage, deferredStopFetch)
  const oldStopPromise = module.exportStopDemoUiSession(deferredStopFetch)
  await stopStarted

  const newCapability = 'new_run_capability_0123456789_ABCDEFGH'
  const newBinding = `http://127.0.0.1:43124/observer-artifact?capability=${newCapability}&actor=HUMAN`
  const newPageUrl = `http://127.0.0.1:5173/?fpmsObserverBinding=${encodeURIComponent(newBinding)}`
  const newPreflight = structuredClone(preflight)
  newPreflight.run_id = 'ui-human-contract-new'
  const newFetch = async (url, init) => {
    assert.equal(new URL(url).pathname, '/revalidate')
    assert.equal(JSON.parse(init.body).run_id, newPreflight.run_id)
    return hostResponse(200, { status: 'VALID' })
  }
  assert.equal(module.configureDemoObserverBinding(newPageUrl), true)
  assert.equal(await module.activateDemoUiSession(newPreflight, localStorage, newFetch), true)
  const newStoredValue = localStorage.getItem(module.DEMO_UI_SESSION_STORAGE_KEY)
  releaseStop()
  await oldStopPromise

  assert.equal(new URL(oldRequests[0].url).searchParams.get('capability'), capability)
  assert.equal(oldRequests[0].body.run_id, preflight.run_id)
  assert.equal(oldRequests[0].body.ledger.events.at(-1).kind, 'STOP')
  assert.equal(localStorage.getItem(module.DEMO_UI_SESSION_STORAGE_KEY), newStoredValue)
  assert.equal(module.getDemoUiSession().run_id, newPreflight.run_id)
  assert.equal(module.isDemoUiSessionActive(), true)
})

assert.deepEqual(terminalHardeningFindings, [], `Ordinal 02U-03U frontend gaps:\n- ${terminalHardeningFindings.join('\n- ')}`)

console.log('demo V6 UI session contract: PASS')
