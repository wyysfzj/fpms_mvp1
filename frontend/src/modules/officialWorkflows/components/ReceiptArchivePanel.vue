<template>
  <section class="case-panel receipt-archive-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">回执归档门禁</h3>
        <p class="archive-subtitle">{{ receiptGateLabel }}</p>
      </div>
      <el-tag :type="closureTagType" size="small">{{ closureText }}</el-tag>
    </div>

    <el-alert
      v-if="archiveWarning"
      type="warning"
      :closable="false"
      :title="archiveWarning"
      show-icon
    />

    <div class="archive-status-grid">
      <div class="archive-status-card">
        <span>工作包类型</span>
        <strong>{{ getPackageKindText(packageKind) }}</strong>
      </div>
      <div class="archive-status-card">
        <span>工作包状态</span>
        <strong>{{ getPackageStatusText(packageStatus) }}</strong>
      </div>
      <div class="archive-status-card">
        <span>归档状态</span>
        <strong>{{ getArchiveStatusText(archiveStatus) }}</strong>
      </div>
      <div class="archive-status-card">
        <span>回执证据</span>
        <strong>{{ receiptEvidenceReady ? '已满足' : '待补齐' }}</strong>
      </div>
    </div>

    <el-form label-position="top" class="archive-form">
      <div class="form-grid">
        <el-form-item label="回执类型">
          <el-select v-model="receiptForm.receiptKind" placeholder="请选择回执类型">
            <el-option label="电子申请回执" value="ELECTRONIC_APPLICATION_RECEIPT" />
            <el-option label="合并 PDF" value="MERGED_PDF" />
            <el-option label="其他归档证明" value="OTHER_ARCHIVE_EVIDENCE" />
          </el-select>
        </el-form-item>
        <el-form-item label="回执文件">
          <el-select
            v-model="selectedReceiptKey"
            :loading="loadingCandidates"
            placeholder="请选择当前案件已复核回执文件"
          >
            <el-option
              v-for="option in receiptOptions"
              :key="receiptKey(option)"
              :value="receiptKey(option)"
              :label="`${option.filename}｜${option.role}`"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="接收案件编号">
          <el-input v-model.trim="receiptForm.receivingCaseNo" placeholder="请输入官方接收案件编号" />
        </el-form-item>
        <el-form-item label="提交人">
          <el-input v-model.trim="receiptForm.submitter" placeholder="请输入提交人" />
        </el-form-item>
        <el-form-item label="接收时间">
          <el-date-picker
            v-model="receiptForm.receivedAt"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="请选择接收时间"
          />
        </el-form-item>
        <el-form-item label="归档状态">
          <el-select v-model="receiptForm.archiveStatus" placeholder="请选择归档状态">
            <el-option label="待归档" value="PENDING" />
            <el-option label="已归档" value="ARCHIVED" />
            <el-option label="需复核" value="NEEDS_REVIEW" />
          </el-select>
        </el-form-item>
      </div>

      <el-form-item label="收到文件清单">
        <el-input
          v-model="receiptForm.receivedFileList"
          type="textarea"
          :rows="4"
          placeholder="逐行记录官方回执中的收到文件清单"
        />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="receiptForm.note" type="textarea" :rows="2" placeholder="可填写归档说明" />
      </el-form-item>

      <div class="action-row">
        <el-button
          type="primary"
          :disabled="!receiptFormComplete"
          :loading="savingReceipt"
          @click="handleCreateReceipt"
        >
          记录回执元数据
        </el-button>
        <el-button
          :disabled="!receiptEvidenceReady && !receiptFormComplete"
          :loading="archiving"
          @click="handleArchive"
        >
          提交归档检查
        </el-button>
        <span v-if="showReceiptFormWarning" class="form-warning">缺少必填回执元数据</span>
      </div>
    </el-form>

    <div v-if="latestReceipt" class="receipt-summary">
      <div class="receipt-summary-title">已记录回执元数据</div>
      <div class="receipt-summary-grid">
        <div>
          <span>回执类型</span>
          <strong>{{ getReceiptKindText(latestReceipt.receipt_kind) }}</strong>
        </div>
        <div>
          <span>接收案件编号</span>
          <strong>{{ latestReceipt.receiving_case_no || '待确认' }}</strong>
        </div>
        <div>
          <span>提交人</span>
          <strong>{{ latestReceipt.submitter || '待确认' }}</strong>
        </div>
        <div>
          <span>接收时间</span>
          <strong>{{ latestReceipt.received_at || '待确认' }}</strong>
        </div>
      </div>
      <div class="received-file-list">
        <span>收到文件清单</span>
        <p>{{ latestReceipt.received_file_list || '待确认' }}</p>
      </div>
    </div>

    <el-divider content-position="left">受控例外处理</el-divider>

    <el-form label-position="top" class="override-form">
      <el-form-item label="例外处理原因">
        <el-input
          v-model="overrideReason"
          type="textarea"
          :rows="3"
          placeholder="请输入不能取得回执或暂不能归档的原因"
        />
      </el-form-item>
      <div class="form-grid">
        <el-form-item label="跟进责任人">
          <el-input v-model.trim="followUpOwner" placeholder="请输入跟进责任人" />
        </el-form-item>
        <el-form-item label="跟进期限">
          <el-date-picker v-model="followUpDueDate" type="date" value-format="YYYY-MM-DD" placeholder="请选择跟进期限" />
        </el-form-item>
      </div>
      <el-form-item label="跟进说明">
        <el-input v-model="followUpNote" type="textarea" :rows="2" placeholder="请输入后续补证或复核安排" />
      </el-form-item>
      <div class="action-row">
        <el-button
          type="warning"
          :disabled="!overrideReady"
          :loading="archiving"
          @click="handleOverrideArchive"
        >
          记录例外并归档
        </el-button>
        <span v-if="!overrideReady" class="form-warning">例外处理必须填写原因和跟进责任人</span>
      </div>
    </el-form>

    <div v-if="evaluation" class="evaluation-block">
      <div class="evaluation-title">
        <strong>归档检查结果</strong>
        <el-tag :type="evaluation.can_archive ? 'success' : 'warning'" size="small">
          {{ evaluation.can_archive ? '允许归档' : '仍有阻止项' }}
        </el-tag>
      </div>
      <div class="evaluation-meta">
        <span>回执硬门禁：{{ evaluation.receipt_hard_gate_satisfied ? '已满足' : '未满足' }}</span>
        <span>状态：{{ getPackageStatusText(evaluation.status) }}</span>
      </div>
      <el-table v-if="evaluation.blockers.length" :data="evaluation.blockers" size="small">
        <el-table-column prop="item_label" label="阻止项" min-width="160">
          <template #default="{ row }">{{ row.item_label || row.item_code || row.blocker_type }}</template>
        </el-table-column>
        <el-table-column prop="message" label="说明" min-width="220" />
      </el-table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  archiveOfficialWorkPackage,
  createReviewedOfficialWorkPackageReceipt,
} from '../../../api/officialWorkflows'
import {
  getCaseDocumentsWithEvidence,
  selectReviewedReceiptEvidenceOptions,
} from '../../../api/documents'
import type { ReviewedDocumentEvidenceOption } from '../../../api/documents.types'
import type {
  OfficialWorkPackageReceipt,
  OfficialWorkPackageStatusEvaluation,
} from '../../../api/officialWorkflows.types'
import type { ApiError } from '../../../api/types'

const props = withDefaults(defineProps<{
  packageId: string
  caseId: string
  packageKind: string
  packageStatus: string
  archiveStatus?: string | null
  receiptEvidenceReady?: boolean
  receiptGateLabel?: string
}>(), {
  archiveStatus: '',
  receiptEvidenceReady: false,
  receiptGateLabel: '电子申请回执 / 合并 PDF',
})

const emit = defineEmits<{
  (event: 'refresh-requested'): void
  (event: 'error', error: ApiError): void
}>()

const savingReceipt = ref(false)
const archiving = ref(false)
const evaluation = ref<OfficialWorkPackageStatusEvaluation | null>(null)
const latestReceipt = ref<OfficialWorkPackageReceipt | null>(null)
const overrideReason = ref('')
const followUpOwner = ref('')
const followUpDueDate = ref('')
const followUpNote = ref('')
const receiptOptions = ref<ReviewedDocumentEvidenceOption[]>([])
const selectedReceiptKey = ref('')
const loadingCandidates = ref(false)

const receiptForm = reactive({
  receiptKind: 'ELECTRONIC_APPLICATION_RECEIPT',
  receivingCaseNo: '',
  submitter: '',
  receivedAt: '',
  receivedFileList: '',
  archiveStatus: 'ARCHIVED',
  note: '',
})

const packageClosed = computed(() => ['ARCHIVED', 'OVERRIDE'].includes(normalize(props.packageStatus)))
const archiveEvidenceReady = computed(() => props.receiptEvidenceReady || isArchiveReady(props.archiveStatus))
const overrideClosed = computed(() => normalize(props.packageStatus) === 'OVERRIDE')
const receiptFormComplete = computed(() =>
  Boolean(
    selectedReceipt.value
    && receiptForm.receivingCaseNo
    && receiptForm.submitter
    && receiptForm.receivedAt
    && receiptForm.receivedFileList.trim()
  )
)
const selectedReceipt = computed(() =>
  receiptOptions.value.find((option) => receiptKey(option) === selectedReceiptKey.value) || null
)
const overrideReady = computed(() => Boolean(overrideReason.value.trim() && followUpOwner.value.trim()))
const showReceiptFormWarning = computed(() => !receiptFormComplete.value && !archiveEvidenceReady.value && !overrideClosed.value)

const closureText = computed(() => {
  if (overrideClosed.value) return '例外处理已记录'
  if (archiveEvidenceReady.value) return '归档证据已满足'
  if (packageClosed.value) return '关闭缺少证据'
  return '待回执归档'
})

const closureTagType = computed((): 'success' | 'warning' | 'danger' | 'info' => {
  if (overrideClosed.value || archiveEvidenceReady.value) return 'success'
  if (packageClosed.value) return 'danger'
  return 'warning'
})

const archiveWarning = computed(() => {
  if (packageClosed.value && !archiveEvidenceReady.value && !overrideClosed.value) {
    return '工作包不能仅凭内部状态显示为已关闭，必须补充回执/归档证据或记录受控例外处理。'
  }
  return ''
})

watch(() => props.caseId, () => { void loadReceiptCandidates() })
onMounted(() => { void loadReceiptCandidates() })

async function loadReceiptCandidates() {
  loadingCandidates.value = true
  try {
    const documents = await getCaseDocumentsWithEvidence(props.caseId)
    receiptOptions.value = selectReviewedReceiptEvidenceOptions(documents, props.caseId)
    if (!receiptOptions.value.some((option) => receiptKey(option) === selectedReceiptKey.value)) {
      selectedReceiptKey.value = ''
    }
  } catch (error) {
    receiptOptions.value = []
    selectedReceiptKey.value = ''
    emit('error', error as ApiError)
  } finally {
    loadingCandidates.value = false
  }
}

async function handleCreateReceipt() {
  if (!receiptFormComplete.value) {
    ElMessage.warning('请先补齐回执附件、接收案件编号、提交人、接收时间和收到文件清单')
    return
  }

  savingReceipt.value = true
  try {
    if (!selectedReceipt.value) return
    latestReceipt.value = await createReviewedOfficialWorkPackageReceipt(
      props.packageId,
      props.caseId,
      selectedReceipt.value,
      {
      receipt_kind: receiptForm.receiptKind,
      receiving_case_no: receiptForm.receivingCaseNo,
      submitter: receiptForm.submitter,
      received_at: receiptForm.receivedAt,
      received_file_list: receiptForm.receivedFileList,
      archive_status: receiptForm.archiveStatus,
      note: receiptForm.note || null,
      },
    )
    ElMessage.success('回执元数据已记录')
  } catch (err) {
    emit('error', err as ApiError)
  } finally {
    savingReceipt.value = false
  }
}

async function handleArchive() {
  archiving.value = true
  try {
    const result = await archiveOfficialWorkPackage(props.packageId)
    evaluation.value = result.evaluation
    ElMessage.success(result.evaluation.can_archive ? '归档检查已通过' : '归档检查已返回阻止项')
    emit('refresh-requested')
  } catch (err) {
    emit('error', err as ApiError)
  } finally {
    archiving.value = false
  }
}

async function handleOverrideArchive() {
  if (!overrideReady.value) {
    ElMessage.warning('例外处理必须填写原因和跟进责任人')
    return
  }

  archiving.value = true
  try {
    const result = await archiveOfficialWorkPackage(props.packageId, {
      override_reason: overrideReason.value,
      follow_up_owner: followUpOwner.value,
      follow_up_due_date: followUpDueDate.value || null,
      follow_up_note: followUpNote.value || null,
    })
    evaluation.value = result.evaluation
    ElMessage.success('例外处理记录已提交')
    emit('refresh-requested')
  } catch (err) {
    emit('error', err as ApiError)
  } finally {
    archiving.value = false
  }
}

function normalize(value?: string | null): string {
  return String(value || '').trim().toUpperCase()
}

function receiptKey(option: ReviewedDocumentEvidenceOption): string {
  return `${option.attachment_id}:${option.evidence_version_id}:${option.content_hash}`
}

function isArchiveReady(value?: string | null): boolean {
  return ['ARCHIVED', 'DONE', 'READY', 'PRESENT', 'PASS'].includes(normalize(value))
}

function getPackageKindText(value?: string | null): string {
  const normalized = normalize(value)
  if (normalized === 'FILING_PREP') return '新申请递交'
  if (normalized === 'OA_REPLY') return 'OA答复'
  return value || '待确认'
}

function getReceiptKindText(value?: string | null): string {
  const normalized = normalize(value)
  if (normalized === 'ELECTRONIC_APPLICATION_RECEIPT') return '电子申请回执'
  if (normalized === 'MERGED_PDF') return '合并 PDF'
  if (normalized === 'OTHER_ARCHIVE_EVIDENCE') return '其他归档证明'
  return value || '待确认'
}

function getPackageStatusText(value?: string | null): string {
  const normalized = normalize(value)
  if (normalized === 'PREPARING') return '准备中'
  if (normalized === 'NEEDS_MAINTENANCE') return '需维护'
  if (normalized === 'NEEDS_CONFIRMATION') return '待确认'
  if (normalized === 'READY_FOR_EXTERNAL_SUBMIT') return '可人工提交'
  if (normalized === 'SUBMITTED') return '已提交'
  if (normalized === 'WAITING_RECEIPT') return '待回执'
  if (normalized === 'ARCHIVED') return '已归档'
  if (normalized === 'OVERRIDE') return '已例外处理'
  if (normalized === 'EXCEPTION') return '异常'
  return value || '待核对'
}

function getArchiveStatusText(value?: string | null): string {
  const normalized = normalize(value)
  if (normalized === 'ARCHIVED') return '已归档'
  if (normalized === 'PRESENT') return '已提供'
  if (normalized === 'READY' || normalized === 'DONE') return '已满足'
  if (normalized === 'MISSING') return '待维护'
  if (normalized === 'PENDING') return '待归档'
  if (normalized === 'NEEDS_REVIEW') return '需复核'
  return value || '待确认'
}
</script>

<style scoped>
.receipt-archive-panel {
  display: grid;
  gap: 16px;
}

.archive-subtitle {
  margin: -6px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.archive-status-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.archive-status-card {
  display: grid;
  gap: 6px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.archive-status-card span {
  color: var(--text-sub);
  font-size: 12px;
}

.archive-status-card strong {
  color: var(--text-main);
  font-size: 14px;
  overflow-wrap: anywhere;
}

.archive-form,
.override-form {
  display: grid;
  gap: 12px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.form-grid :deep(.el-date-editor),
.form-grid :deep(.el-select) {
  width: 100%;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.form-warning {
  color: #b45309;
  font-size: 12px;
}

.receipt-summary {
  display: grid;
  gap: 10px;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 12px;
  background: #eff6ff;
}

.receipt-summary-title {
  color: var(--text-main);
  font-weight: 600;
}

.receipt-summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.receipt-summary-grid > div,
.received-file-list {
  display: grid;
  gap: 4px;
}

.receipt-summary span,
.received-file-list span {
  color: var(--text-sub);
  font-size: 12px;
}

.receipt-summary strong,
.received-file-list p {
  margin: 0;
  color: var(--text-main);
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.evaluation-block {
  display: grid;
  gap: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
}

.evaluation-title,
.evaluation-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.evaluation-meta {
  color: var(--text-sub);
  font-size: 13px;
}

@media (max-width: 980px) {
  .archive-status-grid,
  .receipt-summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .archive-status-grid,
  .receipt-summary-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
