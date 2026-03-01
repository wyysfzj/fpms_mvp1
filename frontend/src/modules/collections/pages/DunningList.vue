<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">催款批次</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/collections/dunning/new">
          <el-button type="primary" aria-label="创建催款批次">创建催款批次</el-button>
        </router-link>
      </div>
    </div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-select
          v-model="filterRoundNo"
          aria-label="催款轮次筛选"
          clearable
          placeholder="选择催款轮次"
          class="full-width"
          @change="onFilterChange"
        >
          <el-option label="全部轮次" :value="undefined" />
          <el-option v-for="option in roundOptions" :key="option" :label="`第 ${option} 轮`" :value="option" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-select
          v-model="filterStatus"
          aria-label="催款状态筛选"
          clearable
          placeholder="选择批次状态"
          class="full-width"
          @change="onFilterChange"
        >
          <el-option label="全部状态" :value="undefined" />
          <el-option
            v-for="option in statusOptions"
            :key="option"
            :label="getStatusText(option)"
            :value="option"
          />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-button aria-label="重置催款筛选" @click="resetFilters">重置筛选</el-button>
      </el-col>
    </el-row>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="10" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无催款批次"
        message="请调整筛选条件或先创建新的催款批次。"
        icon="DN"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        :data="dunningItems"
        aria-label="催款批次列表"
        stripe
        size="small"
        class="compact-table"
        @row-click="handleRowClick"
      >
        <el-table-column label="催款单号" min-width="170">
          <template #default="{ row }">
            <span class="mono-text">{{ row.dunning_no || `DN-${row.id}` }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="client_id" label="客户编号" min-width="140" />
        <el-table-column label="轮次" width="90" align="center">
          <template #default="{ row }">
            第 {{ row.round_no }} 轮
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="截止日期" width="130">
          <template #default="{ row }">
            {{ formatDate(row.to_date) }}
          </template>
        </el-table-column>
        <el-table-column label="总金额" width="170" align="right">
          <template #default="{ row }">
            <span class="mono-text">{{ formatAmount(row.total_amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="发送日期" width="130">
          <template #default="{ row }">
            {{ formatDate(row.sent_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="goToDetail(row.id)">查看明细</el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDunning, mapCollectionsError } from '../../../api/collections'
import type { CollectionsApiError, DunningBatchListItem } from '../../../api/collections.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

type DunningStatus = 'DRAFT' | 'SENT' | 'CANCELLED' | 'CLOSED' | 'UNKNOWN'
type TagType = '' | 'success' | 'warning' | 'info' | 'danger'

const router = useRouter()
const route = useRoute()

const dunningItems = ref<DunningBatchListItem[]>([])
const loading = ref(false)
const error = ref<CollectionsApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterRoundNo = ref<number | undefined>(undefined)
const filterStatus = ref<string | undefined>(undefined)

const roundOptions = [1, 2, 3, 4, 5]
const statusOptions: DunningStatus[] = ['DRAFT', 'SENT', 'CANCELLED', 'CLOSED', 'UNKNOWN']

const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function parsePositiveInt(value: unknown, fallback: number): number {
  if (typeof value !== 'string') return fallback
  const parsed = Number.parseInt(value, 10)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback
}

function parseRoundNo(value: unknown): number | undefined {
  if (typeof value !== 'string' || value.trim() === '') return undefined
  const parsed = Number.parseInt(value, 10)
  if (!Number.isInteger(parsed) || parsed <= 0) return undefined
  return parsed
}

function parseStatus(value: unknown): string | undefined {
  if (typeof value !== 'string' || value.trim() === '') return undefined
  return value
}

function hydrateStateFromQuery() {
  page.value = parsePositiveInt(route.query.page, 1)
  pageSize.value = parsePositiveInt(route.query.page_size, 20)
  filterRoundNo.value = parseRoundNo(route.query.round_no)
  filterStatus.value = parseStatus(route.query.status)
}

function buildListQuery(): Record<string, string> {
  const query: Record<string, string> = {
    page: String(page.value),
    page_size: String(pageSize.value),
  }

  if (filterRoundNo.value !== undefined) {
    query.round_no = String(filterRoundNo.value)
  }
  if (filterStatus.value) {
    query.status = filterStatus.value
  }

  return query
}

async function fetchDunningList() {
  loading.value = true
  error.value = null

  try {
    const result = await getDunning({
      page: page.value,
      page_size: pageSize.value,
      round_no: filterRoundNo.value,
      status: filterStatus.value,
    })
    dunningItems.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = mapCollectionsError(err)
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  fetchDunningList()
}

function resetFilters() {
  filterRoundNo.value = undefined
  filterStatus.value = undefined
  page.value = 1
  fetchDunningList()
}

function goToDetail(id: number) {
  router.push({
    path: `/collections/dunning/${id}`,
    query: buildListQuery(),
  })
}

function handleRowClick(row: DunningBatchListItem) {
  goToDetail(row.id)
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

function formatAmount(amount: number, currency?: string): string {
  const curr = currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(amount)
}

watch([page, pageSize], () => {
  fetchDunningList()
})

onMounted(() => {
  hydrateStateFromQuery()
  fetchDunningList()
})
</script>

<style scoped>
.full-width {
  width: 100%;
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
