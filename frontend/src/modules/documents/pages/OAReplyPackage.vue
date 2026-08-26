<template>
  <main class="page-container oa-reply-page">
    <div class="page-header">
      <div>
        <h1>OA答复工作包</h1>
        <p class="page-subtitle">核对源官文、回复链、陈述意见、附加文件和官方页面人工确认状态。</p>
      </div>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button
          type="primary"
          :disabled="!packageId"
          :loading="refreshing"
          @click="handleRefresh"
        >
          刷新工作包
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-alert
      v-if="!packageId && !documentId && !loading"
      type="info"
      :closable="false"
      title="请选择具体OA答复工作包"
      description="请从官文、任务或工作包入口进入；文书详情入口会保留当前文书上下文。"
      show-icon
    />

    <div v-else-if="loading" class="page-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <template v-else-if="oaPackage">
      <section class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <el-tag :type="getPackageStatusTagType(oaPackage.package.status)" size="small">
              {{ getPackageStatusText(oaPackage.package.status) }}
            </el-tag>
            <span class="meta-divider">|</span>
            <span class="case-no">工作包 {{ oaPackage.package.id }}</span>
            <span class="meta-divider">|</span>
            <router-link class="entity-link" :to="`/cases/${oaPackage.package.case_id}`">
              查看案件
            </router-link>
          </div>
          <div class="case-title">
            <h2>{{ oaPackage.notice_name || 'OA答复核对' }}</h2>
            <p>官方提交证明以回执归档状态为准，回复日期仅表示内部回复链已维护。</p>
          </div>
        </div>
      </section>

      <div class="summary-grid">
        <div class="summary-card">
          <span>申请号</span>
          <strong>{{ oaPackage.application_no || '待维护' }}</strong>
          <small>{{ oaPackage.applicant_display || '申请人待维护' }}</small>
        </div>
        <div class="summary-card">
          <span>官文代码</span>
          <strong>{{ oaPackage.notice_code || '待确认' }}</strong>
          <small>{{ oaPackage.issue_sequence || '通知次数待确认' }}</small>
        </div>
        <div class="summary-card">
          <span>官方期限</span>
          <strong>{{ oaPackage.official_due_date || '待维护' }}</strong>
          <small>内部期限：{{ oaPackage.internal_due_date || '待维护' }}</small>
        </div>
        <div class="summary-card">
          <span>答复状态</span>
          <strong>{{ getReplyStatusText(oaPackage.reply_status) }}</strong>
          <small>回执归档：{{ receiptEvidenceStatus }}</small>
        </div>
      </div>

      <div class="oa-layout">
        <div class="main-stack">
          <section class="case-panel">
            <div class="panel-toolbar">
              <h3 class="panel-heading">源官文与回复链</h3>
              <el-tag :type="receiptEvidenceReady ? 'success' : 'warning'" size="small">
                {{ receiptEvidenceReady ? '回执依据已满足' : '回执依据待确认' }}
              </el-tag>
            </div>
            <div class="reply-chain-grid">
              <div class="reply-chain-card">
                <span>源官文</span>
                <strong>{{ getDocumentLabel(oaPackage.source_document) }}</strong>
                <small>{{ getDocumentDateText(oaPackage.source_document) }}</small>
              </div>
              <div class="reply-chain-card">
                <span>答复文书</span>
                <strong>{{ getDocumentLabel(oaPackage.reply_document) }}</strong>
                <small>{{ getReplyDocumentDateText(oaPackage.reply_document) }}</small>
              </div>
            </div>
            <el-form label-position="top" class="reply-selector">
              <el-form-item label="答复文书">
                <el-select v-model="selectedReplyKey" placeholder="请选择当前案件已复核答复文书">
                  <el-option
                    v-for="option in replyOptions"
                    :key="replyKey(option)"
                    :value="replyKey(option)"
                    :label="`${option.title}｜${option.role}｜${option.filename}`"
                  />
                </el-select>
              </el-form-item>
              <el-button
                type="primary"
                :disabled="!selectedReply"
                :loading="linkingReply"
                @click="handleLinkReplyDocument"
              >
                关联所选答复文书
              </el-button>
            </el-form>
          </section>

          <section class="case-panel">
            <h3 class="panel-heading">陈述意见</h3>
            <div v-if="oaPackage.statement_text" class="statement-preview">
              {{ oaPackage.statement_text }}
            </div>
            <el-empty v-else description="暂无陈述意见文本" :image-size="72" />
          </section>

          <OAReplyChecklist :official-page-checklist="oaPackage.official_page_checklist" />
          <OAReplyManifest
            :statement-word="oaPackage.statement_word"
            :statement-pdf="oaPackage.statement_pdf"
            :modified-claim-files="oaPackage.modified_claim_files"
            :comparison-page="oaPackage.comparison_page"
            :proof-files="oaPackage.proof_files"
            :experiment-data-submitted="oaPackage.experiment_data_submitted"
            :oa-file-roles="oaPackage.oa_file_roles"
          />
          <ReceiptArchivePanel
            :package-id="oaPackage.package.id"
            :case-id="oaPackage.package.case_id"
            :package-kind="oaPackage.package.package_kind"
            :package-status="oaPackage.package.status"
            :archive-status="oaPackage.package.status"
            :receipt-evidence-ready="receiptEvidenceReady"
            receipt-gate-label="OA电子申请回执 / 附加文件归档"
            @refresh-requested="fetchPackage"
            @error="error = $event"
          />
        </div>

        <aside class="side-stack">
          <section class="case-panel side-widget">
            <div class="widget-title">审核动作</div>
            <div class="review-actions">
              <el-button
                v-for="action in requiredChecklistActions"
                :key="action.code"
                size="small"
                :type="action.code === 'STATEMENT_TEXT_CONFIRMED' ? 'primary' : 'default'"
                :loading="reviewingCode === action.code"
                @click="handleChecklistDone(action.code, action.evidenceNote)"
              >
                {{ action.label }}
              </el-button>
              <el-button
                size="small"
                :loading="experimentUpdating"
                @click="handleExperimentToggle"
              >
                {{ oaPackage.experiment_data_submitted ? '取消实验数据标记' : '标记补交实验数据' }}
              </el-button>
            </div>
          </section>

          <section class="case-panel side-widget">
            <div class="widget-title">官文信息</div>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">官文名称</span>
                <span class="info-value">{{ oaPackage.notice_name || '待确认' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">官文代码</span>
                <span class="info-value">{{ oaPackage.notice_code || '待确认' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">发文日</span>
                <span class="info-value">{{ oaPackage.issue_date || '待确认' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">通知次数</span>
                <span class="info-value">{{ oaPackage.issue_sequence || '待确认' }}</span>
              </div>
            </div>
          </section>

          <section class="case-panel side-widget">
            <div class="widget-title">责任边界</div>
            <ul class="boundary-list">
              <li>系统准备字段、文本、文件角色和核对状态。</li>
              <li>工作人员在官方页面完成签名、提交和确认。</li>
              <li>工作包关闭依据来自回执或归档状态。</li>
            </ul>
          </section>
        </aside>
      </div>
    </template>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getOaReplyPackage,
  linkReviewedOaReplyDocument,
  refreshOaReplyPackage,
  resolveOaReplyPackage,
  updateOaReplyChecklist,
} from '../../../api/officialWorkflows'
import {
  getCaseDocumentsWithEvidence,
  selectReviewedReplyDocumentOptions,
} from '../../../api/documents'
import type { ReviewedReplyDocumentOption } from '../../../api/documents.types'
import type {
  OaReplyDocument,
  OaReplyPackage,
  OfficialWorkPackageChecklist,
} from '../../../api/officialWorkflows.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import OAReplyChecklist from '../components/OAReplyChecklist.vue'
import OAReplyManifest from '../components/OAReplyManifest.vue'
import ReceiptArchivePanel from '../../officialWorkflows/components/ReceiptArchivePanel.vue'

const route = useRoute()
const router = useRouter()

const oaPackage = ref<OaReplyPackage | null>(null)
const loading = ref(false)
const refreshing = ref(false)
const reviewingCode = ref('')
const experimentUpdating = ref(false)
const error = ref<ApiError | null>(null)
const replyOptions = ref<ReviewedReplyDocumentOption[]>([])
const selectedReplyKey = ref('')
const linkingReply = ref(false)

const packageId = computed(() => String(route.query.package_id || route.query.packageId || '').trim())
const documentId = computed(() => String(route.query.document_id || route.query.documentId || '').trim())

const receiptEvidenceReady = computed(() => isDone(oaPackage.value?.package.status))
const selectedReply = computed(() =>
  replyOptions.value.find((option) => replyKey(option) === selectedReplyKey.value) || null
)
const receiptEvidenceStatus = computed(() => {
  if (!oaPackage.value) return '待生成'
  return receiptEvidenceReady.value ? '已归档' : '待回执归档'
})

const requiredChecklistActions = [
  { code: 'STATEMENT_TEXT_CONFIRMED', label: '确认陈述意见文本', evidenceNote: '陈述意见文本已人工确认' },
  { code: 'PDF_FIDELITY_CONFIRMED', label: '确认PDF保真附件', evidenceNote: 'PDF保真附件已人工确认' },
  { code: 'MODIFIED_CLAIMS_CONFIRMED', label: '确认修改文件', evidenceNote: '修改文件已人工确认' },
  { code: 'EXPERIMENT_DATA_FLAG_CONFIRMED', label: '确认实验数据标记', evidenceNote: '补交实验数据标记已人工确认' },
  { code: 'PREVIEW_CONFIRMED', label: '确认官方页面预览', evidenceNote: '官方页面预览已人工确认' },
  { code: 'SIGNATURE_CONFIRMED', label: '确认签名与提交', evidenceNote: '签名与提交已由人工确认' },
]

watch(packageId, (nextPackageId) => {
  if (nextPackageId && nextPackageId === oaPackage.value?.package.id) return
  void fetchPackage()
})

onMounted(() => {
  void initializePackage()
})

async function initializePackage() {
  if (packageId.value) {
    await fetchPackage()
    return
  }
  if (!documentId.value) {
    oaPackage.value = null
    return
  }

  loading.value = true
  error.value = null
  try {
    const resolved = await resolveOaReplyPackage(documentId.value)
    oaPackage.value = resolved
    await loadReplyCandidates()
    const query = { ...route.query }
    delete query.document_id
    delete query.documentId
    await router.replace({
      query: {
        ...query,
        package_id: resolved.package.id,
      },
    })
  } catch (err) {
    error.value = localizeResolveError(err)
  } finally {
    loading.value = false
  }
}

async function fetchPackage() {
  if (!packageId.value) {
    oaPackage.value = null
    return
  }

  loading.value = true
  error.value = null
  try {
    oaPackage.value = await getOaReplyPackage(packageId.value)
    await loadReplyCandidates()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  if (!packageId.value) return

  refreshing.value = true
  error.value = null
  try {
    oaPackage.value = await refreshOaReplyPackage(packageId.value)
    await loadReplyCandidates()
    ElMessage.success('工作包已刷新')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    refreshing.value = false
  }
}

async function handleChecklistDone(itemCode: string, evidenceNote: string) {
  if (!packageId.value) return

  reviewingCode.value = itemCode
  error.value = null
  try {
    const result = await updateOaReplyChecklist(packageId.value, itemCode, {
      status: 'DONE',
      evidence_note: evidenceNote,
    })
    replaceChecklistItem(result.checklist_item)
    ElMessage.success('审核动作已记录')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    reviewingCode.value = ''
  }
}

async function loadReplyCandidates() {
  const current = oaPackage.value
  const sourceDocumentId = current?.source_document?.id
  if (!current || !sourceDocumentId) {
    replyOptions.value = []
    selectedReplyKey.value = ''
    return
  }
  const documents = await getCaseDocumentsWithEvidence(current.package.case_id)
  replyOptions.value = selectReviewedReplyDocumentOptions(
    documents,
    current.package.case_id,
    sourceDocumentId,
  )
  if (!replyOptions.value.some((option) => replyKey(option) === selectedReplyKey.value)) {
    selectedReplyKey.value = ''
  }
}

async function handleLinkReplyDocument() {
  if (!oaPackage.value || !selectedReply.value) {
    ElMessage.warning('请选择当前案件已复核答复文书')
    return
  }
  linkingReply.value = true
  error.value = null
  try {
    oaPackage.value = await linkReviewedOaReplyDocument(
      oaPackage.value.package.id,
      oaPackage.value.package.case_id,
      selectedReply.value,
    )
    ElMessage.success('答复文书已关联')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    linkingReply.value = false
  }
}

async function handleExperimentToggle() {
  if (!packageId.value || !oaPackage.value) return

  experimentUpdating.value = true
  error.value = null
  try {
    oaPackage.value = await refreshOaReplyPackage(packageId.value, {
      experiment_data_submitted: !oaPackage.value.experiment_data_submitted,
    })
    ElMessage.success('实验数据标记已更新')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    experimentUpdating.value = false
  }
}

function replaceChecklistItem(nextItem: OfficialWorkPackageChecklist) {
  if (!oaPackage.value) return

  const nextChecklist = [...oaPackage.value.official_page_checklist]
  const index = nextChecklist.findIndex((item) => item.item_code === nextItem.item_code)
  if (index >= 0) {
    nextChecklist.splice(index, 1, nextItem)
  } else {
    nextChecklist.push(nextItem)
  }
  oaPackage.value = {
    ...oaPackage.value,
    official_page_checklist: nextChecklist,
  }
}

function getDocumentLabel(document?: OaReplyDocument | null): string {
  if (!document) return '未关联'
  return document.ref_no || document.title || document.id
}

function getDocumentDateText(document?: OaReplyDocument | null): string {
  if (!document) return '待关联源官文'
  return document.doc_date ? `文书日期：${document.doc_date}` : '文书日期待维护'
}

function getReplyDocumentDateText(document?: OaReplyDocument | null): string {
  if (!document) return '待关联答复文书'
  if (document.reply_date) return `内部回复日期：${document.reply_date}`
  return document.doc_date ? `文书日期：${document.doc_date}` : '内部回复日期待维护'
}

function replyKey(option: ReviewedReplyDocumentOption): string {
  return `${option.document_id}:${option.evidence_version_id}:${option.content_hash}`
}

function goBack() {
  router.back()
}

function localizeResolveError(value: unknown): ApiError {
  const apiError = value as ApiError
  if (apiError.status === 404) {
    return { ...apiError, message: '未找到对应官文，无法进入OA答复工作包。' }
  }
  if (apiError.status === 400) {
    return { ...apiError, message: '当前文书方向不支持进入OA答复工作包。' }
  }
  if (apiError.status === 409) {
    return { ...apiError, message: '当前官文状态、语义或工作包配置不允许进入OA答复工作包。' }
  }
  if (apiError.status === 422) {
    return { ...apiError, message: '官文标识格式无效，请从文书详情重新进入。' }
  }
  return { ...apiError, message: '解析OA答复工作包失败，请稍后重试。' }
}

function isDone(status?: string | null): boolean {
  return ['DONE', 'READY', 'PASS', 'PRESENT', 'ARCHIVED'].includes(String(status || '').toUpperCase())
}

function getPackageStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'PREPARING') return '准备中'
  if (normalized === 'NEEDS_MAINTENANCE') return '需维护'
  if (normalized === 'NEEDS_CONFIRMATION') return '待确认'
  if (normalized === 'READY_FOR_EXTERNAL_SUBMIT') return '可人工提交'
  if (normalized === 'SUBMITTED') return '已提交'
  if (normalized === 'WAITING_RECEIPT') return '待回执'
  if (normalized === 'ARCHIVED') return '已归档'
  if (normalized === 'EXCEPTION') return '异常'
  return status || '待核对'
}

function getReplyStatusText(status?: string | null): string {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'REPLY_DOCUMENT_LINKED') return '已关联答复文书'
  if (normalized === 'READY') return '已准备'
  if (normalized === 'PENDING') return '待处理'
  if (normalized === 'SUBMITTED') return '已提交'
  if (normalized === 'WAITING_RECEIPT') return '待回执'
  if (normalized === 'ARCHIVED') return '已归档'
  if (normalized === 'NEEDS_MAINTENANCE') return '需维护'
  return status || '待核对'
}

function getPackageStatusTagType(status?: string | null): 'success' | 'warning' | 'danger' | 'info' {
  const normalized = String(status || '').toUpperCase()
  if (normalized === 'READY_FOR_EXTERNAL_SUBMIT' || normalized === 'SUBMITTED' || normalized === 'ARCHIVED') return 'success'
  if (normalized === 'NEEDS_MAINTENANCE' || normalized === 'EXCEPTION') return 'danger'
  if (normalized === 'NEEDS_CONFIRMATION' || normalized === 'WAITING_RECEIPT' || normalized === 'PREPARING') return 'warning'
  return 'info'
}
</script>

<style scoped>
.oa-reply-page {
  display: grid;
  gap: 18px;
}

.page-subtitle {
  margin: 6px 0 0;
  color: var(--text-sub);
  font-size: 14px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  display: grid;
  gap: 6px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.summary-card span,
.summary-card small {
  color: var(--text-sub);
  font-size: 12px;
}

.summary-card strong {
  color: var(--text-main);
  font-size: 16px;
  overflow-wrap: anywhere;
}

.oa-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 18px;
  align-items: start;
}

.main-stack,
.side-stack {
  display: grid;
  gap: 16px;
}

.reply-chain-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.reply-chain-card {
  display: grid;
  gap: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.reply-chain-card span,
.reply-chain-card small {
  color: var(--text-sub);
  font-size: 12px;
}

.statement-preview {
  max-height: 240px;
  overflow: auto;
  white-space: pre-wrap;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
  color: var(--text-main);
  font-size: 13px;
  line-height: 1.7;
}

.review-actions {
  display: grid;
  gap: 8px;
}

.reply-selector {
  margin-top: 14px;
}

.review-actions .el-button {
  justify-content: flex-start;
  margin-left: 0;
  width: 100%;
}

.boundary-list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 1180px) {
  .oa-layout {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .summary-grid,
  .reply-chain-grid {
    grid-template-columns: 1fr;
  }
}
</style>
