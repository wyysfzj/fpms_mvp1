<template>
  <section class="case-panel lifecycle-evidence-actions">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">生命周期证据动作</h3>
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
      <el-form-item label="证据文件">
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
      <div class="time-grid">
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
          v-for="action in actions"
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
  recordDocumentLifecycleEvidence,
  selectReviewedEvidenceOptions,
} from '../../../api/documents'
import type {
  Document,
  DocumentLifecycleActionCode,
  ReviewedDocumentEvidenceOption,
} from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'

const props = defineProps<{ document: Document }>()
const emit = defineEmits<{ (event: 'error', error: ApiError): void }>()

const selectedEvidenceKey = ref('')
const effectiveAt = ref('')
const occurredAt = ref('')
const runningAction = ref<DocumentLifecycleActionCode | ''>('')

const actions: Array<{ code: DocumentLifecycleActionCode; label: string }> = [
  { code: 'ACCEPTANCE_NOTICE', label: '记录受理通知' },
  { code: 'PRELIMINARY_START', label: '开始初步审查' },
  { code: 'PRELIMINARY_PASS', label: '记录初审通过' },
  { code: 'PUBLICATION_NOTICE', label: '记录公布通知' },
  { code: 'SUBSTANTIVE_START', label: '开始实质审查' },
]

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
