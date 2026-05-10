<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">{{ ZH.feeList.title }}</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/fees/drafts/new">
          <el-button type="primary">{{ ZH.feeList.newDraft }}</el-button>
        </router-link>
        <router-link to="/reports/fee-drafts">
          <el-button>草稿统计</el-button>
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
      <el-form-item label="案件编号">
        <el-input
          v-model="filters.case_no"
          class="filter-input"
          clearable
          placeholder="请输入案件编号"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="费用类型">
        <el-select
          v-model="filters.fee_type"
          class="filter-select"
          clearable
          placeholder="全部费用类型"
        >
          <el-option label="全部" value="" />
          <el-option label="服务费" value="SERVICE" />
          <el-option label="官费" value="GOV" />
          <el-option label="杂费" value="MISC" />
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
        <el-select
          v-model="filters.draft_status"
          class="filter-select"
          clearable
          placeholder="全部草稿状态"
        >
          <el-option label="全部" value="" />
          <el-option label="开放" value="OPEN" />
          <el-option label="已锁定" value="LOCKED" />
        </el-select>
      </el-form-item>
      <el-form-item label="账单状态">
        <el-select
          v-model="filters.bill_status"
          class="filter-select"
          clearable
          placeholder="全部账单状态"
        >
          <el-option label="全部" value="" />
          <el-option label="未结清" value="UNSETTLED" />
          <el-option label="部分结清" value="PARTIALLY_SETTLED" />
          <el-option label="已结清" value="SETTLED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="applyFilters">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        :title="ZH.feeList.emptyTitle"
        :message="ZH.feeList.emptyMsg"
        icon="📝"
        :cta-label="ZH.feeList.newDraft"
        cta-to="/fees/drafts/new"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        :data="drafts"
        stripe
        size="small"
        class="compact-table"
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" :label="ZH.feeList.draftId" min-width="220">
          <template #default="{ row }">
            <div class="draft-cell">
              <span class="id-value">{{ getDraftDisplayId(row.id) }}</span>
              <span class="draft-subtext">{{ row.currency }} · {{ getFeeDraftStatusText(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.case_" min-width="220">
          <template #default="{ row }">
            <router-link
              class="entity-link"
              :to="`/cases/${row.case_id}`"
              @click.stop
            >
              {{ getCaseDisplay(row) }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.client" min-width="220">
          <template #default="{ row }">
            <router-link
              v-if="row.client_id"
              class="entity-link"
              :to="`/clients/${row.client_id}`"
              @click.stop
            >
              {{ getClientDisplay(row) }}
            </router-link>
            <span v-else class="text-muted">{{ getClientDisplay(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="currency" :label="ZH.feeList.currency" width="120" />
        <el-table-column :label="ZH.feeList.status" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ getFeeDraftStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.amount" width="160">
          <template #default="{ row }">
            <span class="amount">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click.stop="goToDetail(row.id)">{{ ZH.feeList.view }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[20, 50, 100]" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getFeeDrafts } from '../../../api/fees'
import type { FeeDraftListItem, FeeDraftStatus, FeeMoney } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { getFeeDraftStatusText } from '../../../constants/displayText'
import { formatMoney } from '../../../utils/money'

const router = useRouter()

const drafts = ref<FeeDraftListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<{
  client_id: string
  case_no: string
  fee_type: string
  currency: string
  draft_status: '' | FeeDraftStatus
  bill_status: string
  date_range: [string, string] | []
}>({
  client_id: '',
  case_no: '',
  fee_type: '',
  currency: '',
  draft_status: '',
  bill_status: '',
  date_range: [],
})
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function applyFilters() {
  page.value = 1
  fetchDrafts()
}

function resetFilters() {
  filters.client_id = ''
  filters.case_no = ''
  filters.fee_type = ''
  filters.currency = ''
  filters.draft_status = ''
  filters.bill_status = ''
  filters.date_range = []
  applyFilters()
}

async function fetchDrafts() {
  loading.value = true
  error.value = null
  try {
    const [date_from, date_to] = filters.date_range
    const result = await getFeeDrafts({
      page: page.value,
      page_size: pageSize.value,
      client_id: filters.client_id || undefined,
      case_no: filters.case_no || undefined,
      fee_type: filters.fee_type || undefined,
      currency: filters.currency || undefined,
      draft_status: filters.draft_status || undefined,
      status: filters.draft_status || undefined,
      bill_status: filters.bill_status || undefined,
      date_from,
      date_to,
    })
    drafts.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
    drafts.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function statusTagType(status: FeeDraftStatus): 'info' | 'warning' {
  return status === 'LOCKED' ? 'warning' : 'info'
}

function formatAmount(amount: FeeMoney, currency?: string): string {
  return formatMoney(amount, currency)
}

function getShortId(id: string | null | undefined): string {
  if (!id) return '—'
  return id.slice(0, 8).toUpperCase()
}

function getDraftDisplayId(id: string): string {
  return `草稿-${getShortId(id)}`
}

function getCaseDisplay(row: FeeDraftListItem): string {
  return row.case_no || `案件-${getShortId(row.case_id)}`
}

function getClientDisplay(row: FeeDraftListItem): string {
  if (row.client_name) return row.client_name
  if (row.client_id) return `客户-${getShortId(row.client_id)}`
  return '未关联客户'
}

function goToDetail(draftId: string) {
  router.push(`/fees/drafts/${draftId}`)
}

function handleRowClick(row: FeeDraftListItem) {
  router.push(`/fees/drafts/${row.id}`)
}

watch([page, pageSize], () => {
  fetchDrafts()
})

onMounted(() => {
  fetchDrafts()
})
</script>

<style scoped>
.text-muted {
  color: var(--text-sub);
}

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

.id-value {
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 600;
}

.draft-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.draft-subtext {
  color: var(--text-sub);
  font-size: 12px;
}

.entity-link {
  color: var(--color-primary);
  font-size: 13px;
  text-decoration: none;
}

.entity-link:hover {
  text-decoration: underline;
}

.amount {
  font-family: var(--font-mono);
  font-weight: 500;
}
</style>
