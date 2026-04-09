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
      <h2 class="form-card-title">录入支出</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="expense-form"
      >
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item
              label="案件/项目编号"
              prop="case_id"
              :error="fieldErrors.get('case_id')?.join('，')"
            >
              <el-input
                v-model.trim="form.case_id"
                placeholder="请输入案件或顾问项目编号"
              />
              <div class="field-hint">普通案件与顾问项目共用该编号字段。</div>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="12">
            <el-form-item
              label="支出类别"
              prop="category"
              :error="fieldErrors.get('category')?.join('，')"
            >
              <el-select v-model="form.category" class="full-width" placeholder="请选择支出类别">
                <el-option
                  v-for="option in categoryOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item
              label="支出日期"
              prop="expense_date"
              :error="fieldErrors.get('expense_date')?.join('，')"
            >
              <el-date-picker
                v-model="form.expense_date"
                type="date"
                class="full-width"
                placeholder="请选择支出日期"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="12">
            <el-form-item
              label="支出金额"
              prop="amount"
              :error="fieldErrors.get('amount')?.join('，')"
            >
              <el-input-number
                v-model="form.amount"
                class="full-width"
                :min="0.01"
                :precision="2"
                :step="100"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item
              label="币种"
              prop="currency"
              :error="fieldErrors.get('currency')?.join('，')"
            >
              <el-select v-model="form.currency" class="full-width" placeholder="请选择币种">
                <el-option label="人民币（CNY）" value="CNY" />
                <el-option label="美元（USD）" value="USD" />
                <el-option label="欧元（EUR）" value="EUR" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="12">
            <el-form-item
              label="税额（可选）"
              prop="tax_amount"
              :error="fieldErrors.get('tax_amount')?.join('，')"
            >
              <el-input-number
                v-model="form.tax_amount"
                class="full-width"
                :min="0"
                :precision="2"
                :step="100"
                placeholder="请输入税额"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item
              label="支出编号（可选）"
              prop="expense_no"
              :error="fieldErrors.get('expense_no')?.join('，')"
            >
              <el-input
                v-model.trim="form.expense_no"
                placeholder="留空则由系统自动生成"
              />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :md="12">
            <el-form-item
              label="部门编号（可选）"
              prop="department_id"
              :error="fieldErrors.get('department_id')?.join('，')"
            >
              <el-input
                v-model.trim="form.department_id"
                placeholder="请输入部门编号"
              />
              <div class="field-hint">留空则本条支出暂不参与部门统计。</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item
              label="经手人编号（可选）"
              prop="worker_id"
              :error="fieldErrors.get('worker_id')?.join('，')"
            >
              <el-input
                v-model.trim="form.worker_id"
                placeholder="请输入经手人编号"
              />
              <div class="field-hint">留空则本条支出暂不参与经手人统计。</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item
              label="供应商（可选）"
              prop="vendor_name"
              :error="fieldErrors.get('vendor_name')?.join('，')"
            >
              <el-input
                v-model.trim="form.vendor_name"
                placeholder="请输入供应商名称"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item
          label="备注（可选）"
          prop="remark"
          :error="fieldErrors.get('remark')?.join('，')"
        >
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="请输入备注"
          />
        </el-form-item>

        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSubmit">
            保存支出
          </el-button>
        </div>
      </el-form>
    </div>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { createExpense, mapExpenseError } from '../../../api/expenses'
import type {
  ExpenseApiError,
  ExpenseCategory,
} from '../../../api/expenses.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

interface CategoryOption {
  label: string
  value: ExpenseCategory
}

const categoryOptions: CategoryOption[] = [
  { label: '检索费', value: 'SEARCH_DB' },
  { label: '翻译费', value: 'TRANSLATION' },
  { label: '交通费', value: 'TRANSPORT' },
  { label: '其他', value: 'OTHER' },
]

const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ExpenseApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const form = reactive({
  case_id: typeof route.query.case_id === 'string' ? route.query.case_id : '',
  category: 'OTHER' as ExpenseCategory,
  expense_date: new Date().toISOString().slice(0, 10),
  amount: 0,
  currency: 'CNY',
  tax_amount: undefined as number | undefined,
  expense_no: '',
  department_id: '',
  worker_id: '',
  vendor_name: '',
  remark: '',
})

const rules: FormRules = {
  case_id: [{ required: true, message: '案件/项目编号为必填项', trigger: 'blur' }],
  category: [{ required: true, message: '支出类别为必填项', trigger: 'change' }],
  expense_date: [{ required: true, message: '支出日期为必填项', trigger: 'change' }],
  amount: [
    { required: true, message: '支出金额为必填项', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '支出金额必须大于 0', trigger: 'blur' },
  ],
  currency: [{ required: true, message: '币种为必填项', trigger: 'change' }],
}

function goBack() {
  const returnTo = typeof route.query.return_to === 'string' ? route.query.return_to : ''

  if (returnTo) {
    void router.push(returnTo)
    return
  }

  if (window.history.length > 1) {
    router.back()
    return
  }

  void router.push('/dashboard')
}

async function handleSubmit() {
  fieldErrors.value = new Map()
  error.value = null

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true

  try {
    const created = await createExpense({
      case_id: form.case_id,
      ...(form.department_id ? { department_id: form.department_id } : {}),
      ...(form.worker_id ? { worker_id: form.worker_id } : {}),
      category: form.category,
      expense_date: form.expense_date,
      amount: form.amount,
      currency: form.currency,
      ...(form.tax_amount !== undefined ? { tax_amount: form.tax_amount } : {}),
      ...(form.expense_no ? { expense_no: form.expense_no } : {}),
      ...(form.vendor_name ? { vendor_name: form.vendor_name } : {}),
      ...(form.remark ? { remark: form.remark } : {}),
    })

    ElMessage.success(`支出录入成功${created.expense_no ? `（${created.expense_no}）` : ''}`)
    goBack()
  } catch (err) {
    const apiError = mapExpenseError(err, 'create')
    error.value = apiError
    fieldErrors.value = apiError.field_errors || new Map()
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-card-title {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
}

.expense-form {
  max-width: 760px;
}

.full-width {
  width: 100%;
}

.field-hint {
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 12px;
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
