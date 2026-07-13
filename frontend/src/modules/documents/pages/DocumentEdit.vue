<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">编辑文档</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存修改
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Form -->
    <div v-else class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="document-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">文档信息</h3>

          <el-form-item label="标题" prop="title" :error="fieldErrors.get('title')?.join(', ')">
            <el-input v-model="form.title" placeholder="请输入文档标题" />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="方向" prop="direction" :error="fieldErrors.get('direction')?.join(', ')">
                <el-select v-model="form.direction" placeholder="请选择方向" style="width: 100%">
                  <el-option label="收文" value="IN" />
                  <el-option label="发文" value="OUT" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="文档类型" prop="doc_type" :error="fieldErrors.get('doc_type')?.join(', ')">
                <el-select v-model="form.doc_type" placeholder="请选择文件类型" style="width: 100%">
                  <el-option label="官方来文" value="OFFICIAL_IN" />
                  <el-option label="官方去文" value="OFFICIAL_OUT" />
                  <el-option label="客户来文" value="CLIENT_IN" />
                  <el-option label="致函客户" value="CLIENT_OUT" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="文件模板">
                <el-select
                  v-model="form.doc_template_id"
                  placeholder="选择模板（可选）"
                  clearable
                  filterable
                  style="width: 100%"
                >
                  <el-option
                    v-for="t in filteredTemplates"
                    :key="t.id"
                    :label="`${t.code} — ${t.name}`"
                    :value="t.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="文档日期" prop="doc_date" :error="fieldErrors.get('doc_date')?.join(', ')">
                <el-date-picker
                  v-model="form.doc_date"
                  type="date"
                  placeholder="请选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="案件编号" prop="case_id" :error="fieldErrors.get('case_id')?.join(', ')">
                <el-select
                  v-model="form.case_id"
                  filterable
                  clearable
                  :loading="caseOptionsLoading"
                  placeholder="请选择案件"
                  class="full-width"
                >
                  <el-option
                    v-for="caseItem in caseOptions"
                    :key="caseItem.id"
                    :label="formatCaseOption(caseItem)"
                    :value="caseItem.id"
                  />
                </el-select>
                <div class="field-hint">
                  <router-link to="/cases">查看案件列表</router-link> 以确认案卷号
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <div v-if="selectedTemplate" class="template-hints">
            <div class="template-hints-title">模板规则提示</div>
            <div class="template-hints-list">
              <el-tag v-if="selectedTemplate.need_reply" type="warning" size="small">需要回复</el-tag>
              <el-tag v-if="selectedTemplate.deadline_template_code" type="danger" size="small">
                自动建期限：{{ selectedTemplate.deadline_template_code }}
              </el-tag>
              <el-tag v-if="selectedTemplate.fee_draft_type" type="success" size="small">
                自动建费用草稿：{{ getFeeDraftTypeText(selectedTemplate.fee_draft_type) }}
              </el-tag>
              <el-tag v-if="selectedTemplate.status_effect" type="info" size="small">
                状态变更：{{ getCaseStatusText(selectedTemplate.status_effect) }}
              </el-tag>
              <el-tag v-if="selectedTemplate.reply_to_template_code" type="info" size="small">
                回复模板：{{ selectedTemplate.reply_to_template_code }}
              </el-tag>
            </div>
          </div>

          <div class="deadline-lineage-card">
            <div class="deadline-lineage-title">官方截止日来源记录</div>
            <el-descriptions :column="3" border size="small">
              <el-descriptions-item label="官方截止日">
                {{ form.official_due_date || '未记录' }}
              </el-descriptions-item>
              <el-descriptions-item label="截止日来源">
                {{ deadlineSourceLabel }}
              </el-descriptions-item>
              <el-descriptions-item label="确认状态">
                <el-tag :type="deadlineStatusTagType" size="small">{{ deadlineStatusLabel }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <el-row :gutter="20" class="deadline-confirm-fields">
              <el-col :span="12">
                <el-form-item label="官方截止日">
                  <el-date-picker
                    v-model="form.official_due_date"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    placeholder="请选择官方截止日"
                    :disabled="deadlineDateReadOnly"
                    clearable
                    class="full-width"
                    @change="clearDeadlineConfirmationRequest"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="截止日来源">
                  <el-select
                    v-model="form.official_due_date_source"
                    placeholder="请选择截止日来源"
                    :disabled="isDeadlineConfirmed"
                    clearable
                    class="full-width"
                    @change="clearDeadlineConfirmationRequest"
                  >
                    <el-option label="人工核对官方通知" value="MANUAL_OFFICIAL_NOTICE" />
                    <el-option label="从官方通知导入" value="IMPORTED_OFFICIAL_NOTICE" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-alert
              :type="isDeadlineConfirmed ? 'success' : 'info'"
              :closable="false"
              :title="deadlineReadOnlyReason"
              show-icon
            />
            <div v-if="!isDeadlineConfirmed" class="deadline-confirm-actions">
              <el-button
                type="primary"
                :disabled="!canConfirmDeadline"
                @click="confirmOfficialDeadline"
              >
                确认官方截止日
              </el-button>
              <span v-if="deadlineConfirmationRequested" class="deadline-confirmed-hint">
                已标记为待保存的确认信息
              </span>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">内容</h3>

          <el-form-item prop="description" :error="fieldErrors.get('description')?.join(', ')">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="8"
              placeholder="请输入文档内容或说明"
            />
          </el-form-item>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getCase, getCases } from '../../../api/cases'
import type { Case } from '../../../api/cases.types'
import { getDocument, getDocTemplates, updateDocument } from '../../../api/documents'
import type { DocTemplate, Document, DocumentUpdatePayload } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { getCaseStatusText, getFeeDraftTypeText } from '../../../constants/displayText'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const error = ref<ApiError | null>(null)
const docData = ref<Document | null>(null)
const docTemplates = ref<DocTemplate[]>([])
const fieldErrors = ref<Map<string, string[]>>(new Map())
const caseOptionsLoading = ref(false)
const caseOptions = ref<Case[]>([])
const deadlineConfirmationRequested = ref(false)

interface DocumentEditForm extends Omit<DocumentUpdatePayload, 'official_due_date_status'> {
  official_due_date_status?: 'CONFIRMED' | 'NEEDS_CONFIRMATION' | 'LEGACY_UNVERIFIED' | null
}

const form = reactive<DocumentEditForm>({
  title: '',
  direction: undefined,
  case_id: '',
  doc_template_id: null,
  doc_date: '',
  doc_type: undefined,
  description: '',
  official_due_date: null,
  official_due_date_source: null,
  official_due_date_status: null,
})
const filteredTemplates = computed(() =>
  docTemplates.value.filter((t) => !form.direction || t.direction === form.direction)
)
const selectedTemplate = computed(
  () => docTemplates.value.find((t) => t.id === form.doc_template_id) || null
)
const isDeadlineConfirmed = computed(() => docData.value?.official_due_date_status === 'CONFIRMED')
const isLegacyDeadline = computed(
  () => docData.value?.official_due_date_status === 'LEGACY_UNVERIFIED'
)
const deadlineDateReadOnly = computed(
  () => isDeadlineConfirmed.value || Boolean(docData.value?.official_due_date)
)
const canConfirmDeadline = computed(
  () => Boolean(form.official_due_date && form.official_due_date_source)
)
const deadlineSourceLabel = computed(() => {
  if (form.official_due_date_source === 'MANUAL_OFFICIAL_NOTICE') return '人工核对官方通知'
  if (form.official_due_date_source === 'IMPORTED_OFFICIAL_NOTICE') return '从官方通知导入'
  return '未记录'
})
const deadlineStatusLabel = computed(() => {
  if (isDeadlineConfirmed.value) return '已确认'
  if (deadlineConfirmationRequested.value) return '待保存确认'
  if (isLegacyDeadline.value) return '历史待确认'
  if (docData.value?.official_due_date_status === 'NEEDS_CONFIRMATION') return '待确认'
  return '未记录'
})
const deadlineStatusTagType = computed<'success' | 'warning' | 'info'>(() => {
  if (isDeadlineConfirmed.value) return 'success'
  if (isLegacyDeadline.value || deadlineConfirmationRequested.value) return 'warning'
  return 'info'
})
const deadlineReadOnlyReason = computed(() => {
  if (isDeadlineConfirmed.value) {
    return '已确认的官方截止日保持只读；本页面不提供覆盖或改期操作。'
  }
  if (isLegacyDeadline.value) {
    return '历史截止日只能按原日期确认，请选择来源后保存。'
  }
  return '当前未确认官方截止日，请填写日期和来源后执行确认。'
})

const rules: FormRules = {
  title: [
    { required: true, message: '标题为必填项', trigger: 'blur' },
    { max: 500, message: '标题不能超过 500 个字符', trigger: 'blur' },
  ],
  direction: [
    { required: true, message: '方向为必填项', trigger: 'change' },
  ],
  doc_type: [
    { required: true, message: '文件类型为必填项', trigger: 'change' },
  ],
}

async function fetchDocument() {
  const id = String(route.params.id || '').trim()
  if (!id) {
    return
  }

  loading.value = true
  error.value = null

  try {
    docData.value = await getDocument(id)
    // Populate form with existing data
    form.title = docData.value.title || ''
    form.direction = docData.value.direction
    form.case_id = docData.value.case_id || ''
    form.doc_template_id = docData.value.doc_template_id || null
    form.doc_date = docData.value.doc_date || ''
    form.doc_type = docData.value.doc_type || undefined
    form.description = docData.value.description || ''
    form.official_due_date = docData.value.official_due_date || null
    form.official_due_date_source = docData.value.official_due_date_source || null
    form.official_due_date_status = docData.value.official_due_date_status || null
    deadlineConfirmationRequested.value = false
    await ensureCurrentCaseOption(form.case_id)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
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
    await ensureCurrentCaseOption(form.case_id)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    caseOptionsLoading.value = false
  }
}

async function ensureCurrentCaseOption(caseId?: string): Promise<void> {
  if (!caseId || caseOptions.value.some((caseItem) => caseItem.id === caseId)) {
    return
  }
  try {
    const caseItem = await getCase(caseId)
    caseOptions.value = [caseItem, ...caseOptions.value]
  } catch {
    // Keep the saved case id in the form; backend validation handles stale references.
  }
}

async function handleSave() {
  const id = String(route.params.id || '').trim()
  if (!id) return

  // Clear previous field errors
  fieldErrors.value = new Map()

  // Validate form
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    const payload: DocumentUpdatePayload = {
      title: form.title,
      direction: form.direction,
      case_id: form.case_id,
      doc_template_id: form.doc_template_id,
      doc_date: form.doc_date,
      doc_type: form.doc_type,
      description: form.description,
    }
    if (deadlineConfirmationRequested.value) {
      payload.official_due_date = form.official_due_date
      payload.official_due_date_source = form.official_due_date_source
      payload.official_due_date_status = 'CONFIRMED'
    }
    await updateDocument(id, payload)
    ElMessage.success('文档更新成功')
    router.push(`/documents/${id}`)
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    // Map 422 field errors
    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    saving.value = false
  }
}

function clearDeadlineConfirmationRequest() {
  deadlineConfirmationRequested.value = false
  if (!isDeadlineConfirmed.value) {
    form.official_due_date_status = docData.value?.official_due_date_status || null
  }
}

function confirmOfficialDeadline() {
  if (!canConfirmDeadline.value || isDeadlineConfirmed.value) return
  deadlineConfirmationRequested.value = true
  form.official_due_date_status = 'CONFIRMED'
}

function handleCancel() {
  const id = route.params.id
  router.push(`/documents/${id}`)
}

onMounted(() => {
  fetchDocument()
  fetchCaseOptions()
  getDocTemplates({ enabled: true, page_size: 100 })
    .then((result) => {
      docTemplates.value = result.items
    })
    .catch(() => {
      // Silently ignore
    })
})
</script>

<style scoped>
.document-form .el-form-item {
  margin-bottom: 20px;
}

.document-form .el-form-item__label {
  font-weight: 500;
}

.full-width {
  width: 100%;
}

.template-hints {
  margin-bottom: 20px;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-fill-color-light);
}

.template-hints-title {
  margin-bottom: 8px;
  font-weight: 600;
}

.template-hints-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.deadline-lineage-card {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-fill-color-lighter);
}

.deadline-lineage-title {
  margin-bottom: 12px;
  font-weight: 600;
}

.deadline-confirm-fields {
  margin-top: 16px;
}

.deadline-confirm-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.deadline-confirmed-hint {
  color: var(--el-color-success);
  font-size: 13px;
}
</style>
