import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const read = (path) => readFileSync(join(frontendRoot, path), 'utf8')
const demoApi = read('src/modules/demo/demo.api.ts')
const demoContract = read('src/modules/demo/demo.contract.ts')
const govPaymentsApi = read('src/api/govPayments.ts')
const demoAbc = read('src/modules/demo/pages/DemoAbc.vue')
const caseFees = read('src/modules/cases/components/CaseFeesTab.vue')
const feeLane = read('src/modules/cases/components/FeeObligationLane.vue')
const lifecycleDisplay = read('src/modules/cases/components/lifecycleOverlayDisplay.ts')
const feeItems = read('src/modules/fees/components/FeeDraftItemsTable.vue')
const feeDetail = read('src/modules/fees/pages/FeeDraftDetail.vue')
const payList = read('src/modules/annuity/pages/PayListDetail.vue')
const payment = read('src/modules/annuity/pages/GovPaymentCreate.vue')
const script = (source) => source.split('<script setup lang="ts">', 2)[1].split('</script>', 1)[0]

function importFunctions(source, names, prelude = '') {
  const sourceFile = ts.createSourceFile('contract.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
  const declarations = sourceFile.statements.filter(
    (statement) => ts.isFunctionDeclaration(statement) && statement.name && names.includes(statement.name.text),
  )
  assert.equal(declarations.length, names.length, `missing executable helpers: ${names.join(', ')}`)
  const body = declarations.map((declaration) => {
    const text = declaration.getText(sourceFile)
    return text.startsWith('export ') ? text : `export ${text}`
  }).join('\n')
  const compiled = ts.transpileModule(`${prelude}\n${body}`, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  }).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`)
}

const hash = 'a'.repeat(64)
const serviceItem = {
  classification: 'DEMO_ONLY', bundle_id: 'bundle-1', bundle_version: 'v1', manifest_sha256: hash,
  template_code: 'SERVICE_TEMPLATE', template_sha256: hash, template_required_variables: ['case_no'],
  item_code: 'SERVICE_FEE', name_zh_cn: '代理服务费', currency: 'CNY', amount: '1500.00',
  source_ref: 'synthetic', source_version: 'v1', source_sha256: hash, disclaimer_zh_cn: '仅用于技术展示',
}
const resultFor = (overrides = {}) => ({
  ...serviceItem,
  obligation: { id: '11111111-1111-4111-8111-111111111111', case_id: 'case-a', fee_domain: 'SERVICE' },
  source_activity_id: '22222222-2222-4222-8222-222222222222',
  idempotency_key: 'service-intent-1', reused: false, ...overrides,
})

const serviceCalls = []
let itemValue = serviceItem
let createValue = resultFor()
globalThis.__ordinal06ReadItem = async () => {
  serviceCalls.push({ method: 'GET', path: '/fees/demo-service-item' })
  if (itemValue instanceof Error) throw itemValue
  return itemValue
}
globalThis.__ordinal06Create = async (caseId, key) => {
  serviceCalls.push({ method: 'POST', path: '/fees/demo-service-obligations', caseId, key })
  return createValue
}
const demo = await importFunctions(
  demoApi,
  ['createValidatedDemoServiceObligation'],
  'const readDemoServiceItem = globalThis.__ordinal06ReadItem; const createDemoServiceObligation = globalThis.__ordinal06Create',
)
const guards = await importFunctions(script(caseFees), ['canStartDemoServiceObligation'])
const payListRoutes = await importFunctions(script(payList), ['buildPaymentRegistrationQuery'])
const paymentRoutes = await importFunctions(script(payment), ['buildPaymentResultNavigation'])
const govPaymentMoney = await importFunctions(govPaymentsApi, ['toDemoMoney'])
const adjustmentQuantity = await importFunctions(script(feeItems), ['resolveAdjustmentQuantity'])
const feeLaneProjection = await importFunctions(lifecycleDisplay, ['mergeRelatedFacts', 'latestObligationsById'])
const billItems = await importFunctions(demoContract, ['serviceItemAmountsEqualBill', 'serviceReceiptFeeCodeMatchesBill'])

for (const [code, label] of [
  ['GRANT_REGISTRATION_OFFICIAL_FEES', '授权登记官费义务'],
  ['RECOGNIZED', '已确认'],
  ['SUPERSEDED', '已被替代'],
  ['PAY', '缴费'],
  ['CREATED', '已创建'],
  ['NOT_CREATED', '未创建'],
  ['UNPAID', '未缴费'],
  ['NOT_APPLICABLE', '不适用'],
  ['PAY_LIST', '缴费清单'],
]) {
  assert.match(lifecycleDisplay, new RegExp(`${code}: '${label}'`))
}

assert.equal(govPaymentMoney.toDemoMoney(50), '50.00')
assert.equal(govPaymentMoney.toDemoMoney('900.00'), '900.00')
assert.equal(billItems.serviceItemAmountsEqualBill(['1200.00', '600.00'], '1800.00'), true)
assert.equal(billItems.serviceItemAmountsEqualBill(['1200.00', '500.00'], '1800.00'), false)
assert.equal(billItems.serviceItemAmountsEqualBill([], '1800.00'), false)
assert.equal(billItems.serviceReceiptFeeCodeMatchesBill(undefined, ['BASE', 'ADDON']), true)
assert.equal(billItems.serviceReceiptFeeCodeMatchesBill('ADDON', ['BASE', 'ADDON']), true)
assert.equal(billItems.serviceReceiptFeeCodeMatchesBill('GOV', ['BASE', 'ADDON']), false)

const nullableServiceItem = { id: 'service-item-a', quantity: 0 }
const serviceSourceFacts = {
  fee_domain: 'SERVICE',
  lines: [{ current_item_id: 'service-item-a', quantity: 1 }],
}
assert.equal(adjustmentQuantity.resolveAdjustmentQuantity(nullableServiceItem, serviceSourceFacts), 1)
assert.equal(adjustmentQuantity.resolveAdjustmentQuantity(nullableServiceItem, null), 0)
assert.equal(adjustmentQuantity.resolveAdjustmentQuantity(nullableServiceItem, { ...serviceSourceFacts, fee_domain: 'GOV' }), 0)
const draftFactOpen = { kind: 'DRAFT', objectId: 'draft-a', status: 'OPEN' }
const draftFactLocked = { ...draftFactOpen, status: 'LOCKED' }
const paymentFact = { kind: 'PAYMENT', objectId: 'payment-a', status: 'PAID' }
const obligationV1 = { obligationId: 'obligation-a', marker: 'old', relatedFacts: [draftFactOpen, paymentFact] }
const obligationV2 = { obligationId: 'obligation-a', marker: 'latest', relatedFacts: [draftFactLocked] }
const obligationB = { obligationId: 'obligation-b', marker: 'only', relatedFacts: [] }
assert.deepEqual(feeLaneProjection.latestObligationsById([
  { feeObligations: [obligationV1] },
  { feeObligations: [obligationV2, obligationB] },
]), [{ ...obligationV2, relatedFacts: [draftFactLocked, paymentFact] }, obligationB])

const tuple = {
  contract_version: 'fpms.demo-v6-ui-parity/v1', run_id: 'run-1', candidate_commit: '1'.repeat(40),
  candidate_tree: '2'.repeat(40), authority_sha256: '3'.repeat(64), actor: 'HUMAN',
}
assert.equal(guards.canStartDemoServiceObligation(true, tuple, false, false), true)
assert.equal(guards.canStartDemoServiceObligation(false, tuple, false, false), false)
assert.equal(guards.canStartDemoServiceObligation(true, null, false, false), false)
assert.equal(guards.canStartDemoServiceObligation(true, tuple, true, false), false)

const noSessionCalls = serviceCalls.length
if (guards.canStartDemoServiceObligation(false, null, false)) {
  await demo.createValidatedDemoServiceObligation('case-a', 'service-intent-1')
}
assert.equal(serviceCalls.length, noSessionCalls)

const created = await demo.createValidatedDemoServiceObligation('case-a', 'service-intent-1')
assert.equal(created.item_code, serviceItem.item_code)
assert.equal(created.obligation.case_id, 'case-a')
assert.deepEqual(serviceCalls.slice(-2), [
  { method: 'GET', path: '/fees/demo-service-item' },
  {
    method: 'POST', path: '/fees/demo-service-obligations', caseId: 'case-a', key: 'service-intent-1',
  },
])

for (const invalidResult of [
  resultFor({ obligation: { ...resultFor().obligation, case_id: 'case-b' } }),
  resultFor({ item_code: 'DRIFTED_ITEM' }),
  resultFor({ amount: '1.00' }),
  resultFor({ idempotency_key: 'other-key' }),
]) {
  createValue = invalidResult
  const mutationsBefore = serviceCalls.filter((call) => call.method === 'POST').length
  await assert.rejects(demo.createValidatedDemoServiceObligation('case-a', 'service-intent-1'))
  assert.equal(serviceCalls.filter((call) => call.method === 'POST').length, mutationsBefore + 1)
}
itemValue = new Error('service item invalid')
const mutationsBeforeInvalidItem = serviceCalls.filter((call) => call.method === 'POST').length
await assert.rejects(demo.createValidatedDemoServiceObligation('case-a', 'service-intent-1'))
assert.equal(serviceCalls.filter((call) => call.method === 'POST').length, mutationsBeforeInvalidItem)

const handlerHarness = {
  pending: { value: false },
  attempted: { value: false },
  message: { value: '' },
  mutationError: { value: '' },
  refreshError: { value: '' },
  refreshedOverlay: { value: null },
  standaloneOverlay: { value: null },
  sessionEnabled: { value: true },
  managed: { value: true },
  overlay: { lifecycleRevision: 2 },
  refreshFailure: new Error('视图刷新失败'),
  postCount: 0,
  refreshCount: 0,
  draftRefreshCount: 0,
  lastOverlayQuery: null,
}
globalThis.__ordinal06HandlerHarness = handlerHarness
const handler = await importFunctions(
  script(caseFees),
  [
    'canStartDemoServiceObligation',
    'syncDemoSession',
    'errorMessage',
    'reloadDemoFeeView',
    'handleReloadDemoFeeView',
    'handleCreateDemoServiceObligation',
  ],
  `
    const harness = globalThis.__ordinal06HandlerHarness
    const demoObligationPending = harness.pending
    const demoObligationAttempted = harness.attempted
    const demoObligationMessage = harness.message
    const demoObligationError = harness.mutationError
    const demoRefreshError = harness.refreshError
    const demoRefreshedOverlay = harness.refreshedOverlay
    const standaloneOverlay = harness.standaloneOverlay
    const demoSessionEnabled = harness.sessionEnabled
    const isLifecycleOverlayManaged = harness.managed
    const props = { caseId: 'case-a' }
    const demoObligationIdempotencyKey = 'service-intent-1'
    const isDemoUiSessionActive = () => true
    const getDemoUiSession = () => ({ run_id: 'run-1' })
    const createValidatedDemoServiceObligation = async () => {
      harness.postCount += 1
      return { reused: false, name_zh_cn: '代理服务费', currency: 'CNY', amount: '1500.00' }
    }
    const getLifecycleOverlay = async (_caseId, query) => {
      harness.refreshCount += 1
      harness.lastOverlayQuery = query
      if (harness.refreshFailure) throw harness.refreshFailure
      return harness.overlay
    }
    const loadFeeDrafts = async () => { harness.draftRefreshCount += 1 }
  `,
)
await handler.handleCreateDemoServiceObligation()
await handler.handleCreateDemoServiceObligation()
assert.equal(handlerHarness.postCount, 1, 'a terminal mutation attempt must not issue a second POST')
assert.equal(handlerHarness.attempted.value, true)
assert.match(handlerHarness.message.value, /义务已生成/)
assert.equal(handlerHarness.mutationError.value, '')
assert.match(handlerHarness.refreshError.value, /视图刷新失败/)
assert.equal(guards.canStartDemoServiceObligation(true, tuple, false, true), false)

handlerHarness.refreshFailure = null
await handler.handleReloadDemoFeeView()
assert.equal(handlerHarness.postCount, 1)
assert.equal(handlerHarness.refreshCount, 2)
assert.equal(handlerHarness.draftRefreshCount, 2)
assert.equal(handlerHarness.refreshError.value, '')
assert.equal(handlerHarness.refreshedOverlay.value, handlerHarness.overlay)
assert.deepEqual(handlerHarness.lastOverlayQuery, { afterSequence: 0, limit: 200, asOfRevision: null })

handlerHarness.pending.value = false
handlerHarness.attempted.value = false
handlerHarness.message.value = ''
handlerHarness.refreshError.value = ''
handlerHarness.managed.value = false
await handler.handleCreateDemoServiceObligation()
assert.equal(handlerHarness.standaloneOverlay.value, handlerHarness.overlay)
assert.equal(handlerHarness.refreshedOverlay.value, handlerHarness.overlay)

const overlaySelection = await importFunctions(script(caseFees), ['selectActiveFeeOverlay'])
const rev1 = { lifecycleRevision: 1 }
const rev2 = { lifecycleRevision: 2 }
const rev3 = { lifecycleRevision: 3 }
const standalone = { lifecycleRevision: 4 }
assert.equal(overlaySelection.selectActiveFeeOverlay(true, rev1, null, rev2), rev2)
assert.equal(overlaySelection.selectActiveFeeOverlay(true, rev3, null, rev2), rev3)
assert.equal(overlaySelection.selectActiveFeeOverlay(false, null, standalone, rev2), standalone)

const rows = [
  { id: 1, pay_list_id: 7, fee_item_id: 'fee-1', status: 'PLANNED', planned_amt: 100, paid_amount: 0 },
  { id: 2, pay_list_id: 7, fee_item_id: 'fee-paid', status: 'PAID', planned_amt: 200, paid_amount: 200 },
  { id: 3, pay_list_id: 7, fee_item_id: 'fee-2', status: 'PLANNED', planned_amt: 300, paid_amount: 0 },
]
const registrationQuery = payListRoutes.buildPaymentRegistrationQuery(7, rows, rows[0])
assert.deepEqual(registrationQuery, {
  pay_list_id: '7', fee_item_id: 'fee-1', demo_command: '1', paid_amount: '100',
  next_fee_item_id: 'fee-2', next_paid_amount: '300',
})
assert.deepEqual(payListRoutes.buildPaymentRegistrationQuery(7, rows, rows[2]), {
  pay_list_id: '7', fee_item_id: 'fee-2', demo_command: '1', paid_amount: '300',
})

const navigation = paymentRoutes.buildPaymentResultNavigation(7, 'fee-2', 300)
assert.deepEqual(navigation, {
  currentList: { path: '/fee-management/pay-lists/7' },
  nextRow: {
    path: '/fee-management/gov-payments/new',
    query: { pay_list_id: '7', fee_item_id: 'fee-2', demo_command: '1', paid_amount: '300' },
  },
})
assert.deepEqual(paymentRoutes.buildPaymentResultNavigation(7, '', 0), {
  currentList: { path: '/fee-management/pay-lists/7' }, nextRow: null,
})
const consumedRouteQuery = navigation.nextRow.query
const afterNavigation = paymentRoutes.buildPaymentResultNavigation(
  Number(consumedRouteQuery.pay_list_id),
  consumedRouteQuery.next_fee_item_id || '',
  Number(consumedRouteQuery.next_paid_amount || 0),
)
assert.equal(afterNavigation.nextRow, null)
assert.equal(serviceCalls.filter((call) => call.method === 'POST').length, 5)

assert.match(caseFees, /生成服务费义务/)
assert.match(caseFees, /isDemoUiSessionActive\(\)/)
assert.match(caseFees, /getDemoUiSession\(\)/)
assert.match(caseFees, /:loading="demoObligationPending"/)
assert.match(caseFees, /重新加载费用视图/)
assert.doesNotMatch(demoAbc, /createDemoServiceObligation\([\s\S]{0,160}bundle\.value!\.item_code/)
assert.match(payment, /登记下一行/)
assert.match(payment, /返回当前清单/)
assert.match(payment, /parseQueryText\(route\.query\.next_fee_item_id\)/)
assert.doesNotMatch(caseFees + payment, /<el-input[^>]+(?:obligationId|itemCode|payListId|feeItemId|义务ID|项目代码|清单ID|费用项ID)/i)
assert.match(feeDetail, /调整前摘要：sha256:\{\{ row\.adjustment_before_digest \}\}/)
assert.match(feeDetail, /调整后摘要：sha256:\{\{ row\.adjustment_after_digest \}\}/)

delete globalThis.__ordinal06ReadItem
delete globalThis.__ordinal06Create
delete globalThis.__ordinal06HandlerHarness
console.log('demo V6 fee UI parity contract: PASS')
