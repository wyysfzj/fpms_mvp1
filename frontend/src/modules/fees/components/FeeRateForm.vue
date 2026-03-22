<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑费率' : '新建费率'"
    width="680px"
    @close="handleClose"
  >
    <!-- Error Banner -->
    <div v-if="error" class="dialog-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="fee-form"
    >
      <el-form-item label="名称" prop="name" :error="fieldErrors.get('name')?.join(', ')">
        <el-input v-model="form.name" placeholder="例如：标准申请费" />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="费率" prop="rate" :error="fieldErrors.get('rate')?.join(', ')">
            <el-input-number
              v-model="form.rate"
              :min="0"
              :precision="2"
              :step="100"
              style="width: 100%"
              controls-position="right"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="币种" prop="currency" :error="fieldErrors.get('currency')?.join(', ')">
            <el-select v-model="form.currency" placeholder="请选择" style="width: 100%">
              <el-option label="CNY" value="CNY" />
              <el-option label="USD" value="USD" />
              <el-option label="EUR" value="EUR" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="描述" prop="description" :error="fieldErrors.get('description')?.join(', ')">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="可选描述"
        />
      </el-form-item>

      <!-- Dimension Fields Section -->
      <el-divider content-position="left">维度设置</el-divider>

      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="费率组" prop="rate_group">
            <el-select v-model="form.rate_group" placeholder="请选择" clearable style="width: 100%">
              <el-option label="国内" value="DOMESTIC" />
              <el-option label="PCT" value="PCT" />
              <el-option label="年费" value="ANNUITY" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="计算模式" prop="calc_mode">
            <el-select v-model="form.calc_mode" placeholder="请选择" clearable style="width: 100%">
              <el-option label="固定" value="FIXED" />
              <el-option label="按权利要求" value="PER_CLAIM" />
              <el-option label="按页" value="PER_PAGE" />
              <el-option label="阶梯" value="TIER" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="国家/地区" prop="country_code">
            <el-input v-model="form.country_code" placeholder="例如：CN" maxlength="10" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="案件类型" prop="case_type">
            <el-select v-model="form.case_type" placeholder="请选择" clearable style="width: 100%">
              <el-option label="普通" value="NORMAL" />
              <el-option label="PCT国际" value="PCT_INTL" />
              <el-option label="PCT国内" value="PCT_NATL" />
              <el-option label="优先权" value="PRIORITY" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="专利类别" prop="patent_category">
            <el-select v-model="form.patent_category" placeholder="请选择" clearable style="width: 100%">
              <el-option label="发明" value="INV" />
              <el-option label="实用新型" value="UM" />
              <el-option label="外观设计" value="DES" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="允许减缴">
            <el-switch v-model="form.allow_reduction" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="生效日期" prop="effective_from">
            <el-date-picker
              v-model="form.effective_from"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="失效日期" prop="effective_to">
            <el-date-picker
              v-model="form.effective_to"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="计算参数" prop="calc_params">
        <el-input
          v-model="form.calc_params"
          type="textarea"
          :rows="2"
          :placeholder="calcParamsPlaceholder"
        />
        <div class="field-hint">{{ calcParamsHint }}</div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">
        {{ isEdit ? '保存修改' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createFeeRate, updateFeeRate } from '../../../api/fees'
import type { FeeRate, FeeRateCreatePayload, FeeRateUpdatePayload } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const props = defineProps<{
  visible: boolean
  rate?: FeeRate | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const isEdit = computed(() => !!props.rate)
const calcParamsPlaceholder = computed(() => {
  if (form.calc_mode === 'PER_CLAIM') {
    return '{"per_claim_amount":"50","discount_pct":"10","reduction_pct":"20"}'
  }
  return 'JSON格式（可选）'
})
const calcParamsHint = computed(() => {
  if (form.calc_mode === 'PER_CLAIM') {
    if (form.allow_reduction) {
      return '按权利要求模式支持 per_claim_amount、discount_pct、reduction_pct。已开启允许减缴时，减缴比例会参与计算。'
    }
    return '按权利要求模式支持 per_claim_amount、discount_pct、reduction_pct。未开启允许减缴时，reduction_pct 会被忽略。'
  }
  return '如需高级计算，可填写 JSON 参数；未填写时按默认金额处理。'
})

const form = reactive<FeeRateCreatePayload>({
  name: '',
  rate: 0,
  currency: 'CNY',
  description: '',
  rate_group: null,
  country_code: null,
  case_type: null,
  patent_category: null,
  calc_mode: null,
  calc_params: null,
  allow_reduction: false,
  effective_from: null,
  effective_to: null,
})

const rules: FormRules = {
  name: [
    { required: true, message: '名称为必填项', trigger: 'blur' },
    { max: 200, message: '名称不能超过 200 个字符', trigger: 'blur' },
  ],
  rate: [
    { required: true, message: '费率为必填项', trigger: 'blur' },
  ],
}

// Populate form when editing
watch(() => props.rate, (rate) => {
  if (rate) {
    form.name = rate.name
    form.rate = rate.rate
    form.currency = rate.currency || 'CNY'
    form.description = rate.description || ''
    form.rate_group = rate.rate_group ?? null
    form.country_code = rate.country_code ?? null
    form.case_type = rate.case_type ?? null
    form.patent_category = rate.patent_category ?? null
    form.calc_mode = rate.calc_mode ?? null
    form.calc_params = rate.calc_params ?? null
    form.allow_reduction = rate.allow_reduction ?? false
    form.effective_from = rate.effective_from ?? null
    form.effective_to = rate.effective_to ?? null
  } else {
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.name = ''
  form.rate = 0
  form.currency = 'CNY'
  form.description = ''
  form.rate_group = null
  form.country_code = null
  form.case_type = null
  form.patent_category = null
  form.calc_mode = null
  form.calc_params = null
  form.allow_reduction = false
  form.effective_from = null
  form.effective_to = null
  fieldErrors.value = new Map()
  error.value = null
}

function handleClose() {
  emit('update:visible', false)
  resetForm()
}

async function handleSubmit() {
  fieldErrors.value = new Map()
  
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    const payload: FeeRateCreatePayload | FeeRateUpdatePayload = {
      name: form.name,
      rate: form.rate,
      currency: form.currency || undefined,
      description: form.description || undefined,
      rate_group: form.rate_group || undefined,
      country_code: form.country_code || undefined,
      case_type: form.case_type || undefined,
      patent_category: form.patent_category || undefined,
      calc_mode: form.calc_mode || undefined,
      calc_params: form.calc_params || undefined,
      allow_reduction: form.allow_reduction ?? undefined,
      effective_from: form.effective_from || undefined,
      effective_to: form.effective_to || undefined,
    }

    if (isEdit.value && props.rate) {
      await updateFeeRate(props.rate.id, payload)
      ElMessage.success('费率更新成功')
    } else {
      await createFeeRate(payload as FeeRateCreatePayload)
      ElMessage.success('费率创建成功')
    }

    emit('success')
    handleClose()
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
</script>

<style scoped>
.dialog-error {
  margin-bottom: 16px;
}

.fee-form .el-form-item {
  margin-bottom: 18px;
}
</style>
