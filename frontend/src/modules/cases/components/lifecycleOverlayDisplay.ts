import type {
  BusinessStage,
  ConfirmationStatus,
  LegalStatus,
  OfficialProcedureStage,
  OverlayFeeObligation,
  OverlayFeeRelatedFact,
  OverlayMilestone,
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
  ESTIMATE: '估算',
  PAY: '缴费',
  HOLD: '暂缓',
  ABANDON: '放弃',
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
  REVIEW_REQUIRED: '需复核',
  SOURCE_PENDING: '来源待确认',
  MATCHED: '一致',
  DIFFERENT: '存在差额',
  BILL: '客户账单',
  PAYMENT: '付款记录',
  OFFSET: '账单核销',
  GOV_PAYMENT: '官费登记',
  DRAFT: '草单',
  PAY_LIST: '缴费清单',
  OFFICIAL_EVIDENCE: '官方证据',
}

const EVIDENCE_ROLE_LABELS: Readonly<Record<string, string>> = {
  FILING_FULL_WORD: '申请文件完整 Word',
  TRACKED_REVISED_WORD: '修订留痕 Word',
  FILING_COMPONENT: '申请文件组成部分',
  EXTERNAL_XML_PACKAGE: '外部递交 XML 包',
  OFFICIAL_SUBMISSION_LIST: '官方递交清单',
  OFFICIAL_FINAL_PDF: '最终递交 PDF',
  SUBMITTED_XML: '已递交 XML',
  OFFICIAL_RECEIPT: '官方回执',
  CLIENT_LETTER_WORD: '客户函 Word',
  RAW_ATTACHMENT: '原始附件',
  GENERATED_ATTACHMENT: '生成附件',
  OA_STRUCTURED_ATTACHMENT: '审查意见结构化附件',
}

const EVIDENCE_STATE_LABELS: Readonly<Record<string, string>> = {
  DRAFT: '草稿',
  FINAL: '已定稿',
}

const EVIDENCE_REVIEW_LABELS: Readonly<Record<string, string>> = {
  PENDING: '待复核',
  APPROVED: '已复核',
  REJECTED: '复核未通过',
}

const DERIVATION_TYPE_LABELS: Readonly<Record<string, string>> = {
  REVISION: '版本修订',
  COMPONENT_EXTRACTION: '组成部分提取',
  FORMAT_CONVERSION: '格式转换',
  OFFICIAL_RECOGNITION: '官方文件识别',
  EXTERNAL_SUBMISSION: '外部递交',
  RECEIPT_LINK: '回执关联',
  CUSTOMER_LETTER_RENDER: '客户函生成',
  OA_REPLY_PREPARATION: '审查意见答复准备',
}

const WORK_PACKAGE_KIND_LABELS: Readonly<Record<string, string>> = {
  FILING_PREP: '新申请递交',
  OA_REPLY: '审查意见答复',
}

const WORK_PACKAGE_STATUS_LABELS: Readonly<Record<string, string>> = {
  PREPARING: '准备中',
  NEEDS_MAINTENANCE: '需维护',
  NEEDS_CONFIRMATION: '待确认',
  READY_FOR_EXTERNAL_SUBMIT: '可人工提交',
  SUBMITTED: '已提交',
  WAITING_RECEIPT: '待回执',
  ARCHIVED: '已归档',
  EXCEPTION: '异常',
  OVERRIDE: '已例外处理',
}

const RECEIPT_KIND_LABELS: Readonly<Record<string, string>> = {
  RECEIPT_PDF: '回执 PDF',
  MERGED_PDF: '合并 PDF',
  ELECTRONIC_APPLICATION_RECEIPT: '电子申请回执',
}

const RECEIPT_ARCHIVE_LABELS: Readonly<Record<string, string>> = {
  ARCHIVED: '已归档',
  PENDING: '待归档',
}

const TASK_STATUS_LABELS: Readonly<Record<string, string>> = {
  OPEN: '待处理',
  DONE: '已完成',
  CANCELLED: '已取消',
}

const MISSING_GATE_LABELS: Readonly<Record<string, string>> = {
  CHECKLIST_INCOMPLETE: '递交检查清单未完成',
  MANIFEST_MISSING: '递交文件清单缺失',
  RECEIPT_MISSING: '回执缺失',
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

export function feeStatusText(value: string | null, fallback = '待确认'): string {
  if (!value) return '暂无'
  return FEE_STATUS_TEXT[value.toUpperCase()] ?? fallback
}

function closedMapText(
  value: string | null,
  labels: Readonly<Record<string, string>>,
): string {
  if (!value) return '暂无'
  return labels[value.toUpperCase()] ?? '待确认'
}

export function overlayDateText(value: string | null): string {
  if (!value) return '暂无'
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value
  const match = /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?$/.exec(value)
  return match ? `${match[1]} ${match[2]}` : '待确认'
}

export function currencyText(value: string | null): string {
  if (!value) return '币种待确认'
  return value.toUpperCase() === 'CNY' ? '人民币（CNY）' : '币种待确认'
}

export function evidenceRoleText(value: string | null): string {
  return closedMapText(value, EVIDENCE_ROLE_LABELS)
}

export function evidenceStateText(value: string | null): string {
  return closedMapText(value, EVIDENCE_STATE_LABELS)
}

export function evidenceReviewText(value: string | null): string {
  return closedMapText(value, EVIDENCE_REVIEW_LABELS)
}

export function derivationTypeText(value: string | null): string {
  return closedMapText(value, DERIVATION_TYPE_LABELS)
}

export function workPackageKindText(value: string | null): string {
  return closedMapText(value, WORK_PACKAGE_KIND_LABELS)
}

export function workPackageStatusText(value: string | null): string {
  return closedMapText(value, WORK_PACKAGE_STATUS_LABELS)
}

export function receiptKindText(value: string | null): string {
  return closedMapText(value, RECEIPT_KIND_LABELS)
}

export function receiptArchiveStatusText(value: string | null): string {
  return closedMapText(value, RECEIPT_ARCHIVE_LABELS)
}

export function taskStatusText(value: string | null): string {
  return closedMapText(value, TASK_STATUS_LABELS)
}

export function missingGateText(value: string | null): string {
  return closedMapText(value, MISSING_GATE_LABELS)
}

export function uniqueCodes(values: readonly string[]): readonly string[] {
  return [...new Set(values)]
}

function mergeRelatedFacts(
  previous: readonly OverlayFeeRelatedFact[],
  current: readonly OverlayFeeRelatedFact[],
): readonly OverlayFeeRelatedFact[] {
  const merged = new Map<string, OverlayFeeRelatedFact>()
  for (const fact of [...previous, ...current]) {
    merged.set(`${fact.kind}:${fact.objectId}`, fact)
  }
  return [...merged.values()]
}

export function latestObligationsById(
  milestones: readonly OverlayMilestone[],
): readonly OverlayFeeObligation[] {
  const latest = new Map<string, OverlayFeeObligation>()
  for (const milestone of milestones) {
    for (const obligation of milestone.feeObligations) {
      const previous = latest.get(obligation.obligationId)
      latest.set(obligation.obligationId, previous
        ? {
            ...obligation,
            relatedFacts: mergeRelatedFacts(previous.relatedFacts, obligation.relatedFacts),
          }
        : obligation)
    }
  }
  return [...latest.values()]
}
