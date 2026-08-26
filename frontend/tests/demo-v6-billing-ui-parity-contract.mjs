import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { readFile } from 'node:fs/promises'
import ts from 'typescript'

const contractSource = await readFile(
  new URL('../src/modules/demo/demo.contract.ts', import.meta.url),
  'utf8',
)
const compiledContract = ts.transpileModule(contractSource, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
}).outputText
const contract = await import(
  `data:text/javascript;base64,${Buffer.from(compiledContract).toString('base64')}`
)

const ids = {
  bill: '11111111-1111-4111-8111-111111111111',
  client: '22222222-2222-4222-8222-222222222222',
  case: '33333333-3333-4333-8333-333333333333',
  draft: '44444444-4444-4444-8444-444444444444',
  item: '55555555-5555-4555-8555-555555555555',
  payment1: '66666666-6666-4666-8666-666666666666',
  line1: '77777777-7777-4777-8777-777777777777',
  offset1: '88888888-8888-4888-8888-888888888888',
  receipt: '99999999-9999-4999-8999-999999999999',
  payment2: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
  line2: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
  offset2: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
}

const billFor = (status, balance) => ({
  id: ids.bill,
  bill_no: 'SERVICE-AR-1800',
  client_id: ids.client,
  case_id: ids.case,
  currency: 'CNY',
  direction: 'AR',
  status,
  total_gov: '0.00',
  total_service: '1800.00',
  total_misc: '0.00',
  amount: '1800.00',
  balance,
  bill_date: '2026-08-26',
  due_date: '2026-09-26',
  source_draft_ids: [ids.draft],
  items: [{ id: ids.item, fee_type: 'SERVICE', fee_code: 'SERVICE_FEE', amount: '1800.00' }],
})

const unsettledBill = billFor('UNSETTLED', '1800.00')
const partiallySettledBill = billFor('PARTIALLY_SETTLED', '600.00')
const settledBill = billFor('SETTLED', '0.00')

assert.deepEqual(contract.parseDemoBillDetail(structuredClone(unsettledBill)), unsettledBill)
assert.deepEqual(
  contract.parseDemoBillDetail(structuredClone(partiallySettledBill)),
  partiallySettledBill,
)
assert.deepEqual(contract.parseDemoBillDetail(structuredClone(settledBill)), settledBill)

for (const invalid of [
  billFor('UNSETTLED', '600.00'),
  billFor('PARTIALLY_SETTLED', '1800.00'),
  billFor('PARTIALLY_SETTLED', '0.00'),
  billFor('SETTLED', '600.00'),
]) {
  assert.throws(
    () => contract.parseDemoBillDetail(invalid),
    (error) => error?.code === 'FINANCE_CONTRACT_INVALID',
  )
}

function paymentResponse(sequence, amount, bill) {
  const paymentId = sequence === 1 ? ids.payment1 : ids.payment2
  const lineId = sequence === 1 ? ids.line1 : ids.line2
  return {
    payment: {
      id: paymentId,
      pay_no: `SERVICE-PAY-${sequence}`,
      client_id: ids.client,
      pay_date: '2026-08-26',
      currency: 'CNY',
      amount,
      pay_method: 'BANK_TRANSFER',
      bank_ref_no: `SERVICE-BANK-${sequence}`,
    },
    line: {
      id: lineId,
      payment_id: paymentId,
      case_id: ids.case,
      raw_amount: amount,
      allocated_amt: '0.00',
      balance_amt: amount,
      status: 'UNALLOCATED',
    },
    bill,
    target_bill_id: ids.bill,
    idempotency_key: `payment-intent-${sequence}`,
    reused: false,
  }
}

const firstPayment = paymentResponse(1, '1200.00', unsettledBill)
const secondPayment = paymentResponse(2, '600.00', partiallySettledBill)
assert.deepEqual(contract.parseDemoBankReceiptResponse(structuredClone(firstPayment)), firstPayment)
assert.deepEqual(contract.parseDemoBankReceiptResponse(structuredClone(secondPayment)), secondPayment)
assert.equal(firstPayment.bill.balance, '1800.00', 'receipt alone must not change bill balance')

function offsetResponse(sequence, amount, bill, receivedAmount) {
  const payment = sequence === 1 ? firstPayment : secondPayment
  return {
    offset: {
      id: sequence === 1 ? ids.offset1 : ids.offset2,
      payment_line_id: payment.line.id,
      bill_id: ids.bill,
      offset_amt: amount,
      offset_date: '2026-08-26',
      is_reversed: false,
    },
    bill,
    line: {
      ...payment.line,
      allocated_amt: amount,
      balance_amt: '0.00',
      status: 'FULLY_ALLOCATED',
    },
    case_receipt: {
      id: ids.receipt,
      case_id: ids.case,
      fee_type: 'SERVICE',
      fee_code: 'SERVICE_FEE',
      currency: 'CNY',
      receivable_amt: '1800.00',
      received_amt: receivedAmount,
      last_receipt_date: '2026-08-26',
    },
    idempotency_key: `offset-intent-${sequence}`,
    reused: false,
  }
}

const firstOffset = offsetResponse(1, '1200.00', partiallySettledBill, '1200.00')
const secondOffset = offsetResponse(2, '600.00', settledBill, '1800.00')
assert.deepEqual(contract.parseDemoOffsetResponse(structuredClone(firstOffset)), firstOffset)
assert.deepEqual(contract.parseDemoOffsetResponse(structuredClone(secondOffset)), secondOffset)

const readSource = async (path) => readFile(new URL(`../${path}`, import.meta.url), 'utf8')
const billPage = await readSource('src/modules/billing/pages/BillCreate.vue')
const paymentPage = await readSource('src/modules/billing/pages/PaymentCreate.vue')
const paymentListPage = await readSource('src/modules/billing/pages/PaymentList.vue')
const demoApiSource = await readSource('src/modules/demo/demo.api.ts')
const script = (source) => source.split('<script setup lang="ts">', 2)[1].split('</script>', 1)[0]

async function importFunctions(source, names, prelude = '') {
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

const serviceDraft = {
  id: ids.draft,
  case_id: ids.case,
  client_id: ids.client,
  currency: 'CNY',
  status: 'LOCKED',
  total_gov: '0.00',
  total_service: '1800.00',
  total_misc: '0.00',
  amount: '1800.00',
}
const govDraft = { ...serviceDraft, id: ids.item, total_gov: '1800.00', total_service: '0.00' }
const session = { run_id: 'run-1' }
const billUi = await importFunctions(
  script(billPage),
  ['isEligibleDemoServiceDraft', 'selectDemoServiceDraft', 'canCreateDemoBill'],
)
assert.equal(billUi.selectDemoServiceDraft([serviceDraft, govDraft], ids.draft), serviceDraft)
assert.equal(billUi.selectDemoServiceDraft([serviceDraft, { ...serviceDraft, id: ids.item }], ids.draft), null)
assert.equal(billUi.selectDemoServiceDraft([govDraft], ids.item), null)
assert.equal(
  billUi.canCreateDemoBill(true, session, serviceDraft, 'SERVICE-AR-1800', '2026-08-26', '2026-09-26', false),
  true,
)
assert.equal(
  billUi.canCreateDemoBill(false, null, serviceDraft, 'SERVICE-AR-1800', '2026-08-26', '2026-09-26', false),
  false,
)

const paymentUi = await importFunctions(script(paymentPage), ['canCreateDemoPayment'])
assert.equal(
  paymentUi.canCreateDemoPayment(true, session, unsettledBill, ids.bill, '1200.00', 'SERVICE-PAY-1', '2026-08-26', 'BANK-1', '首次回款', false),
  true,
)
let rejectedUnsettledMutations = 0
for (const amount of ['1000.00', '1800.00']) {
  if (paymentUi.canCreateDemoPayment(
    true,
    session,
    unsettledBill,
    ids.bill,
    amount,
    'SERVICE-PAY-1',
    '2026-08-26',
    'BANK-1',
    '首次回款',
    false,
  )) rejectedUnsettledMutations += 1
}
assert.equal(rejectedUnsettledMutations, 0)
assert.equal(
  paymentUi.canCreateDemoPayment(true, session, partiallySettledBill, ids.bill, '600.00', 'SERVICE-PAY-2', '2026-08-26', 'BANK-2', '尾款', false),
  true,
)
assert.equal(
  paymentUi.canCreateDemoPayment(true, session, partiallySettledBill, ids.bill, '1200.00', 'SERVICE-PAY-2', '2026-08-26', 'BANK-2', '尾款', false),
  false,
)
assert.equal(
  paymentUi.canCreateDemoPayment(true, session, partiallySettledBill, ids.bill, '300.00', 'SERVICE-PAY-2', '2026-08-26', 'BANK-2', '尾款', false),
  false,
)
assert.equal(
  paymentUi.canCreateDemoPayment(true, session, partiallySettledBill, ids.item, '600.00', 'SERVICE-PAY-2', '2026-08-26', 'BANK-2', '尾款', false),
  false,
)

const offsetUi = await importFunctions(script(paymentListPage), ['canCreateDemoOffset'])
assert.equal(
  offsetUi.canCreateDemoOffset(true, session, firstPayment, ids.payment1, ids.line1, ids.bill, '1200.00', '2026-08-26', false),
  true,
)
assert.equal(
  offsetUi.canCreateDemoOffset(true, session, firstPayment, ids.payment1, ids.line1, ids.bill, '600.00', '2026-08-26', false),
  false,
)
assert.equal(
  offsetUi.canCreateDemoOffset(true, session, firstPayment, ids.payment2, ids.line1, ids.bill, '1200.00', '2026-08-26', false),
  false,
)

const helperSource = await readSource('src/modules/demo/command-reconcile.ts')
const compiledHelper = ts.transpileModule(helperSource, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
}).outputText
const commandHelper = await import(
  `data:text/javascript;base64,${Buffer.from(compiledHelper).toString('base64')}`
)

const apiHarness = {
  calls: [],
  billResult: { bill: unsettledBill, idempotency_key: 'bill-intent-1', reused: false },
  paymentResults: [firstPayment, secondPayment],
  offsetResults: [firstOffset, secondOffset],
  paymentIndex: 0,
  offsetIndex: 0,
  committedAfterDrop: null,
  deterministicError: null,
}
globalThis.__ordinal07ApiHarness = apiHarness
globalThis.__ordinal07Contract = contract
globalThis.__ordinal07CommandHelper = commandHelper
const api = await importFunctions(
  demoApiSource,
  [
    'readCommand',
    'reconcileUnknownCommand',
    'createDemoBill',
    'createDemoBankReceipt',
    'createDemoFullOffset',
  ],
  `
    const harness = globalThis.__ordinal07ApiHarness
    const parseDemoBillCommandResponse = globalThis.__ordinal07Contract.parseDemoBillCommandResponse
    const parseDemoBankReceiptResponse = globalThis.__ordinal07Contract.parseDemoBankReceiptResponse
    const parseDemoOffsetResponse = globalThis.__ordinal07Contract.parseDemoOffsetResponse
    const reconcileThenRetryMutationOnce = globalThis.__ordinal07CommandHelper.reconcileThenRetryMutationOnce
    const resolveCommandMutationResponse = globalThis.__ordinal07CommandHelper.resolveCommandMutationResponse
    const http = {
      post: async (path, payload) => {
        harness.calls.push({ method: 'POST', path, payload })
        if (harness.deterministicError) throw harness.deterministicError
        if (path === '/bills/demo-from-draft') {
          if (harness.committedAfterDrop) throw { status: 0, code: 'UNKNOWN_ERROR' }
          return { status: 200, data: harness.billResult }
        }
        if (path === '/payments/demo-bank-receipts') {
          return { status: 200, data: harness.paymentResults[harness.paymentIndex++] }
        }
        return { status: 200, data: harness.offsetResults[harness.offsetIndex++] }
      },
      get: async (path) => {
        harness.calls.push({ method: 'GET', path })
        return harness.committedAfterDrop
          ? { status: 200, data: harness.committedAfterDrop }
          : { status: 404, data: {} }
      },
    }
  `,
)

await api.createDemoBill(ids.draft, 'SERVICE-AR-1800', '2026-08-26', '2026-09-26', 'bill-intent-1')
await api.createDemoBankReceipt(
  unsettledBill,
  'SERVICE-PAY-1',
  'SERVICE-BANK-1',
  '2026-08-26',
  'payment-intent-1',
  '1200.00',
  '首次回款',
)
await api.createDemoFullOffset(firstPayment.line, unsettledBill, '2026-08-26', 'offset-intent-1', '1200.00')
await api.createDemoBankReceipt(
  partiallySettledBill,
  'SERVICE-PAY-2',
  'SERVICE-BANK-2',
  '2026-08-26',
  'payment-intent-2',
  '600.00',
  '尾款',
)
await api.createDemoFullOffset(secondPayment.line, partiallySettledBill, '2026-08-26', 'offset-intent-2', '600.00')

const mutations = apiHarness.calls.filter((call) => call.method === 'POST')
assert.deepEqual(mutations.map((call) => call.path), [
  '/bills/demo-from-draft',
  '/payments/demo-bank-receipts',
  '/offsets/demo-full',
  '/payments/demo-bank-receipts',
  '/offsets/demo-full',
])
assert.equal(mutations[1].payload.amount, '1200.00')
assert.equal(mutations[1].payload.remark, '首次回款')
assert.equal(mutations[3].payload.amount, '600.00')
assert.equal(mutations[2].payload.offset_amt, '1200.00')
assert.equal(mutations[4].payload.offset_amt, '600.00')
assert.equal(new Set(mutations.map((call) => call.payload.idempotency_key)).size, 5)

const callsBeforeRecovery = apiHarness.calls.length
apiHarness.committedAfterDrop = {
  bill: unsettledBill,
  idempotency_key: 'bill-recovery-intent',
  reused: true,
}
const recovered = await api.createDemoBill(
  ids.draft,
  'SERVICE-AR-1800',
  '2026-08-26',
  '2026-09-26',
  'bill-recovery-intent',
)
assert.equal(recovered.reused, true)
assert.deepEqual(apiHarness.calls.slice(callsBeforeRecovery).map(({ method }) => method), ['POST', 'GET'])

apiHarness.committedAfterDrop = null
apiHarness.deterministicError = { status: 409, code: 'DEMO_FINANCE_IDEMPOTENCY_CONFLICT' }
const readsBeforeDrift = apiHarness.calls.filter((call) => call.method === 'GET').length
await assert.rejects(
  api.createDemoBill(ids.draft, 'DRIFT', '2026-08-26', '2026-09-26', 'bill-intent-1'),
)
assert.equal(apiHarness.calls.filter((call) => call.method === 'GET').length, readsBeforeDrift)

assert.match(billPage, /服务费草稿/)
assert.match(billPage, /账单编号/)
assert.match(billPage, /账单日期/)
assert.match(billPage, /到期日期/)
assert.match(paymentPage, /银行流水参考号/)
assert.match(paymentPage, /getBillStatusText\(demoSelectedBill\.status\)/)
assert.match(paymentListPage, /getBillStatusText\(demoOffsetResult\.bill\.status\)/)
assert.doesNotMatch(paymentPage, /\$\{demoSelectedBill\.status\}/)
assert.doesNotMatch(paymentListPage, /\$\{demoOffsetResult\.bill\.status\}/)
assert.match(
  paymentListPage,
  /<el-form-item\s+v-if="demoSessionEnabled"\s+label="核销日期"/,
)

const displayTextSource = await readSource('src/constants/displayText.ts')
const compiledDisplayText = ts.transpileModule(displayTextSource, {
  compilerOptions: { module: ts.ModuleKind.ES2022, target: ts.ScriptTarget.ES2022 },
}).outputText
const displayText = await import(
  `data:text/javascript;base64,${Buffer.from(compiledDisplayText).toString('base64')}`
)
assert.equal(displayText.getBillStatusText('UNSETTLED'), '未结清')
assert.equal(displayText.getBillStatusText('PARTIALLY_SETTLED'), '部分结清')
assert.equal(displayText.getBillStatusText('SETTLED'), '已结清')
assert.doesNotMatch(billPage + paymentPage + paymentListPage, /<el-input[^>]+(?:bill_id|draft_id|payment_line_id)/i)

delete globalThis.__ordinal07ApiHarness
delete globalThis.__ordinal07Contract
delete globalThis.__ordinal07CommandHelper

console.log('demo V6 billing UI parity contract: PASS')
