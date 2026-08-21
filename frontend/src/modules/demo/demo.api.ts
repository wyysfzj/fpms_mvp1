import { http } from '../../api/http'
import {
  parseDemoBankReceiptResponse,
  parseDemoBillCommandResponse,
  parseDemoDraft,
  parseDemoFeeObligationResponse,
  parseDemoOffsetResponse,
  parseDemoPreflight,
  parseDemoServiceItem,
} from './demo.contract'
import {
  classifyCommandReadStatus,
  reconcileUnknownMutationResult,
  resolveCommandMutationResponse,
  shouldReconcileUnknownCommand,
} from './command-reconcile'

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
  business_counts: Record<
    'client' | 'contact' | 'case' | 'package' | 'task' | 'obligation' | 'draft' | 'bill' | 'payment' | 'offset',
    number
  >
}

export interface DemoDraft {
  id: string
  case_id: string
  client_id: string
  currency: string
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
  currency: string
  direction: 'AR'
  status: 'UNSETTLED' | 'SETTLED'
  total_gov: string
  total_service: string
  total_misc: string
  amount: string
  balance: string
  bill_date: string
  due_date?: string
  source_draft_ids: string[]
  items: Array<{ id: string; fee_type: string; fee_code: string; amount: string }>
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
    currency: string
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
    fee_type: string
    fee_code: string
    currency: string
    receivable_amt: string
    received_amt: string
    last_receipt_date: string
  }
  idempotency_key: string
  reused: boolean
}

export async function readDemoServiceItem(): Promise<DemoServiceItem> {
  return parseDemoServiceItem((await http.get('/fees/demo-service-item')).data)
}

export async function readDemoPreflight(): Promise<DemoPreflight> {
  return parseDemoPreflight((await http.get('/fees/demo-preflight')).data)
}

export async function createDemoServiceObligation(
  caseId: string,
  itemCode: string,
  idempotencyKey: string,
): Promise<DemoFeeObligationResponse> {
  return parseDemoFeeObligationResponse(
    (
      await http.post('/fees/demo-service-obligations', {
        case_id: caseId,
        item_code: itemCode,
        idempotency_key: idempotencyKey,
      })
    ).data,
  )
}

export async function recordDemoPayInstruction(
  obligationId: string,
  idempotencyKey: string,
): Promise<void> {
  await http.post(`/fees/obligations/${obligationId}/instruction`, {
    instruction: 'PAY',
    idempotency_key: idempotencyKey,
  })
}

export async function createDemoDraft(
  caseId: string,
  clientId: string,
  obligationId: string,
): Promise<DemoDraft> {
  return parseDemoDraft(
    (
      await http.post('/fees/drafts', {
        case_id: caseId,
        client_id: clientId,
        draft_type: 'GENERIC',
        currency: 'CNY',
        obligation_id: obligationId,
      })
    ).data,
  )
}

export async function lockDemoDraft(draftId: string): Promise<DemoDraft> {
  try {
    await http.post(`/fees/drafts/${draftId}/lock`)
  } catch (error) {
    return reconcileUnknownMutationResult(
      error,
      async () =>
        parseDemoDraft((await http.get<DemoDraft>(`/fees/drafts/${draftId}`)).data),
      (draft) => draft.status === 'LOCKED',
    )
  }
  return parseDemoDraft((await http.get<DemoDraft>(`/fees/drafts/${draftId}`)).data)
}

export async function readDemoDraft(draftId: string): Promise<DemoDraft> {
  return parseDemoDraft((await http.get(`/fees/drafts/${draftId}`)).data)
}

async function readCommand(endpoint: string) {
  return http.get(endpoint, {
    validateStatus: (status) => status === 200 || status === 202 || status === 404,
  })
}

async function reconcileUnknownCommand<T>(
  endpoint: string,
  error: unknown,
  parse: (value: unknown) => T,
): Promise<T> {
  if (!shouldReconcileUnknownCommand(error)) throw error
  try {
    const response = await readCommand(endpoint)
    const classification = classifyCommandReadStatus(response.status)
    if (classification === 'ABSENT') throw error
    return await resolveCommandMutationResponse(response, () => readCommand(endpoint), parse)
  } catch {
    throw error
  }
}

async function readCompletedCommand<T>(
  endpoint: string,
  parse: (value: unknown) => T,
): Promise<T | undefined> {
  const response = await readCommand(endpoint)
  return response.status === 200 ? parse(response.data) : undefined
}

export async function readDemoBillCommand(
  idempotencyKey: string,
): Promise<{ bill: DemoBillDetail; idempotency_key: string; reused: boolean } | undefined> {
  return readCompletedCommand(
    `/bills/from-drafts/idempotency/${encodeURIComponent(idempotencyKey)}`,
    parseDemoBillCommandResponse,
  )
}

export async function readDemoPaymentCommand(
  idempotencyKey: string,
): Promise<DemoBankReceiptResponse | undefined> {
  return readCompletedCommand(
    `/payments/idempotency/${encodeURIComponent(idempotencyKey)}`,
    parseDemoBankReceiptResponse,
  )
}

export async function readDemoOffsetCommand(
  idempotencyKey: string,
): Promise<DemoOffsetResponse | undefined> {
  return readCompletedCommand(
    `/offsets/idempotency/${encodeURIComponent(idempotencyKey)}`,
    parseDemoOffsetResponse,
  )
}

export async function createDemoBill(
  draftId: string,
  billNo: string,
  billDate: string,
  dueDate: string,
  idempotencyKey: string,
): Promise<{ bill: DemoBillDetail; idempotency_key: string; reused: boolean }> {
  const endpoint = `/bills/from-drafts/idempotency/${encodeURIComponent(idempotencyKey)}`
  let response
  try {
    response = await http.post('/bills/demo-from-draft', {
      draft_id: draftId,
      bill_no: billNo,
      bill_date: billDate,
      due_date: dueDate,
      idempotency_key: idempotencyKey,
    })
  } catch (error) {
    return reconcileUnknownCommand(endpoint, error, parseDemoBillCommandResponse)
  }
  return resolveCommandMutationResponse(
    response,
    () => readCommand(endpoint),
    parseDemoBillCommandResponse,
  )
}

export async function createDemoBankReceipt(
  bill: DemoBillDetail,
  payNo: string,
  bankRefNo: string,
  payDate: string,
  idempotencyKey: string,
): Promise<DemoBankReceiptResponse> {
  const endpoint = `/payments/idempotency/${encodeURIComponent(idempotencyKey)}`
  let response
  try {
    response = await http.post<DemoBankReceiptResponse>('/payments/demo-bank-receipts', {
      target_bill_id: bill.id,
      amount: bill.balance,
      pay_no: payNo,
      pay_date: payDate,
      currency: 'CNY',
      pay_method: 'BANK_TRANSFER',
      bank_ref_no: bankRefNo,
      remark: 'ABC 本地演示客户回款',
      idempotency_key: idempotencyKey,
    })
  } catch (error) {
    return reconcileUnknownCommand(endpoint, error, parseDemoBankReceiptResponse)
  }
  return resolveCommandMutationResponse(
    response,
    () => readCommand(endpoint),
    parseDemoBankReceiptResponse,
  )
}

export async function createDemoFullOffset(
  paymentLine: DemoPaymentLine,
  bill: DemoBillDetail,
  offsetDate: string,
  idempotencyKey: string,
): Promise<DemoOffsetResponse> {
  const endpoint = `/offsets/idempotency/${encodeURIComponent(idempotencyKey)}`
  let response
  try {
    response = await http.post<DemoOffsetResponse>('/offsets/demo-full', {
      payment_line_id: paymentLine.id,
      bill_id: bill.id,
      offset_amt: paymentLine.balance_amt,
      offset_date: offsetDate,
      idempotency_key: idempotencyKey,
    })
  } catch (error) {
    return reconcileUnknownCommand(endpoint, error, parseDemoOffsetResponse)
  }
  return resolveCommandMutationResponse(
    response,
    () => readCommand(endpoint),
    parseDemoOffsetResponse,
  )
}
