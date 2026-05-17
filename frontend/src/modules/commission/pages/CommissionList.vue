<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">提成记录查询</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
    </div>

    <el-row :gutter="12" class="filter-bar">
      <el-col :xs="24" :sm="12" :md="6" :lg="5">
        <el-input
          v-model.trim="filters.agent_id"
          aria-label="代理人筛选"
          placeholder="代理人编号"
          clearable
          @keyup.enter="onFilterChange"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="5">
        <el-input
          v-model.trim="filters.case_no"
          aria-label="案件筛选"
          placeholder="案号"
          clearable
          @keyup.enter="onFilterChange"
        />
      </el-col>
      <el-col :xs="12" :sm="8" :md="4" :lg="3">
        <el-select v-model="filters.status" aria-label="提成状态筛选" placeholder="状态" clearable>
          <el-option label="全部状态" value="" />
          <el-option label="进行中" value="OPEN" />
          <el-option label="已结算" value="SETTLED" />
          <el-option label="已取消" value="CANCELLED" />
          <el-option label="已作废" value="VOID" />
          <el-option label="已关闭" value="CLOSED" />
        </el-select>
      </el-col>
      <el-col :xs="12" :sm="16" :md="8" :lg="7">
        <el-date-picker
          v-model="filters.settleable_date_range"
          aria-label="可结算日期范围筛选"
          type="daterange"
          range-separator="至"
          start-placeholder="可结算日期开始"
          end-placeholder="可结算日期结束"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          class="w-full"
        />
      </el-col>
      <el-col :xs="24" :sm="16" :md="8" :lg="7">
        <el-date-picker
          v-model="filters.created_at_range"
          aria-label="创建日期范围筛选"
          type="daterange"
          range-separator="至"
          start-placeholder="创建日期开始"
          end-placeholder="创建日期结束"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          class="w-full"
        />
      </el-col>
      <el-col :xs="24" :sm="8" :md="4" :lg="3" class="filter-actions">
        <el-button type="primary" aria-label="查询提成记录" @click="onFilterChange">查询</el-button>
        <el-button aria-label="重置提成筛选" @click="resetFilters">重置</el-button>
      </el-col>
    </el-row>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="10" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无提成记录"
        message="调整筛选条件后重试。"
        icon="📄"
      />
    </div>

    <div v-else class="page-table">
      <el-table :data="records" aria-label="提成记录列表" stripe size="small" class="compact-table">
        <el-table-column prop="case_no" label="案号" min-width="160">
          <template #default="{ row }">
            {{ formatCaseDisplay(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="agent_id" label="代理人" min-width="160">
          <template #default="{ row }">
            {{ formatAgentDisplay(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="fee_type" label="费用类型" width="120">
          <template #default="{ row }">
            {{ formatFeeTypeDisplay(row.fee_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="base_fee" label="基础费用" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.base_fee) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="阶段完成" min-width="150">
          <template #default="{ row }">
            <div class="stage-tags">
              <el-tag :type="row.s1_done ? 'success' : 'info'" size="small">
                S1 {{ row.s1_done ? '已完成' : '未完成' }}
              </el-tag>
              <el-tag :type="row.s2_done ? 'success' : 'info'" size="small">
                S2 {{ row.s2_done ? '已完成' : '未完成' }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="s1_amount" label="S1 金额" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.s1_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="s2_amount" label="S2 金额" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.s2_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_settleable" label="可结算" width="90">
          <template #default="{ row }">
            <el-tag :type="settleableTagType(row.is_settleable)" size="small">
              {{ settleableLabel(row.is_settleable) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="待回款" width="90">
          <template #default="{ row }">
            <el-tag :type="row.wait_pay ? 'warning' : 'info'" size="small">
              {{ row.wait_pay ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="强制结算" width="100">
          <template #default="{ row }">
            <el-tag :type="row.force_settle ? 'success' : 'info'" size="small">
              {{ row.force_settle ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="settleable_date" label="可结算日期" width="130">
          <template #default="{ row }">
            {{ row.settleable_date || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
      />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { getCommission } from '../../../api/commission'
import type { CommissionListParams, CommissionRecord } from '../../../api/commission.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const records = ref<CommissionRecord[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

const filters = reactive({
  agent_id: '',
  case_no: '',
  status: '',
  settleable_date_range: [] as string[],
  created_at_range: [] as string[],
})

function normalizeOptional(value: string): string | undefined {
  const trimmed = value.trim()
  return trimmed || undefined
}

function buildParams(): CommissionListParams {
  const settleableFrom = filters.settleable_date_range[0]
  const settleableTo = filters.settleable_date_range[1]
  const createdFrom = filters.created_at_range[0]
  const createdTo = filters.created_at_range[1]

  return {
    agent_id: normalizeOptional(filters.agent_id),
    case_no: normalizeOptional(filters.case_no),
    status: normalizeOptional(filters.status),
    settleable_date_from: settleableFrom || undefined,
    settleable_date_to: settleableTo || undefined,
    created_at_from: createdFrom || undefined,
    created_at_to: createdTo || undefined,
    page: page.value,
    page_size: pageSize.value,
  }
}

async function fetchRecords() {
  loading.value = true
  error.value = null
  try {
    const result = await getCommission(buildParams())
    records.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  fetchRecords()
}

function resetFilters() {
  filters.agent_id = ''
  filters.case_no = ''
  filters.status = ''
  filters.settleable_date_range = []
  filters.created_at_range = []
  onFilterChange()
}

function formatAmount(value: number): string {
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    OPEN: '进行中',
    SETTLED: '已结算',
    CANCELLED: '已取消',
    VOID: '已作废',
    CLOSED: '已关闭',
  }
  return map[status] || (status ? '未知状态' : '—')
}

function statusTagType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'SETTLED':
      return 'success'
    case 'OPEN':
      return 'warning'
    case 'CANCELLED':
    case 'VOID':
      return 'danger'
    default:
      return 'info'
  }
}

function settleableTagType(isSettleable: boolean): 'success' | 'info' {
  return isSettleable ? 'success' : 'info'
}

function settleableLabel(isSettleable: boolean): string {
  return isSettleable ? '可结算' : '不可结算'
}

function formatCaseDisplay(row: CommissionRecord): string {
  return row.case_no || '未命名案件'
}

function formatAgentDisplay(row: CommissionRecord): string {
  return row.agent_id ? '已分配' : '未分配'
}

function formatFeeTypeDisplay(type: string | null | undefined): string {
  if (!type) return '—'
  const map: Record<string, string> = {
    GOV: '官费',
    SERVICE: '服务费',
    MISC: '其他费用',
  }
  return map[type] || '未知费用类型'
}

watch([page, pageSize], () => {
  fetchRecords()
})

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.filter-bar {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.mono-num {
  font-family: var(--font-mono);
}

.stage-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.w-full {
  width: 100%;
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
