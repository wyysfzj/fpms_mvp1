<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">顾问项目收益视图</h1>
      </div>
    </div>

    <el-row :gutter="12" class="filter-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-input
          v-model.trim="caseId"
          aria-label="项目编号筛选"
          placeholder="项目编号（必填）"
          clearable
          @keyup.enter="handleSearch"
        />
      </el-col>
      <el-col :xs="24" :sm="24" :md="10" :lg="8">
        <el-date-picker
          v-model="expenseDateRange"
          aria-label="支出日期范围筛选"
          type="daterange"
          class="full-width"
          range-separator="至"
          start-placeholder="支出开始日期"
          end-placeholder="支出结束日期"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          clearable
        />
      </el-col>
      <el-col :xs="24" :sm="24" :md="6" :lg="10" class="filter-actions">
        <el-button type="primary" aria-label="查询项目收益" :loading="loading" @click="handleSearch">查询收益</el-button>
        <el-button aria-label="重置收益筛选" :disabled="loading" @click="handleReset">重置</el-button>
      </el-col>
    </el-row>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-alert
      v-if="incomeMissingHint"
      type="warning"
      :closable="false"
      show-icon
      title="该项目暂无收入汇总记录，收入按 0 显示。"
      class="hint-alert"
    />

    <LoadingBlock v-if="loading" :rows="8" />

    <div v-else-if="!queried" class="page-empty">
      <EmptyState
        title="请输入项目后查询"
        message="按项目查看收入、支出与毛利。"
        icon="📈"
      />
    </div>

    <div v-else class="result-container">
      <div class="source-note">数据来源：案件收款汇总（收入）+ 支出台账（支出）</div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">应收收入</div>
          <div class="stat-value mono-num">{{ formatMoney(income.total_billed, currency) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">已收收入</div>
          <div class="stat-value mono-num">{{ formatMoney(income.total_paid, currency) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">支出总额</div>
          <div class="stat-value mono-num">{{ formatMoney(expenseTotal, currency) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">毛利</div>
          <div class="stat-value mono-num" :class="{ 'negative-value': grossProfit < 0 }">
            {{ formatMoney(grossProfit, currency) }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">毛利率（按已收）</div>
          <div class="stat-value">{{ grossMarginText }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">未收收入</div>
          <div class="stat-value mono-num">{{ formatMoney(income.total_outstanding, currency) }}</div>
        </div>
      </div>

      <el-card shadow="never" class="section-card">
        <template #header>
          <div class="section-title">项目收益汇总</div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="项目">{{ formatProjectDisplay(income.case_id, caseId) }}</el-descriptions-item>
          <el-descriptions-item label="统计币种">{{ currency }}</el-descriptions-item>
          <el-descriptions-item label="可计提提成">{{ income.is_commissionable === true ? '是' : income.is_commissionable === false ? '否' : '—' }}</el-descriptions-item>
          <el-descriptions-item label="费用类型">{{ income.fee_type || '—' }}</el-descriptions-item>
          <el-descriptions-item label="费用代码">{{ income.fee_code || '—' }}</el-descriptions-item>
          <el-descriptions-item label="年度">{{ income.year_no ?? '—' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card shadow="never" class="section-card">
        <template #header>
          <div class="section-title">支出分类统计</div>
        </template>

        <el-table :data="expenseCategoryRows" stripe size="small" class="compact-table">
          <el-table-column prop="label" label="支出类别" min-width="180" />
          <el-table-column prop="count" label="笔数" width="100" />
          <el-table-column label="金额" width="160" align="right">
            <template #default="{ row }">
              <span class="mono-num">{{ formatMoney(row.amount, currency) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card shadow="never" class="section-card">
        <template #header>
          <div class="section-title">支出明细</div>
        </template>

        <el-table :data="expenseItems" stripe size="small" class="compact-table">
          <el-table-column prop="expense_no" label="支出编号" min-width="160">
            <template #default="{ row }">
              <span class="mono-num">{{ row.expense_no || '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="expense_date" label="支出日期" width="120">
            <template #default="{ row }">
              {{ formatDate(row.expense_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="category" label="类别" width="140">
            <template #default="{ row }">
              <el-tag size="small" type="info">{{ categoryLabel(row.category) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="140" align="right">
            <template #default="{ row }">
              <span class="mono-num">{{ formatMoney(row.amount, row.currency || currency) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              {{ statusLabel(row.status) }}
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" min-width="180">
            <template #default="{ row }">
              {{ row.remark || '—' }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getCaseReceipts } from '../../../api/billing'
import { getExpenses } from '../../../api/expenses'
import type { CaseReceiptsSummary } from '../../../api/billing.types'
import type { ExpenseItem, ExpenseStats } from '../../../api/expenses.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import { ElMessage } from 'element-plus'

interface CategoryStatRow {
  key: string
  label: string
  count: number
  amount: number
}

const CATEGORY_LABELS: Record<string, string> = {
  SEARCH_DB: '检索数据库费用',
  TRANSLATION: '翻译费用',
  TRANSPORT: '交通费用',
  OTHER: '其他费用',
}

const STATUS_LABELS: Record<string, string> = {
  DRAFT: '草稿',
}

const route = useRoute()

const loading = ref(false)
const queried = ref(false)
const error = ref<ApiError | null>(null)
const incomeMissingHint = ref(false)

const caseId = ref(typeof route.query.case_id === 'string' ? route.query.case_id : '')
const expenseDateRange = ref<string[]>([])

function createEmptyIncome(targetCaseId = ''): CaseReceiptsSummary {
  return {
    case_id: targetCaseId,
    total_billed: 0,
    total_paid: 0,
    total_outstanding: 0,
    currency: 'CNY',
    bills: [],
  }
}

const expenseItems = ref<ExpenseItem[]>([])

function createEmptyExpenseStats(): ExpenseStats {
  return {
    count_by_category: {},
    sum_by_category: {},
    count_total: 0,
    sum_total: 0,
  }
}

function deriveExpenseStatsFromItems(items: ExpenseItem[]): ExpenseStats {
  const count_by_category: Record<string, number> = {}
  const sum_by_category: Record<string, number> = {}
  let sum_total = 0

  for (const item of items) {
    const category = item.category || 'OTHER'
    const amount = Number(item.amount) || 0
    count_by_category[category] = (count_by_category[category] || 0) + 1
    sum_by_category[category] = (sum_by_category[category] || 0) + amount
    sum_total += amount
  }

  return {
    count_by_category,
    sum_by_category,
    count_total: items.length,
    sum_total,
  }
}

const income = ref<CaseReceiptsSummary>(createEmptyIncome())
const expenseStats = ref<ExpenseStats>(createEmptyExpenseStats())

const currency = computed(() => income.value.currency || 'CNY')
const expenseTotal = computed(() => expenseStats.value.sum_total || 0)
const grossProfit = computed(() => income.value.total_paid - expenseTotal.value)

const grossMarginText = computed(() => {
  if (income.value.total_paid <= 0) return '—'
  const ratio = (grossProfit.value / income.value.total_paid) * 100
  return `${ratio.toFixed(2)}%`
})

const expenseCategoryRows = computed<CategoryStatRow[]>(() => {
  const keys = new Set([
    ...Object.keys(expenseStats.value.count_by_category || {}),
    ...Object.keys(expenseStats.value.sum_by_category || {}),
  ])

  return Array.from(keys)
    .map((key) => ({
      key,
      label: categoryLabel(key),
      count: expenseStats.value.count_by_category[key] || 0,
      amount: expenseStats.value.sum_by_category[key] || 0,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
})

function toApiError(errorLike: unknown): ApiError | null {
  if (!errorLike || typeof errorLike !== 'object') return null
  const candidate = errorLike as Partial<ApiError>
  if (typeof candidate.status !== 'number') return null
  if (typeof candidate.code !== 'string') return null
  if (typeof candidate.message !== 'string') return null
  return candidate as ApiError
}

function mapIncomeError(errorLike: unknown): string {
  const apiError = toApiError(errorLike)
  if (!apiError || apiError.status === 0) return '网络异常或服务不可用，收入数据加载失败。'

  if (apiError.status === 404 && apiError.code === 'CASE_RECEIPT_NOT_FOUND') {
    return '该项目暂无收入汇总记录。'
  }
  if (apiError.status === 400) return '项目参数不合法，请检查后重试。'
  if (apiError.status === 401) return '登录已失效，请重新登录后重试。'
  if (apiError.status === 403) return '无权限查看项目收入数据。'
  if (apiError.status === 422) return '收入查询参数校验失败，请检查后重试。'

  return '收入数据加载失败，请稍后重试。'
}

function mapExpenseError(errorLike: unknown): string {
  const apiError = toApiError(errorLike)
  if (!apiError || apiError.status === 0) return '网络异常或服务不可用，支出数据加载失败。'

  if (apiError.status === 400 && apiError.code === 'EXPENSE_INVALID') {
    return '支出筛选条件不合法，请调整后重试。'
  }
  if (apiError.status === 401) return '登录已失效，请重新登录后重试。'
  if (apiError.status === 403) return '无权限查看项目支出数据。'
  if (apiError.status === 422) return '支出查询参数校验失败，请检查后重试。'

  return '支出数据加载失败，请稍后重试。'
}

function categoryLabel(key: string): string {
  return CATEGORY_LABELS[key] || '未知支出类别'
}

function statusLabel(status?: string | null): string {
  if (!status) return '—'
  return STATUS_LABELS[status] || '未知状态'
}

function isUuidLike(value: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value)
}

function formatProjectDisplay(...values: Array<string | null | undefined>): string {
  const readable = values
    .map((value) => String(value || '').trim())
    .find((value) => value && !isUuidLike(value))
  return readable || '当前项目'
}

function formatDate(value?: string | null): string {
  if (!value) return '—'
  return value.slice(0, 10)
}

function formatMoney(value: number, curr: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr || 'CNY',
  }).format(value)
}

function handleReset() {
  caseId.value = ''
  expenseDateRange.value = []
  queried.value = false
  incomeMissingHint.value = false
  error.value = null
  income.value = createEmptyIncome()
  expenseItems.value = []
  expenseStats.value = createEmptyExpenseStats()
}

function handleSearch() {
  if (loading.value) return
  void queryProfitability()
}

async function queryProfitability() {
  if (loading.value) return

  const normalizedCaseId = caseId.value.trim()
  if (!normalizedCaseId) {
    ElMessage.error('请输入项目编号后再查询。')
    return
  }

  loading.value = true
  queried.value = true
  error.value = null
  incomeMissingHint.value = false
  income.value = createEmptyIncome(normalizedCaseId)
  expenseItems.value = []
  expenseStats.value = createEmptyExpenseStats()

  const [incomeResult, expenseResult] = await Promise.allSettled([
    getCaseReceipts(normalizedCaseId),
    getExpenses({
      case_id: normalizedCaseId,
      date_from: expenseDateRange.value[0] || undefined,
      date_to: expenseDateRange.value[1] || undefined,
      include_stats: true,
      page: 1,
      page_size: 100,
    }),
  ])

  if (incomeResult.status === 'fulfilled') {
    income.value = incomeResult.value
  } else {
    const apiError = toApiError(incomeResult.reason)
    if (apiError?.status === 404 && apiError.code === 'CASE_RECEIPT_NOT_FOUND') {
      income.value = createEmptyIncome(normalizedCaseId)
      incomeMissingHint.value = true
    } else {
      income.value = createEmptyIncome(normalizedCaseId)
      error.value = apiError
      ElMessage.error(mapIncomeError(incomeResult.reason))
    }
  }

  if (expenseResult.status === 'fulfilled') {
    const items = expenseResult.value.items
    expenseItems.value = items
    expenseStats.value = expenseResult.value.stats || deriveExpenseStatsFromItems(items)
  } else {
    if (!error.value) {
      error.value = toApiError(expenseResult.reason)
    }
    ElMessage.error(mapExpenseError(expenseResult.reason))
    expenseItems.value = []
    expenseStats.value = createEmptyExpenseStats()
  }

  loading.value = false
}
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

.hint-alert {
  margin-bottom: 12px;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.source-note {
  color: var(--text-sub);
  font-size: 13px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.stat-card {
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 14px;
  background: var(--bg-surface-2);
}

.stat-label {
  font-size: 13px;
  color: var(--text-sub);
}

.stat-value {
  margin-top: 8px;
  font-size: 22px;
  font-weight: 700;
}

.section-card {
  margin-top: 4px;
}

.section-title {
  font-weight: 600;
}

.mono-num {
  font-family: var(--font-mono);
}

.negative-value {
  color: var(--color-danger);
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
