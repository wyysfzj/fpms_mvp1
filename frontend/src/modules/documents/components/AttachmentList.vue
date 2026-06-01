<template>
  <div class="attachment-section">
    <div class="widget-title">附件</div>

    <!-- Error Banner -->
    <div v-if="error" class="attachment-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Upload Area -->
    <div class="attachment-upload">
      <el-upload
        :action="''"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
        :disabled="uploading"
        class="upload-control"
      >
        <el-button size="small" :loading="uploading">
          <span v-if="!uploading">📎 上传文件</span>
          <span v-else>上传中...</span>
        </el-button>
      </el-upload>
    </div>

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
              <span>上传位置：{{ att.external_upload_position || '未指定' }}</span>
              <span>内容哈希：{{ formatHash(att.content_hash) }}</span>
              <span>状态：{{ att.package_usage_hint || '未标注' }}</span>
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
import { ref, onMounted } from 'vue'
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

const OFFICIAL_ROLE_TEXT: Record<string, string> = {
  TECHNICAL_DISCLOSURE: '技术交底书',
  COMMISSION_INSTRUCTION: '委托指示',
  FILING_DOCUMENT: '递交文件',
  FILING_XML_ZIP: 'XML压缩包',
  FILING_MERGED_PDF: '合并PDF',
  FILING_CLAIMS: '权利要求书',
  OA_STATEMENT_WORD: 'OA意见陈述 Word',
  OA_STATEMENT_PDF: 'OA意见陈述 PDF',
  OA_MODIFIED_CLAIMS: 'OA修改后权利要求书',
  OA_AMENDMENT_COMPARISON: 'OA修改对照页',
  OA_OTHER_PROOF: 'OA其他证明文件',
  OA_ADDITIONAL_FILE: 'OA附加文件',
  RECEIPT_PDF: '回执',
  MERGED_PDF: '合并PDF',
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

async function handleFileChange(uploadFile: UploadFile) {
  if (!uploadFile.raw) return

  uploading.value = true
  error.value = null

  try {
    await uploadAttachment(props.documentId, uploadFile.raw)
    ElMessage.success('文件上传成功')
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
  return OFFICIAL_ROLE_TEXT[normalized] || normalized
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
