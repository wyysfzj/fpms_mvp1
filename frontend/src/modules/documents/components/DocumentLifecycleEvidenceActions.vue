<template>
  <section class="case-panel lifecycle-evidence-actions">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">{{ grantTask ? '授权通知证据' : '生命周期证据动作' }}</h3>
        <p>仅可选择当前案件、当前版本且已复核通过的证据。</p>
      </div>
    </div>

    <el-alert
      v-if="!evidenceOptions.length"
      type="warning"
      :closable="false"
      title="未找到同案当前已复核证据"
      show-icon
    />
    <el-form v-else label-position="top">
      <el-form-item :label="isOaNoticeDocument ? '已复核证据版本' : '证据文件'">
        <el-select v-model="selectedEvidenceKey" placeholder="请选择标题、角色和文件名匹配的证据">
          <el-option
            v-for="option in evidenceOptions"
            :key="evidenceKey(option)"
            :value="evidenceKey(option)"
            :label="`${option.title}｜${option.role}｜${option.filename}`"
          />
        </el-select>
      </el-form-item>
      <div v-if="selectedEvidence" class="evidence-binding">
        <span>证据版本：{{ selectedEvidence.evidence_version_id }}</span>
        <span>内容摘要：{{ selectedEvidence.content_hash }}</span>
      </div>
      <div v-if="grantTask" class="time-grid">
        <el-form-item label="授权通知记录时间">
          <el-date-picker
            v-model="recordedAt"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="请选择授权通知记录时间"
          />
        </el-form-item>
      </div>
      <div v-else class="time-grid">
        <el-form-item label="生效时间">
          <el-date-picker
            v-model="effectiveAt"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="请选择生效时间"
          />
        </el-form-item>
        <el-form-item label="记录时间（可选）">
          <el-date-picker
            v-model="occurredAt"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="未填写时由服务端保留为空"
          />
        </el-form-item>
      </div>
      <div class="action-row">
        <el-button
          v-if="grantTask"
          :loading="runningAction === 'GRANT_NOTICE'"
          :disabled="!selectedEvidence || !recordedAt || Boolean(runningAction)"
          @click="handleGrantNotice"
        >
          确认授权通知证据
        </el-button>
        <el-button
          v-for="action in grantTask ? [] : actions"
          :key="action.code"
          :loading="runningAction === action.code"
          :disabled="!selectedEvidence || !effectiveAt || Boolean(runningAction)"
          @click="handleAction(action.code, action.label)"
        >
          {{ action.label }}
        </el-button>
      </div>
    </el-form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  isOaNoticeTemplateCode,
  recordDocumentLifecycleEvidence,
  selectReviewedEvidenceOptions,
} from '../../../api/documents'
import { recordGrantNoticeLifecycle } from '../../../api/grantFees'
import type {
  Document,
  DocumentLifecycleActionCode,
  ReviewedDocumentEvidenceOption,
} from '../../../api/documents.types'
import type { GrantFeeTaskListItem } from '../../../api/grantFees.types'
import type { ApiError } from '../../../api/types'

const props = defineProps<{
  document: Document
  grantTask?: GrantFeeTaskListItem
  templateCode?: string
}>()
const emit = defineEmits<{
  (event: 'error', error: ApiError): void
  (event: 'recorded'): void
}>()

const selectedEvidenceKey = ref('')
const effectiveAt = ref('')
const occurredAt = ref('')
const recordedAt = ref('')
const runningAction = ref<DocumentLifecycleActionCode | 'GRANT_NOTICE' | ''>('')

const baseActions: Array<{ code: DocumentLifecycleActionCode; label: string }> = [
  { code: 'ACCEPTANCE_NOTICE', label: '记录受理通知' },
  { code: 'PRELIMINARY_START', label: '开始初步审查' },
  { code: 'PRELIMINARY_PASS', label: '记录初审通过' },
  { code: 'PUBLICATION_NOTICE', label: '记录公布通知' },
  { code: 'SUBSTANTIVE_START', label: '开始实质审查' },
]
const isOaNoticeDocument = computed(() =>
  isOaNoticeTemplateCode(props.templateCode || props.document.template_code)
)
const actions = computed(() => isOaNoticeDocument.value
  ? [...baseActions, { code: 'OA_NOTICE' as const, label: '记录审查意见通知' }]
  : baseActions
)

const evidenceOptions = computed(() =>
  selectReviewedEvidenceOptions([props.document], props.document.case_id || '')
)
const selectedEvidence = computed(() =>
  evidenceOptions.value.find((option) => evidenceKey(option) === selectedEvidenceKey.value) || null
)

function evidenceKey(option: ReviewedDocumentEvidenceOption): string {
  return `${option.document_id}:${option.evidence_version_id}:${option.content_hash}`
}

async function handleAction(action: DocumentLifecycleActionCode, label: string) {
  if (!props.document.case_id || !selectedEvidence.value || !effectiveAt.value) {
    ElMessage.warning('请选择已复核证据和生效时间')
    return
  }
  runningAction.value = action
  try {
    await recordDocumentLifecycleEvidence(action, props.document.case_id, selectedEvidence.value, {
      effective_at: effectiveAt.value,
      occurred_at: occurredAt.value || null,
      idempotency_key: crypto.randomUUID(),
    })
    ElMessage.success(`${label}已记录`)
  } catch (error) {
    emit('error', error as ApiError)
  } finally {
    runningAction.value = ''
  }
}

async function handleGrantNotice() {
  if (!props.grantTask || !selectedEvidence.value || !recordedAt.value) {
    ElMessage.warning('请选择已复核授权通知证据和记录时间')
    return
  }
  runningAction.value = 'GRANT_NOTICE'
  try {
    await recordGrantNoticeLifecycle(props.grantTask, selectedEvidence.value, {
      recorded_at: recordedAt.value,
      idempotency_key: crypto.randomUUID(),
    })
    ElMessage.success('授权通知证据已记录')
    emit('recorded')
  } catch (error) {
    emit('error', error as ApiError)
  } finally {
    runningAction.value = ''
  }
}
</script>

<style scoped>
.lifecycle-evidence-actions {
  margin-top: 16px;
}

.panel-toolbar p,
.evidence-binding {
  color: var(--text-secondary);
  font-size: 13px;
}

.evidence-binding {
  display: grid;
  gap: 4px;
  margin-bottom: 14px;
  overflow-wrap: anywhere;
}

.time-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 760px) {
  .time-grid {
    grid-template-columns: 1fr;
  }
}
</style>
