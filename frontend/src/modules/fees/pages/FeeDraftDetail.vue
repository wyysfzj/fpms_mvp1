<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> {{ ZH.common.back }}
        </el-button>
      </div>
      <div class="page-header-right">
        <el-button @click="fetchDraft" :loading="loading">{{ ZH.feeDetail.refresh }}</el-button>
        <template v-if="draft">
          <el-button
            v-if="isLocked"
            type="warning"
            :loading="lockLoading"
            @click="confirmUnlock"
          >
            🔓 {{ ZH.feeDetail.unlock }}
          </el-button>
          <el-button
            v-else
            type="primary"
            :loading="lockLoading"
            @click="confirmLock"
          >
            🔒 {{ ZH.feeDetail.lock }}
          </el-button>
        </template>
      </div>
    </div>

    <!-- Lock Error Banner -->
    <div v-if="lockError" class="page-error">
      <ApiErrorBanner :error="lockError" @dismiss="lockError = null" />
    </div>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <template v-else-if="draft">
      <!-- Relation Chain -->
      <RelationChainCard
        :client="draft.client_id ? { id: draft.client_id, name: clientDisplayName } : undefined"
        :case-ref="draft.case_id ? { id: draft.case_id, no: caseDisplayNo } : undefined"
        :fee-draft="{ id: draft.id, label: displayDraftId }"
      />

      <div class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <el-tag :type="statusTagType" size="small">{{ getFeeDraftStatusText(draft.status) }}</el-tag>
            <el-tag v-if="isLocked" type="danger" size="small" class="locked-badge">
              🔒 已锁定
            </el-tag>
            <span class="meta-divider">|</span>
            <span class="case-no">{{ ZH.feeDetail.draftId }}: {{ displayDraftId }}</span>
            <span class="meta-divider">|</span>
            <span>{{ ZH.feeDetail.currency }}: {{ draft.currency }}</span>
          </div>
          <div class="case-title">
            <h1>{{ ZH.feeDetail.feeDraft }}</h1>
            <p class="meta-subtitle">
              {{ ZH.feeDetail.draftType }}: {{ getFeeDraftTypeText(draft.draft_type) }}
            </p>
          </div>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="case-tabs fee-draft-tabs">
        <el-tab-pane :label="ZH.feeDetail.items" name="items">
          <div class="case-panel fee-draft-main">
            <!-- Locked notice -->
            <div v-if="isLocked" class="locked-notice">
              <span class="locked-notice-icon">🔒</span>
              <span>{{ ZH.feeDetail.lockedNotice }}</span>
            </div>
            <FeeDraftItemsTable
              :draft-id="draftId"
              :currency="draft.currency"
              :readonly="isLocked"
              :source-facts="sourceFacts"
              :source-facts-resolved="sourceFactsResolved"
              @change="fetchDraft"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane :label="ZH.feeDetail.overview" name="overview">
          <div class="case-content-grid">
            <div class="case-main-panel">
              <div class="case-panel fee-draft-main">
                <h3 class="panel-heading">{{ ZH.feeDetail.draftMeta }}</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.draftId }}</span>
                    <span class="info-value case-no">{{ displayDraftId }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.status }}</span>
                    <span class="info-value">{{ getFeeDraftStatusText(draft.status) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.caseId }}</span>
                    <router-link class="entity-link info-value" :to="`/cases/${draft.case_id}`">
                      {{ caseDisplayNo }}
                    </router-link>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.clientId }}</span>
                    <router-link
                      v-if="draft.client_id"
                      class="entity-link info-value"
                      :to="`/clients/${draft.client_id}`"
                    >
                      {{ clientDisplayName }}
                    </router-link>
                    <span v-else class="info-value">—</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.draftType }}</span>
                    <span class="info-value">{{ getFeeDraftTypeText(draft.draft_type) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.currency }}</span>
                    <span class="info-value">{{ draft.currency }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">官费合计</span>
                    <span class="info-value mono-num">{{ formatMoney(draft.total_gov, draft.currency) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">服务费合计</span>
                    <span class="info-value mono-num">{{ formatMoney(draft.total_service, draft.currency) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">杂费合计</span>
                    <span class="info-value mono-num">{{ formatMoney(draft.total_misc, draft.currency) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">草稿总额</span>
                    <span class="info-value mono-num">{{ formatMoney(draft.amount, draft.currency) }}</span>
                  </div>
                </div>
              </div>

              <div v-if="sourceFacts" class="case-panel fee-draft-main" data-testid="draft-source-facts">
                <h3 class="panel-heading">计算与来源</h3>
                <el-alert
                  :title="sourceFacts.fee_domain === 'GOV' ? '官费草单：全部明细只读' : '服务费草单：仅授权项目可调整一次'"
                  type="info"
                  :closable="false"
                  show-icon
                />
                <el-table :data="sourceFacts.lines" stripe size="small" class="compact-table source-table">
                  <el-table-column prop="fee_name" label="费用项目" min-width="180" />
                  <el-table-column prop="source_authority" label="来源机构" min-width="150" />
                  <el-table-column prop="source_version" label="版本" min-width="130" />
                  <el-table-column prop="effective_date" label="生效日期" width="120">
                    <template #default="{ row }">{{ row.effective_date || '—' }}</template>
                  </el-table-column>
                  <el-table-column prop="source_ref" label="来源引用" min-width="220" />
                  <el-table-column prop="source_sha256" label="来源摘要" min-width="220">
                    <template #default="{ row }"><span class="source-digest">{{ row.source_sha256 }}</span></template>
                  </el-table-column>
                  <el-table-column prop="activation_status" label="启用状态" width="120" />
                  <el-table-column label="调整记录" min-width="180">
                    <template #default="{ row }">
                      <template v-if="row.adjustment_reason && row.adjustment_before_digest && row.adjustment_after_digest">
                        <div>{{ row.adjustment_reason }}</div>
                        <div>调整前摘要：sha256:{{ row.adjustment_before_digest }}</div>
                        <div>调整后摘要：sha256:{{ row.adjustment_after_digest }}</div>
                      </template>
                      <template v-else>{{ row.adjustable ? '尚未调整' : '不可调整' }}</template>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>

            <div class="case-side-panel">
              <div class="case-panel side-widget">
                <div class="widget-title">{{ ZH.feeDetail.quickActions }}</div>
                <div class="quick-actions">
                  <router-link :to="`/fees/drafts/new`">
                    <el-button size="small">{{ ZH.feeDetail.newDraft }}</el-button>
                  </router-link>
                  <router-link :to="`/fees/drafts/new?case_id=${draft.case_id}&draft_type=APPLY_FEE`">
                    <el-button size="small" type="primary">生成申请费草稿</el-button>
                  </router-link>
                  <router-link :to="`/cases/${draft.case_id}`">
                    <el-button size="small">{{ ZH.feeDetail.openCase }}</el-button>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <FeeLinkagePanel
        v-if="feePackageId"
        class="fee-linkage-section"
        :package-id="feePackageId"
        :focus-id="draft.id"
      />
    </template>

    <div v-else-if="!loading && !error" class="page-empty">
      <div class="empty-state">
        <span class="empty-icon">📝</span>
        <h3 class="empty-title">{{ ZH.feeDetail.notFound }}</h3>
        <p class="empty-message">{{ ZH.feeDetail.notFoundMsg }}</p>
        <el-button type="primary" @click="goBack">{{ ZH.common.back }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCase } from '../../../api/cases'
import { getClient } from '../../../api/clients'
import { getFeeDraft, getFeeDraftSourceFacts, lockFeeDraft, unlockFeeDraft } from '../../../api/fees'
import type { DemoV6DraftSourceFacts, FeeDraftDetail } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import FeeDraftItemsTable from '../components/FeeDraftItemsTable.vue'
import RelationChainCard from '../../../components/relations/RelationChainCard.vue'
import FeeLinkagePanel from '../../officialWorkflows/components/FeeLinkagePanel.vue'
import { usePageContext } from '../../../stores/pageContext'
import { ZH } from '../../../constants/labels.zh'
import { getFeeDraftStatusText, getFeeDraftTypeText } from '../../../constants/displayText'
import { formatMoney } from '../../../utils/money'

const route = useRoute()
const router = useRouter()
const pageContext = usePageContext()

const draft = ref<FeeDraftDetail | null>(null)
const sourceFacts = ref<DemoV6DraftSourceFacts | null>(null)
const sourceFactsResolved = ref(false)
const loading = ref(false)
const error = ref<ApiError | null>(null)
const activeTab = ref('items')
const caseDisplayNo = ref('')
const clientDisplayName = ref('')

// Lock state
const lockLoading = ref(false)
const lockError = ref<ApiError | null>(null)

const draftId = computed(() => String(route.params.id || ''))
const feePackageId = computed(() => String(route.query.package_id || route.query.packageId || '').trim())
const displayDraftId = computed(() => draft.value?.id || '—')

const isLocked = computed(() => draft.value?.status === 'LOCKED')

const statusTagType = computed<'warning' | 'info'>(() => {
  return draft.value?.status === 'LOCKED' ? 'warning' : 'info'
})

async function refreshSourceFacts() {
  sourceFactsResolved.value = false
  try {
    sourceFacts.value = await getFeeDraftSourceFacts(draftId.value)
    sourceFactsResolved.value = true
  } catch (err) {
    sourceFacts.value = null
    sourceFactsResolved.value = (err as { response?: { status?: number } })?.response?.status === 404
  }
}

async function resolveDisplayContext() {
  caseDisplayNo.value = draft.value?.case_id ? '未命名案件' : ''
  clientDisplayName.value = draft.value?.client_id ? '未命名客户' : ''

  const jobs: Promise<void>[] = []

  if (draft.value?.case_id) {
    jobs.push(
      getCase(draft.value.case_id)
        .then(caseData => {
          caseDisplayNo.value = caseData.case_no || '未命名案件'
        })
        .catch(() => {
          caseDisplayNo.value = '未命名案件'
        })
    )
  }

  if (draft.value?.client_id) {
    jobs.push(
      getClient(draft.value.client_id)
        .then(clientData => {
          clientDisplayName.value = clientData.name || '未命名客户'
        })
        .catch(() => {
          clientDisplayName.value = '未命名客户'
        })
    )
  }

  await Promise.all(jobs)
}

async function fetchDraft() {
  if (!draftId.value) return

  loading.value = true
  error.value = null

  try {
    draft.value = await getFeeDraft(draftId.value)
    await refreshSourceFacts()
    await resolveDisplayContext()
    pageContext.setBreadcrumb(['费用管理', '费用草稿', displayDraftId.value])
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function confirmLock() {
  try {
    await ElMessageBox.confirm(
      ZH.feeDetail.lockConfirm,
      ZH.feeDetail.lockTitle,
      {
        confirmButtonText: ZH.feeDetail.lock,
        cancelButtonText: ZH.common.cancel,
        type: 'warning',
      }
    )

    await performLock()
  } catch {
    // User cancelled
  }
}

async function performLock() {
  lockLoading.value = true
  lockError.value = null

  try {
    draft.value = await lockFeeDraft(draftId.value)
    await refreshSourceFacts()
    ElMessage.success(ZH.feeDetail.lockSuccess)
  } catch (err) {
    const apiError = err as ApiError
    lockError.value = apiError

    if (apiError.status === 409) {
      ElMessage.error('冲突：该草稿可能已被修改，请刷新后重试。')
    }
  } finally {
    lockLoading.value = false
  }
}

async function confirmUnlock() {
  try {
    await ElMessageBox.confirm(
      ZH.feeDetail.unlockConfirm,
      ZH.feeDetail.unlockTitle,
      {
        confirmButtonText: ZH.feeDetail.unlock,
        cancelButtonText: ZH.common.cancel,
        type: 'info',
      }
    )

    await performUnlock()
  } catch {
    // User cancelled
  }
}

async function performUnlock() {
  lockLoading.value = true
  lockError.value = null

  try {
    draft.value = await unlockFeeDraft(draftId.value)
    await refreshSourceFacts()
    ElMessage.success(ZH.feeDetail.unlockSuccess)
  } catch (err) {
    const apiError = err as ApiError
    lockError.value = apiError

    if (apiError.status === 409) {
      ElMessage.error('冲突：该草稿可能已被修改，请刷新后重试。')
    }
  } finally {
    lockLoading.value = false
  }
}

function goBack() {
  router.push('/fees/drafts')
}

onMounted(() => {
  fetchDraft()
})

onBeforeUnmount(() => {
  pageContext.clear()
})
</script>

<style scoped>
.meta-subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: var(--text-sub);
}

.entity-link {
  color: var(--color-primary);
  font-family: var(--font-mono);
  text-decoration: none;
}

.entity-link:hover {
  text-decoration: underline;
}

.locked-badge {
  margin-left: 8px;
}

.locked-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  background: var(--color-warning-bg, #fdf6ec);
  border: 1px solid var(--color-warning-border, #f5dab1);
  border-radius: var(--radius-card);
  color: var(--color-warning-text, #e6a23c);
  font-size: 14px;
}

.locked-notice-icon {
  font-size: 16px;
}

.fee-linkage-section {
  margin-top: 16px;
}

.source-table {
  margin-top: 16px;
}

.source-digest {
  font-family: var(--font-mono);
  font-size: 12px;
  overflow-wrap: anywhere;
}
</style>
