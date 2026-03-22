<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">回款列表</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="goToCreate">
          登记回款
        </el-button>
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
        title="暂无回款"
        message="回款登记后会显示在这里。"
        icon="💳"
        cta-label="登记回款"
        @cta="goToCreate"
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
        <el-table-column prop="bill_no" label="账单号" width="140">
          <template #default="{ row }">
            <router-link
              v-if="row.bill_id"
              class="bill-link"
              :to="`/billing/bills/${row.bill_id}`"
            >
              {{ row.bill_no || row.bill_id }}
            </router-link>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="预收状态" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="getPrepaymentTagType(row.prepayment_status)" size="small">
              {{ getPrepaymentStatusText(row.prepayment_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="未分配金额" width="160" align="right">
          <template #default="{ row }">
            <span class="mono-num">
              {{ formatAmount(row.unapplied_amt ?? row.amount, row.currency) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="付款方式" width="140">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ formatMethod(row.payment_method) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payment_date" label="付款日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.payment_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="reference" label="交易参考号" min-width="150">
          <template #default="{ row }">
            {{ row.reference || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150">
          <template #default="{ row }">
            {{ row.notes || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
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
import { useRouter } from 'vue-router'
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
import type {
  BillListItem,
  OffsetListItem,
  PaymentLineItem,
  PaymentListItem,
  PaymentMethod,
} from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { getPaymentMethodText } from '../../../constants/displayText'

const router = useRouter()

// Payments state
const payments = ref<PaymentListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
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
    const result = await getPayments({ page: page.value, page_size: pageSize.value })
    payments.value = result.items
    total.value = result.total
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

function formatAmount(amount: number, currency?: string): string {
  const curr = currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(amount)
}

function formatMethod(method: PaymentMethod): string {
  return getPaymentMethodText(method)
}

function getPrepaymentStatusText(status?: string): string {
  switch (status) {
    case 'FULLY_ALLOCATED':
      return '已分配完'
    case 'PARTIALLY_ALLOCATED':
      return '部分分配'
    case 'UNALLOCATED':
      return '预收中'
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
    default:
      return 'info'
  }
}

function formatPaymentOption(payment: PaymentListItem): string {
  const refText = payment.reference || payment.id
  return `${refText} | ${formatAmount(payment.amount, payment.currency)} | ${payment.client_id}`
}

function formatPaymentLineOption(line: PaymentLineItem): string {
  return `${line.id} | 余额 ${formatAmount(line.balance_amt, 'CNY')}`
}

function formatBillOption(bill: BillListItem): string {
  return `${bill.bill_no} | 余额 ${formatAmount(bill.balance, bill.currency)}`
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

function goToCreate() {
  router.push('/billing/payments/new')
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
})
</script>

<style scoped>
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
</style>
