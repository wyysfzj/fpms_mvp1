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
                    <span class="info-label">案件类型</span>
                    <span class="info-value">{{ caseTypeText }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">专利类别</span>
                    <span class="info-value">{{ patentCategoryText }}</span>
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
                    <span class="info-label">收文日</span>
                    <span class="info-value">{{ caseData.recv_date || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.caseDetail.appDate }}</span>
                    <span class="info-value">{{ caseData.app_date || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">申请号</span>
                    <span class="info-value">{{ caseData.app_no || '-' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">流程方向</span>
                    <span class="info-value">{{ flowDirText }}</span>
                  </div>
                </div>

                <div v-if="statusAutomationHint" class="status-linkage-card">
                  <h4 class="info-section-title">状态联动说明</h4>
                  <p class="status-linkage-text">{{ statusAutomationHint }}</p>
                </div>

                <div v-if="caseData.applicants?.length || caseData.inventors?.length" class="info-section">
                  <h4 class="info-section-title">官方提交主体信息</h4>
                  <div v-if="caseData.applicants?.length" class="official-party-list">
                    <div
                      v-for="(applicant, index) in caseData.applicants"
                      :key="`applicant-${index}`"
                      class="official-party-item"
                    >
                      <strong>申请人 {{ index + 1 }}</strong>
                      <span>名称：{{ applicant.name_cn || applicant.name_en || '-' }}</span>
                      <span>国籍：{{ applicant.nationality || '-' }}</span>
                      <span>证件类型：{{ applicant.certificate_type || '-' }}</span>
                      <span>证件号：{{ applicant.certificate_no || '-' }}</span>
                      <span>官方邮编：{{ applicant.official_postcode || '-' }}</span>
                      <span>官方申请人类型：{{ applicant.official_applicant_kind || '-' }}</span>
                    </div>
                  </div>
                  <div v-if="caseData.inventors?.length" class="official-party-list">
                    <div
                      v-for="(inventor, index) in caseData.inventors"
                      :key="`inventor-${index}`"
                      class="official-party-item"
                    >
                      <strong>发明人 {{ index + 1 }}</strong>
                      <span>姓名：{{ inventor.name_cn || inventor.name_en || '-' }}</span>
                      <span>国籍：{{ inventor.nationality || '-' }}</span>
                      <span>中国籍身份证号：{{ inventor.china_id_no || '-' }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="caseData.priorities?.length" class="info-section">
                  <h4 class="info-section-title">优先权信息</h4>
                  <div class="priority-list">
                    <div v-for="priority in caseData.priorities" :key="priority.seq" class="priority-item">
                      <span>第 {{ priority.seq }} 条</span>
                      <span>{{ priority.country_code || '-' }}</span>
                      <span>{{ priority.prio_no || '-' }}</span>
                      <span>{{ priority.prio_date || '-' }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="caseData.foreign_agent_name || caseData.foreign_ref || caseData.from_country || caseData.to_country || caseData.doc_address_id || caseData.bill_address_id" class="info-section">
                  <h4 class="info-section-title">涉外代理信息</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">外方代理</span>
                      <span class="info-value">{{ formatForeignAgentDisplay() }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">外方案号</span>
                      <span class="info-value">{{ caseData.foreign_ref || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">来源国家/地区</span>
                      <span class="info-value">{{ caseData.from_country || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">目标国家/地区</span>
                      <span class="info-value">{{ caseData.to_country || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">公文地址</span>
                      <span class="info-value">{{ formatAddressConfiguredDisplay(caseData.doc_address_id) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">账单地址</span>
                      <span class="info-value">{{ formatAddressConfiguredDisplay(caseData.bill_address_id) }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="caseData.bio_deposits?.length" class="info-section">
                  <h4 class="info-section-title">菌种保藏</h4>
                  <div class="priority-list">
                    <div v-for="bioDeposit in caseData.bio_deposits" :key="bioDeposit.seq" class="priority-item bio-item">
                      <span>第 {{ bioDeposit.seq }} 条</span>
                      <span>{{ bioDeposit.deposit_no || '-' }}</span>
                      <span>{{ bioDeposit.deposit_unit_name || '-' }}</span>
                      <span>{{ bioDeposit.deposit_date || '-' }}</span>
                      <span>{{ bioDeposit.name || '-' }}</span>
                    </div>
                  </div>
                </div>

                <div
                  v-if="caseData.intl_app_no || caseData.intl_app_date || caseData.pct_national_entry_date"
                  class="info-section"
                >
                  <h4 class="info-section-title">PCT 信息</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">国际申请号</span>
                      <span class="info-value">{{ caseData.intl_app_no || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">国际申请日</span>
                      <span class="info-value">{{ caseData.intl_app_date || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">RO</span>
                      <span class="info-value">{{ caseData.ro || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">ISA</span>
                      <span class="info-value">{{ caseData.isa || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">IPEA</span>
                      <span class="info-value">{{ caseData.ipea || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">国际公开号</span>
                      <span class="info-value">{{ caseData.intl_pub_no || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">国际公开日</span>
                      <span class="info-value">{{ caseData.intl_pub_date || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">国际公开语言</span>
                      <span class="info-value">{{ caseData.intl_pub_lang || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">需要 IPER</span>
                      <span class="info-value">{{ caseData.need_iper === true ? '是' : caseData.need_iper === false ? '否' : '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">IPER 日期</span>
                      <span class="info-value">{{ caseData.iper_date || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">国家阶段进入日</span>
                      <span class="info-value">{{ caseData.pct_national_entry_date || '-' }}</span>
                    </div>
                  </div>
                </div>

                <div
                  v-if="caseData.original_case_id || caseData.invalid_client_id || caseData.invalid_patentee || caseData.invalid_requester || caseData.invalid_role"
                  class="info-section"
                >
                  <h4 class="info-section-title">无效案件信息</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">原案</span>
                      <span class="info-value">{{ formatOriginalCaseDisplay(caseData.original_case_id) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">委托方</span>
                      <span class="info-value">{{ formatInvalidClientDisplay() }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">专利权人</span>
                      <span class="info-value">{{ caseData.invalid_patentee || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">请求人</span>
                      <span class="info-value">{{ caseData.invalid_requester || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">我方角色</span>
                      <span class="info-value">{{ invalidRoleText }}</span>
                    </div>
                  </div>
                </div>

                <!-- A3: Publication & Grant -->
                <div v-if="caseData.issue_date || caseData.cert_no || caseData.pub_date || caseData.pub_no || caseData.grant_date || caseData.grant_no || caseData.patent_no || caseData.valid_until" class="info-section">
                  <h4 class="info-section-title">公告与授权</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="info-label">发证日</span>
                      <span class="info-value">{{ caseData.issue_date || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">证书号</span>
                      <span class="info-value">{{ caseData.cert_no || '-' }}</span>
                    </div>
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
                <div v-if="caseData.spec_pages != null || caseData.draw_pages != null || caseData.claim_count != null || caseData.claim_pages != null || caseData.manuscript_words != null || caseData.has_exam_request != null" class="info-section">
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
                      <span class="info-label">附图页数</span>
                      <span class="info-value">{{ caseData.draw_pages ?? '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">权利要求页数</span>
                      <span class="info-value">{{ caseData.claim_pages ?? '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">说明书字数</span>
                      <span class="info-value">{{ caseData.manuscript_words ?? '-' }}</span>
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
                      <span class="info-value">{{ formatAgentAssignmentDisplay(caseData.primary_agent_id) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">辅办代理人</span>
                      <span class="info-value">{{ formatAgentAssignmentDisplay(caseData.second_agent_id) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">撰写人</span>
                      <span class="info-value">{{ formatAgentAssignmentDisplay(caseData.draftor_id) }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="caseData.agent_splits?.length" class="info-section">
                  <h4 class="info-section-title">代理人分摊</h4>
                  <div class="priority-list">
                    <div
                      v-for="(agentSplit, index) in caseData.agent_splits"
                      :key="`${agentSplit.agent_id || 'agent'}-${agentSplit.role || 'role'}-${index}`"
                      class="priority-item"
                    >
                      <span>分摊 {{ index + 1 }}</span>
                      <span>{{ formatAgentSplitDisplay(agentSplit.agent_id) }}</span>
                      <span>{{ formatAgentSplitRole(agentSplit.role) }}</span>
                      <span>{{ formatShareRatio(agentSplit.share_ratio) }}</span>
                    </div>
                  </div>
                </div>

                <!-- A3: Control Flags -->
                <div v-if="caseData.is_fee_monitor != null || caseData.fee_reduction || caseData.applicant_kind || caseData.discount_rate || caseData.no_power != null || caseData.no_prio_text != null || caseData.require_hk != null || caseData.first_annuity_year != null" class="info-section">
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
                    <div class="info-item">
                      <span class="info-label">减免比例</span>
                      <span class="info-value">{{ caseData.discount_rate || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">无委托书</span>
                      <span class="info-value">{{ caseData.no_power === true ? '是' : caseData.no_power === false ? '否' : '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">无优先权文本</span>
                      <span class="info-value">{{ caseData.no_prio_text === true ? '是' : caseData.no_prio_text === false ? '否' : '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">要求港澳台</span>
                      <span class="info-value">{{ caseData.require_hk === true ? '是' : caseData.require_hk === false ? '否' : '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">首年年费年度</span>
                      <span class="info-value">{{ caseData.first_annuity_year ?? '-' }}</span>
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
import { getCase, getCaseByCaseNo } from '../../../api/cases'
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

const statusDisplayText = computed(() => {
  const status = caseData.value?.status
  if (!status) return '-'

  const mappedStatus = getCaseStatusText(status)
  return mappedStatus === status ? formatUnknownCode('案件状态') : mappedStatus
})

const FEE_REDUCTION_MAP: Record<string, string> = {
  NONE: '不减免', PARTIAL: '部分减免', FULL: '全额减免'
}
const APPLICANT_KIND_MAP: Record<string, string> = {
  INDIVIDUAL: '个人', ENTITY: '企业', UNIV: '高校', GOV: '政府'
}
const CASE_TYPE_MAP: Record<string, string> = {
  NORMAL: '普通案件',
  PCT_INTL: 'PCT 国际阶段',
  PCT_NATL: 'PCT 国家阶段',
  INVALIDATION: '无效案件',
  PRIORITY: '优先权案件',
  CONSULTING: '顾问项目',
  SEARCH: '检索项目',
}
const PATENT_CATEGORY_MAP: Record<string, string> = {
  INV: '发明',
  UM: '实用新型',
  DES: '外观设计',
}
const FLOW_DIR_MAP: Record<string, string> = {
  CN_DOMESTIC: '中国国内',
  CN_OUTBOUND: '中国向外',
  FOREIGN_INBOUND: '国外进入中国',
}

const feeReductionText = computed(() =>
  caseData.value?.fee_reduction
    ? formatMappedCode(caseData.value.fee_reduction, FEE_REDUCTION_MAP, '减免类型')
    : '-'
)
const applicantKindText = computed(() =>
  caseData.value?.applicant_kind
    ? formatMappedCode(caseData.value.applicant_kind, APPLICANT_KIND_MAP, '申请人类型')
    : '-'
)
const caseTypeText = computed(() =>
  caseData.value?.case_type
    ? formatMappedCode(caseData.value.case_type, CASE_TYPE_MAP, '案件类型')
    : '-'
)
const patentCategoryText = computed(() =>
  caseData.value?.patent_category
    ? formatMappedCode(caseData.value.patent_category, PATENT_CATEGORY_MAP, '专利类别')
    : '-'
)
const flowDirText = computed(() =>
  caseData.value?.flow_dir
    ? formatMappedCode(caseData.value.flow_dir, FLOW_DIR_MAP, '流程方向')
    : '-'
)
const statusAutomationHint = computed(() => {
  const status = caseData.value?.status || ''
  if (status === 'ACCEPTED') {
    return '当前状态通常由受理通知等流程联动生成，详情页仅展示结果，编辑页会提示谨慎手工修改。'
  }
  if (status === 'GRANT_PENDING') {
    return '当前状态通常由授权缴费/登记相关流程驱动，请结合来往文书与任务面板核对。'
  }
  return ''
})
const invalidRoleText = computed(() => {
  const role = caseData.value?.invalid_role || ''
  if (role === 'PATENTEE') return '代表专利权人'
  if (role === 'REQUESTER') return '代表请求人'
  if (role === 'BOTH') return '双方均代表'
  return role ? formatUnknownCode('我方角色') : '-'
})

async function fetchCase() {
  const caseNo = String(route.params.caseNo || '').trim()
  const id = String(route.params.id || '').trim()
  if (!caseNo && !id) {
    return
  }

  loading.value = true
  error.value = null

  try {
    caseData.value = caseNo ? await getCaseByCaseNo(caseNo) : await getCase(id)
    pageContext.setBreadcrumb(['案件管理', '案件详情', caseData.value.case_no || caseData.value.title || '未命名案件'])
    if (!caseNo && caseData.value.case_no) {
      await router.replace({ name: 'case_detail_by_no', params: { caseNo: caseData.value.case_no } })
    }
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
  if (caseData.value?.case_no) {
    router.push({ name: 'case_edit_by_no', params: { caseNo: caseData.value.case_no } })
    return
  }
  const id = caseData.value?.id || route.params.id
  router.push({ name: 'case_edit', params: { id } })
}

function handleLimitedEditSuccess() {
  fetchCase()
}

function formatUnknownCode(label: string) {
  return `未识别${label}`
}

function formatMappedCode(value: string, map: Record<string, string>, unknownLabel: string) {
  return map[value] || formatUnknownCode(unknownLabel)
}

function formatForeignAgentDisplay() {
  if (caseData.value?.foreign_agent_name) return caseData.value.foreign_agent_name
  if (caseData.value?.foreign_agent_id) return '已关联外方代理'
  return '-'
}

function formatAddressConfiguredDisplay(addressId?: string | null) {
  return addressId ? '已配置' : '-'
}

function formatOriginalCaseDisplay(originalCaseId?: string | null) {
  return originalCaseId ? '已关联原案' : '-'
}

function formatInvalidClientDisplay() {
  if (caseData.value?.invalid_client_name) return caseData.value.invalid_client_name
  if (caseData.value?.invalid_client_id) return '已关联委托方'
  return '-'
}

function formatAgentAssignmentDisplay(agentId?: string | null) {
  return agentId ? '已指定' : '-'
}

function formatAgentSplitDisplay(agentId?: string | null) {
  return agentId ? '已指定代理人' : '-'
}

function formatAgentSplitRole(role?: string | null) {
  if (role === 'Agent') return '代理人'
  return role ? formatUnknownCode('分摊角色') : '-'
}

function formatShareRatio(ratio?: number | null) {
  if (ratio === null || ratio === undefined || !Number.isFinite(ratio)) return '-'
  return `${ratio}%`
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

.status-linkage-card {
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--el-color-warning-light-9) 85%, white);
  border: 1px solid var(--el-color-warning-light-5);
}

.status-linkage-text {
  margin: 0;
  color: var(--text-main);
  line-height: 1.6;
}

.priority-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.official-party-list {
  display: grid;
  gap: 10px;
  margin-bottom: 10px;
}

.official-party-item {
  display: grid;
  grid-template-columns: 120px repeat(3, minmax(0, 1fr));
  gap: 10px 12px;
  padding: 12px 14px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-bg-card);
}

.official-party-item span,
.official-party-item strong {
  overflow-wrap: anywhere;
}

.priority-item {
  display: grid;
  grid-template-columns: 120px repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
}

.bio-item {
  grid-template-columns: 120px repeat(4, minmax(0, 1fr));
}
</style>
