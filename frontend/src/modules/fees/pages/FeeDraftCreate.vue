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
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="draft-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">{{ isApplyFeeMode ? '生成申请费草稿' : '草稿基础信息' }}</h3>

          <el-alert
            v-if="isApplyFeeMode"
            type="info"
            show-icon
            :closable="false"
            title="将根据案件的权利要求数、费减、折扣率和费率配置生成真实申请费草稿。"
            class="mode-alert"
          />

          <el-form-item label="案件编号" prop="case_id" :error="fieldErrors.get('case_id')?.join(', ')">
            <el-input
              v-model.trim="form.case_id"
              placeholder="请输入案件编号"
              class="full-width"
            />
            <div class="field-hint">
              <router-link to="/cases">查看案件列表</router-link> 以复制正确案件编号
            </div>
          </el-form-item>

          <el-form-item label="客户编号" prop="client_id" :error="fieldErrors.get('client_id')?.join(', ')">
            <el-input
              v-model.trim="form.client_id"
              placeholder="可选客户编号"
              class="full-width"
            />
            <div class="field-hint">
              <router-link to="/clients">查看客户列表</router-link> 以复制正确客户编号
            </div>
          </el-form-item>

          <el-form-item label="币种" prop="currency" :error="fieldErrors.get('currency')?.join(', ')">
            <el-select v-model="form.currency" placeholder="请选择币种" class="full-width">
              <el-option label="CNY" value="CNY" />
              <el-option label="USD" value="USD" />
              <el-option label="EUR" value="EUR" />
            </el-select>
          </el-form-item>

          <el-form-item
            v-if="isApplyFeeMode"
            label="折扣率"
            prop="discount_rate"
            :error="fieldErrors.get('discount_rate')?.join(', ')"
          >
            <el-input
              v-model.trim="form.discount_rate"
              placeholder="可选，例如 0.90"
              class="full-width"
            />
          </el-form-item>

          <div class="field-hint">
            {{ isApplyFeeMode ? '申请费草稿会自动生成官费与服务费明细。' : '币种用于初始化草稿明细与金额汇总。' }}
          </div>
        </div>

        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSubmit">
            {{ isApplyFeeMode ? '生成申请费草稿' : '创建草稿' }}
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createFeeDraft, generateApplyFeeDraft } from '../../../api/fees'
import type { FeeDraftCreatePayload } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const form = reactive({
  case_id: String(route.query.case_id || ''),
  client_id: '',
  currency: 'CNY',
  discount_rate: '',
})

const isApplyFeeMode = computed(() => String(route.query.draft_type || '').toUpperCase() === 'APPLY_FEE')

const rules: FormRules = {
  case_id: [
    { required: true, message: '案件编号为必填项', trigger: 'blur' },
  ],
  currency: [
    { required: true, message: '币种为必填项', trigger: 'change' },
  ],
}

function goBack() {
  router.push('/fees/drafts')
}

async function handleSubmit() {
  fieldErrors.value = new Map()

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    const draft = isApplyFeeMode.value
      ? await generateApplyFeeDraft({
          case_id: form.case_id,
          currency: form.currency,
          discount_rate: form.discount_rate || undefined,
        })
      : await createGenericDraft()
    ElMessage.success(isApplyFeeMode.value ? '申请费草稿生成成功' : '费用草稿创建成功')
    router.push(`/fees/drafts/${draft.id}`)
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

async function createGenericDraft() {
  const payload: FeeDraftCreatePayload = {
    case_id: form.case_id,
    currency: form.currency,
  }
  if (form.client_id) {
    payload.client_id = form.client_id
  }
  return createFeeDraft(payload)
}
</script>

<style scoped>
.full-width {
  width: 100%;
}

.draft-form .el-form-item {
  margin-bottom: 20px;
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

.mode-alert {
  margin-bottom: 16px;
}
</style>
