<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="!routeContextReady"
      class="page-warning"
      type="warning"
      :closable="false"
      show-icon
      title="请从官费清单回执中的“登记缴费”入口进入此页，系统会自动带入清单和费用项。"
    />

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div class="form-card">
      <h2 class="form-card-title">官方缴费登记</h2>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="gov-payment-form">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12">
            <el-form-item
              label="官费清单"
              prop="pay_list_id"
              :error="fieldErrors.get('pay_list_id')?.join('，')"
            >
              <el-input :model-value="formatPayListContext()" style="width: 100%" disabled />
              <div class="field-hint">由回执页自动带入，不能手工修改。</div>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item
              label="费用项"
              prop="fee_item_id"
              :error="fieldErrors.get('fee_item_id')?.join('，')"
            >
              <el-input :model-value="formatFeeItemContext()" placeholder="费用项由上一步自动带入" disabled />
              <div class="field-hint">生成行的费用项已锁定，防止误登记到其他费用项。</div>
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
                :disabled="demoCommandMode"
                style="width: 100%"
              />
              <div class="field-hint">
                {{ demoCommandMode ? '由本次官费计划锁定，不能手工修改。' : '可选；不填时由后端按费用项金额处理。' }}
              </div>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item
              label="官方收据号"
              prop="official_receipt_no"
              :error="fieldErrors.get('official_receipt_no')?.join('，')"
            >
              <el-input
                v-model.trim="form.official_receipt_no"
                :disabled="demoCommandMode"
                :placeholder="demoCommandMode ? '无，待官方凭证' : '请输入收据号（可选)'"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="备注" prop="remark" :error="fieldErrors.get('remark')?.join('，')">
              <el-input v-model.trim="form.remark" :disabled="demoCommandMode" placeholder="可填写说明（可选）" />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" :loading="saving" :disabled="!routeContextReady" @click="handleSubmit">
            提交登记
          </el-button>
        </div>
      </el-form>
    </div>

    <div v-if="result" class="result-card">
      <h2 class="form-card-title">登记结果</h2>

      <el-alert
        v-if="demoCommandMode"
        class="page-warning"
        title="已登记，待官方凭证核验"
        type="warning"
        :closable="false"
        description="本步骤只登记内部缴费事实；官方收据、凭证和发票仍为空。"
      />

      <el-descriptions :column="3" border>
        <el-descriptions-item label="缴费记录">{{ formatGovPaymentDisplay(result.gov_payment.id) }}</el-descriptions-item>
        <el-descriptions-item label="费用项">{{ formatFeeItemContext(result.gov_payment.fee_item_id) }}</el-descriptions-item>
        <el-descriptions-item label="缴费状态">
          <el-tag :type="resultPendingOfficialEvidence ? 'warning' : govPaymentStatusTag(result.gov_payment.status)">
            {{ resultPendingOfficialEvidence ? '已登记，待官方凭证核验' : govPaymentStatusText(result.gov_payment.status) }}
          </el-tag>
        </el-descriptions-item>
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
            {{ formatPayListDisplay(result.pay_list.pay_list_no) }}
          </el-descriptions-item>
          <el-descriptions-item label="清单状态">
            <el-tag :type="resultPendingOfficialEvidence ? 'warning' : payListStatusTag(result.pay_list.status)">
              {{ resultPendingOfficialEvidence ? '已登记，待官方凭证核验' : payListStatusText(result.pay_list.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户">{{ formatClientDisplay(result.pay_list.client_id) }}</el-descriptions-item>
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
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import {
  createDemoGovPaymentCommand,
  mapGovPaymentsError,
  registerGovPayment,
} from '../../../api/govPayments'
import type {
  DemoGovPaymentCommandResult,
  GovPaymentRegisterResult,
  GovPaymentsApiError,
} from '../../../api/govPayments.types'
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
const result = ref<GovPaymentRegisterResult | DemoGovPaymentCommandResult | null>(null)
const resultPendingOfficialEvidence = computed(() => (
  result.value !== null
  && 'fact_status' in result.value
  && result.value.fact_status === 'REGISTERED_PENDING_OFFICIAL_EVIDENCE'
))
const idempotencyKey = crypto.randomUUID()

function parseQueryPositiveInt(value: unknown): number {
  if (typeof value !== 'string' && typeof value !== 'number') return 0
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0
}

function parseQueryText(value: unknown): string {
  if (typeof value === 'string') return value.trim()
  if (Array.isArray(value)) return String(value[0] || '').trim()
  return ''
}

const queryPayListId = parseQueryPositiveInt(route.query.pay_list_id)
const queryFeeItemId = parseQueryText(route.query.fee_item_id)
const demoCommandMode = parseQueryText(route.query.demo_command) === '1'
const queryPaidAmount = Number(parseQueryText(route.query.paid_amount))

const form = reactive<GovPaymentForm>({
  pay_list_id: Number.isFinite(queryPayListId) && queryPayListId > 0 ? queryPayListId : 0,
  fee_item_id: queryFeeItemId,
  paid_date: new Date().toISOString().split('T')[0],
  paid_amount: Number.isFinite(queryPaidAmount) && queryPaidAmount > 0 ? queryPaidAmount : null,
  official_receipt_no: '',
  remark: demoCommandMode ? '已登记，待官方凭证核验' : '',
})

const rules: FormRules<GovPaymentForm> = {
  pay_list_id: [
    { required: true, message: '官费清单为必填项', trigger: 'blur' },
    {
      validator: (_rule, value: unknown, callback) => {
        const numeric = Number(value)
        if (!Number.isFinite(numeric) || numeric <= 0) {
          callback(new Error('官费清单配置无效'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  fee_item_id: [{ required: true, message: '费用项为必填项', trigger: 'blur' }],
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

const routeContextReady = computed(() => form.pay_list_id > 0 && form.fee_item_id.length > 0)

function goBack() {
  router.push('/annuity/pay-lists')
}

function govPaymentStatusText(status: string): string {
  switch (status?.toUpperCase()) {
    case 'PAID':
      return '已缴费'
    case 'RECORDED':
      return '已登记，待官方凭证核验'
    case 'PLANNED':
      return '已计划'
    default:
      return '未知状态'
  }
}

function govPaymentStatusTag(status: string): 'success' | 'info' | 'warning' {
  switch (status?.toUpperCase()) {
    case 'PAID':
      return 'success'
    case 'PLANNED':
      return 'warning'
    default:
      return 'info'
  }
}

function payListStatusText(status?: string): string {
  switch (status?.toUpperCase()) {
    case 'DRAFT':
      return '草稿'
    case 'PARTIAL':
      return '部分完成'
    case 'PAID':
      return '已完成'
    default:
      return '未知状态'
  }
}

function payListStatusTag(status?: string): 'info' | 'warning' | 'success' {
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

function formatPayListContext(): string {
  return form.pay_list_id > 0 ? '已选择清单' : '未选择清单'
}

function formatFeeItemContext(value?: string | null): string {
  const target = value ?? form.fee_item_id
  return target ? '已选择费用项' : '未选择费用项'
}

function formatGovPaymentDisplay(value?: number | string | null): string {
  return value ? '已登记缴费' : '未登记缴费'
}

function formatPayListDisplay(value?: string | null): string {
  return value || '未生成清单编号'
}

function formatClientDisplay(value?: string | null): string {
  return value ? '已关联客户' : '未关联客户'
}

async function handleSubmit() {
  fieldErrors.value = new Map()
  if (!routeContextReady.value) {
    ElMessage.warning('请从官费清单回执中的“登记缴费”入口进入后再提交。')
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null
  try {
    const response = demoCommandMode
      ? await createDemoGovPaymentCommand({
          pay_list_id: form.pay_list_id,
          fee_item_id: form.fee_item_id,
          paid_date: form.paid_date,
          paid_amount: form.paid_amount as number,
          official_receipt_no: null,
          voucher_no: null,
          invoice_no: null,
          remark: '已登记，待官方凭证核验',
          idempotency_key: idempotencyKey,
        })
      : await registerGovPayment({
          pay_list_id: form.pay_list_id,
          fee_item_id: form.fee_item_id,
          paid_date: form.paid_date || undefined,
          paid_amount: form.paid_amount ?? undefined,
          official_receipt_no: form.official_receipt_no || undefined,
          remark: form.remark || undefined,
        })
    result.value = response
    ElMessage.success(
      demoCommandMode
        ? '缴费事实已登记，待官方凭证核验。'
        : '官方缴费登记成功，清单状态已同步更新。',
    )
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

.page-warning {
  margin-bottom: 16px;
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
