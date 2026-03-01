<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">任务模板管理</h1>
        <span class="page-count">{{ templates.length }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="openCreate">新增模板</el-button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="templates"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="code" label="编码" width="150" />
      <el-table-column prop="name" label="名称" min-width="180" />
      <el-table-column label="加天数" width="100">
        <template #default="{ row }">{{ row.add_days ?? '—' }}</template>
      </el-table-column>
      <el-table-column label="加月数" width="100">
        <template #default="{ row }">{{ row.add_months ?? '—' }}</template>
      </el-table-column>
      <el-table-column label="内部偏移天数" width="120">
        <template #default="{ row }">{{ row.inner_offset_days ?? '—' }}</template>
      </el-table-column>
      <el-table-column label="默认角色" width="120">
        <template #default="{ row }">{{ row.default_worker_role || '—' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">
            {{ row.enabled ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button
            size="small"
            :type="row.enabled ? 'warning' : 'success'"
            @click="handleToggleEnabled(row)"
          >
            {{ row.enabled ? '停用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
      <template #empty>
        <div class="table-empty">暂无任务模板，点击"新增模板"创建。</div>
      </template>
    </el-table>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEdit ? '编辑任务模板' : '新增任务模板'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-position="top"
      >
        <el-form-item label="编码" prop="code">
          <el-input v-model.trim="form.code" :disabled="isEdit" placeholder="模板编码" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model.trim="form.name" placeholder="模板名称" />
        </el-form-item>
        <el-form-item label="加天数" prop="add_days">
          <el-input-number v-model="form.add_days" :min="0" placeholder="天数" />
        </el-form-item>
        <el-form-item label="加月数" prop="add_months">
          <el-input-number v-model="form.add_months" :min="0" placeholder="月数" />
        </el-form-item>
        <el-form-item label="内部偏移天数" prop="inner_offset_days">
          <el-input-number v-model="form.inner_offset_days" :min="0" placeholder="天数" />
        </el-form-item>
        <el-form-item label="默认角色" prop="default_worker_role">
          <el-input v-model.trim="form.default_worker_role" placeholder="例如：审查员" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="模板描述" />
        </el-form-item>
        <el-form-item v-if="isEdit" label="启用" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getTaskTemplates, createTaskTemplate, updateTaskTemplate } from '../../../api/tasks'
import type { TaskTemplate } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const templates = ref<TaskTemplate[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)

const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  code: '',
  name: '',
  add_days: undefined as number | undefined,
  add_months: undefined as number | undefined,
  inner_offset_days: undefined as number | undefined,
  default_worker_role: '',
  description: '',
  enabled: true,
})

const formRules: FormRules = {
  code: [{ required: true, message: '编码为必填项', trigger: 'blur' }],
  name: [{ required: true, message: '名称为必填项', trigger: 'blur' }],
}

async function fetchTemplates() {
  loading.value = true
  error.value = null
  try {
    templates.value = await getTaskTemplates()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.code = ''
  form.name = ''
  form.add_days = undefined
  form.add_months = undefined
  form.inner_offset_days = undefined
  form.default_worker_role = ''
  form.description = ''
  form.enabled = true
}

function openCreate() {
  resetForm()
  isEdit.value = false
  editingId.value = ''
  showDialog.value = true
}

function openEdit(row: TaskTemplate) {
  form.code = row.code
  form.name = row.name
  form.add_days = row.add_days ?? undefined
  form.add_months = row.add_months ?? undefined
  form.inner_offset_days = row.inner_offset_days ?? undefined
  form.default_worker_role = row.default_worker_role ?? ''
  form.description = row.description ?? ''
  form.enabled = row.enabled
  isEdit.value = true
  editingId.value = row.id
  showDialog.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await updateTaskTemplate(editingId.value, {
        name: form.name,
        add_days: form.add_days ?? null,
        add_months: form.add_months ?? null,
        inner_offset_days: form.inner_offset_days ?? null,
        default_worker_role: form.default_worker_role || null,
        description: form.description || null,
        enabled: form.enabled,
      })
      ElMessage.success('模板更新成功')
    } else {
      await createTaskTemplate({
        code: form.code,
        name: form.name,
        add_days: form.add_days ?? null,
        add_months: form.add_months ?? null,
        inner_offset_days: form.inner_offset_days ?? null,
        default_worker_role: form.default_worker_role || null,
        description: form.description || null,
      })
      ElMessage.success('模板创建成功')
    }
    showDialog.value = false
    resetForm()
    fetchTemplates()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(apiError.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleToggleEnabled(row: TaskTemplate) {
  try {
    await updateTaskTemplate(row.id, { enabled: !row.enabled })
    ElMessage.success(row.enabled ? '已停用' : '已启用')
    fetchTemplates()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(apiError.message || '操作失败')
  }
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.table-empty {
  padding: 32px 0;
  color: var(--text-sub);
}
</style>
