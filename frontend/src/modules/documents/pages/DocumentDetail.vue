<template>
  <div class="page-container focus-reading-page document-detail-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> {{ ZH.common.back }}
        </el-button>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="handleEdit">
          {{ ZH.docDetail.editDoc }}
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Content -->
    <template v-else-if="doc">
      <!-- Relation Chain -->
      <RelationChainCard
        :case-ref="doc.case_id ? { id: doc.case_id, no: doc.case_no } : undefined"
        :document="{ id: doc.id, refNo: doc.ref_no || undefined, title: doc.title }"
      />

      <!-- Document Header Card -->
      <div class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <span class="case-tag" :class="directionClass">{{ getDocumentDirectionText(doc.direction) }}</span>
            <span class="meta-divider">|</span>
            <span v-if="doc.doc_date">{{ doc.doc_date }}</span>
            <template v-if="doc.case_no">
              <span class="meta-divider">|</span>
              <span class="case-no">{{ doc.case_no }}</span>
            </template>
            <template v-if="doc.doc_type">
              <span class="meta-divider">|</span>
              <span>{{ getDocumentDocTypeText(doc.doc_type) }}</span>
            </template>
          </div>
          <div class="case-title">
            <h1>{{ doc.title }}</h1>
          </div>
        </div>
      </div>

      <!-- Content Grid -->
      <div class="case-content-grid">
        <!-- Main Panel -->
        <div class="case-main-panel focus-reading-main">
          <div class="case-panel">
            <h3 class="panel-heading">{{ ZH.docDetail.docContent }}</h3>
            <div class="doc-content focus-reading-body" v-if="doc.description">
              <p class="doc-p">{{ doc.description }}</p>
            </div>
            <div v-else class="placeholder-content focus-reading-body">
              <span class="placeholder-icon">📄</span>
              <p>{{ ZH.docDetail.noContent }}</p>
            </div>
          </div>
          <GrantEvidenceReviewPanel :document-id="doc.id" />
          <DocumentLifecycleEvidenceActions :document="doc" @error="error = $event" />
          <LetterHandoffPanel
            v-if="showLetterHandoffAction"
            class="letter-handoff-section"
            :document-id="doc.id"
            :direction="doc.direction"
          />
        </div>

        <!-- Side Panel -->
        <div class="case-side-panel focus-reading-aside">
          <div class="case-panel side-widget">
            <div class="widget-title">{{ ZH.docDetail.docInfo }}</div>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">文档</span>
                <span class="info-value case-no">{{ formatDocumentDisplay(doc) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">{{ ZH.docDetail.direction }}</span>
                <span class="info-value">{{ getDocumentDirectionText(doc.direction) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">文件类型</span>
                <span class="info-value">{{ getDocumentDocTypeText(doc.doc_type) }}</span>
              </div>
              <div v-if="doc.ref_no" class="info-item">
                <span class="info-label">文号</span>
                <span class="info-value">{{ doc.ref_no }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">{{ ZH.docDetail.created }}</span>
                <span class="info-value">{{ formatDate(doc.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">{{ ZH.docDetail.updated }}</span>
                <span class="info-value">{{ formatDate(doc.updated_at) }}</span>
              </div>
              <div v-if="doc.need_reply != null" class="info-item">
                <span class="info-label">需回复</span>
                <span class="info-value">
                  <el-tag v-if="doc.need_reply && !doc.reply_date" type="warning" size="small">待回复</el-tag>
                  <el-tag v-else-if="doc.need_reply && doc.reply_date" type="success" size="small">已于 {{ doc.reply_date }} 回复</el-tag>
                  <span v-else>否</span>
                </span>
              </div>
              <div v-if="doc.reply_to_id" class="info-item">
                <span class="info-label">回复来源</span>
                <span class="info-value">
                  <router-link :to="`/documents/${doc.reply_to_id}`" class="reply-link">
                    查看原文档 →
                  </router-link>
                </span>
              </div>
              <div v-if="templateHints.length" class="info-item info-item-full">
                <span class="info-label">模板规则</span>
                <div class="info-value template-rule-list">
                  <el-tag
                    v-for="hint in templateHints"
                    :key="hint"
                    size="small"
                    class="template-rule-tag"
                  >
                    {{ hint }}
                  </el-tag>
                </div>
              </div>
              <div v-if="attachmentOfficialSummaries.length" class="info-item info-item-full">
                <span class="info-label">附件官方角色</span>
                <div class="info-value template-rule-list">
                  <el-tag
                    v-for="summary in attachmentOfficialSummaries"
                    :key="summary"
                    size="small"
                    class="template-rule-tag"
                  >
                    {{ summary }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>

          <div class="case-panel side-widget">
            <div class="widget-title">{{ ZH.docDetail.quickActions }}</div>
            <div class="quick-actions">
              <el-button size="small" @click="handleEdit">{{ ZH.docDetail.editDoc }}</el-button>
              <router-link v-if="showOaReplyAction" :to="oaReplyPackageRoute">
                <el-button size="small">OA答复工作包</el-button>
              </router-link>
              <el-button v-if="showLetterHandoffAction" size="small" @click="scrollToLetterHandoff">
                信函交接
              </el-button>
            </div>
          </div>

          <!-- Attachments -->
          <div class="case-panel side-widget">
            <AttachmentList :document-id="doc.id" />
          </div>
        </div>
      </div>
    </template>

    <!-- Empty State (document not found) -->
    <div v-else-if="!loading && !error" class="page-empty">
      <div class="empty-state">
        <span class="empty-icon">📄</span>
        <h3 class="empty-title">{{ ZH.docDetail.notFound }}</h3>
        <p class="empty-message">{{ ZH.docDetail.notFoundMsg }}</p>
        <el-button type="primary" @click="goBack">{{ ZH.common.back }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDocument, getDocTemplate } from '../../../api/documents'
import type { Attachment, DocTemplate, Document } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import AttachmentList from '../components/AttachmentList.vue'
import DocumentLifecycleEvidenceActions from '../components/DocumentLifecycleEvidenceActions.vue'
import GrantEvidenceReviewPanel from '../components/GrantEvidenceReviewPanel.vue'
import RelationChainCard from '../../../components/relations/RelationChainCard.vue'
import LetterHandoffPanel from '../../officialWorkflows/components/LetterHandoffPanel.vue'
import { usePageContext } from '../../../stores/pageContext'
import { ZH } from '../../../constants/labels.zh'
import {
  getCaseStatusText,
  getDocumentDirectionText,
  getDocumentDocTypeText,
  getFeeDraftTypeText,
} from '../../../constants/displayText'

const route = useRoute()
const router = useRouter()
const pageContext = usePageContext()

const doc = ref<Document | null>(null)
const docTemplate = ref<DocTemplate | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)

const directionClass = computed(() => {
  return doc.value?.direction === 'IN' ? 'direction-in' : 'direction-out'
})
const templateHints = computed(() => {
  if (!docTemplate.value) return []
  const hints: string[] = []
  if (docTemplate.value.need_reply) hints.push('需要回复')
  if (docTemplate.value.deadline_template_code) {
    hints.push(`自动建期限：${docTemplate.value.deadline_template_code}`)
  }
  if (docTemplate.value.fee_draft_type) {
    hints.push(`自动建费用草稿：${getFeeDraftTypeText(docTemplate.value.fee_draft_type)}`)
  }
  if (docTemplate.value.status_effect) {
    hints.push(`状态变更：${getCaseStatusText(docTemplate.value.status_effect)}`)
  }
  if (docTemplate.value.reply_to_template_code) {
    hints.push(`回复模板：${docTemplate.value.reply_to_template_code}`)
  }
  return hints
})
const attachmentOfficialSummaries = computed(() => {
  const attachments = doc.value?.attachments || []
  return attachments
    .map((attachment) => getAttachmentOfficialSummary(attachment))
    .filter((summary): summary is string => Boolean(summary))
})
const showOaReplyAction = computed(() => {
  const current = doc.value
  if (!current) return false

  const templateCode = normalizeCode(current.template_code || docTemplate.value?.code)
  return Boolean(
    current.need_reply
    || current.reply_to_id
    || current.doc_type === 'OFFICIAL_IN'
    || templateCode.includes('OA')
    || templateCode.includes('REPLY')
  )
})
const oaReplyPackageRoute = computed(() => ({
  path: '/official-workflows/oa-reply',
  query: {
    document_id: doc.value?.id || '',
  },
}))
const showLetterHandoffAction = computed(() => ['IN', 'OUT'].includes(normalizeCode(doc.value?.direction)))

const OFFICIAL_ROLE_TEXT: Record<string, string> = {
  TECHNICAL_DISCLOSURE: '技术交底书',
  COMMISSION_INSTRUCTION: '委托指示',
  FILING_DOCUMENT: '递交文件',
  FILING_XML_ZIP: 'XML压缩包',
  FILING_MERGED_PDF: '合并PDF',
  FILING_CLAIMS: '权利要求书',
  OA_STATEMENT_WORD: 'OA意见陈述 Word',
  OA_STATEMENT_PDF: 'OA意见陈述 PDF',
  OA_MODIFIED_CLAIMS: 'OA修改后权利要求书',
  OA_AMENDMENT_COMPARISON: 'OA修改对照页',
  OA_OTHER_PROOF: 'OA其他证明文件',
  OA_ADDITIONAL_FILE: 'OA附加文件',
  SOURCE_DOCUMENT: '来源文书',
  SOURCE_OFFICIAL_DOCUMENT: '来源官文',
  ELECTRONIC_RECEIPT: '电子申请回执',
  OFFICIAL_NOTICE_PDF: '官方通知书PDF',
  RECEIPT_PDF: '回执',
  MERGED_PDF: '合并PDF',
}

async function fetchDocument() {
  const id = String(route.params.id || '').trim()
  if (!id) {
    return
  }

  loading.value = true
  error.value = null

  try {
    doc.value = await getDocument(id)
    docTemplate.value = doc.value.doc_template_id
      ? await getDocTemplate(doc.value.doc_template_id)
      : null
    pageContext.setBreadcrumb([
      '案件管理',
      '文档详情',
      doc.value.doc_type ? getDocumentDocTypeText(doc.value.doc_type) : formatDocumentDisplay(doc.value),
    ])
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

function formatDocumentDisplay(value: Document): string {
  return value.ref_no || value.title || '未命名往来文件'
}

function normalizeCode(value?: string | null): string {
  return String(value || '').trim().toUpperCase()
}

function getOfficialRoleText(role?: string | null): string {
  const normalized = normalizeCode(role)
  if (!normalized) return ''
  return OFFICIAL_ROLE_TEXT[normalized] || '官方文件角色待确认'
}

function getAttachmentOfficialSummary(attachment: Attachment): string {
  const roleText = getOfficialRoleText(attachment.official_file_role)
  if (roleText) return roleText
  if (attachment.source_role_alias) return `历史别名：${attachment.source_role_alias}`
  if (attachment.is_receipt_evidence) return '回执证据'
  if (attachment.is_archive_evidence) return '归档证据'
  return ''
}

function goBack() {
  router.push('/documents')
}

function handleEdit() {
  const id = route.params.id
  router.push(`/documents/${id}/edit`)
}

function scrollToLetterHandoff() {
  document.querySelector('.letter-handoff-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(() => {
  fetchDocument()
})

onBeforeUnmount(() => {
  pageContext.clear()
})
</script>

<style scoped>
.direction-in {
  background: #DBEAFE;
  color: #1D4ED8;
}

.direction-out {
  background: #D1FAE5;
  color: #047857;
}

.doc-content {
  font-family: var(--font-read);
  line-height: 1.8;
  font-size: 15px;
  color: var(--text-main);
}

.doc-p {
  margin-bottom: 20px;
  text-align: justify;
  white-space: pre-wrap;
}

.reply-link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: 13px;
}

.reply-link:hover {
  text-decoration: underline;
}

.info-item-full {
  grid-column: 1 / -1;
}

.template-rule-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-rule-tag {
  margin-right: 0;
}

.letter-handoff-section {
  margin-top: 16px;
}
</style>
