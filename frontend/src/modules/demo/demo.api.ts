import { http } from '../../api/http'
import { getLifecycleOverlay } from '../../api/lifecycleOverlay'
import {
  parseDemoBankReceiptResponse,
  parseDemoBillCommandResponse,
  parseDemoDraft,
  parseDemoFeeObligationResponse,
  parseDemoOffsetResponse,
  parseDemoPreflight,
  parseDemoServiceItem,
} from './demo.contract'
import type {
  DemoFeeObligationResponse,
  DemoPreflight,
  DemoServiceItem,
} from './demo.contract'
export type { DemoFeeObligationResponse, DemoPreflight, DemoServiceItem } from './demo.contract'
import {
  reconcileThenRetryMutationOnce,
  reconcileUnknownMutationResult,
  resolveCommandMutationResponse,
} from './command-reconcile'

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
  status: 'UNSETTLED' | 'PARTIALLY_SETTLED' | 'SETTLED'
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

export async function readDemoServiceObligation(
  obligationId: string,
  caseId: string,
  expectedItem: DemoServiceItem,
  intentKey: string,
): Promise<DemoFeeObligationResponse> {
  const value: unknown = (await http.get(`/fees/obligations/${obligationId}`)).data
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error('演示服务费义务响应无效')
  }
  const detail = value as Record<string, unknown>
  const source = detail.source
  const statuses = detail.statuses
  const lines = detail.lines
  if (
    detail.id !== obligationId
    || detail.case_id !== caseId
    || detail.fee_domain !== 'SERVICE'
    || detail.currency !== expectedItem.currency
    || typeof source !== 'object'
    || source === null
    || Array.isArray(source)
    || typeof statuses !== 'object'
    || statuses === null
    || Array.isArray(statuses)
    || !Array.isArray(lines)
    || lines.length !== 1
  ) {
    throw new Error('演示服务费义务与当前案件不一致')
  }
  const sourceRow = source as Record<string, unknown>
  const statusRow = statuses as Record<string, unknown>
  const line = lines[0]
  if (
    typeof line !== 'object'
    || line === null
    || Array.isArray(line)
    || (line as Record<string, unknown>).obligation_id !== obligationId
    || (line as Record<string, unknown>).case_id !== caseId
    || (line as Record<string, unknown>).fee_code !== expectedItem.item_code
    || (line as Record<string, unknown>).payable_amount !== expectedItem.amount
    || statusRow.obligation_status !== 'RECOGNIZED'
    || !['PENDING', 'PAY'].includes(String(statusRow.client_instruction_status))
    || !['NOT_CREATED', 'CREATED'].includes(String(statusRow.draft_status))
    || statusRow.pay_list_status !== 'NOT_CREATED'
    || statusRow.payment_status !== 'UNPAID'
    || statusRow.official_evidence_status !== 'NOT_APPLICABLE'
    || typeof sourceRow.source_activity_id !== 'string'
    || sourceRow.source_activity_id.length === 0
  ) {
    throw new Error('演示服务费义务权威状态无效')
  }
  return {
    ...expectedItem,
    obligation: { id: obligationId },
    source_activity_id: sourceRow.source_activity_id,
    idempotency_key: intentKey,
    reused: true,
  }
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

export async function recoverDemoLockedDraft(
  caseId: string,
  clientId: string,
  obligation: DemoFeeObligationResponse,
): Promise<DemoDraft> {
  const overlay = await getLifecycleOverlay(caseId, {
    afterSequence: 0,
    limit: 200,
    asOfRevision: null,
  })
  if (overlay.caseId !== caseId || overlay.hasMore) {
    throw new Error('案件费用事实未完整加载，无法恢复演示草单')
  }
  const obligationMatches = overlay.milestones
    .flatMap((milestone) => milestone.feeObligations)
    .filter((row) => row.obligationId === obligation.obligation.id
      && row.relatedFacts.some((fact) => fact.kind === 'DRAFT'))
  if (obligationMatches.length !== 1) {
    throw new Error('当前案件没有唯一的服务费义务事实')
  }
  const [match] = obligationMatches
  const [line] = match.lines
  const { feeCode, payableAmount } = line || {}
  const { sourceActivityId } = match
  if (
    sourceActivityId !== obligation.source_activity_id
    || match.sourceStatus !== 'VERIFIED'
    || match.feeDomain !== 'SERVICE'
    || match.currency !== obligation.currency
    || match.statuses.obligationStatus !== 'RECOGNIZED'
    || match.statuses.clientInstructionStatus !== 'PAY'
    || match.statuses.draftStatus !== 'CREATED'
    || match.statuses.payListStatus !== 'NOT_CREATED'
    || match.statuses.paymentStatus !== 'UNPAID'
    || match.statuses.officialEvidenceStatus !== 'NOT_APPLICABLE'
    || match.lines.length !== 1
    || feeCode !== obligation.item_code
    || payableAmount !== obligation.amount
  ) {
    throw new Error('服务费义务来源或状态与当前演示输入不一致')
  }
  const draftFacts = match.relatedFacts.filter((fact) => fact.kind === 'DRAFT')
  if (draftFacts.length !== 1 || draftFacts[0].status !== 'LOCKED') {
    throw new Error('当前服务费义务没有唯一的已锁定草单')
  }
  const draft = await readDemoDraft(draftFacts[0].objectId)
  if (
    draft.case_id !== caseId
    || draft.client_id !== clientId
    || draft.currency !== 'CNY'
    || draft.status !== 'LOCKED'
    || draft.total_gov !== '0.00'
    || draft.total_service !== obligation.amount
    || draft.total_misc !== '0.00'
    || draft.amount !== obligation.amount
  ) {
    throw new Error('已锁定草单与当前案件、义务或金额不一致')
  }
  return draft
}

async function readCommand(endpoint: string) {
  return http.get(endpoint, {
    validateStatus: (status) => status === 200 || status === 202 || status === 404,
  })
}

async function reconcileUnknownCommand<T>(
  endpoint: string,
  error: unknown,
  retryMutation: () => Promise<{ status: number; data: unknown }>,
  parse: (value: unknown) => T,
): Promise<T> {
  return reconcileThenRetryMutationOnce(
    error,
    () => readCommand(endpoint),
    retryMutation,
    parse,
  )
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
  const payload = {
    draft_id: draftId,
    bill_no: billNo,
    bill_date: billDate,
    due_date: dueDate,
    idempotency_key: idempotencyKey,
  }
  const retryMutation = () => http.post('/bills/demo-from-draft', payload)
  let response
  try {
    response = await retryMutation()
  } catch (error) {
    return reconcileUnknownCommand(endpoint, error, retryMutation, parseDemoBillCommandResponse)
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
  const payload = {
    target_bill_id: bill.id,
    amount: bill.balance,
    pay_no: payNo,
    pay_date: payDate,
    currency: 'CNY',
    pay_method: 'BANK_TRANSFER',
    bank_ref_no: bankRefNo,
    remark: '澄岳智造技术（苏州）有限公司客户回款',
    idempotency_key: idempotencyKey,
  }
  const retryMutation = () => http.post<DemoBankReceiptResponse>('/payments/demo-bank-receipts', payload)
  let response
  try {
    response = await retryMutation()
  } catch (error) {
    return reconcileUnknownCommand(endpoint, error, retryMutation, parseDemoBankReceiptResponse)
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
  const payload = {
    payment_line_id: paymentLine.id,
    bill_id: bill.id,
    offset_amt: paymentLine.balance_amt,
    offset_date: offsetDate,
    idempotency_key: idempotencyKey,
  }
  const retryMutation = () => http.post<DemoOffsetResponse>('/offsets/demo-full', payload)
  let response
  try {
    response = await retryMutation()
  } catch (error) {
    return reconcileUnknownCommand(endpoint, error, retryMutation, parseDemoOffsetResponse)
  }
  return resolveCommandMutationResponse(
    response,
    () => readCommand(endpoint),
    parseDemoOffsetResponse,
  )
}
