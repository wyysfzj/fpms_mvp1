<template>
  <section class="fee-obligation-lane" data-testid="fee-obligation-lane">
    <header class="lane-header">
      <p class="lane-kicker">右侧费用线</p>
      <h2>同案双轨费用概览</h2>
    </header>

    <div class="track-summary">
      <p>官费轨：{{ govObligations.length }} 项，以费率来源和官方证据状态为准。</p>
      <p>服务费轨：{{ serviceObligations.length }} 项，余额以客户账单页为准。</p>
    </div>

    <p v-if="obligations.length === 0" class="empty-state">暂无费用义务事实</p>
    <article
      v-for="obligation in obligations"
      :key="obligation.obligationId"
      class="obligation-card"
      :data-testid="`fee-obligation-${obligation.obligationId}`"
    >
      <h3>{{ statusText(obligation.obligationType, '费用类型待确认') }}</h3>
      <p>费用域：{{ statusText(obligation.feeDomain) }}</p>
      <p>来源状态：{{ statusText(obligation.sourceStatus) }}</p>
      <p>到期日：{{ overlayDateText(obligation.dueDate) }}</p>
      <p>币种：{{ currencyText(obligation.currency) }}</p>

      <div class="status-grid" aria-label="费用义务七状态">
        <p>估算状态：{{ statusText(obligation.statuses.estimateStatus) }}</p>
        <p>义务状态：{{ statusText(obligation.statuses.obligationStatus) }}</p>
        <p>客户指示状态：{{ statusText(obligation.statuses.clientInstructionStatus) }}</p>
        <p>草单状态：{{ statusText(obligation.statuses.draftStatus) }}</p>
        <p>缴费清单状态：{{ statusText(obligation.statuses.payListStatus) }}</p>
        <p>付款状态：{{ statusText(obligation.statuses.paymentStatus) }}</p>
        <p>官方证据状态：{{ statusText(obligation.statuses.officialEvidenceStatus) }}</p>
      </div>

      <div v-for="line in obligation.lines" :key="line.lineId" class="fee-line">
        <h4>{{ line.feeName }}</h4>
        <p v-if="line.feeYearKey !== 0">费种年度：{{ line.feeYearKey }}</p>
        <p>官费全额：{{ displayValue(line.officialFullAmount) }}</p>
        <p>减缴比例：{{ line.reductionRatio }}</p>
        <p>应缴金额：{{ line.payableAmount }}</p>
        <p>来源金额：{{ displayValue(line.sourceAmount) }}</p>
        <p>来源日期：{{ overlayDateText(line.sourceDate) }}</p>
        <p>差额复核状态：{{ statusText(line.differenceReviewState) }}</p>
      </div>

      <p v-for="fact in obligation.relatedFacts" :key="`${fact.kind}-${fact.objectId}`">
        关联事实：{{ statusText(fact.kind) }} / {{ statusText(fact.status) }}
      </p>
      <p v-if="obligation.supersedeReason">替代理由：{{ obligation.supersedeReason }}</p>

      <details class="audit-details">
        <summary>审计信息</summary>
        <p>义务编号：{{ obligation.obligationId }}</p>
        <p>来源活动：{{ obligation.sourceActivityId }}</p>
        <p>来源文书：{{ displayValue(obligation.sourceDocumentId) }}</p>
        <p>原始费用域：{{ obligation.feeDomain }}</p>
        <p>原始义务类型：{{ obligation.obligationType }}</p>
        <p>原始来源状态：{{ obligation.sourceStatus }}</p>
        <p>原始估算状态：{{ displayValue(obligation.statuses.estimateStatus) }}</p>
        <p>原始义务状态：{{ obligation.statuses.obligationStatus }}</p>
        <p>原始客户指示：{{ obligation.statuses.clientInstructionStatus }}</p>
        <p>原始草单状态：{{ obligation.statuses.draftStatus }}</p>
        <p>原始缴费清单状态：{{ obligation.statuses.payListStatus }}</p>
        <p>原始付款状态：{{ obligation.statuses.paymentStatus }}</p>
        <p>原始官方证据状态：{{ obligation.statuses.officialEvidenceStatus }}</p>
        <template v-for="line in obligation.lines" :key="`audit-${line.lineId}`">
          <p>费用行编号：{{ line.lineId }}</p>
          <p>费用代码：{{ line.feeCode }}</p>
          <p>费种年度：{{ line.feeYearKey }}</p>
          <p>原始差额复核状态：{{ line.differenceReviewState }}</p>
        </template>
        <template v-for="fact in obligation.relatedFacts" :key="`audit-${fact.kind}-${fact.objectId}`">
          <p>关联事实编号：{{ fact.objectId }}</p>
          <p>原始关联事实：{{ fact.kind }} / {{ fact.status }}</p>
        </template>
        <p>替代前义务：{{ displayValue(obligation.supersedesObligationId) }}</p>
      </details>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OverlayFeeObligation, OverlayMilestone } from '../../../api/lifecycleOverlay.types'
import {
  currencyText,
  feeStatusText,
  latestObligationsById,
  overlayDateText,
} from './lifecycleOverlayDisplay'

const props = defineProps<{
  milestones: readonly OverlayMilestone[]
}>()

const obligations = computed<readonly OverlayFeeObligation[]>(() =>
  latestObligationsById(props.milestones),
)
const govObligations = computed(() => obligations.value.filter((item) => item.feeDomain === 'GOV'))
const serviceObligations = computed(() => obligations.value.filter((item) => item.feeDomain === 'SERVICE'))

function statusText(value: string | null, fallback = '待确认'): string {
  return feeStatusText(value, fallback)
}

function displayValue(value: string | null): string {
  return value || '暂无'
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

.track-summary {
  display: grid;
  gap: 6px;
  margin-top: 12px;
  padding: 10px;
  border-radius: 10px;
  background: var(--bg-page);
}

.track-summary p {
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

.audit-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--color-border);
}

.audit-details summary {
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
}

.empty-state {
  margin-top: 16px;
  color: var(--text-secondary);
}
</style>
