<template>
  <div class="workflow-overview panel">
    <div class="panel-header">
      <div class="panel-title">{{ ZH.workflow.title }}</div>
      <button class="wf-view-all-btn" @click="emit('clear')">
        {{ ZH.workflow.viewAll }}
      </button>
    </div>
    <div class="workflow-grid">
      <div
        v-for="step in steps"
        :key="step.key"
        class="wf-card"
        :class="{ selected: selectedStep === step.key }"
        @click="emit('select', step.key)"
      >
        <div class="wf-topline" :style="{ background: step.color }"></div>
        <div class="wf-title">{{ step.label }}</div>
        <div class="wf-count">{{ step.count }}</div>
        <div class="wf-hint">占比 {{ step.percent }}% · 点击查看</div>
      </div>
    </div>
    <div class="summary-note">
      <span>当前共 {{ total }} 件案件在主干流程中</span>
      <span>{{ ZH.workflow.summaryHint }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ZH } from '../../../constants/labels.zh'
import type { WorkflowStepStat } from '../dashboard.api'

defineProps<{
  steps: WorkflowStepStat[]
  total: number
  selectedStep: string | null
}>()

const emit = defineEmits<{
  select: [stepKey: string]
  clear: []
}>()
</script>

<style scoped>
.wf-view-all-btn {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid var(--border, #e2e8f0);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  background: white;
  color: var(--text-main, #0f172a);
}
.wf-view-all-btn:hover {
  border-color: #cbd5e1;
}
</style>
