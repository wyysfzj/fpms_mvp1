<template>
  <div class="task-log-timeline">
    <!-- Loading -->
    <div v-if="loading" class="timeline-loading">
      <el-skeleton :rows="4" animated />
    </div>

    <!-- Empty -->
    <div v-else-if="logs.length === 0" class="timeline-empty">
      <span class="timeline-empty-text">暂无操作日志</span>
    </div>

    <!-- Timeline -->
    <el-timeline v-else>
      <el-timeline-item
        v-for="log in logs"
        :key="log.id"
        :timestamp="formatTime(log.created_at)"
        placement="top"
      >
        <div class="log-item">
          <span class="log-action">{{ getActionLabel(log.action) }}</span>
          <span v-if="log.from_status || log.to_status" class="log-transition">
            {{ getStatusLabel(log.from_status) }} → {{ getStatusLabel(log.to_status) }}
          </span>
          <p v-if="log.remark" class="log-remark">{{ log.remark }}</p>
        </div>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import dayjs from 'dayjs'
import { getTaskLogs } from '../../../api/tasks'
import type { TaskLog } from '../../../api/tasks.types'
import { getTaskStatusText } from '../../../constants/displayText'

const props = defineProps<{
  taskId: string
}>()

const logs = ref<TaskLog[]>([])
const loading = ref(false)

const ACTION_LABELS: Record<string, string> = {
  CREATE: '创建任务',
  UPDATE: '更新任务',
  ASSIGN: '分配任务',
  CLOSE: '关闭任务',
  REOPEN: '重新打开',
  CANCEL: '取消任务',
  AUTO_CREATE: '自动创建',
  AUTO_CREATE_FROM_DOCUMENT: '文档自动创建',
  AUTO_WRITEOFF: '自动核销',
  STATUS_CHANGE: '状态变更',
}

function getActionLabel(action: string): string {
  return ACTION_LABELS[action] || action
}

function getStatusLabel(status?: string): string {
  if (!status) return '-'
  return getTaskStatusText(status)
}

function formatTime(dateStr: string): string {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

async function fetchLogs() {
  loading.value = true
  try {
    logs.value = await getTaskLogs(props.taskId)
  } catch {
    logs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
})

watch(() => props.taskId, () => {
  fetchLogs()
})
</script>

<style scoped>
.task-log-timeline {
  padding: 8px 0;
}

.timeline-loading {
  padding: 16px 0;
}

.timeline-empty {
  text-align: center;
  padding: 32px 0;
}

.timeline-empty-text {
  font-size: 14px;
  color: var(--text-sub);
}

.log-item {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: baseline;
}

.log-action {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
}

.log-transition {
  font-size: 13px;
  color: var(--text-sub);
  font-family: var(--font-mono);
}

.log-remark {
  width: 100%;
  margin: 4px 0 0 0;
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.5;
}
</style>
