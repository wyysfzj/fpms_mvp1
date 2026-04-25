<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">案件统计</h1>
        <span class="page-count">{{ summary.total_case_count }} 件</span>
      </div>
      <div class="page-header-right">
        <router-link to="/cases">
          <el-button>返回案件列表</el-button>
        </router-link>
      </div>
    </div>

    <el-card class="filter-panel" shadow="never">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="客户" class="filter-item">
            <el-select v-model="filters.client_id" placeholder="全部客户" clearable filterable style="width: 100%">
              <el-option v-for="c in clientOptions" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="案件类型" class="filter-item">
            <el-select v-model="filters.case_type" placeholder="全部" clearable style="width: 100%">
              <el-option label="普通申请" value="NORMAL" />
              <el-option label="PCT国际" value="PCT_INTL" />
              <el-option label="PCT国内" value="PCT_NATL" />
              <el-option label="优先权" value="PRIORITY" />
              <el-option label="检索" value="SEARCH" />
              <el-option label="咨询" value="CONSULTING" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="专利类别" class="filter-item">
            <el-select v-model="filters.patent_category" placeholder="全部" clearable style="width: 100%">
              <el-option label="发明" value="INV" />
              <el-option label="实用新型" value="UM" />
              <el-option label="外观设计" value="DES" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="国家/地区" class="filter-item">
            <el-input v-model.trim="filters.country" placeholder="请输入国家/地区代码" clearable />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="状态" class="filter-item">
            <el-select v-model="filters.status" placeholder="全部" clearable style="width: 100%">
              <el-option v-for="(label, key) in statusOptions" :key="key" :label="label" :value="key" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="时间区间从" class="filter-item">
            <el-date-picker v-model="filters.date_from" type="date" placeholder="起始日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="时间区间至" class="filter-item">
            <el-date-picker v-model="filters.date_to" type="date" placeholder="截止日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="代理人" class="filter-item">
            <el-input v-model.trim="filters.agent_id" placeholder="请输入代理人ID" clearable />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row justify="end">
        <el-button type="primary" @click="handleSearch">查询统计</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-row>
    </el-card>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <template v-else>
      <div class="report-summary">
        <div class="summary-card">
          <span class="summary-label">案件总数</span>
          <span class="summary-value">{{ summary.total_case_count }} 件</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">状态分布</span>
          <span class="summary-value">{{ summary.status_counts.length }} 类</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">类型分布</span>
          <span class="summary-value">{{ summary.case_type_counts.length }} 类</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">客户分布</span>
          <span class="summary-value">{{ summary.client_counts.length }} 户</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">国别分布</span>
          <span class="summary-value">{{ summary.country_counts.length }} 类</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">代理人分布</span>
          <span class="summary-value">{{ summary.agent_counts.length }} 人</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">授权数量</span>
          <span class="summary-value">{{ summary.granted_count }} 件</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">授权率</span>
          <span class="summary-value">{{ formatGrantRate(summary.grant_rate) }}</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">终止数量</span>
          <span class="summary-value">{{ summary.terminated_count }} 件</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">无效数量</span>
          <span class="summary-value">{{ summary.invalidated_count }} 件</span>
        </div>
        <div class="summary-card">
          <span class="summary-label">审中数量</span>
          <span class="summary-value">{{ summary.in_prosecution_count }} 件</span>
        </div>
      </div>

      <div class="distribution-grid">
        <section class="distribution-card">
          <div class="distribution-title">按状态统计</div>
          <div v-if="summary.status_counts.length" class="distribution-list">
            <div v-for="item in summary.status_counts" :key="`status-${item.key}`" class="distribution-item">
              <span>{{ statusOptions[item.key] || item.key }}</span>
              <span class="distribution-count">{{ item.count }} 件</span>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无状态统计</div>
        </section>
        <section class="distribution-card">
          <div class="distribution-title">按案件类型统计</div>
          <div v-if="summary.case_type_counts.length" class="distribution-list">
            <div v-for="item in summary.case_type_counts" :key="`type-${item.key}`" class="distribution-item">
              <span>{{ caseTypeLabel(item.key) }}</span>
              <span class="distribution-count">{{ item.count }} 件</span>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无类型统计</div>
        </section>
        <section class="distribution-card">
          <div class="distribution-title">按客户统计</div>
          <div v-if="summary.client_counts.length" class="distribution-list">
            <div v-for="item in summary.client_counts" :key="`client-${item.key}`" class="distribution-item-stacked">
              <div class="distribution-row">
                <span>{{ item.label }}</span>
                <span class="distribution-count">{{ item.count }} 件</span>
              </div>
              <div class="distribution-subline">{{ clientCaseTypeSummary(item.case_type_counts) }}</div>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无客户统计</div>
        </section>
        <section class="distribution-card">
          <div class="distribution-title">按国别统计</div>
          <div v-if="summary.country_counts.length" class="distribution-list">
            <div v-for="item in summary.country_counts" :key="`country-${item.key}`" class="distribution-item">
              <span>{{ countryLabel(item.key) }}</span>
              <span class="distribution-count">{{ item.count }} 件</span>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无国别统计</div>
        </section>
        <section class="distribution-card">
          <div class="distribution-title">按代理人统计</div>
          <div v-if="summary.agent_counts.length" class="distribution-list">
            <div v-for="item in summary.agent_counts" :key="`agent-${item.key}`" class="distribution-item">
              <span>{{ agentLabel(item.key) }}</span>
              <span class="distribution-count">{{ item.count }} 件</span>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无代理人统计</div>
        </section>
      </div>

      <div class="distribution-grid">
        <section class="distribution-card">
          <div class="distribution-title">按年份趋势</div>
          <div v-if="summary.year_trends.length" class="distribution-list">
            <div v-for="item in summary.year_trends" :key="`year-${item.key}`" class="distribution-item-stacked">
              <div class="distribution-row"><span>{{ item.label }}</span></div>
              <div class="distribution-subline">{{ formatTrendSummary(item) }}</div>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无年份趋势</div>
        </section>
        <section class="distribution-card">
          <div class="distribution-title">按月份趋势</div>
          <div v-if="summary.month_trends.length" class="distribution-list">
            <div v-for="item in summary.month_trends" :key="`month-${item.key}`" class="distribution-item-stacked">
              <div class="distribution-row"><span>{{ item.label }}</span></div>
              <div class="distribution-subline">{{ formatTrendSummary(item) }}</div>
            </div>
          </div>
          <div v-else class="distribution-empty">暂无月份趋势</div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { getCases } from '../../../api/cases'
import { getClients } from '../../../api/clients'
import type { CaseListSummary } from '../../../api/cases.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import { CASE_STATUS_TEXT } from '../../../constants/displayText'

const emptySummary = (): CaseListSummary => ({
  total_case_count: 0,
  status_counts: [],
  case_type_counts: [],
  client_counts: [],
  country_counts: [],
  agent_counts: [],
  year_trends: [],
  month_trends: [],
  granted_count: 0,
  grant_rate: null,
  terminated_count: 0,
  invalidated_count: 0,
  in_prosecution_count: 0,
})

const filters = reactive({
  client_id: '',
  case_type: '',
  patent_category: '',
  country: '',
  status: '',
  date_from: '',
  date_to: '',
  agent_id: '',
})
const clientOptions = ref<Array<{ id: string; name: string }>>([])
const summary = ref<CaseListSummary>(emptySummary())
const loading = ref(false)
const error = ref<ApiError | null>(null)
const statusOptions = CASE_STATUS_TEXT

async function fetchReport() {
  loading.value = true
  error.value = null
  try {
    const result = await getCases({
      page: 1,
      page_size: 1,
      ...filters,
    })
    summary.value = result.summary
  } catch (err) {
    error.value = err as ApiError
    summary.value = emptySummary()
  } finally {
    loading.value = false
  }
}

async function fetchClientOptions() {
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clientOptions.value = result.items.map(c => ({ id: c.id, name: c.name }))
  } catch {
    clientOptions.value = []
  }
}

function handleSearch() {
  fetchReport()
}

function handleReset() {
  filters.client_id = ''
  filters.case_type = ''
  filters.patent_category = ''
  filters.country = ''
  filters.status = ''
  filters.date_from = ''
  filters.date_to = ''
  filters.agent_id = ''
  fetchReport()
}

function formatGrantRate(value: number | null): string {
  if (value == null) return '暂无'
  return `${(value * 100).toFixed(1)}%`
}

function caseTypeLabel(value?: string) {
  switch (value) {
    case 'NORMAL':
      return '普通申请'
    case 'PCT_INTL':
      return 'PCT国际'
    case 'PCT_NATL':
      return 'PCT国内'
    case 'PRIORITY':
      return '优先权'
    case 'SEARCH':
      return '检索'
    case 'CONSULTING':
      return '咨询'
    default:
      return value || '未分类'
  }
}

function countryLabel(value?: string) {
  return value || '未填写'
}

function clientCaseTypeSummary(items: Array<{ key: string; count: number }>) {
  if (!items.length) return '暂无类型分布'
  return items.map(item => `${caseTypeLabel(item.key)} ${item.count} 件`).join(' · ')
}

function agentLabel(value?: string) {
  return value || '未分配'
}

function formatTrendSummary(item: {
  new_case_count: number
  granted_count: number
  terminated_count: number
  invalidated_count: number
  withdrawn_count: number
  abandoned_count: number
}) {
  return [
    `新案 ${item.new_case_count} 件`,
    `授权 ${item.granted_count} 件`,
    `终止 ${item.terminated_count} 件`,
    `无效 ${item.invalidated_count} 件`,
    `撤回 ${item.withdrawn_count} 件`,
    `放弃 ${item.abandoned_count} 件`,
  ].join(' · ')
}

onMounted(() => {
  fetchReport()
  fetchClientOptions()
})
</script>

<style scoped>
.filter-panel {
  margin-bottom: 16px;
  border: 1px solid var(--color-border);
}

.filter-item {
  margin-bottom: 8px;
}

.filter-item :deep(.el-form-item__label) {
  padding-bottom: 2px;
  color: var(--text-sub);
  font-size: 12px;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card,
.distribution-card {
  padding: 14px 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--el-bg-color);
}

.summary-label,
.distribution-title {
  color: var(--text-sub);
  font-size: 12px;
}

.summary-value {
  display: block;
  margin-top: 6px;
  font-size: 18px;
  font-weight: 600;
}

.distribution-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.distribution-item,
.distribution-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
}

.distribution-item-stacked {
  font-size: 13px;
}

.distribution-subline {
  margin-top: 4px;
  color: var(--text-sub);
  font-size: 12px;
}

.distribution-count {
  font-weight: 600;
}

.distribution-empty {
  margin-top: 10px;
  color: var(--text-sub);
  font-size: 13px;
}

@media (max-width: 960px) {
  .report-summary,
  .distribution-grid {
    grid-template-columns: 1fr;
  }
}
</style>
