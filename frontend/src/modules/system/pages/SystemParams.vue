<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">系统参数</h1>
        <span class="page-count">{{ params.length }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button @click="fetchParams" :loading="loading">刷新</el-button>
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
        title="暂无参数配置"
        message="系统参数配置后会显示在这里。"
        icon="⚙"
      />
    </div>

    <!-- Table with Inline Edit -->
    <div v-else class="page-table">
      <el-table
        :data="params"
        stripe
        size="small"
        class="compact-table params-table"
      >
        <el-table-column prop="key" label="键" width="250">
          <template #default="{ row }">
            <span class="param-key">{{ row.key }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="值" min-width="300">
          <template #default="{ row }">
            <div v-if="editingKey === row.key" class="edit-cell">
                <el-input
                  v-model="editForm.value"
                  size="small"
                  placeholder="请输入参数值"
                  @keyup.enter="handleSave"
                  @keyup.escape="cancelEdit"
                />
            </div>
            <span v-else class="param-value">{{ row.value }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="{ row }">
            <div v-if="editingKey === row.key" class="edit-cell">
                <el-input
                  v-model="editForm.description"
                  size="small"
                  placeholder="可选描述"
                />
              </div>
            <span v-else class="param-desc">{{ row.description || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">
            {{ row.updated_at ? formatDate(row.updated_at) : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <template v-if="editingKey === row.key">
              <el-button type="primary" text size="small" :loading="saving" @click="handleSave">
                保存
              </el-button>
              <el-button text size="small" @click="cancelEdit">取消</el-button>
            </template>
            <el-button v-else type="primary" text size="small" @click="startEdit(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Add New Parameter -->
    <div class="add-param-section">
      <h3 class="section-title">新增参数</h3>

      <div v-if="addError" class="section-error">
        <ApiErrorBanner :error="addError" @dismiss="addError = null" />
      </div>

      <el-form
        ref="addFormRef"
        :model="addForm"
        :rules="addRules"
        inline
        class="add-form"
      >
        <el-form-item
          label="键"
          prop="key"
          :error="addFieldErrors.get('key')?.join(', ')"
        >
          <el-input
            v-model.trim="addForm.key"
            placeholder="请输入参数键（例如：MAX_LOGIN_RETRY）"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item
          label="值"
          prop="value"
          :error="addFieldErrors.get('value')?.join(', ')"
        >
          <el-input
            v-model="addForm.value"
            placeholder="请输入参数值"
            style="width: 250px"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="addForm.description"
            placeholder="可选描述"
            style="width: 250px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="adding" @click="handleAdd">
            新增参数
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getSystemParams, upsertSystemParam } from '../../../api/system'
import type { SystemParamListItem } from '../../../api/system.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

const params = ref<SystemParamListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const isEmpty = computed(() => !loading.value && !error.value && params.value.length === 0)

// Inline edit state
const editingKey = ref<string | null>(null)
const saving = ref(false)
const editForm = reactive({
  value: '',
  description: '',
})

// Add form state
const addFormRef = ref<FormInstance>()
const adding = ref(false)
const addError = ref<ApiError | null>(null)
const addFieldErrors = ref<Map<string, string[]>>(new Map())
const addForm = reactive({
  key: '',
  value: '',
  description: '',
})

const addRules: FormRules = {
  key: [
    { required: true, message: '键为必填项', trigger: 'blur' },
  ],
  value: [
    { required: true, message: '值为必填项', trigger: 'blur' },
  ],
}

async function fetchParams() {
  loading.value = true
  error.value = null
  try {
    params.value = await getSystemParams()
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

function startEdit(param: SystemParamListItem) {
  editingKey.value = param.key
  editForm.value = param.value
  editForm.description = param.description || ''
}

function cancelEdit() {
  editingKey.value = null
  editForm.value = ''
  editForm.description = ''
}

async function handleSave() {
  if (!editingKey.value) return

  saving.value = true
  error.value = null

  try {
    await upsertSystemParam(editingKey.value, {
      value: editForm.value,
      description: editForm.description || undefined,
    })

    ElMessage.success('参数更新成功')
    cancelEdit()
    fetchParams()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    saving.value = false
  }
}

async function handleAdd() {
  addFieldErrors.value = new Map()

  const valid = await addFormRef.value?.validate().catch(() => false)
  if (!valid) return

  adding.value = true
  addError.value = null

  try {
    await upsertSystemParam(addForm.key, {
      value: addForm.value,
      description: addForm.description || undefined,
    })

    ElMessage.success('参数新增成功')
    addForm.key = ''
    addForm.value = ''
    addForm.description = ''
    fetchParams()
  } catch (err) {
    const apiError = err as ApiError
    addError.value = apiError

    if (apiError.status === 422 && apiError.details) {
      addFieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    adding.value = false
  }
}

onMounted(() => {
  fetchParams()
})
</script>

<style scoped>
.param-key {
  font-family: var(--font-mono);
  font-weight: 500;
  color: var(--color-primary);
}

.param-value {
  font-family: var(--font-mono);
}

.param-desc {
  color: var(--text-sub);
  font-size: 13px;
}

.edit-cell {
  display: flex;
  align-items: center;
}

.params-table :deep(.el-table__row) {
  cursor: default;
}

.add-param-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-light);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
}

.section-error {
  margin-bottom: 16px;
}

.add-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: flex-start;
}

.add-form :deep(.el-form-item) {
  margin-bottom: 0;
}
</style>
