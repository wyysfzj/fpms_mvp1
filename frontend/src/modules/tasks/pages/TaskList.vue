<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">{{ ZH.taskList.title }}</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button :loading="exporting" @click="handleExport">导出清单</el-button>
        <el-button :loading="printing" @click="handlePrint">打印清单</el-button>
        <router-link to="/tasks/new">
          <el-button type="primary">{{ ZH.taskList.newTask }}</el-button>
        </router-link>
      </div>
    </div>

    <!-- Filter Bar -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-segmented
          v-model="viewMode"
          :options="viewOptions"
          @change="onFilterChange"
        />
      </el-col>
      <el-col :span="6">
        <el-select v-model="filterStatus" placeholder="全部" clearable @change="onFilterChange">
          <el-option label="全部" value="" />
          <el-option label="待处理" value="OPEN" />
          <el-option label="已完成" value="DONE" />
          <el-option label="已取消" value="CANCELLED" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-select
          v-model="filterClientId"
          placeholder="全部客户"
          clearable
          filterable
          @change="onFilterChange"
        >
          <el-option
            v-for="c in clientOptions"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
        </el-select>
      </el-col>
    </el-row>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <LoadingBlock v-if="loading" :rows="10" />

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        :title="ZH.taskList.emptyTitle"
        :message="ZH.taskList.emptyMsg"
        icon="✅"
        :cta-label="ZH.taskList.newTask"
        cta-to="/tasks/new"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="tasks"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="id" :label="ZH.taskList.id" width="70" />
        <el-table-column prop="title" :label="ZH.taskList.taskTitle" min-width="200" />
        <el-table-column prop="case_no" :label="ZH.taskList.case_" width="120">
          <template #default="{ row }">
            <router-link v-if="row.case_id" :to="`/cases/${row.case_id}`" class="task-case-link">
              {{ row.case_no || `#${row.case_id}` }}
            </router-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="客户" width="140">
          <template #default="{ row }">
            {{ row.client_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.taskList.status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getTaskStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.taskList.priority" width="100">
          <template #default="{ row }">
            <span :class="getPriorityClass(row.priority)">
              {{ getTaskPriorityText(row.priority) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.taskList.dueDate" width="130">
          <template #default="{ row }">
            <span :class="{ 'task-due-urgent': isUrgent(row.due_date) }">
              {{ formatDate(row.due_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="assigned_to" :label="ZH.taskList.assigned" width="120">
          <template #default="{ row }">
            {{ row.assigned_to || '-' }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.taskList.actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" :disabled="actionLoading">
              <el-button
                text
                size="small"
                class="row-actions-trigger"
                :loading="actionLoading && actionTaskId === row.id"
                :aria-label="`打开任务操作：${row.title || row.id}`"
              >
                <span>{{ ZH.common.actions }}</span>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-if="canClose(row.status)"
                    @click="handleClose(row)"
                  >
                    {{ ZH.taskList.close }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="canReopen(row.status)"
                    @click="handleReopen(row)"
                  >
                    {{ ZH.taskList.reopen }}
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="canCancel(row.status)"
                    divided
                    @click="handleCancel(row)"
                  >
                    <span class="action-danger">{{ ZH.taskList.cancel }}</span>
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleDelete(row)">
                    <span class="action-danger">删除</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  cancelTask,
  closeTask,
  deleteTask,
  exportTaskList,
  getTasks,
  printTaskList,
  reopenTask,
} from '../../../api/tasks'
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import type { Task } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { getTaskActionText, getTaskPriorityText, getTaskStatusText } from '../../../constants/displayText'

const tasks = ref<Task[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref('')
const filterClientId = ref('')
const viewMode = ref<'all' | 'worker' | 'supervisor'>('all')
const clientOptions = ref<Client[]>([])
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)
const exporting = ref(false)
const printing = ref(false)
const viewOptions = [
  { label: '全部任务', value: 'all' },
  { label: '我的任务', value: 'worker' },
  { label: '团队任务', value: 'supervisor' },
]

function onFilterChange() {
  page.value = 1
  fetchTasks()
}

const actionLoading = ref(false)
const actionTaskId = ref<string | null>(null)

async function fetchTasks() {
  loading.value = true
  error.value = null
  try {
    const result = await getTasks(buildListParams())
    tasks.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function buildListParams() {
  return {
    page: page.value,
    page_size: pageSize.value,
    status: filterStatus.value || undefined,
    client_id: filterClientId.value || undefined,
    as: viewMode.value === 'all' ? undefined : viewMode.value,
  } as const
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

function isUrgent(dueDate?: string): boolean {
  if (!dueDate) return false
  const due = dayjs(dueDate)
  const now = dayjs()
  const daysUntilDue = due.diff(now, 'day')
  return daysUntilDue <= 3 && daysUntilDue >= 0
}

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status?.toLowerCase()) {
    case 'completed':
    case 'done':
    case 'closed':
      return 'success'
    case 'in_progress':
    case 'in progress':
      return 'warning'
    case 'overdue':
    case 'blocked':
      return 'danger'
    case 'cancelled':
    case 'canceled':
      return 'info'
    case 'pending':
      return 'info'
    default:
      return ''
  }
}

function getPriorityClass(priority?: string): string {
  switch (priority?.toLowerCase()) {
    case 'high':
    case 'urgent':
      return 'task-priority-high'
    case 'medium':
      return 'task-priority-medium'
    case 'low':
      return 'task-priority-low'
    default:
      return ''
  }
}

// Status transition helpers
function canClose(status: string): boolean {
  const s = status?.toLowerCase()
  return s !== 'closed' && s !== 'completed' && s !== 'done' && s !== 'cancelled' && s !== 'canceled'
}

function canReopen(status: string): boolean {
  const s = status?.toLowerCase()
  return s === 'closed' || s === 'completed' || s === 'done'
}

function canCancel(status: string): boolean {
  const s = status?.toLowerCase()
  return s !== 'cancelled' && s !== 'canceled'
}

async function handleClose(row: Task) {
  try {
    await ElMessageBox.confirm(
      ZH.taskList.closeConfirm.replace('{title}', row.title),
      ZH.taskList.closeTitle,
      { confirmButtonText: ZH.taskList.close, cancelButtonText: ZH.common.cancel, type: 'info' }
    )
    await executeAction(row.id, 'close', closeTask)
  } catch {
    // User cancelled
  }
}

async function handleReopen(row: Task) {
  try {
    await ElMessageBox.confirm(
      ZH.taskList.reopenConfirm.replace('{title}', row.title),
      ZH.taskList.reopenTitle,
      { confirmButtonText: ZH.taskList.reopen, cancelButtonText: ZH.common.cancel, type: 'info' }
    )
    await executeAction(row.id, 'reopen', reopenTask)
  } catch {
    // User cancelled
  }
}

async function handleCancel(row: Task) {
  try {
    await ElMessageBox.confirm(
      ZH.taskList.cancelConfirm.replace('{title}', row.title),
      ZH.taskList.cancelTitle,
      { confirmButtonText: ZH.common.confirm, cancelButtonText: ZH.common.cancel, type: 'warning' }
    )
    await executeAction(row.id, 'cancel', cancelTask)
  } catch {
    // User cancelled
  }
}

async function handleDelete(row: Task) {
  try {
    await ElMessageBox.confirm(
      `确认删除任务“${row.title}”吗？该操作不可撤销。`,
      '删除任务',
      { confirmButtonText: '删除', cancelButtonText: ZH.common.cancel, type: 'warning' }
    )
    await executeAction(row.id, 'delete', deleteTask)
  } catch {
    // User cancelled
  }
}

async function executeAction(
  id: string | number,
  actionName: string,
  actionFn: (id: string | number) => Promise<void>,
) {
  actionLoading.value = true
  actionTaskId.value = String(id)
  error.value = null

  try {
    await actionFn(id)
    ElMessage.success(ZH.taskList.actionSuccess.replace('{action}', getTaskActionText(actionName)))
    await fetchTasks()
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError
    
    // Show specific message for 409/400 conflict
    if (apiError.status === 409 || apiError.status === 400) {
      const requestIdMsg = apiError.requestId ? `（请求ID：${apiError.requestId}）` : ''
      ElMessage.error(`无法执行“${getTaskActionText(actionName)}”操作：${apiError.message}${requestIdMsg}`)
    }
  } finally {
    actionLoading.value = false
    actionTaskId.value = null
  }
}

function downloadBlob(blob: Blob, fileName: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

function buildExportFileName() {
  if (viewMode.value === 'worker') return '我的时限任务清单.xlsx'
  if (viewMode.value === 'supervisor') return '监督时限任务清单.xlsx'
  return '时限任务清单.xlsx'
}

async function handleExport() {
  exporting.value = true
  error.value = null
  try {
    const blob = await exportTaskList(buildListParams())
    downloadBlob(blob, buildExportFileName())
    ElMessage.success('时限任务清单已开始导出。')
  } catch (err) {
    error.value = err as ApiError
    ElMessage.error('导出失败，请稍后重试。')
  } finally {
    exporting.value = false
  }
}

async function handlePrint() {
  printing.value = true
  error.value = null
  try {
    const html = await printTaskList(buildListParams())
    const printWindow = window.open('', '_blank', 'noopener,noreferrer')
    if (!printWindow) {
      ElMessage.error('浏览器拦截了打印窗口，请允许弹窗后重试。')
      return
    }
    printWindow.document.open()
    printWindow.document.write(html)
    printWindow.document.close()
    printWindow.focus()
    printWindow.print()
    ElMessage.success('时限任务清单已打开打印预览。')
  } catch (err) {
    error.value = err as ApiError
    ElMessage.error('打印失败，请稍后重试。')
  } finally {
    printing.value = false
  }
}

watch([page, pageSize], () => {
  fetchTasks()
})

async function loadClients() {
  try {
    const result = await getClients({ page: 1, page_size: 9999 })
    clientOptions.value = result.items
  } catch {
    // silently ignore
  }
}

onMounted(() => {
  fetchTasks()
  loadClients()
})
</script>

<style scoped>
.action-danger {
  color: var(--color-danger);
}
</style>
