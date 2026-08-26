import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const read = (path) => readFileSync(join(frontendRoot, path), 'utf8')
const page = read('src/modules/grantFees/pages/GrantFeeTaskList.vue')
const panelPath = join(frontendRoot, 'src/modules/documents/components/DocumentLifecycleEvidenceActions.vue')
const panel = existsSync(panelPath) ? readFileSync(panelPath, 'utf8') : ''
const grantApi = read('src/api/grantFees.ts')
const documentsApi = read('src/api/documents.ts')

function importFunctions(source, names, prelude = '') {
  const sourceFile = ts.createSourceFile('contract.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
  const declarations = sourceFile.statements.filter(
    (statement) => ts.isFunctionDeclaration(statement) && statement.name && names.includes(statement.name.text),
  )
  assert.equal(declarations.length, names.length, `missing executable helpers: ${names.join(', ')}`)
  const compiled = ts.transpileModule(
    `${prelude}\n${declarations.map((declaration) => declaration.getText(sourceFile)).join('\n')}`,
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`)
}

const httpCalls = []
let rejectedError = null
globalThis.__ordinal05Http = {
  async get(url) {
    httpCalls.push({ method: 'GET', url })
    if (rejectedError) throw rejectedError
    if (url.endsWith('/official-fee-preview')) return { data: { preview_digest: 'preview-digest' } }
    if (url === '/grant-fee-tasks/list') return { data: globalThis.__ordinal05List }
    return { data: globalThis.__ordinal05State }
  },
  async post(url, payload) {
    httpCalls.push({ method: 'POST', url, payload })
    if (rejectedError) throw rejectedError
    if (url.endsWith('/replacement-notice')) {
      return { data: { document: { id: 'replacement-document' }, replacement_task: baseTask, superseded_task_id: 'task-original', reused: false } }
    }
    if (url === '/grant-fee-tasks/batch-instruction') {
      return { data: { success_count: 1, failure_count: 0, updated_task_ids: payload.task_ids } }
    }
    return { data: { event_type: 'GRANT_REGISTRATION_NOTICE_RECORDED', reused: false } }
  },
  async put(url, payload) {
    httpCalls.push({ method: 'PUT', url, payload })
    if (rejectedError) throw rejectedError
    return { data: globalThis.__ordinal05State }
  },
}

const grant = await importFunctions(
  grantApi,
  [
    'normalizeBoolean',
    'normalizeStatus',
    'normalizeInstruction',
    'normalizeLineageStatus',
    'mapGrantFeeTask',
    'normalizeAction',
    'mapGrantFeeTaskStateResult',
    'bindGrantFeeTaskState',
    'isCurrentGrantFeeTask',
    'grantFeeTaskAllowsAction',
    'getGrantFeeTasks',
    'getGrantFeeTaskState',
    'recordGrantNoticeLifecycle',
    'createGrantFeeTaskReplacementNotice',
    'getGrantOfficialFeePreview',
    'applyGrantFeeTaskAction',
    'applyGrantFeeBatchInstruction',
  ],
  'const http = globalThis.__ordinal05Http',
)
const documents = await importFunctions(documentsApi, ['selectReviewedEvidenceOptions'])

const hashA = `sha256:${'a'.repeat(64)}`
const hashB = `sha256:${'b'.repeat(64)}`
const baseTask = {
  task_id: 'task-original', case_id: 'case-a', case_no: 'A-001', status: 'OPEN', due_date: '2026-09-01',
  client_instruction: 'NONE', gov_fee_amt: 100, service_fee_amt: 20, currency: 'CNY', draft_generated: false,
  notice_sent: false, notify_count: 0, is_overdue: false, billed: false, trigger_rule: '授权通知',
  deadline_rule: '通知期限', fee_basis: '官费依据', fee_node_explanation: '授权阶段', lineage_status: 'CONFIRMED',
  source_document_id: 'document-original', deadline_source: 'IMPORTED_OFFICIAL_NOTICE',
  deadline_confirmed_at: '2026-08-26T10:00:00', allowed_actions: [], state_binding_current: false,
  projection_valid: true,
}
const baseState = {
  task_id: 'task-original', case_id: 'case-a', state: 'OPEN', client_instruction: 'NONE', notify_count: 0,
  draft_generated: false, notice_sent: false, is_overdue: false,
  allowed_actions: ['mark_waiting_client'], lineage_status: 'CONFIRMED',
  source_document_id: 'document-original', deadline_source: 'IMPORTED_OFFICIAL_NOTICE',
  deadline_confirmed_at: '2026-08-26T10:00:00', trigger_rule: '授权通知', deadline_rule: '通知期限',
  fee_basis: '官费依据', fee_node_explanation: '授权阶段',
  projection_valid: true,
}

const currentTask = grant.bindGrantFeeTaskState(baseTask, baseState, 1)
assert.equal(grant.isCurrentGrantFeeTask(currentTask), true)
assert.equal(grant.grantFeeTaskAllowsAction(currentTask, 'mark_waiting_client'), true)
assert.equal(grant.grantFeeTaskAllowsAction(currentTask, 'record_pay_instruction'), false)
assert.equal(grant.grantFeeTaskAllowsAction({ ...currentTask, client_instruction: 'PAY' }, 'record_pay_instruction'), false)

const earlyPayState = { ...baseState, allowed_actions: ['mark_waiting_client', 'record_pay_instruction'] }
const earlyPayTask = grant.bindGrantFeeTaskState(baseTask, earlyPayState, 1)
const callsBeforeEarlyPay = httpCalls.length
if (grant.grantFeeTaskAllowsAction(earlyPayTask, 'record_pay_instruction')) {
  await grant.applyGrantFeeBatchInstruction({ task_ids: [earlyPayTask.task_id], action: 'record_pay_instruction' })
}
assert.equal(httpCalls.length, callsBeforeEarlyPay)

const canonicalStateActions = {
  OPEN: ['mark_waiting_client'],
  WAITING_CLIENT: ['record_pay_instruction', 'record_abandon_instruction'],
  READY_TO_DRAFT: ['mark_draft_generated'],
  DRAFT_GENERATED: ['mark_done'],
  DONE: [],
}
const stateFacts = {
  OPEN: { client_instruction: 'NONE', draft_generated: false },
  WAITING_CLIENT: { client_instruction: 'NONE', draft_generated: false },
  READY_TO_DRAFT: { client_instruction: 'PAY', draft_generated: false },
  DRAFT_GENERATED: { client_instruction: 'PAY', draft_generated: true },
  DONE: { client_instruction: 'ABANDON', draft_generated: false },
}
const boundByState = {}
for (const [state, allowedActions] of Object.entries(canonicalStateActions)) {
  const facts = stateFacts[state]
  globalThis.__ordinal05State = { ...baseState, state, allowed_actions: allowedActions, ...facts }
  boundByState[state] = grant.bindGrantFeeTaskState(
    { ...baseTask, status: state, ...facts },
    await grant.getGrantFeeTaskState(baseTask.task_id),
    1,
  )
  assert.equal(grant.isCurrentGrantFeeTask(boundByState[state]), true)
  assert.deepEqual(boundByState[state].allowed_actions, allowedActions)
}
for (const mismatchedState of [
  { ...baseState, allowed_actions: ['mark_waiting_client', 'record_pay_instruction'] },
  { ...baseState, allowed_actions: [] },
  { ...baseState, allowed_actions: ['mark_waiting_client', 'mark_waiting_client'] },
  { ...baseState, allowed_actions: ['mark_waiting_client', 'unknown_action'] },
  { ...baseState, state: 'WAITING_CLIENT', allowed_actions: ['record_pay_instruction'] },
]) {
  const task = { ...baseTask, status: mismatchedState.state }
  const bound = grant.bindGrantFeeTaskState(task, mismatchedState, 1)
  assert.equal(grant.isCurrentGrantFeeTask(bound), false)
  assert.deepEqual(bound.allowed_actions, [])
}

for (const invalid of [
  grant.bindGrantFeeTaskState(baseTask, baseState, 2),
  grant.bindGrantFeeTaskState({ ...baseTask, lineage_status: 'SUPERSEDED' }, baseState, 1),
  grant.bindGrantFeeTaskState(baseTask, { ...baseState, case_id: 'case-b' }, 1),
  grant.bindGrantFeeTaskState(baseTask, { ...baseState, source_document_id: 'document-drift' }, 1),
]) {
  assert.equal(grant.isCurrentGrantFeeTask(invalid), false)
  assert.equal(grant.grantFeeTaskAllowsAction(invalid, 'mark_waiting_client'), false)
  assert.deepEqual(invalid.allowed_actions, [])
}

globalThis.__ordinal05State = baseState
assert.deepEqual(await grant.getGrantFeeTaskState('task-original'), baseState)
assert.deepEqual(httpCalls.at(-1), { method: 'GET', url: '/grant-fee-tasks/task-original/state' })

const backendListTask = {
  task_id: baseTask.task_id, case_id: baseTask.case_id, case_no: baseTask.case_no, status: baseTask.status,
  due_date: baseTask.due_date, client_instruction: baseTask.client_instruction, gov_fee_amt: baseTask.gov_fee_amt,
  service_fee_amt: baseTask.service_fee_amt, currency: baseTask.currency, draft_generated: baseTask.draft_generated,
  notice_sent: baseTask.notice_sent, notify_count: baseTask.notify_count, is_overdue: baseTask.is_overdue,
  billed: baseTask.billed, trigger_rule: baseTask.trigger_rule, deadline_rule: baseTask.deadline_rule,
  fee_basis: baseTask.fee_basis, fee_node_explanation: baseTask.fee_node_explanation,
  lineage_status: baseTask.lineage_status, source_document_id: baseTask.source_document_id,
  deadline_source: baseTask.deadline_source, deadline_confirmed_at: baseTask.deadline_confirmed_at,
}
for (const [rawListOverrides, rawStateOverrides] of [
  [{ status: 'UNKNOWN_STATE', client_instruction: 'UNKNOWN_INSTRUCTION' }, { state: 'UNKNOWN_STATE', client_instruction: 'UNKNOWN_INSTRUCTION' }],
  [{}, { allowed_actions: ['mark_waiting_client', 'unknown_action'] }],
  [{}, { allowed_actions: ['mark_waiting_client', 'mark_waiting_client'] }],
  [{ status: 'DONE', client_instruction: 'ABANDON' }, { state: 'DONE', client_instruction: 'ABANDON', allowed_actions: null }],
]) {
  globalThis.__ordinal05List = { items: [{ ...backendListTask, ...rawListOverrides }], page: 1, page_size: 20, total: 1 }
  globalThis.__ordinal05State = { ...baseState, ...rawStateOverrides }
  const mappedTask = (await grant.getGrantFeeTasks()).items[0]
  const mappedState = await grant.getGrantFeeTaskState(mappedTask.task_id)
  const bound = grant.bindGrantFeeTaskState(mappedTask, mappedState, 1)
  const mutationCallsBefore = httpCalls.filter((call) => call.method !== 'GET').length
  if (grant.grantFeeTaskAllowsAction(bound, 'mark_waiting_client')) {
    await grant.applyGrantFeeTaskAction(bound.task_id, 'mark_waiting_client')
  }
  assert.equal(grant.isCurrentGrantFeeTask(bound), false)
  assert.deepEqual(bound.allowed_actions, [])
  assert.equal(httpCalls.filter((call) => call.method !== 'GET').length, mutationCallsBefore)
}
globalThis.__ordinal05State = baseState

const approvedAttachment = (overrides = {}) => ({
  id: 'attachment-original', filename: '原始授权通知书.pdf', file_size: 12, created_at: '2026-08-20',
  document_id: 'document-original', role: 'GRANT_NOTICE', evidence_version_id: 'evidence-original',
  content_hash: hashA, review_state: 'APPROVED', is_current: true, is_final: true, ...overrides,
})
const originalDocument = {
  id: 'document-original', case_id: 'case-a', title: '原始授权通知书', direction: 'IN',
  attachments: [
    approvedAttachment(),
    approvedAttachment({ id: 'pending', review_state: 'PENDING' }),
    approvedAttachment({ id: 'stale', is_current: false }),
    approvedAttachment({ id: 'drift', content_hash: `sha256:${'A'.repeat(64)}` }),
  ],
}
const replacementDocument = {
  id: 'document-replacement', case_id: 'case-a', title: '更正授权通知书', direction: 'IN',
  attachments: [approvedAttachment({
    id: 'attachment-replacement', filename: '更正授权通知书.pdf', document_id: 'document-replacement',
    evidence_version_id: 'evidence-replacement', content_hash: hashB,
  })],
}
const originalOptions = documents.selectReviewedEvidenceOptions([originalDocument], 'case-a')
const replacementOptions = documents.selectReviewedEvidenceOptions([replacementDocument], 'case-a')
assert.deepEqual(originalOptions.map(({ title, role, filename }) => ({ title, role, filename })), [
  { title: '原始授权通知书', role: 'GRANT_NOTICE', filename: '原始授权通知书.pdf' },
])
assert.deepEqual(replacementOptions.map(({ title, role, filename }) => ({ title, role, filename })), [
  { title: '更正授权通知书', role: 'GRANT_NOTICE', filename: '更正授权通知书.pdf' },
])

const replacementTask = grant.bindGrantFeeTaskState(
  { ...baseTask, task_id: 'task-replacement', source_document_id: 'document-replacement' },
  { ...baseState, task_id: 'task-replacement', source_document_id: 'document-replacement' },
  1,
)
const timing = { recorded_at: '2026-08-26T11:00:00', idempotency_key: 'grant-notice-1' }
await grant.recordGrantNoticeLifecycle(currentTask, originalOptions[0], timing)
await grant.recordGrantNoticeLifecycle(replacementTask, replacementOptions[0], { ...timing, idempotency_key: 'grant-notice-2' })
assert.deepEqual(httpCalls.slice(-2), [
  {
    method: 'POST', url: '/grant-fee-tasks/task-original/lifecycle/grant-notice',
    payload: { reviewed_evidence_version_id: 'evidence-original', expected_content_hash: hashA, ...timing },
  },
  {
    method: 'POST', url: '/grant-fee-tasks/task-replacement/lifecycle/grant-notice',
    payload: {
      reviewed_evidence_version_id: 'evidence-replacement', expected_content_hash: hashB,
      recorded_at: timing.recorded_at, idempotency_key: 'grant-notice-2',
    },
  },
])

const callsBeforeInvalid = httpCalls.length
for (const [task, evidence] of [
  [{ ...currentTask, lineage_status: 'SUPERSEDED' }, originalOptions[0]],
  [currentTask, { ...originalOptions[0], case_id: 'case-b' }],
  [currentTask, { ...originalOptions[0], document_id: 'document-replacement' }],
  [currentTask, { ...originalOptions[0], content_hash: `sha256:${'A'.repeat(64)}` }],
]) {
  await assert.rejects(grant.recordGrantNoticeLifecycle(task, evidence, timing))
}
const collisionDocument = {
  ...originalDocument,
  attachments: [
    approvedAttachment({ id: 'collision-a', filename: '碰撞甲.pdf' }),
    approvedAttachment({ id: 'collision-b', filename: '碰撞乙.pdf' }),
  ],
}
assert.deepEqual(documents.selectReviewedEvidenceOptions([collisionDocument], 'case-a'), [])
for (const option of documents.selectReviewedEvidenceOptions([collisionDocument], 'case-a')) {
  await grant.recordGrantNoticeLifecycle(currentTask, option, timing)
}
assert.equal(httpCalls.length, callsBeforeInvalid)

const backendError = { status: 409, code: 'EVIDENCE_CONFLICT' }
rejectedError = backendError
await assert.rejects(
  grant.recordGrantNoticeLifecycle(currentTask, originalOptions[0], timing),
  (error) => error === backendError,
)
rejectedError = null

const replacementPayload = {
  idempotency_key: 'replace-1', reason: '更正期限',
  document: {
    doc_template_id: 'template-1', doc_date: '2026-08-26', title: '更正授权通知书', ref_no: 'GRANT-2',
    official_due_date: '2026-09-10', official_due_date_source: 'IMPORTED_OFFICIAL_NOTICE',
    official_due_date_status: 'CONFIRMED',
  },
}
const replacementResult = await grant.createGrantFeeTaskReplacementNotice('task-original', replacementPayload)
assert.equal(replacementResult.superseded_task_id, 'task-original')
assert.deepEqual(httpCalls.at(-1), {
  method: 'POST', url: '/grant-fee-tasks/task-original/replacement-notice', payload: replacementPayload,
})
assert.deepEqual(await grant.getGrantOfficialFeePreview('task-original'), { preview_digest: 'preview-digest' })
assert.deepEqual(httpCalls.at(-1), { method: 'GET', url: '/grant-fee-tasks/task-original/official-fee-preview' })
const payCallsBefore = httpCalls.length
assert.equal(grant.grantFeeTaskAllowsAction(boundByState.WAITING_CLIENT, 'record_pay_instruction'), true)
await grant.applyGrantFeeBatchInstruction({ task_ids: [boundByState.WAITING_CLIENT.task_id], action: 'record_pay_instruction' })
assert.deepEqual(httpCalls.at(-1), {
  method: 'POST', url: '/grant-fee-tasks/batch-instruction',
  payload: { task_ids: ['task-original'], action: 'record_pay_instruction' },
})
assert.equal(httpCalls.length, payCallsBefore + 1)
assert.equal(grant.grantFeeTaskAllowsAction(boundByState.READY_TO_DRAFT, 'record_pay_instruction'), false)

assert.match(page, /<DocumentLifecycleEvidenceActions/)
assert.match(page, /选择授权通知证据/)
assert.match(page, /标记等待客户/)
assert.match(page, /grantFeeTaskAllowsAction\(row, 'mark_waiting_client'\)/)
assert.match(panel, /\$\{option\.title\}｜\$\{option\.role\}｜\$\{option\.filename\}/)
assert.match(panel, /recordGrantNoticeLifecycle/)
assert.doesNotMatch(page + panel, /<el-input[^>]+(?:taskId|documentId|attachmentId|evidenceVersionId|任务ID|文书ID|附件ID|证据版本ID)/i)
for (const unchanged of ['预览官费', '更正通知', "record_pay_instruction", 'preview_digest']) {
  assert.match(page, new RegExp(unchanged))
}

delete globalThis.__ordinal05Http
delete globalThis.__ordinal05State
delete globalThis.__ordinal05List
console.log('demo V6 grant UI contract: PASS')
