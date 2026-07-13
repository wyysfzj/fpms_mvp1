<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">费率设置</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="openCreate">新建费率</el-button>
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
        title="暂无费率"
        message="创建首个费率后可在此维护。"
        icon="💰"
        cta-label="新建费率"
        @cta="openCreate"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="rates"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column label="费率" width="120">
          <template #default="{ row }">
            <span class="rate-value">{{ formatRate(row.rate, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="币种" width="100" />
        <el-table-column prop="fee_type" label="费用类型" width="100">
          <template #default="{ row }">
            {{ feeTypeLabel(row.fee_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="rate_group" label="费率组" width="90">
          <template #default="{ row }">
            {{ rateGroupLabel(row.rate_group) }}
          </template>
        </el-table-column>
        <el-table-column prop="calc_mode" label="计算模式" width="110">
          <template #default="{ row }">
            {{ calcModeLabel(row.calc_mode) }}
          </template>
        </el-table-column>
        <el-table-column prop="case_type" label="案件类型" width="110">
          <template #default="{ row }">
            {{ caseTypeLabel(row.case_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="patent_category" label="专利类别" width="100">
          <template #default="{ row }">
            {{ patentCategoryLabel(row.patent_category) }}
          </template>
        </el-table-column>
        <el-table-column prop="country_code" label="国家/地区" width="100" />
        <el-table-column prop="allow_reduction" label="允许减缴" width="90">
          <template #default="{ row }">
            {{ row.allow_reduction ? '是' : '否' }}
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="200">
          <template #default="{ row }">
            <span v-if="row.effective_from || row.effective_to">
              {{ row.effective_from || '—' }} ~ {{ row.effective_to || '—' }}
            </span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="来源状态" width="100">
          <template #default="{ row }">
            <el-tag :type="sourceStatusTag(row.source_status)" size="small">
              {{ sourceStatusLabel(row.source_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="来源" min-width="160">
          <template #default="{ row }">
            <el-tooltip
              v-if="row.source_doc || row.source_policy || row.source_url"
              :content="sourceTooltip(row)"
              placement="top"
            >
              <span class="source-cell">{{ row.source_doc || row.source_policy || row.source_url }}</span>
            </el-tooltip>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click="openEdit(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[20, 50, 100]" />
    </div>

    <!-- Form Dialog -->
    <FeeRateForm
      v-model:visible="dialogVisible"
      :rate="editingRate"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getFeeRates } from '../../../api/fees'
import type { FeeRate } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import FeeRateForm from '../components/FeeRateForm.vue'

const rates = ref<FeeRate[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

const dialogVisible = ref(false)
const editingRate = ref<FeeRate | null>(null)

async function fetchRates() {
  loading.value = true
  error.value = null
  try {
    const result = await getFeeRates({ page: page.value, page_size: pageSize.value })
    rates.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatRate(rate: number, currency?: string): string {
  const curr = currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(rate)
}

function openCreate() {
  editingRate.value = null
  dialogVisible.value = true
}

function openEdit(rate: FeeRate) {
  editingRate.value = rate
  dialogVisible.value = true
}

function handleFormSuccess() {
  fetchRates()
}

function feeTypeLabel(v?: string | null): string {
  const map: Record<string, string> = { GOV: '官费', SERVICE: '服务费', MISC: '其他' }
  return v ? (map[v] ?? unknownLabel('费用类型')) : '—'
}

function rateGroupLabel(v?: string | null): string {
  const map: Record<string, string> = { DOMESTIC: '国内', PCT: 'PCT', ANNUITY: '年费' }
  return v ? (map[v] ?? unknownLabel('费率组')) : '—'
}

function calcModeLabel(v?: string | null): string {
  const map: Record<string, string> = {
    FIXED: '固定', PER_CLAIM: '按权利要求', PER_PAGE: '按页', TIER: '阶梯'
  }
  return v ? (map[v] ?? unknownLabel('计算模式')) : '—'
}

function caseTypeLabel(v?: string | null): string {
  const map: Record<string, string> = {
    NORMAL: '普通', PCT_INTL: 'PCT国际', PCT_NATL: 'PCT国内', PRIORITY: '优先权'
  }
  return v ? (map[v] ?? unknownLabel('案件类型')) : '—'
}

function patentCategoryLabel(v?: string | null): string {
  const map: Record<string, string> = { INV: '发明', UM: '实用新型', DES: '外观设计' }
  return v ? (map[v] ?? unknownLabel('专利类别')) : '—'
}

function unknownLabel(label: string): string {
  return `未知${label}`
}

function sourceStatusLabel(v?: string | null): string {
  const normalized = (v || '').toUpperCase()
  if (normalized === 'CONFIRMED') return '已确认'
  if (normalized === 'PENDING' || normalized === 'PENDING_CONFIRMATION') return '待确认'
  if (normalized === 'DISABLED') return '未启用'
  return '未标记'
}

function sourceStatusTag(v?: string | null): 'success' | 'warning' | 'info' {
  const normalized = (v || '').toUpperCase()
  if (normalized === 'CONFIRMED') return 'success'
  if (normalized === 'PENDING' || normalized === 'PENDING_CONFIRMATION') return 'warning'
  return 'info'
}

function sourceTooltip(row: FeeRate): string {
  const parts: string[] = []
  if (row.source_doc) parts.push(`来源文件：${row.source_doc}`)
  if (row.source_policy) parts.push(`政策依据：${row.source_policy}`)
  if (row.source_url) parts.push(`来源链接：${row.source_url}`)
  if (row.source_version) parts.push(`版本：${row.source_version}`)
  return parts.join('；') || '—'
}

watch([page, pageSize], () => {
  fetchRates()
})

onMounted(() => {
  fetchRates()
})
</script>

<style scoped>
.rate-value {
  font-family: var(--font-mono);
  font-weight: 500;
}

.source-cell {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}
</style>
