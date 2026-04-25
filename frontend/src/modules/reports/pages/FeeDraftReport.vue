<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">费用草稿统计</h1>
        <span class="page-count">{{ summary.total_draft_count }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/fees/drafts">
          <el-button>返回费用草稿</el-button>
        </router-link>
      </div>
    </div>

    <el-form class="filter-form" :inline="true">
      <el-form-item label="客户编号">
        <el-input v-model.trim="filters.client_id" class="filter-input" clearable placeholder="请输入客户编号" @keyup.enter="fetchReport" />
      </el-form-item>
      <el-form-item label="案件编号">
        <el-input v-model.trim="filters.case_id" class="filter-input" clearable placeholder="请输入案件编号" @keyup.enter="fetchReport" />
      </el-form-item>
      <el-form-item label="费用类型">
        <el-select v-model="filters.fee_type" class="filter-select" clearable placeholder="全部费用类型">
          <el-option label="全部" value="" />
          <el-option label="服务费" value="SERVICE" />
          <el-option label="官费" value="GOV" />
          <el-option label="杂费" value="MISC" />
        </el-select>
      </el-form-item>
      <el-form-item label="币种">
        <el-input v-model.trim="filters.currency" class="filter-input" clearable placeholder="例如 CNY" @keyup.enter="fetchReport" />
      </el-form-item>
      <el-form-item label="草稿日期">
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
      <el-form-item label="草稿状态">
        <el-select v-model="filters.draft_status" class="filter-select" clearable placeholder="全部草稿状态">
          <el-option label="全部" value="" />
          <el-option label="开放" value="OPEN" />
          <el-option label="已锁定" value="LOCKED" />
        </el-select>
      </el-form-item>
      <el-form-item label="账单状态">
        <el-select v-model="filters.bill_status" class="filter-select" clearable placeholder="全部账单状态">
          <el-option label="全部" value="" />
          <el-option label="未结清" value="UNSETTLED" />
          <el-option label="部分结清" value="PARTIALLY_SETTLED" />
          <el-option label="已结清" value="SETTLED" />
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

    <LoadingBlock v-if="loading" :rows="8" />

    <template v-else>
      <div class="report-summary">
        <div class="summary-card">
          <span class="summary-label">草稿数量</span>
          <span class="summary-value">{{ summary.total_draft_count }} 条</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">服务费总额</span>
          <span class="summary-value amount">{{ formatAmount(summary.service_fee_amount, summaryCurrency) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">官费总额</span>
          <span class="summary-value amount">{{ formatAmount(summary.government_fee_amount, summaryCurrency) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">草稿总收入</span>
          <span class="summary-value amount">{{ formatAmount(summary.income_amount, summaryCurrency) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">已开账单金额</span>
          <span class="summary-value amount">{{ formatAmount(summary.billed_amount, summaryCurrency) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">已收金额</span>
          <span class="summary-value amount">{{ formatAmount(summary.received_amount, summaryCurrency) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">未收余额</span>
          <span class="summary-value amount">{{ formatAmount(summary.unpaid_balance_amount, summaryCurrency) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">部分收款账单数</span>
          <span class="summary-value">{{ summary.partially_received_bill_count }} 张</span>
        </div>
      </div>

      <div class="grouped-summary-grid">
        <section class="grouped-summary-card">
          <div class="grouped-summary-header">
            <h3>按客户汇总</h3>
            <span>{{ summary.client_amounts.length }} 组</span>
          </div>
          <GroupedAmountList :items="summary.client_amounts" :currency="summaryCurrency" empty-text="暂无客户汇总数据" />
        </section>
        <section class="grouped-summary-card">
          <div class="grouped-summary-header">
            <h3>按案件类型汇总</h3>
            <span>{{ summary.case_type_amounts.length }} 组</span>
          </div>
          <GroupedAmountList :items="summary.case_type_amounts" :currency="summaryCurrency" empty-text="暂无案件类型汇总数据" />
        </section>
        <section class="grouped-summary-card">
          <div class="grouped-summary-header">
            <h3>按国家汇总</h3>
            <span>{{ summary.country_amounts.length }} 组</span>
          </div>
          <GroupedAmountList :items="summary.country_amounts" :currency="summaryCurrency" empty-text="暂无国家汇总数据" />
        </section>
        <section class="grouped-summary-card">
          <div class="grouped-summary-header">
            <h3>按代理人服务费汇总</h3>
            <span>{{ summary.agent_service_amounts.length }} 组</span>
          </div>
          <div v-if="summary.agent_service_amounts.length" class="grouped-summary-list">
            <div v-for="item in summary.agent_service_amounts" :key="`agent-${item.key}`" class="grouped-summary-item">
              <div class="grouped-summary-main">
                <span class="grouped-summary-title">{{ item.label }}</span>
                <span class="grouped-summary-sub">草稿 {{ item.draft_count }} 条</span>
              </div>
              <div class="grouped-summary-amounts">
                <span class="amount">服务费 {{ formatAmount(item.service_fee_amount, summaryCurrency) }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无代理人服务费汇总数据" :image-size="72" />
        </section>
        <section class="grouped-summary-card">
          <div class="grouped-summary-header">
            <h3>按年份汇总</h3>
            <span>{{ summary.year_amounts.length }} 组</span>
          </div>
          <TrendAmountList :items="summary.year_amounts" :currency="summaryCurrency" empty-text="暂无按年份汇总数据" />
        </section>
        <section class="grouped-summary-card">
          <div class="grouped-summary-header">
            <h3>按月份汇总</h3>
            <span>{{ summary.month_amounts.length }} 组</span>
          </div>
          <TrendAmountList :items="summary.month_amounts" :currency="summaryCurrency" empty-text="暂无按月份汇总数据" />
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, reactive, ref, type PropType } from 'vue'
import { getFeeDrafts } from '../../../api/fees'
import type {
  FeeDraftGroupedAmount,
  FeeDraftReportSummary,
  FeeDraftStatus,
  FeeDraftTrendAmount,
  FeeMoney,
} from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

const emptySummary = (): FeeDraftReportSummary => ({
  total_draft_count: 0,
  service_fee_amount: 0,
  government_fee_amount: 0,
  income_amount: 0,
  billed_amount: 0,
  received_amount: 0,
  unpaid_balance_amount: 0,
  partially_received_bill_count: 0,
  client_amounts: [],
  case_type_amounts: [],
  country_amounts: [],
  agent_service_amounts: [],
  year_amounts: [],
  month_amounts: [],
})

const filters = reactive<{
  client_id: string
  case_id: string
  fee_type: string
  currency: string
  draft_status: '' | FeeDraftStatus
  bill_status: string
  date_range: [string, string] | []
}>({
  client_id: '',
  case_id: '',
  fee_type: '',
  currency: '',
  draft_status: '',
  bill_status: '',
  date_range: [],
})
const summary = ref<FeeDraftReportSummary>(emptySummary())
const loading = ref(false)
const error = ref<ApiError | null>(null)
const summaryCurrency = computed(() => filters.currency || 'CNY')

async function fetchReport() {
  loading.value = true
  error.value = null
  try {
    const [date_from, date_to] = filters.date_range
    const result = await getFeeDrafts({
      page: 1,
      page_size: 1,
      client_id: filters.client_id || undefined,
      case_id: filters.case_id || undefined,
      fee_type: filters.fee_type || undefined,
      currency: filters.currency || undefined,
      draft_status: filters.draft_status || undefined,
      status: filters.draft_status || undefined,
      bill_status: filters.bill_status || undefined,
      date_from,
      date_to,
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
  filters.client_id = ''
  filters.case_id = ''
  filters.fee_type = ''
  filters.currency = ''
  filters.draft_status = ''
  filters.bill_status = ''
  filters.date_range = []
  fetchReport()
}

function formatAmount(amount: FeeMoney, currency?: string): string {
  const curr = currency || 'CNY'
  const numericAmount = typeof amount === 'number' ? amount : Number(amount)
  if (Number.isNaN(numericAmount)) return `${curr} ${amount}`

  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(numericAmount)
}

function formatDraftTypeBreakdown(rows: Array<{ label: string; income_amount: FeeMoney }>, currency: string): string {
  if (!rows.length) return '暂无'
  return rows
    .map((row) => `${row.label} ${formatAmount(row.income_amount, currency)}`)
    .join('，')
}

const GroupedAmountList = defineComponent({
  props: {
    items: { type: Array as PropType<FeeDraftGroupedAmount[]>, required: true },
    currency: { type: String, required: true },
    emptyText: { type: String, required: true },
  },
  setup(props) {
    return () => props.items.length
      ? h('div', { class: 'grouped-summary-list' }, props.items.map((item) => h('div', {
        key: item.key,
        class: 'grouped-summary-item',
      }, [
        h('div', { class: 'grouped-summary-main' }, [
          h('span', { class: 'grouped-summary-title' }, item.label),
          h('span', { class: 'grouped-summary-sub' }, `草稿 ${item.draft_count} 条`),
        ]),
        h('div', { class: 'grouped-summary-amounts' }, [
          h('span', `服务费 ${formatAmount(item.service_fee_amount, props.currency)}`),
          h('span', `官费 ${formatAmount(item.government_fee_amount, props.currency)}`),
          h('span', { class: 'amount' }, `收入 ${formatAmount(item.income_amount, props.currency)}`),
        ]),
      ])))
      : h('div', { class: 'empty-inline' }, props.emptyText)
  },
})

const TrendAmountList = defineComponent({
  props: {
    items: { type: Array as PropType<FeeDraftTrendAmount[]>, required: true },
    currency: { type: String, required: true },
    emptyText: { type: String, required: true },
  },
  setup(props) {
    return () => props.items.length
      ? h('div', { class: 'grouped-summary-list' }, props.items.map((item) => h('div', {
        key: item.key,
        class: 'grouped-summary-item',
      }, [
        h('div', { class: 'grouped-summary-main' }, [
          h('span', { class: 'grouped-summary-title' }, item.label),
          h('span', { class: 'grouped-summary-sub' }, `草稿 ${item.draft_count} 条`),
        ]),
        h('div', { class: 'grouped-summary-amounts' }, [
          h('span', `服务费 ${formatAmount(item.service_fee_amount, props.currency)}`),
          h('span', `官费 ${formatAmount(item.government_fee_amount, props.currency)}`),
          h('span', { class: 'amount' }, `收入 ${formatAmount(item.income_amount, props.currency)}`),
          h('span', { class: 'grouped-summary-breakdown' }, `类型分布 ${formatDraftTypeBreakdown(item.draft_type_amounts, props.currency)}`),
        ]),
      ])))
      : h('div', { class: 'empty-inline' }, props.emptyText)
  },
})

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

.grouped-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.grouped-summary-card {
  padding: 16px;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  background: var(--surface-raised);
}

.grouped-summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.grouped-summary-header h3 {
  margin: 0;
  font-size: 15px;
}

.grouped-summary-header span,
.empty-inline {
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
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border-radius: 8px;
  background: var(--surface-default);
}

.grouped-summary-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.grouped-summary-title {
  font-weight: 600;
}

.grouped-summary-sub {
  color: var(--text-sub);
  font-size: 12px;
}

.grouped-summary-amounts {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.grouped-summary-breakdown {
  color: var(--text-sub);
  font-size: 12px;
  line-height: 1.5;
}

.amount {
  font-family: var(--font-mono);
  font-weight: 500;
}
</style>
