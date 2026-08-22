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

          <div
            v-if="hasObligationQuery"
            class="obligation-card"
            data-testid="linked-fee-obligation"
          >
            <h4 class="obligation-card-title">关联缴费义务</h4>
            <p v-if="obligationLoading">正在读取缴费义务详情……</p>
            <template v-else-if="linkedObligation">
              <p>义务编号：{{ linkedObligation.id }}</p>
              <p>来源活动：{{ linkedObligation.source.source_activity_id }}</p>
              <p>来源文档：{{ linkedObligation.source.source_document_id || '无' }}</p>
              <p>来源状态：{{ linkedObligation.source.status }}</p>
              <p>客户指示：{{ linkedObligation.statuses.client_instruction_status }}</p>
            </template>
            <p v-if="linkedDraftBlockMessage" class="obligation-block-message">
              {{ linkedDraftBlockMessage }}
            </p>
          </div>

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
          <el-button
            type="primary"
            :loading="saving"
            :disabled="linkedDraftBlocked"
            @click="handleSubmit"
          >
            {{ isApplyFeeMode ? '生成申请费草稿' : '创建草稿' }}
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createFeeDraft, generateApplyFeeDraft, getFeeObligation } from '../../../api/fees'
import type { FeeDraftCreatePayload, FeeObligationDetail } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const obligationLoading = ref(false)
const linkedObligation = ref<FeeObligationDetail | null>(null)

const obligationQuery = route.query.obligation_id
const hasObligationQuery = obligationQuery !== undefined
const obligationId = typeof obligationQuery === 'string' && obligationQuery !== ''
  ? obligationQuery
  : null

const form = reactive({
  case_id: String(route.query.case_id || ''),
  client_id: '',
  currency: 'CNY',
  discount_rate: '',
})

const isApplyFeeMode = computed(() => String(route.query.draft_type || '').toUpperCase() === 'APPLY_FEE')
const linkedDraftBlocked = computed(() => hasObligationQuery && (
  obligationId === null
  || linkedObligation.value?.id !== obligationId
  || linkedObligation.value.statuses.client_instruction_status !== 'PAY'
  || isApplyFeeMode.value
))
const linkedDraftBlockMessage = computed(() => {
  if (!hasObligationQuery || obligationLoading.value) return null
  if (obligationId === null) return '链接中缺少唯一有效的缴费义务编号，无法创建关联草稿。'
  if (!linkedObligation.value) return '缴费义务详情加载失败，无法创建关联草稿。'
  if (linkedObligation.value.id !== obligationId) {
    return '后端返回的缴费义务与链接不一致，无法创建关联草稿。'
  }
  if (isApplyFeeMode.value) return '关联缴费义务仅支持创建普通费用草稿。'
  if (linkedObligation.value.statuses.client_instruction_status !== 'PAY') {
    return '仅当客户指示为 PAY 时才可创建关联草稿。'
  }
  return null
})

const rules: FormRules = {
  case_id: [
    { required: true, message: '案件编号为必填项', trigger: 'blur' },
  ],
  currency: [
    { required: true, message: '币种为必填项', trigger: 'change' },
  ],
}

onMounted(async () => {
  if (!hasObligationQuery || obligationId === null) return

  obligationLoading.value = true
  try {
    linkedObligation.value = await getFeeObligation(obligationId)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    obligationLoading.value = false
  }
})

function goBack() {
  router.push('/fees/drafts')
}

async function handleSubmit() {
  fieldErrors.value = new Map()

  if (linkedDraftBlocked.value) return

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
  if (obligationId) {
    payload.obligation_id = obligationId
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

.obligation-card {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-body);
}

.obligation-card-title {
  margin: 0 0 10px;
}

.obligation-card p {
  margin: 4px 0;
}

.obligation-block-message {
  color: var(--color-warning);
}
</style>
