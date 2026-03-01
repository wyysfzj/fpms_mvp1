<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div class="form-card">
      <h2 class="form-card-title">官方缴费登记</h2>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="gov-payment-form">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12">
            <el-form-item
              label="官费清单ID"
              prop="pay_list_id"
              :error="fieldErrors.get('pay_list_id')?.join('，')"
            >
              <el-input-number
                v-model="form.pay_list_id"
                :min="1"
                :precision="0"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item
              label="费用项ID"
              prop="fee_item_id"
              :error="fieldErrors.get('fee_item_id')?.join('，')"
            >
              <el-input v-model.trim="form.fee_item_id" placeholder="请输入费用项编号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="缴费日期" prop="paid_date" :error="fieldErrors.get('paid_date')?.join('，')">
              <el-date-picker
                v-model="form.paid_date"
                type="date"
                placeholder="请选择缴费日期（可选）"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item
              label="缴费金额"
              prop="paid_amount"
              :error="fieldErrors.get('paid_amount')?.join('，')"
            >
              <el-input-number
                v-model="form.paid_amount"
                :min="0.01"
                :precision="2"
                :step="10"
                controls-position="right"
                style="width: 100%"
              />
              <div class="field-hint">可选；不填时由后端按费用项金额处理。</div>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item
              label="官方收据号"
              prop="official_receipt_no"
              :error="fieldErrors.get('official_receipt_no')?.join('，')"
            >
              <el-input v-model.trim="form.official_receipt_no" placeholder="请输入收据号（可选）" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="备注" prop="remark" :error="fieldErrors.get('remark')?.join('，')">
              <el-input v-model.trim="form.remark" placeholder="可填写说明（可选）" />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSubmit">提交登记</el-button>
        </div>
      </el-form>
    </div>

    <div v-if="result" class="result-card">
      <h2 class="form-card-title">登记结果</h2>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="缴费记录ID">{{ result.gov_payment.id }}</el-descriptions-item>
        <el-descriptions-item label="费用项ID">{{ result.gov_payment.fee_item_id }}</el-descriptions-item>
        <el-descriptions-item label="缴费状态">{{ govPaymentStatusText(result.gov_payment.status) }}</el-descriptions-item>
        <el-descriptions-item label="缴费日期">{{ result.gov_payment.paid_date || '—' }}</el-descriptions-item>
        <el-descriptions-item label="缴费金额">
          {{ formatMoney(result.gov_payment.paid_amount, result.gov_payment.currency) }}
        </el-descriptions-item>
        <el-descriptions-item label="收据号">
          {{ result.gov_payment.official_receipt_no || '—' }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="result-section">
        <h3 class="section-title">官费清单状态</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="清单编号">
            {{ result.pay_list.pay_list_no || `#${result.pay_list.id}` }}
          </el-descriptions-item>
          <el-descriptions-item label="清单状态">
            <el-tag :type="payListStatusTag(result.pay_list.status)">
              {{ payListStatusText(result.pay_list.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户ID">{{ result.pay_list.client_id }}</el-descriptions-item>
          <el-descriptions-item label="更新后总额">
            {{ formatMoney(result.pay_list.total_amount, result.pay_list.currency) }}
          </el-descriptions-item>
          <el-descriptions-item label="清单缴费日期">
            {{ result.pay_list.paid_date || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="币种">{{ result.pay_list.currency }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { mapGovPaymentsError, registerGovPayment } from '../../../api/govPayments'
import type { GovPaymentRegisterResult, GovPaymentsApiError } from '../../../api/govPayments.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

interface GovPaymentForm {
  pay_list_id: number
  fee_item_id: string
  paid_date: string
  paid_amount: number | null
  official_receipt_no: string
  remark: string
}

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<GovPaymentsApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const result = ref<GovPaymentRegisterResult | null>(null)

const queryPayListId = Number(route.query.pay_list_id || 0)
const queryFeeItemId = String(route.query.fee_item_id || '')

const form = reactive<GovPaymentForm>({
  pay_list_id: Number.isFinite(queryPayListId) && queryPayListId > 0 ? queryPayListId : 0,
  fee_item_id: queryFeeItemId,
  paid_date: new Date().toISOString().split('T')[0],
  paid_amount: null,
  official_receipt_no: '',
  remark: '',
})

const rules: FormRules<GovPaymentForm> = {
  pay_list_id: [
    { required: true, message: '官费清单ID为必填项', trigger: 'blur' },
    {
      validator: (_rule, value: unknown, callback) => {
        const numeric = Number(value)
        if (!Number.isFinite(numeric) || numeric <= 0) {
          callback(new Error('官费清单ID必须大于 0'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  fee_item_id: [{ required: true, message: '费用项ID为必填项', trigger: 'blur' }],
  paid_amount: [
    {
      validator: (_rule, value: unknown, callback) => {
        if (value === null || value === undefined || value === '') {
          callback()
          return
        }
        const numeric = Number(value)
        if (!Number.isFinite(numeric) || numeric <= 0) {
          callback(new Error('缴费金额必须大于 0'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

function goBack() {
  router.push('/annuity/pay-lists')
}

function govPaymentStatusText(status: string): string {
  switch (status?.toUpperCase()) {
    case 'PAID':
      return '已缴费'
    case 'RECORDED':
      return '已登记'
    case 'PLANNED':
      return '已计划'
    default:
      return status || '未知'
  }
}

function payListStatusText(status: string): string {
  switch (status?.toUpperCase()) {
    case 'DRAFT':
      return '草稿'
    case 'PARTIAL':
      return '部分完成'
    case 'PAID':
      return '已完成'
    default:
      return status || '未知'
  }
}

function payListStatusTag(status: string): 'info' | 'warning' | 'success' {
  switch (status?.toUpperCase()) {
    case 'PAID':
      return 'success'
    case 'PARTIAL':
      return 'warning'
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

async function handleSubmit() {
  fieldErrors.value = new Map()
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null
  try {
    const response = await registerGovPayment({
      pay_list_id: form.pay_list_id,
      fee_item_id: form.fee_item_id,
      paid_date: form.paid_date || undefined,
      paid_amount: form.paid_amount ?? undefined,
      official_receipt_no: form.official_receipt_no || undefined,
      remark: form.remark || undefined,
    })
    result.value = response
    ElMessage.success('官方缴费登记成功。')
  } catch (err) {
    const mapped = mapGovPaymentsError(err)
    error.value = mapped
    if (mapped.field_errors && mapped.field_errors.size > 0) {
      fieldErrors.value = mapped.field_errors
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.gov-payment-form {
  max-width: 920px;
}

.field-hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-sub);
}

.result-card {
  margin-top: 20px;
}

.result-section {
  margin-top: 16px;
}

.section-title {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
}

.page-error {
  outline: none;
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
  .filter-actions,
  .action-row,
  .form-actions,
  .batch-action-bar {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-header-right :deep(.el-button),
  .filter-actions :deep(.el-button),
  .action-row :deep(.el-button),
  .form-actions :deep(.el-button),
  .batch-action-bar :deep(.el-button) {
    flex: 1;
    min-width: 120px;
  }
}
</style>
