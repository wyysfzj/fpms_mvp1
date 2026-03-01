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
        :client="draft.client_id ? { id: draft.client_id } : undefined"
        :case-ref="draft.case_id ? { id: draft.case_id } : undefined"
        :fee-draft="{ id: draft.id, label: draft.draft_type }"
      />

      <div class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <el-tag :type="statusTagType" size="small">{{ getFeeDraftStatusText(draft.status) }}</el-tag>
            <el-tag v-if="isLocked" type="danger" size="small" class="locked-badge">
              🔒 已锁定
            </el-tag>
            <span class="meta-divider">|</span>
            <span class="case-no">{{ ZH.feeDetail.draftId }}: {{ draft.id }}</span>
            <span class="meta-divider">|</span>
            <span>{{ ZH.feeDetail.currency }}: {{ draft.currency }}</span>
          </div>
          <div class="case-title">
            <h1>{{ ZH.feeDetail.feeDraft }}</h1>
            <p class="meta-subtitle">
              {{ ZH.feeDetail.draftType }}: {{ draft.draft_type }}
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
                    <span class="info-value case-no">{{ draft.id }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.status }}</span>
                    <span class="info-value">{{ getFeeDraftStatusText(draft.status) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.caseId }}</span>
                    <router-link class="entity-link info-value" :to="`/cases/${draft.case_id}`">
                      {{ draft.case_id }}
                    </router-link>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.clientId }}</span>
                    <router-link
                      v-if="draft.client_id"
                      class="entity-link info-value"
                      :to="`/clients/${draft.client_id}/edit`"
                    >
                      {{ draft.client_id }}
                    </router-link>
                    <span v-else class="info-value">—</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.draftType }}</span>
                    <span class="info-value">{{ draft.draft_type }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.feeDetail.currency }}</span>
                    <span class="info-value">{{ draft.currency }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="case-side-panel">
              <div class="case-panel side-widget">
                <div class="widget-title">{{ ZH.feeDetail.quickActions }}</div>
                <div class="quick-actions">
                  <router-link :to="`/fees/drafts/new`">
                    <el-button size="small">{{ ZH.feeDetail.newDraft }}</el-button>
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
import { getFeeDraft, lockFeeDraft, unlockFeeDraft } from '../../../api/fees'
import type { FeeDraftDetail } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import FeeDraftItemsTable from '../components/FeeDraftItemsTable.vue'
import RelationChainCard from '../../../components/relations/RelationChainCard.vue'
import { usePageContext } from '../../../stores/pageContext'
import { ZH } from '../../../constants/labels.zh'
import { getFeeDraftStatusText } from '../../../constants/displayText'

const route = useRoute()
const router = useRouter()
const pageContext = usePageContext()

const draft = ref<FeeDraftDetail | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)
const activeTab = ref('items')

// Lock state
const lockLoading = ref(false)
const lockError = ref<ApiError | null>(null)

const draftId = computed(() => String(route.params.id || ''))

const isLocked = computed(() => draft.value?.status === 'LOCKED')

const statusTagType = computed<'warning' | 'info'>(() => {
  return draft.value?.status === 'LOCKED' ? 'warning' : 'info'
})

async function fetchDraft() {
  if (!draftId.value) return

  loading.value = true
  error.value = null

  try {
    draft.value = await getFeeDraft(draftId.value)
    pageContext.setBreadcrumb(['费用管理', '费用草稿', draftId.value.slice(0, 8)])
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
</style>
