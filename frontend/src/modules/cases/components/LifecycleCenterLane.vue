<template>
  <section class="lifecycle-center-lane" data-testid="lifecycle-center-lane">
    <header class="lane-header">
      <p class="lane-kicker">中央主线</p>
      <h2>案件生命周期</h2>
    </header>

    <div class="current-state" aria-label="当前案件生命周期状态">
      <p>业务阶段：{{ displayValue(snapshot.businessStage) }}</p>
      <p>官方程序阶段：{{ displayValue(snapshot.officialProcedureStage) }}</p>
      <p>法律状态：{{ displayValue(snapshot.legalStatus) }}</p>
      <p>核验状态：{{ displayValue(snapshot.verificationStatus) }}</p>
      <p>生效时间：{{ displayValue(snapshot.effectiveAt) }}</p>
      <p>来源事件：{{ displayValue(snapshot.sourceEventId) }}</p>
    </div>

    <div class="confirmed-changes">
      <h3>已确认的中心变化</h3>
      <p v-if="confirmedChanges.length === 0" class="empty-state">暂无已确认的中心变化</p>
      <article
        v-for="milestone in confirmedChanges"
        :key="milestone.activityId"
        class="change-card"
        :data-testid="`center-change-${milestone.activityId}`"
      >
        <p>事件类型：{{ milestone.activityType }}</p>
        <p>生效时间：{{ milestone.effectiveAt }}</p>
        <p>核验状态：{{ milestone.confirmationStatus }}</p>
        <p v-for="axis in changedAxes(milestone)" :key="axis.key">
          {{ axis.label }}：{{ displayValue(axis.previousValue) }} →
          {{ displayValue(axis.currentValue) }}
        </p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type {
  LifecycleOverlay,
  OverlayCenterAxis,
  OverlayMilestone,
} from '../../../api/lifecycleOverlay.types'

const props = defineProps<{
  snapshot: LifecycleOverlay['centerSnapshot']
  milestones: readonly OverlayMilestone[]
}>()

const AXES: ReadonlyArray<{ key: OverlayCenterAxis; label: string }> = [
  { key: 'BUSINESS_STAGE', label: '业务阶段' },
  { key: 'OFFICIAL_PROCEDURE_STAGE', label: '官方程序阶段' },
  { key: 'LEGAL_STATUS', label: '法律状态' },
]

const confirmedChanges = computed(() =>
  props.milestones.filter(
    (milestone) =>
      milestone.confirmationStatus === 'CONFIRMED' && changedAxes(milestone).length > 0,
  ),
)

function changedAxes(milestone: OverlayMilestone) {
  return AXES.flatMap(({ key, label }) => {
    const change = milestone.centerChanges[key]
    return change ? [{ key, label, ...change }] : []
  })
}

function displayValue(value: string | null): string {
  return value ?? '-'
}
</script>

<style scoped>
.lifecycle-center-lane {
  min-width: 0;
  padding: 20px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--bg-card);
}

.lane-header h2,
.confirmed-changes h3 {
  margin: 0;
}

.lane-kicker {
  margin: 0 0 4px;
  color: var(--el-color-primary);
  font-size: 12px;
  font-weight: 600;
}

.current-state {
  margin-top: 16px;
  padding: 14px;
  border-left: 3px solid var(--el-color-primary);
  background: var(--bg-page);
}

.current-state p,
.change-card p {
  margin: 4px 0;
  overflow-wrap: anywhere;
}

.confirmed-changes {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}

.change-card {
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}

.empty-state {
  margin: 0;
  color: var(--text-secondary);
}
</style>
