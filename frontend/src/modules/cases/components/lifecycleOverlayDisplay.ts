import type {
  BusinessStage,
  ConfirmationStatus,
  LegalStatus,
  OfficialProcedureStage,
} from '../../../api/lifecycleOverlay.types'

type CenterState = BusinessStage | OfficialProcedureStage | LegalStatus | ConfirmationStatus

const CENTER_STATE_LABELS = {
  NEW_CASE: '新建案件',
  FILING_PREPARATION: '递交准备',
  WAITING_EXTERNAL_RECEIPT: '等待外部回执',
  PROSECUTION_MANAGEMENT: '流程管理',
  OA_REPLY_IN_PROGRESS: '审查意见答复中',
  GRANT_REGISTRATION_IN_PROGRESS: '授权登记中',
  POST_GRANT_MAINTENANCE: '授权后维护',
  CLOSED: '已结案',
  NOT_SUBMITTED: '尚未递交',
  SUBMITTED_WAITING_RECEIPT: '已递交，等待回执',
  SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE: '递交已确认，等待受理',
  ACCEPTED: '已受理',
  PRELIMINARY_EXAMINATION: '初步审查',
  RECTIFICATION_RESPONSE: '补正答复',
  PUBLISHED: '已公布',
  SUBSTANTIVE_EXAMINATION: '实质审查',
  OFFICE_ACTION_RESPONSE: '审查意见答复',
  REEXAMINATION: '复审',
  GRANT_REGISTRATION: '授权登记',
  GRANT_ANNOUNCED: '授权公告',
  PROCEDURE_CLOSED: '官方程序已结束',
  NOT_ESTABLISHED: '权利尚未成立',
  APPLICATION_PENDING: '申请审理中',
  APPLICATION_REJECTED: '申请已驳回',
  APPLICATION_WITHDRAWN: '申请已撤回',
  APPLICATION_ABANDONED: '申请已放弃',
  PATENT_IN_FORCE: '专利权有效',
  PATENT_TERMINATED: '专利权终止',
  PATENT_EXPIRED: '专利权期限届满',
  PATENT_INVALIDATED: '专利权无效',
  UNKNOWN: '状态未知',
  NEEDS_REVIEW: '需复核',
  CONFIRMED: '已确认',
  LEGACY_UNVERIFIED: '历史数据待核验',
} as const satisfies Readonly<Record<CenterState, string>>

const ACTIVITY_TYPE_LABELS: Readonly<Record<string, string>> = {
  FILING_PREPARATION_STARTED: '申请文件准备已开始',
  DOCUMENT_EVIDENCE_VERSION_REGISTERED: '文件证据版本已登记',
  DOCUMENT_EVIDENCE_REVIEW_DECIDED: '文件证据复核结论已记录',
  DOCUMENT_EVIDENCE_EXTERNAL_SUBMISSION_FINALIZED: '外部递交文件已定稿',
  FILING_EXTERNAL_SUBMISSION_RECORDED: '申请文件已递交',
  FILING_RECEIPT_ARCHIVED: '申请回执已归档',
  ACCEPTANCE_NOTICE_RECORDED: '受理通知已登记',
  PRELIMINARY_EXAMINATION_STARTED: '初步审查已开始',
  PRELIMINARY_EXAMINATION_PASSED: '初步审查已通过',
  PUBLICATION_NOTICE_RECORDED: '公布通知已登记',
  SUBSTANTIVE_EXAMINATION_STARTED: '实质审查已开始',
  OA_NOTICE_RECORDED: '审查意见通知已登记',
  OA_EXTERNAL_SUBMISSION_RECORDED: '审查意见答复已递交',
  OA_RECEIPT_ARCHIVED: '审查意见答复回执已归档',
  GRANT_REGISTRATION_NOTICE_RECORDED: '授权登记通知已登记',
}

const FEE_STATUS_TEXT: Readonly<Record<string, string>> = {
  GOV: '官费',
  SERVICE: '服务费',
  OFFICIAL_FEE: '官费缴费义务',
  GRANT_REGISTRATION_OFFICIAL_FEES: '授权登记官费义务',
  SERVICE_FEE: '服务费应收义务',
  RECOGNIZED: '已确认',
  SUPERSEDED: '已被替代',
  PAY: '缴费',
  CREATED: '已创建',
  NOT_CREATED: '未创建',
  UNPAID: '未缴费',
  NOT_APPLICABLE: '不适用',
  OPEN: '处理中',
  LOCKED: '已锁定',
  DRAFT: '草稿',
  PAY_LIST: '缴费清单',
  PLANNED: '已计划',
  RECORDED: '已登记，待官方凭证核验',
  PAID: '已缴费',
  PARTIAL: '部分完成',
  UNSETTLED: '未结清',
  PARTIALLY_SETTLED: '部分结清',
  SETTLED: '已结清',
  PENDING: '待处理',
  NOT_AVAILABLE: '暂无',
  NOT_REQUIRED: '不需要',
  UNVERIFIED: '待核验',
  VERIFIED: '已核验',
  MATCHED: '一致',
  DIFFERENT: '存在差额',
  BILL: '客户账单',
  PAYMENT: '客户回款',
  OFFSET: '账单核销',
  GOV_PAYMENT: '官费登记',
}

export function centerStateText(value: string | null, emptyText = '-'): string {
  if (value === null) return emptyText
  return CENTER_STATE_LABELS[value as CenterState] ?? '未识别状态'
}

export function activityTypeText(
  activityType: string,
  fallback = '活动类型待确认',
): string {
  return ACTIVITY_TYPE_LABELS[activityType] ?? fallback
}

export function feeStatusText(value: string | null, fallback = '未识别状态'): string {
  if (!value) return '暂无'
  return FEE_STATUS_TEXT[value.toUpperCase()] ?? fallback
}
