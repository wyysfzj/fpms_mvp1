<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">登记往来文件</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" :disabled="isCaseContextUnavailable" @click="handleSave">
          登记往来文件
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="activeError" class="page-error">
      <ApiErrorBanner :error="activeError" @dismiss="handleDismissError" />
    </div>

    <!-- Form -->
    <div class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="document-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">往来文件信息</h3>
          
          <el-form-item label="标题" prop="title" :error="fieldErrors.get('title')?.join(', ')">
            <el-input v-model="form.title" placeholder="请输入文件标题" />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="方向" prop="direction" :error="fieldErrors.get('direction')?.join(', ')">
                <el-radio-group v-model="form.direction">
                  <el-radio-button value="IN">
                    <span class="direction-label direction-in">收文</span>
                  </el-radio-button>
                  <el-radio-button value="OUT">
                    <span class="direction-label direction-out">发文</span>
                  </el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="文件日期" prop="doc_date" :error="fieldErrors.get('doc_date')?.join(', ')">
                <el-date-picker
                  v-model="form.doc_date"
                  type="date"
                  placeholder="请选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  class="full-width"
                />
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
                  @change="onTemplateChange"
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
              <el-form-item label="回复来源文件">
                <el-select
                  v-model="form.reply_to_id"
                  placeholder="选择回复来源文件（可选）"
                  clearable
                  filterable
                  style="width: 100%"
                  :disabled="!form.case_id"
                >
                  <el-option
                    v-for="d in caseDocuments"
                    :key="d.id"
                    :label="`${d.title} (${d.direction === 'IN' ? '收文' : '发文'})`"
                    :value="d.id"
                  />
                </el-select>
                <div v-if="!form.case_id" class="field-hint">
                  请先选择案件
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                v-if="hasLockedCaseContext"
                label="所属案件"
                prop="case_id"
                :error="fieldErrors.get('case_id')?.join(', ')"
              >
                <el-input
                  :model-value="lockedCaseNo"
                  readonly
                  class="full-width"
                  placeholder="案件编号已自动带入"
                />
                <div class="field-hint">
                  该案件已从案件详情页带入，当前流程不可修改
                </div>
              </el-form-item>
              <el-form-item v-else label="案件编号" prop="case_id" :error="fieldErrors.get('case_id')?.join(', ')">
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
            <el-col :span="12">
              <el-form-item label="文件类型" prop="doc_type" :error="fieldErrors.get('doc_type')?.join(', ')">
                <el-select v-model="form.doc_type" placeholder="请选择文件类型" style="width: 100%">
                  <el-option label="官方来文" value="OFFICIAL_IN" />
                  <el-option label="官方去文" value="OFFICIAL_OUT" />
                  <el-option label="客户来文" value="CLIENT_IN" />
                  <el-option label="致函客户" value="CLIENT_OUT" />
                </el-select>
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

          <el-form-item label="描述" prop="description" :error="fieldErrors.get('description')?.join(', ')">
            <el-input 
              v-model="form.description" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入文件说明" 
            />
          </el-form-item>
        </div>

        <div class="form-section document-impact-section">
          <h3 class="form-section-title">来源文件与影响预览</h3>
          <div class="document-impact-grid">
            <section class="document-impact-card">
              <h4 class="document-impact-title">来源文件</h4>
              <div class="source-file-zone">
                <div>
                  <strong>上传或选择已核验来源文件</strong>
                  <span>官方来文没有来源文件时，不应触发状态、期限或费用影响。</span>
                </div>
                <el-button type="primary" size="small" disabled>选择来源文件</el-button>
              </div>
              <el-descriptions :column="1" size="small" border>
                <el-descriptions-item
                  v-for="item in sourceFilePreviewRows"
                  :key="item.label"
                  :label="item.label"
                >
                  <el-tag v-if="item.tagType" :type="item.tagType" size="small">{{ item.value }}</el-tag>
                  <span v-else>{{ item.value }}</span>
                </el-descriptions-item>
              </el-descriptions>
            </section>

            <section class="document-impact-card">
              <h4 class="document-impact-title">影响预览</h4>
              <el-skeleton v-if="impactPreviewLoading" :rows="4" animated />
              <el-alert
                v-else-if="impactPreviewError"
                type="error"
                :closable="false"
                title="影响预览加载失败"
                :description="impactPreviewError.message"
                show-icon
              />
              <el-empty
                v-else-if="!impactPreviewRows.length"
                description="请选择案件并填写标题后查看影响预览"
                :image-size="72"
              />
              <el-table v-else :data="impactPreviewRows" size="small" class="impact-preview-table">
                <el-table-column prop="impactType" label="影响类型" min-width="120" />
                <el-table-column prop="result" label="预览结果" min-width="220" />
                <el-table-column label="确认要求" min-width="130">
                  <template #default="{ row }">
                    <el-tag :type="row.tagType" size="small">{{ row.confirmation }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="risk" label="风险提示" min-width="180" />
              </el-table>
            </section>
          </div>

          <el-alert
            v-if="impactPreview?.confirmation_required"
            class="impact-warning"
            type="warning"
            :closable="false"
            title="确认警示"
            :description="confirmationDescription"
            show-icon
          />
          <el-alert
            v-if="impactPreview?.risk_tips.length"
            class="impact-warning"
            type="error"
            :closable="false"
            title="风险提示"
            :description="impactPreview.risk_tips.join('；')"
            show-icon
          />
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getCase, getCases } from '../../../api/cases'
import type { Case } from '../../../api/cases.types'
import { createDocument, getDocTemplates, getDocuments, previewDocumentImpact } from '../../../api/documents'
import type { DocumentCreatePayload, DocumentImpactItem, DocumentImpactPreviewResult } from '../../../api/documents.types'
import type { DocTemplate, Document as Doc } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { getCaseStatusText, getFeeDraftTypeText } from '../../../constants/displayText'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const caseContextError = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const lockedCaseNo = ref('')
const hasLockedCaseContext = ref(false)
const caseContextReady = ref(false)
const caseOptionsLoading = ref(false)
const caseOptions = ref<Case[]>([])
const impactPreview = ref<DocumentImpactPreviewResult | null>(null)
const impactPreviewLoading = ref(false)
const impactPreviewError = ref<ApiError | null>(null)

const form = reactive<DocumentCreatePayload>({
  title: '',
  direction: 'IN',
  case_id: '',
  doc_date: new Date().toISOString().split('T')[0],
  doc_type: undefined,
  description: '',
  doc_template_id: null as string | null,
  reply_to_id: null as string | null,
})

// FC2: Template and reply chain
const docTemplates = ref<DocTemplate[]>([])
const caseDocuments = ref<Doc[]>([])
const selectedTemplate = ref<DocTemplate | null>(null)

const filteredTemplates = computed(() =>
  docTemplates.value.filter(t => t.direction === form.direction)
)
const activeError = computed(() => caseContextError.value ?? error.value)
const isCaseContextUnavailable = computed(() => hasLockedCaseContext.value && !caseContextReady.value)
const selectedReplyDocument = computed(() =>
  caseDocuments.value.find((document) => document.id === form.reply_to_id) || null
)
const sourceFilePreviewRows = computed(() => [
  {
    label: '来源文件',
    value: selectedReplyDocument.value?.title || '未选择来源文件',
    tagType: selectedReplyDocument.value ? 'success' : '',
  },
  {
    label: '所属案件',
    value: impactPreview.value?.case_no || lockedCaseNo.value || '待选择案件',
    tagType: '',
  },
  {
    label: '模板代码',
    value: impactPreview.value?.template_code || selectedTemplate.value?.code || '未选择模板',
    tagType: '',
  },
  {
    label: '文件状态影响',
    value: impactPreview.value?.file_status_impacts.length
      ? impactPreview.value.file_status_impacts.map((item) => item.title).join('；')
      : '暂无文件状态影响',
    tagType: impactPreview.value?.file_status_impacts.length ? 'warning' : 'info',
  },
])
const impactPreviewRows = computed(() => {
  if (!impactPreview.value) return []
  const groups = [
    { label: '状态影响', items: impactPreview.value.status_impacts },
    { label: '期限与任务影响', items: impactPreview.value.deadline_impacts },
    { label: '任务影响', items: impactPreview.value.task_impacts },
    { label: '费用影响', items: impactPreview.value.fee_impacts },
    { label: '文件状态影响', items: impactPreview.value.file_status_impacts },
  ]

  return groups.flatMap((group) =>
    group.items.map((item) => ({
      impactType: group.label,
      result: formatImpactItem(item),
      confirmation: item.requires_confirmation ? '需要确认' : '自动记录',
      risk: item.detail || '无额外风险提示',
      tagType: impactTagType(item),
    }))
  )
})
const confirmationDescription = computed(() =>
  impactPreview.value?.confirmation_items.length
    ? impactPreview.value.confirmation_items.join('；')
    : '登记前请确认本次影响预览。'
)

function formatImpactItem(item: DocumentImpactItem) {
  const effect = item.effect ? `：${item.effect}` : ''
  const detail = item.detail ? `；${item.detail}` : ''
  return `${item.title}${effect}${detail}`
}

function impactTagType(item: DocumentImpactItem): 'success' | 'warning' | 'info' {
  if (!item.enabled) return 'info'
  if (item.requires_confirmation) return 'warning'
  return 'success'
}

function getQueryParam(value: unknown): string {
  if (Array.isArray(value)) {
    return typeof value[0] === 'string' ? value[0].trim() : ''
  }
  return typeof value === 'string' ? value.trim() : ''
}

function onTemplateChange(templateId: string | null) {
  if (!templateId) {
    selectedTemplate.value = null
    return
  }
  const tmpl = docTemplates.value.find(t => t.id === templateId)
  if (tmpl) {
    form.direction = tmpl.direction
    selectedTemplate.value = tmpl
  }
}

let impactPreviewRequestSeq = 0

async function fetchImpactPreview() {
  if (!form.case_id || !form.title.trim() || !form.doc_date || !form.direction) {
    impactPreview.value = null
    impactPreviewError.value = null
    impactPreviewLoading.value = false
    return
  }

  const requestSeq = ++impactPreviewRequestSeq
  impactPreviewLoading.value = true
  impactPreviewError.value = null

  try {
    const result = await previewDocumentImpact({
      case_id: form.case_id,
      doc_template_id: form.doc_template_id || null,
      doc_type: form.doc_type,
      direction: form.direction,
      doc_date: form.doc_date,
      title: form.title.trim(),
      extra_data: form.description?.trim() || null,
      reply_to_id: form.reply_to_id || null,
    })
    if (requestSeq !== impactPreviewRequestSeq) return
    impactPreview.value = result
  } catch (err) {
    if (requestSeq !== impactPreviewRequestSeq) return
    impactPreview.value = null
    impactPreviewError.value = err as ApiError
  } finally {
    if (requestSeq === impactPreviewRequestSeq) {
      impactPreviewLoading.value = false
    }
  }
}

watch(() => form.case_id, async (newCaseId) => {
  form.reply_to_id = null
  if (!newCaseId) {
    caseDocuments.value = []
    return
  }
  try {
    const result = await getDocuments({ case_id: newCaseId, page_size: 100 })
    caseDocuments.value = result.items
  } catch {
    // Silently fail
  }
})

watch(
  () => [
    form.case_id,
    form.doc_template_id,
    form.doc_type,
    form.direction,
    form.doc_date,
    form.title,
    form.description,
    form.reply_to_id,
  ],
  () => {
    void fetchImpactPreview()
  },
  { immediate: true }
)

async function initializeCaseContext() {
  const routeCaseId = getQueryParam(route.query.case_id)
  const routeCaseNo = getQueryParam(route.query.case_no)

  if (!routeCaseId) {
    hasLockedCaseContext.value = false
    caseContextReady.value = true
    caseContextError.value = null
    return
  }

  form.case_id = routeCaseId
  lockedCaseNo.value = routeCaseNo
  hasLockedCaseContext.value = true

  try {
    const caseData = await getCase(routeCaseId)
    lockedCaseNo.value = caseData.case_no || lockedCaseNo.value
    caseContextReady.value = true
    caseContextError.value = null
  } catch {
    form.case_id = ''
    caseContextReady.value = false
    caseContextError.value = {
      status: 404,
      code: 'CASE_CONTEXT_INVALID',
      message: '关联案件不存在或已失效，请返回案件详情页后重新登记往来文件。',
    }
  }
}

function formatCaseOption(caseItem: Case): string {
  const title = caseItem.title ? ` · ${caseItem.title}` : ''
  const client = caseItem.client_name ? ` · ${caseItem.client_name}` : ''
  return `${caseItem.case_no}${title}${client}`
}

async function fetchCaseOptions(): Promise<void> {
  caseOptionsLoading.value = true
  try {
    const result = await getCases({ page: 1, page_size: 100 })
    caseOptions.value = result.items
  } catch (err) {
    error.value = err as ApiError
  } finally {
    caseOptionsLoading.value = false
  }
}

onMounted(async () => {
  await initializeCaseContext()
  if (!hasLockedCaseContext.value) {
    await fetchCaseOptions()
  }

  try {
    const result = await getDocTemplates({ enabled: true, page_size: 100 })
    docTemplates.value = result.items
  } catch {
    // Silently fail
  }
})

const rules: FormRules = {
  title: [
    { required: true, message: '标题为必填项', trigger: 'blur' },
  ],
  direction: [
    { required: true, message: '方向为必填项', trigger: 'change' },
  ],
  case_id: [
    { required: true, message: '请选择案件', trigger: 'change' },
  ],
  doc_date: [
    { required: true, message: '文件日期为必填项', trigger: 'change' },
  ],
  doc_type: [
    { required: true, message: '文件类型为必填项', trigger: 'change' },
  ],
}

async function handleSave() {
  if (isCaseContextUnavailable.value) {
    if (!caseContextError.value) {
      caseContextError.value = {
        status: 400,
        code: 'CASE_CONTEXT_REQUIRED',
        message: '未找到有效案件，当前无法登记往来文件。',
      }
    }
    return
  }

  fieldErrors.value = new Map()
  
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  error.value = null
  
  try {
    // Build payload, omitting empty optional fields
    const payload: DocumentCreatePayload = {
      title: form.title,
      direction: form.direction,
      case_id: form.case_id,
      doc_date: form.doc_date,
    }
    if (form.doc_type) payload.doc_type = form.doc_type
    if (form.description) payload.description = form.description
    if (form.doc_template_id) payload.doc_template_id = form.doc_template_id
    if (form.reply_to_id) payload.reply_to_id = form.reply_to_id

    await createDocument(payload)
    ElMessage.success('往来文件登记成功')
    router.push('/documents')
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

function handleDismissError() {
  if (caseContextError.value) {
    caseContextError.value = null
    return
  }
  error.value = null
}

function handleCancel() {
  router.push('/documents')
}
</script>

<style scoped>
.full-width {
  width: 100%;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
}

.field-hint a {
  color: var(--color-primary);
}

.direction-label {
  font-weight: 600;
}

.direction-in {
  color: #10B981;
}

.direction-out {
  color: #F59E0B;
}

.document-form .el-form-item {
  margin-bottom: 20px;
}

.document-form .el-form-item__label {
  font-weight: 500;
  color: var(--text-main);
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
  color: var(--el-text-color-primary);
}

.template-hints-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.document-impact-section {
  margin-top: 8px;
}

.document-impact-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.85fr) minmax(0, 1.15fr);
  gap: 16px;
}

.document-impact-card {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 16px;
}

.document-impact-title {
  margin: 0 0 12px;
  color: var(--text-main);
  font-size: 15px;
  font-weight: 600;
}

.source-file-zone {
  align-items: center;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 14px;
  padding: 14px;
}

.source-file-zone div {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.source-file-zone strong {
  color: var(--text-main);
  font-size: 14px;
}

.source-file-zone span {
  color: var(--text-sub);
  font-size: 12px;
  line-height: 1.5;
}

.source-file-zone .el-button {
  flex: 0 0 auto;
}

.impact-preview-table {
  width: 100%;
}

.impact-warning {
  margin-top: 14px;
}

@media (max-width: 1100px) {
  .document-impact-grid {
    grid-template-columns: 1fr;
  }

  .source-file-zone {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
