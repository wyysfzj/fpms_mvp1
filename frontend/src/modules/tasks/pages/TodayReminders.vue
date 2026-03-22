<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">今日提醒</h1>
        <span class="page-count">{{ reminders.length }} 条</span>
      </div>
      <div class="page-header-right">
        <el-segmented v-model="viewMode" :options="modeOptions" @change="handleModeChange" />
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && reminders.length === 0 && !error" class="page-empty">
      <div class="empty-state">
        <div class="empty-icon">🔔</div>
        <h3 class="empty-title">今日暂无提醒</h3>
        <p class="empty-message">
          {{ viewMode === 'worker' 
            ? '今日没有到期任务，可稍后再查看或前往任务列表。' 
            : '今日暂无需要关注的团队任务。' 
          }}
        </p>
        <router-link to="/tasks">
          <el-button type="primary">查看全部任务</el-button>
        </router-link>
      </div>
    </div>

    <!-- Reminders List -->
    <div v-else class="reminders-list">
      <div 
        v-for="task in reminders" 
        :key="task.id" 
        class="reminder-card"
        @click="handleTaskClick(task)"
      >
        <div class="reminder-header">
          <span class="reminder-id">{{ task.id }}</span>
          <el-tag :type="getStatusType(task.status)" size="small">
            {{ getTaskStatusText(task.status) }}
          </el-tag>
        </div>
        <div class="reminder-title">{{ task.title }}</div>
        <div class="reminder-meta">
          <span v-if="task.due_date" class="reminder-due" :class="{ urgent: isUrgent(task.due_date) }">
            截止：{{ formatDate(task.due_date) }}
          </span>
          <span v-if="task.case_no" class="reminder-case">
            案件：{{ task.case_no }}
          </span>
          <span v-if="task.client_name" class="reminder-client">
            客户：{{ task.client_name }}
          </span>
          <span v-if="displayAssignee(task)" class="reminder-assignee">
            {{ displayAssignee(task) }}
          </span>
        </div>
        <div v-if="task.internal_due" class="reminder-secondary">
          内部期限：{{ formatDate(task.internal_due) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { getTodayReminders } from '../../../api/tasks'
import type { Task } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { getTaskStatusText } from '../../../constants/displayText'

const router = useRouter()

const reminders = ref<Task[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const viewMode = ref<'worker' | 'supervisor'>('worker')

const modeOptions = [
  { label: '我的任务', value: 'worker' },
  { label: '团队任务', value: 'supervisor' },
]

async function fetchReminders() {
  loading.value = true
  error.value = null
  try {
    const result = await getTodayReminders(viewMode.value)
    reminders.value = result.items
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function handleModeChange() {
  fetchReminders()
}

function handleTaskClick(task: Task) {
  if (task.case_id) {
    router.push(`/cases/${task.case_id}`)
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

function isUrgent(dueDate?: string): boolean {
  if (!dueDate) return false
  const due = dayjs(dueDate)
  const now = dayjs()
  return due.isSame(now, 'day') || due.isBefore(now, 'day')
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
    case 'pending':
      return 'info'
    default:
      return ''
  }
}

function displayAssignee(task: Task): string {
  if (viewMode.value === 'worker' && task.supervisor_id) {
    return `监督人：${task.supervisor_id}`
  }
  if (viewMode.value === 'supervisor' && task.worker_id) {
    return `负责人：${task.worker_id}`
  }
  return task.assigned_to ? `负责人：${task.assigned_to}` : ''
}

onMounted(() => {
  fetchReminders()
})
</script>

<style scoped>
.reminders-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reminder-card {
  background: var(--color-bg-panel);
  border: var(--border-panel);
  border-radius: var(--radius-base);
  padding: 16px;
  cursor: pointer;
  transition: var(--transition);
}

.reminder-card:hover {
  box-shadow: var(--shadow-card);
  border-color: var(--color-primary);
}

.reminder-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.reminder-id {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-sub);
}

.reminder-title {
  font-weight: 500;
  color: var(--text-main);
  margin-bottom: 8px;
}

.reminder-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: var(--text-sub);
}

.reminder-due {
  font-family: var(--font-mono);
}

.reminder-due.urgent {
  color: var(--color-danger);
  font-weight: 600;
}

.reminder-case {
  font-family: var(--font-mono);
}

.reminder-secondary {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-sub);
}

.reminder-card {
  position: relative;
}
</style>
