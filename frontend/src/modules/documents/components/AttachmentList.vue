<template>
  <div class="attachment-section">
    <div class="widget-title">附件</div>

    <!-- Error Banner -->
    <div v-if="error" class="attachment-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Upload Area -->
    <div class="attachment-upload">
      <el-button
        size="small"
        :loading="uploading"
        data-testid="attachment-open-upload"
        @click="openUploadDialog"
      >
        <span v-if="!uploading">上传附件</span>
        <span v-else>上传中...</span>
      </el-button>
    </div>

    <el-dialog
      v-model="uploadDialogVisible"
      data-testid="attachment-upload-dialog"
      title="上传附件"
      width="520px"
      @closed="resetUploadDraft"
    >
      <el-form label-position="top" class="attachment-upload-form">
        <el-form-item label="选择文件">
          <el-upload
            :action="''"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            :disabled="uploading"
            data-testid="attachment-file-picker"
            class="upload-control"
          >
            <el-button size="small">选择文件</el-button>
          </el-upload>
          <span v-if="selectedUploadFileName" class="selected-file-name">
            {{ selectedUploadFileName }}
          </span>
        </el-form-item>

        <el-form-item label="附件角色">
          <el-select
            v-model="uploadDraft.official_file_role"
            clearable
            filterable
            placeholder="选择附件角色"
            class="upload-dialog-select"
          >
            <el-option
              v-for="option in officialRoleOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="历史别名（可选）">
          <el-select
            v-model="uploadDraft.source_role_alias"
            clearable
            filterable
            placeholder="选择历史别名（可选）"
            class="upload-dialog-select"
          >
            <el-option
              v-for="alias in historicalAliasOptions"
              :key="alias"
              :label="alias"
              :value="alias"
            />
          </el-select>
        </el-form-item>

        <div class="upload-preview">
          <span>上传位置：{{ getDraftUploadPositionText() }}</span>
          <span>用途：{{ getDraftPackageUsageText() }}</span>
        </div>
      </el-form>

      <template #footer>
        <el-button :disabled="uploading" @click="cancelUploadDialog">取消</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="uploading || !canConfirmUpload"
          @click="handleUploadConfirm"
        >
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <!-- Loading -->
    <div v-if="loading" class="attachment-loading">
      <el-skeleton :rows="2" animated />
    </div>

    <!-- Attachment List -->
    <template v-else>
      <div v-if="attachments.length === 0" class="attachment-empty">
        <span class="empty-text">暂无附件</span>
      </div>
      <div v-else class="attachment-list">
        <div
          v-for="att in attachments"
          :key="att.id"
          class="attachment-item"
          :data-testid="att.evidence_version_id ? `attachment-${att.evidence_version_id}` : undefined"
        >
          <div class="attachment-info">
            <span class="attachment-name">{{ att.filename }}</span>
            <span class="attachment-size">{{ formatSize(att.file_size) }}</span>
            <div class="attachment-role-tags">
              <el-tag :type="getGateTagType(att)" size="small">{{ getGateClassification(att) }}</el-tag>
              <el-tag size="small" type="info">官方文件角色：{{ getOfficialRoleText(att.official_file_role) }}</el-tag>
              <el-tag v-if="att.source_role_alias" size="small" type="warning">
                历史别名：{{ att.source_role_alias }}
              </el-tag>
              <el-tag v-if="att.is_archive_evidence" size="small" type="info">归档证据</el-tag>
              <el-tag v-if="att.is_receipt_evidence" size="small" type="success">回执证据</el-tag>
            </div>
            <div class="attachment-official-meta">
              <span>上传位置：{{ getUploadPositionText(att.external_upload_position) }}</span>
              <span>内容哈希：{{ formatHash(att.content_hash) }}</span>
              <span>状态：{{ getPackageUsageHintText(att.package_usage_hint) }}</span>
            </div>
            <div v-if="att.evidence_version_id" class="attachment-review-meta">
              <span>创建人：{{ att.creator_id || '待确认' }}</span>
              <span>复核人：{{ att.reviewer_id || '未复核' }}</span>
              <el-tag :type="getReviewTagType(att.review_state)" size="small">
                复核状态：{{ getReviewStateText(att.review_state) }}
              </el-tag>
            </div>
            <span v-if="isSelfReview(att)" class="self-review-warning">
              创建人不能复核自己的证据版本
            </span>
          </div>
          <div class="attachment-actions">
            <div v-if="showReviewActions(att)" class="attachment-review-actions">
              <el-button
                size="small"
                type="success"
                :loading="reviewingKey === `${att.evidence_version_id}:APPROVE`"
                :disabled="reviewActionDisabled(att)"
                @click="handleReview(att, 'APPROVE')"
              >
                通过
              </el-button>
              <el-button
                size="small"
                type="danger"
                plain
                :loading="reviewingKey === `${att.evidence_version_id}:REJECT`"
                :disabled="reviewActionDisabled(att)"
                @click="handleReview(att, 'REJECT')"
              >
                驳回
              </el-button>
            </div>
            <el-button
              size="small"
              text
              :loading="downloadingId === att.id"
              @click="handleDownload(att)"
            >
              ⬇️ 下载
            </el-button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import {
  downloadAttachment,
  getDocument,
  reviewDocumentEvidence,
  uploadAttachment,
} from '../../../api/documents'
import { http } from '../../../api/http'
import type { Attachment, DocumentEvidenceReviewPayload } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { useAuthStore } from '../../../stores/auth'

const props = defineProps<{
  documentId: string | number
}>()

const emit = defineEmits<{
  uploaded: []
}>()

const authStore = useAuthStore()
const attachments = ref<Attachment[]>([])
const loading = ref(false)
const uploading = ref(false)
const error = ref<ApiError | null>(null)
const downloadingId = ref<string | null>(null)
const reviewingKey = ref<string | null>(null)
const caseId = ref<string | null>(null)
const currentUserId = ref<string | null>(null)
const reviewIntents = new Map<string, DocumentEvidenceReviewPayload>()
const uploadDialogVisible = ref(false)
const selectedUploadFile = ref<File | null>(null)
const selectedUploadFileName = ref('')
const uploadDraft = reactive({
  official_file_role: '',
  source_role_alias: '',
})
const canConfirmUpload = computed(() => (
  selectedUploadFile.value !== null && uploadDraft.official_file_role.trim() !== ''
))

const OFFICIAL_ROLE_TEXT: Record<string, string> = {
  TECHNICAL_DISCLOSURE: '技术交底书',
  COMMISSION_INSTRUCTION: '委托指示',
  FILING_FULL_WORD: '完整递交文件 Word',
  FILING_ABSTRACT: '摘要',
  CLAIMS: '权利要求书',
  FILING_DOCUMENT: '递交文件',
  FILING_XML_ZIP: 'XML压缩包',
  FILING_MERGED_PDF: '合并PDF',
  FILING_CLAIMS: '权利要求书',
  FILING_DESCRIPTION: '说明书',
  FILING_DRAWINGS: '说明书附图',
  FILING_SEQUENCE_LISTING: '序列表',
  OA_STATEMENT_WORD: 'OA意见陈述 Word',
  OA_STATEMENT_PDF: 'OA意见陈述 PDF',
  OA_MODIFIED_CLAIMS: '修改后的权利要求书',
  OA_AMENDMENT_COMPARISON: '修改对照页',
  OA_OTHER_PROOF: '其他证明文件',
  OA_ADDITIONAL_FILE: '附加文件',
  SOURCE_DOCUMENT: '来源文书',
  SOURCE_OFFICIAL_DOCUMENT: '来源官文',
  ELECTRONIC_RECEIPT: '电子申请回执',
  OFFICIAL_NOTICE_PDF: '官方通知书PDF',
  RECEIPT_PDF: '回执',
  MERGED_PDF: '合并PDF',
}

const officialRoleOptions = [
  { value: 'TECHNICAL_DISCLOSURE', label: '技术交底书' },
  { value: 'COMMISSION_INSTRUCTION', label: '委托指示' },
  { value: 'FILING_FULL_WORD', label: '完整递交文件 Word' },
  { value: 'FILING_XML_ZIP', label: 'XML压缩包' },
  { value: 'FILING_MERGED_PDF', label: '合并PDF' },
  { value: 'OFFICIAL_NOTICE_PDF', label: '官方通知书PDF' },
  { value: 'CLAIMS', label: '权利要求书' },
  { value: 'OA_STATEMENT_WORD', label: 'OA意见陈述 Word' },
  { value: 'OA_STATEMENT_PDF', label: 'OA意见陈述 PDF' },
  { value: 'OA_MODIFIED_CLAIMS', label: '修改后的权利要求书' },
  { value: 'OA_AMENDMENT_COMPARISON', label: '修改对照页' },
  { value: 'OA_OTHER_PROOF', label: '其他证明文件' },
  { value: 'ELECTRONIC_RECEIPT', label: '电子申请回执' },
]

const historicalAliasOptions = [
  'PCT 公开文本',
  '补正后说明书',
  '递交电子申请文件',
  '客户提供原始文件',
]

const PACKAGE_USAGE_HINT_TEXT: Record<string, string> = {
  CASE_INTAKE: '收案材料',
  FILING_PREP: '新申请递交准备',
  OA_REPLY: 'OA答复准备',
  FILING_ARCHIVE: '新申请归档',
  RECEIPT_ARCHIVE: '回执归档',
  READY: '已准备',
  PRESENT: '已提供',
  DONE: '已完成',
  MISSING: '待补齐',
  ARCHIVED: '已归档',
  RECEIPT_EVIDENCE: '回执证据',
  ARCHIVE_EVIDENCE: '归档证据',
}

const UPLOAD_POSITION_TEXT: Record<string, string> = {
  FILING_SOURCE_WORD: '新申请源文件',
  FILING_XML_ZIP_AUTO_ASSIGN: 'XML压缩包自动匹配',
  FILING_XML_ZIP_UPLOAD: 'XML压缩包上传',
  OA_REPLY_STATEMENT_SOURCE: 'OA意见陈述源文件',
  OA_REPLY_OTHER_PROOF_FILES: 'OA其他证明文件',
  OA_REPLY_CLAIMS: 'OA权利要求书',
  OA_REPLY_COMPARISON_PAGE: 'OA修改对照页',
  OA_REPLY_ADDITIONAL_FILES: 'OA附加文件',
  FILING_ARCHIVE: '新申请归档',
  RECEIPT_ARCHIVE: '回执归档',
}

const ROLE_UPLOAD_POSITION: Record<string, string> = {
  FILING_FULL_WORD: 'FILING_SOURCE_WORD',
  FILING_XML_ZIP: 'FILING_XML_ZIP_UPLOAD',
  FILING_MERGED_PDF: 'FILING_ARCHIVE',
  OFFICIAL_NOTICE_PDF: 'OFFICIAL_NOTICE_EVIDENCE',
  CLAIMS: 'FILING_XML_ZIP_AUTO_ASSIGN',
  OA_STATEMENT_WORD: 'OA_REPLY_STATEMENT_SOURCE',
  OA_STATEMENT_PDF: 'OA_REPLY_OTHER_PROOF_FILES',
  OA_MODIFIED_CLAIMS: 'OA_REPLY_CLAIMS',
  OA_AMENDMENT_COMPARISON: 'OA_REPLY_COMPARISON_PAGE',
  OA_OTHER_PROOF: 'OA_REPLY_OTHER_PROOF_FILES',
  ELECTRONIC_RECEIPT: 'RECEIPT_ARCHIVE',
}

const ROLE_PACKAGE_USAGE_HINT: Record<string, string> = {
  TECHNICAL_DISCLOSURE: 'CASE_INTAKE',
  COMMISSION_INSTRUCTION: 'CASE_INTAKE',
  FILING_FULL_WORD: 'FILING_PREP',
  FILING_XML_ZIP: 'FILING_PREP',
  FILING_MERGED_PDF: 'FILING_ARCHIVE',
  OFFICIAL_NOTICE_PDF: 'OFFICIAL_NOTICE_EVIDENCE',
  CLAIMS: 'FILING_PREP',
  OA_STATEMENT_WORD: 'OA_REPLY',
  OA_STATEMENT_PDF: 'OA_REPLY',
  OA_MODIFIED_CLAIMS: 'OA_REPLY',
  OA_AMENDMENT_COMPARISON: 'OA_REPLY',
  OA_OTHER_PROOF: 'OA_REPLY',
  ELECTRONIC_RECEIPT: 'RECEIPT_ARCHIVE',
}

async function fetchAttachments() {
  loading.value = true
  error.value = null

  try {
    const document = await getDocument(props.documentId)
    attachments.value = document.attachments || []
    caseId.value = document.case_id || null
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function fetchCurrentUserId() {
  try {
    const response = await http.get<{ user?: { id?: string } }>('/auth/me')
    currentUserId.value = response.data.user?.id?.trim() || null
  } catch {
    currentUserId.value = null
  }
}

function showReviewActions(att: Attachment): boolean {
  return Boolean(
    authStore.hasPermission('Doc.Edit')
    && att.evidence_version_id
    && att.review_state === 'PENDING'
  )
}

function isSelfReview(att: Attachment): boolean {
  return Boolean(att.creator_id && currentUserId.value && att.creator_id === currentUserId.value)
}

function reviewActionDisabled(att: Attachment): boolean {
  return Boolean(
    reviewingKey.value
    || !caseId.value
    || !currentUserId.value
    || isSelfReview(att)
  )
}

function getReviewIntent(
  evidenceVersionId: string,
  decision: 'APPROVE' | 'REJECT',
): DocumentEvidenceReviewPayload {
  const intentKey = `${evidenceVersionId}:${decision}`
  const existing = reviewIntents.get(intentKey)
  if (existing) return existing
  const payload: DocumentEvidenceReviewPayload = {
    case_id: caseId.value!,
    decision,
    reviewed_at: new Date().toISOString().slice(0, 19),
    idempotency_key: `review-ui:${evidenceVersionId}:${decision}`,
  }
  reviewIntents.set(intentKey, payload)
  return payload
}

async function handleReview(att: Attachment, decision: 'APPROVE' | 'REJECT') {
  if (!att.evidence_version_id || !att.role || !caseId.value || !currentUserId.value) {
    ElMessage.error('暂时无法确认复核所需信息，请刷新后重试。')
    return
  }
  if (isSelfReview(att)) {
    ElMessage.warning('创建人不能复核自己的证据版本。')
    return
  }

  reviewingKey.value = `${att.evidence_version_id}:${decision}`
  error.value = null

  try {
    const payload = getReviewIntent(att.evidence_version_id, decision)
    const projection = await reviewDocumentEvidence(
      String(props.documentId),
      att.evidence_version_id,
      payload,
      {
        expectedReviewerId: currentUserId.value,
        role: att.role,
        isCurrent: att.is_current === true,
        isFinal: att.is_final === true,
      },
    )
    att.creator_id = projection.creator_id
    att.reviewer_id = projection.reviewer_id
    att.review_state = projection.review_state
    att.is_current = projection.is_current
    att.is_final = projection.is_final
    ElMessage.success(decision === 'APPROVE' ? '附件复核已通过' : '附件复核已驳回')
  } catch (err) {
    error.value = getReviewError(err)
  } finally {
    reviewingKey.value = null
  }
}

function getReviewError(err: unknown): ApiError {
  const apiError = (err || {}) as Partial<ApiError>
  const status = typeof apiError.status === 'number' ? apiError.status : 0
  const code = typeof apiError.code === 'string' ? apiError.code : 'REVIEW_FAILED'
  let message = '附件复核失败，请稍后重试。'

  if (code === 'EVIDENCE_REVIEW_SELF_REVIEW') {
    message = '创建人不能复核自己的证据版本。'
  } else if (status === 400 || status === 422) {
    message = '复核请求无效，请核对后重试。'
  } else if (status === 401) {
    message = '登录已失效，请重新登录。'
  } else if (status === 403) {
    message = '您没有复核附件的权限。'
  } else if (status === 404) {
    message = '未找到待复核的证据版本。'
  } else if (status === 409) {
    message = '附件复核状态已变化，请刷新后重试。'
  }

  return {
    status,
    code,
    message,
    details: apiError.details,
    requestId: apiError.requestId,
  }
}

function openUploadDialog() {
  resetUploadDraft()
  error.value = null
  uploadDialogVisible.value = true
}

function cancelUploadDialog() {
  uploadDialogVisible.value = false
}

function resetUploadDraft() {
  selectedUploadFile.value = null
  selectedUploadFileName.value = ''
  uploadDraft.official_file_role = ''
  uploadDraft.source_role_alias = ''
}

async function handleFileChange(uploadFile: UploadFile) {
  if (!uploadFile.raw) return
  selectedUploadFile.value = uploadFile.raw
  selectedUploadFileName.value = uploadFile.name || uploadFile.raw.name
}

async function handleUploadConfirm() {
  if (!selectedUploadFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  if (!uploadDraft.official_file_role.trim()) {
    ElMessage.warning('请选择附件角色')
    return
  }
  uploading.value = true
  error.value = null

  try {
    await uploadAttachment(props.documentId, selectedUploadFile.value, {
      official_file_role: uploadDraft.official_file_role || null,
      source_role_alias: uploadDraft.source_role_alias || null,
    })
    ElMessage.success('附件上传成功')
    uploadDialogVisible.value = false
    resetUploadDraft()
    await fetchAttachments()
    emit('uploaded')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    uploading.value = false
  }
}

async function handleDownload(att: Attachment) {
  downloadingId.value = String(att.id)
  error.value = null

  try {
    const blob = await downloadAttachment(props.documentId, att.id)
    
    // Trigger browser download
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = att.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    downloadingId.value = null
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function normalizeCode(value?: string | null): string {
  return String(value || '').trim().toUpperCase()
}

function getOfficialRoleText(role?: string | null): string {
  const normalized = normalizeCode(role)
  if (!normalized) return '未标注'
  return OFFICIAL_ROLE_TEXT[normalized] || '官方文件角色待确认'
}

function getPackageUsageHintText(value?: string | null): string {
  const normalized = normalizeCode(value)
  if (!normalized) return '未标注'
  return PACKAGE_USAGE_HINT_TEXT[normalized] || '待核对'
}

function getUploadPositionText(value?: string | null): string {
  const normalized = normalizeCode(value)
  if (!normalized) return '未指定'
  return UPLOAD_POSITION_TEXT[normalized] || normalized
}

function getDraftUploadPositionText(): string {
  const role = normalizeCode(uploadDraft.official_file_role)
  return getUploadPositionText(ROLE_UPLOAD_POSITION[role])
}

function getDraftPackageUsageText(): string {
  const role = normalizeCode(uploadDraft.official_file_role)
  return getPackageUsageHintText(ROLE_PACKAGE_USAGE_HINT[role])
}

function getGateClassification(att: Attachment): string {
  const role = normalizeCode(att.official_file_role)
  if (role === 'TECHNICAL_DISCLOSURE' || role === 'COMMISSION_INSTRUCTION') return '收案门禁'
  if (role.startsWith('FILING_')) return '递交文件'
  if (role.startsWith('OA_')) return 'OA附件'
  if (role.includes('RECEIPT') || att.is_receipt_evidence) return '回执'
  if (role.includes('MERGED_PDF') || att.is_archive_evidence) return '归档证据'
  if (att.source_role_alias) return '历史别名'
  return '未分类'
}

function getGateTagType(att: Attachment): 'success' | 'warning' | 'danger' | 'info' {
  const classification = getGateClassification(att)
  if (classification === '收案门禁') return 'danger'
  if (classification === '递交文件' || classification === 'OA附件') return 'success'
  if (classification === '回执' || classification === '归档证据') return 'warning'
  return 'info'
}

function formatHash(value?: string | null): string {
  if (!value) return '未生成'
  return value.length > 12 ? `${value.slice(0, 12)}...` : value
}

function getReviewStateText(state?: Attachment['review_state']): string {
  if (state === 'APPROVED') return '已通过'
  if (state === 'REJECTED') return '已驳回'
  if (state === 'PENDING') return '待复核'
  return '未关联'
}

function getReviewTagType(
  state?: Attachment['review_state']
): 'success' | 'warning' | 'danger' | 'info' {
  if (state === 'APPROVED') return 'success'
  if (state === 'REJECTED') return 'danger'
  if (state === 'PENDING') return 'warning'
  return 'info'
}

onMounted(async () => {
  await Promise.all([fetchAttachments(), fetchCurrentUserId()])
})
</script>

<style scoped>
.attachment-section {
  margin-top: 16px;
}

.attachment-upload {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.attachment-upload-form {
  display: grid;
  gap: 4px;
}

.upload-dialog-select {
  width: 100%;
}

.selected-file-name {
  margin-left: 12px;
  color: #4b5563;
  font-size: 13px;
}

.upload-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 8px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #4b5563;
  font-size: 13px;
  background: #f9fafb;
}

.upload-control {
  display: inline-block;
}

.attachment-loading {
  padding: 8px 0;
}

.attachment-empty {
  padding: 16px 0;
  text-align: center;
}

.empty-text {
  color: var(--text-sub);
  font-size: 13px;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #F8FAFC;
  border-radius: var(--radius-base);
  border: 1px solid #E2E8F0;
}

.attachment-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.attachment-name {
  font-size: 13px;
  color: var(--text-main);
  font-weight: 500;
}

.attachment-size {
  font-size: 12px;
  color: var(--text-sub);
}

.attachment-role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.attachment-official-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px 12px;
  color: var(--text-sub);
  font-size: 12px;
}

.attachment-review-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 12px;
  color: var(--text-sub);
  font-size: 12px;
}

.attachment-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.attachment-review-actions {
  display: flex;
}

.self-review-warning {
  color: var(--el-color-danger);
  font-size: 12px;
}

.attachment-error {
  margin-bottom: 12px;
}

@media (max-width: 720px) {
  .attachment-item {
    align-items: flex-start;
    flex-direction: column;
  }

  .attachment-official-meta {
    grid-template-columns: 1fr;
  }

  .attachment-actions {
    align-items: flex-start;
  }
}
</style>
