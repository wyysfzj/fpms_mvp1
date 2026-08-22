import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import ts from 'typescript'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const api = readFileSync(join(root, 'src/modules/demo/demo.api.ts'), 'utf8')
const feesApi = readFileSync(join(root, 'src/api/fees.ts'), 'utf8')
const page = readFileSync(join(root, 'src/modules/demo/pages/DemoAbc.vue'), 'utf8')
const inputsPage = readFileSync(join(root, 'src/modules/demo/pages/DemoInputs.vue'), 'utf8')
const router = readFileSync(join(root, 'src/router/index.ts'), 'utf8')
const menu = readFileSync(join(root, 'src/constants/menu.ts'), 'utf8')
const runbook = readFileSync(join(root, '../docs/postdemo/demo-lifecycle-customer-v5-runbook.md'), 'utf8')

function importFunctions(source, names) {
  const sourceFile = ts.createSourceFile(
    'fees.ts',
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TS,
  )
  const declarations = sourceFile.statements.filter(
    (statement) => ts.isFunctionDeclaration(statement)
      && statement.name
      && names.includes(statement.name.text),
  )
  assert.equal(declarations.length, names.length, 'all executable lock helpers must exist')
  const compiled = ts.transpileModule(
    declarations.map((declaration) => declaration.getText(sourceFile)).join('\n'),
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`)
}

const {
  executeFeeDraftLockCommand,
  shouldReconcileFeeDraftLock,
} = await importFunctions(feesApi, [
  'shouldReconcileFeeDraftLock',
  'executeFeeDraftLockCommand',
])

for (const endpoint of [
  '/fees/demo-preflight',
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
assert.ok(router.includes("path: 'demo/inputs'"))
assert.ok(!menu.includes("route: '/demo/abc'"))
assert.ok(!menu.includes("route: '/demo/inputs'"))
assert.ok(!menu.includes('ABC 演示台'))
assert.ok(runbook.includes('同一浏览器会话中保留一个不共享的 `/demo/abc` 标签页'))
assert.ok(runbook.includes('点击“校验全新演示环境”'))
assert.match(inputsPage, /import \{ readDemoPreflight \} from '\.\.\/demo\.api'/)
for (const readOnlyField of [
  'readiness',
  'authority_classification',
  'customer_activation_eligible',
  'business_counts',
  'bundle_id',
  'bundle_version',
  'manifest_sha256',
  'template_code',
  'template_sha256',
  'item_code',
  'source_ref',
  'source_version',
  'source_sha256',
]) assert.ok(inputsPage.includes(readOnlyField), `missing read-only input field ${readOnlyField}`)
for (const businessCount of [
  'client', 'contact', 'case', 'package', 'task', 'obligation', 'draft', 'bill', 'payment', 'offset',
]) assert.ok(inputsPage.includes(`key: '${businessCount}'`), `missing business count ${businessCount}`)
for (const forbiddenControl of [
  'createDemoServiceObligation',
  'recordDemoPayInstruction',
  'createDemoDraft',
  'lockDemoDraft',
  'createDemoBill',
  'createDemoBankReceipt',
  'createDemoFullOffset',
  'readDemoServiceItem',
  'data-testid="create-obligation"',
  'data-testid="create-draft"',
  'data-testid="create-bill"',
  'data-testid="create-payment"',
  'data-testid="create-offset"',
]) assert.ok(!inputsPage.includes(forbiddenControl), `read-only input page exposes ${forbiddenControl}`)
assert.ok(page.includes('DEMO_ONLY'))
assert.ok(page.includes('template_sha256'))
assert.ok(page.includes('manifest_sha256'))
for (const visibleLabel of [
  'Bundle ID / 版本',
  'Manifest SHA-256',
  '模板代码',
  '模板文件 SHA-256',
  '费率项目代码',
  '费率来源',
  '费率来源版本',
  '费率来源 SHA-256',
  '官方费用：未配置（不计入总额）',
]) assert.ok(page.includes(visibleLabel), `missing visible IA-00 label ${visibleLabel}`)
assert.ok(page.includes('data-testid="demo-preflight"'))
assert.ok(page.includes('data-testid="demo-disclaimer"'))
assert.ok(page.includes("const demoReady = computed(() => preflight.value?.readiness === 'READY')"))
assert.ok(page.includes("preflight.value = undefined"))
assert.ok(page.includes(':disabled="!selectedCase || !demoReady"'))
assert.ok(page.includes('if (!selectedCase.value || !bundle.value || !demoReady.value) return'))
assert.ok(page.includes('演示输入已加载，尚未通过全新环境校验'))
for (const testId of [
  'bundle-id', 'bundle-version', 'manifest-sha256', 'template-code', 'template-sha256',
  'rate-item-code', 'rate-source-ref', 'rate-source-version', 'rate-source-sha256',
]) assert.ok(page.includes(`data-testid="${testId}"`), `missing IA-00 provenance test id ${testId}`)
assert.ok(api.includes('readDemoPreflight'))
assert.ok(api.includes('parseDemoPreflight'))
assert.ok(page.includes('idempotencyKeys'))
assert.ok(page.includes("const DEMO_SESSION_KEY = 'fpms_demo_abc_session_v1'"))
assert.ok(page.includes('sessionStorage.setItem(DEMO_SESSION_KEY'))
assert.ok(page.includes('sessionStorage.getItem(DEMO_SESSION_KEY)'))
assert.ok(page.includes('obligation_id?: string'))
assert.ok(page.includes('obligation_id: obligation.value?.obligation.id'))
assert.ok(!page.includes('obligation?: DemoFeeObligationResponse'))
assert.ok(!page.includes('obligation: obligation.value,'))
assert.ok(page.includes('readDemoServiceObligation('))
assert.ok(api.includes('export async function readDemoServiceObligation('))
assert.ok(api.includes("`/fees/obligations/${obligationId}`"))
assert.ok(page.includes('saved.preflight.manifest_sha256 !== currentBundle.manifest_sha256'))
for (const authoritativeRead of [
  '`/fees/drafts/${draftId}`',
  '`/bills/from-drafts/idempotency/${encodeURIComponent(idempotencyKey)}`',
  '`/payments/idempotency/${encodeURIComponent(idempotencyKey)}`',
  '`/offsets/idempotency/${encodeURIComponent(idempotencyKey)}`',
]) assert.ok(api.includes(authoritativeRead), `missing authoritative reload ${authoritativeRead}`)
assert.equal(
  (api.match(/idempotency_key: idempotencyKey/g) || []).length,
  5,
  'obligation, instruction, bill, payment and offset each send one idempotency key',
)
assert.ok(!/idempotency_key: idempotencyKey,\s*idempotency_key: idempotencyKey/.test(api))
assert.ok(!page.includes('amount || 0'))
assert.ok(!page.includes('Number('))
assert.ok(page.includes("import { getCaseByCaseNo } from '../../../api/cases'"))
assert.ok(page.includes('getCaseByCaseNo(caseNoInput.value)'))
assert.ok(page.includes('data-testid="demo-case-no"'))
assert.ok(!page.includes('data-testid="demo-case-id"'))
assert.match(
  api,
  /http\.post\(`\/fees\/drafts\/\$\{draftId\}\/lock`\)[\s\S]*http\.get<DemoDraft>\(`\/fees\/drafts\/\$\{draftId\}`\)/,
  'draft lock acknowledgement must be reconciled with the authoritative draft detail',
)
const lockFeeDraftStart = feesApi.indexOf('export async function lockFeeDraft(')
const unlockFeeDraftStart = feesApi.indexOf('export async function unlockFeeDraft(')
assert.ok(lockFeeDraftStart >= 0 && unlockFeeDraftStart > lockFeeDraftStart, 'missing bounded lockFeeDraft adapter')
const lockFeeDraftSource = feesApi.slice(lockFeeDraftStart, unlockFeeDraftStart)
assert.match(lockFeeDraftSource, /return executeFeeDraftLockCommand\(/)
assert.match(lockFeeDraftSource, /await http\.post\(`\/fees\/drafts\/\$\{draftId\}\/lock`\)/)
assert.ok(lockFeeDraftSource.includes('() => getFeeDraft(draftId)'), 'normal fee page must project the authoritative draft after the lock acknowledgement')
assert.ok(!lockFeeDraftSource.includes('return response.data'), 'lock acknowledgement is not a fee draft detail')

assert.equal(shouldReconcileFeeDraftLock({ status: 0, code: 'UNKNOWN_ERROR' }), true)
for (const error of [
  { status: 400, code: 'BAD_REQUEST' },
  { status: 409, code: 'CONFLICT' },
  { status: 500, code: 'UNKNOWN_ERROR' },
  { status: 0, code: 'OTHER' },
  null,
]) {
  assert.equal(shouldReconcileFeeDraftLock(error), false)
}

const draftId = 'draft-locked-1'
const lockedDraft = { id: draftId, status: 'LOCKED' }
const successCalls = { post: 0, read: 0 }
assert.equal(
  await executeFeeDraftLockCommand(
    draftId,
    async () => { successCalls.post += 1 },
    async () => { successCalls.read += 1; return lockedDraft },
  ),
  lockedDraft,
)
assert.deepEqual(successCalls, { post: 1, read: 1 })

for (const deterministicError of [
  { status: 400, code: 'BAD_REQUEST' },
  { status: 409, code: 'CONFLICT' },
  { status: 500, code: 'UNKNOWN_ERROR' },
  { status: 0, code: 'OTHER' },
]) {
  const calls = { post: 0, read: 0 }
  await assert.rejects(
    executeFeeDraftLockCommand(
      draftId,
      async () => { calls.post += 1; throw deterministicError },
      async () => { calls.read += 1; return lockedDraft },
    ),
    (error) => error === deterministicError,
  )
  assert.deepEqual(calls, { post: 1, read: 0 })
}

const unknownTransportError = { status: 0, code: 'UNKNOWN_ERROR' }
const reconciliationCalls = { post: 0, read: 0 }
assert.equal(
  await executeFeeDraftLockCommand(
    draftId,
    async () => { reconciliationCalls.post += 1; throw unknownTransportError },
    async () => { reconciliationCalls.read += 1; return lockedDraft },
  ),
  lockedDraft,
)
assert.deepEqual(reconciliationCalls, { post: 1, read: 1 })

for (const readResult of [
  { id: 'another-draft', status: 'LOCKED' },
  { id: draftId, status: 'OPEN' },
]) {
  const calls = { post: 0, read: 0 }
  await assert.rejects(
    executeFeeDraftLockCommand(
      draftId,
      async () => { calls.post += 1; throw unknownTransportError },
      async () => { calls.read += 1; return readResult },
    ),
    (error) => error === unknownTransportError,
  )
  assert.deepEqual(calls, { post: 1, read: 1 })
}

const readFailure = new Error('read failed')
const readFailureCalls = { post: 0, read: 0 }
await assert.rejects(
  executeFeeDraftLockCommand(
    draftId,
    async () => { readFailureCalls.post += 1; throw unknownTransportError },
    async () => { readFailureCalls.read += 1; throw readFailure },
  ),
  (error) => error === unknownTransportError,
)
assert.deepEqual(readFailureCalls, { post: 1, read: 1 })

for (const requiredCustomerValue of [
  'CYIP-CN-INV-<运行后缀>',
  '授权登记阶段代理服务费',
  '`AR-CYZN-${suffix}`',
  '`RCPT-CYZN-${suffix}`',
  '`BTR-CYZN-${suffix}`',
]) assert.ok(page.includes(requiredCustomerValue), `missing realistic customer value ${requiredCustomerValue}`)
assert.ok(api.includes("remark: '澄岳智造技术（苏州）有限公司客户回款'"))
for (const rejectedCustomerValue of [
  'DEMO-AR-',
  'DEMO-PAY-',
  'DEMO-BANK-',
  '虚构集成演示客户',
  '虚构主联系人',
  '集成演示服务费',
]) assert.ok(!page.includes(rejectedCustomerValue) && !api.includes(rejectedCustomerValue), `rejected customer value ${rejectedCustomerValue}`)

for (const recoveryContract of [
  'recoverDemoLockedDraft',
  'overlay.caseId !== caseId',
  'overlay.hasMore',
  'obligationMatches.length !== 1',
  'sourceActivityId !== obligation.source_activity_id',
  'draftFacts.length !== 1',
  'feeCode !== obligation.item_code',
  'payableAmount !== obligation.amount',
  'draft.case_id !== caseId',
  'draft.client_id !== clientId',
  "draft.currency !== 'CNY'",
  "draft.status !== 'LOCKED'",
  "draft.total_gov !== '0.00'",
  'draft.total_service !== obligation.amount',
  "draft.total_misc !== '0.00'",
  'draft.amount !== obligation.amount',
]) assert.ok(api.includes(recoveryContract), `missing fail-closed cross-page recovery contract ${recoveryContract}`)
assert.ok(page.includes('draft.value = await recoverDemoLockedDraft('))
assert.ok(!page.includes('data-testid="create-draft"'))
assert.ok(!page.includes('confirmPayAndLock'))

console.log('demo ABC frontend source contract OK')
