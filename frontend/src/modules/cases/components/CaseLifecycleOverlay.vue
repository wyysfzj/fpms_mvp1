<template>
  <section class="case-lifecycle-overlay" data-testid="case-lifecycle-overlay">
    <div v-if="loading" class="overlay-loading">正在加载三线生命周期…</div>
    <ApiErrorBanner v-else-if="error" :error="error" :dismissable="false" />
    <template v-else-if="overlay">
      <header class="overlay-meta">
        <span>快照修订：{{ overlay.lifecycleRevision }}</span>
        <span>生成时间：{{ overlay.generatedAt }}</span>
      </header>

      <div class="lifecycle-summary-grid" data-testid="lifecycle-summary-grid">
        <LifecycleSummaryCard
          test-id="lifecycle-summary-document"
          kicker="左侧证据线"
          title="文件证据"
          :status-label="documentSummary.statusLabel"
          :current-lines="documentSummary.currentLines"
          :latest-text="documentSummary.latestText"
          :latest-at="documentSummary.latestAt"
          :next-text="documentSummary.nextText"
          :next-at="documentSummary.nextAt"
        />
        <LifecycleSummaryCard
          test-id="lifecycle-summary-lifecycle"
          kicker="中央主线"
          title="案件生命周期"
          :status-label="lifecycleSummary.statusLabel"
          :current-lines="lifecycleSummary.currentLines"
          :latest-text="lifecycleSummary.latestText"
          :latest-at="lifecycleSummary.latestAt"
          :next-text="lifecycleSummary.nextText"
          :next-at="lifecycleSummary.nextAt"
          emphasis
        />
        <LifecycleSummaryCard
          test-id="lifecycle-summary-fee"
          kicker="右侧费用线"
          title="费用义务"
          :status-label="feeSummary.statusLabel"
          :current-lines="feeSummary.currentLines"
          :latest-text="feeSummary.latestText"
          :latest-at="feeSummary.latestAt"
          :next-text="feeSummary.nextText"
          :next-at="feeSummary.nextAt"
          footnote="服务费余额以客户账单页为准"
        />
      </div>

      <section
        v-if="warningProjection.snapshot.length > 0 || warningProjection.activities.length > 0"
        class="overlay-warning-projection"
        data-testid="overlay-visible-warnings"
      >
        <h2>{{ overlay.hasMore ? '当前已加载警告' : '客户可见警告' }}</h2>
        <section
          v-if="warningProjection.snapshot.length > 0"
          class="overlay-facts"
          data-testid="overlay-snapshot-warnings"
        >
          <h3>当前快照警告</h3>
          <article
            v-for="warning in warningProjection.snapshot"
            :key="warningKey(warning)"
            class="warning-row"
          >
            <p>{{ warningKindLabel(warning.kind) }}</p>
            <p>{{ warning.message }}</p>
            <p>警告代码：{{ warning.code }}</p>
            <p>关联活动：{{ displayValue(warning.activityId) }}</p>
            <p>
              来源对象：{{ displayValue(warning.sourceObjectType) }} /
              {{ displayValue(warning.sourceObjectId) }}
            </p>
          </article>
        </section>
        <section
          v-for="entry in warningProjection.activities"
          :key="entry.activityId"
          class="overlay-facts"
          :data-testid="`overlay-activity-warnings-${entry.activityId}`"
        >
          <h3>活动局部警告</h3>
          <p>活动编号：{{ entry.activityId }}</p>
          <article v-for="warning in entry.warnings" :key="warningKey(warning)" class="warning-row">
            <p>{{ warningKindLabel(warning.kind) }}</p>
            <p>{{ warning.message }}</p>
            <p>警告代码：{{ warning.code }}</p>
            <p>关联活动：{{ displayValue(warning.activityId) }}</p>
            <p>
              来源对象：{{ displayValue(warning.sourceObjectType) }} /
              {{ displayValue(warning.sourceObjectId) }}
            </p>
          </article>
        </section>
      </section>

      <div class="history-disclosure">
        <el-button
          data-testid="lifecycle-history-toggle"
          :aria-expanded="historyExpanded"
          aria-controls="lifecycle-history-details"
          @click="historyExpanded = !historyExpanded"
        >
          {{ historyExpanded ? '收起完整历史' : '查看完整历史' }}
        </el-button>
      </div>

      <div
        v-if="historyExpanded"
        id="lifecycle-history-details"
        data-testid="lifecycle-history-details"
      >
        <p class="history-boundary">
          以下为历史事实与审计追溯，不代表当前节点阻断；当前状态以上方摘要为准。
        </p>
        <div class="overlay-grid">
          <div data-overlay-lane="document">
            <DocumentEvidenceLane :milestones="overlay.milestones" />
          </div>
          <div data-overlay-lane="lifecycle">
            <LifecycleCenterLane
              :snapshot="overlay.centerSnapshot"
              :milestones="overlay.milestones"
            />
          </div>
          <div data-overlay-lane="fee">
            <FeeObligationLane :milestones="overlay.milestones" />
          </div>
        </div>

        <ApiErrorBanner v-if="loadMoreError" :error="loadMoreError" :dismissable="false" />
        <div class="overlay-pagination">
          <el-button
            v-if="overlay.hasMore"
            :loading="loadingMore"
            :disabled="overlay.nextCursor === null"
            @click="loadMoreOverlay"
          >
            加载更多生命周期记录
          </el-button>
          <span v-else>已加载全部生命周期记录</span>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getLifecycleOverlay } from '../../../api/lifecycleOverlay'
import type {
  ActivityLane,
  LifecycleOverlay,
  OverlayCenterAxis,
  OverlayFeeObligation,
  OverlayMilestone,
  OverlayTask,
  OverlayWarning,
  OverlayWarningKind,
} from '../../../api/lifecycleOverlay.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import DocumentEvidenceLane from './DocumentEvidenceLane.vue'
import FeeObligationLane from './FeeObligationLane.vue'
import LifecycleCenterLane from './LifecycleCenterLane.vue'
import LifecycleSummaryCard from './LifecycleSummaryCard.vue'
import {
  activityTypeText,
  centerStateText,
  currencyText,
  feeStatusText,
  latestObligationsById,
} from './lifecycleOverlayDisplay'

const INCOMPLETE_HISTORY = '尚有历史未加载，完整状态待确认'
const NO_NEXT_TASK = '暂无明确下一步'
const CENTER_AXES: ReadonlyArray<{ key: OverlayCenterAxis; label: string }> = [
  { key: 'BUSINESS_STAGE', label: '业务阶段' },
  { key: 'OFFICIAL_PROCEDURE_STAGE', label: '官方程序阶段' },
  { key: 'LEGAL_STATUS', label: '法律状态' },
]

interface SummaryProjection {
  statusLabel: string
  currentLines: readonly string[]
  latestText: string
  latestAt: string | null
  nextText: string
  nextAt: string | null
}

interface WarningActivityProjection {
  activityId: string
  warnings: readonly OverlayWarning[]
}

const props = defineProps<{
  caseId: string
}>()
const emit = defineEmits<{
  loaded: [overlay: LifecycleOverlay]
  failed: [error: ApiError]
}>()

const overlay = ref<LifecycleOverlay | null>(null)
const loading = ref(true)
const error = ref<ApiError | null>(null)
const traversalRevision = ref<number | null>(null)
const loadingMore = ref(false)
const loadMoreError = ref<ApiError | null>(null)
const historyExpanded = ref(false)

const warningKindLabels: Readonly<Record<OverlayWarningKind, string>> = {
  UNVERIFIED: '未核验',
  CUSTOMER_DECISION_GATE: '客户待确认',
  CONFLICT: '来源冲突',
  REFERENCE_ONLY: '仅供参考',
}

const documentSummary = computed<SummaryProjection>(() => {
  const current = overlay.value
  if (!current) return emptySummary('暂无文件证据事实')
  const next = current.hasMore ? null : nextOpenTask(current.milestones)
  if (current.hasMore) {
    return {
      statusLabel: '历史未完整',
      currentLines: [INCOMPLETE_HISTORY],
      latestText: INCOMPLETE_HISTORY,
      latestAt: null,
      nextText: INCOMPLETE_HISTORY,
      nextAt: null,
    }
  }
  const versions = currentEvidenceVersions(current.milestones)
  const hasEvidence = current.milestones.some((milestone) => milestone.documentEvidence.length > 0)
  const reviewCounts = new Map<string, number>()
  for (const version of versions) {
    reviewCounts.set(version.reviewState, (reviewCounts.get(version.reviewState) ?? 0) + 1)
  }
  const reviewText = [
    ['APPROVED', '已复核'],
    ['PENDING', '待复核'],
    ['REJECTED', '复核未通过'],
  ]
    .flatMap(([state, label]) => {
      const count = reviewCounts.get(state) ?? 0
      return count > 0 ? [`${label} ${count}`] : []
    })
    .join('、')
  const currentLines = versions.length > 0
    ? [`当前文件版本 ${versions.length} 份`, reviewText]
    : [hasEvidence ? '已有文件事实，暂无当前版本' : '暂无文件证据事实']
  const latest = latestMilestone(current.milestones, 'DOCUMENT')
  return {
    statusLabel: documentStatusLabel(reviewCounts, versions.length),
    currentLines,
    latestText: latest ? activityTypeText(latest.activityType, '文件活动待确认') : '暂无文件证据变化',
    latestAt: latest?.effectiveAt ?? null,
    nextText: nextTaskText(next),
    nextAt: nextTaskDate(next),
  }
})

const lifecycleSummary = computed<SummaryProjection>(() => {
  const current = overlay.value
  if (!current) return emptySummary('官方程序阶段：暂无')
  const snapshot = current.centerSnapshot
  const latest = current.hasMore ? null : latestConfirmedCenterChange(current.milestones)
  const next = current.hasMore ? null : nextOpenTask(current.milestones)
  return {
    statusLabel: centerStateText(snapshot.officialProcedureStage, '暂无'),
    currentLines: [
      `官方程序阶段：${centerStateText(snapshot.officialProcedureStage, '暂无')}`,
      `业务阶段：${centerStateText(snapshot.businessStage, '暂无')}`,
      `法律状态：${centerStateText(snapshot.legalStatus, '暂无')}`,
      `核验状态：${centerStateText(snapshot.verificationStatus, '暂无')}`,
    ],
    latestText: current.hasMore
      ? INCOMPLETE_HISTORY
      : latest
        ? centerChangeText(latest)
        : '暂无已确认的中心变化',
    latestAt: current.hasMore ? null : latest?.effectiveAt ?? null,
    nextText: current.hasMore ? INCOMPLETE_HISTORY : nextTaskText(next),
    nextAt: current.hasMore ? null : nextTaskDate(next),
  }
})

const feeSummary = computed<SummaryProjection>(() => {
  const current = overlay.value
  if (!current) return emptySummary('暂无费用义务事实')
  if (current.hasMore) {
    return {
      statusLabel: '历史未完整',
      currentLines: [INCOMPLETE_HISTORY],
      latestText: INCOMPLETE_HISTORY,
      latestAt: null,
      nextText: INCOMPLETE_HISTORY,
      nextAt: null,
    }
  }
  const obligations = latestObligationsById(current.milestones)
  const feeMilestones = current.milestones.filter((milestone) => milestone.lane === 'FEE')
  const latest = latestMilestone(feeMilestones, 'FEE')
  const next = nextOpenTask(feeMilestones)
  return {
    statusLabel: feeStatusLabel(obligations),
    currentLines: feeCurrentLines(obligations),
    latestText: feeLatestText(latest),
    latestAt: latest?.effectiveAt ?? null,
    nextText: nextTaskText(next),
    nextAt: nextTaskDate(next),
  }
})

const warningProjection = computed<{
  snapshot: readonly OverlayWarning[]
  activities: readonly WarningActivityProjection[]
}>(() => {
  const current = overlay.value
  if (!current) return { snapshot: [], activities: [] }
  const seen = new Set<string>()
  const activityIds = new Set(current.milestones.map((milestone) => milestone.activityId))
  const grouped = new Map<string, OverlayWarning[]>()
  for (const milestone of current.milestones) {
    for (const warning of milestone.warnings) {
      if (!isCustomerVisibleWarning(warning)) continue
      const key = warningKey(warning)
      if (seen.has(key)) continue
      seen.add(key)
      const warnings = grouped.get(milestone.activityId) ?? []
      warnings.push(warning)
      grouped.set(milestone.activityId, warnings)
    }
  }
  const snapshot: OverlayWarning[] = []
  for (const warning of current.warnings) {
    if (!isCustomerVisibleWarning(warning)) continue
    if (warning.activityId && activityIds.has(warning.activityId)) continue
    const key = warningKey(warning)
    if (seen.has(key)) continue
    seen.add(key)
    snapshot.push(warning)
  }
  return {
    snapshot,
    activities: [...grouped.entries()].map(([activityId, warnings]) => ({ activityId, warnings })),
  }
})

async function loadOverlay(): Promise<void> {
  loading.value = true
  error.value = null
  loadMoreError.value = null
  traversalRevision.value = null
  overlay.value = null
  historyExpanded.value = false
  try {
    const firstPage = await getLifecycleOverlay(props.caseId, {
      afterSequence: 0,
      limit: 200,
      asOfRevision: null,
    })
    const pageError = validateOverlayPage(firstPage, 0, null)
    if (pageError) throw pageError
    traversalRevision.value = firstPage.lifecycleRevision
    overlay.value = firstPage
    emit('loaded', firstPage)
  } catch (caught) {
    error.value = caught as ApiError
    emit('failed', error.value)
  } finally {
    loading.value = false
  }
}

async function loadMoreOverlay(): Promise<void> {
  const current = overlay.value
  const revision = traversalRevision.value
  if (
    !current ||
    !current.hasMore ||
    current.nextCursor === null ||
    revision === null ||
    loadingMore.value
  ) {
    return
  }

  loadingMore.value = true
  loadMoreError.value = null
  try {
    const nextPage = await getLifecycleOverlay(props.caseId, {
      afterSequence: current.nextCursor,
      limit: 200,
      asOfRevision: revision,
    })
    const pageError = validateOverlayPage(nextPage, current.nextCursor, revision)
    if (pageError) {
      loadMoreError.value = pageError
      return
    }
    const seenSequences = new Set(current.milestones.map((milestone) => milestone.sequence))
    const milestones = [...current.milestones]
    for (const milestone of nextPage.milestones) {
      if (!seenSequences.has(milestone.sequence)) {
        const lastAccepted = milestones[milestones.length - 1]
        if (lastAccepted && milestone.sequence <= lastAccepted.sequence) {
          loadMoreError.value = invalidPageError('分页新增里程碑会破坏累计顺序')
          return
        }
        seenSequences.add(milestone.sequence)
        milestones.push(milestone)
      }
    }
    const accumulated: LifecycleOverlay = {
      ...nextPage,
      lifecycleRevision: revision,
      milestones,
      warnings: mergeWarnings(current.warnings, nextPage.warnings),
    }
    overlay.value = accumulated
    emit('loaded', accumulated)
  } catch (caught) {
    loadMoreError.value = caught as ApiError
  } finally {
    loadingMore.value = false
  }
}

onMounted(loadOverlay)

function emptySummary(currentText: string): SummaryProjection {
  return {
    statusLabel: '暂无',
    currentLines: [currentText],
    latestText: '暂无',
    latestAt: null,
    nextText: NO_NEXT_TASK,
    nextAt: null,
  }
}

function latestMilestone(
  milestones: readonly OverlayMilestone[],
  lane: ActivityLane,
): OverlayMilestone | null {
  return milestones
    .filter((item) => item.lane === lane)
    .reduce<OverlayMilestone | null>(
      (latest, item) => !latest || item.sequence > latest.sequence ? item : latest,
      null,
    )
}

function currentEvidenceVersions(milestones: readonly OverlayMilestone[]) {
  const byId = new Map<string, OverlayMilestone['documentEvidence'][number]['version']>()
  for (const milestone of milestones) {
    for (const evidence of milestone.documentEvidence) {
      byId.set(evidence.version.evidenceVersionId, evidence.version)
    }
  }
  return [...byId.values()].filter((version) => version.isCurrent)
}

function documentStatusLabel(reviewCounts: ReadonlyMap<string, number>, versionCount: number): string {
  if ((reviewCounts.get('REJECTED') ?? 0) > 0) return '复核未通过'
  if ((reviewCounts.get('PENDING') ?? 0) > 0) return '待复核'
  if (versionCount > 0) return '全部已复核'
  return '暂无当前版本'
}

function nextOpenTask(milestones: readonly OverlayMilestone[]): OverlayTask | null {
  const latestById = new Map<string, { task: OverlayTask; firstOrder: number }>()
  let nextOrder = 0
  for (const milestone of milestones) {
    for (const task of milestone.tasks) {
      const existing = latestById.get(task.taskId)
      latestById.set(task.taskId, {
        task,
        firstOrder: existing?.firstOrder ?? nextOrder++,
      })
    }
  }
  const candidates = [...latestById.values()].filter(({ task }) => task.status === 'OPEN')
  candidates.sort((left, right) => {
    const leftGroup = left.task.dueDate ? 0 : left.task.internalDueDate ? 1 : 2
    const rightGroup = right.task.dueDate ? 0 : right.task.internalDueDate ? 1 : 2
    if (leftGroup !== rightGroup) return leftGroup - rightGroup
    const leftDate = left.task.dueDate ?? left.task.internalDueDate ?? ''
    const rightDate = right.task.dueDate ?? right.task.internalDueDate ?? ''
    return leftDate.localeCompare(rightDate) || left.firstOrder - right.firstOrder
  })
  return candidates[0]?.task ?? null
}

function nextTaskText(task: OverlayTask | null): string {
  return task?.title || (task ? '待办任务' : NO_NEXT_TASK)
}

function nextTaskDate(task: OverlayTask | null): string | null {
  return task?.dueDate ?? task?.internalDueDate ?? null
}

function latestConfirmedCenterChange(milestones: readonly OverlayMilestone[]): OverlayMilestone | null {
  return milestones.reduce<OverlayMilestone | null>((latest, milestone) => {
    if (milestone.confirmationStatus !== 'CONFIRMED' || changedAxes(milestone).length === 0) {
      return latest
    }
    return !latest || milestone.sequence > latest.sequence ? milestone : latest
  }, null)
}

function changedAxes(milestone: OverlayMilestone) {
  return CENTER_AXES.flatMap(({ key, label }) => {
    const change = milestone.centerChanges[key]
    return change ? [{ key, label, ...change }] : []
  })
}

function centerChangeText(milestone: OverlayMilestone): string {
  const change = changedAxes(milestone)[0]
  return change
    ? `${change.label}：${centerStateText(change.previousValue, '暂无')} → ${centerStateText(change.currentValue, '暂无')}`
    : '暂无已确认的中心变化'
}

function feeStatusLabel(obligations: readonly OverlayFeeObligation[]): string {
  if (obligations.length === 0) return '暂无费用义务'
  const govCount = obligations.filter((item) => item.feeDomain === 'GOV').length
  const serviceCount = obligations.filter((item) => item.feeDomain === 'SERVICE').length
  return `官费 ${govCount} · 服务费 ${serviceCount}`
}

function feeCurrentLines(obligations: readonly OverlayFeeObligation[]): readonly string[] {
  if (obligations.length === 0) return ['暂无费用义务事实']
  return (['GOV', 'SERVICE'] as const).flatMap((domain) => {
    const counts = new Map<string, number>()
    for (const obligation of obligations.filter((item) => item.feeDomain === domain)) {
      const currency = currencyText(obligation.currency)
      counts.set(currency, (counts.get(currency) ?? 0) + 1)
    }
    if (counts.size === 0) return []
    const items = [...counts.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([currency, count]) => `${currency} ${count} 项`)
      .join('、')
    return [`${feeStatusText(domain)}：${items}`]
  })
}

function feeLatestText(milestone: OverlayMilestone | null): string {
  if (!milestone) return '暂无费用义务变化'
  const labels = new Set(
    milestone.feeObligations.map(
      (obligation) => `${feeStatusText(obligation.feeDomain)} · ${feeStatusText(obligation.obligationType, '费用活动待确认')}`,
    ),
  )
  return labels.size > 0 ? [...labels].join('、') : '费用事实已更新'
}

function mergeWarnings(
  previous: readonly OverlayWarning[],
  current: readonly OverlayWarning[],
): readonly OverlayWarning[] {
  const merged = new Map<string, OverlayWarning>()
  for (const warning of [...previous, ...current]) {
    const key = warningKey(warning)
    if (!merged.has(key)) merged.set(key, warning)
  }
  return [...merged.values()]
}

function warningKey(warning: OverlayWarning): string {
  return [
    warning.kind,
    warning.code,
    warning.activityId ?? '',
    warning.sourceObjectType ?? '',
    warning.sourceObjectId ?? '',
    warning.message,
  ].join('|')
}

function displayValue(value: string | null): string {
  return value ?? '-'
}

function validateOverlayPage(
  page: LifecycleOverlay,
  afterSequence: number,
  expectedRevision: number | null,
): ApiError | null {
  if (expectedRevision !== null && page.lifecycleRevision !== expectedRevision) {
    return invalidPageError('分页响应修订与首次修订不一致')
  }
  for (let index = 1; index < page.milestones.length; index += 1) {
    if (page.milestones[index].sequence <= page.milestones[index - 1].sequence) {
      return invalidPageError('分页里程碑序列必须严格递增')
    }
  }
  if (page.hasMore && page.nextCursor === null) {
    return invalidPageError('分页响应缺少下一游标')
  }
  if (page.hasMore && page.nextCursor !== null && page.nextCursor <= afterSequence) {
    return invalidPageError('分页响应下一游标未前进')
  }
  return null
}

function invalidPageError(message: string): ApiError {
  return {
    status: 0,
    code: 'LIFECYCLE_OVERLAY_PAGE_INVALID',
    message,
  }
}

function isCustomerVisibleWarning(warning: OverlayWarning): boolean {
  return warning.kind !== 'CUSTOMER_DECISION_GATE'
    && warning.sourceObjectType !== 'CUSTOMER_DECISION_GATE'
}

function warningKindLabel(kind: OverlayWarningKind): string {
  return warningKindLabels[kind]
}
</script>

<style scoped>
.case-lifecycle-overlay {
  margin: 20px 0;
}

.overlay-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 10px;
  color: var(--text-secondary);
  font-size: 12px;
}

.lifecycle-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  align-items: stretch;
}

.overlay-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr) minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.overlay-loading {
  padding: 28px;
  text-align: center;
  color: var(--text-secondary);
}

.history-disclosure,
.overlay-pagination {
  margin-top: 14px;
  color: var(--text-secondary);
}

.history-boundary {
  margin: 14px 0;
  padding: 10px 12px;
  border-left: 3px solid var(--el-color-info);
  background: var(--bg-page);
  color: var(--text-secondary);
  font-size: 13px;
}

.overlay-warning-projection {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.overlay-warning-projection h2,
.overlay-warning-projection h3,
.overlay-warning-projection p,
.overlay-facts p {
  margin: 0;
}

.overlay-facts {
  display: grid;
  gap: 10px;
}

.warning-row {
  display: grid;
  gap: 5px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  overflow-wrap: anywhere;
}

@media (max-width: 1099px) and (min-width: 900px) {
  .lifecycle-summary-grid {
    gap: 10px;
  }
}

@media (max-width: 899px) {
  .lifecycle-summary-grid,
  .overlay-grid {
    grid-template-columns: 1fr;
  }
}
</style>
