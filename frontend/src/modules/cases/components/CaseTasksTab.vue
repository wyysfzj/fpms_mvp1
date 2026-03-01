<template>
  <div class="case-panel">
    <div class="panel-toolbar">
      <h3 class="panel-heading">任务记录</h3>
      <el-button type="primary" size="small" @click="handleCreate">新建任务</el-button>
    </div>
    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="items.length === 0" class="placeholder-content">
      <p>暂无任务记录</p>
    </div>
    <el-table v-else :data="items" stripe style="width: 100%">
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="due_date" label="截止日期" width="120" />
      <el-table-column prop="assigned_to" label="执行人" width="120" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTasks } from '../../../api/tasks'
import type { Task } from '../../../api/tasks.types'

const props = defineProps<{
  caseId: string
}>()

const router = useRouter()
const items = ref<Task[]>([])
const loading = ref(true)

function statusTagType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'warning'
    case 'CLOSED': return 'success'
    case 'CANCELLED': return 'info'
    default: return ''
  }
}

onMounted(async () => {
  try {
    const res = await getTasks({ case_id: props.caseId, page: 1, page_size: 50 })
    items.value = res.items
  } catch {
    // silently fail
  } finally {
    loading.value = false
  }
})

function handleCreate() {
  router.push(`/tasks/new?case_id=${props.caseId}`)
}
</script>
