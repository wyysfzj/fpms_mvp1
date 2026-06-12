<template>
  <div class="page-container applicant-page">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">申请人主数据</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button @click="handleRefresh" :loading="loading">刷新</el-button>
        <el-button type="primary" @click="openCreate">新增申请人</el-button>
      </div>
    </div>

    <div v-if="pageError" class="page-error">
      <ApiErrorBanner :error="pageError" @dismiss="pageError = null" />
    </div>

    <div class="page-toolbar">
      <el-input
        v-model.trim="searchQuery"
        clearable
        placeholder="搜索申请人名称或编码"
        class="search-input"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button :disabled="!searchQuery" @click="handleClearSearch">重置</el-button>
    </div>

    <LoadingBlock v-if="loading && applicants.length === 0" :rows="8" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无申请人"
        message="创建首个申请人后，可在这里维护编码、中文名、英文名和启停用状态。"
        icon="👤"
        cta-label="新增申请人"
        @cta="openCreate"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        v-loading="loading && applicants.length > 0"
        :data="applicants"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="code" label="编码" width="140" />
        <el-table-column prop="name_cn" label="中文名称" min-width="180" />
        <el-table-column label="英文名称" min-width="180">
          <template #default="{ row }">
            {{ row.name_en || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="总委托书备案编号" min-width="180">
          <template #default="{ row }">
            {{ row.total_power_of_attorney_no || '—' }}
          </template>
        </el-table-column>
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
              :loading="isRowBusy(row.id, 'disable')"
              @click="handleDisable(row)"
            >
              停用
            </el-button>
            <el-button
              v-else
              text
              type="success"
              size="small"
              :loading="isRowBusy(row.id, 'enable')"
              @click="handleEnable(row)"
            >
              启用
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <div class="table-empty">暂无符合条件的申请人。</div>
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
      :title="isEdit ? '编辑申请人' : '新增申请人'"
      width="720px"
      @closed="handleDialogClosed"
    >
      <div v-if="dialogError" class="dialog-error">
        <ApiErrorBanner :error="dialogError" @dismiss="dialogError = null" />
      </div>

      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="申请人编码" prop="code" :error="fieldErrors.get('code')?.join('，')">
              <el-input v-model.trim="form.code" placeholder="请输入申请人编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="中文名称" prop="name_cn" :error="fieldErrors.get('name_cn')?.join('，')">
          <el-input v-model.trim="form.name_cn" placeholder="请输入中文名称" />
        </el-form-item>

        <el-form-item label="英文名称" prop="name_en" :error="fieldErrors.get('name_en')?.join('，')">
          <el-input v-model.trim="form.name_en" placeholder="请输入英文名称（可选）" />
        </el-form-item>

        <el-form-item
          label="总委托书备案编号"
          prop="total_power_of_attorney_no"
          :error="fieldErrors.get('total_power_of_attorney_no')?.join('，')"
        >
          <el-input v-model.trim="form.total_power_of_attorney_no" placeholder="请输入总委托书备案编号（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建申请人' }}
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
  createApplicant,
  getApplicants,
  updateApplicant,
} from '../../../api/masterdata'
import type { Applicant } from '../../../api/masterdata.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

type RowAction = 'enable' | 'disable'

const applicants = ref<Applicant[]>([])
const loading = ref(false)
const pageError = ref<ApiError | null>(null)
const dialogError = ref<ApiError | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const total = ref(0)
const isEmpty = computed(() => !searchQuery.value && !loading.value && !pageError.value && applicants.value.length === 0)

const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const saving = ref(false)
const formRef = ref<FormInstance>()
const fieldErrors = ref<Map<string, string[]>>(new Map())
const rowActionId = ref('')
const rowActionType = ref<RowAction | ''>('')

const form = reactive({
  code: '',
  name_cn: '',
  name_en: '',
  total_power_of_attorney_no: '',
  is_active: true,
})

const formRules: FormRules = {
  code: [{ required: true, message: '申请人编码为必填项', trigger: 'blur' }],
  name_cn: [{ required: true, message: '中文名称为必填项', trigger: 'blur' }],
}

function toListParams() {
  return {
    page: currentPage.value,
    page_size: pageSize.value,
    q: searchQuery.value || undefined,
  }
}

async function fetchApplicants() {
  loading.value = true
  pageError.value = null
  try {
    const result = await getApplicants(toListParams())
    applicants.value = result.items
    total.value = result.total
  } catch (err) {
    pageError.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function resetForm() {
  fieldErrors.value = new Map()
  form.code = ''
  form.name_cn = ''
  form.name_en = ''
  form.total_power_of_attorney_no = ''
  form.is_active = true
}

function openCreate() {
  resetForm()
  dialogError.value = null
  isEdit.value = false
  editingId.value = ''
  showDialog.value = true
}

function openEdit(row: Applicant) {
  resetForm()
  dialogError.value = null
  isEdit.value = true
  editingId.value = row.id
  form.code = row.code
  form.name_cn = row.name_cn
  form.name_en = row.name_en || ''
  form.total_power_of_attorney_no = row.total_power_of_attorney_no || ''
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
      await updateApplicant(editingId.value, {
        code: form.code,
        name_cn: form.name_cn,
        name_en: form.name_en,
        total_power_of_attorney_no: form.total_power_of_attorney_no,
        is_active: form.is_active,
      })
      ElMessage.success('申请人更新成功')
    } else {
      await createApplicant({
        code: form.code,
        name_cn: form.name_cn,
        name_en: form.name_en,
        total_power_of_attorney_no: form.total_power_of_attorney_no,
        is_active: form.is_active,
      })
      ElMessage.success('申请人创建成功')
    }
    showDialog.value = false
    await fetchApplicants()
  } catch (err) {
    const apiError = err as ApiError
    dialogError.value = apiError
    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapValidationDetailsToFieldErrors(apiError.details)
    }
  } finally {
    saving.value = false
  }
}

function isRowBusy(id: string, action: RowAction): boolean {
  return rowActionId.value === id && rowActionType.value === action
}

async function handleDisable(row: Applicant) {
  try {
    await ElMessageBox.confirm(
      `确定要停用申请人“${row.code}”吗？停用后该申请人将不再显示为启用状态。`,
      '停用申请人',
      {
        confirmButtonText: '确认停用',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
      },
    )
  } catch {
    return
  }

  rowActionId.value = row.id
  rowActionType.value = 'disable'
  pageError.value = null

  try {
    await updateApplicant(row.id, { is_active: false })
    ElMessage.success('申请人已停用')
    await fetchApplicants()
  } catch (err) {
    pageError.value = err as ApiError
  } finally {
    rowActionId.value = ''
    rowActionType.value = ''
  }
}

async function handleEnable(row: Applicant) {
  try {
    await ElMessageBox.confirm(
      `确定要启用申请人“${row.code}”吗？`,
      '启用申请人',
      {
        confirmButtonText: '确认启用',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  rowActionId.value = row.id
  rowActionType.value = 'enable'
  pageError.value = null

  try {
    await updateApplicant(row.id, { is_active: true })
    ElMessage.success('申请人已启用')
    await fetchApplicants()
  } catch (err) {
    pageError.value = err as ApiError
  } finally {
    rowActionId.value = ''
    rowActionType.value = ''
  }
}

function handleRefresh() {
  void fetchApplicants()
}

function handleSearch() {
  currentPage.value = 1
  void fetchApplicants()
}

function handleClearSearch() {
  searchQuery.value = ''
  currentPage.value = 1
  void fetchApplicants()
}

function handleCurrentChange(page: number) {
  currentPage.value = page
  void fetchApplicants()
}

function handlePageSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  void fetchApplicants()
}

onMounted(() => {
  void fetchApplicants()
})
</script>

<style scoped>
.applicant-page {
  display: grid;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #111827;
}

.page-count {
  color: #6b7280;
  font-size: 14px;
}

.page-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-error,
.dialog-error {
  min-width: 0;
}

.page-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  max-width: 360px;
}

.page-table {
  display: grid;
  gap: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
}

.table-empty {
  padding: 32px 0;
  text-align: center;
  color: #6b7280;
}

@media (max-width: 768px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .page-header-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .page-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .search-input {
    max-width: none;
  }

  .pagination-wrap {
    justify-content: center;
  }
}
</style>
