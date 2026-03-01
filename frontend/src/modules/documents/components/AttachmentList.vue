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
  gap: 2px;
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

.attachment-error {
  margin-bottom: 12px;
}
</style>
