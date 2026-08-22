<template>
  <section class="lifecycle-center-lane" data-testid="lifecycle-center-lane">
    <header class="lane-header">
      <p class="lane-kicker">中央主线</p>
      <h2>案件生命周期</h2>
    </header>

    <div class="current-state" aria-label="当前案件生命周期状态">
      <p>业务阶段：{{ displayState(snapshot.businessStage) }}</p>
      <p>官方程序阶段：{{ displayState(snapshot.officialProcedureStage) }}</p>
      <p>法律状态：{{ displayState(snapshot.legalStatus) }}</p>
      <p>核验状态：{{ displayState(snapshot.verificationStatus) }}</p>
      <p>生效时间：{{ displayPlainValue(snapshot.effectiveAt) }}</p>
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
        <p>生效时间：{{ milestone.effectiveAt }}</p>
        <p>核验状态：{{ displayState(milestone.confirmationStatus) }}</p>
        <p v-for="axis in changedAxes(milestone)" :key="axis.key">
          {{ axis.label }}：{{ displayState(axis.previousValue) }} →
          {{ displayState(axis.currentValue) }}
        </p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type {
  BusinessStage,
  ConfirmationStatus,
  LifecycleOverlay,
  LegalStatus,
  OfficialProcedureStage,
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

type CenterState = BusinessStage | OfficialProcedureStage | LegalStatus | ConfirmationStatus

const CENTER_STATE_LABELS = {
  NEW_CASE: '新建案件',
  FILING_PREPARATION: '递交准备',
  WAITING_EXTERNAL_RECEIPT: '等待外部回执',
  PROSECUTION_MANAGEMENT: '流程管理',
  OA_REPLY_IN_PROGRESS: '审查意见答复中',
  GRANT_REGISTRATION_IN_PROGRESS: '授权登记中',
  POST_GRANT_MAINTENANCE: '授权后维护',
  CLOSED: '已结案',
  NOT_SUBMITTED: '尚未递交',
  SUBMITTED_WAITING_RECEIPT: '已递交，等待回执',
  SUBMISSION_CONFIRMED_WAITING_ACCEPTANCE: '递交已确认，等待受理',
  ACCEPTED: '已受理',
  PRELIMINARY_EXAMINATION: '初步审查',
  RECTIFICATION_RESPONSE: '补正答复',
  PUBLISHED: '已公布',
  SUBSTANTIVE_EXAMINATION: '实质审查',
  OFFICE_ACTION_RESPONSE: '审查意见答复',
  REEXAMINATION: '复审',
  GRANT_REGISTRATION: '授权登记',
  GRANT_ANNOUNCED: '授权公告',
  PROCEDURE_CLOSED: '官方程序已结束',
  NOT_ESTABLISHED: '权利尚未成立',
  APPLICATION_PENDING: '申请审理中',
  APPLICATION_REJECTED: '申请已驳回',
  APPLICATION_WITHDRAWN: '申请已撤回',
  APPLICATION_ABANDONED: '申请已放弃',
  PATENT_IN_FORCE: '专利权有效',
  PATENT_TERMINATED: '专利权终止',
  PATENT_EXPIRED: '专利权期限届满',
  PATENT_INVALIDATED: '专利权无效',
  UNKNOWN: '状态未知',
  NEEDS_REVIEW: '需复核',
  CONFIRMED: '已确认',
  LEGACY_UNVERIFIED: '历史数据待核验',
} as const satisfies Readonly<Record<CenterState, string>>

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

function displayState(value: string | null): string {
  if (value === null) return '-'
  return CENTER_STATE_LABELS[value as CenterState] ?? '未识别状态'
}

function displayPlainValue(value: string | null): string {
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
