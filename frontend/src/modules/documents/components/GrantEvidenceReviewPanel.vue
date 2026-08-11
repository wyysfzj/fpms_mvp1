<template>
  <section class="case-panel grant-evidence-review-panel" data-testid="grant-evidence-review-panel">
    <div class="panel-header">
      <div>
        <h3 class="panel-heading">授权证据候选复核</h3>
        <p class="panel-description">候选信息仅供人工复核，最终结果以服务器记录为准。</p>
      </div>
      <el-button size="small" :loading="loading" @click="fetchCandidates">刷新候选</el-button>
    </div>

    <ApiErrorBanner v-if="error" :error="error" @dismiss="error = null" />

    <el-skeleton v-if="loading" :rows="3" animated />
    <el-empty v-else-if="candidates.length === 0" description="暂无授权证据候选" />
    <div v-else class="candidate-list">
      <article
        v-for="candidate in candidates"
        :key="candidate.candidate_id"
        class="candidate-card"
        :data-testid="`grant-evidence-candidate-${candidate.candidate_id}`"
      >
        <div class="candidate-title-row">
          <strong>{{ getScopeText(candidate.evidence_scope) }}</strong>
          <el-tag :type="getReviewTagType(candidate.review_status)" size="small">
            复核状态：{{ getReviewStatusText(candidate.review_status) }}
          </el-tag>
        </div>

        <div class="candidate-meta-grid">
          <span>来源记录：{{ candidate.source_record_id }}</span>
          <span>来源版本：{{ candidate.source_version }}</span>
          <span>原始引用：{{ candidate.original_reference }}</span>
          <span>获取方式：{{ candidate.acquisition_method }}</span>
          <span>获取时间：{{ formatDateTime(candidate.acquired_at) }}</span>
          <span>提出人：{{ candidate.proposed_by }}</span>
          <span>提出时间：{{ formatDateTime(candidate.proposed_at) }}</span>
          <span>复核人：{{ candidate.reviewer_id || '未复核' }}</span>
          <span>复核时间：{{ formatDateTime(candidate.reviewed_at) }}</span>
        </div>

        <div class="candidate-section">
          <div class="section-title">候选事实</div>
          <div class="fact-list">
            <span v-for="fact in candidate.facts" :key="`${fact.name}:${fact.raw_value}`">
              {{ fact.name }}：{{ fact.raw_value }}
            </span>
          </div>
        </div>

        <div v-if="candidate.conflicts.length" class="candidate-section">
          <div class="section-title">待人工核对的冲突</div>
          <el-alert
            v-for="conflict in candidate.conflicts"
            :key="conflict.name"
            :title="`冲突字段：${conflict.name}`"
            type="warning"
            :closable="false"
            show-icon
            class="conflict-alert"
            :data-testid="`grant-evidence-conflict-${candidate.candidate_id}-${conflict.name}`"
          >
            <div class="conflict-values">
              <el-tag v-for="value in conflict.raw_values" :key="value" type="warning" size="small">
                {{ value }}
              </el-tag>
            </div>
          </el-alert>
        </div>

        <div v-if="candidate.review_reason" class="review-reason">
          复核理由：{{ candidate.review_reason }}
        </div>

        <div v-if="showReviewActions(candidate)" class="review-actions">
          <el-alert
            v-if="isSelfReview(candidate)"
            title="提出人不能复核自己提出的候选"
            type="warning"
            :closable="false"
            show-icon
          />
          <el-input
            v-model="reviewReasons[candidate.candidate_id]"
            type="textarea"
            :rows="2"
            maxlength="4096"
            show-word-limit
            aria-label="复核理由"
            placeholder="请填写复核理由"
            :disabled="isSelfReview(candidate) || Boolean(reviewingCandidateId)"
          />
          <div class="review-buttons">
            <el-button
              type="success"
              :loading="isReviewing(candidate, 'APPROVE')"
              :disabled="reviewDisabled(candidate)"
              @click="submitReview(candidate, 'APPROVE')"
            >
              批准候选
            </el-button>
            <el-button
              type="danger"
              plain
              :loading="isReviewing(candidate, 'REJECT')"
              :disabled="reviewDisabled(candidate)"
              @click="submitReview(candidate, 'REJECT')"
            >
              驳回候选
            </el-button>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { listGrantEvidenceCandidates, reviewGrantEvidence } from '../../../api/documents'
import { http } from '../../../api/http'
import type {
  GrantEvidenceCandidate,
  GrantEvidenceReviewPayload,
} from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { useAuthStore } from '../../../stores/auth'

const props = defineProps<{
  documentId: string
}>()

const authStore = useAuthStore()
const candidates = ref<GrantEvidenceCandidate[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const currentUserId = ref<string | null>(null)
const reviewingCandidateId = ref<string | null>(null)
const reviewingDecision = ref<GrantEvidenceReviewPayload['decision'] | null>(null)
const reviewReasons = reactive<Record<string, string>>({})

async function fetchCandidates(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    candidates.value = await listGrantEvidenceCandidates(props.documentId)
  } catch (err) {
    error.value = toPanelError(err, '加载授权证据候选失败，请稍后重试。')
  } finally {
    loading.value = false
  }
}

async function fetchCurrentUser(): Promise<void> {
  try {
    const response = await http.get<{ user?: { id?: string } }>('/auth/me')
    currentUserId.value = response.data.user?.id?.trim() || null
  } catch {
    currentUserId.value = null
  }
}

function showReviewActions(candidate: GrantEvidenceCandidate): boolean {
  return authStore.hasPermission('Doc.Edit') && candidate.review_status === 'PENDING'
}

function isSelfReview(candidate: GrantEvidenceCandidate): boolean {
  return Boolean(currentUserId.value && currentUserId.value === candidate.proposed_by)
}

function reviewDisabled(candidate: GrantEvidenceCandidate): boolean {
  return Boolean(
    reviewingCandidateId.value
    || !currentUserId.value
    || isSelfReview(candidate)
    || !reviewReasons[candidate.candidate_id]?.trim()
  )
}

function isReviewing(
  candidate: GrantEvidenceCandidate,
  decision: GrantEvidenceReviewPayload['decision']
): boolean {
  return reviewingCandidateId.value === candidate.candidate_id && reviewingDecision.value === decision
}

async function submitReview(
  candidate: GrantEvidenceCandidate,
  decision: GrantEvidenceReviewPayload['decision']
): Promise<void> {
  const reason = reviewReasons[candidate.candidate_id]?.trim()
  if (!reason) {
    ElMessage.warning('请填写复核理由')
    return
  }
  if (!currentUserId.value || isSelfReview(candidate)) {
    ElMessage.warning('提出人不能复核自己提出的候选')
    return
  }

  reviewingCandidateId.value = candidate.candidate_id
  reviewingDecision.value = decision
  error.value = null
  try {
    await reviewGrantEvidence(candidate.candidate_id, { decision, reason })
    await fetchCandidates()
    ElMessage.success(decision === 'APPROVE' ? '授权证据候选已批准' : '授权证据候选已驳回')
  } catch (err) {
    error.value = toPanelError(err, '授权证据候选复核失败，请稍后重试。')
  } finally {
    reviewingCandidateId.value = null
    reviewingDecision.value = null
  }
}

function toPanelError(err: unknown, fallback: string): ApiError {
  const apiError = (err || {}) as Partial<ApiError>
  const status = typeof apiError.status === 'number' ? apiError.status : 0
  let message = fallback
  if (status === 401) message = '登录已失效，请重新登录。'
  else if (status === 403) message = '您没有复核授权证据候选的权限。'
  else if (status === 404) message = '未找到授权证据候选。'
  else if (status === 409) message = '候选、来源或复核配置已变化，请刷新后重试。'
  else if (status === 400 || status === 422) message = '复核请求无效，请核对后重试。'
  return {
    status,
    code: typeof apiError.code === 'string' ? apiError.code : 'GRANT_EVIDENCE_REVIEW_FAILED',
    message,
    details: apiError.details,
    requestId: apiError.requestId,
  }
}

function getScopeText(scope: GrantEvidenceCandidate['evidence_scope']): string {
  return scope === 'GRANT_ANNOUNCEMENT' ? '授权公告证据候选' : '专利登记簿证据候选'
}

function getReviewStatusText(status: GrantEvidenceCandidate['review_status']): string {
  if (status === 'APPROVED') return '已批准'
  if (status === 'REJECTED') return '已驳回'
  return '待复核'
}

function getReviewTagType(
  status: GrantEvidenceCandidate['review_status']
): 'success' | 'danger' | 'warning' {
  if (status === 'APPROVED') return 'success'
  if (status === 'REJECTED') return 'danger'
  return 'warning'
}

function formatDateTime(value: string | null): string {
  if (!value) return '未记录'
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchCandidates()
  fetchCurrentUser()
})
</script>

<style scoped>
.grant-evidence-review-panel {
  margin-top: 16px;
}

.panel-header,
.candidate-title-row,
.review-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-heading {
  margin: 0;
}

.panel-description {
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.candidate-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.candidate-card {
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
}

.candidate-meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 16px;
  margin-top: 14px;
  color: var(--text-secondary);
  font-size: 13px;
  overflow-wrap: anywhere;
}

.candidate-section,
.review-reason,
.review-actions {
  margin-top: 14px;
}

.section-title {
  margin-bottom: 8px;
  font-weight: 600;
}

.fact-list,
.conflict-values {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.conflict-alert + .conflict-alert {
  margin-top: 8px;
}

.review-actions {
  display: grid;
  gap: 10px;
}

.review-buttons {
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .candidate-meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
