<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">预收款管理报表</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/billing/payments/new">
          <el-button type="primary">新增回款</el-button>
        </router-link>
      </div>
    </div>

    <div class="report-summary">
      <div class="summary-card">
        <div class="card-label">预收款笔数</div>
        <div class="card-value">{{ summary.prepayment_count }} 笔</div>
      </div>
      <div class="summary-card">
        <div class="card-label">预收总额</div>
        <div class="card-value mono-num">{{ formatAmount(summary.prepayment_total_amount, summaryCurrency) }}</div>
      </div>
      <div class="summary-card">
        <div class="card-label">已核销金额</div>
        <div class="card-value mono-num">{{ formatAmount(summary.allocated_total_amount, summaryCurrency) }}</div>
      </div>
      <div class="summary-card">
        <div class="card-label">剩余预收余额</div>
        <div class="card-value mono-num">{{ formatAmount(summary.remaining_prepayment_balance, summaryCurrency) }}</div>
      </div>
    </div>

    <el-form :model="filters" inline class="filter-form">
      <el-form-item label="客户ID">
        <el-select
          v-model="filters.client_id"
          clearable
          filterable
          :loading="clientOptionsLoading"
          class="filter-input"
          placeholder="请选择客户"
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
      <el-form-item label="预收状态">
        <el-select
          v-model="filters.prepayment_status"
          clearable
          class="filter-select"
          placeholder="全部"
          @change="onFilterChange"
        >
          <el-option label="全部" value="" />
          <el-option label="未核销" value="UNALLOCATED" />
          <el-option label="部分核销" value="PARTIALLY_ALLOCATED" />
          <el-option label="已核销" value="FULLY_ALLOCATED" />
        </el-select>
      </el-form-item>
      <el-form-item label="收款日期">
        <el-date-picker
          v-model="filters.pay_date_range"
          class="filter-range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="onFilterChange"
        />
      </el-form-item>
      <el-form-item label="剩余预收">
        <el-checkbox v-model="filters.has_unapplied_only" @change="onFilterChange">
          仅显示有剩余预收余额
        </el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <LoadingBlock v-if="loading" :rows="10" />

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无预收款记录"
        message="当前筛选条件下没有符合条件的预收款。"
        icon="📭"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="payments"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="pay_no" label="收款编号" width="160">
          <template #default="{ row }">
            <span class="mono-num">{{ formatPaymentNo(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="client_name" label="客户" min-width="180">
          <template #default="{ row }">
            {{ row.client_name || row.client_id || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="收款日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.payment_date) }}
          </template>
        </el-table-column>
        <el-table-column label="预收总额" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已核销金额" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num">
              {{ formatAmount(row.allocated_amt ?? 0, row.currency) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="剩余预收余额" width="150" align="right">
          <template #default="{ row }">
            <span class="mono-num">
              {{ formatAmount(row.unapplied_amt ?? 0, row.currency) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="预收状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getPrepaymentTagType(row.prepayment_status)" size="small">
              {{ getPrepaymentStatusText(row.prepayment_status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" />
    </div>

    <!-- Offsets Section -->
    <div class="section-divider">
      <h2 class="section-title">核销记录</h2>
      <el-button size="small" @click="openOffsetDialog">创建核销</el-button>
    </div>

    <div class="offset-note">
      当前后端暂不提供完整核销列表筛选能力，现阶段支持创建与冲销。
    </div>

    <div v-if="offsetsLoading" class="page-loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="offsets.length === 0" class="offsets-empty">
      <p>暂无核销记录。</p>
    </div>

    <div v-else class="page-table">
      <el-table :data="offsets" stripe size="small" class="compact-table">
        <el-table-column prop="payment_line_id" label="付款分录" width="220">
          <template #default="{ row }">
            <span class="mono-num">{{ row.payment_line_id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="bill_id" label="账单" width="180">
          <template #default="{ row }">
            <router-link class="bill-link" :to="`/billing/bills/${row.bill_id}`">
              {{ row.bill_id }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_reversed" type="danger" size="small">已冲销</el-tag>
            <el-tag v-else type="success" size="small">生效中</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_reversed"
              type="warning"
              text
              size="small"
              @click="handleReverseOffset(row)"
            >
              冲销
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Offset Create Dialog -->
    <el-dialog
      v-model="showOffsetDialog"
      title="创建核销"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      @open="handleOffsetDialogOpen"
      @close="resetOffsetForm"
      @closed="restoreOffsetTriggerFocus"
    >
      <div v-if="offsetError" class="dialog-error">
        <ApiErrorBanner :error="offsetError" @dismiss="offsetError = null" />
      </div>

      <div v-if="offsetOptionsLoading" class="dialog-loading">
        <el-skeleton :rows="4" animated />
      </div>

      <el-form
        v-else
        ref="offsetFormRef"
        :model="offsetForm"
        :rules="offsetRules"
        label-position="top"
      >
        <el-form-item label="付款记录" prop="payment_id" :error="offsetFieldErrors.get('payment_id')?.join(', ')">
          <el-select
            v-model="offsetForm.payment_id"
            class="full-width"
            filterable
            placeholder="请选择付款记录"
          >
            <el-option
              v-for="payment in offsetPaymentOptions"
              :key="payment.id"
              :label="formatPaymentOption(payment)"
              :value="payment.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="付款分录" prop="payment_line_id" :error="offsetFieldErrors.get('payment_line_id')?.join(', ')">
          <el-select
            v-model="offsetForm.payment_line_id"
            class="full-width"
            filterable
            :loading="paymentLinesLoading"
            :disabled="!offsetForm.payment_id"
            placeholder="请选择付款分录"
          >
            <el-option
              v-for="line in paymentLines"
              :key="line.id"
              :label="formatPaymentLineOption(line)"
              :value="line.id"
            />
          </el-select>
          <div class="field-hint">仅展示所选付款记录下的分录。</div>
        </el-form-item>

        <el-form-item label="账单编号" prop="bill_id" :error="offsetFieldErrors.get('bill_id')?.join(', ')">
          <el-select
            v-model="offsetForm.bill_id"
            class="full-width"
            filterable
            placeholder="请选择账单"
          >
            <el-option
              v-for="bill in offsetBillCandidates"
              :key="bill.id"
              :label="formatBillOption(bill)"
              :value="bill.id"
            />
          </el-select>
          <div class="field-hint">如可识别客户，将优先筛选同客户账单。</div>
        </el-form-item>

        <el-form-item label="核销金额" prop="offset_amt" :error="offsetFieldErrors.get('offset_amt')?.join(', ')">
          <el-input-number
            v-model="offsetForm.offset_amt"
            :min="0"
            :precision="2"
            class="full-width"
          />
        </el-form-item>

      </el-form>

      <template #footer>
        <el-button @click="showOffsetDialog = false">取消</el-button>
        <el-button type="primary" :loading="offsetSaving" @click="handleCreateOffset">
          创建核销
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createOffset,
  getBills,
  getOffsets,
  getPaymentLines,
  getPayments,
  reverseOffset,
} from '../../../api/billing'
import { getClients } from '../../../api/clients'
import type {
  BillListItem,
  OffsetListItem,
  PaymentLineItem,
  PaymentListItem,
  PaymentListResponse,
} from '../../../api/billing.types'
import type { Client } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const payments = ref<PaymentListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const summary = ref<Pick<
  PaymentListResponse,
  | 'prepayment_count'
  | 'prepayment_total_amount'
  | 'allocated_total_amount'
  | 'remaining_prepayment_balance'
>>({
  prepayment_count: 0,
  prepayment_total_amount: 0,
  allocated_total_amount: 0,
  remaining_prepayment_balance: 0,
})
const filters = reactive({
  client_id: '',
  prepayment_status: '',
  pay_date_range: null as [string, string] | null,
  has_unapplied_only: false,
})
const clientOptionsLoading = ref(false)
const clientOptions = ref<Client[]>([])
const summaryCurrency = computed(() => payments.value[0]?.currency || 'CNY')
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

// Offsets state
const offsets = ref<OffsetListItem[]>([])
const offsetsLoading = ref(false)

// Offset dialog state
const showOffsetDialog = ref(false)
const offsetSaving = ref(false)
const offsetError = ref<ApiError | null>(null)
const offsetFormRef = ref<FormInstance>()
const offsetFieldErrors = ref<Map<string, string[]>>(new Map())
const lastFocusedElement = ref<HTMLElement | null>(null)
const offsetOptionsLoading = ref(false)
const paymentLinesLoading = ref(false)
const offsetPaymentOptions = ref<PaymentListItem[]>([])
const offsetBillOptions = ref<BillListItem[]>([])
const paymentLines = ref<PaymentLineItem[]>([])

const offsetForm = reactive({
  payment_id: '',
  payment_line_id: '',
  bill_id: '',
  offset_amt: 0,
  offset_date: new Date().toISOString().split('T')[0],
})

const offsetRules: FormRules = {
  payment_id: [
    { required: true, message: '付款记录为必填项', trigger: 'change' },
  ],
  payment_line_id: [
    { required: true, message: '付款分录为必填项', trigger: 'change' },
  ],
  bill_id: [
    { required: true, message: '账单编号为必填项', trigger: 'change' },
  ],
  offset_amt: [
    { required: true, message: '核销金额为必填项', trigger: 'blur' },
  ],
}

const selectedOffsetPayment = computed(() =>
  offsetPaymentOptions.value.find((item) => item.id === offsetForm.payment_id) || null
)

const offsetBillCandidates = computed(() => {
  const clientId = selectedOffsetPayment.value?.client_id
  if (!clientId) {
    return offsetBillOptions.value
  }
  return offsetBillOptions.value.filter((bill) => bill.client_id === clientId)
})

async function fetchPayments() {
  loading.value = true
  error.value = null
  try {
    const [payDateFrom, payDateTo] = filters.pay_date_range || []
    const result = await getPayments({
      page: page.value,
      page_size: pageSize.value,
      client_id: filters.client_id.trim() || undefined,
      prepayment_status: filters.prepayment_status || undefined,
      pay_date_from: payDateFrom,
      pay_date_to: payDateTo,
      has_unapplied_only: filters.has_unapplied_only ? true : undefined,
    })
    payments.value = result.items
    total.value = result.total
    summary.value = {
      prepayment_count: result.prepayment_count,
      prepayment_total_amount: result.prepayment_total_amount,
      allocated_total_amount: result.allocated_total_amount,
      remaining_prepayment_balance: result.remaining_prepayment_balance,
    }
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function fetchOffsets() {
  offsetsLoading.value = true
  try {
    const result = await getOffsets({ page: 1, page_size: 100 })
    offsets.value = result.items
  } catch (err) {
    // Silently handle offsets error
    console.error('获取核销记录失败:', err)
  } finally {
    offsetsLoading.value = false
  }
}

async function fetchClientOptions() {
  clientOptionsLoading.value = true
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clientOptions.value = result.items
  } catch (err) {
    error.value = err as ApiError
  } finally {
    clientOptionsLoading.value = false
  }
}

function onFilterChange() {
  const alreadyOnFirstPage = page.value === 1
  page.value = 1
  if (alreadyOnFirstPage) {
    fetchPayments()
  }
}

function resetFilters() {
  filters.client_id = ''
  filters.prepayment_status = ''
  filters.pay_date_range = null
  filters.has_unapplied_only = false
  const alreadyOnFirstPage = page.value === 1
  page.value = 1
  if (alreadyOnFirstPage) {
    fetchPayments()
  }
}

function formatAmount(amount: number, currency?: string): string {
  const curr = currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(amount)
}

function getPrepaymentStatusText(status?: string): string {
  switch (status) {
    case 'FULLY_ALLOCATED':
      return '已核销'
    case 'PARTIALLY_ALLOCATED':
      return '部分核销'
    case 'UNALLOCATED':
      return '未核销'
    default:
      return '待确认'
  }
}

function getPrepaymentTagType(status?: string): 'success' | 'warning' | 'info' {
  switch (status) {
    case 'FULLY_ALLOCATED':
      return 'success'
    case 'PARTIALLY_ALLOCATED':
      return 'warning'
    case 'UNALLOCATED':
      return 'info'
    default:
      return 'info'
  }
}

function formatPaymentNo(payment: PaymentListItem): string {
  return payment.reference || payment.id
}

function formatClientOption(client: Client): string {
  const code = client.client_code ? `${client.client_code} · ` : ''
  return `${code}${client.name || client.id}`
}

function formatPaymentOption(payment: PaymentListItem): string {
  const refText = formatPaymentNo(payment)
  const clientText = payment.client_name || payment.client_id
  return `${refText} | ${clientText} | ${formatAmount(payment.amount, payment.currency)}`
}

function formatPaymentLineOption(line: PaymentLineItem): string {
  return `${line.id} | 余额 ${formatAmount(line.balance_amt, 'CNY')}`
}

function formatBillOption(bill: BillListItem): string {
  return `${bill.bill_no} | 余额 ${formatAmount(bill.balance, bill.currency)}`
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

function resetOffsetForm() {
  offsetForm.payment_id = ''
  offsetForm.payment_line_id = ''
  offsetForm.bill_id = ''
  offsetForm.offset_amt = 0
  offsetForm.offset_date = new Date().toISOString().split('T')[0]
  offsetError.value = null
  offsetFieldErrors.value = new Map()
  paymentLines.value = []
}

function openOffsetDialog() {
  lastFocusedElement.value = document.activeElement instanceof HTMLElement
    ? document.activeElement
    : null
  showOffsetDialog.value = true
}

async function handleOffsetDialogOpen() {
  await loadOffsetDialogOptions()
}

function restoreOffsetTriggerFocus() {
  lastFocusedElement.value?.focus()
  lastFocusedElement.value = null
}

async function handleCreateOffset() {
  offsetFieldErrors.value = new Map()

  const valid = await offsetFormRef.value?.validate().catch(() => false)
  if (!valid) return

  offsetSaving.value = true
  offsetError.value = null

  try {
    await createOffset({
      payment_line_id: offsetForm.payment_line_id,
      bill_id: offsetForm.bill_id,
      offset_amt: offsetForm.offset_amt,
      offset_date: offsetForm.offset_date || undefined,
    })

    ElMessage.success('核销创建成功')
    showOffsetDialog.value = false
    resetOffsetForm()
    fetchOffsets()
  } catch (err) {
    const apiError = err as ApiError
    offsetError.value = apiError

    if (apiError.status === 422 && apiError.details) {
      offsetFieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    offsetSaving.value = false
  }
}

async function loadOffsetDialogOptions() {
  offsetOptionsLoading.value = true
  offsetError.value = null

  try {
    const [paymentResult, billResult] = await Promise.all([
      getPayments({ page: 1, page_size: 100 }),
      getBills({ page: 1, page_size: 100 }),
    ])
    offsetPaymentOptions.value = paymentResult.items
    offsetBillOptions.value = billResult.items
  } catch (err) {
    offsetError.value = err as ApiError
  } finally {
    offsetOptionsLoading.value = false
  }
}

async function loadPaymentLinesForSelectedPayment() {
  if (!offsetForm.payment_id) {
    paymentLines.value = []
    offsetForm.payment_line_id = ''
    return
  }

  paymentLinesLoading.value = true
  offsetFieldErrors.value.delete('payment_line_id')

  try {
    paymentLines.value = await getPaymentLines(offsetForm.payment_id)

    const firstAvailableLine = paymentLines.value.find((line) => line.balance_amt > 0) || paymentLines.value[0]
    if (firstAvailableLine) {
      offsetForm.payment_line_id = firstAvailableLine.id
      if (!offsetForm.offset_amt || offsetForm.offset_amt <= 0) {
        offsetForm.offset_amt = Number(firstAvailableLine.balance_amt.toFixed(2))
      }
    } else {
      offsetForm.payment_line_id = ''
    }
  } catch (err) {
    paymentLines.value = []
    offsetForm.payment_line_id = ''
    offsetError.value = err as ApiError
  } finally {
    paymentLinesLoading.value = false
  }
}

async function handleReverseOffset(offset: OffsetListItem) {
  try {
    await ElMessageBox.confirm(
      '确定要冲销这条核销记录吗？此操作不可撤销。',
      '确认冲销',
      {
        confirmButtonText: '确认冲销',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await reverseOffset(offset.id)
    ElMessage.success('核销冲销成功')
    fetchOffsets()
  } catch (err) {
    if (err !== 'cancel') {
      error.value = err as ApiError
    }
  }
}

watch([page, pageSize], () => {
  fetchPayments()
})

watch(
  () => offsetForm.payment_id,
  async () => {
    offsetForm.payment_line_id = ''
    await loadPaymentLinesForSelectedPayment()

    const preferredBill = offsetBillCandidates.value.find((bill) => bill.balance > 0) || offsetBillCandidates.value[0]
    if (preferredBill) {
      offsetForm.bill_id = preferredBill.id
    }
  }
)

onMounted(() => {
  fetchPayments()
  fetchOffsets()
  fetchClientOptions()
})
</script>

<style scoped>
.report-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  background: var(--el-bg-color);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-label {
  font-size: 12px;
  color: var(--text-sub);
}

.card-value {
  font-size: 20px;
  font-weight: 600;
}

.filter-form {
  margin-bottom: 16px;
}

.filter-input {
  width: 180px;
}

.filter-select {
  width: 150px;
}

.filter-range {
  width: 280px;
}

.bill-link {
  color: var(--color-primary);
  font-family: var(--font-mono);
  text-decoration: none;
}

.bill-link:hover {
  text-decoration: underline;
}

.mono-num {
  font-family: var(--font-mono);
}

.section-divider {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 32px;
  margin-bottom: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.offset-note {
  margin: 0 0 12px 0;
  color: var(--text-sub);
  font-size: 12px;
}

.offsets-empty {
  text-align: center;
  padding: 24px;
  color: var(--text-sub);
}

.full-width {
  width: 100%;
}

.dialog-error {
  margin-bottom: 16px;
}

.dialog-loading {
  margin-bottom: 12px;
}

.field-hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-sub);
}

@media (max-width: 1200px) {
  .report-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .report-summary {
    grid-template-columns: 1fr;
  }

  .filter-input,
  .filter-select,
  .filter-range {
    width: 100%;
  }
}
</style>
