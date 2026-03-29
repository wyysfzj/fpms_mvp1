<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">{{ ZH.billList.title }}</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/billing/bills/new">
          <el-button type="primary">{{ ZH.billList.newBill }}</el-button>
        </router-link>
      </div>
    </div>

    <!-- Filter Bar -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-select v-model="filterStatus" placeholder="全部账单状态" clearable @change="onFilterChange">
          <el-option label="全部" value="" />
          <el-option label="已开具" value="ISSUED" />
          <el-option label="已付款" value="PAID" />
          <el-option label="已作废" value="VOID" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-select
          v-model="filterBadDebtStatus"
          placeholder="全部坏账状态"
          clearable
          @change="onFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="无坏账" value="NONE" />
          <el-option label="未结清" value="OPEN" />
          <el-option label="已结清" value="CLOSED" />
        </el-select>
      </el-col>
    </el-row>

    <div class="bad-debt-summary">
      <div class="bad-debt-summary-card">
        <span class="bad-debt-summary-label">坏账账单数</span>
        <span class="bad-debt-summary-value">{{ summary.bad_debt_bill_count }} 条</span>
      </div>
      <div class="bad-debt-summary-card">
        <span class="bad-debt-summary-label">坏账金额</span>
        <span class="bad-debt-summary-value mono-num">
          {{ formatAmount(summary.bad_debt_amount, summaryCurrency) }}
        </span>
      </div>
      <div class="bad-debt-summary-card">
        <span class="bad-debt-summary-label">累计回收金额</span>
        <span class="bad-debt-summary-value mono-num">
          {{ formatAmount(summary.total_recovered_amount, summaryCurrency) }}
        </span>
      </div>
      <div class="bad-debt-summary-card">
        <span class="bad-debt-summary-label">剩余坏账余额</span>
        <span class="bad-debt-summary-value mono-num">
          {{ formatAmount(summary.remaining_bad_debt_balance, summaryCurrency) }}
        </span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <LoadingBlock v-if="loading" :rows="10" />

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        :title="ZH.billList.emptyTitle"
        :message="ZH.billList.emptyMsg"
        icon="🧾"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="bills"
        stripe
        size="small"
        class="compact-table"
        @row-click="handleRowClick"
      >
        <el-table-column prop="bill_no" :label="ZH.billList.billNo" width="140">
          <template #default="{ row }">
            <span class="bill-no">{{ row.bill_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="client_name" :label="ZH.billList.client" min-width="180">
          <template #default="{ row }">
            {{ row.client_name || row.client_id || '—' }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.billList.status" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ getBillStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.billList.amount" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.billList.balance" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num" :class="{ 'balance-zero': row.balance === 0 }">
              {{ formatAmount(row.balance, row.currency) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.billList.issueDate" width="120">
          <template #default="{ row }">
            {{ row.issue_date ? formatDate(row.issue_date) : '—' }}
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getBills } from '../../../api/billing'
import type { BillListItem, BillStatus, BillListResponse } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { getBillStatusText } from '../../../constants/displayText'

const router = useRouter()

const bills = ref<BillListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref('')
const filterBadDebtStatus = ref('')
const summary = ref<Pick<
  BillListResponse,
  | 'bad_debt_bill_count'
  | 'bad_debt_amount'
  | 'total_recovered_amount'
  | 'remaining_bad_debt_balance'
>>({
  bad_debt_bill_count: 0,
  bad_debt_amount: 0,
  total_recovered_amount: 0,
  remaining_bad_debt_balance: 0,
})
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)
const summaryCurrency = computed(() => bills.value[0]?.currency || 'CNY')

function onFilterChange() {
  page.value = 1
}

async function fetchBills() {
  loading.value = true
  error.value = null
  try {
    const result = await getBills({
      page: page.value,
      page_size: pageSize.value,
      status: filterStatus.value || undefined,
      bad_debt_status: filterBadDebtStatus.value || undefined,
    })
    bills.value = result.items
    total.value = result.total
    summary.value = {
      bad_debt_bill_count: result.bad_debt_bill_count,
      bad_debt_amount: result.bad_debt_amount,
      total_recovered_amount: result.total_recovered_amount,
      remaining_bad_debt_balance: result.remaining_bad_debt_balance,
    }
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function statusTagType(status: BillStatus): 'info' | 'warning' | 'success' | 'danger' {
  switch (status) {
    case 'PAID': return 'success'
    case 'ISSUED': return 'warning'
    case 'VOID': return 'danger'
    default: return 'info'
  }
}

function formatAmount(amount: number, currency?: string): string {
  const curr = currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(amount)
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

function handleRowClick(row: BillListItem) {
  router.push(`/billing/bills/${row.id}`)
}

watch([page, pageSize, filterStatus, filterBadDebtStatus], () => {
  fetchBills()
}, { immediate: true })
</script>

<style scoped>
.bill-no {
  font-family: var(--font-mono);
  font-weight: 500;
}

.mono-num {
  font-family: var(--font-mono);
}

.balance-zero {
  color: var(--color-success);
}

.bad-debt-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.bad-debt-summary-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  background: var(--el-bg-color);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bad-debt-summary-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.bad-debt-summary-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

@media (max-width: 1200px) {
  .bad-debt-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .bad-debt-summary {
    grid-template-columns: 1fr;
  }
}
</style>
