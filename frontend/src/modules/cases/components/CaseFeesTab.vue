<template>
  <div class="case-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">官费估算</h3>
        <p class="panel-hint">仅在明确选择条件后估算，不会创建费用义务或费用草稿。</p>
      </div>
      <el-tag v-if="estimate" type="warning" size="small">{{ estimate.estimate_status }}</el-tag>
    </div>

    <div class="estimate-controls">
      <label>
        估算触发上下文
        <select v-model="trigger" aria-label="估算触发上下文" @change="clearEstimate">
          <option value="">请选择</option>
          <option value="FILING_ACCEPTED">FILING_ACCEPTED</option>
          <option value="REEXAM_REQUESTED">REEXAM_REQUESTED</option>
        </select>
      </label>
      <label>
        来源文档
        <select v-model="sourceDocumentId" aria-label="来源文档" @change="clearEstimate">
          <option value="">不选择来源文档</option>
          <option v-for="documentId in reviewedSourceDocumentIds" :key="documentId" :value="documentId">
            {{ documentId }}
          </option>
        </select>
      </label>
      <label>
        费率生效日
        <input v-model="rateEffectiveOn" aria-label="费率生效日" type="date" @input="clearEstimate" />
      </label>
      <el-button type="primary" @click="estimateOfficialFee">估算官费</el-button>
    </div>

    <p v-if="validationMessage" class="validation-message">{{ validationMessage }}</p>
    <el-alert
      v-if="previewError"
      :title="previewError.code"
      :description="previewError.message"
      type="warning"
      show-icon
      :closable="false"
    />

    <div v-if="estimate" class="estimate-result" data-testid="official-fee-estimate">
      <div class="estimate-summary">
        <span>估算状态：{{ estimate.estimate_status }}</span>
        <span>币种：{{ estimate.currency }}</span>
        <span>应缴合计：{{ estimate.total_payable_amount }}</span>
      </div>
      <div v-for="(candidate, index) in estimate.candidates" :key="index" class="estimate-candidate">
        <strong>{{ candidate.line.fee_name }}（{{ candidate.line.fee_code }}）</strong>
        <span>官方全额：{{ candidate.line.official_full_amount ?? '' }}</span>
        <span>费减比例：{{ candidate.line.reduction_ratio }}</span>
        <span>应缴金额：{{ candidate.line.payable_amount }}</span>
        <span>来源金额：{{ candidate.line.source_amount ?? '' }}</span>
        <span>来源日期：{{ candidate.line.source_date ?? '' }}</span>
        <span>差异复核：{{ candidate.line.difference_review_state }}</span>
        <span>费率标识：{{ candidate.source.rate_id ?? '' }}</span>
        <span>来源文档：{{ candidate.source.source_document_id ?? '' }}</span>
        <span>来源文件：{{ candidate.source.source_doc ?? '' }}</span>
        <span>来源地址：{{ candidate.source.source_url ?? '' }}</span>
        <span>来源政策：{{ candidate.source.source_policy ?? '' }}</span>
        <span>来源版本：{{ candidate.source.source_version ?? '' }}</span>
        <span>来源状态：{{ candidate.source.status }}</span>
      </div>
    </div>
  </div>

  <div class="case-panel" data-testid="real-fee-obligations">
    <div class="panel-toolbar">
      <h3 class="panel-heading">真实费用义务</h3>
      <el-button
        v-if="demoSessionEnabled"
        type="primary"
        size="small"
        :loading="demoObligationPending"
        :disabled="demoObligationPending || demoObligationAttempted"
        @click="handleCreateDemoServiceObligation"
      >
        生成服务费义务
      </el-button>
    </div>
    <el-alert
      v-if="demoObligationMessage"
      type="success"
      :closable="false"
      :title="demoObligationMessage"
      show-icon
    />
    <el-alert
      v-if="demoObligationError"
      type="warning"
      :closable="false"
      title="服务费义务结果未确认"
      :description="demoObligationError"
      show-icon
    />
    <el-alert
      v-if="demoRefreshError"
      type="warning"
      :closable="false"
      title="服务费义务已生成，费用视图刷新失败"
      :description="demoRefreshError"
      show-icon
    />
    <el-button
      v-if="demoRefreshError"
      type="primary"
      plain
      size="small"
      @click="handleReloadDemoFeeView"
    >
      重新加载费用视图
    </el-button>
    <div v-if="overlayLoading" class="placeholder-content">正在加载真实费用义务...</div>
    <el-alert
      v-else-if="activeOverlayError"
      :title="activeOverlayError.code"
      :description="activeOverlayError.message"
      type="warning"
      show-icon
      :closable="false"
    />
    <div v-else-if="realObligations.length === 0" class="placeholder-content">暂无真实费用义务</div>
    <div v-for="(obligation, obligationIndex) in realObligations" :key="obligationIndex" class="obligation-card">
      <strong>{{ obligation.obligationId }}</strong>
      <span>来源活动：{{ obligation.sourceActivityId }}</span>
      <span>来源文档：{{ obligation.sourceDocumentId ?? '' }}</span>
      <span>来源状态：{{ obligation.sourceStatus }}</span>
      <span>费用域：{{ obligation.feeDomain }}</span>
      <span>义务类型：{{ obligation.obligationType }}</span>
      <span>到期日：{{ obligation.dueDate ?? '' }}</span>
      <span>估算状态：{{ obligation.statuses.estimateStatus ?? '' }}</span>
      <span>义务状态：{{ obligation.statuses.obligationStatus }}</span>
      <span>客户指示：{{ obligation.statuses.clientInstructionStatus }}</span>
      <span>草稿状态：{{ obligation.statuses.draftStatus }}</span>
      <span>清单状态：{{ obligation.statuses.payListStatus }}</span>
      <span>支付状态：{{ obligation.statuses.paymentStatus }}</span>
      <span>官方证据状态：{{ obligation.statuses.officialEvidenceStatus }}</span>
      <span>替代义务：{{ obligation.supersedesObligationId ?? '' }}</span>
      <span>替代原因：{{ obligation.supersedeReason ?? '' }}</span>
      <div v-for="(line, lineIndex) in obligation.lines" :key="lineIndex" class="nested-fact">
        <span>{{ line.feeCode }}</span>
        <span>{{ line.officialFullAmount ?? '' }}</span>
        <span>{{ line.reductionRatio }}</span>
        <span>{{ line.payableAmount }}</span>
        <span>{{ line.sourceAmount ?? '' }}</span>
        <span>{{ line.sourceDate ?? '' }}</span>
        <span>{{ line.differenceReviewState }}</span>
      </div>
      <div v-for="(fact, factIndex) in obligation.relatedFacts" :key="factIndex" class="nested-fact">
        <span>{{ fact.kind }}</span>
        <span>{{ fact.objectId }}</span>
        <span>{{ fact.status }}</span>
      </div>
      <div class="instruction-actions">
        <el-button
          size="small"
          :disabled="instructionLoading[obligation.obligationId]"
          @click="recordInstruction(obligation.obligationId, 'PAY')"
        >
          记录支付指示
        </el-button>
        <el-button
          size="small"
          :disabled="instructionLoading[obligation.obligationId]"
          @click="recordInstruction(obligation.obligationId, 'HOLD')"
        >
          记录暂缓指示
        </el-button>
        <el-button
          size="small"
          :disabled="instructionLoading[obligation.obligationId]"
          @click="recordInstruction(obligation.obligationId, 'ABANDON')"
        >
          记录放弃指示
        </el-button>
      </div>
      <el-alert
        v-if="instructionErrors[obligation.obligationId]"
        :title="instructionErrors[obligation.obligationId]?.code"
        :description="instructionErrors[obligation.obligationId]?.message"
        type="warning"
        show-icon
        :closable="false"
      />
      <div
        v-if="instructionResults[obligation.obligationId]"
        class="instruction-result"
        data-testid="fee-instruction-result"
      >
        <strong>服务端指示事实</strong>
        <span>服务端义务编号：{{ instructionResults[obligation.obligationId]?.obligation_id }}</span>
        <span>服务端客户指示：{{ instructionResults[obligation.obligationId]?.client_instruction_status }}</span>
        <span>服务端活动编号：{{ instructionResults[obligation.obligationId]?.activity_id }}</span>
        <span>服务端幂等键：{{ instructionResults[obligation.obligationId]?.idempotency_key }}</span>
        <span>服务端复用结果：{{ instructionResults[obligation.obligationId]?.reused ? '是' : '否' }}</span>
        <router-link
          v-if="instructionResults[obligation.obligationId]?.client_instruction_status === 'PAY'"
          :to="`/fees/drafts/new?obligation_id=${encodeURIComponent(instructionResults[obligation.obligationId]!.obligation_id)}`"
        >
          创建关联费用草稿
        </router-link>
      </div>
    </div>
  </div>

  <div class="case-panel" data-testid="persisted-fee-drafts">
    <div class="panel-toolbar">
      <h3 class="panel-heading">已保存费用草稿</h3>
      <el-button type="primary" size="small" @click="handleCreate">创建费用草稿</el-button>
    </div>
    <div v-if="draftLoading" class="muted">加载中...</div>
    <div v-else-if="items.length === 0" class="placeholder-content">暂无费用草稿</div>
    <el-table v-else :data="items" stripe style="width: 100%">
      <el-table-column prop="id" label="草稿标识" min-width="180" />
      <el-table-column label="草稿类型" width="120">
        <template #default="{ row }">{{ formatDraftType(row.draft_type) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'LOCKED' ? 'danger' : 'success'" size="small">
            {{ getFeeDraftStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="currency" label="币种" width="80" />
      <el-table-column label="总金额" width="140">
        <template #default="{ row }">{{ row.amount }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getFeeDrafts, previewOfficialFeeCandidates, recordFeeObligationInstruction } from '../../../api/fees'
import type {
  FeeDraftListItem,
  FeeObligationInstructionPayload,
  FeeObligationInstructionResult,
  OfficialFeeEstimateResult,
} from '../../../api/fees.types'
import { getLifecycleOverlay } from '../../../api/lifecycleOverlay'
import type { LifecycleOverlay } from '../../../api/lifecycleOverlay.types'
import type { ApiError } from '../../../api/types'
import { getFeeDraftStatusText, getFeeDraftTypeText } from '../../../constants/displayText'
import { createValidatedDemoServiceObligation } from '../../demo/demo.api'
import {
  DEMO_UI_SESSION_CHANGE_EVENT,
  getDemoUiSession,
  isDemoUiSessionActive,
} from '../../demo/demoUiSession'
import type { DemoHostTuple } from '../../demo/demoUiSession'

const props = defineProps<{
  caseId: string
  lifecycleOverlay?: LifecycleOverlay | null
  lifecycleOverlayError?: ApiError | null
  lifecycleOverlayManaged?: boolean
}>()

const router = useRouter()
const items = ref<FeeDraftListItem[]>([])
const draftLoading = ref(true)
const standaloneOverlay = ref<LifecycleOverlay | null>(null)
const standaloneOverlayError = ref<ApiError | null>(null)
const demoRefreshedOverlay = ref<LifecycleOverlay | null>(null)
const demoSessionEnabled = ref(false)
const demoObligationPending = ref(false)
const demoObligationAttempted = ref(false)
const demoObligationMessage = ref('')
const demoObligationError = ref('')
const demoRefreshError = ref('')
const demoObligationIdempotencyKey = crypto.randomUUID()
const trigger = ref('')
const sourceDocumentId = ref('')
const rateEffectiveOn = ref('')
const estimate = ref<OfficialFeeEstimateResult | null>(null)
const previewError = ref<ApiError | null>(null)
const validationMessage = ref('')
const pendingInstructionAttempts = ref<Record<string, PendingInstructionAttempt | undefined>>({})
const instructionLoading = ref<Record<string, boolean | undefined>>({})
const instructionErrors = ref<Record<string, ApiError | undefined>>({})
const instructionResults = ref<Record<string, FeeObligationInstructionResult | undefined>>({})

type FeeInstruction = FeeObligationInstructionPayload['instruction']

interface PendingInstructionAttempt {
  instruction: FeeInstruction
  idempotencyKey: string
}

const isLifecycleOverlayManaged = computed(
  () =>
    props.lifecycleOverlayManaged === true ||
    props.lifecycleOverlay !== undefined ||
    props.lifecycleOverlayError !== undefined,
)
const activeOverlay = computed(() => selectActiveFeeOverlay(
  isLifecycleOverlayManaged.value,
  props.lifecycleOverlay ?? null,
  standaloneOverlay.value,
  demoRefreshedOverlay.value,
))
const activeOverlayError = computed(() =>
  activeOverlay.value !== null
    ? null
    : isLifecycleOverlayManaged.value
    ? props.lifecycleOverlayError ?? null
    : standaloneOverlayError.value,
)
const overlayLoading = computed(
  () =>
    isLifecycleOverlayManaged.value &&
    activeOverlay.value === null &&
    activeOverlayError.value === null,
)

const reviewedSourceDocumentIds = computed(() => {
  const documentIds: string[] = []
  for (const milestone of activeOverlay.value?.milestones ?? []) {
    for (const evidence of milestone.documentEvidence) {
      const documentId = evidence.version.documentId
      if (evidence.version.reviewState === 'APPROVED' && documentId !== null && !documentIds.includes(documentId)) {
        documentIds.push(documentId)
      }
    }
  }
  return documentIds
})

const realObligations = computed(() =>
  (activeOverlay.value?.milestones ?? []).flatMap((milestone) => milestone.feeObligations),
)

onMounted(async () => {
  syncDemoSession()
  window.addEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
  const loaders = [loadFeeDrafts()]
  if (!isLifecycleOverlayManaged.value) {
    loaders.push(loadLifecycleOverlay())
  }
  await Promise.all(loaders)
})

onBeforeUnmount(() => {
  window.removeEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
})

function canStartDemoServiceObligation(
  sessionActive: boolean,
  session: DemoHostTuple | null,
  pending: boolean,
  attempted: boolean,
): boolean {
  return sessionActive && session !== null && !pending && !attempted
}

function selectActiveFeeOverlay(
  managed: boolean,
  managedOverlay: LifecycleOverlay | null,
  standaloneOverlayValue: LifecycleOverlay | null,
  refreshedOverlay: LifecycleOverlay | null,
): LifecycleOverlay | null {
  if (!managed) return standaloneOverlayValue
  if (refreshedOverlay === null) return managedOverlay
  if (
    managedOverlay !== null &&
    managedOverlay.lifecycleRevision >= refreshedOverlay.lifecycleRevision
  ) return managedOverlay
  return refreshedOverlay
}

function syncDemoSession() {
  demoSessionEnabled.value = isDemoUiSessionActive() && getDemoUiSession() !== null
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : '请刷新后重试。'
}

async function reloadDemoFeeView() {
  const [overlay] = await Promise.all([
    getLifecycleOverlay(props.caseId, { afterSequence: 0, limit: 50, asOfRevision: null }),
    loadFeeDrafts(),
  ])
  if (isLifecycleOverlayManaged.value) {
    demoRefreshedOverlay.value = overlay
  } else {
    standaloneOverlay.value = overlay
  }
}

async function handleReloadDemoFeeView() {
  demoRefreshError.value = ''
  try {
    await reloadDemoFeeView()
  } catch (error) {
    demoRefreshError.value = errorMessage(error)
  }
}

async function handleCreateDemoServiceObligation() {
  if (!canStartDemoServiceObligation(
    isDemoUiSessionActive(),
    getDemoUiSession(),
    demoObligationPending.value,
    demoObligationAttempted.value,
  )) return
  demoObligationPending.value = true
  demoObligationAttempted.value = true
  demoObligationMessage.value = ''
  demoObligationError.value = ''
  demoRefreshError.value = ''
  syncDemoSession()
  try {
    let result
    try {
      result = await createValidatedDemoServiceObligation(
        props.caseId,
        demoObligationIdempotencyKey,
      )
    } catch (error) {
      demoObligationError.value = errorMessage(error)
      return
    }
    demoObligationMessage.value = result.reused
      ? `${result.name_zh_cn}义务已复用（${result.currency} ${result.amount}）`
      : `${result.name_zh_cn}义务已生成（${result.currency} ${result.amount}）`
    try {
      await reloadDemoFeeView()
    } catch (error) {
      demoRefreshError.value = errorMessage(error)
    }
  } finally {
    demoObligationPending.value = false
    syncDemoSession()
  }
}

function clearEstimate() {
  estimate.value = null
  previewError.value = null
  validationMessage.value = ''
}

async function loadFeeDrafts() {
  try {
    const response = await getFeeDrafts({ case_id: props.caseId, page: 1, page_size: 50 })
    items.value = response.items
  } finally {
    draftLoading.value = false
  }
}

async function loadLifecycleOverlay() {
  standaloneOverlayError.value = null
  try {
    standaloneOverlay.value = await getLifecycleOverlay(props.caseId, {
      afterSequence: 0,
      limit: 50,
      asOfRevision: null,
    })
  } catch (error) {
    standaloneOverlay.value = null
    standaloneOverlayError.value = error as ApiError
  }
}

async function estimateOfficialFee() {
  clearEstimate()
  if (!rateEffectiveOn.value) {
    validationMessage.value = '请选择费率生效日期'
    return
  }
  if (!trigger.value) {
    validationMessage.value = '请选择估算触发上下文'
    return
  }
  try {
    estimate.value = await previewOfficialFeeCandidates({
      case_id: props.caseId,
      trigger_context: {
        trigger: trigger.value,
        source_document_id: sourceDocumentId.value || null,
      },
      currency: 'CNY',
      rate_effective_on: rateEffectiveOn.value,
    })
  } catch (error) {
    previewError.value = error as ApiError
  }
}

async function recordInstruction(obligationId: string, instruction: FeeInstruction) {
  const retainedAttempt = pendingInstructionAttempts.value[obligationId]
  const attempt = retainedAttempt?.instruction === instruction
    ? retainedAttempt
    : { instruction, idempotencyKey: crypto.randomUUID() }

  pendingInstructionAttempts.value[obligationId] = attempt
  instructionLoading.value[obligationId] = true
  instructionErrors.value[obligationId] = undefined
  instructionResults.value[obligationId] = undefined

  try {
    instructionResults.value[obligationId] = await recordFeeObligationInstruction(obligationId, {
      instruction,
      idempotency_key: attempt.idempotencyKey,
    })
    pendingInstructionAttempts.value[obligationId] = undefined
  } catch (error) {
    const apiError = error as ApiError
    instructionErrors.value[obligationId] = apiError
    if (apiError.status !== 0) {
      pendingInstructionAttempts.value[obligationId] = undefined
    }
  } finally {
    instructionLoading.value[obligationId] = false
  }
}

function handleCreate() {
  router.push(`/fees/drafts/new?case_id=${props.caseId}&draft_type=APPLY_FEE`)
}

function formatDraftType(type?: string | null): string {
  return type ? getFeeDraftTypeText(type) : '费用草稿'
}
</script>

<style scoped>
.panel-hint,
.validation-message {
  color: var(--text-sub, #64748b);
  font-size: 13px;
}

.estimate-controls,
.estimate-summary,
.estimate-candidate,
.obligation-card,
.nested-fact,
.instruction-actions,
.instruction-result {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.estimate-controls {
  align-items: end;
  margin-bottom: 12px;
}

.estimate-controls label {
  display: grid;
  gap: 4px;
}

.estimate-result,
.obligation-card {
  margin-top: 12px;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  padding: 12px;
}

.estimate-candidate,
.obligation-card,
.nested-fact,
.instruction-result {
  flex-direction: column;
}

.nested-fact {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--color-border, #e2e8f0);
}
</style>
