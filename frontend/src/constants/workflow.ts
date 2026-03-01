/**
 * Workflow Step definitions and status mapping for Case lifecycle.
 * Maps backend CaseStatus values to 5-step workflow progression.
 */
import { getCaseStatusText } from './displayText'

export interface WorkflowStep {
  key: string
  label: string
  color: string
}

export const WORKFLOW_STEPS: WorkflowStep[] = [
  { key: 'ACCEPTED', label: '受理', color: '#2563eb' },
  { key: 'PRELIM', label: '初审', color: '#f59e0b' },
  { key: 'PUBLISHED', label: '公布', color: '#8b5cf6' },
  { key: 'SUB_EXAM', label: '实审', color: '#1d4ed8' },
  { key: 'GRANTED', label: '授权', color: '#10b981' },
]

export interface StatusRule {
  stepKey: string
  legalStatusCode: string
  legalText: string
  stepText: string
  nextAction: string
  branchNote?: string
}

export const STATUS_STEP_MAP: Record<string, StatusRule> = {
  NOT_FILED: { stepKey: 'ACCEPTED', legalStatusCode: 'NOT_FILED', legalText: getCaseStatusText('NOT_FILED'), stepText: '受理', nextAction: '完成递交后进入受理节点。' },
  WAITING_RECEIPT: { stepKey: 'ACCEPTED', legalStatusCode: 'WAITING_RECEIPT', legalText: getCaseStatusText('WAITING_RECEIPT'), stepText: '受理', nextAction: '收到受理通知后进入初审节点。' },
  PRELIM_EXAM: { stepKey: 'PRELIM', legalStatusCode: 'PRELIM_EXAM', legalText: getCaseStatusText('PRELIM_EXAM'), stepText: '初审', nextAction: '初审通过后进入公布节点。' },
  PRELIM_PASS: { stepKey: 'PRELIM', legalStatusCode: 'PRELIM_PASS', legalText: getCaseStatusText('PRELIM_PASS'), stepText: '初审', nextAction: '完成公开手续后进入公布节点。' },
  AMENDMENT: { stepKey: 'PRELIM', legalStatusCode: 'AMENDMENT', legalText: getCaseStatusText('AMENDMENT'), stepText: '初审', nextAction: '补正完成后回到初审并推进公开。' },
  PUBLISHED: { stepKey: 'PUBLISHED', legalStatusCode: 'PUBLISHED', legalText: getCaseStatusText('PUBLISHED'), stepText: '公布', nextAction: '进入实审流程（可能经历 OA 往返）。' },
  SUB_EXAM: { stepKey: 'SUB_EXAM', legalStatusCode: 'SUB_EXAM', legalText: getCaseStatusText('SUB_EXAM'), stepText: '实审', nextAction: '实审通过后录入授权通知进入授权。' },
  OA1: { stepKey: 'SUB_EXAM', legalStatusCode: 'OA1', legalText: getCaseStatusText('OA1'), stepText: '实审', nextAction: '提交 OA 答复后回到实审。' },
  OA2: { stepKey: 'SUB_EXAM', legalStatusCode: 'OA2', legalText: getCaseStatusText('OA2'), stepText: '实审', nextAction: '继续答复审查意见，满足条件后可授权。' },
  REEXAM: { stepKey: 'SUB_EXAM', legalStatusCode: 'REEXAM', legalText: getCaseStatusText('REEXAM'), stepText: '实审', nextAction: '复审结果决定是否转入授权或驳回。' },
  GRANTED: { stepKey: 'GRANTED', legalStatusCode: 'GRANTED', legalText: getCaseStatusText('GRANTED'), stepText: '授权', nextAction: '进入授权后费用和年费管理。' },
  REJECTED: { stepKey: 'SUB_EXAM', legalStatusCode: 'REJECTED', legalText: getCaseStatusText('REJECTED'), stepText: '实审', nextAction: '可按策略进入复审或结案。', branchNote: '该案已进入分支状态：驳回。主干流程停留在第4步（实审），未进入“授权”。' },
  TERMINATED: { stepKey: 'GRANTED', legalStatusCode: 'TERMINATED', legalText: getCaseStatusText('TERMINATED'), stepText: '授权', nextAction: '检查年费或恢复权利策略。', branchNote: '该案已进入分支状态：终止。主干流程保留“授权”的历史位置。' },
  INVALIDATED: { stepKey: 'GRANTED', legalStatusCode: 'INVALIDATED', legalText: getCaseStatusText('INVALIDATED'), stepText: '授权', nextAction: '查看无效决定文书并评估后续动作。', branchNote: '该案已进入分支状态：全部无效。主干流程保留“授权”的历史位置。' },
  INVALIDATED_PARTIAL: { stepKey: 'GRANTED', legalStatusCode: 'INVALIDATED_PARTIAL', legalText: getCaseStatusText('INVALIDATED_PARTIAL'), stepText: '授权', nextAction: '核对受影响权利要求并评估后续策略。', branchNote: '该案已进入分支状态：部分无效。主干流程保留“授权”的历史位置。' },
}

const DEFAULT_RULE: StatusRule = {
  stepKey: 'ACCEPTED',
  legalStatusCode: 'UNKNOWN',
  legalText: '未知状态',
  stepText: '受理',
  nextAction: '请更新案件法律状态。',
}

export function getStatusRule(status: string | undefined): StatusRule {
  if (!status) return DEFAULT_RULE
  return STATUS_STEP_MAP[status] || {
    ...DEFAULT_RULE,
    legalStatusCode: status,
    legalText: getCaseStatusText(status),
  }
}

export function getStepIndex(stepKey: string): number {
  const idx = WORKFLOW_STEPS.findIndex(s => s.key === stepKey)
  return idx >= 0 ? idx : 0
}

export function getCaseWorkflow(status: string | undefined) {
  const rule = getStatusRule(status)
  const stepIndex = getStepIndex(rule.stepKey)
  return {
    rule,
    stepIndex,
    stepLabel: WORKFLOW_STEPS[stepIndex].label,
    stepNoText: `第${stepIndex + 1}步/5`,
  }
}

export function getStatusTagClass(status: string): string {
  if (status === 'GRANTED') return 'green'
  if (status === 'WAITING_RECEIPT' || status === 'NOT_FILED') return 'blue'
  if (['PRELIM_EXAM', 'PRELIM_PASS', 'AMENDMENT'].includes(status)) return 'orange'
  if (status === 'PUBLISHED') return 'indigo'
  if (['SUB_EXAM', 'OA1', 'OA2', 'REEXAM'].includes(status)) return 'blue'
  if (['REJECTED', 'INVALIDATED'].includes(status)) return 'red'
  if (status === 'TERMINATED') return 'gray'
  return 'gray'
}
