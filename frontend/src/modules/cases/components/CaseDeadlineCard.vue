<template>
  <div class="deadline-card" v-if="deadline">
    <div class="deadline-card-title">{{ ZH.deadline.title }}</div>
    <div class="deadline-date">{{ deadline.date }}</div>
    <div class="deadline-left">{{ deadline.leftText }}</div>
  </div>
  <div v-else class="muted" style="margin-bottom: 14px;">
    {{ ZH.deadline.noDeadline }}
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getTasks } from '../../../api/tasks'
import { ZH } from '../../../constants/labels.zh'

const props = defineProps<{
  caseId: string
}>()

const nearestDueDate = ref<string | null>(null)

const deadline = computed(() => {
  if (!nearestDueDate.value) return null
  const due = new Date(nearestDueDate.value)
  const now = new Date()
  const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  let leftText: string
  if (diffDays < 0) {
    leftText = `已逾期 ${Math.abs(diffDays)} 天`
  } else {
    leftText = `剩余 ${diffDays} 天`
  }
  return {
    date: nearestDueDate.value,
    leftText,
  }
})

onMounted(async () => {
  try {
    const res = await getTasks({ page: 1, page_size: 50, status: 'OPEN' })
    const caseTasks = res.items.filter(t => t.case_id === props.caseId && t.due_date)
    if (caseTasks.length > 0) {
      caseTasks.sort((a, b) => new Date(a.due_date!).getTime() - new Date(b.due_date!).getTime())
      nearestDueDate.value = caseTasks[0].due_date!
    }
  } catch {
    // silently fail
  }
})
</script>
