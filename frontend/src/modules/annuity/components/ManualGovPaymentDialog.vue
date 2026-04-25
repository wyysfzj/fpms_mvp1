<template>
  <el-dialog
    v-model="visible"
    title="新增历史缴费明细"
    width="760px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <div class="dialog-intro">
      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="仅空的历史清单可新增手工明细，费用项编号可以留空。"
        :description="dialogHint"
      />
    </div>

    <div v-if="error" class="dialog-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="manual-gov-payment-form"
    >
      <el-row :gutter="12">
        <el-col :xs="24" :sm="12">
          <el-form-item
            label="案件编号"
            prop="case_id"
            :error="fieldErrors.get('case_id')?.join('，')"
          >
            <el-select
              v-model="form.case_id"
              filterable
              clearable
              :loading="caseOptionsLoading"
              placeholder="请选择案件"
              style="width: 100%"
            >
              <el-option
                v-for="caseItem in caseOptions"
                :key="caseItem.id"
                :label="formatCaseOption(caseItem)"
                :value="caseItem.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item
            label="费用项编号（可选）"
            prop="fee_item_id"
            :error="fieldErrors.get('fee_item_id')?.join('，')"
          >
            <el-input
              v-model.trim="form.fee_item_id"
              placeholder="留空表示不绑定费用项"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item
            label="缴费日期"
            prop="paid_date"
            :error="fieldErrors.get('paid_date')?.join('，')"
          >
            <el-date-picker
              v-model="form.paid_date"
              type="date"
              placeholder="请选择日期"
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
              placeholder="请输入收据号（可选）"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item
            label="备注"
            prop="remark"
            :error="fieldErrors.get('remark')?.join('，')"
          >
            <el-input
              v-model.trim="form.remark"
              type="textarea"
              :rows="3"
              placeholder="可填写补录说明（可选）"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">提交补录</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { getCases } from '../../../api/cases'
import type { Case } from '../../../api/cases.types'
import { addManualGovPayment, mapGovPaymentsError } from '../../../api/govPayments'
import type { GovPaymentsApiError } from '../../../api/govPayments.types'
import { mapFieldErrors } from '../../../api/errors'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

interface ManualGovPaymentForm {
  case_id: string
  fee_item_id: string
  paid_date: string
  paid_amount: number | null
  official_receipt_no: string
  remark: string
}

const props = defineProps<{
  modelValue: boolean
  payListId: number | null
  payListTitle: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const visible = ref(props.modelValue)
const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<GovPaymentsApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const caseOptionsLoading = ref(false)
const caseOptions = ref<Case[]>([])

const form = reactive<ManualGovPaymentForm>({
  case_id: '',
  fee_item_id: '',
  paid_date: dayjs().format('YYYY-MM-DD'),
  paid_amount: null,
  official_receipt_no: '',
  remark: '',
})

const rules: FormRules<ManualGovPaymentForm> = {
  case_id: [{ required: true, message: '请选择案件', trigger: 'change' }],
  paid_date: [{ required: true, message: '缴费日期为必填项', trigger: 'change' }],
  paid_amount: [
    {
      validator: (_rule, value: unknown, callback) => {
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

const dialogHint = computed(() => {
  const label = props.payListTitle || '当前清单'
  return `将把这条手工明细补录到“${label}”。如果费用项编号不填写，系统会保留为空。`
})

function resetForm() {
  form.case_id = ''
  form.fee_item_id = ''
  form.paid_date = dayjs().format('YYYY-MM-DD')
  form.paid_amount = null
  form.official_receipt_no = ''
  form.remark = ''
  error.value = null
  fieldErrors.value = new Map()
}

function formatCaseOption(caseItem: Case): string {
  const title = caseItem.title ? ` · ${caseItem.title}` : ''
  const client = caseItem.client_name ? ` · ${caseItem.client_name}` : ''
  return `${caseItem.case_no}${title}${client}`
}

async function fetchCaseOptions() {
  caseOptionsLoading.value = true
  try {
    const result = await getCases({ page: 1, page_size: 100 })
    caseOptions.value = result.items
  } catch (err) {
    error.value = mapGovPaymentsError(err)
  } finally {
    caseOptionsLoading.value = false
  }
}

watch(
  () => props.modelValue,
  (value) => {
    visible.value = value
    if (value) {
      resetForm()
      void fetchCaseOptions()
    }
  },
)

watch(visible, (value) => {
  emit('update:modelValue', value)
})

function handleClose() {
  visible.value = false
}

function mapErrorMessage(apiError: ApiError): string {
  switch (apiError.code) {
    case 'PAY_LIST_NOT_FOUND':
      return '官费清单不存在，请刷新后重试。'
    case 'PAY_LIST_STATE_CONFLICT':
      return '当前清单状态不允许补录手工明细。'
    case 'CASE_REQUIRED':
      return '请选择案件。'
    case 'CASE_NOT_FOUND':
      return '案件不存在，请检查后重试。'
    case 'PAY_LIST_SCOPE_INVALID':
      return '案件或费用项与当前清单不匹配，请检查后重试。'
    case 'FEE_ITEM_NOT_FOUND':
      return '费用项不存在，请检查后重试。'
    case 'GOV_PAYMENT_INVALID':
      return '缴费金额必须大于 0，请检查后重试。'
    case 'VALIDATION_ERROR':
      return '请求参数校验失败，请检查后重试。'
    default:
      if (apiError.status === 401) return '登录已失效，请重新登录。'
      if (apiError.status === 403) return '无权限执行该操作。'
      if (apiError.status === 404) return '目标资源不存在，请确认后重试。'
      if (apiError.status === 409) return '数据冲突，当前请求无法完成。'
      if (apiError.status === 422) return '请求参数不符合要求，请检查后重试。'
      return '补录失败，请稍后重试。'
  }
}

async function handleSubmit() {
  fieldErrors.value = new Map()

  if (!props.payListId || props.payListId <= 0) {
    ElMessage.error('清单编号无效，无法补录。')
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    await addManualGovPayment(props.payListId, {
      case_id: form.case_id.trim(),
      fee_item_id: form.fee_item_id.trim() || undefined,
      paid_date: form.paid_date,
      paid_amount: form.paid_amount as number,
      official_receipt_no: form.official_receipt_no.trim() || undefined,
      remark: form.remark.trim() || undefined,
    })
    ElMessage.success('历史缴费明细已补录。')
    visible.value = false
    emit('success')
  } catch (err) {
    const mapped = mapGovPaymentsError(err)
    error.value = {
      ...mapped,
      message: mapErrorMessage(mapped),
    }
    if (mapped.category === 'validation' && mapped.details) {
      fieldErrors.value = mapFieldErrors(mapped.details)
    }
  } finally {
    saving.value = false
  }
}
</script>
