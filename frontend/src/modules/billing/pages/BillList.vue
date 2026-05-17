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
        <router-link to="/reports/bills">
          <el-button>账单统计</el-button>
        </router-link>
      </div>
    </div>

    <el-form class="filter-form" :inline="true">
      <el-form-item label="客户编号">
        <el-input
          v-model="filters.client_id"
          class="filter-input"
          clearable
          placeholder="请输入客户编号"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="账单状态">
        <el-select
          v-model="filters.bill_status"
          class="filter-select"
          clearable
          placeholder="全部账单状态"
        >
          <el-option label="全部" value="" />
          <el-option label="草稿" value="DRAFT" />
          <el-option label="已开具" value="ISSUED" />
          <el-option label="已付款" value="PAID" />
          <el-option label="已作废" value="VOID" />
        </el-select>
      </el-form-item>
      <el-form-item label="币种">
        <el-input
          v-model="filters.currency"
          class="filter-input"
          clearable
          placeholder="例如 CNY"
          @keyup.enter="applyFilters"
        />
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
        <el-select
          v-model="filters.aging_bucket"
          class="filter-select"
          clearable
          placeholder="全部账龄"
        >
          <el-option label="全部" value="" />
          <el-option label="未到期" value="CURRENT" />
          <el-option label="0-30 天" value="0-30" />
          <el-option label="31-60 天" value="31-60" />
          <el-option label="61-90 天" value="61-90" />
          <el-option label="90 天以上" value="90+" />
        </el-select>
      </el-form-item>
      <el-form-item label="逾期">
        <el-select
          v-model="filters.is_overdue"
          class="filter-select"
          placeholder="全部"
        >
          <el-option label="全部" :value="''" />
          <el-option label="仅逾期" :value="'true'" />
          <el-option label="仅未逾期" :value="'false'" />
        </el-select>
      </el-form-item>
      <el-form-item label="坏账">
        <el-select
          v-model="filters.is_bad_debt"
          class="filter-select"
          placeholder="全部"
        >
          <el-option label="全部" :value="''" />
          <el-option label="仅坏账" :value="'true'" />
          <el-option label="仅非坏账" :value="'false'" />
        </el-select>
      </el-form-item>
      <el-form-item label="坏账状态">
        <el-select
          v-model="filters.bad_debt_status"
          class="filter-select"
          clearable
          placeholder="全部坏账状态"
        >
          <el-option label="全部" value="" />
          <el-option label="无坏账" value="NONE" />
          <el-option label="未结清" value="OPEN" />
          <el-option label="已结清" value="CLOSED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="applyFilters">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

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
            <span class="bill-no">{{ getBillDisplayNo(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="client_name" :label="ZH.billList.client" min-width="180">
          <template #default="{ row }">
            {{ row.client_name || '未命名客户' }}
          </template>
        </el-table-column>
        <el-table-column label="方向" width="90">
          <template #default="{ row }">
            <el-tag :type="billDirectionTagType(row.direction)" size="small">
              {{ billDirectionText(row.direction) }}
            </el-tag>
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
        <el-table-column label="到期日期" width="120">
          <template #default="{ row }">
            {{ row.due_date ? formatDate(row.due_date) : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="账龄" width="120">
          <template #default="{ row }">
            <el-tag :type="agingBucketTagType(row.aging_bucket)" size="small">
              {{ agingBucketLabel(row.aging_bucket) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="逾期" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_overdue ? 'danger' : 'info'" size="small">
              {{ row.is_overdue ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="坏账" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_bad_debt ? 'warning' : 'info'" size="small">
              {{ row.is_bad_debt ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.billList.issueDate" width="120">
          <template #default="{ row }">
            {{ row.issue_date ? formatDate(row.issue_date) : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" :loading="printingBillId === row.id" @click.stop="handlePrint(row)">
              打印
            </el-button>
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
import { ElMessage } from 'element-plus'
import { getBills, printBill } from '../../../api/billing'
import type { BillListItem, BillStatus } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { getBillDirectionText, getBillStatusText } from '../../../constants/displayText'

const router = useRouter()

const bills = ref<BillListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const printingBillId = ref<string | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
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
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function applyFilters() {
  page.value = 1
  fetchBills()
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
  page.value = 1
  fetchBills()
}

async function fetchBills() {
  loading.value = true
  error.value = null
  try {
    const result = await getBills({
      page: page.value,
      page_size: pageSize.value,
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
    bills.value = result.items
    total.value = result.total
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

function billDirectionText(direction?: string): string {
  return getBillDirectionText(direction)
}

function billDirectionTagType(direction?: string): 'success' | 'warning' | 'info' {
  switch ((direction || '').toUpperCase()) {
    case 'AR':
      return 'success'
    case 'AP':
      return 'warning'
    default:
      return 'info'
  }
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

function agingBucketTagType(bucket?: string): 'success' | 'warning' | 'danger' | 'info' {
  switch (bucket) {
    case 'CURRENT': return 'success'
    case '0-30': return 'info'
    case '31-60': return 'warning'
    case '61-90':
    case '90+':
      return 'danger'
    default:
      return 'info'
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

function isUuidLike(input?: string | null): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(String(input || '').trim())
}

function getBillDisplayNo(row: BillListItem): string {
  if (row.bill_no && !isUuidLike(row.bill_no)) {
    return row.bill_no
  }
  return row.id ? '已关联账单' : '未生成账单号'
}

function handleRowClick(row: BillListItem) {
  router.push(`/billing/bills/${row.id}`)
}

async function handlePrint(row: BillListItem) {
  printingBillId.value = row.id
  error.value = null

  try {
    const blob = await printBill(row.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const billNo = getBillDisplayNo(row)

    link.href = url
    link.download = `bill-${billNo}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('账单下载成功')
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    if (apiError.status === 409) {
      ElMessage.error('账单模板未配置，请在系统设置中配置模板。')
    } else {
      ElMessage.error('打印失败，请稍后重试。')
    }
  } finally {
    printingBillId.value = null
  }
}

watch([page, pageSize], () => {
  fetchBills()
}, { immediate: true })
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

</style>
