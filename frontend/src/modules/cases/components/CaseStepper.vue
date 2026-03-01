<template>
  <div class="case-stepper-section">
    <!-- Stepper bar -->
    <div class="stepper">
      <div
        v-for="(step, idx) in steps"
        :key="step.key"
        class="step"
        :class="stepClass(idx)"
      >
        {{ idx + 1 }}. {{ step.label }}
      </div>
    </div>

    <!-- KPI 4 cards -->
    <div class="flow-state-card">
      <div class="flow-kpi-box">
        <div class="flow-kpi-label">{{ ZH.stepper.currentStep }}</div>
        <div class="flow-kpi-value">{{ flow.stepLabel }}</div>
      </div>
      <div class="flow-kpi-box">
        <div class="flow-kpi-label">{{ ZH.stepper.stepIndex }}</div>
        <div class="flow-kpi-value">{{ flow.stepNoText }}</div>
      </div>
      <div class="flow-kpi-box">
        <div class="flow-kpi-label">{{ ZH.stepper.legalStatus }}</div>
        <div class="flow-kpi-value">{{ flow.rule.legalText }}</div>
      </div>
      <div class="flow-kpi-box">
        <div class="flow-kpi-label">{{ ZH.stepper.nextAction }}</div>
        <div class="flow-kpi-value small">{{ flow.rule.nextAction }}</div>
      </div>
    </div>

    <!-- Branch note -->
    <div v-if="flow.rule.branchNote" class="alert-note">
      {{ flow.rule.branchNote }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { WORKFLOW_STEPS, getCaseWorkflow } from '../../../constants/workflow'
import { ZH } from '../../../constants/labels.zh'

const props = defineProps<{
  status?: string
}>()

const steps = WORKFLOW_STEPS

const flow = computed(() => getCaseWorkflow(props.status))

function stepClass(idx: number): string {
  if (idx < flow.value.stepIndex) return 'done'
  if (idx === flow.value.stepIndex) return 'active'
  return ''
}
</script>
