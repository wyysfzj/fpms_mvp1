<template>
  <div class="page-container focus-reading-page case-detail-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> {{ ZH.common.back }}
        </el-button>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="handleEdit">
          {{ ZH.caseDetail.editCase }}
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- Content -->
    <template v-else-if="caseData">
      <!-- Relation Chain -->
      <RelationChainCard
        :client="caseData.client_id ? { id: String(caseData.client_id), name: caseData.client_name } : undefined"
        :case-ref="{ id: caseData.id, no: caseData.case_no, title: caseData.title }"
      />

      <!-- Case Header -->
      <div class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <span class="case-no">{{ caseData.case_no }}</span>
            <span class="meta-divider">|</span>
            <span v-if="caseData.filing_date || caseData.app_date">
              {{ ZH.caseDetail.filingDate }}: {{ caseData.filing_date || caseData.app_date }}
            </span>
            <span class="meta-divider">|</span>
            <span v-if="caseData.client_name">{{ ZH.caseDetail.client }}: {{ caseData.client_name }}</span>
          </div>
          <div class="case-title">
            <h1>{{ caseData.title || ZH.caseDetail.untitled }}</h1>
          </div>
        </div>
        <div class="case-header-actions">
          <span v-if="caseData.status" class="tag" :class="statusTagClass">{{ statusDisplayText }}</span>
        </div>
      </div>

      <!-- V3 Stepper (above tabs) -->
      <CaseStepper :status="caseData.status" />

      <!-- Main content grid: left tabs + right panel -->
      <div class="case-detail-v3-grid">
        <div class="case-detail-v3-main">
          <!-- Tabs -->
          <el-tabs v-model="activeTab" class="case-tabs">
            <el-tab-pane :label="ZH.caseDetail.overview" name="overview">
              <div class="case-panel">
                <h3 class="panel-heading">{{ ZH.caseDetail.caseInfo }}</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">{{ ZH.caseDetail.caseNumber }}</span>
                    <span class="info-value case-no">{{ caseData.case_no }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.caseDetail.title }}</span>
                    <span class="info-value">{{ caseData.title || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.caseDetail.client }}</span>
                    <span class="info-value">{{ caseData.client_name || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.caseDetail.status }}</span>
                    <span class="info-value">{{ statusDisplayText }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.caseDetail.filingDate }}</span>
                    <span class="info-value">{{ caseData.filing_date || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.caseDetail.appDate }}</span>
                    <span class="info-value">{{ caseData.app_date || '-' }}</span>
                  </div>
                </div>

                <!-- A3: Publication & Grant -->
                <div v-if="caseData.pub_date || caseData.pub_no || caseData.grant_date || caseData.grant_no || caseData.patent_no || caseData.valid_until" class="info-section">
                  <h4 class="info-section-title">公告与授权</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">公告日</span>
                      <span class="info-value">{{ caseData.pub_date || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">公告号</span>
                      <span class="info-value">{{ caseData.pub_no || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">授权日</span>
                      <span class="info-value">{{ caseData.grant_date || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">授权号</span>
                      <span class="info-value">{{ caseData.grant_no || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">专利号</span>
                      <span class="info-value">{{ caseData.patent_no || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">有效期至</span>
                      <span class="info-value">{{ caseData.valid_until || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- A3: Specification -->
                <div v-if="caseData.spec_pages != null || caseData.claim_count != null || caseData.has_exam_request != null" class="info-section">
                  <h4 class="info-section-title">说明书信息</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">说明书页数</span>
                      <span class="info-value">{{ caseData.spec_pages ?? '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">权利要求项数</span>
                      <span class="info-value">{{ caseData.claim_count ?? '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">已提实审请求</span>
                      <span class="info-value">{{ caseData.has_exam_request === true ? '是' : caseData.has_exam_request === false ? '否' : '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- A3: Agent Assignment -->
                <div v-if="caseData.primary_agent_id || caseData.second_agent_id || caseData.draftor_id" class="info-section">
                  <h4 class="info-section-title">代理人分配</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">主办代理人</span>
                      <span class="info-value">{{ caseData.primary_agent_id || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">辅办代理人</span>
                      <span class="info-value">{{ caseData.second_agent_id || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">撰写人</span>
                      <span class="info-value">{{ caseData.draftor_id || '-' }}</span>
                    </div>
                  </div>
                </div>

                <!-- A3: Control Flags -->
                <div v-if="caseData.is_fee_monitor != null || caseData.fee_reduction || caseData.applicant_kind" class="info-section">
                  <h4 class="info-section-title">控制标记</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">费用监控</span>
                      <span class="info-value">{{ caseData.is_fee_monitor === true ? '是' : caseData.is_fee_monitor === false ? '否' : '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">减免类型</span>
                      <span class="info-value">{{ feeReductionText }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">申请人类型</span>
                      <span class="info-value">{{ applicantKindText }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="caseData.notes" class="notes-section">
                  <h4 class="notes-title">{{ ZH.caseDetail.notes }}</h4>
                  <p class="notes-content focus-reading-body">{{ caseData.notes }}</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane :label="ZH.caseDetail.claims" name="claims">
              <CaseClaimsTab :applicants="caseData.applicants || []" :inventors="caseData.inventors || []" />
            </el-tab-pane>

            <el-tab-pane :label="ZH.caseDetail.officialDocs" name="docs">
              <CaseDocumentsTab :case-id="caseData.id" />
            </el-tab-pane>

            <el-tab-pane :label="ZH.caseDetail.fees" name="fees">
              <CaseFeesTab :case-id="caseData.id" />
            </el-tab-pane>

            <el-tab-pane :label="ZH.caseDetail.billing" name="billing">
              <div class="case-panel">
                <CaseReceiptsSummary v-if="caseData" :case-id="caseData.id" />
              </div>
            </el-tab-pane>

            <el-tab-pane :label="ZH.caseDetail.tasks" name="tasks">
              <CaseTasksTab :case-id="caseData.id" />
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- Right Panel -->
        <div class="case-detail-v3-aside">
          <CaseDeadlineCard :case-id="caseData.id" />
          <CaseRelatedTasks :case-id="caseData.id" />

          <!-- Inventors -->
          <div v-if="caseData.inventors?.length" style="margin-top: 14px;">
            <div class="related-tasks-title">{{ ZH.caseDetail.inventors }}</div>
            <div class="inventor-tags">
              <span
                v-for="(inventor, idx) in caseData.inventors"
                :key="idx"
                class="inventor-tag"
              >
                {{ inventor.name_cn || inventor.name_en || '—' }}
              </span>
            </div>
          </div>

          <!-- Quick Actions -->
          <div style="margin-top: 14px;">
            <div class="related-tasks-title">{{ ZH.caseDetail.quickActions }}</div>
            <div class="quick-actions">
              <el-button size="small" @click="handleEdit">{{ ZH.caseDetail.editCase }}</el-button>
              <el-button size="small" @click="showLimitedEdit = true">{{ ZH.caseDetail.quickEdit }}</el-button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Empty State (case not found) -->
    <div v-else-if="!loading && !error" class="page-empty">
      <div class="empty-state">
        <span class="empty-icon">📂</span>
        <h3 class="empty-title">{{ ZH.caseDetail.notFound }}</h3>
        <p class="empty-message">{{ ZH.caseDetail.notFoundMsg }}</p>
        <el-button type="primary" @click="goBack">{{ ZH.common.back }}</el-button>
      </div>
    </div>

    <!-- Limited Edit Dialog -->
    <LimitedEditDialog
      v-if="caseData"
      v-model="showLimitedEdit"
      :case-id="caseData.id"
      :initial-notes="caseData.notes"
      @success="handleLimitedEditSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCase } from '../../../api/cases'
import type { Case } from '../../../api/cases.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import RelationChainCard from '../../../components/relations/RelationChainCard.vue'
import LimitedEditDialog from '../components/LimitedEditDialog.vue'
import CaseReceiptsSummary from '../components/CaseReceiptsSummary.vue'
import CaseStepper from '../components/CaseStepper.vue'
import CaseDeadlineCard from '../components/CaseDeadlineCard.vue'
import CaseRelatedTasks from '../components/CaseRelatedTasks.vue'
import CaseDocumentsTab from '../components/CaseDocumentsTab.vue'
import CaseTasksTab from '../components/CaseTasksTab.vue'
import CaseFeesTab from '../components/CaseFeesTab.vue'
import CaseClaimsTab from '../components/CaseClaimsTab.vue'
import { usePageContext } from '../../../stores/pageContext'
import { ZH } from '../../../constants/labels.zh'
import { getStatusTagClass } from '../../../constants/workflow'
import { getCaseStatusText } from '../../../constants/displayText'

const route = useRoute()
const router = useRouter()
const pageContext = usePageContext()

const caseData = ref<Case | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)
const activeTab = ref('overview')
const showLimitedEdit = ref(false)

const statusTagClass = computed(() =>
  caseData.value?.status ? getStatusTagClass(caseData.value.status) : 'gray'
)

const statusDisplayText = computed(() => getCaseStatusText(caseData.value?.status))

const FEE_REDUCTION_MAP: Record<string, string> = {
  NONE: '不减免', PARTIAL: '部分减免', FULL: '全额减免'
}
const APPLICANT_KIND_MAP: Record<string, string> = {
  INDIVIDUAL: '个人', ENTITY: '企业', UNIV: '高校', GOV: '政府'
}

const feeReductionText = computed(() =>
  caseData.value?.fee_reduction
    ? FEE_REDUCTION_MAP[caseData.value.fee_reduction] || caseData.value.fee_reduction
    : '-'
)
const applicantKindText = computed(() =>
  caseData.value?.applicant_kind
    ? APPLICANT_KIND_MAP[caseData.value.applicant_kind] || caseData.value.applicant_kind
    : '-'
)

async function fetchCase() {
  const id = String(route.params.id || '').trim()
  if (!id) {
    return
  }

  loading.value = true
  error.value = null

  try {
    caseData.value = await getCase(id)
    pageContext.setBreadcrumb(['案件管理', '案件详情', caseData.value.case_no || id])
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/cases')
}

function handleEdit() {
  const id = route.params.id
  router.push(`/cases/${id}/edit`)
}

function handleLimitedEditSuccess() {
  fetchCase()
}

onMounted(() => {
  fetchCase()
})

onBeforeUnmount(() => {
  pageContext.clear()
})
</script>

<style scoped>
.info-section {
  margin-top: 20px;
}
.info-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}
</style>
