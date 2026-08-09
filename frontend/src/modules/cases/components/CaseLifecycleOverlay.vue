<template>
  <section class="case-lifecycle-overlay" data-testid="case-lifecycle-overlay">
    <div v-if="loading" class="overlay-loading">正在加载三线生命周期…</div>
    <ApiErrorBanner v-else-if="error" :error="error" :dismissable="false" />
    <template v-else-if="overlay">
      <header class="overlay-meta">
        <span>快照修订：{{ overlay.lifecycleRevision }}</span>
        <span>生成时间：{{ overlay.generatedAt }}</span>
      </header>
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

      <ApiErrorBanner
        v-if="loadMoreError"
        :error="loadMoreError"
        :dismissable="false"
      />
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

      <section class="overlay-facts" data-testid="overlay-decision-gates">
        <h2>客户决策</h2>
        <article
          v-for="gate in overlay.decisionGates"
          :key="lifecycleOverlayGateKey(gate)"
          class="gate-row"
          :data-gate-key="lifecycleOverlayGateKey(gate)"
        >
          <p>门禁代码：{{ gate.gateCode }}</p>
          <p>请求范围：{{ gate.requestedScopeKey }}</p>
          <p>解析状态：{{ gate.resolutionStatus }}</p>
          <template v-if="gate.resolutionStatus === 'RESOLVED'">
            <p>解析范围：{{ displayValue(gate.resolvedScopeKey) }}</p>
            <p>决策值：{{ displayValue(gate.decisionValue) }}</p>
            <p>来源引用：{{ displayValue(gate.sourceReference) }}</p>
            <p>来源版本：{{ displayValue(gate.sourceVersion) }}</p>
            <p>确认人：{{ displayValue(gate.confirmedBy) }}</p>
            <p>生效时间：{{ displayValue(gate.effectiveAt) }}</p>
            <div v-if="isReferenceOnlyGate(gate)" class="gate-markers">
              <span>仅供参考</span>
              <span>非激活</span>
            </div>
            <div v-else-if="gate.decisionValue === 'CURRENT_OFFICIAL'" class="gate-markers">
              <span>可供后续激活</span>
            </div>
          </template>
          <template v-else>
            <p>未解析原因</p>
            <p>{{ unresolvedReasonText(gate.unresolvedReason) }}</p>
          </template>
        </article>
      </section>

      <section class="overlay-facts" data-testid="overlay-snapshot-warnings">
        <h2>当前快照警告</h2>
        <article v-for="(warning, index) in overlay.warnings" :key="index" class="warning-row">
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
        v-for="milestone in milestonesWithWarnings"
        :key="milestone.activityId"
        class="overlay-facts"
        :data-testid="`overlay-activity-warnings-${milestone.activityId}`"
      >
        <h2>活动局部警告</h2>
        <p>活动编号：{{ milestone.activityId }}</p>
        <article v-for="(warning, index) in milestone.warnings" :key="index" class="warning-row">
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
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getLifecycleOverlay, lifecycleOverlayGateKey } from '../../../api/lifecycleOverlay'
import type {
  LifecycleOverlay,
  OverlayDecisionGate,
  OverlayWarningKind,
} from '../../../api/lifecycleOverlay.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import DocumentEvidenceLane from './DocumentEvidenceLane.vue'
import FeeObligationLane from './FeeObligationLane.vue'
import LifecycleCenterLane from './LifecycleCenterLane.vue'

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

const unresolvedReasonLabels: Readonly<Record<string, string>> = {
  DECISION_GATE_NOT_FOUND: '未找到适用的客户决策',
  DECISION_GATE_REVOKED: '客户决策已撤销',
  DECISION_GATE_NOT_EFFECTIVE: '客户决策尚未生效',
  DECISION_GATE_CANDIDATE_MULTIPLICITY: '存在多个候选客户决策',
  DECISION_GATE_CURRENT_IDENTITY_CONFLICT: '当前客户决策标识冲突',
  DECISION_GATE_CURRENT_ROW_CORRUPT: '当前客户决策记录损坏',
  DECISION_GATE_LEGACY_MAP_CORRUPT: '历史表单分类映射损坏',
}
const warningKindLabels: Readonly<Record<OverlayWarningKind, string>> = {
  UNVERIFIED: '未核验',
  CUSTOMER_DECISION_GATE: '客户待确认',
  CONFLICT: '来源冲突',
  REFERENCE_ONLY: '仅供参考',
}

const milestonesWithWarnings = computed(() =>
  overlay.value?.milestones.filter((milestone) => milestone.warnings.length > 0) ?? [],
)

async function loadOverlay(): Promise<void> {
  loading.value = true
  error.value = null
  loadMoreError.value = null
  traversalRevision.value = null
  overlay.value = null
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

function unresolvedReasonText(reason: string | null): string {
  if (!reason) return '-'
  const label = unresolvedReasonLabels[reason]
  return label ? `${label}（${reason}）` : reason
}

function isReferenceOnlyGate(gate: OverlayDecisionGate): boolean {
  return gate.decisionValue === 'HISTORICAL' || gate.decisionValue === 'INTERNAL_ONLY'
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

.overlay-pagination {
  margin-top: 14px;
  color: var(--text-secondary);
}

.overlay-facts {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.overlay-facts h2,
.overlay-facts p {
  margin: 0;
}

.gate-row,
.warning-row {
  display: grid;
  gap: 5px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  overflow-wrap: anywhere;
}

.gate-markers {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--el-color-warning-dark-2);
  font-weight: 600;
}

@media (max-width: 1100px) {
  .overlay-grid {
    grid-template-columns: 1fr;
  }
}
</style>
