import type { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import {
  DEMO_BUSINESS_COUNT_KEYS,
  DEMO_UI_PARITY_SCHEMA_ID,
  parseDemoUiSessionPreflight,
} from './demo.contract'

export const DEMO_UI_SESSION_STORAGE_KEY = 'fpms_demo_v6_ui_session_v1'
export const DEMO_UI_SESSION_CHANGE_EVENT = 'fpms:demo-ui-session-change'

interface DemoUiSessionTuple {
  contract_version: typeof DEMO_UI_PARITY_SCHEMA_ID
  authority_classification: 'SYNTHETIC_TEST_ONLY'
  run_id: string
  candidate_commit: string
  candidate_tree: string
  authority_sha256: string
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

interface StopObservation {
  kind: 'STOP'
  reason: string
}

interface FinalizedObservation {
  kind: 'FINALIZED'
}

type DemoObserverEvent =
  | VisibleAction
  | MutationObservation
  | FailureObservation
  | StopObservation
  | FinalizedObservation

const mutationMethods = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])
const sensitiveKeys = /authorization|token|password|passwd|secret|credential|cookie/i
const requestObservations = new WeakMap<object, MutationObservation>()
const pendingDigests = new Set<Promise<void>>()
const observerLedger: DemoObserverEvent[] = []

let activeSession: DemoUiSessionTuple | null = null
let activeStorage: Storage | null = null
let observerBindingUrl: string | null = null
let lastVisibleAction: VisibleAction | null = null
let domObserverInstalled = false

function emitSessionChange(): void {
  if (typeof window !== 'undefined' && typeof CustomEvent !== 'undefined') {
    window.dispatchEvent(new CustomEvent(DEMO_UI_SESSION_CHANGE_EVENT))
  }
}

function storageOrDefault(storage?: Storage): Storage | null {
  if (storage) return storage
  return typeof sessionStorage === 'undefined' ? null : sessionStorage
}

function exactTuple(value: unknown): DemoUiSessionTuple {
  const preflight = parseDemoUiSessionPreflight(value)
  return {
    contract_version: preflight.contract_version,
    authority_classification: 'SYNTHETIC_TEST_ONLY',
    run_id: preflight.run_id,
    candidate_commit: preflight.candidate_commit,
    candidate_tree: preflight.candidate_tree,
    authority_sha256: preflight.authority_sha256,
  }
}

function parseStoredTuple(value: string | null): DemoUiSessionTuple | null {
  if (!value) return null
  try {
    const parsed: unknown = JSON.parse(value)
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) return null
    const row = parsed as Record<string, unknown>
    if (
      Object.keys(row).sort().join('|') !==
        [
          'authority_classification',
          'authority_sha256',
          'candidate_commit',
          'candidate_tree',
          'contract_version',
          'run_id',
        ].join('|') ||
      row.contract_version !== DEMO_UI_PARITY_SCHEMA_ID ||
      row.authority_classification !== 'SYNTHETIC_TEST_ONLY' ||
      typeof row.run_id !== 'string' ||
      row.run_id.length === 0 ||
      typeof row.candidate_commit !== 'string' ||
      !/^[0-9a-f]{40}$/.test(row.candidate_commit) ||
      typeof row.candidate_tree !== 'string' ||
      !/^[0-9a-f]{40}$/.test(row.candidate_tree) ||
      typeof row.authority_sha256 !== 'string' ||
      !/^[0-9a-f]{64}$/.test(row.authority_sha256)
    ) {
      return null
    }
    return row as unknown as DemoUiSessionTuple
  } catch {
    return null
  }
}

function sameTuple(left: DemoUiSessionTuple, right: DemoUiSessionTuple): boolean {
  return Object.keys(left).every(
    (key) => left[key as keyof DemoUiSessionTuple] === right[key as keyof DemoUiSessionTuple],
  )
}

function clearActiveSession(storage?: Storage): void {
  activeSession = null
  lastVisibleAction = null
  const target = storageOrDefault(storage) ?? activeStorage
  target?.removeItem(DEMO_UI_SESSION_STORAGE_KEY)
  activeStorage = null
  emitSessionChange()
}

export function stopDemoUiSession(reason: string, storage?: Storage): void {
  observerLedger.push({ kind: 'STOP', reason })
  clearActiveSession(storage)
}

export function activateDemoUiSession(value: unknown, storage?: Storage): boolean {
  const target = storageOrDefault(storage)
  if (!observerBindingUrl) {
    stopDemoUiSession('OBSERVER_BINDING_INVALID', target ?? undefined)
    return false
  }
  if (!target) {
    stopDemoUiSession('SESSION_STORAGE_MISSING')
    return false
  }
  try {
    const tuple = exactTuple(value)
    const storedRaw = target.getItem(DEMO_UI_SESSION_STORAGE_KEY)
    const stored = parseStoredTuple(storedRaw)
    if (storedRaw !== null && (!stored || !sameTuple(stored, tuple))) {
      stopDemoUiSession('SESSION_TUPLE_DRIFT', target)
      return false
    }
    target.setItem(DEMO_UI_SESSION_STORAGE_KEY, JSON.stringify(tuple))
    activeStorage = target
    activeSession = tuple
    emitSessionChange()
    return true
  } catch {
    stopDemoUiSession('PREFLIGHT_INVALID', target)
    return false
  }
}

export function restoreDemoUiSession(value: unknown, storage?: Storage): boolean {
  const target = storageOrDefault(storage)
  if (!observerBindingUrl) {
    stopDemoUiSession('OBSERVER_BINDING_INVALID', target ?? undefined)
    return false
  }
  if (!target) {
    stopDemoUiSession('SESSION_STORAGE_MISSING')
    return false
  }
  const stored = parseStoredTuple(target.getItem(DEMO_UI_SESSION_STORAGE_KEY))
  if (!stored) {
    stopDemoUiSession('SESSION_TUPLE_MISSING', target)
    return false
  }
  try {
    const current = exactTuple(value)
    if (!sameTuple(stored, current)) {
      stopDemoUiSession('SESSION_TUPLE_DRIFT', target)
      return false
    }
    activeStorage = target
    activeSession = current
    emitSessionChange()
    return true
  } catch {
    stopDemoUiSession('PREFLIGHT_INVALID', target)
    return false
  }
}

export function hasStoredDemoUiSession(storage?: Storage): boolean {
  const target = storageOrDefault(storage)
  return target !== null && target.getItem(DEMO_UI_SESSION_STORAGE_KEY) !== null
}

export function isDemoUiSessionActive(): boolean {
  return activeSession !== null
}

export function getDemoUiSession(): DemoUiSessionTuple | null {
  return activeSession === null ? null : { ...activeSession }
}

export function getDemoObserverLedger(): DemoObserverEvent[] {
  return observerLedger.map((entry) => ({ ...entry }))
}

export function configureDemoObserverBinding(pageHref: string): boolean {
  try {
    const pageUrl = new URL(pageHref)
    if (!['127.0.0.1', 'localhost'].includes(pageUrl.hostname)) return false
    const rawBinding = pageUrl.searchParams.get('fpmsObserverBinding')
    if (!rawBinding) return false
    const binding = new URL(rawBinding)
    if (
      binding.protocol !== 'http:' ||
      binding.hostname !== '127.0.0.1' ||
      binding.pathname !== '/observer-artifact' ||
      binding.username !== '' ||
      binding.password !== '' ||
      binding.search !== '' ||
      binding.hash !== ''
    ) {
      return false
    }
    observerBindingUrl = binding.href
    return true
  } catch {
    return false
  }
}

function actionId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `action-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function recordVisibleAction(input: {
  route: string
  role: string
  label_or_testid: string
}): string {
  const action: VisibleAction = {
    kind: 'action',
    action_id: actionId(),
    route: input.route,
    role: input.role,
    label_or_testid: input.label_or_testid,
  }
  if (activeSession) {
    lastVisibleAction = action
    observerLedger.push(action)
  }
  return action.action_id
}

function normalizedDigestValue(value: unknown, key = ''): unknown {
  if (sensitiveKeys.test(key)) return '[REDACTED]'
  if (value === null || typeof value === 'boolean' || typeof value === 'number') return value
  if (typeof value === 'string') {
    try {
      return normalizedDigestValue(JSON.parse(value))
    } catch {
      return value.normalize('NFKC').trim()
    }
  }
  if (value instanceof URLSearchParams) {
    return normalizedDigestValue(Object.fromEntries(value.entries()))
  }
  if (typeof FormData !== 'undefined' && value instanceof FormData) {
    const normalized: Record<string, unknown> = {}
    for (const [formKey, formValue] of value.entries()) {
      normalized[formKey] =
        typeof formValue === 'string'
          ? normalizedDigestValue(formValue, formKey)
          : { size: formValue.size, type: formValue.type }
    }
    return normalizedDigestValue(normalized)
  }
  if (Array.isArray(value)) return value.map((entry) => normalizedDigestValue(entry))
  if (typeof value === 'object' && value !== null) {
    return Object.fromEntries(
      Object.entries(value)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([entryKey, entryValue]) => [
          entryKey,
          normalizedDigestValue(entryValue, entryKey),
        ]),
    )
  }
  return String(value)
}

export async function normalizedPayloadSha256(payload: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(JSON.stringify(normalizedDigestValue(payload)))
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('')
}

function mutationPath(config: AxiosRequestConfig): string {
  try {
    const base = config.baseURL ?? (
      typeof window === 'undefined' ? 'http://127.0.0.1' : window.location.origin
    )
    return new URL(config.url ?? '/', base).pathname
  } catch {
    return '/'
  }
}

function trackDigest(observation: MutationObservation, payload: unknown): void {
  const pending = normalizedPayloadSha256(payload)
    .then((digest) => { observation.payload_sha256 = digest })
    .catch(() => { observation.payload_sha256 = '0'.repeat(64) })
  pendingDigests.add(pending)
  void pending.finally(() => pendingDigests.delete(pending))
}

export function observeMutationRequest<T extends AxiosRequestConfig>(config: T): T {
  const method = (config.method ?? 'GET').toUpperCase()
  if (!activeSession || !mutationMethods.has(method)) return config
  const action = lastVisibleAction
  const observation: MutationObservation = {
    kind: 'mutation',
    action_id: action?.action_id ?? null,
    route: action?.route ?? '',
    role: action?.role ?? '',
    label_or_testid: action?.label_or_testid ?? '',
    method,
    path: mutationPath(config),
    payload_sha256: '0'.repeat(64),
    status: null,
  }
  requestObservations.set(config, observation)
  observerLedger.push(observation)
  trackDigest(observation, config.data)
  if (!action) stopDemoUiSession('UNMATCHED_MUTATION')
  lastVisibleAction = null
  return config
}

export function observeMutationResponse(config: AxiosRequestConfig, status: number): void {
  const observation = requestObservations.get(config)
  if (observation) observation.status = status
}

function trackFailure(
  kind: FailureObservation['kind'],
  value: unknown,
  correlatedActionId: string | null = lastVisibleAction?.action_id ?? null,
): void {
  const failure: FailureObservation = {
    kind,
    action_id: correlatedActionId,
    digest: '0'.repeat(64),
  }
  observerLedger.push(failure)
  const pending = normalizedPayloadSha256(value)
    .then((digest) => { failure.digest = digest })
    .catch(() => undefined)
  pendingDigests.add(pending)
  void pending.finally(() => pendingDigests.delete(pending))
}

export function observeMutationFailure(config: AxiosRequestConfig, error: unknown): void {
  const observation = requestObservations.get(config)
  if (observation) observation.status = 0
  const failure = error as { name?: unknown; code?: unknown; status?: unknown }
  trackFailure(
    'network_failure',
    { name: failure?.name, code: failure?.code, status: failure?.status },
    observation?.action_id ?? null,
  )
}

export async function waitForObserverDigests(): Promise<void> {
  await Promise.allSettled([...pendingDigests])
}

export function installDemoUiObserver(instance: AxiosInstance): void {
  instance.interceptors.request.use((config) => observeMutationRequest(config))
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      observeMutationResponse(response.config, response.status)
      return response
    },
    (error: AxiosError) => {
      if (error.config) observeMutationFailure(error.config, error)
      return Promise.reject(error)
    },
  )
}

function visibleControl(target: EventTarget | null): HTMLElement | null {
  if (!(target instanceof Element)) return null
  const control = target.closest<HTMLElement>(
    '[data-testid],button,form,[role],input[type="submit"],input[type="button"]',
  )
  if (!control || control.hidden || control.getAttribute('aria-hidden') === 'true') return null
  if ('disabled' in control && control.disabled) return null
  const style = window.getComputedStyle(control)
  if (style.display === 'none' || style.visibility === 'hidden') return null
  return control
}

function controlRole(control: HTMLElement): string {
  const explicit = control.getAttribute('role')
  if (explicit) return explicit
  if (control.tagName === 'FORM') return 'form'
  return control.tagName === 'BUTTON' || control instanceof HTMLButtonElement ? 'button' : 'control'
}

function controlLabel(control: HTMLElement): string {
  return (
    control.dataset.testid ||
    control.getAttribute('aria-label') ||
    control.textContent?.replace(/\s+/g, ' ').trim() ||
    control.getAttribute('name') ||
    'unlabelled-control'
  ).slice(0, 160)
}

function installDomObserver(): void {
  if (domObserverInstalled || typeof document === 'undefined') return
  domObserverInstalled = true
  const capture = (event: Event) => {
    const control = visibleControl(event.target)
    if (!control) return
    recordVisibleAction({
      route: window.location.pathname,
      role: controlRole(control),
      label_or_testid: controlLabel(control),
    })
  }
  document.addEventListener('click', capture, true)
  document.addEventListener('submit', capture, true)

  const originalConsoleError = console.error.bind(console)
  console.error = (...values: unknown[]) => {
    originalConsoleError(...values)
    if (activeSession) trackFailure('console_failure', values)
  }
  window.addEventListener('error', (event) => {
    if (activeSession) trackFailure('console_failure', event.error ?? event.message)
  })
  window.addEventListener('unhandledrejection', (event) => {
    if (activeSession) trackFailure('console_failure', event.reason)
  })
}

export function prepareDemoUiSessionObserver(): boolean {
  if (typeof window === 'undefined' || !configureDemoObserverBinding(window.location.href)) {
    stopDemoUiSession('OBSERVER_BINDING_INVALID')
    return false
  }
  installDomObserver()
  return true
}

export async function finalizeDemoUiSessionEvidence(
  fetcher: typeof fetch = fetch,
): Promise<void> {
  if (!activeSession || !observerBindingUrl) throw new Error('演示会话未激活')
  await waitForObserverDigests()
  observerLedger.push({ kind: 'FINALIZED' })
  try {
    const response = await fetcher(observerBindingUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: 'observer-ui-ledger.json',
        encoding: 'json',
        content: {
          schema_id: DEMO_UI_PARITY_SCHEMA_ID,
          business_count_keys: [...DEMO_BUSINESS_COUNT_KEYS],
          session: activeSession,
          events: observerLedger,
        },
      }),
    })
    if (!response.ok) throw new Error('观察证据导出失败')
  } catch (error) {
    trackFailure('network_failure', { status: 'OBSERVER_BINDING_FAILED' })
    stopDemoUiSession('OBSERVER_FINALIZE_FAILED')
    throw error
  }
  clearActiveSession()
}
