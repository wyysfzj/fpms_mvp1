<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">年费任务统计</h1>
        <span class="page-count" aria-live="polite">{{ summary.total_task_count }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/annuity/tasks">
          <el-button>返回年费任务</el-button>
        </router-link>
      </div>
    </div>

    <el-form class="filter-form" :inline="true">
      <el-form-item label="客户编号">
        <el-input v-model="filters.client_id" class="filter-input" clearable placeholder="请输入客户编号" @keyup.enter="applyFilters" />
      </el-form-item>
      <el-form-item label="案件编号">
        <el-input v-model="filters.case_id" class="filter-input" clearable placeholder="请输入案件编号" @keyup.enter="applyFilters" />
      </el-form-item>
      <el-form-item label="国家">
        <el-input v-model="filters.country" class="filter-input" clearable placeholder="例如 CN" @keyup.enter="applyFilters" />
      </el-form-item>
      <el-form-item label="年度">
        <el-input-number v-model="filters.annuity_year" class="filter-input" :min="1" :step="1" controls-position="right" />
      </el-form-item>
      <el-form-item label="任务状态">
        <el-select v-model="filters.task_status" class="filter-select" clearable placeholder="全部任务状态">
          <el-option label="全部" value="" />
          <el-option label="待处理" value="OPEN" />
          <el-option label="已完成" value="DONE" />
          <el-option label="已取消" value="CANCELLED" />
        </el-select>
      </el-form-item>
      <el-form-item label="缴费状态">
        <el-select v-model="filters.payment_status" class="filter-select" clearable placeholder="全部缴费状态">
          <el-option label="全部" value="" />
          <el-option label="已缴费" value="PAID" />
          <el-option label="未缴费" value="UNPAID" />
        </el-select>
      </el-form-item>
      <el-form-item label="到期日期">
        <el-date-picker
          v-model="filters.date_range"
          class="filter-range"
          type="daterange"
          range-separator="至"
          start-placeholder="到期开始日期"
          end-placeholder="到期结束日期"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          clearable
        />
      </el-form-item>
      <el-form-item label="处理范围">
        <el-select v-model="filters.pending_mode" class="filter-select" clearable placeholder="全部处理范围">
          <el-option label="全部" value="" />
          <el-option label="仅待处理" value="pending" />
          <el-option label="仅已处理" value="processed" />
        </el-select>
      </el-form-item>
      <el-form-item label="通知状态">
        <el-select v-model="filters.notice_status" class="filter-select" clearable placeholder="全部通知状态">
          <el-option label="全部" value="" />
          <el-option label="待通知" value="PENDING" />
          <el-option label="已通知" value="SENT" />
          <el-option label="无需通知" value="SKIPPED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="applyFilters">查询统计</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <template v-else>
      <div class="report-summary">
        <div class="summary-card">
          <span class="summary-label">任务总数</span>
          <span class="summary-value">{{ summary.total_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">待处理任务</span>
          <span class="summary-value">{{ summary.open_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">已完成任务</span>
          <span class="summary-value">{{ summary.done_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">逾期任务</span>
          <span class="summary-value">{{ summary.overdue_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">官费已缴任务</span>
          <span class="summary-value">{{ summary.official_paid_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">客户已收任务</span>
          <span class="summary-value">{{ summary.client_received_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">已收未缴</span>
          <span class="summary-value">{{ summary.collected_not_paid_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">未收未缴</span>
          <span class="summary-value">{{ summary.outstanding_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">监视任务</span>
          <span class="summary-value">{{ summary.monitored_task_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">按时缴费</span>
          <span class="summary-value">{{ summary.on_time_paid_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">逾期缴费</span>
          <span class="summary-value">{{ summary.late_paid_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">监视成功率</span>
          <span class="summary-value">{{ formatSuccessRate(summary.success_rate) }}</span>
        </div>
      </div>

      <div class="distribution-summary">
        <section class="distribution-card">
          <div class="distribution-title">状态分布</div>
          <div v-if="summary.status_counts.length" class="distribution-tags">
            <el-tag v-for="item in summary.status_counts" :key="`status-${item.key}`" size="small" effect="plain">
              {{ taskStatusText(item.key) }} {{ item.count }}
            </el-tag>
          </div>
          <div v-else class="distribution-empty">暂无状态分布</div>
        </section>
        <section class="distribution-card">
          <div class="distribution-title">年度分布</div>
          <div v-if="summary.year_counts.length" class="distribution-tags">
            <el-tag v-for="item in summary.year_counts" :key="`year-${item.key}`" size="small" effect="plain">
              第 {{ item.key }} 年 {{ item.count }}
            </el-tag>
          </div>
          <div v-else class="distribution-empty">暂无年度分布</div>
        </section>
      </div>

      <div class="grouped-summary-grid">
        <section class="distribution-card">
          <div class="distribution-header">
            <div class="distribution-title">按客户金额汇总</div>
            <span>{{ summary.client_amounts.length }} 组</span>
          </div>
          <div v-if="summary.client_amounts.length" class="grouped-summary-list">
            <div v-for="item in summary.client_amounts" :key="`client-${item.key}`" class="grouped-summary-item">
              <div class="grouped-summary-name">{{ item.label }}</div>
              <div class="grouped-summary-meta">任务 {{ item.task_count }} 条</div>
              <div class="grouped-summary-amounts">
                <span>应缴 {{ formatMoney(item.payable_amount) }}</span>
                <span>官费实缴 {{ formatMoney(item.official_paid_amount) }}</span>
                <span>客户实收 {{ formatMoney(item.client_received_amount) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无客户金额汇总</div>
        </section>

        <section class="distribution-card">
          <div class="distribution-header">
            <div class="distribution-title">按国家金额汇总</div>
            <span>{{ summary.country_amounts.length }} 组</span>
          </div>
          <div v-if="summary.country_amounts.length" class="grouped-summary-list">
            <div v-for="item in summary.country_amounts" :key="`country-${item.key}`" class="grouped-summary-item">
              <div class="grouped-summary-name">{{ item.label }}</div>
              <div class="grouped-summary-meta">任务 {{ item.task_count }} 条</div>
              <div class="grouped-summary-amounts">
                <span>应缴 {{ formatMoney(item.payable_amount) }}</span>
                <span>官费实缴 {{ formatMoney(item.official_paid_amount) }}</span>
                <span>客户实收 {{ formatMoney(item.client_received_amount) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无国家金额汇总</div>
        </section>

        <section class="distribution-card">
          <div class="distribution-header">
            <div class="distribution-title">按年度金额汇总</div>
            <span>{{ summary.year_amounts.length }} 组</span>
          </div>
          <div v-if="summary.year_amounts.length" class="grouped-summary-list">
            <div v-for="item in summary.year_amounts" :key="`year-amount-${item.key}`" class="grouped-summary-item">
              <div class="grouped-summary-name">{{ item.label }}</div>
              <div class="grouped-summary-meta">任务 {{ item.task_count }} 条</div>
              <div class="grouped-summary-amounts">
                <span>应缴 {{ formatMoney(item.payable_amount) }}</span>
                <span>官费实缴 {{ formatMoney(item.official_paid_amount) }}</span>
                <span>客户实收 {{ formatMoney(item.client_received_amount) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无年度金额汇总</div>
        </section>
      </div>
    </template>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { getAnnuityTasks } from '../../../api/annuity'
import type { AnnuityPendingMode, AnnuityTaskReportSummary } from '../../../api/annuity.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

const emptySummary = (): AnnuityTaskReportSummary => ({
  total_task_count: 0,
  open_task_count: 0,
  done_task_count: 0,
  overdue_task_count: 0,
  official_paid_task_count: 0,
  client_received_task_count: 0,
  collected_not_paid_task_count: 0,
  outstanding_task_count: 0,
  monitored_task_count: 0,
  on_time_paid_count: 0,
  late_paid_count: 0,
  success_rate: null,
  status_counts: [],
  year_counts: [],
  client_amounts: [],
  country_amounts: [],
  year_amounts: [],
})

const filters = reactive<{
  client_id: string
  case_id: string
  country: string
  annuity_year: number | undefined
  task_status: string
  payment_status: string
  pending_mode: AnnuityPendingMode | ''
  notice_status: string
  date_range: string[]
}>({
  client_id: '',
  case_id: '',
  country: '',
  annuity_year: undefined,
  task_status: '',
  payment_status: '',
  pending_mode: '',
  notice_status: '',
  date_range: [],
})
const summary = ref<AnnuityTaskReportSummary>(emptySummary())
const loading = ref(false)
const error = ref<ApiError | null>(null)

function applyFilters() {
  fetchReport()
}

function resetFilters() {
  filters.client_id = ''
  filters.case_id = ''
  filters.country = ''
  filters.annuity_year = undefined
  filters.task_status = ''
  filters.payment_status = ''
  filters.pending_mode = ''
  filters.notice_status = ''
  filters.date_range = []
  fetchReport()
}

async function fetchReport() {
  loading.value = true
  error.value = null
  try {
    const dueFrom = filters.date_range.length === 2 ? filters.date_range[0] : undefined
    const dueTo = filters.date_range.length === 2 ? filters.date_range[1] : undefined
    const result = await getAnnuityTasks({
      page: 1,
      page_size: 1,
      client_id: filters.client_id || undefined,
      case_id: filters.case_id || undefined,
      country: filters.country || undefined,
      annuity_year: filters.annuity_year,
      task_status: filters.task_status || undefined,
      payment_status: filters.payment_status || undefined,
      pending_mode: filters.pending_mode || undefined,
      notice_status: filters.notice_status || undefined,
      date_from: dueFrom,
      date_to: dueTo,
    })
    summary.value = result.summary
  } catch (err) {
    error.value = err as ApiError
    summary.value = emptySummary()
  } finally {
    loading.value = false
  }
}

function taskStatusText(status: string): string {
  switch (status?.toUpperCase()) {
    case 'OPEN':
      return '待处理'
    case 'DONE':
      return '已完成'
    case 'CANCELLED':
    case 'CANCELED':
      return '已取消'
    default:
      return status || '未知'
  }
}

function formatMoney(amount: number, currency = 'CNY'): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(amount || 0)
}

function formatSuccessRate(value: number | null): string {
  if (value === null) return '暂无'
  return `${(value * 100).toFixed(1)}%`
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

.report-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-raised);
}

.summary-label {
  color: var(--text-sub);
  font-size: 13px;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
}

.distribution-summary,
.grouped-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.distribution-card {
  padding: 16px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-raised);
}

.distribution-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
  color: var(--text-sub);
  font-size: 13px;
}

.distribution-title {
  margin-bottom: 10px;
  color: var(--text-sub);
  font-size: 13px;
}

.distribution-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.grouped-summary-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.grouped-summary-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border-radius: 8px;
  background: var(--el-fill-color-extra-light);
}

.grouped-summary-name {
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: 600;
}

.grouped-summary-meta,
.distribution-empty {
  color: var(--text-sub);
  font-size: 13px;
}

.grouped-summary-amounts {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.page-error {
  outline: none;
}
</style>
