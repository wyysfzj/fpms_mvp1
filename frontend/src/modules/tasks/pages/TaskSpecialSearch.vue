<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">专项期限检索</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button :loading="exporting" @click="handleExport">导出清单</el-button>
        <el-button :loading="printing" @click="handlePrint">打印清单</el-button>
        <router-link to="/tasks">
          <el-button>返回任务列表</el-button>
        </router-link>
      </div>
    </div>

    <el-form :model="filters" inline class="filter-form">
      <el-form-item label="任务类型">
        <el-select
          v-model="filters.task_code"
          clearable
          class="filter-select"
          placeholder="全部"
          @change="applyFilters"
        >
          <el-option label="全部" value="" />
          <el-option label="申请费时限" value="APPLY_FEE_LIMIT" />
          <el-option label="实审请求时限" value="EXAM_REQUEST_LIMIT" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select
          v-model="filters.status"
          clearable
          class="filter-select"
          placeholder="全部"
          @change="applyFilters"
        >
          <el-option label="全部" value="" />
          <el-option
            v-for="option in statusOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="案件编号">
        <el-input
          v-model.trim="filters.case_no"
          clearable
          class="filter-input"
          placeholder="请输入案件编号"
          @keyup.enter="applyFilters"
          @change="applyFilters"
        />
      </el-form-item>
      <el-form-item label="客户名称">
        <el-input
          v-model.trim="filters.client_name"
          clearable
          class="filter-input"
          placeholder="请输入客户名称"
          @keyup.enter="applyFilters"
          @change="applyFilters"
        />
      </el-form-item>
      <el-form-item label="截止日期">
        <el-date-picker
          v-model="filters.due_date_range"
          clearable
          class="filter-range"
          end-placeholder="结束日期"
          range-separator="至"
          start-placeholder="开始日期"
          type="daterange"
          value-format="YYYY-MM-DD"
          @change="applyFilters"
        />
      </el-form-item>
      <el-form-item label="是否逾期">
        <el-select
          v-model="filters.is_overdue"
          clearable
          class="filter-select"
          placeholder="全部"
          @change="applyFilters"
        >
          <el-option label="全部" :value="null" />
          <el-option label="已逾期" :value="true" />
          <el-option label="未逾期" :value="false" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="applyFilters">查询</el-button>
        <el-button :disabled="loading" @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading && items.length === 0" :rows="10" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无专项检索结果"
        message="请调整筛选条件后重试。"
        icon="🔎"
        cta-label="返回任务列表"
        cta-to="/tasks"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        :data="items"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="task_code" label="任务编码" width="160">
          <template #default="{ row }">
            <div class="code-cell">
              <span class="mono-num">{{ row.task_code }}</span>
              <span class="code-label">{{ getTaskCodeLabel(row.task_code) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="task_id" label="任务ID" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <router-link class="task-link mono-num" :to="`/tasks/${row.task_id}`">
              {{ row.task_id }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="案件" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="code-cell">
              <router-link v-if="row.case_id" class="case-link" :to="`/cases/${row.case_id}`">
                {{ row.case_no || '未填写案件编号' }}
              </router-link>
              <span v-else>—</span>
              <span class="code-label mono-num">{{ row.case_id }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="client_name" label="客户名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.client_name || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <router-link class="task-title-link" :to="`/tasks/${row.task_id}`">
              {{ row.title }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="截止日期" width="120">
          <template #default="{ row }">
            <span :class="{ 'task-due-urgent': row.is_overdue }">
              {{ formatDate(row.due_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="逾期" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_overdue ? 'danger' : 'success'" size="small">
              {{ row.is_overdue ? '已逾期' : '未逾期' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.remark || '—' }}
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
      />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { exportSpecialTasks, printSpecialTasks, searchSpecialTasks } from '../../../api/tasks'
import type { ApiError } from '../../../api/types'
import type { TaskSpecialSearchItem } from '../../../api/tasks.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { getTaskStatusText } from '../../../constants/displayText'

const items = ref<TaskSpecialSearchItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const exporting = ref(false)
const printing = ref(false)

const filters = reactive({
  task_code: null as string | null,
  status: null as string | null,
  case_no: '',
  client_name: '',
  due_date_range: null as [string, string] | null,
  is_overdue: null as boolean | null,
})

const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

const TASK_CODE_LABELS: Record<string, string> = {
  APPLY_FEE_LIMIT: '申请费时限',
  EXAM_REQUEST_LIMIT: '实审请求时限',
}

const statusOptions = [
  { value: 'OPEN', label: getTaskStatusText('OPEN') },
  { value: 'PENDING', label: getTaskStatusText('PENDING') },
  { value: 'IN_PROGRESS', label: getTaskStatusText('IN_PROGRESS') },
  { value: 'DONE', label: getTaskStatusText('DONE') },
  { value: 'COMPLETED', label: getTaskStatusText('COMPLETED') },
  { value: 'CLOSED', label: getTaskStatusText('CLOSED') },
  { value: 'CANCELLED', label: getTaskStatusText('CANCELLED') },
  { value: 'BLOCKED', label: getTaskStatusText('BLOCKED') },
  { value: 'OVERDUE', label: getTaskStatusText('OVERDUE') },
]

function buildParams() {
  const dueDateRange = filters.due_date_range || []
  const [dueDateFrom, dueDateTo] = dueDateRange

  return {
    page: page.value,
    page_size: pageSize.value,
    ...(filters.task_code ? { task_code: filters.task_code } : {}),
    ...(filters.status ? { status: filters.status } : {}),
    ...(filters.case_no ? { case_no: filters.case_no } : {}),
    ...(filters.client_name ? { client_name: filters.client_name } : {}),
    ...(dueDateFrom && dueDateTo ? { due_date_from: dueDateFrom, due_date_to: dueDateTo } : {}),
    ...(filters.is_overdue !== null ? { is_overdue: filters.is_overdue } : {}),
  }
}

async function fetchSpecialSearch() {
  loading.value = true
  error.value = null
  try {
    const result = await searchSpecialTasks(buildParams())
    items.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const blob = await exportSpecialTasks(buildParams())
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'special-task-search.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('专项检索清单导出成功')
  } catch {
    ElMessage.error('专项检索清单导出失败')
  } finally {
    exporting.value = false
  }
}

async function handlePrint() {
  printing.value = true
  try {
    const html = await printSpecialTasks(buildParams())
    const popup = window.open('', '_blank', 'noopener,noreferrer')
    if (!popup) {
      throw new Error('popup_blocked')
    }
    popup.document.open()
    popup.document.write(html)
    popup.document.close()
    popup.focus()
    popup.print()
    ElMessage.success('专项检索清单打印页已打开')
  } catch {
    ElMessage.error('专项检索清单打印失败')
  } finally {
    printing.value = false
  }
}

function applyFilters() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  fetchSpecialSearch()
}

function resetFilters() {
  filters.task_code = null
  filters.status = null
  filters.case_no = ''
  filters.client_name = ''
  filters.due_date_range = null
  filters.is_overdue = null

  if (page.value !== 1) {
    page.value = 1
    return
  }
  fetchSpecialSearch()
}

function formatDate(value?: string | null): string {
  return value ? dayjs(value).format('YYYY-MM-DD') : '—'
}

function getTaskCodeLabel(code: string): string {
  return TASK_CODE_LABELS[code] || code
}

function getStatusText(status: string): string {
  return getTaskStatusText(status)
}

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status?.toUpperCase()) {
    case 'DONE':
      return 'success'
    case 'CANCELLED':
      return 'danger'
    case 'OPEN':
      return 'warning'
    default:
      return 'info'
  }
}

watch([page, pageSize], () => {
  fetchSpecialSearch()
}, { immediate: true })
</script>

<style scoped>
.filter-form {
  margin-bottom: 16px;
}

.filter-input,
.filter-select,
.filter-range {
  width: 220px;
}

.code-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.code-label {
  font-size: 12px;
  color: var(--text-sub);
}

.task-link,
.case-link,
.task-title-link {
  color: inherit;
  text-decoration: none;
}

.task-link:hover,
.case-link:hover,
.task-title-link:hover {
  color: var(--color-primary);
}
</style>
