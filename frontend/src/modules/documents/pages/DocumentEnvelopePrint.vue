<template>
  <div class="page-container envelope-page">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">信封打印预览</h1>
        <span class="page-count">当前文档</span>
      </div>
      <div class="page-header-right">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="handlePrint">打印</el-button>
      </div>
    </div>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="6" />

    <template v-else-if="preview">
      <el-card shadow="never" class="meta-card">
        <div class="meta-grid">
          <div class="meta-item">
            <span class="meta-label">案号</span>
            <span class="meta-value">{{ preview.case_no || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">客户</span>
            <span class="meta-value">{{ preview.client_name || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">地址来源</span>
            <span class="meta-value">{{ addressSourceLabel }}</span>
          </div>
        </div>
      </el-card>

      <el-card shadow="never" class="envelope-card">
        <div class="envelope-preview">
          <div class="envelope-recipient-label">收件人</div>
          <div class="envelope-recipient">{{ preview.recipient_name || '需要手工填写' }}</div>
          <div class="envelope-address">{{ preview.recipient_address || '当前没有可打印地址，请先补齐地址信息。' }}</div>
        </div>
      </el-card>

      <el-alert
        title="当前只关闭信封打印预览与地址来源展示，不记录打印日志。"
        type="info"
        :closable="false"
        show-icon
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getDocumentEnvelopePreview } from '../../../api/documents'
import type { DocumentEnvelopePreviewOut } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref<ApiError | null>(null)
const preview = ref<DocumentEnvelopePreviewOut | null>(null)

const documentId = computed(() => String(route.params.id || '').trim())
const addressSourceLabel = computed(() => {
  const value = preview.value?.address_source
  switch (value) {
    case 'CASE_DOC_ADDRESS':
      return '案卷收件地址'
    case 'CLIENT_DEFAULT_ADDRESS':
      return '客户默认地址'
    case 'FIRST_APPLICANT_ADDRESS':
      return '申请人首选地址'
    case 'MANUAL_REQUIRED':
      return '需要手工补录'
    default:
      return value ? '未知地址来源' : '-'
  }
})

async function fetchPreview() {
  if (!documentId.value) {
    return
  }
  loading.value = true
  error.value = null
  try {
    preview.value = await getDocumentEnvelopePreview(documentId.value)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function handlePrint() {
  window.print()
}

function goBack() {
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push('/documents/dispatch')
}

onMounted(fetchPreview)
</script>

<style scoped>
.meta-card,
.envelope-card {
  margin-bottom: 16px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.meta-value {
  color: var(--el-text-color-primary);
  font-size: 15px;
}

.envelope-preview {
  min-height: 220px;
  border: 1px dashed var(--el-border-color);
  border-radius: 12px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: linear-gradient(180deg, #fffdf7 0%, #ffffff 100%);
}

.envelope-recipient-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-bottom: 8px;
}

.envelope-recipient {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
}

.envelope-address {
  font-size: 16px;
  line-height: 1.8;
  white-space: pre-wrap;
}

@media (max-width: 900px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
