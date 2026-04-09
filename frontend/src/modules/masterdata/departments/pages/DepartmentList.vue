<template>
  <div class="page-container department-page">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">部门主数据</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button :loading="loading" @click="handleRefresh">刷新</el-button>
        <el-button type="primary" @click="openCreate">新增部门</el-button>
      </div>
    </div>

    <div v-if="pageError" class="page-error">
      <ApiErrorBanner :error="pageError" @dismiss="pageError = null" />
    </div>

    <div class="filter-bar">
      <el-input
        v-model.trim="filters.q"
        class="filter-input"
        clearable
        placeholder="请输入部门编码或中文名称"
        @keyup.enter="handleSearch"
      />
      <el-select v-model="filters.is_active" class="filter-select" @change="handleSearch">
        <el-option label="全部状态" value="all" />
        <el-option label="启用" value="true" />
        <el-option label="停用" value="false" />
      </el-select>
      <el-button type="primary" @click="handleSearch">查询</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <LoadingBlock v-if="loading && departments.length === 0" :rows="8" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无部门"
        message="创建首个部门后，可在这里维护编码、中文名和启停用状态。"
        icon="🏢"
        cta-label="新增部门"
        @cta="openCreate"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        v-loading="loading && departments.length > 0"
        :data="departments"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="department_code" label="编码" width="160" />
        <el-table-column prop="name_cn" label="部门名称" min-width="220" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click="openEdit(row)">编辑</el-button>
            <el-button
              v-if="row.is_active"
              text
              type="danger"
              size="small"
              :loading="isRowBusy(row.id, 'deactivate')"
              @click="handleDeactivate(row)"
            >
              停用
            </el-button>
            <el-button
              v-else
              text
              type="success"
              size="small"
              :loading="isRowBusy(row.id, 'activate')"
              @click="handleActivate(row)"
            >
              启用
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <div class="table-empty">暂无符合条件的部门。</div>
        </template>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @current-change="handleCurrentChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </div>

    <el-dialog
      v-model="showDialog"
      :close-on-click-modal="false"
      :title="isEdit ? '编辑部门' : '新增部门'"
      width="720px"
      @closed="handleDialogClosed"
    >
      <div v-if="dialogError" class="dialog-error">
        <ApiErrorBanner :error="dialogError" @dismiss="dialogError = null" />
      </div>

      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item
              label="部门编码"
              prop="department_code"
              :error="fieldErrors.get('department_code')?.join('，')"
            >
              <el-input v-model.trim="form.department_code" placeholder="请输入部门编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="部门名称" prop="name_cn" :error="fieldErrors.get('name_cn')?.join('，')">
          <el-input v-model.trim="form.name_cn" placeholder="请输入部门名称" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建部门' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  createDepartment,
  deactivateDepartment,
  getDepartments,
  updateDepartment,
} from '../../../../api/departments'
import type { Department } from '../../../../api/departments.types'
import type { ApiError } from '../../../../api/types'
import ApiErrorBanner from '../../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../../components/state/LoadingBlock.vue'
import { mapValidationDetailsToFieldErrors } from '../../../../utils/validation'

type RowAction = 'activate' | 'deactivate'
type StatusFilter = 'all' | 'true' | 'false'

const departments = ref<Department[]>([])
const loading = ref(false)
const pageError = ref<ApiError | null>(null)
const dialogError = ref<ApiError | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !pageError.value && departments.value.length === 0)

const filters = reactive<{ q: string; is_active: StatusFilter }>({
  q: '',
  is_active: 'all',
})

const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const saving = ref(false)
const formRef = ref<FormInstance>()
const fieldErrors = ref<Map<string, string[]>>(new Map())
const rowActionId = ref('')
const rowActionType = ref<RowAction | ''>('')
const skipNextCurrentChange = ref(false)

const form = reactive({
  department_code: '',
  name_cn: '',
  is_active: true,
})

const formRules: FormRules = {
  department_code: [{ required: true, message: '部门编码为必填项', trigger: 'blur' }],
  name_cn: [{ required: true, message: '部门名称为必填项', trigger: 'blur' }],
}

function toListParams() {
  return {
    page: currentPage.value,
    page_size: pageSize.value,
    q: filters.q.trim() || undefined,
    is_active: filters.is_active === 'all' ? undefined : filters.is_active === 'true',
  }
}

async function fetchDepartments() {
  loading.value = true
  pageError.value = null
  try {
    const result = await getDepartments(toListParams())
    departments.value = result.items
    total.value = result.total
  } catch (err) {
    pageError.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function resetForm() {
  fieldErrors.value = new Map()
  form.department_code = ''
  form.name_cn = ''
  form.is_active = true
}

function openCreate() {
  resetForm()
  dialogError.value = null
  isEdit.value = false
  editingId.value = ''
  showDialog.value = true
}

function openEdit(row: Department) {
  resetForm()
  dialogError.value = null
  isEdit.value = true
  editingId.value = row.id
  form.department_code = row.department_code
  form.name_cn = row.name_cn
  form.is_active = row.is_active
  showDialog.value = true
}

function handleDialogClosed() {
  dialogError.value = null
  fieldErrors.value = new Map()
  resetForm()
  editingId.value = ''
  isEdit.value = false
}

async function handleSave() {
  fieldErrors.value = new Map()
  dialogError.value = null

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      await updateDepartment(editingId.value, {
        department_code: form.department_code,
        name_cn: form.name_cn,
        is_active: form.is_active,
      })
      ElMessage.success('部门更新成功')
    } else {
      await createDepartment({
        department_code: form.department_code,
        name_cn: form.name_cn,
        is_active: form.is_active,
      })
      ElMessage.success('部门创建成功')
    }
    showDialog.value = false
    await fetchDepartments()
  } catch (err) {
    const apiError = err as ApiError
    dialogError.value = apiError
    fieldErrors.value = mapValidationDetailsToFieldErrors(apiError)
  } finally {
    saving.value = false
  }
}

function isRowBusy(id: string, action: RowAction) {
  return rowActionId.value === id && rowActionType.value === action
}

async function handleDeactivate(row: Department) {
  await ElMessageBox.confirm(
    `确定要停用部门“${row.department_code}”吗？停用后该部门将不再显示为启用状态。`,
    '停用部门',
    { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' },
  )
  rowActionId.value = row.id
  rowActionType.value = 'deactivate'
  try {
    await deactivateDepartment(row.id)
    ElMessage.success('部门已停用')
    await fetchDepartments()
  } finally {
    rowActionId.value = ''
    rowActionType.value = ''
  }
}

async function handleActivate(row: Department) {
  rowActionId.value = row.id
  rowActionType.value = 'activate'
  try {
    await updateDepartment(row.id, { is_active: true })
    ElMessage.success('部门已启用')
    await fetchDepartments()
  } finally {
    rowActionId.value = ''
    rowActionType.value = ''
  }
}

function handleSearch() {
  skipNextCurrentChange.value = true
  currentPage.value = 1
  void fetchDepartments()
}

function handleReset() {
  filters.q = ''
  filters.is_active = 'all'
  skipNextCurrentChange.value = true
  currentPage.value = 1
  void fetchDepartments()
}

function handleRefresh() {
  void fetchDepartments()
}

function handleCurrentChange(page: number) {
  currentPage.value = page
  if (skipNextCurrentChange.value) {
    skipNextCurrentChange.value = false
    return
  }
  void fetchDepartments()
}

function handlePageSizeChange(size: number) {
  pageSize.value = size
  skipNextCurrentChange.value = true
  currentPage.value = 1
  void fetchDepartments()
}

onMounted(() => {
  void fetchDepartments()
})
</script>
