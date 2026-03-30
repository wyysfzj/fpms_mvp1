<template>
  <div class="page-container country-page">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">国家主数据</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button @click="handleRefresh" :loading="loading">刷新</el-button>
        <el-button type="primary" @click="openCreate">新增国家</el-button>
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
        placeholder="请输入国家编码、中文名或英文名"
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

    <LoadingBlock v-if="loading && countries.length === 0" :rows="8" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无国家"
        message="创建首个国家后，可在这里维护启用状态和基础信息。"
        icon="🌍"
        cta-label="新增国家"
        @cta="openCreate"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        v-loading="loading && countries.length > 0"
        :data="countries"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name_cn" label="中文名称" min-width="180" />
        <el-table-column label="英文名称" min-width="180">
          <template #default="{ row }">
            {{ row.name_en || '—' }}
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
          <div class="table-empty">暂无符合条件的国家。</div>
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
      :title="isEdit ? '编辑国家' : '新增国家'"
      width="720px"
      @closed="handleDialogClosed"
    >
      <div v-if="dialogError" class="dialog-error">
        <ApiErrorBanner :error="dialogError" @dismiss="dialogError = null" />
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-position="top"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="国家编码" prop="code" :error="fieldErrors.get('code')?.join('，')">
              <el-input v-model.trim="form.code" placeholder="请输入国家编码，例如 CN" />
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
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建国家' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createCountry, deactivateCountry, getCountries, updateCountry } from '../../../api/masterdata'
import type { Country } from '../../../api/masterdata.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

type RowAction = 'activate' | 'deactivate'
type StatusFilter = 'all' | 'true' | 'false'

const countries = ref<Country[]>([])
const loading = ref(false)
const pageError = ref<ApiError | null>(null)
const dialogError = ref<ApiError | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !pageError.value && countries.value.length === 0)

const filters = reactive<{
  q: string
  is_active: StatusFilter
}>({
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
  code: '',
  name_cn: '',
  name_en: '',
  is_active: true,
})

const formRules: FormRules = {
  code: [
    { required: true, message: '国家编码为必填项', trigger: 'blur' },
  ],
  name_cn: [
    { required: true, message: '中文名称为必填项', trigger: 'blur' },
  ],
}

function toListParams() {
  return {
    page: currentPage.value,
    page_size: pageSize.value,
    q: filters.q.trim() || undefined,
    is_active:
      filters.is_active === 'all'
        ? undefined
        : filters.is_active === 'true',
  }
}

async function fetchCountries() {
  loading.value = true
  pageError.value = null
  try {
    const result = await getCountries(toListParams())
    countries.value = result.items
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
  form.is_active = true
}

function openCreate() {
  resetForm()
  dialogError.value = null
  isEdit.value = false
  editingId.value = ''
  showDialog.value = true
}

function openEdit(row: Country) {
  resetForm()
  dialogError.value = null
  isEdit.value = true
  editingId.value = row.id
  form.code = row.code
  form.name_cn = row.name_cn
  form.name_en = row.name_en || ''
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
      await updateCountry(editingId.value, {
        code: form.code,
        name_cn: form.name_cn,
        name_en: form.name_en,
        is_active: form.is_active,
      })
      ElMessage.success('国家更新成功')
    } else {
      await createCountry({
        code: form.code,
        name_cn: form.name_cn,
        name_en: form.name_en,
        is_active: form.is_active,
      })
      ElMessage.success('国家创建成功')
    }
    showDialog.value = false
    await fetchCountries()
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

async function handleDeactivate(row: Country) {
  try {
    await ElMessageBox.confirm(
      `确定要停用国家“${row.code}”吗？停用后该国家将不再显示为启用状态。`,
      '停用国家',
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
  rowActionType.value = 'deactivate'
  pageError.value = null

  try {
    await deactivateCountry(row.id)
    ElMessage.success('国家已停用')
    await fetchCountries()
  } catch (err) {
    pageError.value = err as ApiError
  } finally {
    rowActionId.value = ''
    rowActionType.value = ''
  }
}

async function handleActivate(row: Country) {
  try {
    await ElMessageBox.confirm(
      `确定要启用国家“${row.code}”吗？`,
      '启用国家',
      {
        confirmButtonText: '确认启用',
        cancelButtonText: '取消',
        type: 'info',
      },
    )
  } catch {
    return
  }

  rowActionId.value = row.id
  rowActionType.value = 'activate'
  pageError.value = null

  try {
    await updateCountry(row.id, { is_active: true })
    ElMessage.success('国家已启用')
    await fetchCountries()
  } catch (err) {
    pageError.value = err as ApiError
  } finally {
    rowActionId.value = ''
    rowActionType.value = ''
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchCountries()
}

function handleReset() {
  filters.q = ''
  filters.is_active = 'all'
  currentPage.value = 1
  fetchCountries()
}

function handleRefresh() {
  fetchCountries()
}

function handleCurrentChange(nextPage: number) {
  if (skipNextCurrentChange.value) {
    skipNextCurrentChange.value = false
    return
  }
  currentPage.value = nextPage
  fetchCountries()
}

function handlePageSizeChange(nextSize: number) {
  pageSize.value = nextSize
  currentPage.value = 1
  skipNextCurrentChange.value = true
  queueMicrotask(() => {
    skipNextCurrentChange.value = false
  })
  fetchCountries()
}

onMounted(() => {
  fetchCountries()
})
</script>

<style scoped>
.country-page {
  display: grid;
  gap: 16px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-input {
  width: min(360px, 100%);
}

.filter-select {
  width: 140px;
}

.page-empty {
  padding: 12px 0 8px;
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
  color: var(--text-sub);
}

.dialog-error {
  margin-bottom: 16px;
}
</style>
