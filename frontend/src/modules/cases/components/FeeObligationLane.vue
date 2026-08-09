<template>
  <section class="fee-obligation-lane" data-testid="fee-obligation-lane">
    <header class="lane-header">
      <p class="lane-kicker">右侧费用线</p>
      <h2>费用节点</h2>
    </header>

    <p v-if="obligations.length === 0" class="empty-state">暂无费用义务事实</p>
    <article
      v-for="obligation in obligations"
      :key="obligation.obligationId"
      class="obligation-card"
      :data-testid="`fee-obligation-${obligation.obligationId}`"
    >
      <h3>{{ obligation.obligationType }}</h3>
      <p>义务编号：{{ obligation.obligationId }}</p>
      <p>费用域：{{ obligation.feeDomain }}</p>
      <p>来源状态：{{ obligation.sourceStatus }}</p>
      <p>来源活动：{{ obligation.sourceActivityId }}</p>
      <p>来源文书：{{ displayValue(obligation.sourceDocumentId) }}</p>
      <p>到期日：{{ displayValue(obligation.dueDate) }}</p>
      <p>币种：{{ obligation.currency }}</p>

      <div class="status-grid" aria-label="费用义务七状态">
        <p>估算状态：{{ displayValue(obligation.statuses.estimateStatus) }}</p>
        <p>义务状态：{{ obligation.statuses.obligationStatus }}</p>
        <p>客户指示状态：{{ obligation.statuses.clientInstructionStatus }}</p>
        <p>草单状态：{{ obligation.statuses.draftStatus }}</p>
        <p>缴费清单状态：{{ obligation.statuses.payListStatus }}</p>
        <p>付款状态：{{ obligation.statuses.paymentStatus }}</p>
        <p>官方证据状态：{{ obligation.statuses.officialEvidenceStatus }}</p>
      </div>

      <div v-for="line in obligation.lines" :key="line.lineId" class="fee-line">
        <h4>{{ line.feeName }}</h4>
        <p>费用代码：{{ line.feeCode }}</p>
        <p>费种年度：{{ line.feeYearKey }}</p>
        <p>官费全额：{{ displayValue(line.officialFullAmount) }}</p>
        <p>减缴比例：{{ line.reductionRatio }}</p>
        <p>应缴金额：{{ line.payableAmount }}</p>
        <p>来源金额：{{ displayValue(line.sourceAmount) }}</p>
        <p>来源日期：{{ displayValue(line.sourceDate) }}</p>
        <p>差额复核状态：{{ line.differenceReviewState }}</p>
      </div>

      <p v-for="fact in obligation.relatedFacts" :key="`${fact.kind}-${fact.objectId}`">
        关联事实：{{ fact.kind }} / {{ fact.objectId }} / {{ fact.status }}
      </p>
      <p>替代前义务：{{ displayValue(obligation.supersedesObligationId) }}</p>
      <p>替代理由：{{ displayValue(obligation.supersedeReason) }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OverlayFeeObligation, OverlayMilestone } from '../../../api/lifecycleOverlay.types'

const props = defineProps<{
  milestones: readonly OverlayMilestone[]
}>()

const obligations = computed<readonly OverlayFeeObligation[]>(() =>
  props.milestones.flatMap((milestone) => milestone.feeObligations),
)

function displayValue(value: string | null): string {
  return value ?? '-'
}
</script>

<style scoped>
.fee-obligation-lane {
  min-width: 0;
  padding: 18px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--bg-card);
}

.lane-header h2,
.obligation-card h3,
.fee-line h4 {
  margin: 0;
}

.lane-kicker {
  margin: 0 0 4px;
  color: var(--el-color-warning);
  font-size: 12px;
  font-weight: 600;
}

.obligation-card,
.fee-line,
.status-grid {
  display: grid;
  gap: 6px;
}

.obligation-card {
  margin-top: 16px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}

.status-grid,
.fee-line {
  margin-top: 6px;
  padding: 10px;
  background: var(--bg-page);
}

.obligation-card p,
.fee-line p,
.status-grid p,
.empty-state {
  margin: 0;
  overflow-wrap: anywhere;
}

.empty-state {
  margin-top: 16px;
  color: var(--text-secondary);
}
</style>
