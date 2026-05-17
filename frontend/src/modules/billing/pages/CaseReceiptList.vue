<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">个案收款登记</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="openCreateDialog">新增收款记录</el-button>
      </div>
    </div>

    <!-- Filter Bar -->
    <el-form :model="filters" inline class="filter-form" style="margin-bottom: 16px">
      <el-form-item label="客户">
        <el-select
          v-model="filters.client_id"
          placeholder="请选择客户"
          clearable
          filterable
          :loading="clientOptionsLoading"
          style="width: 180px"
          @change="onFilterChange"
        >
          <el-option
            v-for="client in clientOptions"
            :key="client.id"
            :label="formatClientOption(client)"
            :value="client.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="案号">
        <el-input v-model="filters.case_no" placeholder="案号" clearable style="width: 140px" @change="onFilterChange" />
      </el-form-item>
      <el-form-item label="费用类型">
        <el-select v-model="filters.fee_type" placeholder="全部" clearable style="width: 120px" @change="onFilterChange">
          <el-option label="官费" value="GOV" />
          <el-option label="服务费" value="SERVICE" />
          <el-option label="其他" value="MISC" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否欠款">
        <el-checkbox v-model="filters.is_arrears" @change="onFilterChange">欠款</el-checkbox>
      </el-form-item>
      <el-form-item label="是否可提成">
        <el-checkbox v-model="filters.is_commissionable" @change="onFilterChange">可提成</el-checkbox>
      </el-form-item>
      <el-form-item label="币种">
        <el-input v-model="filters.currency" placeholder="如 CNY" clearable style="width: 90px" @change="onFilterChange" />
      </el-form-item>
      <el-form-item label="收款日期">
        <el-date-picker
          v-model="filters.date_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 260px"
          @change="onFilterChange"
        />
      </el-form-item>
      <el-form-item>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- Loading State -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty" style="text-align: center; padding: 60px 0; color: var(--text-sub)">
      暂无数据
    </div>

    <!-- Table -->
    <div v-else>
      <el-table :data="receipts" stripe size="small" class="compact-table">
        <el-table-column prop="case_no" label="案号" width="140">
          <template #default="{ row }">
            {{ row.case_no || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="client_name" label="客户名称" min-width="150">
          <template #default="{ row }">
            {{ row.client_name || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="fee_code" label="费用代码" width="120">
          <template #default="{ row }">
            {{ row.fee_code || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="fee_name" label="费用名称" min-width="140">
          <template #default="{ row }">
            {{ row.fee_name || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="year_no" label="年度" width="70" align="center">
          <template #default="{ row }">
            {{ row.year_no ?? '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="fee_type" label="费用类型" width="90">
          <template #default="{ row }">
            {{ getFeeTypeLabel(row.fee_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="receivable_amt" label="应收金额" width="110" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ row.receivable_amt.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="received_amt" label="实收金额" width="110" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ row.received_amt.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="币种" width="70" align="center" />
        <el-table-column label="是否欠款" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_arrears ? 'danger' : 'success'" size="small">
              {{ row.is_arrears ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="是否预收" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_prepayment ? 'warning' : 'info'" size="small">
              {{ row.is_prepayment ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="收款日期" width="110">
          <template #default="{ row }">
            {{ row.last_receipt_date ? formatDate(row.last_receipt_date) : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="到期日" width="110">
          <template #default="{ row }">
            {{ row.due_date ? formatDate(row.due_date) : '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="invoice_no" label="发票号" width="130">
          <template #default="{ row }">
            {{ row.invoice_no || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchReceipts"
        />
      </div>
    </div>

    <!-- Dialog -->
    <CaseReceiptDialog
      v-model="dialogVisible"
      :receipt-id="editReceiptId"
      :prefill-case-id="null"
      :initial-data="editInitialData"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { listCaseReceipts } from '../../../api/billing'
import { getClients } from '../../../api/clients'
import type { CaseReceiptListItem, CaseReceiptListResponse } from '../../../api/billing.types'
import type { Client } from '../../../api/clients.types'
import CaseReceiptDialog from '../components/CaseReceiptDialog.vue'

const receipts = ref<CaseReceiptListItem[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && total.value === 0)

const dialogVisible = ref(false)
const editReceiptId = ref<string | null>(null)
const editInitialData = ref<CaseReceiptListItem | null>(null)
const clientOptions = ref<Client[]>([])
const clientOptionsLoading = ref(false)

const filters = reactive({
  client_id: '',
  case_no: '',
  fee_type: '',
  is_arrears: false,
  is_commissionable: false,
  currency: '',
  date_range: null as [string, string] | null,
})

function getFeeTypeLabel(feeType?: string | null): string {
  switch (feeType) {
    case 'GOV': return '官费'
    case 'SERVICE': return '服务费'
    case 'MISC': return '其他'
    default: return feeType || '—'
  }
}

function formatClientOption(client: Client): string {
  const code = client.client_code ? `${client.client_code} · ` : ''
  return `${code}${client.name || '未命名客户'}`
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

function onFilterChange() {
  page.value = 1
  fetchReceipts()
}

function resetFilters() {
  filters.client_id = ''
  filters.case_no = ''
  filters.fee_type = ''
  filters.is_arrears = false
  filters.is_commissionable = false
  filters.currency = ''
  filters.date_range = null
  page.value = 1
  fetchReceipts()
}

async function fetchReceipts() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.client_id) params.client_id = filters.client_id
    if (filters.case_no) params.case_no = filters.case_no
    if (filters.fee_type) params.fee_type = filters.fee_type
    if (filters.is_arrears) params.is_arrears = true
    if (filters.is_commissionable) params.is_commissionable = true
    if (filters.currency) params.currency = filters.currency
    if (filters.date_range) {
      params.date_from = filters.date_range[0]
      params.date_to = filters.date_range[1]
    }
    const result: CaseReceiptListResponse = await listCaseReceipts(params)
    receipts.value = result.items
    total.value = result.total
  } finally {
    loading.value = false
  }
}

async function loadClientOptions() {
  clientOptionsLoading.value = true
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clientOptions.value = result.items
  } finally {
    clientOptionsLoading.value = false
  }
}

function openCreateDialog() {
  editReceiptId.value = null
  editInitialData.value = null
  dialogVisible.value = true
}

function openEditDialog(row: CaseReceiptListItem) {
  editReceiptId.value = row.id
  editInitialData.value = row
  dialogVisible.value = true
}

function onSaved() {
  fetchReceipts()
}

watch([page, pageSize], () => {
  fetchReceipts()
})

onMounted(() => {
  fetchReceipts()
  loadClientOptions()
})
</script>

<style scoped>
.mono-num {
  font-family: var(--font-mono, monospace);
}
</style>
