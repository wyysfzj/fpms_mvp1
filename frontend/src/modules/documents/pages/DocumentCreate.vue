<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">新建文档</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          创建文档
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
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
          <h3 class="form-section-title">文档信息</h3>
          
          <el-form-item label="标题" prop="title" :error="fieldErrors.get('title')?.join(', ')">
            <el-input v-model="form.title" placeholder="请输入文档标题" />
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
              <el-form-item label="文档日期" prop="doc_date" :error="fieldErrors.get('doc_date')?.join(', ')">
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
              <el-form-item label="文档模板">
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
                <div v-if="selectedTemplate?.need_reply" class="field-hint">
                  <el-tag type="warning" size="small">需要回复</el-tag>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="回复来源文档">
                <el-select
                  v-model="form.reply_to_id"
                  placeholder="选择回复的文档（可选）"
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
                  请先填写案件编号
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="案件编号" prop="case_id" :error="fieldErrors.get('case_id')?.join(', ')">
                <el-input
                  v-model.trim="form.case_id"
                  placeholder="请输入案件编号"
                  class="full-width"
                />
                <div class="field-hint">
                  <router-link to="/cases">查看案件列表</router-link> 以获取正确编号
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="文档类型" prop="doc_type" :error="fieldErrors.get('doc_type')?.join(', ')">
                <el-input v-model="form.doc_type" placeholder="例如：审查意见通知书、答复文件" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="描述" prop="description" :error="fieldErrors.get('description')?.join(', ')">
            <el-input 
              v-model="form.description" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入文档描述" 
            />
          </el-form-item>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createDocument, getDocTemplates, getDocuments } from '../../../api/documents'
import type { DocumentCreatePayload } from '../../../api/documents.types'
import type { DocTemplate, Document as Doc } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const form = reactive<DocumentCreatePayload>({
  title: '',
  direction: 'IN',
  case_id: '',
  doc_date: new Date().toISOString().split('T')[0],
  doc_type: '',
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

watch(() => form.case_id, async (newCaseId) => {
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

onMounted(async () => {
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
    { required: true, message: '案件编号为必填项', trigger: 'blur' },
  ],
  doc_date: [
    { required: true, message: '文档日期为必填项', trigger: 'change' },
  ],
}

async function handleSave() {
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
    ElMessage.success('文档创建成功')
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
</style>
