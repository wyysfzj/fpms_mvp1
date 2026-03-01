<template>
  <div class="panel">
    <div class="panel-header">
      <span class="panel-title">{{ ZH.actionCenter.title }}</span>
      <router-link to="/tasks" class="panel-link">{{ ZH.actionCenter.viewAll }}</router-link>
    </div>

    <el-skeleton v-if="loading" :rows="4" animated style="padding: 18px;" />

    <div v-else-if="tasks.length === 0" class="panel-empty">
      暂无待办任务
    </div>

    <template v-else>
      <div
        v-for="task in tasks"
        :key="task.id"
        class="list-item"
        @click="onRowClick(task)"
      >
        <div class="task-main">
          <div class="task-title-row">
            <span v-if="task.case_no" class="case-tag">{{ task.case_no }}</span>
            <span class="task-title">{{ task.title }}</span>
          </div>
          <div class="task-sub-row">
            <span v-if="task.client_name">{{ task.client_name }}</span>
            <span v-if="task.has_document" class="rel-tag doc">{{ ZH.actionCenter.relDoc }}</span>
            <span v-if="task.has_fee" class="rel-tag fee">{{ ZH.actionCenter.relFee }}</span>
          </div>
        </div>
        <span v-if="task.deadline_text" :class="['badge', task.deadline_class]">
          {{ task.deadline_text }}
        </span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ZH } from '../../../constants/labels.zh'

export interface EnrichedTask {
  id: string
  title: string
  case_id?: string
  case_no?: string
  client_name?: string
  has_document: boolean
  has_fee: boolean
  deadline_text: string
  deadline_class: string
}

defineProps<{
  tasks: EnrichedTask[]
  loading: boolean
}>()

const router = useRouter()

function onRowClick(task: EnrichedTask) {
  if (task.case_id) {
    router.push(`/cases/${task.case_id}`)
  }
}
</script>
