<template>
  <div class="case-panel case-document-gate-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">文件材料与文书事件</h3>
        <p class="document-gate-subtitle">当前节点材料核验、文件角色和文书事件状态</p>
      </div>
      <el-button type="primary" size="small" @click="handleCreate">登记往来文件</el-button>
    </div>

    <div class="document-gate-status-strip" v-loading="gateLoading">
      <span v-for="item in gateStatusItems" :key="item.label">{{ item.label }} {{ item.value }}</span>
    </div>

    <section class="document-gate-card intake-role-card">
      <h4 class="document-gate-title">新申请收案门禁</h4>
      <el-table :data="newCaseGateRows" size="small" class="document-gate-table">
        <el-table-column prop="fileName" label="客户文件" min-width="150" />
        <el-table-column prop="requirement" label="要求" width="110">
          <template #default="{ row }">
            <el-tag :type="row.tagType" size="small">{{ row.requirement }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage" label="用途" min-width="220" />
      </el-table>
    </section>

    <div class="document-gate-grid">
      <section class="document-gate-card">
        <h4 class="document-gate-title">当前节点文件材料</h4>
        <el-skeleton v-if="gateLoading" :rows="4" animated />
        <el-alert
          v-else-if="gateError"
          type="error"
          :closable="false"
          title="材料门禁加载失败"
          :description="gateError.message"
          show-icon
        />
        <el-empty
          v-else-if="!documentGate"
          description="暂无材料门禁数据"
          :image-size="72"
        />
        <el-table v-else :data="materialRequirements" size="small" class="document-gate-table">
          <el-table-column prop="requirement" label="要求项" min-width="110" />
          <el-table-column prop="matchedFile" label="匹配文件" min-width="150" />
          <el-table-column prop="role" label="材料角色" min-width="110" />
          <el-table-column label="结论" width="120">
            <template #default="{ row }">
              <el-tag :type="row.tagType" size="small">{{ row.result }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-alert
          v-if="documentGate"
          class="document-gate-alert"
          :type="gateAlertType"
          :closable="false"
          title="门禁结论"
          :description="gateConclusionDescription"
          show-icon
        />
      </section>

      <section class="document-gate-card">
        <h4 class="document-gate-title">当前建议动作</h4>
        <el-skeleton v-if="gateLoading" :rows="3" animated />
        <el-alert
          v-else-if="gateError"
          type="error"
          :closable="false"
          title="建议动作加载失败"
          :description="gateError.message"
          show-icon
        />
        <el-empty
          v-else-if="!suggestedActions.length"
          description="暂无建议动作"
          :image-size="72"
        />
        <div v-else class="document-action-list">
          <div v-for="action in suggestedActions" :key="action.title" class="document-action-item">
            <div>
              <strong>{{ action.title }}</strong>
              <span>{{ action.description }}</span>
            </div>
            <el-button
              size="small"
              :type="action.primary ? 'primary' : undefined"
              :disabled="action.disabled"
              @click="action.primary ? handleCreate() : undefined"
            >
              {{ action.buttonText }}
            </el-button>
          </div>
        </div>
      </section>
    </div>

    <section class="document-event-section">
      <h4 class="document-gate-title">文件材料与文书事件</h4>
      <div v-if="loading" class="muted">加载中...</div>
      <div v-else-if="items.length === 0" class="placeholder-content">
        <p>暂无往来文件记录</p>
      </div>
      <el-table v-else :data="items" stripe style="width: 100%">
        <el-table-column label="方向" width="90">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'IN' ? 'success' : 'warning'" size="small">
              {{ row.direction === 'IN' ? '收文' : '发文' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column label="业务阶段" min-width="110">
          <template #default="{ row }">{{ getDocumentStage(row) }}</template>
        </el-table-column>
        <el-table-column label="文件角色" min-width="130">
          <template #default="{ row }">{{ getDocumentRole(row) }}</template>
        </el-table-column>
        <el-table-column label="官方附件" min-width="180">
          <template #default="{ row }">
            <div class="attachment-role-inline">
              <template v-if="getAttachmentOfficialSummaries(row).length">
                <el-tag
                  v-for="summary in getAttachmentOfficialSummaries(row)"
                  :key="summary"
                  size="small"
                  type="info"
                >
                  {{ summary }}
                </el-tag>
              </template>
              <span v-else class="muted">未标注</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="效果状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getFileEventTagType(row)" size="small">
              {{ getFileEventStatusText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="doc_date" label="文件日期" width="120" />
        <el-table-column prop="created_at" label="登记时间" width="160" />
      </el-table>
      <el-alert
        class="document-gate-alert"
        type="info"
        :closable="false"
        title="审计提示"
        description="本页仅展示文书事件和文件效果摘要；完整效果账本留给后续任务实现。"
        show-icon
      />
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDocuments } from '../../../api/documents'
import { getCase, getCaseDocumentGate } from '../../../api/cases'
import type {
  CaseDocumentGateCheck,
  CaseDocumentGateConclusion,
  CaseDocumentGateFileEvent,
  CaseDocumentGatePreview,
} from '../../../api/cases.types'
import type { Attachment, Document } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'

const props = defineProps<{
  caseId: string
}>()

const router = useRouter()
const items = ref<Document[]>([])
const loading = ref(true)
const caseNo = ref('')
const documentGate = ref<CaseDocumentGatePreview | null>(null)
const gateLoading = ref(true)
const gateError = ref<ApiError | null>(null)

const gateStatusItems = computed(() => [
  { label: '已匹配材料', value: documentGate.value ? `${documentGate.value.material_count}` : '-' },
  { label: '缺失材料', value: documentGate.value ? `${documentGate.value.missing_items.length}` : '-' },
  { label: '硬性阻止', value: documentGate.value ? (documentGate.value.hard_block ? '是' : '否') : '-' },
  { label: '后补审计', value: documentGate.value ? (documentGate.value.afterfill_audit_required ? '需要' : '不需要') : '-' },
])

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
  RECEIPT_PDF: '回执',
  MERGED_PDF: '合并PDF',
}

const newCaseGateRows = [
  {
    fileName: '技术交底书',
    requirement: '必传',
    tagType: 'danger',
    usage: '作为新申请内容准备和后续官方递交文件生成的稳定来源。',
  },
  {
    fileName: '委托指示（如有）',
    requirement: '条件项',
    tagType: 'warning',
    usage: '客户提供时必须入库；未提供时不阻止建案。',
  },
]

const materialRequirements = computed(() =>
  (documentGate.value?.checks || []).map((check) => ({
    requirement: check.requirement_name,
    matchedFile: matchedDocumentText(check),
    role: check.role,
    result: checkStatusText(check),
    tagType: checkStatusTagType(check),
  }))
)

const suggestedActions = computed(() =>
  (documentGate.value?.suggested_actions || []).map((title, index) => ({
    title,
    description: '来自当前材料门禁的后续处理建议。',
    buttonText: index === 0 ? '登记往来文件' : '待后续处理',
    primary: index === 0,
    disabled: index !== 0,
  }))
)

const gateAlertType = computed(() =>
  documentGate.value ? gateConclusionAlertType(documentGate.value.conclusion) : 'info'
)
const gateConclusionDescription = computed(() => {
  if (!documentGate.value) return '暂无门禁结论。'
  const actions = documentGate.value.suggested_actions.length
    ? `；${documentGate.value.suggested_actions.join('；')}`
    : ''
  return `${gateConclusionText(documentGate.value.conclusion)}${actions}`
})

const fileEventByDocumentId = computed(() => {
  const events = new Map<string, CaseDocumentGateFileEvent>()
  for (const event of documentGate.value?.file_events || []) {
    events.set(event.document_id, event)
  }
  return events
})

const roleByDocumentId = computed(() => {
  const roles = new Map<string, string[]>()
  for (const check of documentGate.value?.checks || []) {
    for (const document of check.matched_documents) {
      const current = roles.get(document.id) || []
      if (!current.includes(check.role)) {
        current.push(check.role)
      }
      roles.set(document.id, current)
    }
  }
  return roles
})

function gateConclusionText(conclusion: CaseDocumentGateConclusion) {
  if (conclusion === 'PASS') return '通过'
  if (conclusion === 'WARNING') return '需后补'
  if (conclusion === 'BLOCKED') return '阻止'
  return conclusion
}

function gateConclusionAlertType(conclusion: CaseDocumentGateConclusion): 'success' | 'warning' | 'error' | 'info' {
  if (conclusion === 'PASS') return 'success'
  if (conclusion === 'WARNING') return 'warning'
  if (conclusion === 'BLOCKED') return 'error'
  return 'info'
}

function matchedDocumentText(check: CaseDocumentGateCheck) {
  const titles = check.matched_documents
    .map((document) => document.title || document.template_code || document.id)
    .filter(Boolean)
  return titles.length ? titles.join('，') : '未匹配'
}

function checkStatusText(check: CaseDocumentGateCheck) {
  if (check.status === 'MATCHED') return '已满足'
  if (check.afterfill_allowed) return '允许后补'
  if (check.blocks_submission) return '缺失阻止'
  return '未匹配'
}

function checkStatusTagType(check: CaseDocumentGateCheck): 'success' | 'warning' | 'danger' | 'info' {
  if (check.status === 'MATCHED') return 'success'
  if (check.afterfill_allowed) return 'warning'
  if (check.blocks_submission) return 'danger'
  return 'info'
}

function eventStatusText(status?: string) {
  if (status === 'REPLY_FILE') return '答复文件'
  if (status === 'REPLIED') return '已答复'
  if (status === 'NEED_REPLY') return '需答复'
  if (status === 'MAILED') return '已邮寄'
  if (status === 'REGISTERED') return '已登记'
  return '未核验'
}

function eventStatusTagType(status?: string): 'success' | 'warning' | 'info' {
  if (status === 'NEED_REPLY') return 'warning'
  if (status === 'REGISTERED' || status === 'REPLIED' || status === 'REPLY_FILE' || status === 'MAILED') {
    return 'success'
  }
  return 'info'
}

function getDocumentStage(row: Document) {
  const event = fileEventByDocumentId.value.get(row.id)
  if (event?.event_status === 'NEED_REPLY') return '答复节点'
  if (event?.event_status === 'REPLY_FILE') return '答复文件'
  if (event?.event_status === 'MAILED') return '发文邮寄'
  return row.direction === 'IN' ? '收文登记' : '文书流转'
}

function getDocumentRole(row: Document) {
  const roles = roleByDocumentId.value.get(row.id)
  if (roles?.length) return roles.join('、')
  return row.direction === 'IN' ? '往来收文' : '对外文书'
}

function normalizeCode(value?: string | null): string {
  return String(value || '').trim().toUpperCase()
}

function getOfficialRoleText(role?: string | null): string {
  const normalized = normalizeCode(role)
  if (!normalized) return ''
  return OFFICIAL_ROLE_TEXT[normalized] || normalized
}

function getAttachmentOfficialSummary(attachment: Attachment): string {
  const roleText = getOfficialRoleText(attachment.official_file_role)
  if (roleText) return roleText
  if (attachment.source_role_alias) return `历史别名：${attachment.source_role_alias}`
  if (attachment.is_receipt_evidence) return '回执证据'
  if (attachment.is_archive_evidence) return '归档证据'
  return ''
}

function getAttachmentOfficialSummaries(row: Document): string[] {
  return (row.attachments || [])
    .map((attachment) => getAttachmentOfficialSummary(attachment))
    .filter((summary): summary is string => Boolean(summary))
}

function getFileEventStatusText(row: Document) {
  return eventStatusText(fileEventByDocumentId.value.get(row.id)?.event_status)
}

function getFileEventTagType(row: Document) {
  return eventStatusTagType(fileEventByDocumentId.value.get(row.id)?.event_status)
}

async function resolveCaseNo() {
  if (caseNo.value) return caseNo.value

  try {
    const caseData = await getCase(props.caseId)
    caseNo.value = caseData.case_no
  } catch {
    // Keep existing flow if case metadata fetch fails.
  }

  return caseNo.value
}

async function fetchDocumentGate() {
  gateLoading.value = true
  gateError.value = null
  try {
    documentGate.value = await getCaseDocumentGate(props.caseId)
  } catch (err) {
    documentGate.value = null
    gateError.value = err as ApiError
  } finally {
    gateLoading.value = false
  }
}

onMounted(async () => {
  void resolveCaseNo()
  void fetchDocumentGate()

  try {
    const res = await getDocuments({ case_id: props.caseId, page: 1, page_size: 50 })
    items.value = res.items
  } catch {
    // silently fail
  } finally {
    loading.value = false
  }
})

async function handleCreate() {
  const resolvedCaseNo = await resolveCaseNo()
  const query: Record<string, string> = { case_id: props.caseId }

  if (resolvedCaseNo) {
    query.case_no = resolvedCaseNo
  }

  router.push({
    path: '/documents/new',
    query,
  })
}
</script>

<style scoped>
.case-document-gate-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.document-gate-subtitle {
  margin: -8px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.document-gate-status-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.document-gate-status-strip span {
  border: 1px solid #d8e1ee;
  border-radius: 4px;
  background: #f8fafc;
  color: var(--text-main);
  font-size: 12px;
  font-weight: 600;
  padding: 6px 10px;
}

.document-gate-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(280px, 0.75fr);
  gap: 16px;
}

.document-gate-card,
.document-event-section {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 16px;
}

.intake-role-card {
  background: #fbfdff;
}

.document-gate-title {
  margin: 0 0 12px;
  color: var(--text-main);
  font-size: 15px;
  font-weight: 600;
}

.document-gate-table {
  width: 100%;
}

.document-gate-alert {
  margin-top: 14px;
}

.document-action-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.document-action-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid #edf2f7;
  border-radius: 6px;
  padding: 12px;
}

.document-action-item div {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.document-action-item strong {
  color: var(--text-main);
  font-size: 14px;
}

.document-action-item span {
  color: var(--text-sub);
  font-size: 12px;
  line-height: 1.5;
}

.document-action-item .el-button {
  flex: 0 0 auto;
}

.attachment-role-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

@media (max-width: 1100px) {
  .document-gate-grid {
    grid-template-columns: 1fr;
  }

  .document-action-item {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
