<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">官费清单</h1>
        <span class="page-count">{{ pageCountText }}</span>
      </div>
      <div class="page-header-right">
        <el-button @click="handleRefresh">刷新</el-button>
        <el-button type="primary" @click="toggleHistoricalForm">
          {{ showHistoricalForm ? '收起历史清单入口' : '新建历史清单' }}
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-card class="form-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="form-card-title">清单查询</span>
        </div>
      </template>

      <el-form label-position="top" class="pay-list-form">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :lg="6">
            <el-form-item label="清单编号">
              <el-input
                v-model.trim="searchForm.pay_list_no"
                placeholder="请输入清单编号"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :lg="6">
            <el-form-item label="客户编号">
              <el-select
                v-model="searchForm.client_id"
                filterable
                clearable
                :loading="clientOptionsLoading"
                placeholder="请选择客户"
                style="width: 100%"
              >
                <el-option
                  v-for="client in clientOptions"
                  :key="client.id"
                  :label="formatClientOption(client)"
                  :value="String(client.id)"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :lg="6">
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" placeholder="全部" clearable style="width: 100%">
                <el-option
                  v-for="option in statusOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :lg="6">
            <el-form-item label="币种">
              <el-input
                v-model.trim="searchForm.currency"
                placeholder="请输入币种代码"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :lg="6">
            <el-form-item label="计划缴费日期起">
              <el-date-picker
                v-model="searchForm.planned_pay_date_from"
                type="date"
                placeholder="起始日期"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :lg="6">
            <el-form-item label="计划缴费日期止">
              <el-date-picker
                v-model="searchForm.planned_pay_date_to"
                type="date"
                placeholder="截止日期"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button @click="handleReset">重置</el-button>
          <el-button type="primary" :loading="loading" @click="handleSearch">查询</el-button>
        </div>
      </el-form>
    </el-card>

    <el-card v-if="showHistoricalForm" class="form-card historical-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="form-card-title">历史清单入口</span>
        </div>
      </template>

      <el-form
        ref="historicalFormRef"
        :model="historicalForm"
        :rules="historicalRules"
        label-position="top"
        class="pay-list-form"
      >
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12">
            <el-form-item label="客户编号" prop="client_id" :error="fieldErrors.get('client_id')?.join('，')">
              <el-select
                v-model="historicalForm.client_id"
                filterable
                clearable
                :loading="clientOptionsLoading"
                placeholder="请选择客户"
                style="width: 100%"
              >
                <el-option
                  v-for="client in clientOptions"
                  :key="client.id"
                  :label="formatClientOption(client)"
                  :value="String(client.id)"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="币种" prop="currency" :error="fieldErrors.get('currency')?.join('，')">
              <el-input
                v-model.trim="historicalForm.currency"
                placeholder="例如 CNY"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="计划缴费日期" prop="planned_pay_date" :error="fieldErrors.get('planned_pay_date')?.join('，')">
              <el-date-picker
                v-model="historicalForm.planned_pay_date"
                type="date"
                placeholder="可选"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="备注" prop="remark" :error="fieldErrors.get('remark')?.join('，')">
              <el-input
                v-model.trim="historicalForm.remark"
                placeholder="可填写说明（可选）"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button @click="resetHistoricalForm">重置</el-button>
          <el-button type="primary" :loading="creatingHistorical" @click="handleCreateHistorical">
            提交历史清单
          </el-button>
        </div>
      </el-form>
    </el-card>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else-if="isEmpty" class="page-empty">
      <el-empty description="暂无官费清单" />
    </div>

    <div v-else class="page-table">
      <el-table :data="payLists" stripe size="small" class="compact-table">
        <el-table-column label="清单编号" min-width="160">
          <template #default="{ row }">
            {{ row.pay_list_no || `#${row.id}` }}
          </template>
        </el-table-column>
        <el-table-column label="客户" min-width="160">
          <template #default="{ row }">
            {{ row.client_name || row.client_id || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="币种" width="100" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="payListStatusTag(row.status)">
              {{ payListStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="计划缴费日期" width="130">
          <template #default="{ row }">
            {{ row.planned_pay_date || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="实际缴费日期" width="130">
          <template #default="{ row }">
            {{ row.paid_date || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="清单金额" min-width="140" align="right">
          <template #default="{ row }">
            {{ formatMoney(row.total_amount, row.currency) }}
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="180">
          <template #default="{ row }">
            {{ row.remark || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="goToDetail(row)">
              详情
            </el-button>
            <el-button
              text
              type="success"
              :disabled="!canExport(row)"
              :loading="exportingId === row.id"
              @click="handleExport(row)"
            >
              导出
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import {
  createHistoricalPayList,
  exportPayList,
  listPayLists,
  mapGovPaymentsError,
} from '../../../api/govPayments'
import type {
  GovPaymentsApiError,
  HistoricalPayListCreatePayload,
  PayListInfo,
  PayListListItem,
} from '../../../api/govPayments.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const router = useRouter()

interface PayListSearchForm {
  pay_list_no: string
  client_id: string
  status: string
  currency: string
  planned_pay_date_from: string
  planned_pay_date_to: string
}

interface HistoricalPayListForm {
  client_id: string
  currency: string
  planned_pay_date: string
  remark: string
}

const defaultSearchForm: PayListSearchForm = {
  pay_list_no: '',
  client_id: '',
  status: '',
  currency: '',
  planned_pay_date_from: '',
  planned_pay_date_to: '',
}

const defaultHistoricalForm: HistoricalPayListForm = {
  client_id: '',
  currency: 'CNY',
  planned_pay_date: '',
  remark: '',
}

const statusOptions = [
  { label: '草稿', value: 'DRAFT' },
  { label: '已导出', value: 'EXPORTED' },
  { label: '已缴费', value: 'PAID' },
  { label: '已取消', value: 'CANCELLED' },
  { label: '部分完成', value: 'PARTIAL' },
]

const payLists = ref<PayListListItem[]>([])
const loading = ref(false)
const error = ref<GovPaymentsApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const exportingId = ref<number | null>(null)
const creatingHistorical = ref(false)
const showHistoricalForm = ref(false)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const historicalFormRef = ref<FormInstance>()
const clientOptionsLoading = ref(false)
const clientOptions = ref<Client[]>([])

const searchForm = reactive<PayListSearchForm>({ ...defaultSearchForm })
const historicalForm = reactive<HistoricalPayListForm>({ ...defaultHistoricalForm })

const historicalRules: FormRules<HistoricalPayListForm> = {
  client_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
  currency: [{ required: true, message: '币种为必填项', trigger: 'blur' }],
}

const isEmpty = computed(() => !loading.value && !error.value && payLists.value.length === 0)

const pageCountText = computed(() => `共 ${total.value} 条`)

function normalizeText(value: string): string | undefined {
  const trimmed = value.trim()
  return trimmed || undefined
}

function normalizeStatus(value: string): string | undefined {
  const trimmed = value.trim().toUpperCase()
  return trimmed || undefined
}

function normalizeCurrency(value: string): string | undefined {
  const trimmed = value.trim().toUpperCase()
  return trimmed || undefined
}

function payListStatusText(status?: string): string {
  switch ((status || '').toUpperCase()) {
    case 'DRAFT':
      return '草稿'
    case 'EXPORTED':
      return '已导出'
    case 'PAID':
      return '已缴费'
    case 'CANCELLED':
      return '已取消'
    case 'PARTIAL':
      return '部分完成'
    default:
      return status || '未知'
  }
}

function payListStatusTag(status?: string): 'info' | 'warning' | 'success' | 'danger' {
  switch ((status || '').toUpperCase()) {
    case 'PAID':
      return 'success'
    case 'EXPORTED':
      return 'warning'
    case 'CANCELLED':
      return 'danger'
    case 'PARTIAL':
      return 'info'
    default:
      return 'info'
  }
}

function formatMoney(amount: number, currency: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(amount || 0)
}

function formatDateTime(dateValue?: string): string {
  if (!dateValue) return '—'
  const parsed = dayjs(dateValue)
  return parsed.isValid() ? parsed.format('YYYY-MM-DD HH:mm') : dateValue
}

function formatClientOption(client: Client): string {
  const code = client.client_code ? `${client.client_code} · ` : ''
  const name = client.name || client.name_cn || client.name_en || `客户 ${client.id}`
  return `${code}${name}`
}

async function fetchClientOptions() {
  clientOptionsLoading.value = true
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clientOptions.value = result.items
  } catch (err) {
    error.value = mapGovPaymentsError(err)
  } finally {
    clientOptionsLoading.value = false
  }
}

function toggleHistoricalForm() {
  showHistoricalForm.value = !showHistoricalForm.value
}

function resetHistoricalForm() {
  Object.assign(historicalForm, defaultHistoricalForm)
  fieldErrors.value = new Map()
  error.value = null
  historicalFormRef.value?.clearValidate()
}

function buildQueryParams() {
  return {
    pay_list_no: normalizeText(searchForm.pay_list_no),
    client_id: normalizeText(searchForm.client_id),
    status: normalizeStatus(searchForm.status),
    currency: normalizeCurrency(searchForm.currency),
    planned_pay_date_from: normalizeText(searchForm.planned_pay_date_from),
    planned_pay_date_to: normalizeText(searchForm.planned_pay_date_to),
    page: page.value,
    page_size: pageSize.value,
  }
}

async function loadPayLists() {
  loading.value = true
  error.value = null
  try {
    const response = await listPayLists(buildQueryParams())
    payLists.value = response.items
    total.value = response.total
    page.value = response.page
    pageSize.value = response.page_size
  } catch (err) {
    error.value = mapGovPaymentsError(err)
  } finally {
    loading.value = false
  }
}

async function handleSearch() {
  page.value = 1
  await loadPayLists()
}

async function handleReset() {
  Object.assign(searchForm, defaultSearchForm)
  page.value = 1
  await loadPayLists()
}

async function handlePageChange(nextPage: number) {
  page.value = nextPage
  await loadPayLists()
}

async function handleSizeChange(nextPageSize: number) {
  pageSize.value = nextPageSize
  page.value = 1
  await loadPayLists()
}

function downloadBlob(blob: Blob, fileName: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

function buildExportFileName(row: PayListListItem): string {
  const displayNo = row.pay_list_no || `清单-${row.id}`
  return `官费清单-${displayNo}.xlsx`
}

function canExport(row: PayListListItem): boolean {
  return (row.status || '').toUpperCase() === 'DRAFT'
}

function goToDetail(row: PayListListItem) {
  router.push(`/fee-management/pay-lists/${row.id}`)
}

async function handleExport(row: PayListListItem) {
  if (!canExport(row)) {
    ElMessage.warning('只有草稿状态的官费清单可以导出。')
    return
  }
  exportingId.value = row.id
  error.value = null
  try {
    const blob = await exportPayList(row.id)
    downloadBlob(blob, buildExportFileName(row))
    ElMessage.success('官费清单已开始导出。')
    await loadPayLists()
  } catch (err) {
    error.value = mapGovPaymentsError(err)
  } finally {
    exportingId.value = null
  }
}

function buildHistoricalPayload(): HistoricalPayListCreatePayload {
  return {
    client_id: historicalForm.client_id.trim(),
    currency: historicalForm.currency.trim().toUpperCase(),
    planned_pay_date: historicalForm.planned_pay_date || undefined,
    remark: historicalForm.remark.trim() || undefined,
  }
}

async function handleCreateHistorical() {
  fieldErrors.value = new Map()
  const valid = await historicalFormRef.value?.validate().catch(() => false)
  if (!valid) return

  creatingHistorical.value = true
  error.value = null
  try {
    const created: PayListInfo = await createHistoricalPayList(buildHistoricalPayload())
    ElMessage.success(`历史清单已创建：${created.pay_list_no || `#${created.id}`}`)
    showHistoricalForm.value = false
    resetHistoricalForm()
    await loadPayLists()
  } catch (err) {
    const mapped = mapGovPaymentsError(err)
    error.value = mapped
    if (mapped.field_errors && mapped.field_errors.size > 0) {
      fieldErrors.value = mapped.field_errors
    }
  } finally {
    creatingHistorical.value = false
  }
}

function handleRefresh() {
  void loadPayLists()
}

onMounted(() => {
  void fetchClientOptions()
  void loadPayLists()
})
</script>

<style scoped>
.pay-list-form {
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.historical-card {
  margin-top: 16px;
}

.loading-state {
  padding: 16px 0 8px;
}

.page-table {
  margin-top: 16px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
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
  .form-actions {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-header-right :deep(.el-button),
  .form-actions :deep(.el-button) {
    flex: 1;
    min-width: 120px;
  }

  .pagination-bar {
    justify-content: flex-start;
    overflow-x: auto;
  }
}
</style>
