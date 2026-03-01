<template>
  <div>
    <div class="related-tasks-title">{{ ZH.relatedTasks.title }}</div>
    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="tasks.length === 0" class="muted">{{ ZH.relatedTasks.noTasks }}</div>
    <div v-else>
      <div
        v-for="task in tasks"
        :key="task.id"
        class="related-task-item"
      >
        <div>{{ task.title }}</div>
        <div class="muted" v-if="task.due_date">截止: {{ task.due_date }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTasks } from '../../../api/tasks'
import type { Task } from '../../../api/tasks.types'
import { ZH } from '../../../constants/labels.zh'

const props = defineProps<{
  caseId: string
}>()

const tasks = ref<Task[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getTasks({ page: 1, page_size: 50, status: 'OPEN' })
    tasks.value = res.items.filter(t => t.case_id === props.caseId)
  } catch {
    // silently fail
  } finally {
    loading.value = false
  }
})
</script>
