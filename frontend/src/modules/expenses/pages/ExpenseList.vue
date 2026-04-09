<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">支出列表</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" aria-label="录入支出" @click="goToCreate">
          录入支出
        </el-button>
      </div>
    </div>

    <el-row :gutter="12" class="filter-row">
      <el-col :xs="24" :sm="12" :md="7" :lg="6">
        <el-input
          v-model.trim="filterCaseId"
          aria-label="案件或项目筛选"
          placeholder="案件/项目编号"
          clearable
          @keyup.enter="handleSearch"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="5">
        <el-input
          v-model.trim="filterDepartmentId"
          aria-label="部门筛选"
          placeholder="部门编号"
          clearable
          @keyup.enter="handleSearch"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="5">
        <el-input
          v-model.trim="filterWorkerId"
          aria-label="经手人筛选"
          placeholder="经手人编号"
          clearable
          @keyup.enter="handleSearch"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="5" :lg="4">
        <el-select
          v-model="filterCategory"
          aria-label="支出类别筛选"
          class="full-width"
          placeholder="支出类别"
          clearable
        >
          <el-option
            v-for="option in categoryOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-col>
      <el-col :xs="24" :sm="24" :md="7" :lg="5">
        <el-date-picker
          v-model="filterDateRange"
          aria-label="支出日期范围筛选"
          type="daterange"
          class="full-width"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          clearable
        />
      </el-col>
      <el-col :xs="24" :sm="24" :md="24" :lg="4" class="filter-actions">
        <el-button type="primary" aria-label="查询支出记录" @click="handleSearch">查询</el-button>
        <el-button aria-label="重置支出筛选" @click="handleReset">重置</el-button>
      </el-col>
    </el-row>

    <div v-if="stats" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">总笔数</div>
        <div class="stat-value">{{ stats.count_total }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总金额</div>
        <div class="stat-value mono-num">{{ formatAmount(stats.sum_total, 'CNY') }}</div>
      </div>
      <div
        v-for="stat in categoryStats"
        :key="stat.category"
        class="stat-card"
      >
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-value">{{ stat.count }} 笔</div>
      </div>
    </div>

    <div v-if="stats && (caseStats.length || clientStats.length || departmentStats.length)" class="grouped-summary-grid">
      <section class="grouped-summary-card">
        <div class="grouped-summary-header">
          <h3>每案总支出</h3>
          <span>{{ caseStats.length }} 组</span>
        </div>
        <div v-if="caseStats.length" class="grouped-summary-list">
          <div
            v-for="item in caseStats"
            :key="item.key"
            class="grouped-summary-item"
          >
            <div class="grouped-summary-main">
              <span class="grouped-summary-title">{{ item.label }}</span>
              <span class="grouped-summary-sub">支出 {{ item.expense_count }} 笔</span>
            </div>
            <div class="grouped-summary-amounts mono-num">
              {{ formatAmount(item.total_amount, 'CNY') }}
            </div>
          </div>
        </div>
      </section>

      <section class="grouped-summary-card">
        <div class="grouped-summary-header">
          <h3>每客户支出</h3>
          <span>{{ clientStats.length }} 组</span>
        </div>
        <div v-if="clientStats.length" class="grouped-summary-list">
          <div
            v-for="item in clientStats"
            :key="item.key"
            class="grouped-summary-item"
          >
            <div class="grouped-summary-main">
              <span class="grouped-summary-title">{{ item.label }}</span>
              <span class="grouped-summary-sub">支出 {{ item.expense_count }} 笔</span>
            </div>
            <div class="grouped-summary-amounts mono-num">
              {{ formatAmount(item.total_amount, 'CNY') }}
            </div>
          </div>
        </div>
      </section>

      <section class="grouped-summary-card">
        <div class="grouped-summary-header">
          <h3>每部门支出</h3>
          <span>{{ departmentStats.length }} 组</span>
        </div>
        <div v-if="departmentStats.length" class="grouped-summary-list">
          <div
            v-for="item in departmentStats"
            :key="item.key"
            class="grouped-summary-item"
          >
            <div class="grouped-summary-main">
              <span class="grouped-summary-title">{{ item.label }}</span>
              <span class="grouped-summary-sub">支出 {{ item.expense_count }} 笔</span>
            </div>
            <div class="grouped-summary-amounts mono-num">
              {{ formatAmount(item.total_amount, 'CNY') }}
            </div>
          </div>
        </div>
      </section>
    </div>

    <section v-if="grossProfitStats.length" class="grouped-summary-card gross-profit-card">
      <div class="grouped-summary-header">
        <h3>案件毛利分析</h3>
        <span>{{ grossProfitStats.length }} 组</span>
      </div>
      <div class="grouped-summary-list">
        <div
          v-for="item in grossProfitStats"
          :key="`${item.key}-${item.currency}`"
          class="grouped-summary-item grouped-summary-item-column"
        >
          <div class="grouped-summary-main">
            <span class="grouped-summary-title">{{ item.label }}</span>
            <span class="grouped-summary-sub">币种 {{ item.currency }}</span>
          </div>
          <div class="gross-profit-breakdown mono-num">
            <span>收款 {{ formatAmount(item.received_total, item.currency) }}</span>
            <span>支出 {{ formatAmount(item.expense_total, item.currency) }}</span>
            <strong>毛利 {{ formatAmount(item.gross_profit_total, item.currency) }}</strong>
          </div>
        </div>
      </div>
    </section>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无支出记录"
        message="请调整筛选条件，或先录入一条支出。"
        icon="🧾"
        cta-label="录入支出"
        @cta="goToCreate"
      />
    </div>

    <div v-else class="page-table">
      <el-table :data="expenses" aria-label="支出记录列表" stripe size="small" class="compact-table">
        <el-table-column prop="expense_no" label="支出编号" min-width="180">
          <template #default="{ row }">
            <span class="mono-num">{{ row.expense_no || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="case_id" label="案件/项目" min-width="200">
          <template #default="{ row }">
            <span class="mono-num">{{ row.case_id || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="worker_id" label="经手人" min-width="180">
          <template #default="{ row }">
            <span class="mono-num">{{ row.worker_id || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="department_id" label="部门" min-width="180">
          <template #default="{ row }">
            <span class="mono-num">{{ row.department_id || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="类别" width="140">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ getCategoryText(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expense_date" label="支出日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.expense_date) }}
          </template>
        </el-table-column>
        <el-table-column label="金额" width="160" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="getStatusTagType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="180">
          <template #default="{ row }">
            {{ row.remark || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
      />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getExpenses, mapExpenseError } from '../../../api/expenses'
import type {
  ExpenseApiError,
  ExpenseCategory,
  ExpenseGrossProfitStat,
  ExpenseGroupedStat,
  ExpenseItem,
  ExpenseStats,
} from '../../../api/expenses.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

interface CategoryOption {
  label: string
  value: ExpenseCategory
}

interface CategoryStatView {
  category: string
  label: string
  count: number
}

interface GroupedStatView {
  key: string
  label: string
  expense_count: number
  total_amount: number
}

interface GrossProfitStatView {
  key: string
  label: string
  currency: string
  expense_total: number
  received_total: number
  gross_profit_total: number
}

const CATEGORY_TEXT: Record<string, string> = {
  SEARCH_DB: '检索费',
  TRANSLATION: '翻译费',
  TRANSPORT: '交通费',
  OTHER: '其他',
}

const STATUS_TEXT: Record<string, string> = {
  DRAFT: '草稿',
}

const categoryOptions: CategoryOption[] = [
  { label: '检索费', value: 'SEARCH_DB' },
  { label: '翻译费', value: 'TRANSLATION' },
  { label: '交通费', value: 'TRANSPORT' },
  { label: '其他', value: 'OTHER' },
]

const router = useRouter()
const route = useRoute()

const expenses = ref<ExpenseItem[]>([])
const loading = ref(false)
const error = ref<ExpenseApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const stats = ref<ExpenseStats | null>(null)

const filterCaseId = ref(typeof route.query.case_id === 'string' ? route.query.case_id : '')
const filterDepartmentId = ref(
  typeof route.query.department_id === 'string' ? route.query.department_id : '',
)
const filterWorkerId = ref(typeof route.query.worker_id === 'string' ? route.query.worker_id : '')
const filterCategory = ref<ExpenseCategory | ''>('')
const filterDateRange = ref<string[]>([])

const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

const categoryStats = computed<CategoryStatView[]>(() => {
  if (!stats.value) return []

  return Object.entries(stats.value.count_by_category)
    .map(([category, count]) => ({
      category,
      label: getCategoryText(category),
      count,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
})

function mapGroupedStats(rows: ExpenseGroupedStat[] | undefined): GroupedStatView[] {
  return (rows || []).map((row) => ({
    key: row.key,
    label: row.label,
    expense_count: row.expense_count,
    total_amount: row.total_amount,
  }))
}

const caseStats = computed<GroupedStatView[]>(() => mapGroupedStats(stats.value?.case_amounts))
const clientStats = computed<GroupedStatView[]>(() => mapGroupedStats(stats.value?.client_amounts))
const departmentStats = computed<GroupedStatView[]>(() =>
  mapGroupedStats(stats.value?.department_amounts),
)
const grossProfitStats = computed<GrossProfitStatView[]>(() =>
  (stats.value?.gross_profit_amounts || []).map((row: ExpenseGrossProfitStat) => ({
    key: row.key,
    label: row.label,
    currency: row.currency,
    expense_total: row.expense_total,
    received_total: row.received_total,
    gross_profit_total: row.gross_profit_total,
  })),
)

function getCategoryText(category: string): string {
  return CATEGORY_TEXT[category] || category
}

function getStatusText(status: string): string {
  return STATUS_TEXT[status] || status
}

function getStatusTagType(status: string): 'info' | 'success' {
  if (status === 'DRAFT') return 'info'
  return 'success'
}

function formatDate(value?: string | null): string {
  if (!value) return '—'
  return value.slice(0, 10)
}

function formatAmount(amount: number, currency: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(amount)
}

function handleSearch() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  void fetchExpenses()
}

function handleReset() {
  filterCaseId.value = ''
  filterDepartmentId.value = ''
  filterWorkerId.value = ''
  filterCategory.value = ''
  filterDateRange.value = []
  handleSearch()
}

function goToCreate() {
  const query: Record<string, string> = {}
  if (filterCaseId.value) {
    query.case_id = filterCaseId.value
  }
  query.return_to = '/expenses'

  void router.push({ path: '/expenses/new', query })
}

async function fetchExpenses() {
  loading.value = true
  error.value = null

  try {
    const [dateFrom, dateTo] = filterDateRange.value
    const result = await getExpenses({
      case_id: filterCaseId.value || undefined,
      department_id: filterDepartmentId.value || undefined,
      worker_id: filterWorkerId.value || undefined,
      category: filterCategory.value || undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
      include_stats: true,
      page: page.value,
      page_size: pageSize.value,
    })

    expenses.value = result.items
    total.value = result.total
    stats.value = result.stats || null
  } catch (err) {
    error.value = mapExpenseError(err, 'list')
  } finally {
    loading.value = false
  }
}

watch([page, pageSize], () => {
  void fetchExpenses()
})

onMounted(() => {
  void fetchExpenses()
})
</script>

<style scoped>
.filter-row {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.full-width {
  width: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-1);
  padding: 12px;
}

.stat-label {
  color: var(--text-sub);
  font-size: 12px;
}

.stat-value {
  margin-top: 6px;
  font-size: 18px;
  font-weight: 600;
}

.grouped-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.grouped-summary-card {
  border: 1px solid var(--border-default);
  border-radius: 12px;
  background: var(--surface-1);
  padding: 16px;
}

.grouped-summary-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}

.grouped-summary-header h3 {
  margin: 0;
  font-size: 15px;
}

.grouped-summary-header span {
  color: var(--text-sub);
  font-size: 12px;
}

.grouped-summary-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.grouped-summary-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--surface-0);
}

.grouped-summary-item-column {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.grouped-summary-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.grouped-summary-title {
  font-weight: 600;
}

.grouped-summary-sub {
  color: var(--text-sub);
  font-size: 12px;
}

.grouped-summary-amounts {
  align-self: center;
  font-weight: 600;
}

.gross-profit-card {
  margin-bottom: 16px;
}

.gross-profit-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.mono-num {
  font-family: var(--font-mono);
}

@media (max-width: 768px) {
  .filter-actions {
    margin-top: 4px;
  }
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
