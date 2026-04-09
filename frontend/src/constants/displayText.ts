export const CASE_STATUS_TEXT: Record<string, string> = {
  ACCEPTED: '已受理',
  NOT_FILED: '未递交',
  WAITING_RECEIPT: '等待受理',
  PENDING: '审查中',
  PRELIM_EXAM: '初审',
  AMENDMENT: '补正中',
  PRELIM_PASS: '初审通过',
  PUBLISHED: '已公开',
  SUB_EXAM: '实审中',
  OA1: '一通阶段',
  OA2: '二通阶段',
  GRANT_PENDING: '待授权',
  GRANTED: '已授权',
  REJECTED: '驳回',
  WITHDRAWN: '已撤回',
  ABANDONED: '视为放弃',
  EXPIRED: '已失效',
  TERMINATED: '中止/终止',
  INVALIDATED: '全部无效',
  INVALIDATED_PARTIAL: '部分无效',
  REEXAM: '复审中',
}

export const BILL_STATUS_TEXT: Record<string, string> = {
  ISSUED: '已开具',
  PAID: '已支付',
  UNSETTLED: '未结清',
  VOID: '已作废',
}

export const FEE_DRAFT_STATUS_TEXT: Record<string, string> = {
  OPEN: '开放',
  LOCKED: '已锁定',
}

export const FEE_DRAFT_TYPE_TEXT: Record<string, string> = {
  APPLY_FEE: '申请费',
  OA_FEE: '审查意见费',
  GRANT_FEE: '授权费',
  ANNUITY_FEE: '年费',
  INVALID_FEE: '无效费',
  CONSULT_FEE: '顾问费',
  SEARCH_FEE: '检索费',
}

export const CASE_TYPE_TEXT: Record<string, string> = {
  NORMAL: '普通',
  PCT_INTL: 'PCT国际',
  PCT_NATL: 'PCT国内',
  PRIORITY: '优先权',
  CONSULTING: '顾问项目',
  SEARCH: '检索项目',
}

export const FEE_TYPE_TEXT: Record<string, string> = {
  GOV: '官费',
  SERVICE: '服务费',
  MISC: '其他',
  APPLY_FEE: '申请费',
  OA_FEE: '审查意见费',
  GRANT_FEE: '授权费',
  ANNUITY_FEE: '年费',
  INVALID_FEE: '无效费',
  CONSULT_FEE: '顾问费',
  SEARCH_FEE: '检索费',
}

export const TASK_STATUS_TEXT: Record<string, string> = {
  OPEN: '待处理',
  PENDING: '待处理',
  IN_PROGRESS: '进行中',
  'IN PROGRESS': '进行中',
  CLOSED: '已关闭',
  COMPLETED: '已完成',
  DONE: '已完成',
  CANCELLED: '已取消',
  CANCELED: '已取消',
  OVERDUE: '已逾期',
  BLOCKED: '已阻塞',
}

export const TASK_PRIORITY_TEXT: Record<string, string> = {
  URGENT: '紧急',
  HIGH: '高',
  MEDIUM: '中',
  LOW: '低',
}

export const DOCUMENT_DIRECTION_TEXT: Record<string, string> = {
  IN: '收文',
  OUT: '发文',
}

export const DOCUMENT_DOC_TYPE_TEXT: Record<string, string> = {
  OFFICIAL_IN: '官方来文',
  OFFICIAL_OUT: '官方去文',
  CLIENT_IN: '客户来文',
  CLIENT_OUT: '致函客户',
}

export const PAYMENT_METHOD_TEXT: Record<string, string> = {
  CASH: '现金',
  BANK_TRANSFER: '银行转账',
  CHECK: '支票',
  OTHER: '其他',
}

export function getCaseStatusText(status?: string): string {
  if (!status) return '-'
  return CASE_STATUS_TEXT[status] || status
}

export function getBillStatusText(status?: string): string {
  if (!status) return '-'
  return BILL_STATUS_TEXT[status] || status
}

export function getFeeDraftStatusText(status?: string): string {
  if (!status) return '-'
  return FEE_DRAFT_STATUS_TEXT[status] || status
}

export function getFeeDraftTypeText(type?: string | null): string {
  if (!type) return '-'
  const key = type.toUpperCase()
  return FEE_DRAFT_TYPE_TEXT[key] || type
}

export function getCaseTypeText(type?: string | null): string {
  if (!type) return '-'
  const key = type.toUpperCase()
  return CASE_TYPE_TEXT[key] || type
}

export function getFeeTypeText(type?: string | null): string {
  if (!type) return '-'
  const key = type.toUpperCase()
  return FEE_TYPE_TEXT[key] || type
}

export function getTaskStatusText(status?: string): string {
  if (!status) return '-'
  const key = status.toUpperCase()
  return TASK_STATUS_TEXT[key] || status
}

export function getTaskPriorityText(priority?: string): string {
  if (!priority) return '-'
  const key = priority.toUpperCase()
  return TASK_PRIORITY_TEXT[key] || priority
}

export function getDocumentDirectionText(direction?: string): string {
  if (!direction) return '-'
  return DOCUMENT_DIRECTION_TEXT[direction] || direction
}

export function getDocumentDocTypeText(docType?: string | null): string {
  if (!docType) return '-'
  return DOCUMENT_DOC_TYPE_TEXT[docType] || docType
}

export function getPaymentMethodText(method?: string): string {
  if (!method) return '-'
  return PAYMENT_METHOD_TEXT[method] || method
}

export function getTaskActionText(actionName: string): string {
  if (actionName === 'close') return '关闭'
  if (actionName === 'reopen') return '重新打开'
  if (actionName === 'cancel') return '取消'
  return actionName
}
