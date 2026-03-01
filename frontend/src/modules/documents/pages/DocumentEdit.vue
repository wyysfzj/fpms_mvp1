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
                <el-input v-model="form.doc_type" placeholder="例如：审查意见通知书、答复文件" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
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
            <el-col :span="12">
              <el-form-item label="案件编号" prop="case_id" :error="fieldErrors.get('case_id')?.join(', ')">
                <el-input
                  v-model.trim="form.case_id"
                  placeholder="请输入关联案件编号"
                  class="full-width"
                />
              </el-form-item>
            </el-col>
          </el-row>
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
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getDocument, updateDocument } from '../../../api/documents'
import type { Document, DocumentUpdatePayload } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const error = ref<ApiError | null>(null)
const docData = ref<Document | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const form = reactive<DocumentUpdatePayload>({
  title: '',
  direction: undefined,
  case_id: '',
  doc_date: '',
  doc_type: '',
  description: '',
})

const rules: FormRules = {
  title: [
    { required: true, message: '标题为必填项', trigger: 'blur' },
    { max: 500, message: '标题不能超过 500 个字符', trigger: 'blur' },
  ],
  direction: [
    { required: true, message: '方向为必填项', trigger: 'change' },
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
    form.doc_date = docData.value.doc_date || ''
    form.doc_type = docData.value.doc_type || ''
    form.description = docData.value.description || ''
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
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
    await updateDocument(id, form)
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

function handleCancel() {
  const id = route.params.id
  router.push(`/documents/${id}`)
}

onMounted(() => {
  fetchDocument()
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
</style>
