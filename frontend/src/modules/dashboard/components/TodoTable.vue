<template>
  <div class="data-panel">
    <div class="panel-header">
      <h3 class="panel-title">待办任务</h3>
      <el-button type="primary" size="small" @click="$router.push('/tasks')">
        查看全部
      </el-button>
    </div>

    <el-skeleton v-if="loading" :rows="4" animated />

    <div v-else-if="tasks.length === 0" class="todo-empty">
      暂无待办任务
    </div>

    <el-table v-else :data="tasks" stripe size="small" class="todo-table">
      <el-table-column prop="title" label="任务标题" min-width="200" />
      <el-table-column label="关联案件" width="140">
        <template #default="{ row }">
          <router-link
            v-if="row.case_id"
            :to="`/cases/${row.case_id}`"
            class="chain-link"
          >
            {{ row.case_no || row.case_id.slice(0, 8) + '...' }}
          </router-link>
          <span v-else class="text-muted">—</span>
        </template>
      </el-table-column>
      <el-table-column label="客户" width="160">
        <template #default="{ row }">
          {{ row.client_name || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="期限" width="140">
        <template #default="{ row }">
          <span :class="{ 'text-danger': isUrgent(row.due_date) }">
            {{ row.due_date || '—' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <span :class="['status-tag', statusClass(row.status)]">
            {{ statusLabel(row.status) }}
          </span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import type { Task } from '../../../api/tasks.types'

defineProps<{
  tasks: Task[]
  loading: boolean
}>()

function isUrgent(dueDate?: string): boolean {
  if (!dueDate) return false
  const due = new Date(dueDate)
  const now = new Date()
  const diffDays = (due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  return diffDays <= 3 && diffDays >= 0
}

function statusClass(status: string): string {
  switch (status) {
    case 'OPEN': return 'tag-warning'
    case 'DONE': return 'tag-normal'
    case 'CANCELLED': return 'tag-urgent'
    default: return 'tag-warning'
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case 'OPEN': return '待处理'
    case 'DONE': return '已完成'
    case 'CANCELLED': return '已取消'
    default: return status
  }
}
</script>
