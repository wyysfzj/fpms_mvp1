<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button
          v-if="stepFilter"
          @click="clearFilter"
          style="margin-right: 8px;"
        >
          {{ ZH.caseList.clearFilter }}
        </el-button>
        <router-link to="/cases/new">
          <el-button type="primary">{{ ZH.caseList.newCase }}</el-button>
        </router-link>
      </div>
    </div>

    <!-- FB5: Advanced Filter Panel -->
    <el-card class="filter-panel" shadow="never" style="margin-bottom: 16px;">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="客户" class="filter-item">
            <el-select
              v-model="filters.client_id"
              placeholder="全部客户"
              clearable
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="c in clientOptions"
                :key="c.id"
                :label="c.name"
                :value="c.id"
              />
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
            <el-input
              v-model="filters.country"
              placeholder="请输入国家/地区代码"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="状态" class="filter-item">
            <el-select v-model="filters.status" placeholder="全部" clearable style="width: 100%">
              <el-option
                v-for="(label, key) in statusOptions"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="时间区间从" class="filter-item">
            <el-date-picker
              v-model="filters.date_from"
              type="date"
              placeholder="起始日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="时间区间至" class="filter-item">
            <el-date-picker
              v-model="filters.date_to"
              type="date"
              placeholder="截止日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="代理人" class="filter-item">
            <el-input
              v-model="filters.agent_id"
              placeholder="请输入代理人ID"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row justify="end">
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleResetFilters">重置</el-button>
      </el-row>
    </el-card>

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
    </div>

    <div class="distribution-grid">
      <div class="distribution-card">
        <div class="distribution-title">按状态统计</div>
        <div v-if="summary.status_counts.length" class="distribution-list">
          <div
            v-for="item in summary.status_counts"
            :key="`status-${item.key}`"
            class="distribution-item"
          >
            <span>{{ statusOptions[item.key] || item.key }}</span>
            <span class="distribution-count">{{ item.count }} 件</span>
          </div>
        </div>
        <div v-else class="distribution-empty">暂无状态统计</div>
      </div>
      <div class="distribution-card">
        <div class="distribution-title">按案件类型统计</div>
        <div v-if="summary.case_type_counts.length" class="distribution-list">
          <div
            v-for="item in summary.case_type_counts"
            :key="`type-${item.key}`"
            class="distribution-item"
          >
            <span>{{ caseTypeLabel(item.key) }}</span>
            <span class="distribution-count">{{ item.count }} 件</span>
          </div>
        </div>
        <div v-else class="distribution-empty">暂无类型统计</div>
      </div>
    </div>

    <!-- Filter subtitle -->
    <div v-if="stepFilter && stepLabel" class="page-filter-subtitle muted" style="margin-bottom: 12px;">
      共 {{ total }} 件，均处于{{ stepNoText }}
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
        :title="ZH.caseList.emptyTitle"
        :message="ZH.caseList.emptyMsg"
        icon="📂"
        :cta-label="ZH.caseList.newCase"
        cta-to="/cases/new"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="displayCases"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="case_no" :label="ZH.caseList.caseNo" width="140" />
        <el-table-column prop="client_name" :label="ZH.caseList.client" min-width="130" />
        <el-table-column prop="title" :label="ZH.caseList.caseTitle" min-width="200" />
        <el-table-column :label="ZH.workflow.colStep" width="150">
          <template #default="{ row }">
            {{ getFlow(row).stepNoText }} · {{ getFlow(row).stepLabel }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.workflow.colStatus" width="150">
          <template #default="{ row }">
            <span class="tag" :class="getTagClass(row)">
              {{ getFlow(row).rule.legalText }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.workflow.colFilingDate" width="120">
          <template #default="{ row }">
            {{ row.filing_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.caseList.updated" width="160">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.caseList.actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click="handleView(row)">
              {{ ZH.caseList.view }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { getCases } from '../../../api/cases'
import { getClients } from '../../../api/clients'
import type { Case, CaseListResponse } from '../../../api/cases.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { CASE_STATUS_TEXT } from '../../../constants/displayText'
import { getCaseWorkflow, getStatusTagClass, getStatusRule, getStepIndex, WORKFLOW_STEPS } from '../../../constants/workflow'

const route = useRoute()
const router = useRouter()

const cases = ref<Case[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

// FB5: Filter state
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
const summary = ref<CaseListResponse['summary']>({
  total_case_count: 0,
  status_counts: [],
  case_type_counts: [],
})

// Client options for selector
const clientOptions = ref<Array<{ id: string; name: string }>>([])

// Status options (from displayText.ts)
const statusOptions = CASE_STATUS_TEXT

// Step filter from route query
const stepFilter = computed(() => (route.query.step as string) || null)

const stepLabel = computed(() => {
  if (!stepFilter.value) return null
  const step = WORKFLOW_STEPS.find(s => s.key === stepFilter.value)
  return step?.label || stepFilter.value
})

const stepNoText = computed(() => {
  if (!stepFilter.value) return ''
  const idx = getStepIndex(stepFilter.value)
  return `第${idx + 1}步/5`
})

const pageTitle = computed(() => {
  if (stepFilter.value && stepLabel.value) {
    return ZH.caseList.titleFiltered.replace('{name}', stepLabel.value)
  }
  return ZH.caseList.title
})

// Filter cases by step client-side
const displayCases = computed(() => {
  if (!stepFilter.value) return cases.value
  return cases.value.filter(c => {
    const rule = getStatusRule(c.status)
    return rule.stepKey === stepFilter.value
  })
})

async function fetchCases() {
  loading.value = true
  error.value = null
  try {
    const result = await getCases({
      page: page.value,
      page_size: stepFilter.value ? 200 : pageSize.value,
      ...filters,
    })
    cases.value = result.items
    summary.value = result.summary
    if (stepFilter.value) {
      total.value = displayCases.value.length
    } else {
      total.value = result.total
    }
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

function handleView(row: Case) {
  router.push(`/cases/${row.id}`)
}

function clearFilter() {
  router.push({ path: '/cases' })
}

function getFlow(c: Case) {
  return getCaseWorkflow(c.status)
}

function getTagClass(c: Case) {
  return getStatusTagClass(c.status || '')
}

/** FB5: Load client options for filter dropdown */
async function fetchClientOptions() {
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clientOptions.value = result.items.map(c => ({ id: c.id, name: c.name }))
  } catch {
    // Silently fail — client filter will just be empty
  }
}

/** FB5: Trigger filtered search — resets to page 1 */
function handleSearch() {
  page.value = 1
  fetchCases()
}

/** FB5: Reset all filter fields and re-fetch */
function handleResetFilters() {
  filters.client_id = ''
  filters.case_type = ''
  filters.patent_category = ''
  filters.country = ''
  filters.status = ''
  filters.date_from = ''
  filters.date_to = ''
  filters.agent_id = ''
  page.value = 1
  fetchCases()
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

// Watch for pagination and filter changes
watch([page, pageSize], () => {
  fetchCases()
})

watch(() => route.query.step, () => {
  page.value = 1
  fetchCases()
})

onMounted(() => {
  fetchCases()
  fetchClientOptions()
})
</script>

<style scoped>
.filter-panel {
  border: 1px solid var(--color-border);
}
.filter-panel .filter-item {
  margin-bottom: 8px;
}
.filter-panel .filter-item :deep(.el-form-item__label) {
  font-size: 12px;
  color: var(--text-sub);
  padding-bottom: 2px;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card,
.distribution-card {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--el-bg-color);
  padding: 14px 16px;
}

.summary-label,
.distribution-title {
  font-size: 12px;
  color: var(--text-sub);
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

.distribution-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
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
