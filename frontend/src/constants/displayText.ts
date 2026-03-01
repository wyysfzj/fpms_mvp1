export const CASE_STATUS_TEXT: Record<string, string> = {
  NOT_FILED: '未递交',
  WAITING_RECEIPT: '等待受理',
  PRELIM_EXAM: '初审',
  AMENDMENT: '补正中',
  PRELIM_PASS: '初审通过',
  PUBLISHED: '已公开',
  SUB_EXAM: '实审中',
  OA1: '一通阶段',
  OA2: '二通阶段',
  GRANTED: '已授权',
  REJECTED: '驳回',
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
