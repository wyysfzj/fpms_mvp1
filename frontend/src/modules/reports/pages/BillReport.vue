<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">账单统计</h1>
        <span class="page-count">应收、逾期、账龄与坏账</span>
      </div>
      <div class="page-header-right">
        <router-link to="/billing/bills">
          <el-button>返回账单列表</el-button>
        </router-link>
      </div>
    </div>

    <el-form class="filter-form" :inline="true">
      <el-form-item label="客户编号">
        <el-input v-model.trim="filters.client_id" class="filter-input" clearable placeholder="请输入客户编号" @keyup.enter="fetchReport" />
      </el-form-item>
      <el-form-item label="账单状态">
        <el-select v-model="filters.bill_status" class="filter-select" clearable placeholder="全部账单状态">
          <el-option label="全部" value="" />
          <el-option label="草稿" value="DRAFT" />
          <el-option label="已开具" value="ISSUED" />
          <el-option label="已付款" value="PAID" />
          <el-option label="已作废" value="VOID" />
        </el-select>
      </el-form-item>
      <el-form-item label="币种">
        <el-input v-model.trim="filters.currency" class="filter-input" clearable placeholder="例如 CNY" @keyup.enter="fetchReport" />
      </el-form-item>
      <el-form-item label="账单日期">
        <el-date-picker
          v-model="filters.bill_date_range"
          class="filter-range"
          clearable
          end-placeholder="结束日期"
          range-separator="至"
          start-placeholder="开始日期"
          type="daterange"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="账龄区间">
        <el-select v-model="filters.aging_bucket" class="filter-select" clearable placeholder="全部账龄">
          <el-option label="全部" value="" />
          <el-option label="未到期" value="CURRENT" />
          <el-option label="0-30 天" value="0-30" />
          <el-option label="31-60 天" value="31-60" />
          <el-option label="61-90 天" value="61-90" />
          <el-option label="90 天以上" value="90+" />
        </el-select>
      </el-form-item>
      <el-form-item label="逾期">
        <el-select v-model="filters.is_overdue" class="filter-select" placeholder="全部">
          <el-option label="全部" :value="''" />
          <el-option label="仅逾期" :value="'true'" />
          <el-option label="仅未逾期" :value="'false'" />
        </el-select>
      </el-form-item>
      <el-form-item label="坏账">
        <el-select v-model="filters.is_bad_debt" class="filter-select" placeholder="全部">
          <el-option label="全部" :value="''" />
          <el-option label="仅坏账" :value="'true'" />
          <el-option label="仅非坏账" :value="'false'" />
        </el-select>
      </el-form-item>
      <el-form-item label="坏账状态">
        <el-select v-model="filters.bad_debt_status" class="filter-select" clearable placeholder="全部坏账状态">
          <el-option label="全部" value="" />
          <el-option label="无坏账" value="NONE" />
          <el-option label="未结清" value="OPEN" />
          <el-option label="已结清" value="CLOSED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchReport">查询统计</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="6" />

    <template v-else>
      <div class="report-summary">
        <div class="summary-card">
          <span class="summary-label">应收账单数</span>
          <span class="summary-value">{{ summary.receivable_bill_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">应收余额</span>
          <span class="summary-value mono-num">{{ formatAmount(summary.receivable_amount, summaryCurrency) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">逾期账单数</span>
          <span class="summary-value">{{ summary.overdue_bill_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">逾期余额</span>
          <span class="summary-value mono-num">{{ formatAmount(summary.overdue_amount, summaryCurrency) }}</span>
        </div>
      </div>

      <div class="report-grid">
        <section class="report-card">
          <div class="report-card-title">账龄区间</div>
          <div v-if="summary.aging_buckets.length" class="line-list">
            <div v-for="bucket in summary.aging_buckets" :key="bucket.bucket" class="line-item">
              <span>{{ agingBucketLabel(bucket.bucket) }}</span>
              <span>{{ bucket.bill_count }} 条 · {{ formatAmount(bucket.amount, summaryCurrency) }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无账龄统计" :image-size="72" />
        </section>

        <section class="report-card">
          <div class="report-card-title">坏账与回收</div>
          <div class="line-list">
            <div class="line-item">
              <span>坏账账单数</span>
              <span>{{ summary.bad_debt_bill_count }} 条</span>
            </div>
            <div class="line-item">
              <span>坏账金额</span>
              <span>{{ formatAmount(summary.bad_debt_amount, summaryCurrency) }}</span>
            </div>
            <div class="line-item">
              <span>累计回收金额</span>
              <span>{{ formatAmount(summary.total_recovered_amount, summaryCurrency) }}</span>
            </div>
            <div class="line-item">
              <span>剩余坏账余额</span>
              <span>{{ formatAmount(summary.remaining_bad_debt_balance, summaryCurrency) }}</span>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getBills } from '../../../api/billing'
import type { BillListReportSummary } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

const emptySummary = (): BillListReportSummary => ({
  receivable_bill_count: 0,
  receivable_amount: 0,
  overdue_bill_count: 0,
  overdue_amount: 0,
  bad_debt_bill_count: 0,
  bad_debt_amount: 0,
  total_recovered_amount: 0,
  remaining_bad_debt_balance: 0,
  aging_buckets: [],
})

const filters = ref({
  client_id: '',
  bill_status: '',
  currency: '',
  bill_date_range: [] as string[],
  aging_bucket: '',
  is_overdue: '' as '' | 'true' | 'false',
  is_bad_debt: '' as '' | 'true' | 'false',
  bad_debt_status: '',
})
const summary = ref<BillListReportSummary>(emptySummary())
const loading = ref(false)
const error = ref<ApiError | null>(null)
const summaryCurrency = computed(() => filters.value.currency || 'CNY')

async function fetchReport() {
  loading.value = true
  error.value = null
  try {
    const result = await getBills({
      page: 1,
      page_size: 1,
      bill_status: filters.value.bill_status || undefined,
      client_id: filters.value.client_id || undefined,
      currency: filters.value.currency || undefined,
      bill_date_from: filters.value.bill_date_range[0] || undefined,
      bill_date_to: filters.value.bill_date_range[1] || undefined,
      aging_bucket: filters.value.aging_bucket || undefined,
      is_overdue:
        filters.value.is_overdue === '' ? undefined : filters.value.is_overdue === 'true',
      is_bad_debt:
        filters.value.is_bad_debt === '' ? undefined : filters.value.is_bad_debt === 'true',
      bad_debt_status: filters.value.bad_debt_status || undefined,
    })
    summary.value = result.summary
  } catch (err) {
    error.value = err as ApiError
    summary.value = emptySummary()
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.value = {
    client_id: '',
    bill_status: '',
    currency: '',
    bill_date_range: [],
    aging_bucket: '',
    is_overdue: '',
    is_bad_debt: '',
    bad_debt_status: '',
  }
  fetchReport()
}

function agingBucketLabel(bucket?: string): string {
  switch (bucket) {
    case 'CURRENT': return '未到期'
    case '0-30': return '0-30 天'
    case '31-60': return '31-60 天'
    case '61-90': return '61-90 天'
    case '90+': return '90 天以上'
    default: return '未分类'
  }
}

function formatAmount(amount: number, currency?: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(amount)
}

onMounted(() => {
  fetchReport()
})
</script>

<style scoped>
.filter-form {
  margin-bottom: 16px;
}

.filter-input,
.filter-select {
  width: 180px;
}

.filter-range {
  width: 260px;
}

.mono-num {
  font-family: var(--font-mono);
}

.report-summary,
.report-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.report-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.summary-card,
.report-card {
  padding: 14px 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-bg-color);
}

.summary-label,
.report-card-title {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.summary-value {
  display: block;
  margin-top: 6px;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

.line-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.line-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-size: 13px;
}

@media (max-width: 960px) {
  .report-summary,
  .report-grid {
    grid-template-columns: 1fr;
  }
}
</style>
