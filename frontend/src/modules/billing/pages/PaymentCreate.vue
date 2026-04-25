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
                <el-select v-model="form.payment_method" placeholder="请选择付款方式" class="full-width">
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
            label="收款编号 / 交易参考号"
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
import { onMounted, ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { createPayment, getBills } from '../../../api/billing'
import type { BillListItem, PaymentMethod } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const billOptionsLoading = ref(false)
const billOptions = ref<BillListItem[]>([])

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

function goBack() {
  router.push('/billing/payments')
}

function formatBillOption(bill: BillListItem): string {
  const clientText = bill.client_name || bill.client_id || '未关联客户'
  const balanceText = bill.balance.toLocaleString('zh-CN', {
    style: 'currency',
    currency: bill.currency || 'CNY',
  })
  return `${bill.bill_no} · ${clientText} · 余额 ${balanceText}`
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
  fieldErrors.value = new Map()

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    await createPayment({
      bill_id: form.bill_id,
      amount: form.amount,
      payment_method: form.payment_method,
      payment_date: form.payment_date,
      reference: form.reference || undefined,
      notes: form.notes || undefined,
    })

    ElMessage.success('回款登记成功，可在回款列表查看预收状态与未分配金额')
    router.push('/billing/payments')
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
  fetchBillOptions()
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
