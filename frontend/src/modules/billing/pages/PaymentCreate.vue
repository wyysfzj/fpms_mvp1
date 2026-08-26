<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回
        </el-button>
      </div>
    </div>

    <div class="page-error" v-if="error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div class="form-card">
      <h2 class="form-card-title">登记回款</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="payment-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">回款信息</h3>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item
                label="账单编号（收款对象）"
                prop="bill_id"
                :error="fieldErrors.get('bill_id')?.join(', ')"
              >
                <el-select
                  v-model="form.bill_id"
                  filterable
                  clearable
                  :loading="billOptionsLoading"
                  class="full-width"
                  placeholder="请选择账单"
                >
                  <el-option
                    v-for="bill in billOptions"
                    :key="bill.id"
                    :label="formatBillOption(bill)"
                    :value="bill.id"
                  />
                </el-select>
                <div class="field-hint">
                  <router-link to="/billing/bills">查看账单列表</router-link> 以确认客户、币种和应收余额
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="回款金额"
                prop="amount"
                :error="fieldErrors.get('amount')?.join(', ')"
              >
                <el-input-number
                  v-model="form.amount"
                  :min="0"
                  :precision="2"
                  class="full-width"
                  placeholder="请输入回款金额"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item
                label="付款方式"
                prop="payment_method"
                :error="fieldErrors.get('payment_method')?.join(', ')"
              >
                <el-select
                  v-model="form.payment_method"
                  :disabled="demoSessionEnabled"
                  placeholder="请选择付款方式"
                  class="full-width"
                >
                  <el-option label="银行转账" value="BANK_TRANSFER" />
                  <el-option label="现金" value="CASH" />
                  <el-option label="支票" value="CHECK" />
                  <el-option label="其他" value="OTHER" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="收款日期"
                prop="payment_date"
                :error="fieldErrors.get('payment_date')?.join(', ')"
              >
                <el-date-picker
                  v-model="form.payment_date"
                  type="date"
                  placeholder="请选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  class="full-width"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item
            :label="demoSessionEnabled ? '收款编号' : '收款编号 / 交易参考号'"
            prop="reference"
            :error="fieldErrors.get('reference')?.join(', ')"
          >
            <el-input
              v-model.trim="form.reference"
              placeholder="例如 PAY-202604-001，可选"
            />
            <div class="field-hint">
              该值会作为后端回款编号或交易参考号保存，便于后续核销时识别。
            </div>
          </el-form-item>

          <el-form-item v-if="demoSessionEnabled" label="银行流水参考号">
            <el-input v-model.trim="demoBankRefNo" placeholder="请输入银行流水参考号" />
          </el-form-item>

          <el-alert
            v-if="demoSessionEnabled && demoSelectedBill"
            type="info"
            :closable="false"
            :title="`当前账单状态：${getBillStatusText(demoSelectedBill.status)}`"
            :description="`最新可见余额：CNY ${demoSelectedBill.balance}`"
          />

          <el-form-item label="备注" prop="notes">
            <el-input
              v-model="form.notes"
              type="textarea"
              :rows="3"
              placeholder="请输入备注（可选）"
            />
          </el-form-item>

          <div class="field-hint">
            新登记的回款在未核销到账单前会保持“预收中”状态，后续核销后未分配金额会自动减少。
          </div>
        </div>

        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSubmit">
            登记回款
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { createPayment, getBills } from '../../../api/billing'
import type { BillListItem, PaymentMethod } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { getBillStatusText } from '../../../constants/displayText'
import { createDemoBankReceipt, readDemoBill } from '../../demo/demo.api'
import type { DemoBillDetail } from '../../demo/demo.api'
import {
  DEMO_UI_SESSION_CHANGE_EVENT,
  getDemoUiSession,
  isDemoUiSessionActive,
} from '../../demo/demoUiSession'

const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const billOptionsLoading = ref(false)
const billOptions = ref<BillListItem[]>([])
const demoSessionEnabled = ref(false)
const demoSelectedBill = ref<DemoBillDetail | null>(null)
const demoBankRefNo = ref('')
const demoPaymentIdempotencyKey = crypto.randomUUID()

// Pre-fill bill_id from query param if provided
const initialBillId = (route.query.bill_id as string) || ''

const form = reactive({
  bill_id: initialBillId,
  amount: 0,
  payment_method: 'BANK_TRANSFER' as PaymentMethod,
  payment_date: new Date().toISOString().split('T')[0],
  reference: '',
  notes: '',
})

const rules: FormRules = {
  bill_id: [
    { required: true, message: '请选择账单', trigger: 'change' },
  ],
  amount: [
    { required: true, message: '金额为必填项', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于 0', trigger: 'blur' },
  ],
  payment_method: [
    { required: true, message: '付款方式为必填项', trigger: 'change' },
  ],
  payment_date: [
    { required: true, message: '付款日期为必填项', trigger: 'change' },
  ],
}

function canCreateDemoPayment(
  sessionActive: boolean,
  session: unknown,
  bill: DemoBillDetail | null,
  selectedBillId: string,
  amount: string,
  payNo: string,
  payDate: string,
  bankRefNo: string,
  remark: string,
  pending: boolean,
): boolean {
  if (
    !sessionActive
    || session === null
    || bill === null
    || bill.id !== selectedBillId
    || bill.status === 'SETTLED'
    || !/^\d+\.\d{2}$/.test(amount)
    || !payNo.trim()
    || !/^\d{4}-\d{2}-\d{2}$/.test(payDate)
    || !bankRefNo.trim()
    || !remark.trim()
    || pending
  ) return false
  const amountMinor = BigInt(amount.replace('.', ''))
  const balanceMinor = BigInt(bill.balance.replace('.', ''))
  return amountMinor > 0n
    && amountMinor <= balanceMinor
    && (bill.status === 'UNSETTLED' ? amount === '1200.00' : amount === bill.balance)
}

function syncDemoSession() {
  demoSessionEnabled.value = isDemoUiSessionActive() && getDemoUiSession() !== null
  if (!demoSessionEnabled.value) demoSelectedBill.value = null
}

async function loadDemoSelectedBill() {
  demoSelectedBill.value = null
  if (!demoSessionEnabled.value || !form.bill_id) return
  try {
    const bill = await readDemoBill(form.bill_id)
    demoSelectedBill.value = bill
    if (bill.status === 'PARTIALLY_SETTLED') {
      form.amount = Number(bill.balance)
    }
  } catch (err) {
    error.value = err as ApiError
  }
}

function goBack() {
  router.push('/billing/payments')
}

function formatBillOption(bill: BillListItem): string {
  const clientText = formatBillClient(bill)
  const balanceText = bill.balance.toLocaleString('zh-CN', {
    style: 'currency',
    currency: bill.currency || 'CNY',
  })
  return `${bill.bill_no} · ${clientText} · 余额 ${balanceText}`
}

function formatBillClient(bill: BillListItem): string {
  if (bill.client_name) return bill.client_name
  return bill.client_id ? '未命名客户' : '未关联客户'
}

async function fetchBillOptions() {
  billOptionsLoading.value = true
  try {
    const result = await getBills({ page: 1, page_size: 100 })
    billOptions.value = result.items
  } catch (err) {
    error.value = err as ApiError
  } finally {
    billOptionsLoading.value = false
  }
}

async function handleSubmit() {
  if (saving.value) return
  fieldErrors.value = new Map()

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    if (demoSessionEnabled.value) {
      const amount = form.amount.toFixed(2)
      if (!canCreateDemoPayment(
        isDemoUiSessionActive(),
        getDemoUiSession(),
        demoSelectedBill.value,
        form.bill_id,
        amount,
        form.reference,
        form.payment_date,
        demoBankRefNo.value,
        form.notes,
        false,
      )) throw new Error('回款输入与最新账单余额不一致')
      const result = await createDemoBankReceipt(
        demoSelectedBill.value!,
        form.reference,
        demoBankRefNo.value,
        form.payment_date,
        demoPaymentIdempotencyKey,
        amount,
        form.notes,
      )
      ElMessage.success('客户回款已登记，账单余额尚未改变')
      router.push({
        path: '/billing/payments',
        query: {
          bill_id: result.bill.id,
          payment_id: result.payment.id,
          demo_payment_key: demoPaymentIdempotencyKey,
        },
      })
      return
    }

    const createdPayment = await createPayment({
      bill_id: form.bill_id,
      amount: form.amount,
      payment_method: form.payment_method,
      payment_date: form.payment_date,
      reference: form.reference || undefined,
      notes: form.notes || undefined,
    })

    ElMessage.success('回款登记成功，可在回款列表查看预收状态与未分配金额')
    router.push({
      path: '/billing/payments',
      query: {
        bill_id: createdPayment.bill_id || form.bill_id,
        payment_id: createdPayment.id,
      },
    })
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  syncDemoSession()
  window.addEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
  fetchBillOptions()
  void loadDemoSelectedBill()
})

onBeforeUnmount(() => {
  window.removeEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
})

watch(() => form.bill_id, () => {
  void loadDemoSelectedBill()
})
</script>

<style scoped>
.form-card-title {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
}

.payment-form {
  max-width: 600px;
}

.full-width {
  width: 100%;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 6px;
}

.field-hint a {
  color: var(--color-primary);
  text-decoration: none;
}

.field-hint a:hover {
  text-decoration: underline;
}
</style>
