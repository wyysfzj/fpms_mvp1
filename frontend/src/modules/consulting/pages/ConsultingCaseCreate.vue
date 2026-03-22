<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">顾问/检索项目立案</h1>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-card shadow="never" class="form-card">
      <template #header>
        <div class="form-card-title">创建项目</div>
      </template>

      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="项目类型" prop="case_type">
              <el-select v-model="form.case_type" placeholder="请选择项目类型">
                <el-option label="顾问项目" value="CONSULTING" />
                <el-option label="检索项目" value="SEARCH" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="案件编号" prop="case_no">
              <el-input v-model.trim="form.case_no" placeholder="请输入案件编号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="接收日期" prop="recv_date">
              <el-date-picker
                v-model="form.recv_date"
                type="date"
                placeholder="请选择接收日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                class="w-full"
              />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="客户编号" prop="client_id">
              <el-input v-model.trim="form.client_id" placeholder="请输入客户编号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="负责人编号" prop="primary_agent_id">
              <el-input v-model.trim="form.primary_agent_id" placeholder="请输入负责人编号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="8">
            <el-form-item label="项目标题（中文）" prop="title_cn">
              <el-input v-model.trim="form.title_cn" placeholder="请输入项目标题" />
            </el-form-item>
          </el-col>

          <el-col v-if="form.case_type === 'CONSULTING'" :xs="24" :sm="12" :md="12">
            <el-form-item label="咨询范围" prop="consulting_scope">
              <el-input
                v-model.trim="form.consulting_scope"
                type="textarea"
                :rows="2"
                placeholder="请输入咨询范围"
              />
            </el-form-item>
          </el-col>
          <el-col v-if="form.case_type === 'CONSULTING'" :xs="24" :sm="12" :md="12">
            <el-form-item label="预估工时" prop="estimated_hours">
              <el-input-number v-model="form.estimated_hours" :min="0.5" :step="0.5" :precision="1" class="w-full" />
            </el-form-item>
          </el-col>

          <el-col v-if="form.case_type === 'SEARCH'" :xs="24" :sm="12" :md="12">
            <el-form-item label="检索关键词" prop="search_keywords">
              <el-input
                v-model.trim="form.search_keywords"
                type="textarea"
                :rows="2"
                placeholder="请输入检索关键词"
              />
            </el-form-item>
          </el-col>
          <el-col v-if="form.case_type === 'SEARCH'" :xs="24" :sm="12" :md="12">
            <el-form-item label="检索数据库" prop="search_database">
              <el-input v-model.trim="form.search_database" placeholder="请输入检索数据库名称" />
            </el-form-item>
          </el-col>

          <el-col :span="24" class="action-row">
            <el-button @click="resetForm">重置</el-button>
            <el-button type="primary" :loading="submitting" @click="handleSubmit">创建项目</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card v-if="createdCase" shadow="never" class="result-card">
      <template #header>
        <div class="form-card-title">创建结果</div>
      </template>

      <el-descriptions :column="3" border>
        <el-descriptions-item label="案件标识">{{ createdCase.id }}</el-descriptions-item>
        <el-descriptions-item label="案件编号">{{ createdCase.case_no }}</el-descriptions-item>
        <el-descriptions-item label="项目类型">{{ caseTypeLabel(createdCase.case_type) }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ getCaseStatusText(createdCase.status) }}</el-descriptions-item>
        <el-descriptions-item label="客户编号">{{ createdCase.client_id || '—' }}</el-descriptions-item>
        <el-descriptions-item label="负责人编号">{{ createdCase.primary_agent_id || '—' }}</el-descriptions-item>
        <el-descriptions-item label="接收日期">{{ createdCase.recv_date || '—' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(createdCase.created_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { createConsultingCase } from '../../../api/consulting'
import type {
  ConsultingCase,
  ConsultingCaseCreatePayload,
  ConsultingCaseType,
} from '../../../api/consulting.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { getCaseStatusText } from '../../../constants/displayText'

const router = useRouter()
const formRef = ref<FormInstance>()
const submitting = ref(false)
const error = ref<ApiError | null>(null)
const createdCase = ref<ConsultingCase | null>(null)

const form = reactive({
  case_type: 'CONSULTING' as ConsultingCaseType,
  case_no: '',
  client_id: '',
  title_cn: '',
  primary_agent_id: '',
  recv_date: '',
  consulting_scope: '',
  estimated_hours: undefined as number | undefined,
  search_keywords: '',
  search_database: '',
})

function toApiError(errorLike: unknown): ApiError | null {
  if (!errorLike || typeof errorLike !== 'object') return null
  const candidate = errorLike as Partial<ApiError>
  if (typeof candidate.status !== 'number') return null
  if (typeof candidate.code !== 'string') return null
  if (typeof candidate.message !== 'string') return null
  return candidate as ApiError
}

function mapCreateCaseError(errorLike: unknown): string {
  const apiError = toApiError(errorLike)
  if (!apiError || apiError.status === 0) return '网络异常或服务不可用，请稍后重试。'

  if (apiError.status === 400 && apiError.code === 'CONSULTING_CASE_INVALID') {
    return '项目参数无效，请检查项目类型与必填字段。'
  }
  if (apiError.status === 409 && apiError.code === 'CASE_NO_DUPLICATE') {
    return '案件编号已存在，请更换后重试。'
  }
  if (apiError.status === 401) return '登录已失效，请重新登录后重试。'
  if (apiError.status === 403) return '无权限创建顾问/检索项目。'
  if (apiError.status === 422) return '提交数据校验失败，请检查日期和字段格式。'

  return '创建项目失败，请稍后重试。'
}

function validateSpecialFields() {
  if (form.case_type === 'CONSULTING') {
    const scope = form.consulting_scope.trim()
    if (!scope) {
      return '顾问项目必须填写咨询范围。'
    }
    if (!form.estimated_hours || form.estimated_hours <= 0) {
      return '顾问项目必须填写有效的预估工时。'
    }
  }

  if (form.case_type === 'SEARCH') {
    const keywords = form.search_keywords.trim()
    const db = form.search_database.trim()
    if (!keywords) {
      return '检索项目必须填写检索关键词。'
    }
    if (!db) {
      return '检索项目必须填写检索数据库。'
    }
  }

  return null
}

const formRules: FormRules = {
  case_type: [{ required: true, message: '项目类型为必填项', trigger: 'change' }],
  case_no: [{ required: true, message: '案件编号为必填项', trigger: 'blur' }],
  client_id: [{ required: true, message: '客户编号为必填项', trigger: 'blur' }],
  title_cn: [{ required: true, message: '项目标题为必填项', trigger: 'blur' }],
  primary_agent_id: [{ required: true, message: '负责人编号为必填项', trigger: 'blur' }],
  recv_date: [{ required: true, message: '接收日期为必填项', trigger: 'change' }],
}

function buildPayload(): ConsultingCaseCreatePayload {
  return {
    case_no: form.case_no.trim(),
    case_type: form.case_type,
    client_id: form.client_id.trim(),
    title_cn: form.title_cn.trim(),
    primary_agent_id: form.primary_agent_id.trim(),
    recv_date: form.recv_date,
  }
}

function resetForm() {
  form.case_type = 'CONSULTING'
  form.case_no = ''
  form.client_id = ''
  form.title_cn = ''
  form.primary_agent_id = ''
  form.recv_date = ''
  form.consulting_scope = ''
  form.estimated_hours = undefined
  form.search_keywords = ''
  form.search_database = ''
}

function caseTypeLabel(caseType: ConsultingCaseType): string {
  return caseType === 'CONSULTING' ? '顾问项目' : '检索项目'
}

function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  const specialFieldError = validateSpecialFields()
  if (specialFieldError) {
    ElMessage.error(specialFieldError)
    return
  }

  submitting.value = true
  error.value = null
  try {
    const created = await createConsultingCase(buildPayload())
    createdCase.value = created
    ElMessage.success('项目创建成功，正在跳转。')
    const targetPath = created.id ? `/cases/${created.id}` : '/cases'
    await router.push(targetPath)
  } catch (err) {
    error.value = toApiError(err)
    ElMessage.error(mapCreateCaseError(err))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-card,
.result-card {
  margin-top: 16px;
}

.form-card-title {
  font-weight: 600;
}

.action-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.w-full {
  width: 100%;
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
