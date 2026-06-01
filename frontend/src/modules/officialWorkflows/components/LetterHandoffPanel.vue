<template>
  <section class="case-panel letter-handoff-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">格式函与龙虾交接</h3>
        <p class="handoff-subtitle">核对联系人、称谓、正文、Word路径和附件清单，生成交接记录供外部邮件流程使用。</p>
      </div>
      <div class="panel-actions">
        <el-tag :type="handoffStatusTagType" size="small">{{ handoffStatusText }}</el-tag>
        <el-button size="small" :disabled="!documentId" :loading="loading" @click="fetchPreview">刷新预览</el-button>
      </div>
    </div>

    <el-alert
      v-if="!documentId"
      type="info"
      :closable="false"
      title="请选择单份去文"
      description="请从文书详情进入，或在邮寄登记页勾选一份去文后查看信函交接预览。"
      show-icon
    />

    <div v-else-if="error" class="inline-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div v-else-if="loading" class="panel-loading">
      <el-skeleton :rows="6" animated />
    </div>

    <template v-else-if="preview">
      <div class="summary-grid">
        <div class="summary-card">
          <span>案件</span>
          <strong>{{ preview.case_no || preview.case_id }}</strong>
        </div>
        <div class="summary-card">
          <span>模板状态</span>
          <strong>{{ getTemplateStatusText(preview.template_status) }}</strong>
        </div>
        <div class="summary-card">
          <span>联系人来源</span>
          <strong>{{ getSourceText(preview.contact_selection_source) }}</strong>
        </div>
        <div class="summary-card">
          <span>称谓来源</span>
          <strong>{{ getSourceText(preview.salutation_source) }}</strong>
        </div>
      </div>

      <section class="handoff-section">
        <h4 class="subsection-title">模板映射</h4>
        <div class="mapping-grid">
          <div>
            <span>格式函模板</span>
            <strong>{{ preview.mapping?.format_letter_template_code || preview.mapping?.format_letter_template_id || '待配置' }}</strong>
          </div>
          <div>
            <span>输出命名规则</span>
            <strong>{{ preview.mapping?.output_name_rule || '待确认' }}</strong>
          </div>
          <div>
            <span>联系人规则</span>
            <strong>{{ preview.mapping?.contact_rule_code || '待确认' }}</strong>
          </div>
          <div>
            <span>称谓规则</span>
            <strong>{{ preview.mapping?.salutation_rule_code || '尊敬的：您好' }}</strong>
          </div>
        </div>
      </section>

      <section class="handoff-section">
        <h4 class="subsection-title">联系人与称谓</h4>
        <div class="contact-grid">
          <div>
            <span>联系人</span>
            <strong>{{ preview.contact?.contact_name || '未确认联系人' }}</strong>
          </div>
          <div>
            <span>邮箱</span>
            <strong>{{ preview.contact?.email || '待确认' }}</strong>
          </div>
          <div>
            <span>称谓</span>
            <strong>{{ displaySalutation }}</strong>
          </div>
        </div>
      </section>

      <section class="handoff-section">
        <h4 class="subsection-title">邮件主题</h4>
        <div class="text-preview">{{ preview.mail_subject || '待生成' }}</div>
      </section>

      <section class="handoff-section">
        <h4 class="subsection-title">邮件正文</h4>
        <div class="text-preview body-preview">{{ preview.mail_body_draft || displaySalutation }}</div>
      </section>

      <section class="handoff-section">
        <h4 class="subsection-title">Word路径</h4>
        <div class="text-preview">{{ preview.generated_word_path || '待生成格式函 Word' }}</div>
      </section>

      <section class="handoff-section">
        <h4 class="subsection-title">附件清单</h4>
        <el-table :data="preview.attachments" size="small" class="attachment-table">
          <el-table-column prop="file_name" label="附件" min-width="180" />
          <el-table-column label="角色" min-width="140">
            <template #default="{ row }">{{ getAttachmentRoleText(row.attachment_role) }}</template>
          </el-table-column>
          <el-table-column label="要求" width="90">
            <template #default="{ row }">
              <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                {{ row.required ? '必需' : '可选' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="row.included ? 'success' : 'warning'" size="small">
                {{ row.included ? '已纳入' : '待补齐' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="路径" min-width="190">
            <template #default="{ row }">{{ row.file_path || row.attachment_id || '待确认' }}</template>
          </el-table-column>
        </el-table>
      </section>

      <section class="handoff-section">
        <h4 class="subsection-title">龙虾交接状态</h4>
        <div class="handoff-actions">
          <el-input
            v-model="handoffRemark"
            type="textarea"
            :rows="2"
            placeholder="记录本次交接说明"
          />
          <el-button
            type="primary"
            :loading="creating"
            @click="handleCreateHandoff"
          >
            生成交接记录
          </el-button>
        </div>

        <div v-if="handoff" class="handoff-status-form">
          <el-select v-model="statusForm.longxia_handoff_status" placeholder="请选择交接状态">
            <el-option label="待交接" value="PENDING" />
            <el-option label="已交接" value="HANDED_OFF" />
            <el-option label="需复核" value="NEEDS_REVIEW" />
          </el-select>
          <el-date-picker
            v-model="statusForm.handoff_at"
            type="datetime"
            value-format="YYYY-MM-DDTHH:mm:ss"
            placeholder="交接时间"
          />
          <el-input
            v-model="statusForm.longxia_handoff_payload"
            placeholder="交接载荷或外部编号"
          />
          <el-button :loading="updatingStatus" @click="handleUpdateStatus">
            更新交接状态
          </el-button>
        </div>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  createLetterHandoff,
  getLetterHandoffPreview,
  updateLetterHandoffStatus,
} from '../../../api/officialWorkflows'
import type {
  LetterHandoff,
  LetterHandoffPreview,
} from '../../../api/officialWorkflows.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const props = withDefaults(defineProps<{
  documentId?: string
}>(), {
  documentId: '',
})

const preview = ref<LetterHandoffPreview | null>(null)
const handoff = ref<LetterHandoff | null>(null)
const loading = ref(false)
const creating = ref(false)
const updatingStatus = ref(false)
const error = ref<ApiError | null>(null)
const handoffRemark = ref('')
const statusForm = reactive({
  longxia_handoff_status: 'PENDING',
  longxia_handoff_payload: '',
  handoff_at: '',
})

const documentId = computed(() => String(props.documentId || '').trim())

const displaySalutation = computed(() => {
  const value = preview.value?.salutation_text?.trim()
  return value || '尊敬的：您好'
})

const handoffStatusText = computed(() => {
  if (handoff.value) return getHandoffStatusText(handoff.value.longxia_handoff_status)
  if (preview.value) return '待生成记录'
  return '待读取'
})

const handoffStatusTagType = computed((): 'success' | 'warning' | 'danger' | 'info' => {
  const normalized = String(handoff.value?.longxia_handoff_status || '').toUpperCase()
  if (normalized === 'HANDED_OFF') return 'success'
  if (normalized === 'NEEDS_REVIEW') return 'warning'
  if (normalized === 'FAILED') return 'danger'
  return 'info'
})

watch(documentId, () => {
  void fetchPreview()
})

onMounted(() => {
  void fetchPreview()
})

async function fetchPreview() {
  if (!documentId.value) {
    preview.value = null
    handoff.value = null
    return
  }

  loading.value = true
  error.value = null
  try {
    preview.value = await getLetterHandoffPreview(documentId.value)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function handleCreateHandoff() {
  if (!documentId.value) return

  creating.value = true
  error.value = null
  try {
    const result = await createLetterHandoff(documentId.value, {
      remark: handoffRemark.value.trim() || null,
    })
    if (result.preview) {
      preview.value = result.preview
    }
    handoff.value = result.handoff
    statusForm.longxia_handoff_status = result.handoff.longxia_handoff_status || 'PENDING'
    statusForm.longxia_handoff_payload = result.handoff.longxia_handoff_payload || ''
    statusForm.handoff_at = result.handoff.handoff_at || ''
    ElMessage.success('交接记录已生成')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    creating.value = false
  }
}

async function handleUpdateStatus() {
  if (!documentId.value || !handoff.value) return

  updatingStatus.value = true
  error.value = null
  try {
    const result = await updateLetterHandoffStatus(documentId.value, handoff.value.id, {
      longxia_handoff_status: statusForm.longxia_handoff_status,
      longxia_handoff_payload: statusForm.longxia_handoff_payload || null,
      handoff_at: statusForm.handoff_at || null,
    })
    if (result.preview) {
      preview.value = result.preview
    }
    handoff.value = result.handoff
    ElMessage.success('交接状态已更新')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    updatingStatus.value = false
  }
}

function getTemplateStatusText(value?: string | null): string {
  const normalized = String(value || '').toUpperCase()
  if (normalized === 'READY') return '已配置'
  if (normalized === 'MISSING') return '缺失'
  if (normalized === 'PENDING') return '待确认'
  return value || '待确认'
}

function getSourceText(value?: string | null): string {
  const normalized = String(value || '').toUpperCase()
  if (normalized === 'PRIMARY_CONTACT') return '主联系人'
  if (normalized === 'MAPPING_RULE') return '映射规则'
  if (normalized === 'DEFAULT') return '默认规则'
  if (normalized === 'MANUAL') return '手工确认'
  return value || '待确认'
}

function getAttachmentRoleText(value?: string | null): string {
  const normalized = String(value || '').toUpperCase()
  if (normalized === 'FORMAT_LETTER_WORD') return '格式函 Word'
  if (normalized === 'SOURCE_DOCUMENT') return '源文书'
  if (normalized === 'OFFICIAL_RECEIPT') return '官方回执'
  if (normalized === 'CLIENT_ATTACHMENT') return '客户附件'
  return value || '未标注'
}

function getHandoffStatusText(value?: string | null): string {
  const normalized = String(value || '').toUpperCase()
  if (normalized === 'PENDING') return '待交接'
  if (normalized === 'HANDED_OFF') return '已交接'
  if (normalized === 'NEEDS_REVIEW') return '需复核'
  if (normalized === 'FAILED') return '失败'
  return value || '待生成记录'
}
</script>

<style scoped>
.letter-handoff-panel {
  display: grid;
  gap: 16px;
}

.handoff-subtitle {
  margin: -6px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.panel-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.inline-error,
.panel-loading {
  min-height: 80px;
}

.summary-grid,
.mapping-grid,
.contact-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.contact-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.summary-card,
.mapping-grid > div,
.contact-grid > div {
  display: grid;
  gap: 6px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.summary-card span,
.mapping-grid span,
.contact-grid span {
  color: var(--text-sub);
  font-size: 12px;
}

.summary-card strong,
.mapping-grid strong,
.contact-grid strong {
  color: var(--text-main);
  font-size: 14px;
  overflow-wrap: anywhere;
}

.handoff-section {
  display: grid;
  gap: 10px;
}

.subsection-title {
  margin: 2px 0 0;
  color: var(--text-main);
  font-size: 15px;
}

.text-preview {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
  color: var(--text-main);
  font-size: 13px;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.body-preview {
  max-height: 180px;
  overflow: auto;
}

.attachment-table {
  width: 100%;
}

.handoff-actions,
.handoff-status-form {
  display: grid;
  gap: 10px;
}

.handoff-status-form {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  align-items: start;
}

.handoff-status-form :deep(.el-select),
.handoff-status-form :deep(.el-date-editor) {
  width: 100%;
}

@media (max-width: 1180px) {
  .summary-grid,
  .mapping-grid,
  .contact-grid,
  .handoff-status-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .summary-grid,
  .mapping-grid,
  .contact-grid,
  .handoff-status-form {
    grid-template-columns: 1fr;
  }
}
</style>
