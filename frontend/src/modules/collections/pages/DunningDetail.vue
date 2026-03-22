<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回列表
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="6" />

    <div v-else-if="dunningItem" class="detail-content">
      <div class="detail-card">
        <div class="detail-card-header">
          <h1 class="detail-title">催款批次详情</h1>
          <el-tag :type="getStatusTagType(dunningItem.status)" size="large">
            {{ getStatusText(dunningItem.status) }}
          </el-tag>
        </div>
        <p class="detail-subtitle">
          催款单号：<span class="mono-text">{{ dunningItem.dunning_no || `DN-${dunningItem.id}` }}</span>
        </p>
      </div>

      <div class="detail-card">
        <h2 class="section-title">批次信息</h2>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="批次编号">{{ dunningItem.id }}</el-descriptions-item>
          <el-descriptions-item label="客户编号">{{ dunningItem.client_id }}</el-descriptions-item>
          <el-descriptions-item label="催款轮次">第 {{ dunningItem.round_no }} 轮</el-descriptions-item>
          <el-descriptions-item label="批次状态">{{ getStatusText(dunningItem.status) }}</el-descriptions-item>
          <el-descriptions-item label="截止日期">{{ formatDate(dunningItem.to_date) }}</el-descriptions-item>
          <el-descriptions-item label="发送日期">{{ formatDate(dunningItem.sent_date) }}</el-descriptions-item>
          <el-descriptions-item label="批次总金额">
            <span class="mono-text">{{ formatAmount(dunningItem.total_amount, dunningItem.currency) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="币种">{{ dunningItem.currency || '—' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ dunningItem.remark?.trim() || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(dunningItem.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDateTime(dunningItem.updated_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDunningDetail, mapCollectionsError } from '../../../api/collections'
import type { CollectionsApiError, DunningDetail } from '../../../api/collections.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

type TagType = '' | 'success' | 'warning' | 'info' | 'danger'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const dunningItem = ref<DunningDetail | null>(null)
const error = ref<CollectionsApiError | null>(null)

const dunningId = computed(() => {
  const raw = route.params.id
  const numericId = Number(raw)
  if (!Number.isInteger(numericId) || numericId <= 0) return null
  return numericId
})

function extractListQuery(): Record<string, string> {
  const query: Record<string, string> = {}
  const maybeKeys = ['round_no', 'status', 'page', 'page_size']

  for (const key of maybeKeys) {
    const value = route.query[key]
    if (typeof value === 'string' && value.trim() !== '') {
      query[key] = value
    }
  }

  return query
}

async function fetchDunningItem() {
  if (dunningId.value === null) {
    error.value = {
      status: 404,
      code: 'DUNNING_NOT_FOUND',
      message: '催款批次不存在或编号无效。',
      category: 'not_found',
    }
    dunningItem.value = null
    return
  }

  loading.value = true
  error.value = null

  try {
    const detail = await getDunningDetail(dunningId.value)
    dunningItem.value = detail
  } catch (err) {
    error.value = mapCollectionsError(err)
    dunningItem.value = null
  } finally {
    loading.value = false
  }
}

function goBack() {
  const query = extractListQuery()
  router.push({
    path: '/collections/dunning',
    query,
  })
}

function getStatusText(status: string): string {
  switch (status) {
    case 'DRAFT':
      return '草稿'
    case 'SENT':
      return '已发送'
    case 'CANCELLED':
      return '已取消'
    case 'CLOSED':
      return '已关闭'
    default:
      return '未知'
  }
}

function getStatusTagType(status: string): TagType {
  switch (status) {
    case 'DRAFT':
      return 'warning'
    case 'SENT':
      return 'success'
    case 'CANCELLED':
      return 'info'
    case 'CLOSED':
      return 'danger'
    default:
      return ''
  }
}

function formatDate(input: string | null): string {
  if (!input) return '—'
  const date = new Date(input)
  if (Number.isNaN(date.getTime())) return input
  return date.toLocaleDateString('zh-CN')
}

function formatDateTime(input: string): string {
  const date = new Date(input)
  if (Number.isNaN(date.getTime())) return input
  return date.toLocaleString('zh-CN')
}

function formatAmount(amount: number, currency?: string): string {
  const curr = currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(amount)
}

onMounted(() => {
  fetchDunningItem()
})
</script>

<style scoped>
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
}

.detail-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-title {
  margin: 0;
  font-size: 24px;
}

.detail-subtitle {
  margin: 10px 0 0;
  color: var(--text-secondary);
}

.section-title {
  margin: 0 0 12px;
  font-size: 18px;
}

.mono-text {
  font-family: var(--font-mono);
}

.page-error {
  outline: none;
}

:deep(.el-button:focus-visible),
:deep(.el-input__wrapper:focus-within),
:deep(.el-select__wrapper.is-focused),
:deep(.el-textarea__inner:focus-visible),
:deep(.el-date-editor:focus-within) {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
}
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .page-header-right,
  .filter-actions,
  .action-row,
  .form-actions,
  .batch-action-bar {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-header-right :deep(.el-button),
  .filter-actions :deep(.el-button),
  .action-row :deep(.el-button),
  .form-actions :deep(.el-button),
  .batch-action-bar :deep(.el-button) {
    flex: 1;
    min-width: 120px;
  }
}
</style>
