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
        <el-button type="primary" :loading="uploading" @click="handleUploadConfirm">
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { getAttachments, uploadAttachment, downloadAttachment } from '../../../api/documents'
import type { Attachment } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const props = defineProps<{
  documentId: string | number
}>()

const emit = defineEmits<{
  uploaded: []
}>()

const attachments = ref<Attachment[]>([])
const loading = ref(false)
const uploading = ref(false)
const error = ref<ApiError | null>(null)
const downloadingId = ref<string | null>(null)
const uploadDialogVisible = ref(false)
const selectedUploadFile = ref<File | null>(null)
const selectedUploadFileName = ref('')
const uploadDraft = reactive({
  official_file_role: '',
  source_role_alias: '',
})

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
    attachments.value = await getAttachments(props.documentId)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
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

onMounted(() => {
  fetchAttachments()
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
}
</style>
