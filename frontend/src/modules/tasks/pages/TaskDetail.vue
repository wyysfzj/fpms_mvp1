<template>
  <div class="page-container task-detail-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">&larr;</span> {{ ZH.common.back }}
        </el-button>
      </div>
      <div class="page-header-right">
        <el-button
          v-if="task && canClose(task.status)"
          type="primary"
          @click="handleClose"
        >
          关闭
        </el-button>
        <el-button
          v-if="task && canReopen(task.status)"
          type="primary"
          @click="handleReopen"
        >
          重新打开
        </el-button>
        <el-button
          v-if="task && canCancel(task.status)"
          type="danger"
          plain
          @click="handleCancel"
        >
          取消
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

    <!-- Content -->
    <template v-else-if="task">
      <!-- Task Header -->
      <div class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <span class="case-no">#{{ task.id }}</span>
            <span class="meta-divider">|</span>
            <span v-if="task.case_id">
              <router-link :to="`/cases/${task.case_id}`" class="task-case-link">
                {{ task.case_no || `案件 #${task.case_id}` }}
              </router-link>
            </span>
            <template v-if="task.worker_id">
              <span class="meta-divider">|</span>
              <span>负责人: {{ task.worker_id }}</span>
            </template>
            <template v-if="task.supervisor_id">
              <span class="meta-divider">|</span>
              <span>监督人: {{ task.supervisor_id }}</span>
            </template>
          </div>
          <div class="case-title">
            <h1>{{ task.title || '未命名任务' }}</h1>
          </div>
        </div>
        <div class="case-header-actions">
          <el-tag :type="getStatusType(task.status)" size="default">
            {{ getTaskStatusText(task.status) }}
          </el-tag>
        </div>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" class="case-tabs">
        <el-tab-pane label="概览" name="overview">
          <div class="case-panel">
            <h3 class="panel-heading">任务信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">截止日期</span>
                <span class="info-value" :class="{ 'task-due-urgent': isUrgent(task.due_date) }">
                  {{ formatDate(task.due_date) }}
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">内部截止</span>
                <span class="info-value">{{ formatDate(task.internal_due) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">基准日期</span>
                <span class="info-value">{{ formatDate(task.base_date) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">状态</span>
                <span class="info-value">{{ getTaskStatusText(task.status) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">负责人</span>
                <span class="info-value">{{ task.worker_id || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">监督人</span>
                <span class="info-value">{{ task.supervisor_id || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatDateTime(task.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">更新时间</span>
                <span class="info-value">{{ formatDateTime(task.updated_at) }}</span>
              </div>
            </div>
            <div v-if="task.remark" class="notes-section">
              <h4 class="notes-title">备注</h4>
              <p class="notes-content">{{ task.remark }}</p>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="操作日志" name="logs">
          <div class="case-panel">
            <TaskLogTimeline :task-id="task.id" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- Empty State (task not found) -->
    <div v-else-if="!loading && !error" class="page-empty">
      <div class="empty-state">
        <h3 class="empty-title">未找到任务</h3>
        <p class="empty-message">请求的任务不存在。</p>
        <el-button type="primary" @click="goBack">{{ ZH.common.back }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTask, closeTask, reopenTask, cancelTask } from '../../../api/tasks'
import type { Task } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import TaskLogTimeline from '../components/TaskLogTimeline.vue'
import { usePageContext } from '../../../stores/pageContext'
import { ZH } from '../../../constants/labels.zh'
import { getTaskStatusText, getTaskActionText } from '../../../constants/displayText'

const route = useRoute()
const router = useRouter()
const pageContext = usePageContext()

const task = ref<Task | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)
const activeTab = ref('overview')

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

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

function formatDateTime(dateStr?: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

function isUrgent(dueDate?: string): boolean {
  if (!dueDate) return false
  const due = dayjs(dueDate)
  const now = dayjs()
  const daysUntilDue = due.diff(now, 'day')
  return daysUntilDue <= 3 && daysUntilDue >= 0
}

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
  return s === 'open'
}

async function fetchTask() {
  const id = String(route.params.id || '').trim()
  if (!id) return

  loading.value = true
  error.value = null

  try {
    task.value = await getTask(id)
    pageContext.setBreadcrumb(['期限监控', '任务详情', task.value.title || id])
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function handleClose() {
  if (!task.value) return
  try {
    await ElMessageBox.confirm(
      ZH.taskList.closeConfirm.replace('{title}', task.value.title),
      ZH.taskList.closeTitle,
      { confirmButtonText: ZH.taskList.close, cancelButtonText: ZH.common.cancel, type: 'info' }
    )
    await executeAction('close', closeTask)
  } catch {
    // User cancelled
  }
}

async function handleReopen() {
  if (!task.value) return
  try {
    await ElMessageBox.confirm(
      ZH.taskList.reopenConfirm.replace('{title}', task.value.title),
      ZH.taskList.reopenTitle,
      { confirmButtonText: ZH.taskList.reopen, cancelButtonText: ZH.common.cancel, type: 'info' }
    )
    await executeAction('reopen', reopenTask)
  } catch {
    // User cancelled
  }
}

async function handleCancel() {
  if (!task.value) return
  try {
    await ElMessageBox.confirm(
      ZH.taskList.cancelConfirm.replace('{title}', task.value.title),
      ZH.taskList.cancelTitle,
      { confirmButtonText: ZH.common.confirm, cancelButtonText: ZH.common.cancel, type: 'warning' }
    )
    await executeAction('cancel', cancelTask)
  } catch {
    // User cancelled
  }
}

async function executeAction(
  actionName: string,
  actionFn: (id: string | number) => Promise<void>,
) {
  if (!task.value) return
  error.value = null

  try {
    await actionFn(task.value.id)
    ElMessage.success(ZH.taskList.actionSuccess.replace('{action}', getTaskActionText(actionName)))
    await fetchTask()
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError
    if (apiError.status === 409 || apiError.status === 400) {
      ElMessage.error(`无法执行"${getTaskActionText(actionName)}"操作：${apiError.message}`)
    }
  }
}

function goBack() {
  router.push('/tasks')
}

onMounted(() => {
  fetchTask()
})

onBeforeUnmount(() => {
  pageContext.clear()
})
</script>

<style scoped>
.task-case-link {
  color: var(--color-primary);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 13px;
}

.task-case-link:hover {
  text-decoration: underline;
}
</style>
