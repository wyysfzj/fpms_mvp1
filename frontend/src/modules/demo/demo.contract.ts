export class FinanceContractError extends Error {
  readonly code = 'FINANCE_CONTRACT_INVALID'

  constructor(path: string) {
    super(`财务响应契约无效：${path}`)
    this.name = 'FinanceContractError'
  }
}

type JsonRecord = Record<string, unknown>

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
const MONEY = /^(?:0|[1-9]\d*)\.\d{2}$/
const SHA256 = /^[0-9a-f]{64}$/
const DATE = /^\d{4}-\d{2}-\d{2}$/

export const DEMO_UI_PARITY_SCHEMA_ID = 'fpms.demo-v6-ui-parity/v1'

// Frozen from Ordinal 02: sorted(Base.metadata.tables - SYSTEM_RUNTIME_TABLE_ALLOWLIST).
export const DEMO_BUSINESS_COUNT_KEYS = [
  't_annuity_task',
  't_applicant',
  't_bad_debt_recovery',
  't_bad_debt_voucher',
  't_bill',
  't_bill_draft_source',
  't_bill_item',
  't_bio_deposit',
  't_case',
  't_case_activity_event',
  't_case_activity_event_conflict',
  't_case_activity_event_evidence',
  't_case_agent_split',
  't_case_applicant',
  't_case_inventor',
  't_case_receipt',
  't_client',
  't_client_address',
  't_client_contact',
  't_commission',
  't_commission_rule',
  't_commission_settle_line',
  't_commission_settlement',
  't_country',
  't_customer_decision_gate',
  't_demo_finance_command',
  't_demo_offset_command',
  't_demo_payment_command',
  't_department',
  't_doc_attachment',
  't_doc_dispatch',
  't_doc_dispatch_line',
  't_document',
  't_document_evidence_derivation',
  't_document_evidence_version',
  't_dunning',
  't_dunning_line',
  't_expense',
  't_fee_draft',
  't_fee_item',
  't_fee_obligation',
  't_fee_obligation_draft_item_link',
  't_fee_obligation_line',
  't_fee_obligation_payment_evidence_link',
  't_fee_reduction_approval',
  't_format_letter_mapping',
  't_future_annuity_draft_exception_record',
  't_future_annuity_reduction_lineage',
  't_gov_payment',
  't_grant_evidence_candidate',
  't_grant_evidence_source_config',
  't_grant_evidence_source_record',
  't_grant_fee_task',
  't_grant_manual_review_role_config',
  't_grant_official_copy_verification_event',
  't_legacy_fee_reduction_provenance',
  't_letter_handoff',
  't_letter_handoff_attachment',
  't_letter_head',
  't_official_fee_checklist',
  't_official_payment_workbook_input_version',
  't_official_work_package',
  't_official_work_package_checklist',
  't_official_work_package_manifest',
  't_official_work_package_override',
  't_official_work_package_receipt',
  't_offset',
  't_pay_list',
  't_pay_list_export_artifact',
  't_payment',
  't_payment_line',
  't_priority',
  't_service_price_book',
  't_system_param',
  't_task',
  't_task_log',
  't_template',
] as const

export type DemoBusinessCountKey = (typeof DEMO_BUSINESS_COUNT_KEYS)[number]

function invalid(path: string): never {
  throw new FinanceContractError(path)
}

function record(value: unknown, path: string): JsonRecord {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) invalid(path)
  return value as JsonRecord
}

function string(value: unknown, path: string): string {
  if (typeof value !== 'string' || value.length === 0 || value.includes('\0')) invalid(path)
  return value
}

function optionalString(value: unknown, path: string): string | undefined {
  if (value === undefined || value === null) return undefined
  return string(value, path)
}

function id(value: unknown, path: string): string {
  const parsed = string(value, path)
  if (!UUID.test(parsed)) invalid(path)
  return parsed
}

function money(value: unknown, path: string): string {
  if (typeof value !== 'string' || !MONEY.test(value)) invalid(path)
  return value
}

function digest(value: unknown, path: string): string {
  const parsed = string(value, path)
  if (!SHA256.test(parsed)) invalid(path)
  return parsed
}

function date(value: unknown, path: string): string {
  const parsed = string(value, path)
  if (!DATE.test(parsed)) invalid(path)
  const [year, month, day] = parsed.split('-').map(Number)
  const leap = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  if (month < 1 || month > 12 || day < 1 || day > days[month - 1]) invalid(path)
  return parsed
}

function equal(actual: string, expected: string, path: string): void {
  if (actual !== expected) invalid(path)
}

function literal<T extends string>(value: unknown, allowed: readonly T[], path: string): T {
  if (typeof value !== 'string' || !allowed.includes(value as T)) invalid(path)
  return value as T
}

function boolean(value: unknown, path: string): boolean {
  if (typeof value !== 'boolean') invalid(path)
  return value
}

function count(value: unknown, path: string): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < 0) invalid(path)
  return value
}

function stringArray(value: unknown, path: string, item: (value: unknown, path: string) => string): string[] {
  if (!Array.isArray(value)) invalid(path)
  return value.map((entry, index) => item(entry, `${path}[${index}]`))
}

export interface DemoServiceItem {
  classification: 'DEMO_ONLY'
  bundle_id: string
  bundle_version: string
  manifest_sha256: string
  template_code: string
  template_sha256: string
  template_required_variables: string[]
  item_code: string
  name_zh_cn: string
  currency: 'CNY'
  amount: string
  source_ref: string
  source_version: string
  source_sha256: string
  disclaimer_zh_cn: string
}

export interface DemoFeeObligationResponse extends DemoServiceItem {
  obligation: { id: string }
  source_activity_id: string
  idempotency_key: string
  reused: boolean
}

export interface DemoPreflight extends DemoServiceItem {
  authority_classification: 'SYNTHETIC_TEST_ONLY' | 'CUSTOMER_AUTHORIZED'
  customer_activation_eligible: boolean
  readiness: 'READY'
  run_id: string | null
  candidate_commit: string | null
  candidate_tree: string | null
  authority_sha256: string
  contract_version: typeof DEMO_UI_PARITY_SCHEMA_ID | null
  business_counts: Record<DemoBusinessCountKey, number>
}

export interface DemoUiSessionPreflight extends DemoPreflight {
  authority_classification: 'SYNTHETIC_TEST_ONLY'
  customer_activation_eligible: false
  run_id: string
  candidate_commit: string
  candidate_tree: string
  contract_version: typeof DEMO_UI_PARITY_SCHEMA_ID
}

export interface DemoDraft {
  id: string
  case_id: string
  client_id: string
  currency: 'CNY'
  status: 'OPEN' | 'LOCKED'
  total_gov: string
  total_service: string
  total_misc: string
  amount: string
}

export interface DemoBillDetail {
  id: string
  bill_no: string
  client_id: string
  case_id: string
  currency: 'CNY'
  direction: 'AR'
  status: 'UNSETTLED' | 'PARTIALLY_SETTLED' | 'SETTLED'
  total_gov: string
  total_service: string
  total_misc: string
  amount: string
  balance: string
  bill_date: string
  due_date?: string
  source_draft_ids: string[]
  items: Array<{ id: string; fee_type: 'SERVICE'; fee_code: string; amount: string }>
}

export interface DemoPaymentLine {
  id: string
  payment_id: string
  case_id: string
  raw_amount: string
  allocated_amt: string
  balance_amt: string
  status: 'UNALLOCATED' | 'FULLY_ALLOCATED'
}

export interface DemoBankReceiptResponse {
  payment: {
    id: string
    pay_no: string
    client_id: string
    pay_date: string
    currency: 'CNY'
    amount: string
    pay_method: 'BANK_TRANSFER'
    bank_ref_no: string
  }
  line: DemoPaymentLine
  bill: DemoBillDetail
  target_bill_id: string
  idempotency_key: string
  reused: boolean
}

export interface DemoOffsetResponse {
  offset: {
    id: string
    payment_line_id: string
    bill_id: string
    offset_amt: string
    offset_date: string
    is_reversed: boolean
  }
  bill: DemoBillDetail
  line: DemoPaymentLine
  case_receipt: {
    id: string
    case_id: string
    fee_type: 'SERVICE'
    fee_code: string
    currency: 'CNY'
    receivable_amt: string
    received_amt: string
    last_receipt_date: string
  }
  idempotency_key: string
  reused: boolean
}

export interface DemoBillCommandResponse {
  bill: DemoBillDetail
  idempotency_key: string
  reused: boolean
}

export function parseDemoServiceItem(value: unknown): DemoServiceItem {
  const raw = record(value, 'service_item')
  let row = raw
  if (Array.isArray(raw.items)) {
    const primary = record(raw.items[0], 'service_item.items[0]')
    row = { ...raw, ...primary, amount: raw.total_amount }
  }
  literal(row.classification, ['DEMO_ONLY'], 'service_item.classification')
  string(row.bundle_id, 'service_item.bundle_id')
  string(row.bundle_version, 'service_item.bundle_version')
  digest(row.manifest_sha256, 'service_item.manifest_sha256')
  string(row.template_code, 'service_item.template_code')
  digest(row.template_sha256, 'service_item.template_sha256')
  stringArray(row.template_required_variables, 'service_item.template_required_variables', string)
  string(row.item_code, 'service_item.item_code')
  string(row.name_zh_cn, 'service_item.name_zh_cn')
  literal(row.currency, ['CNY'], 'service_item.currency')
  money(row.amount, 'service_item.amount')
  string(row.source_ref, 'service_item.source_ref')
  string(row.source_version, 'service_item.source_version')
  digest(row.source_sha256, 'service_item.source_sha256')
  string(row.disclaimer_zh_cn, 'service_item.disclaimer_zh_cn')
  return row as unknown as DemoServiceItem
}

export function parseDemoPreflight(value: unknown): DemoPreflight {
  const normalized = parseDemoServiceItem(value)
  const row = record(normalized, 'demo_preflight')
  literal(
    row.authority_classification,
    ['SYNTHETIC_TEST_ONLY', 'CUSTOMER_AUTHORIZED'],
    'demo_preflight.authority_classification',
  )
  const customerEligible = boolean(
    row.customer_activation_eligible,
    'demo_preflight.customer_activation_eligible',
  )
  literal(row.readiness, ['READY'], 'demo_preflight.readiness')
  digest(row.authority_sha256, 'demo_preflight.authority_sha256')
  const sessionIdentity = [
    row.run_id,
    row.candidate_commit,
    row.candidate_tree,
    row.contract_version,
  ]
  if (!sessionIdentity.every((entry) => entry === null)) {
    string(row.run_id, 'demo_preflight.run_id')
    const candidateCommit = string(row.candidate_commit, 'demo_preflight.candidate_commit')
    const candidateTree = string(row.candidate_tree, 'demo_preflight.candidate_tree')
    if (!/^[0-9a-f]{40}$/.test(candidateCommit)) invalid('demo_preflight.candidate_commit')
    if (!/^[0-9a-f]{40}$/.test(candidateTree)) invalid('demo_preflight.candidate_tree')
    literal(
      row.contract_version,
      [DEMO_UI_PARITY_SCHEMA_ID],
      'demo_preflight.contract_version',
    )
  }
  const counts = record(row.business_counts, 'demo_preflight.business_counts')
  if (Object.keys(counts).sort().join('|') !== DEMO_BUSINESS_COUNT_KEYS.join('|')) {
    invalid('demo_preflight.business_counts')
  }
  for (const key of DEMO_BUSINESS_COUNT_KEYS) {
    if (count(counts[key], `demo_preflight.business_counts.${key}`) !== 0) {
      invalid(`demo_preflight.business_counts.${key}`)
    }
  }
  if (
    (row.authority_classification === 'SYNTHETIC_TEST_ONLY' && customerEligible) ||
    (row.authority_classification === 'CUSTOMER_AUTHORIZED' && !customerEligible)
  ) {
    invalid('demo_preflight.customer_activation_eligible')
  }
  return normalized as DemoPreflight
}

export function parseDemoUiSessionPreflight(value: unknown): DemoUiSessionPreflight {
  const normalized = parseDemoPreflight(value)
  if (
    normalized.authority_classification !== 'SYNTHETIC_TEST_ONLY' ||
    normalized.customer_activation_eligible ||
    normalized.run_id === null ||
    normalized.candidate_commit === null ||
    normalized.candidate_tree === null ||
    normalized.contract_version !== DEMO_UI_PARITY_SCHEMA_ID
  ) {
    invalid('demo_ui_session_preflight')
  }
  return normalized as DemoUiSessionPreflight
}

export function parseDemoFeeObligationResponse(value: unknown): DemoFeeObligationResponse {
  const normalized = parseDemoServiceItem(value)
  const row = record(normalized, 'obligation_response')
  id(record(row.obligation, 'obligation_response.obligation').id, 'obligation_response.obligation.id')
  id(row.source_activity_id, 'obligation_response.source_activity_id')
  string(row.idempotency_key, 'obligation_response.idempotency_key')
  boolean(row.reused, 'obligation_response.reused')
  return normalized as DemoFeeObligationResponse
}

export function parseDemoDraft(value: unknown): DemoDraft {
  const row = record(value, 'draft')
  id(row.id, 'draft.id')
  id(row.case_id, 'draft.case_id')
  id(row.client_id, 'draft.client_id')
  literal(row.currency, ['CNY'], 'draft.currency')
  literal(row.status, ['OPEN', 'LOCKED'], 'draft.status')
  for (const field of ['total_gov', 'total_service', 'total_misc', 'amount']) {
    money(row[field], `draft.${field}`)
  }
  return value as DemoDraft
}

export function parseDemoBillDetail(value: unknown): DemoBillDetail {
  const row = record(value, 'bill')
  id(row.id, 'bill.id')
  string(row.bill_no, 'bill.bill_no')
  id(row.client_id, 'bill.client_id')
  id(row.case_id, 'bill.case_id')
  literal(row.currency, ['CNY'], 'bill.currency')
  literal(row.direction, ['AR'], 'bill.direction')
  const status = literal(
    row.status,
    ['UNSETTLED', 'PARTIALLY_SETTLED', 'SETTLED'],
    'bill.status',
  )
  const totalGov = money(row.total_gov, 'bill.total_gov')
  const totalService = money(row.total_service, 'bill.total_service')
  const totalMisc = money(row.total_misc, 'bill.total_misc')
  const amount = money(row.amount, 'bill.amount')
  const balance = money(row.balance, 'bill.balance')
  const billDate = date(row.bill_date, 'bill.bill_date')
  const dueDate = optionalString(row.due_date, 'bill.due_date')
  if (dueDate !== undefined && date(dueDate, 'bill.due_date') < billDate) {
    invalid('bill.due_date')
  }
  const sourceDraftIds = stringArray(row.source_draft_ids, 'bill.source_draft_ids', id)
  if (sourceDraftIds.length !== 1) invalid('bill.source_draft_ids')
  if (!Array.isArray(row.items) || row.items.length !== 1) invalid('bill.items')
  const item = record(row.items[0], 'bill.items[0]')
  id(item.id, 'bill.items[0].id')
  literal(item.fee_type, ['SERVICE'], 'bill.items[0].fee_type')
  string(item.fee_code, 'bill.items[0].fee_code')
  const itemAmount = money(item.amount, 'bill.items[0].amount')
  equal(totalGov, '0.00', 'bill.total_gov')
  equal(totalMisc, '0.00', 'bill.total_misc')
  if (amount === '0.00') invalid('bill.amount')
  equal(totalService, amount, 'bill.total_service')
  equal(itemAmount, amount, 'bill.items[0].amount')
  if (status === 'UNSETTLED') {
    equal(balance, amount, 'bill.balance')
  } else if (status === 'PARTIALLY_SETTLED') {
    if (
      balance === '0.00' ||
      BigInt(balance.replace('.', '')) >= BigInt(amount.replace('.', ''))
    ) invalid('bill.balance')
  } else {
    equal(balance, '0.00', 'bill.balance')
  }
  return value as DemoBillDetail
}

function parseDemoPaymentLine(value: unknown): DemoPaymentLine {
  const row = record(value, 'payment_line')
  id(row.id, 'payment_line.id')
  id(row.payment_id, 'payment_line.payment_id')
  id(row.case_id, 'payment_line.case_id')
  money(row.raw_amount, 'payment_line.raw_amount')
  money(row.allocated_amt, 'payment_line.allocated_amt')
  money(row.balance_amt, 'payment_line.balance_amt')
  literal(row.status, ['UNALLOCATED', 'FULLY_ALLOCATED'], 'payment_line.status')
  return value as DemoPaymentLine
}

export function parseDemoBillCommandResponse(value: unknown): DemoBillCommandResponse {
  const row = record(value, 'bill_command')
  parseDemoBillDetail(row.bill)
  string(row.idempotency_key, 'bill_command.idempotency_key')
  boolean(row.reused, 'bill_command.reused')
  return value as DemoBillCommandResponse
}

export function parseDemoBankReceiptResponse(
  value: unknown,
  expectedAmount?: string,
): DemoBankReceiptResponse {
  const row = record(value, 'bank_receipt')
  const payment = record(row.payment, 'bank_receipt.payment')
  const paymentId = id(payment.id, 'bank_receipt.payment.id')
  string(payment.pay_no, 'bank_receipt.payment.pay_no')
  const clientId = id(payment.client_id, 'bank_receipt.payment.client_id')
  date(payment.pay_date, 'bank_receipt.payment.pay_date')
  literal(payment.currency, ['CNY'], 'bank_receipt.payment.currency')
  const paymentAmount = money(payment.amount, 'bank_receipt.payment.amount')
  literal(payment.pay_method, ['BANK_TRANSFER'], 'bank_receipt.payment.pay_method')
  string(payment.bank_ref_no, 'bank_receipt.payment.bank_ref_no')
  const line = parseDemoPaymentLine(row.line)
  const bill = parseDemoBillDetail(row.bill)
  const targetBillId = id(row.target_bill_id, 'bank_receipt.target_bill_id')
  string(row.idempotency_key, 'bank_receipt.idempotency_key')
  boolean(row.reused, 'bank_receipt.reused')
  equal(line.payment_id, paymentId, 'bank_receipt.line.payment_id')
  equal(line.case_id, bill.case_id, 'bank_receipt.line.case_id')
  equal(line.raw_amount, paymentAmount, 'bank_receipt.line.raw_amount')
  equal(line.allocated_amt, '0.00', 'bank_receipt.line.allocated_amt')
  equal(line.balance_amt, paymentAmount, 'bank_receipt.line.balance_amt')
  equal(line.status, 'UNALLOCATED', 'bank_receipt.line.status')
  equal(clientId, bill.client_id, 'bank_receipt.payment.client_id')
  if (expectedAmount !== undefined) {
    equal(paymentAmount, money(expectedAmount, 'bank_receipt.expected_amount'), 'bank_receipt.payment.amount')
  }
  if (BigInt(paymentAmount.replace('.', '')) > BigInt(bill.balance.replace('.', ''))) {
    invalid('bank_receipt.payment.amount')
  }
  equal(targetBillId, bill.id, 'bank_receipt.target_bill_id')
  if (bill.status === 'SETTLED') invalid('bank_receipt.bill.status')
  return value as DemoBankReceiptResponse
}

export function parseDemoOffsetResponse(value: unknown): DemoOffsetResponse {
  const row = record(value, 'offset_response')
  const offset = record(row.offset, 'offset_response.offset')
  id(offset.id, 'offset_response.offset.id')
  const paymentLineId = id(offset.payment_line_id, 'offset_response.offset.payment_line_id')
  const billId = id(offset.bill_id, 'offset_response.offset.bill_id')
  const offsetAmount = money(offset.offset_amt, 'offset_response.offset.offset_amt')
  const offsetDate = date(offset.offset_date, 'offset_response.offset.offset_date')
  const reversed = boolean(offset.is_reversed, 'offset_response.offset.is_reversed')
  const bill = parseDemoBillDetail(row.bill)
  const line = parseDemoPaymentLine(row.line)
  const receipt = record(row.case_receipt, 'offset_response.case_receipt')
  id(receipt.id, 'offset_response.case_receipt.id')
  const receiptCaseId = id(receipt.case_id, 'offset_response.case_receipt.case_id')
  literal(receipt.fee_type, ['SERVICE'], 'offset_response.case_receipt.fee_type')
  const receiptFeeCode = string(receipt.fee_code, 'offset_response.case_receipt.fee_code')
  literal(receipt.currency, ['CNY'], 'offset_response.case_receipt.currency')
  const receivableAmount = money(
    receipt.receivable_amt,
    'offset_response.case_receipt.receivable_amt',
  )
  const receivedAmount = money(
    receipt.received_amt,
    'offset_response.case_receipt.received_amt',
  )
  const receiptDate = date(
    receipt.last_receipt_date,
    'offset_response.case_receipt.last_receipt_date',
  )
  string(row.idempotency_key, 'offset_response.idempotency_key')
  boolean(row.reused, 'offset_response.reused')
  if (reversed) invalid('offset_response.offset.is_reversed')
  equal(paymentLineId, line.id, 'offset_response.offset.payment_line_id')
  equal(billId, bill.id, 'offset_response.offset.bill_id')
  equal(line.case_id, bill.case_id, 'offset_response.line.case_id')
  equal(line.raw_amount, offsetAmount, 'offset_response.line.raw_amount')
  equal(line.allocated_amt, offsetAmount, 'offset_response.line.allocated_amt')
  equal(line.balance_amt, '0.00', 'offset_response.line.balance_amt')
  equal(line.status, 'FULLY_ALLOCATED', 'offset_response.line.status')
  if (bill.status === 'UNSETTLED') invalid('offset_response.bill.status')
  equal(receiptCaseId, bill.case_id, 'offset_response.case_receipt.case_id')
  equal(receiptFeeCode, bill.items[0].fee_code, 'offset_response.case_receipt.fee_code')
  equal(receivableAmount, bill.amount, 'offset_response.case_receipt.receivable_amt')
  const remaining = BigInt(bill.balance.replace('.', ''))
  const receivable = BigInt(receivableAmount.replace('.', ''))
  const received = BigInt(receivedAmount.replace('.', ''))
  const offsetMinor = BigInt(offsetAmount.replace('.', ''))
  if (received !== receivable - remaining || offsetMinor > received) {
    invalid('offset_response.case_receipt.received_amt')
  }
  equal(receiptDate, offsetDate, 'offset_response.case_receipt.last_receipt_date')
  return value as DemoOffsetResponse
}
