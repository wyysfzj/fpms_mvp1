import type { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { DEMO_UI_PARITY_SCHEMA_ID, parseDemoUiSessionPreflight } from './demo.contract'

export const DEMO_UI_SESSION_STORAGE_KEY = 'fpms_demo_v6_ui_session_v1'
export const DEMO_UI_LEDGER_STORAGE_KEY = 'fpms_demo_v6_ui_ledger_v1'
export const DEMO_UI_TERMINAL_STORAGE_KEY = 'fpms_demo_v6_ui_terminal_v1'
export const DEMO_UI_SESSION_CHANGE_EVENT = 'fpms:demo-ui-session-change'
export const DEMO_UI_SCREENSHOT_COUNT = 11

export interface DemoHostTuple {
  contract_version: typeof DEMO_UI_PARITY_SCHEMA_ID
  run_id: string
  candidate_commit: string
  candidate_tree: string
  authority_sha256: string
  actor: 'HUMAN' | 'CODEX'
}

interface PersistedSession {
  binding: string
  tuple: DemoHostTuple
}

interface VisibleAction {
  kind: 'action'
  action_id: string
  route: string
  role: string
  label_or_testid: string
}

interface MutationObservation {
  kind: 'mutation'
  action_id: string | null
  route: string
  role: string
  label_or_testid: string
  method: string
  path: string
  payload_sha256: string
  status: number | null
}

interface FailureObservation {
  kind: 'console_failure' | 'network_failure'
  action_id: string | null
  digest: string
}

type DemoObserverEvent =
  | VisibleAction
  | MutationObservation
  | FailureObservation
  | { kind: 'screenshot'; stage: number; sha256: string; width: number; height: number }
  | { kind: 'STOP'; reason: string }
  | { kind: 'FINALIZED' }

interface StageEvidenceStore {
  put(runId: string, stage: number, png: Blob): Promise<void>
  list(runId: string): Promise<Array<{ stage: number; png: Blob }>>
  clear(runId: string): Promise<void>
}

const mutationMethods = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])
const excludedRoutes = new Set(['/login', '/demo/abc'])
const sensitiveKeys = /authorization|token|password|passwd|secret|credential|cookie/i
const requestObservations = new WeakMap<object, MutationObservation>()
const pendingDigests = new Set<Promise<void>>()
const observerLedger: DemoObserverEvent[] = []

let persistedSession: PersistedSession | null = null
let active = false
let activeStorage: Storage | null = null
let activeFetcher: typeof fetch | null = null
let lastVisibleAction: VisibleAction | null = null
let stopExportPromise: Promise<void> | null = null
let axiosDisposer: (() => void) | null = null
let domDisposer: (() => void) | null = null

function storageOrDefault(storage?: Storage): Storage | null {
  if (storage) return storage
  return typeof sessionStorage === 'undefined' ? null : sessionStorage
}

function currentRoute(): string {
  return typeof window === 'undefined' ? '/' : window.location.pathname
}

function routeIsObserved(route = currentRoute()): boolean {
  return !excludedRoutes.has(route)
}

function emitSessionChange(): void {
  if (typeof window !== 'undefined' && typeof CustomEvent !== 'undefined') {
    window.dispatchEvent(new CustomEvent(DEMO_UI_SESSION_CHANGE_EVENT))
  }
}

function exactKeys(value: Record<string, unknown>, keys: string[]): boolean {
  return Object.keys(value).sort().join('|') === [...keys].sort().join('|')
}

function isObserverEvent(value: unknown): value is DemoObserverEvent {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false
  const row = value as Record<string, unknown>
  if (row.kind === 'action') return exactKeys(row, ['kind', 'action_id', 'route', 'role', 'label_or_testid']) &&
    [row.action_id, row.route, row.role, row.label_or_testid].every((entry) => typeof entry === 'string')
  if (row.kind === 'mutation') return exactKeys(row, ['kind', 'action_id', 'route', 'role', 'label_or_testid', 'method', 'path', 'payload_sha256', 'status']) &&
    (row.action_id === null || typeof row.action_id === 'string') &&
    [row.route, row.role, row.label_or_testid, row.method, row.path].every((entry) => typeof entry === 'string') &&
    typeof row.payload_sha256 === 'string' && /^[0-9a-f]{64}$/.test(row.payload_sha256) &&
    (row.status === null || (typeof row.status === 'number' && Number.isInteger(row.status)))
  if (row.kind === 'console_failure' || row.kind === 'network_failure') return exactKeys(row, ['kind', 'action_id', 'digest']) &&
    (row.action_id === null || typeof row.action_id === 'string') && typeof row.digest === 'string' && /^[0-9a-f]{64}$/.test(row.digest)
  if (row.kind === 'screenshot') return exactKeys(row, ['kind', 'stage', 'sha256', 'width', 'height']) &&
    typeof row.stage === 'number' && Number.isInteger(row.stage) && row.stage >= 1 && row.stage <= DEMO_UI_SCREENSHOT_COUNT &&
    typeof row.sha256 === 'string' && /^[0-9a-f]{64}$/.test(row.sha256) &&
    typeof row.width === 'number' && typeof row.height === 'number'
  if (row.kind === 'STOP') return exactKeys(row, ['kind', 'reason']) && typeof row.reason === 'string' && row.reason.trim().length > 0
  if (row.kind === 'FINALIZED') return exactKeys(row, ['kind'])
  return false
}

function parseBinding(raw: string): { binding: string; actor: 'HUMAN' | 'CODEX' } | null {
  try {
    const binding = new URL(raw)
    const actor = binding.searchParams.get('actor')
    const capability = binding.searchParams.get('capability')
    if (
      binding.protocol !== 'http:' || binding.hostname !== '127.0.0.1' ||
      binding.pathname !== '/observer-artifact' || binding.username !== '' ||
      binding.password !== '' || binding.hash !== '' ||
      !capability || !/^[A-Za-z0-9_-]{32,}$/.test(capability) ||
      !actor || !['HUMAN', 'CODEX'].includes(actor) ||
      [...binding.searchParams.keys()].sort().join('|') !== 'actor|capability'
    ) return null
    return { binding: binding.href, actor: actor as 'HUMAN' | 'CODEX' }
  } catch {
    return null
  }
}

function isTuple(value: unknown): value is DemoHostTuple {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false
  const row = value as Record<string, unknown>
  return Object.keys(row).sort().join('|') ===
      'actor|authority_sha256|candidate_commit|candidate_tree|contract_version|run_id' &&
    row.contract_version === DEMO_UI_PARITY_SCHEMA_ID &&
    typeof row.run_id === 'string' && row.run_id.length > 0 &&
    typeof row.candidate_commit === 'string' && /^[0-9a-f]{40}$/.test(row.candidate_commit) &&
    typeof row.candidate_tree === 'string' && /^[0-9a-f]{40}$/.test(row.candidate_tree) &&
    typeof row.authority_sha256 === 'string' && /^[0-9a-f]{64}$/.test(row.authority_sha256) &&
    (row.actor === 'HUMAN' || row.actor === 'CODEX')
}

function parseStored(raw: string | null): PersistedSession | null {
  if (!raw) return null
  try {
    const value: unknown = JSON.parse(raw)
    if (typeof value !== 'object' || value === null || Array.isArray(value)) return null
    const row = value as Record<string, unknown>
    if (Object.keys(row).sort().join('|') !== 'binding|tuple' || typeof row.binding !== 'string') return null
    const binding = parseBinding(row.binding)
    if (!binding || !isTuple(row.tuple) || binding.actor !== row.tuple.actor) return null
    return { binding: binding.binding, tuple: row.tuple }
  } catch {
    return null
  }
}

function terminalRunId(storage: Storage): string | null | undefined {
  const raw = storage.getItem(DEMO_UI_TERMINAL_STORAGE_KEY)
  if (raw === null) return null
  try {
    const value: unknown = JSON.parse(raw)
    if (typeof value !== 'object' || value === null || Array.isArray(value)) return undefined
    const row = value as Record<string, unknown>
    return exactKeys(row, ['run_id', 'status']) && row.status === 'STOPPED' && typeof row.run_id === 'string'
      ? row.run_id : undefined
  } catch {
    return undefined
  }
}

function ledgerStorageKey(runId: string): string {
  return `${DEMO_UI_LEDGER_STORAGE_KEY}:${runId}`
}

function persistLedger(): void {
  if (!activeStorage || !persistedSession || !isTuple(persistedSession.tuple)) return
  activeStorage.setItem(ledgerStorageKey(persistedSession.tuple.run_id), JSON.stringify({
    schema_id: DEMO_UI_PARITY_SCHEMA_ID,
    run_id: persistedSession.tuple.run_id,
    events: observerLedger,
  }))
}

function hydrateLedger(storage: Storage, session: PersistedSession): boolean {
  try {
    const raw = storage.getItem(ledgerStorageKey(session.tuple.run_id))
    if (!raw) return false
    const capability = new URL(session.binding).searchParams.get('capability')
    if (capability && raw.includes(capability)) return false
    const value: unknown = JSON.parse(raw)
    if (typeof value !== 'object' || value === null || Array.isArray(value)) return false
    const row = value as Record<string, unknown>
    if (!exactKeys(row, ['schema_id', 'run_id', 'events']) ||
      row.schema_id !== DEMO_UI_PARITY_SCHEMA_ID || row.run_id !== session.tuple.run_id ||
      !Array.isArray(row.events) || !row.events.every(isObserverEvent)) return false
    observerLedger.splice(0, observerLedger.length, ...row.events)
    return true
  } catch {
    return false
  }
}

function appendEvent(event: DemoObserverEvent): void {
  const capability = persistedSession
    ? new URL(persistedSession.binding).searchParams.get('capability')
    : null
  if (capability && JSON.stringify(event).includes(capability)) {
    active = false
    lastVisibleAction = null
    observerLedger.push({ kind: 'STOP', reason: 'CAPABILITY_LEAK_BLOCKED' })
    if (activeStorage && persistedSession && isTuple(persistedSession.tuple)) {
      activeStorage.setItem(DEMO_UI_TERMINAL_STORAGE_KEY, JSON.stringify({
        run_id: persistedSession.tuple.run_id,
        status: 'STOPPED',
      }))
    }
    persistLedger()
    emitSessionChange()
    if (activeFetcher) void exportStopDemoUiSession(activeFetcher)
    return
  }
  observerLedger.push(event)
  persistLedger()
}

async function expectHostResponse(
  response: Response,
  status: number,
  body: Record<string, string>,
): Promise<void> {
  if (response.status !== status) throw new Error(`OBSERVER_STATUS_${response.status}`)
  let value: unknown
  try { value = await response.json() } catch { throw new Error('OBSERVER_RESPONSE_INVALID') }
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new Error('OBSERVER_RESPONSE_INVALID')
  const row = value as Record<string, unknown>
  if (!exactKeys(row, Object.keys(body)) || Object.entries(body).some(([key, expected]) => row[key] !== expected)) {
    throw new Error('OBSERVER_RESPONSE_INVALID')
  }
}

function operationUrl(operation: '/revalidate' | '/observer-artifact' | '/stop' | '/finalize'): string {
  if (!persistedSession) throw new Error('演示观察宿主未绑定')
  const url = new URL(persistedSession.binding)
  url.pathname = operation
  url.searchParams.delete('actor')
  return url.href
}

async function postHost(
  operation: '/revalidate' | '/observer-artifact' | '/stop' | '/finalize',
  payload: object,
  fetcher: typeof fetch,
): Promise<Response> {
  return fetcher(operationUrl(operation), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function configureDemoObserverBinding(pageHref: string): boolean {
  persistedSession = null
  try {
    const page = new URL(pageHref)
    if (page.protocol !== 'http:' || page.hostname !== '127.0.0.1' || page.port !== '5173') return false
    const raw = page.searchParams.get('fpmsObserverBinding')
    if (!raw) return false
    const parsed = parseBinding(raw)
    if (!parsed) return false
    persistedSession = { binding: parsed.binding, tuple: null as unknown as DemoHostTuple }
    page.searchParams.delete('fpmsObserverBinding')
    if (typeof window !== 'undefined') {
      window.history.replaceState(window.history.state, '', `${page.pathname}${page.search}${page.hash}`)
    }
    return true
  } catch {
    return false
  }
}

function tupleFromPreflight(value: unknown): DemoHostTuple {
  const preflight = parseDemoUiSessionPreflight(value)
  const binding = persistedSession && parseBinding(persistedSession.binding)
  if (!binding) throw new Error('演示观察宿主未绑定')
  return {
    contract_version: preflight.contract_version,
    run_id: preflight.run_id,
    candidate_commit: preflight.candidate_commit,
    candidate_tree: preflight.candidate_tree,
    authority_sha256: preflight.authority_sha256,
    actor: binding.actor,
  }
}

function candidateTuple(value: unknown): DemoHostTuple {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new Error('演示预检身份缺失')
  const row = value as Record<string, unknown>
  const binding = persistedSession && parseBinding(persistedSession.binding)
  const tuple = {
    contract_version: row.contract_version,
    run_id: row.run_id,
    candidate_commit: row.candidate_commit,
    candidate_tree: row.candidate_tree,
    authority_sha256: row.authority_sha256,
    actor: binding?.actor,
  }
  if (!isTuple(tuple)) throw new Error('演示预检身份无效')
  return tuple
}

export async function activateDemoUiSession(
  value: unknown,
  storage?: Storage,
  fetcher: typeof fetch = fetch,
): Promise<boolean> {
  const target = storageOrDefault(storage)
  if (!target || !persistedSession || !routeIsObserved()) {
    stopDemoUiSession(!target ? 'SESSION_STORAGE_MISSING' : 'OBSERVER_BINDING_INVALID', storage)
    return false
  }
  try {
    const binding = persistedSession.binding
    const candidate = candidateTuple(value)
    persistedSession = { binding, tuple: candidate }
    activeStorage = target
    activeFetcher = fetcher
    const terminal = terminalRunId(target)
    if (terminal === undefined) throw new Error('SESSION_TERMINAL_INVALID')
    if (terminal === candidate.run_id) {
      active = false
      emitSessionChange()
      return false
    }
    const tuple = tupleFromPreflight(value)
    const response = await postHost('/revalidate', tuple, fetcher)
    await expectHostResponse(response, 200, { status: 'VALID' })
    target.setItem(DEMO_UI_SESSION_STORAGE_KEY, JSON.stringify(persistedSession))
    observerLedger.splice(0, observerLedger.length)
    persistLedger()
    target.removeItem(DEMO_UI_TERMINAL_STORAGE_KEY)
    active = true
    stopExportPromise = null
    emitSessionChange()
    return true
  } catch {
    stopDemoUiSession('PREFLIGHT_OR_REVALIDATION_INVALID', target, fetcher)
    return false
  }
}

export async function restoreDemoUiSession(
  storage?: Storage,
  fetcher: typeof fetch = fetch,
): Promise<boolean> {
  const target = storageOrDefault(storage)
  const stored = target && parseStored(target.getItem(DEMO_UI_SESSION_STORAGE_KEY))
  if (!target || !stored || !routeIsObserved()) {
    stopDemoUiSession(!stored ? 'SESSION_TUPLE_MISSING' : 'ROUTE_EXCLUDED', storage)
    return false
  }
  persistedSession = stored
  activeStorage = target
  activeFetcher = fetcher
  try {
    const terminal = terminalRunId(target)
    if (terminal === undefined) throw new Error('SESSION_TERMINAL_INVALID')
    if (terminal === stored.tuple.run_id) {
      active = false
      emitSessionChange()
      return false
    }
    if (!hydrateLedger(target, stored)) throw new Error('SESSION_LEDGER_INVALID')
    const response = await postHost('/revalidate', stored.tuple, fetcher)
    await expectHostResponse(response, 200, { status: 'VALID' })
    active = true
    stopExportPromise = null
    emitSessionChange()
    return true
  } catch {
    stopDemoUiSession('SESSION_REVALIDATION_FAILED', target, fetcher)
    return false
  }
}

export function hasStoredDemoUiSession(storage?: Storage): boolean {
  return storageOrDefault(storage)?.getItem(DEMO_UI_SESSION_STORAGE_KEY) !== null
}

export function isDemoUiSessionActive(): boolean { return active }
export function getDemoUiSession(): DemoHostTuple | null {
  return persistedSession?.tuple && isTuple(persistedSession.tuple) ? { ...persistedSession.tuple } : null
}
export function getDemoObserverLedger(): DemoObserverEvent[] {
  return observerLedger.map((event) => ({ ...event }))
}

function ledgerContent(): Record<string, unknown> {
  if (!persistedSession || !isTuple(persistedSession.tuple)) throw new Error('演示会话元组缺失')
  return { schema_id: DEMO_UI_PARITY_SCHEMA_ID, session: persistedSession.tuple, events: observerLedger }
}

async function uploadLedger(fetcher: typeof fetch): Promise<void> {
  if (!persistedSession || !isTuple(persistedSession.tuple)) return
  await waitForObserverDigests()
  const response = await postHost('/observer-artifact', {
    ...persistedSession.tuple,
    filename: 'observer-ui-ledger.json', encoding: 'json', content: ledgerContent(),
  }, fetcher)
  await expectHostResponse(response, 201, { filename: 'observer-ui-ledger.json' })
}

export async function exportStopDemoUiSession(fetcher: typeof fetch = fetch): Promise<void> {
  if (stopExportPromise) return stopExportPromise
  if (!persistedSession || !isTuple(persistedSession.tuple)) return
  const tuple = { ...persistedSession.tuple }
  const binding = persistedSession.binding
  const storage = activeStorage
  const storedValue = storage?.getItem(DEMO_UI_SESSION_STORAGE_KEY) ?? null
  const events = [...observerLedger]
  const stopUrl = new URL(binding)
  stopUrl.pathname = '/stop'
  stopUrl.searchParams.delete('actor')
  stopExportPromise = (async () => {
    try {
      await waitForObserverDigests()
      const ledger = JSON.parse(JSON.stringify({
        schema_id: DEMO_UI_PARITY_SCHEMA_ID,
        session: tuple,
        events,
      })) as Record<string, unknown>
      const response = await fetcher(stopUrl.href, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...tuple, ledger }),
      })
      await expectHostResponse(response, 200, { status: 'STOPPED' })
      if (storedValue !== null && storage?.getItem(DEMO_UI_SESSION_STORAGE_KEY) === storedValue) {
        storage.removeItem(DEMO_UI_SESSION_STORAGE_KEY)
      }
    } catch {
      // Terminal STOP is single-attempt. Preserve the bound run when the host does not confirm it.
    }
  })()
  return stopExportPromise
}

export function stopDemoUiSession(reason: string, storage?: Storage, fetcher?: typeof fetch): void {
  active = false
  lastVisibleAction = null
  activeStorage = storageOrDefault(storage) ?? activeStorage
  if (activeStorage && persistedSession && isTuple(persistedSession.tuple)) {
    activeStorage.setItem(DEMO_UI_TERMINAL_STORAGE_KEY, JSON.stringify({
      run_id: persistedSession.tuple.run_id,
      status: 'STOPPED',
    }))
  }
  if (observerLedger.at(-1)?.kind !== 'STOP') appendEvent({ kind: 'STOP', reason })
  emitSessionChange()
  if (fetcher ?? activeFetcher) void exportStopDemoUiSession((fetcher ?? activeFetcher) as typeof fetch)
  else if (typeof fetch !== 'undefined') void exportStopDemoUiSession(fetch)
}

export async function handleDemoUiRoute(
  route: string,
  storage?: Storage,
  fetcher: typeof fetch = fetch,
): Promise<boolean> {
  if (route !== '/demo/abc') return false
  const target = storageOrDefault(storage)
  if (!active) {
    const stored = target && parseStored(target.getItem(DEMO_UI_SESSION_STORAGE_KEY))
    if (!target || !stored) return false
    persistedSession = stored
    activeStorage = target
    activeFetcher = fetcher
    if (!hydrateLedger(target, stored)) return false
    const terminal = terminalRunId(target)
    if (terminal === stored.tuple.run_id) return false
    if (terminal === undefined) {
      stopDemoUiSession('SESSION_TERMINAL_INVALID', target, fetcher)
      await exportStopDemoUiSession(fetcher)
      return true
    }
  }
  stopDemoUiSession(`ROUTE_EXCLUDED:${route}`, target ?? undefined, fetcher)
  await exportStopDemoUiSession(fetcher)
  return true
}

function actionId(): string {
  return typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID() : `action-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function recordVisibleAction(input: Omit<VisibleAction, 'kind' | 'action_id'>): string {
  const action: VisibleAction = { kind: 'action', action_id: actionId(), ...input }
  if (active && routeIsObserved(input.route)) {
    lastVisibleAction = action
    appendEvent(action)
  }
  return action.action_id
}

function normalizedDigestValue(value: unknown, key = ''): unknown {
  if (sensitiveKeys.test(key)) return '[REDACTED]'
  if (value === null || typeof value === 'boolean' || typeof value === 'number') return value
  if (typeof value === 'string') {
    try { return normalizedDigestValue(JSON.parse(value)) } catch { return value.normalize('NFKC').trim() }
  }
  if (value instanceof URLSearchParams) return normalizedDigestValue(Object.fromEntries(value.entries()))
  if (typeof FormData !== 'undefined' && value instanceof FormData) {
    return normalizedDigestValue(Object.fromEntries([...value.entries()].map(([key, entry]) => [
      key, typeof entry === 'string' ? normalizedDigestValue(entry, key) : { size: entry.size, type: entry.type },
    ])))
  }
  if (Array.isArray(value)) return value.map((entry) => normalizedDigestValue(entry))
  if (typeof value === 'object' && value !== null) return Object.fromEntries(
    Object.entries(value).sort(([left], [right]) => left.localeCompare(right))
      .map(([entryKey, entry]) => [entryKey, normalizedDigestValue(entry, entryKey)]),
  )
  return String(value)
}

export async function normalizedPayloadSha256(payload: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(JSON.stringify(normalizedDigestValue(payload)))
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('')
}

function trackPending(task: Promise<void>): void {
  pendingDigests.add(task)
  void task.finally(() => pendingDigests.delete(task))
}

function mutationPath(config: AxiosRequestConfig): string {
  try {
    return new URL(config.url ?? '/', config.baseURL ?? (typeof window === 'undefined' ? 'http://127.0.0.1' : window.location.origin)).pathname
  } catch { return '/' }
}

export function observeMutationRequest<T extends AxiosRequestConfig>(config: T): T {
  const method = (config.method ?? 'GET').toUpperCase()
  if (!active || !routeIsObserved() || !mutationMethods.has(method)) return config
  if (method === 'POST' && config.url === '/documents/impact-preview') return config
  const action = lastVisibleAction
  const observation: MutationObservation = {
    kind: 'mutation', action_id: action?.action_id ?? null, route: action?.route ?? '',
    role: action?.role ?? '', label_or_testid: action?.label_or_testid ?? '', method,
    path: mutationPath(config), payload_sha256: '0'.repeat(64), status: null,
  }
  requestObservations.set(config, observation)
  appendEvent(observation)
  trackPending(normalizedPayloadSha256(config.data).then((digest) => {
    observation.payload_sha256 = digest
    persistLedger()
  }))
  lastVisibleAction = null
  if (!action) stopDemoUiSession('UNMATCHED_MUTATION')
  return config
}

export function observeMutationResponse(config: AxiosRequestConfig, status: number): void {
  const observation = requestObservations.get(config)
  if (observation) {
    observation.status = status
    persistLedger()
  }
}

function trackFailure(kind: FailureObservation['kind'], value: unknown, actionIdValue: string | null): void {
  const failure: FailureObservation = { kind, action_id: actionIdValue, digest: '0'.repeat(64) }
  appendEvent(failure)
  trackPending(normalizedPayloadSha256(value).then((digest) => {
    failure.digest = digest
    persistLedger()
  }))
}

export function observeMutationFailure(config: AxiosRequestConfig, error: AxiosError): void {
  const observation = requestObservations.get(config)
  const status = error.response?.status ?? 0
  if (observation) observation.status = status
  trackFailure('network_failure', { name: error.name, code: error.code, status }, observation?.action_id ?? null)
  if (status === 0) stopDemoUiSession('NETWORK_FAILURE')
}

export async function waitForObserverDigests(): Promise<void> {
  await Promise.allSettled([...pendingDigests])
}

export function installDemoUiObserver(instance: AxiosInstance): () => void {
  axiosDisposer?.()
  const requestId = instance.interceptors.request.use((config) => observeMutationRequest(config))
  const responseId = instance.interceptors.response.use(
    (response: AxiosResponse) => { observeMutationResponse(response.config, response.status); return response },
    (error: AxiosError) => { if (error.config) observeMutationFailure(error.config, error); return Promise.reject(error) },
  )
  let disposed = false
  axiosDisposer = () => {
    if (disposed) return
    disposed = true
    instance.interceptors.request.eject(requestId)
    instance.interceptors.response.eject(responseId)
    if (axiosDisposer && disposed) axiosDisposer = null
  }
  return axiosDisposer
}

function visibleControl(target: EventTarget | null): HTMLElement | null {
  if (!(target instanceof Element)) return null
  const control = target.closest<HTMLElement>('[data-testid],button,form,[role],input[type="submit"],input[type="button"]')
  if (!control || control.hidden || control.getAttribute('aria-hidden') === 'true') return null
  if ('disabled' in control && control.disabled) return null
  const style = window.getComputedStyle(control)
  return style.display === 'none' || style.visibility === 'hidden' ? null : control
}

export function installDemoUiDomObserver(): () => void {
  domDisposer?.()
  if (typeof document === 'undefined' || typeof window === 'undefined') return () => undefined
  const capture = (event: Event) => {
    if (!active || !routeIsObserved()) return
    const control = visibleControl(event.target)
    if (!control) return
    recordVisibleAction({
      route: currentRoute(),
      role: control.getAttribute('role') || (control.tagName === 'FORM' ? 'form' : 'button'),
      label_or_testid: (control.dataset.testid || control.getAttribute('aria-label') || control.textContent?.replace(/\s+/g, ' ').trim() || control.getAttribute('name') || 'unlabelled-control').slice(0, 160),
    })
  }
  const onError = (event: ErrorEvent) => { if (active && routeIsObserved()) { trackFailure('console_failure', event.error ?? event.message, lastVisibleAction?.action_id ?? null); stopDemoUiSession('CONSOLE_FAILURE') } }
  const onRejection = (event: PromiseRejectionEvent) => { if (active && routeIsObserved()) { trackFailure('console_failure', event.reason, lastVisibleAction?.action_id ?? null); stopDemoUiSession('CONSOLE_FAILURE') } }
  const originalConsoleError = console.error
  console.error = (...values: unknown[]) => {
    const capability = active && persistedSession
      ? new URL(persistedSession.binding).searchParams.get('capability')
      : null
    const sinkValues = capability
      ? values.map((value) => {
        try {
          const searchable = typeof value === 'string'
            ? value
            : value instanceof Error
              ? `${value.message}\n${value.stack ?? ''}`
              : JSON.stringify(value)
          return searchable?.includes(capability) ? '[FPMS_DEMO_REDACTED]' : value
        } catch {
          return '[FPMS_DEMO_REDACTED]'
        }
      })
      : values
    originalConsoleError(...sinkValues)
    if (active && routeIsObserved()) { trackFailure('console_failure', sinkValues, lastVisibleAction?.action_id ?? null); stopDemoUiSession('CONSOLE_FAILURE') }
  }
  document.addEventListener('click', capture, true)
  document.addEventListener('submit', capture, true)
  window.addEventListener('error', onError)
  window.addEventListener('unhandledrejection', onRejection)
  let disposed = false
  domDisposer = () => {
    if (disposed) return
    disposed = true
    document.removeEventListener('click', capture, true)
    document.removeEventListener('submit', capture, true)
    window.removeEventListener('error', onError)
    window.removeEventListener('unhandledrejection', onRejection)
    console.error = originalConsoleError
    if (domDisposer && disposed) domDisposer = null
  }
  return domDisposer
}

export function prepareDemoUiSessionObserver(pageHref?: string, storage?: Storage): boolean {
  const href = pageHref ?? (typeof window === 'undefined' ? '' : window.location.href)
  if (!href) return false
  try {
    const page = new URL(href)
    if (!page.searchParams.has('fpmsObserverBinding')) return hasStoredDemoUiSession(storage)
    if (configureDemoObserverBinding(href)) return true
    const target = storageOrDefault(storage)
    const stored = target && parseStored(target.getItem(DEMO_UI_SESSION_STORAGE_KEY))
    if (stored) {
      persistedSession = stored
      activeStorage = target
    }
    stopDemoUiSession('OBSERVER_BINDING_INVALID', storage)
    return false
  } catch {
    stopDemoUiSession('OBSERVER_BINDING_INVALID', storage)
    return false
  }
}

const stageEvidenceStore: StageEvidenceStore = {
  async put(runId, stage, png) {
    const db = await openStageDb()
    await idbRequest(db.transaction('stages', 'readwrite').objectStore('stages').put({ id: `${runId}:${stage}`, runId, stage, png }))
    db.close()
  },
  async list(runId) {
    const db = await openStageDb()
    const rows = await idbRequest<Array<{ runId: string; stage: number; png: Blob }>>(db.transaction('stages').objectStore('stages').getAll())
    db.close()
    return rows.filter((row) => row.runId === runId).map(({ stage, png }) => ({ stage, png })).sort((a, b) => a.stage - b.stage)
  },
  async clear(runId) {
    const db = await openStageDb()
    const rows = await idbRequest<Array<{ id: string; runId: string }>>(db.transaction('stages').objectStore('stages').getAll())
    const store = db.transaction('stages', 'readwrite').objectStore('stages')
    const deletions = rows.filter((row) => row.runId === runId).map((row) => idbRequest(store.delete(row.id)))
    await Promise.all(deletions)
    db.close()
  },
}

let evidenceStore: StageEvidenceStore = stageEvidenceStore
let captureAdapter: (() => Promise<Blob>) | null = null
export function setDemoStageEvidenceAdaptersForTest(store: StageEvidenceStore, capture: () => Promise<Blob>): void {
  evidenceStore = store
  captureAdapter = capture
}

function idbRequest<T = unknown>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => { request.onsuccess = () => resolve(request.result); request.onerror = () => reject(request.error) })
}

function openStageDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('fpms-demo-v6-ui-session', 1)
    request.onupgradeneeded = () => request.result.createObjectStore('stages', { keyPath: 'id' })
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function nativeCapture(): Promise<Blob> {
  if (!navigator.mediaDevices?.getDisplayMedia) throw new Error('当前浏览器不支持阶段截图')
  const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false })
  try {
    const video = document.createElement('video')
    video.srcObject = stream
    await new Promise<void>((resolve, reject) => { video.onloadedmetadata = () => resolve(); video.onerror = () => reject(new Error('屏幕画面读取失败')) })
    await video.play()
    const scale = Math.min(1, 1280 / video.videoWidth)
    const canvas = document.createElement('canvas')
    canvas.width = Math.max(1, Math.floor(video.videoWidth * scale))
    canvas.height = Math.max(1, Math.floor(video.videoHeight * scale))
    canvas.getContext('2d')?.drawImage(video, 0, 0, canvas.width, canvas.height)
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/png'))
    if (!blob) throw new Error('阶段截图编码失败')
    return blob
  } finally {
    stream.getTracks().forEach((track) => track.stop())
  }
}

async function pngIdentity(png: Blob): Promise<{ sha256: string; width: number; height: number }> {
  const bytes = new Uint8Array(await png.arrayBuffer())
  if (bytes.length < 24 || bytes.slice(0, 8).join(',') !== '137,80,78,71,13,10,26,10') throw new Error('阶段截图不是有效 PNG')
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength)
  const width = view.getUint32(16)
  const height = view.getUint32(20)
  if (width < 320 || height < 180 || png.size > 1_400_000) throw new Error('阶段截图尺寸或大小不符合证据边界')
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  const sha256 = [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('')
  return { sha256, width, height }
}

export async function captureDemoStageScreenshot(stage: number): Promise<void> {
  if (!active || !persistedSession || !routeIsObserved()) throw new Error('演示会话未激活')
  if (!Number.isInteger(stage) || stage < 1 || stage > DEMO_UI_SCREENSHOT_COUNT) throw new Error('阶段序号无效')
  const capturePromise = (captureAdapter ?? nativeCapture)()
  try {
    const existing = await evidenceStore.list(persistedSession.tuple.run_id)
    const expectedStage = existing.length + 1
    if (stage !== expectedStage) throw new Error(`请先记录阶段 ${String(expectedStage).padStart(2, '0')} 截图`)
    if (existing.some((entry) => entry.stage === stage)) throw new Error('本阶段截图已记录')
    const png = await capturePromise
    const identity = await pngIdentity(png)
    const identities = await Promise.all(existing.map((entry) => pngIdentity(entry.png)))
    if (identities.some((entry) => entry.sha256 === identity.sha256)) throw new Error('阶段截图必须与此前阶段不同')
    await evidenceStore.put(persistedSession.tuple.run_id, stage, png)
    appendEvent({ kind: 'screenshot', stage, ...identity })
    emitSessionChange()
  } catch (error) {
    await capturePromise.catch(() => undefined)
    throw error
  }
}

export async function getNextDemoScreenshotStage(): Promise<number | null> {
  if (!persistedSession || !isTuple(persistedSession.tuple)) return null
  const stages = new Set((await evidenceStore.list(persistedSession.tuple.run_id)).map((entry) => entry.stage))
  for (let stage = 1; stage <= DEMO_UI_SCREENSHOT_COUNT; stage += 1) if (!stages.has(stage)) return stage
  return null
}

function bytesToBase64(bytes: Uint8Array): string {
  let binary = ''
  for (const byte of bytes) binary += String.fromCharCode(byte)
  return btoa(binary)
}

export async function finalizeDemoUiSessionEvidence(fetcher: typeof fetch = fetch): Promise<void> {
  if (!active || !persistedSession || !isTuple(persistedSession.tuple)) throw new Error('演示会话未激活')
  const session = persistedSession
  const screenshots = await evidenceStore.list(session.tuple.run_id)
  if (screenshots.length !== DEMO_UI_SCREENSHOT_COUNT || screenshots.some((entry, index) => entry.stage !== index + 1)) throw new Error('请先记录全部 11 个阶段截图')
  const identities = await Promise.all(screenshots.map((entry) => pngIdentity(entry.png)))
  if (new Set(identities.map((entry) => entry.sha256)).size !== DEMO_UI_SCREENSHOT_COUNT) throw new Error('阶段截图不得重复')
  try {
    await uploadLedger(fetcher)
    for (const entry of screenshots) {
      const filename = `observer-stage-${String(entry.stage).padStart(2, '0')}.png`
      const response = await postHost('/observer-artifact', {
        ...session.tuple,
        filename,
        encoding: 'base64', content: bytesToBase64(new Uint8Array(await entry.png.arrayBuffer())),
      }, fetcher)
      await expectHostResponse(response, 201, { filename })
    }
    const response = await postHost('/finalize', session.tuple, fetcher)
    await expectHostResponse(response, 200, { status: 'FINALIZED' })
    appendEvent({ kind: 'FINALIZED' })
    active = false
    activeStorage?.removeItem(DEMO_UI_SESSION_STORAGE_KEY)
    activeStorage?.removeItem(ledgerStorageKey(session.tuple.run_id))
    activeStorage?.removeItem(DEMO_UI_TERMINAL_STORAGE_KEY)
    await evidenceStore.clear(session.tuple.run_id)
    persistedSession = null
    emitSessionChange()
  } catch (error) {
    stopDemoUiSession('OBSERVER_FINALIZE_FAILED', activeStorage ?? undefined, fetcher)
    await exportStopDemoUiSession(fetcher)
    throw error
  }
}
