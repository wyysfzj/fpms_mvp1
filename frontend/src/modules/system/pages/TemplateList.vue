<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">模板管理</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="openUploadDialog">
          上传模板
        </el-button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <LoadingBlock v-if="loading" :rows="10" />

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无模板"
        message="上传模板后可在此管理。"
        icon="📄"
        cta-label="上传模板"
        @cta="openUploadDialog"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="templates"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="code" label="编码" width="180">
          <template #default="{ row }">
            <span class="template-code">{{ row.code }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="file_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.file_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="{ row }">
            {{ row.description || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button
              type="danger"
              text
              size="small"
              @click.stop="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" />
    </div>

    <!-- Upload Dialog -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传模板"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      @open="handleUploadDialogOpen"
      @close="resetUploadForm"
      @closed="restoreUploadTriggerFocus"
    >
      <div v-if="uploadError" class="dialog-error">
        <ApiErrorBanner :error="uploadError" @dismiss="uploadError = null" />
      </div>

      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-position="top"
      >
        <el-form-item label="编码" prop="code" :error="fieldErrors.get('code')?.join(', ')">
          <el-input
            ref="uploadCodeInputRef"
            v-model.trim="uploadForm.code"
            placeholder="例如：BILL_TEMPLATE_1"
          />
        </el-form-item>

        <el-form-item label="名称" prop="name" :error="fieldErrors.get('name')?.join(', ')">
          <el-input
            v-model.trim="uploadForm.name"
            placeholder="模板显示名称"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="2"
            placeholder="可选描述"
          />
        </el-form-item>

        <el-form-item label="模板文件" prop="file" :error="fieldErrors.get('file')?.join(', ')">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".docx,.xlsx,.html"
          >
            <el-button>选择文件</el-button>
            <template #tip>
              <div class="upload-tip">支持格式：.docx、.xlsx、.html</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules, InputInstance, UploadFile, UploadInstance } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTemplates, uploadTemplate, deleteTemplate } from '../../../api/system'
import type { TemplateListItem } from '../../../api/system.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const templates = ref<TemplateListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

// Upload dialog state
const showUploadDialog = ref(false)
const uploading = ref(false)
const uploadError = ref<ApiError | null>(null)
const uploadFormRef = ref<FormInstance>()
const uploadCodeInputRef = ref<InputInstance>()
const uploadRef = ref<UploadInstance>()
const fieldErrors = ref<Map<string, string[]>>(new Map())
const selectedFile = ref<File | null>(null)
const lastFocusedElement = ref<HTMLElement | null>(null)

const uploadForm = reactive({
  code: '',
  name: '',
  description: '',
})

const uploadRules: FormRules = {
  code: [
    { required: true, message: '编码为必填项', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '名称为必填项', trigger: 'blur' },
  ],
}

async function fetchTemplates() {
  loading.value = true
  error.value = null
  try {
    const result = await getTemplates({ page: page.value, page_size: pageSize.value })
    templates.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

function handleFileChange(file: UploadFile) {
  selectedFile.value = file.raw || null
}

function handleFileRemove() {
  selectedFile.value = null
}

function openUploadDialog() {
  lastFocusedElement.value = document.activeElement instanceof HTMLElement
    ? document.activeElement
    : null
  showUploadDialog.value = true
}

async function handleUploadDialogOpen() {
  await nextTick()
  uploadCodeInputRef.value?.focus?.()
}

function restoreUploadTriggerFocus() {
  lastFocusedElement.value?.focus()
  lastFocusedElement.value = null
}

function resetUploadForm() {
  uploadForm.code = ''
  uploadForm.name = ''
  uploadForm.description = ''
  selectedFile.value = null
  uploadError.value = null
  fieldErrors.value = new Map()
  uploadRef.value?.clearFiles()
}

async function handleUpload() {
  fieldErrors.value = new Map()

  const valid = await uploadFormRef.value?.validate().catch(() => false)
  if (!valid) return

  if (!selectedFile.value) {
    fieldErrors.value.set('file', ['请选择文件'])
    return
  }

  uploading.value = true
  uploadError.value = null

  try {
    // Determine file type from extension
    const fileName = selectedFile.value.name
    const ext = fileName.split('.').pop()?.toLowerCase() || 'docx'

    await uploadTemplate({
      code: uploadForm.code,
      name: uploadForm.name,
      file_type: ext,
      description: uploadForm.description || undefined,
      file: selectedFile.value,
    })

    ElMessage.success('模板上传成功')
    showUploadDialog.value = false
    resetUploadForm()
    fetchTemplates()
  } catch (err) {
    const apiError = err as ApiError
    uploadError.value = apiError

    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    uploading.value = false
  }
}

async function handleDelete(template: TemplateListItem) {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板“${template.name}”吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteTemplate(template.id)
    ElMessage.success('模板删除成功')
    fetchTemplates()
  } catch (err) {
    if (err !== 'cancel') {
      error.value = err as ApiError
    }
  }
}

watch([page, pageSize], () => {
  fetchTemplates()
})

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.template-code {
  font-family: var(--font-mono);
  font-weight: 500;
}

.upload-tip {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
}

.dialog-error {
  margin-bottom: 16px;
}
</style>
