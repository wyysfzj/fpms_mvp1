<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">统一费用查询</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
    </div>

    <el-form class="filter-form" :inline="true">
      <el-form-item label="记录类型">
        <el-select
          v-model="filters.record_type"
          clearable
          class="filter-input"
          placeholder="全部"
        >
          <el-option label="付款记录" value="PAYMENT" />
          <el-option label="收款记录" value="RECEIPT" />
        </el-select>
      </el-form-item>
      <el-form-item label="案件编号">
        <el-input
          v-model.trim="filters.case_id"
          class="filter-input"
          clearable
          placeholder="请输入案件编号"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="业务编号">
        <el-input
          v-model.trim="filters.biz_no"
          class="filter-input"
          clearable
          placeholder="请输入业务编号"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="当事人">
        <el-input
          v-model.trim="filters.party_name"
          class="filter-input"
          clearable
          placeholder="请输入当事人"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="状态">
        <el-input
          v-model.trim="filters.status"
          class="filter-input"
          clearable
          placeholder="请输入状态"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="币种">
        <el-input
          v-model.trim="filters.currency"
          class="filter-input"
          clearable
          placeholder="例如 CNY"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="业务日期">
        <el-date-picker
          v-model="filters.date_range"
          class="filter-range"
          clearable
          end-placeholder="结束日期"
          range-separator="至"
          start-placeholder="开始日期"
          type="daterange"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="金额区间">
        <div class="amount-range">
          <el-input-number
            v-model="filters.amount_range[0]"
            class="filter-number"
            controls-position="right"
            :precision="2"
            :step="0.01"
            :min="0"
          />
          <span class="range-separator">至</span>
          <el-input-number
            v-model="filters.amount_range[1]"
            class="filter-number"
            controls-position="right"
            :precision="2"
            :step="0.01"
            :min="0"
          />
        </div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="applyFilters">查询</el-button>
        <el-button :disabled="loading" @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <div v-if="!hasUnifiedQueryPerm" class="page-empty">
      <EmptyState
        title="暂无访问权限"
        message="需要同时具备付款读取和收款读取权限后才能使用统一费用查询。"
        icon="🔐"
      />
    </div>

    <div v-else-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-else-if="loading" :rows="10" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无统一查询记录"
        message="请调整筛选条件后重试。"
        icon="🔎"
      />
    </div>

    <div v-else class="page-table">
      <el-table :data="items" stripe size="small" class="compact-table">
        <el-table-column label="记录类型" width="130">
          <template #default="{ row }">
            <el-tag :type="recordTypeTagType(row.record_type)" size="small">
              {{ row.record_type || '—' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="记录编号" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="mono-num">{{ row.record_id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="案件编号" width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.case_id || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="业务编号" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.biz_no || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="当事人" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.party_name || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="币种" width="90" align="center" />
        <el-table-column label="状态" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ row.status || '—' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="业务日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.biz_date) }}
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.remark || '—' }}
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
      />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { getFeeUnifiedQuery } from '../../../api/billing'
import type { FeeUnifiedQueryItem, FeeUnifiedQueryResponse } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { useAuthStore } from '../../../stores/auth'

const items = ref<FeeUnifiedQueryItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const authStore = useAuthStore()

const filters = reactive({
  record_type: '',
  case_id: '',
  biz_no: '',
  party_name: '',
  status: '',
  currency: '',
  date_range: [] as [string, string] | [],
  amount_range: [] as [number, number] | [],
})

const hasUnifiedQueryPerm = computed(() => (
  authStore.hasPermission('Payment.Read') && authStore.hasPermission('CaseReceipt.Read')
))
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function formatAmount(value: number, currency: string): string {
  const safeValue = Number.isFinite(value) ? value : 0
  return `${currency || 'CNY'} ${safeValue.toFixed(2)}`
}

function formatDate(value?: string | null): string {
  return value ? value.slice(0, 10) : '—'
}

function recordTypeTagType(recordType?: string | null): 'info' | 'success' | 'warning' | 'danger' {
  const normalized = (recordType || '').toUpperCase()
  if (normalized.includes('PAY')) return 'success'
  if (normalized.includes('RECEIPT') || normalized.includes('REC')) return 'warning'
  if (normalized.includes('OFFSET') || normalized.includes('REVERSE')) return 'danger'
  return 'info'
}

function statusTagType(status?: string | null): 'info' | 'success' | 'warning' | 'danger' {
  const normalized = (status || '').toUpperCase()
  if (normalized.includes('CLOSE') || normalized.includes('PAID') || normalized.includes('DONE')) return 'success'
  if (normalized.includes('VOID') || normalized.includes('CANCEL') || normalized.includes('REVERSE')) return 'danger'
  if (normalized.includes('OPEN') || normalized.includes('PENDING') || normalized.includes('PART')) return 'warning'
  return 'info'
}

function buildParams() {
  return {
    page: page.value,
    page_size: pageSize.value,
    record_type: filters.record_type || undefined,
    case_id: filters.case_id || undefined,
    biz_no: filters.biz_no || undefined,
    party_name: filters.party_name || undefined,
    status: filters.status || undefined,
    currency: filters.currency || undefined,
    date_range: filters.date_range,
    amount_range: filters.amount_range,
  }
}

async function fetchRecords() {
  if (!hasUnifiedQueryPerm.value) {
    items.value = []
    total.value = 0
    loading.value = false
    return
  }
  loading.value = true
  error.value = null
  try {
    const result: FeeUnifiedQueryResponse = await getFeeUnifiedQuery(buildParams())
    items.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  if (filters.amount_range.length === 2 && filters.amount_range[0] > filters.amount_range[1]) {
    error.value = {
      message: '金额区间无效，请调整后再查询。',
    } as ApiError
    return
  }
  if (page.value === 1) {
    fetchRecords()
    return
  }
  page.value = 1
}

function resetFilters() {
  filters.record_type = ''
  filters.case_id = ''
  filters.biz_no = ''
  filters.party_name = ''
  filters.status = ''
  filters.currency = ''
  filters.date_range = []
  filters.amount_range = []
  error.value = null
  if (page.value === 1) {
    fetchRecords()
    return
  }
  page.value = 1
}

watch([page, pageSize], () => {
  fetchRecords()
})

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.mono-num {
  font-family: var(--font-mono, monospace);
}

.filter-number {
  width: 170px;
}

.amount-range {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: var(--text-sub, #64748b);
  font-size: 12px;
}
</style>
