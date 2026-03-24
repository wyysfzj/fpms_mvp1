<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="760px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <el-alert
      v-if="amountHint"
      :title="amountHint"
      type="warning"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="case-receipt-form"
    >
      <el-row :gutter="12">
        <!-- 案卷 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="案卷" prop="case_id">
            <el-select
              v-model="form.case_id"
              filterable
              remote
              clearable
              :remote-method="searchCases"
              :loading="caseSearchLoading"
              :disabled="isEditMode || !!prefillCaseId"
              placeholder="请输入案卷编号搜索"
              style="width: 100%"
            >
              <el-option
                v-for="c in caseOptions"
                :key="c.id"
                :label="c.case_no"
                :value="c.id"
              />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 费用类型 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="费用类型" prop="fee_type">
            <el-select
              v-model="form.fee_type"
              clearable
              placeholder="请选择费用类型"
              style="width: 100%"
            >
              <el-option value="GOV" label="官费" />
              <el-option value="SERVICE" label="服务费" />
              <el-option value="MISC" label="其他" />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 费用代码 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="费用代码" prop="fee_code">
            <el-input
              v-model.trim="form.fee_code"
              placeholder="请输入费用代码"
              clearable
            />
          </el-form-item>
        </el-col>

        <!-- 费用名称 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="费用名称" prop="fee_name">
            <el-input
              v-model.trim="form.fee_name"
              placeholder="请输入费用名称"
              clearable
            />
          </el-form-item>
        </el-col>

        <!-- 年度 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="年度" prop="year_no">
            <el-input-number
              v-model="form.year_no"
              :min="1900"
              :max="2100"
              controls-position="right"
              placeholder="请输入年度"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>

        <!-- 币种 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="币种" prop="currency">
            <el-select
              v-model="form.currency"
              placeholder="请选择币种"
              style="width: 100%"
            >
              <el-option value="CNY" label="CNY" />
              <el-option value="USD" label="USD" />
              <el-option value="EUR" label="EUR" />
              <el-option value="JPY" label="JPY" />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 应收金额 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="应收金额" prop="receivable_amt">
            <el-input-number
              v-model="form.receivable_amt"
              :min="0"
              :precision="2"
              controls-position="right"
              placeholder="请输入应收金额"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>

        <!-- 实收金额 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="实收金额" prop="received_amt">
            <el-input-number
              v-model="form.received_amt"
              :min="0"
              :precision="2"
              controls-position="right"
              placeholder="请输入实收金额"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>

        <!-- 收款日期 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="收款日期" prop="last_receipt_date">
            <el-date-picker
              v-model="form.last_receipt_date"
              type="date"
              placeholder="请选择收款日期"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>

        <!-- 到期日 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="到期日" prop="due_date">
            <el-date-picker
              v-model="form.due_date"
              type="date"
              placeholder="请选择到期日"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>

        <!-- 发票号 -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="发票号" prop="invoice_no">
            <el-input
              v-model.trim="form.invoice_no"
              placeholder="请输入发票号"
              clearable
            />
          </el-form-item>
        </el-col>

        <!-- Checkboxes -->
        <el-col :xs="24" :sm="12">
          <el-form-item label="标记选项">
            <el-checkbox v-model="form.is_arrears">是否欠款</el-checkbox>
            <el-checkbox v-model="form.is_prepayment" style="margin-left: 16px">是否预收</el-checkbox>
            <el-checkbox v-model="form.is_commissionable" style="margin-left: 16px">是否可提成</el-checkbox>
          </el-form-item>
        </el-col>

        <!-- 备注 -->
        <el-col :xs="24">
          <el-form-item label="备注" prop="remark">
            <el-input
              v-model.trim="form.remark"
              type="textarea"
              :rows="3"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createCaseReceipt, updateCaseReceipt } from '../../../api/billing'
import type { CaseReceiptCreate, CaseReceiptUpdate, CaseReceiptListItem } from '../../../api/billing.types'
import { getCases } from '../../../api/cases'

interface CaseOption {
  id: string
  case_no: string
}

interface ReceiptForm {
  case_id: string
  fee_type: string | null
  fee_code: string
  fee_name: string
  year_no: number | null
  currency: string
  receivable_amt: number | null
  received_amt: number | null
  last_receipt_date: string | null
  due_date: string | null
  is_arrears: boolean
  is_prepayment: boolean
  is_commissionable: boolean
  invoice_no: string
  remark: string
}

const props = defineProps<{
  modelValue: boolean
  receiptId: string | null
  prefillCaseId: string | null
  initialData?: CaseReceiptListItem | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: []
}>()

const visible = ref(props.modelValue)
const formRef = ref<FormInstance>()
const saving = ref(false)
const caseSearchLoading = ref(false)
const caseOptions = ref<CaseOption[]>([])

const isEditMode = computed(() => !!props.receiptId)

const dialogTitle = computed(() => (isEditMode.value ? '编辑收款记录' : '新增收款记录'))

function makeEmptyForm(): ReceiptForm {
  return {
    case_id: props.prefillCaseId || '',
    fee_type: null,
    fee_code: '',
    fee_name: '',
    year_no: null,
    currency: 'CNY',
    receivable_amt: null,
    received_amt: null,
    last_receipt_date: null,
    due_date: null,
    is_arrears: false,
    is_prepayment: false,
    is_commissionable: false,
    invoice_no: '',
    remark: '',
  }
}

const form = reactive<ReceiptForm>(makeEmptyForm())

const amountHint = computed(() => {
  const rec = form.receivable_amt ?? 0
  const paid = form.received_amt ?? 0
  if (paid > 0 && rec > 0) {
    if (paid < rec) return '实收金额小于应收金额，将标记为欠款'
    if (paid > rec) return '实收金额大于应收金额，将标记为预收'
  }
  return ''
})

const rules: FormRules<ReceiptForm> = {
  case_id: [{ required: true, message: '请选择案卷', trigger: 'change' }],
  currency: [{ required: true, message: '请选择币种', trigger: 'change' }],
  receivable_amt: [
    {
      validator: (_rule, value: unknown, callback) => {
        const n = Number(value)
        if (value === null || value === undefined || !Number.isFinite(n) || n < 0) {
          callback(new Error('请输入有效的应收金额'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  received_amt: [
    {
      validator: (_rule, value: unknown, callback) => {
        const n = Number(value)
        if (value === null || value === undefined || !Number.isFinite(n) || n < 0) {
          callback(new Error('请输入有效的实收金额'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

function populateFromInitialData(data: CaseReceiptListItem) {
  form.case_id = data.case_id || ''
  form.fee_type = data.fee_type || null
  form.fee_code = data.fee_code || ''
  form.fee_name = data.fee_name || ''
  form.year_no = data.year_no ?? null
  form.currency = data.currency || 'CNY'
  form.receivable_amt = data.receivable_amt ?? null
  form.received_amt = data.received_amt ?? null
  form.last_receipt_date = data.last_receipt_date || null
  form.due_date = data.due_date || null
  form.is_arrears = data.is_arrears ?? false
  form.is_prepayment = data.is_prepayment ?? false
  form.is_commissionable = data.is_commissionable ?? false
  form.invoice_no = data.invoice_no || ''
  form.remark = data.remark || ''

  // Ensure the case appears in the options list when editing
  if (data.case_id && data.case_no) {
    const exists = caseOptions.value.some((c) => c.id === data.case_id)
    if (!exists) {
      caseOptions.value = [{ id: data.case_id, case_no: data.case_no }, ...caseOptions.value]
    }
  }
}

function resetForm() {
  const empty = makeEmptyForm()
  Object.assign(form, empty)
  caseOptions.value = []

  if (props.prefillCaseId) {
    form.case_id = props.prefillCaseId
  }

  if (isEditMode.value && props.initialData) {
    populateFromInitialData(props.initialData)
  }
}

watch(
  () => props.modelValue,
  (value) => {
    visible.value = value
    if (value) {
      resetForm()
    }
  },
)

watch(visible, (value) => {
  emit('update:modelValue', value)
})

async function searchCases(query: string) {
  if (!query || query.trim().length < 1) {
    caseOptions.value = []
    return
  }
  caseSearchLoading.value = true
  try {
    // getCases accepts extended filter params including case_no (server-side filter)
    const result = await getCases({ page: 1, page_size: 20, case_no: query.trim() } as Parameters<typeof getCases>[0])
    caseOptions.value = result.items.map((c) => ({ id: c.id, case_no: c.case_no }))
  } catch {
    caseOptions.value = []
  } finally {
    caseSearchLoading.value = false
  }
}

function handleClose() {
  visible.value = false
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEditMode.value && props.receiptId) {
      const payload: CaseReceiptUpdate = {
        fee_type: form.fee_type || null,
        fee_code: form.fee_code || null,
        fee_name: form.fee_name || null,
        year_no: form.year_no ?? null,
        currency: form.currency || null,
        receivable_amt: form.receivable_amt ?? 0,
        received_amt: form.received_amt ?? 0,
        last_receipt_date: form.last_receipt_date || null,
        due_date: form.due_date || null,
        is_arrears: form.is_arrears,
        is_prepayment: form.is_prepayment,
        is_commissionable: form.is_commissionable,
        invoice_no: form.invoice_no || null,
        remark: form.remark || null,
      }
      await updateCaseReceipt(props.receiptId, payload)
    } else {
      const payload: CaseReceiptCreate = {
        case_id: form.case_id,
        fee_type: form.fee_type || null,
        fee_code: form.fee_code || null,
        fee_name: form.fee_name || null,
        year_no: form.year_no ?? null,
        currency: form.currency,
        receivable_amt: form.receivable_amt ?? 0,
        received_amt: form.received_amt ?? 0,
        last_receipt_date: form.last_receipt_date || null,
        due_date: form.due_date || null,
        is_arrears: form.is_arrears,
        is_prepayment: form.is_prepayment,
        is_commissionable: form.is_commissionable,
        invoice_no: form.invoice_no || null,
        remark: form.remark || null,
      }
      await createCaseReceipt(payload)
    }
    ElMessage.success('保存成功')
    visible.value = false
    emit('saved')
  } catch {
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}
</script>
