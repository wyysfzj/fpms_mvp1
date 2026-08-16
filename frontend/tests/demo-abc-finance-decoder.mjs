import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { readFile } from 'node:fs/promises'
import ts from 'typescript'

const sourceUrl = new URL('../src/modules/demo/demo.contract.ts', import.meta.url)
const source = await readFile(sourceUrl, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ES2022,
    target: ts.ScriptTarget.ES2022,
  },
}).outputText
const contract = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`)

const baseBill = {
  id: '11111111-1111-4111-8111-111111111111',
  bill_no: 'DEMO-AR-1',
  client_id: '22222222-2222-4222-8222-222222222222',
  case_id: '33333333-3333-4333-8333-333333333333',
  currency: 'CNY',
  direction: 'AR',
  status: 'UNSETTLED',
  total_gov: '0.00',
  total_service: '1200.00',
  total_misc: '0.00',
  amount: '1200.00',
  balance: '1200.00',
  bill_date: '2026-08-17',
  due_date: '2026-08-31',
  source_draft_ids: ['44444444-4444-4444-8444-444444444444'],
  items: [
    {
      id: '55555555-5555-4555-8555-555555555555',
      fee_type: 'SERVICE',
      amount: '1200.00',
    },
  ],
}

assert.deepEqual(contract.parseDemoBillDetail(structuredClone(baseBill)), baseBill)
const largeExact = {
  ...structuredClone(baseBill),
  total_service: '9007199254740993.01',
  amount: '9007199254740993.01',
  balance: '9007199254740993.01',
  items: [{ ...baseBill.items[0], amount: '9007199254740993.01' }],
}
assert.equal(
  contract.parseDemoBillDetail(largeExact).amount,
  '9007199254740993.01',
)

for (const bad of [null, undefined, '', 'NaN', 'Infinity', 1200, '1', '1.0', '-1.00']) {
  assert.throws(
    () => contract.parseDemoBillDetail({ ...structuredClone(baseBill), amount: bad }),
    (error) => error?.code === 'FINANCE_CONTRACT_INVALID',
  )
}

for (const mutation of [
  { id: 'not-a-uuid' },
  { currency: null },
  { currency: 'USD' },
  { status: 'PAID' },
  { direction: 'AP' },
  { source_draft_ids: [null] },
  { bill_date: '2026-02-30' },
  { due_date: '2026-13-01' },
  { total_service: '1100.00' },
  { total_gov: '1.00' },
  { balance: '0.00' },
]) {
  assert.throws(
    () => contract.parseDemoBillDetail({ ...structuredClone(baseBill), ...mutation }),
    (error) => error?.code === 'FINANCE_CONTRACT_INVALID',
  )
}

const paymentResponse = {
  payment: {
    id: '66666666-6666-4666-8666-666666666666',
    pay_no: 'DEMO-PAY-1',
    client_id: baseBill.client_id,
    pay_date: '2026-08-17',
    currency: 'CNY',
    amount: '1200.00',
    pay_method: 'BANK_TRANSFER',
    bank_ref_no: 'DEMO-BANK-1',
  },
  line: {
    id: '77777777-7777-4777-8777-777777777777',
    payment_id: '66666666-6666-4666-8666-666666666666',
    case_id: baseBill.case_id,
    raw_amount: '1200.00',
    allocated_amt: '0.00',
    balance_amt: '1200.00',
    status: 'UNALLOCATED',
  },
  bill: baseBill,
  target_bill_id: baseBill.id,
  idempotency_key: 'payment-intent-1',
  reused: false,
}
assert.deepEqual(contract.parseDemoBankReceiptResponse(paymentResponse), paymentResponse)
assert.throws(
  () => contract.parseDemoBankReceiptResponse({ ...paymentResponse, line: { ...paymentResponse.line, status: 'PARTIAL' } }),
  (error) => error?.code === 'FINANCE_CONTRACT_INVALID',
)

for (const mutation of [
  { line: { ...paymentResponse.line, payment_id: '88888888-8888-4888-8888-888888888888' } },
  { line: { ...paymentResponse.line, case_id: '88888888-8888-4888-8888-888888888888' } },
  { line: { ...paymentResponse.line, raw_amount: '1199.00' } },
  { payment: { ...paymentResponse.payment, client_id: '88888888-8888-4888-8888-888888888888' } },
  { payment: { ...paymentResponse.payment, pay_date: '2026-02-30' } },
  { target_bill_id: '88888888-8888-4888-8888-888888888888' },
]) {
  assert.throws(
    () => contract.parseDemoBankReceiptResponse({ ...structuredClone(paymentResponse), ...mutation }),
    (error) => error?.code === 'FINANCE_CONTRACT_INVALID',
  )
}

const settledBill = {
  ...structuredClone(baseBill),
  status: 'SETTLED',
  balance: '0.00',
}
const offsetResponse = {
  offset: {
    id: '88888888-8888-4888-8888-888888888888',
    payment_line_id: paymentResponse.line.id,
    bill_id: settledBill.id,
    offset_amt: '1200.00',
    offset_date: '2026-08-17',
    is_reversed: false,
  },
  bill: settledBill,
  line: {
    ...paymentResponse.line,
    allocated_amt: '1200.00',
    balance_amt: '0.00',
    status: 'FULLY_ALLOCATED',
  },
  case_receipt: {
    id: '99999999-9999-4999-8999-999999999999',
    case_id: settledBill.case_id,
    fee_type: 'SERVICE',
    fee_code: 'DEMO_SERVICE_1',
    currency: 'CNY',
    receivable_amt: '1200.00',
    received_amt: '1200.00',
    last_receipt_date: '2026-08-17',
  },
  idempotency_key: 'offset-intent-1',
  reused: false,
}
assert.deepEqual(contract.parseDemoOffsetResponse(structuredClone(offsetResponse)), offsetResponse)

for (const mutation of [
  { offset: { ...offsetResponse.offset, payment_line_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa' } },
  { offset: { ...offsetResponse.offset, bill_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa' } },
  { offset: { ...offsetResponse.offset, offset_date: '2025-02-29' } },
  { offset: { ...offsetResponse.offset, is_reversed: true } },
  { line: { ...offsetResponse.line, case_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa' } },
  { line: { ...offsetResponse.line, allocated_amt: '1199.00' } },
  { bill: { ...offsetResponse.bill, status: 'UNSETTLED' } },
  { case_receipt: { ...offsetResponse.case_receipt, case_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa' } },
  { case_receipt: { ...offsetResponse.case_receipt, received_amt: '1199.00' } },
  { case_receipt: { ...offsetResponse.case_receipt, last_receipt_date: '2026-08-18' } },
]) {
  assert.throws(
    () => contract.parseDemoOffsetResponse({ ...structuredClone(offsetResponse), ...mutation }),
    (error) => error?.code === 'FINANCE_CONTRACT_INVALID',
  )
}

console.log('demo ABC finance decoder contract OK')
