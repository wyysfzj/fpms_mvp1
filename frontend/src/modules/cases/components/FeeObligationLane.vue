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
      <h3>{{ statusText(obligation.obligationType) }}</h3>
      <p>义务编号：{{ obligation.obligationId }}</p>
      <p>费用域：{{ statusText(obligation.feeDomain) }}</p>
      <p>来源状态：{{ statusText(obligation.sourceStatus) }}</p>
      <p>来源活动：{{ obligation.sourceActivityId }}</p>
      <p>来源文书：{{ displayValue(obligation.sourceDocumentId) }}</p>
      <p>到期日：{{ displayValue(obligation.dueDate) }}</p>
      <p>币种：{{ obligation.currency }}</p>

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
        <p>费用代码：{{ line.feeCode }}</p>
        <p>费种年度：{{ line.feeYearKey }}</p>
        <p>官费全额：{{ displayValue(line.officialFullAmount) }}</p>
        <p>减缴比例：{{ line.reductionRatio }}</p>
        <p>应缴金额：{{ line.payableAmount }}</p>
        <p>来源金额：{{ displayValue(line.sourceAmount) }}</p>
        <p>来源日期：{{ displayValue(line.sourceDate) }}</p>
        <p>差额复核状态：{{ statusText(line.differenceReviewState) }}</p>
      </div>

      <p v-for="fact in obligation.relatedFacts" :key="`${fact.kind}-${fact.objectId}`">
        关联事实：{{ statusText(fact.kind) }} / {{ fact.objectId }} / {{ statusText(fact.status) }}
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

function latestObligationsById(
  milestones: readonly OverlayMilestone[],
): readonly OverlayFeeObligation[] {
  const latest = new Map<string, OverlayFeeObligation>()
  for (const milestone of milestones) {
    for (const obligation of milestone.feeObligations) {
      latest.set(obligation.obligationId, obligation)
    }
  }
  return [...latest.values()]
}

const obligations = computed<readonly OverlayFeeObligation[]>(() =>
  latestObligationsById(props.milestones),
)
const govObligations = computed(() => obligations.value.filter((item) => item.feeDomain === 'GOV'))
const serviceObligations = computed(() => obligations.value.filter((item) => item.feeDomain === 'SERVICE'))

const STATUS_TEXT: Readonly<Record<string, string>> = {
  GOV: '官费',
  SERVICE: '服务费',
  OFFICIAL_FEE: '官费缴费义务',
  SERVICE_FEE: '服务费应收义务',
  OPEN: '处理中',
  LOCKED: '已锁定',
  DRAFT: '草稿',
  PLANNED: '已计划',
  RECORDED: '已登记，待官方凭证核验',
  PAID: '已缴费',
  PARTIAL: '部分完成',
  UNSETTLED: '未结清',
  PARTIALLY_SETTLED: '部分结清',
  SETTLED: '已结清',
  PENDING: '待处理',
  NOT_AVAILABLE: '暂无',
  NOT_REQUIRED: '不需要',
  UNVERIFIED: '待核验',
  VERIFIED: '已核验',
  MATCHED: '一致',
  DIFFERENT: '存在差额',
  BILL: '客户账单',
  PAYMENT: '客户回款',
  OFFSET: '账单核销',
  GOV_PAYMENT: '官费登记',
}

function statusText(value: string | null): string {
  if (!value) return '暂无'
  return STATUS_TEXT[value.toUpperCase()] || '未识别状态'
}

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

.empty-state {
  margin-top: 16px;
  color: var(--text-secondary);
}
</style>
