<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">授权费任务看板</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-space wrap>
          <el-button
            type="success"
            :loading="batchNoticeLoading"
            :disabled="!selectedTaskIds.length || batchActionLoading !== null || batchNoticeLoading"
            @click="handleBatchNoticeGeneration"
          >
            批量生成通知函
          </el-button>
          <el-button
            type="primary"
            :loading="batchActionLoading === 'record_pay_instruction'"
            :disabled="!selectedTaskIds.length || batchActionLoading !== null || batchNoticeLoading"
            @click="handleBatchInstruction('record_pay_instruction')"
          >
            批量标记支付
          </el-button>
          <el-button
            type="warning"
            :loading="batchActionLoading === 'record_abandon_instruction'"
            :disabled="!selectedTaskIds.length || batchActionLoading !== null || batchNoticeLoading"
            @click="handleBatchInstruction('record_abandon_instruction')"
          >
            批量标记放弃
          </el-button>
          <el-button disabled>账单联动（后续）</el-button>
        </el-space>
      </div>
    </div>

    <el-alert
      class="page-note"
      title="当前页面支持查看、筛选、批量客户指示、批量生成通知函、单行生成草单和草单后完成。生成通知函会创建真实文书并回写内部通知状态。"
      type="info"
      show-icon
      :closable="false"
    />

    <el-form class="filter-form" :inline="true">
      <el-form-item label="状态">
        <el-select v-model="filters.status" class="filter-select" clearable placeholder="全部状态">
          <el-option label="全部" value="" />
          <el-option label="待处理" value="OPEN" />
          <el-option label="等待客户" value="WAITING_CLIENT" />
          <el-option label="可生成草单" value="READY_TO_DRAFT" />
          <el-option label="已生成草单" value="DRAFT_GENERATED" />
          <el-option label="已完成" value="DONE" />
        </el-select>
      </el-form-item>
      <el-form-item label="客户指示">
        <el-select
          v-model="filters.client_instruction"
          class="filter-select"
          clearable
          placeholder="全部客户指示"
        >
          <el-option label="全部" value="" />
          <el-option label="未指示" value="NONE" />
          <el-option label="支付" value="PAY" />
          <el-option label="放弃" value="ABANDON" />
        </el-select>
      </el-form-item>
      <el-form-item label="已生成草单">
        <el-select v-model="draftGeneratedText" class="filter-select" clearable placeholder="全部">
          <el-option label="全部" value="" />
          <el-option label="是" value="true" />
          <el-option label="否" value="false" />
        </el-select>
      </el-form-item>
      <el-form-item label="是否逾期">
        <el-select v-model="overdueText" class="filter-select" clearable placeholder="全部">
          <el-option label="全部" value="" />
          <el-option label="是" value="true" />
          <el-option label="否" value="false" />
        </el-select>
      </el-form-item>
      <el-form-item label="案件编号">
        <el-input
          v-model="filters.case_no"
          class="filter-input"
          clearable
          placeholder="请输入案件编号"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="到期日期">
        <el-date-picker
          v-model="filters.date_range"
          class="filter-range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          clearable
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="applyFilters">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <div class="page-summary">
      <div class="summary-card">
        <span class="summary-label">当前页</span>
        <span class="summary-value">{{ tasks.length }} 条</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">总记录</span>
        <span class="summary-value">{{ total }} 条</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">页面说明</span>
        <span class="summary-value summary-note">查看、筛选、批量指示、批量通知、单行生成</span>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState title="暂无授权费任务" message="请调整筛选条件后重试。" icon="📄" />
    </div>

    <div v-else class="page-table">
      <el-table
        :data="tasks"
        aria-label="授权费任务列表"
        stripe
        size="small"
        class="compact-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="48" :selectable="isOrdinaryMutationSelectable" />
        <el-table-column label="案件" min-width="180">
          <template #default="{ row }">
            <router-link v-if="row.case_no" :to="{ name: 'case_detail_by_no', params: { caseNo: row.case_no } }" class="case-link">
              {{ formatCaseDisplay(row) }}
            </router-link>
            <span v-else>{{ formatCaseDisplay(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="140">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="沿革" min-width="260">
          <template #default="{ row }">
            <div class="lineage-cell">
              <el-tag :type="lineageTagType(row.lineage_status)" size="small">
                {{ lineageStatusText(row.lineage_status) }}
              </el-tag>
              <span><strong>来源文书：</strong>{{ displayLineageValue(row.source_document_id) }}</span>
              <span><strong>期限来源：</strong>{{ deadlineSourceText(row.deadline_source) }}</span>
              <span><strong>确认时间：</strong>{{ confirmedAtText(row.deadline_confirmed_at) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="到期日" width="130">
          <template #default="{ row }">
            {{ row.due_date }}
          </template>
        </el-table-column>
        <el-table-column label="期限依据" min-width="280">
          <template #default="{ row }">
            <div class="rule-cell">
              <span class="rule-main">{{ row.deadline_rule }}</span>
              <span class="rule-sub">{{ row.fee_basis }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="客户指示" width="120">
          <template #default="{ row }">
            {{ clientInstructionText(row.client_instruction) }}
          </template>
        </el-table-column>
        <el-table-column label="官费" width="120" align="right">
          <template #default="{ row }">
            {{ formatAmount(row.gov_fee_amt, row.currency) }}
          </template>
        </el-table-column>
        <el-table-column label="服务费" width="120" align="right">
          <template #default="{ row }">
            {{ formatAmount(row.service_fee_amt, row.currency) }}
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="币种" width="90" />
        <el-table-column label="草单" width="110">
          <template #default="{ row }">
            <el-tag :type="row.draft_generated ? 'success' : 'info'" size="small">
              {{ row.draft_generated ? '已生成' : '未生成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通知" width="110">
          <template #default="{ row }">
            <div class="notice-cell">
              <el-tag :type="row.notice_sent ? 'success' : 'warning'" size="small">
                {{ row.notice_sent ? '内部已通知' : '内部待通知' }}
              </el-tag>
              <span class="notice-count">次数 {{ row.notify_count }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="账单" min-width="180">
          <template #default="{ row }">
            <template v-if="row.billed && row.linked_bill_id">
              <router-link class="bill-link" :to="`/billing/bills/${row.linked_bill_id}`">
                {{ formatBillDisplay(row) }}
              </router-link>
            </template>
            <el-tag v-else :type="row.draft_generated ? 'warning' : 'info'" size="small">
              {{ row.draft_generated ? '未开账单' : '待生成草单' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="是否逾期" width="110">
          <template #default="{ row }">
            <el-tag :type="row.is_overdue ? 'danger' : 'success'" size="small">
              {{ row.is_overdue ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="动作入口" min-width="240" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <template v-if="isCurrentGrantFeeTask(row)">
                <el-button
                  size="small"
                  @click="openGrantEvidenceDialog(row)"
                >
                  选择授权通知证据
                </el-button>
                <el-button
                  v-if="grantFeeTaskAllowsAction(row, 'mark_waiting_client')"
                  size="small"
                  :loading="waitingTaskId === row.task_id"
                  @click="handleMarkWaitingClient(row)"
                >
                  标记等待客户
                </el-button>
                <el-button
                  size="small"
                  type="warning"
                  :loading="previewLoadingTaskId === row.task_id"
                  @click="openOfficialFeePreview(row)"
                >
                  预览官费
                </el-button>
                <el-button
                  size="small"
                  type="primary"
                  :loading="generatingTaskId === row.task_id"
                  :disabled="!canGenerateDraft(row)"
                  @click="handleGenerateDraft(row)"
                >
                  生成草单
                </el-button>
                <el-button
                  size="small"
                  type="success"
                  :loading="completingTaskId === row.task_id"
                  :disabled="!canMarkDone(row)"
                  @click="handleMarkDone(row)"
                >
                  标记完成
                </el-button>
                <template v-if="canSeeReplacementAction(row)">
                  <el-button
                    type="warning"
                    size="small"
                    :title="replacementDisabledReason"
                    :disabled="Boolean(replacementDisabledReason)"
                    @click="openReplacementDialog(row)"
                  >
                    更正通知
                  </el-button>
                  <span v-if="replacementDisabledReason" class="replacement-unavailable">
                    {{ replacementDisabledReason }}
                  </span>
                </template>
              </template>
              <span v-else class="ordinary-mutation-unavailable">
                来源未确认、已被替代或状态已变化，仅可查看
              </span>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[20, 50, 100]" />
    </div>

    <el-dialog
      v-model="grantEvidenceDialogVisible"
      title="选择授权通知证据"
      width="760px"
      :close-on-click-modal="false"
    >
      <LoadingBlock v-if="grantEvidenceLoading" :rows="4" />
      <DocumentLifecycleEvidenceActions
        v-else-if="grantEvidenceTask && grantEvidenceDocument"
        :document="grantEvidenceDocument"
        :grant-task="grantEvidenceTask"
        @error="handleGrantEvidenceError"
        @recorded="handleGrantEvidenceRecorded"
      />
    </el-dialog>

    <el-dialog
      v-model="officialFeeDialogVisible"
      title="授权登记官费预览"
      width="860px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="候选预览，尚未形成缴费义务"
        description="以下金额、版本和摘要均来自服务端当前生效的官费来源；确认后才生成只读官费草单。"
        type="warning"
        :closable="false"
        show-icon
      />
      <template v-if="officialFeePreview">
        <el-descriptions class="preview-source" :column="2" border>
          <el-descriptions-item label="来源机构">{{ officialFeePreview.source_authority }}</el-descriptions-item>
          <el-descriptions-item label="费率版本">{{ officialFeePreview.rate_book_version }}</el-descriptions-item>
          <el-descriptions-item label="生效日期">{{ officialFeePreview.effective_from }}</el-descriptions-item>
          <el-descriptions-item label="预览摘要">{{ officialFeePreview.preview_digest }}</el-descriptions-item>
          <el-descriptions-item label="费率簿摘要" :span="2">{{ officialFeePreview.rate_book_sha256 }}</el-descriptions-item>
        </el-descriptions>
        <el-table :data="officialFeePreview.lines" stripe size="small" class="preview-lines">
          <el-table-column prop="fee_code" label="费用代码" min-width="130" />
          <el-table-column prop="fee_name" label="费用项目" min-width="180" />
          <el-table-column prop="quantity" label="数量" width="80" align="right" />
          <el-table-column label="应缴金额" width="140" align="right">
            <template #default="{ row }">{{ formatAmount(row.payable_amount, row.currency) }}</template>
          </el-table-column>
          <el-table-column prop="source_version" label="来源版本" min-width="130" />
          <el-table-column prop="effective_from" label="行生效日" width="120" />
        </el-table>
        <p class="preview-total">
          合计：{{ formatAmount(officialFeePreview.total_payable_amount, officialFeePreview.currency) }}
        </p>
      </template>
      <template #footer>
        <el-button @click="officialFeeDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="officialFeeConfirming"
          :disabled="!officialFeePreview"
          @click="confirmOfficialFeePreview"
        >
          确认官费并生成草单
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="replacementDialogVisible"
      title="登记更正授权通知"
      width="620px"
      :close-on-click-modal="false"
      @closed="resetReplacementForm"
    >
      <el-alert
        v-if="replacementTemplateError"
        :title="replacementTemplateError"
        type="error"
        show-icon
        :closable="false"
        class="replacement-alert"
      />
      <el-form label-position="top" :model="replacementForm">
        <el-form-item label="文书模板">
          <el-select
            v-model="replacementForm.doc_template_id"
            class="replacement-full-width"
            filterable
            :loading="replacementTemplatesLoading"
            :disabled="replacementTemplatesLoading || Boolean(replacementTemplateError)"
            placeholder="请选择更正通知模板"
          >
            <el-option
              v-for="template in replacementTemplates"
              :key="template.id"
              :label="`${template.code} — ${template.name}`"
              :value="template.id"
            />
          </el-select>
        </el-form-item>
        <div class="replacement-grid">
          <el-form-item label="文书日期">
            <el-date-picker
              v-model="replacementForm.doc_date"
              type="date"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
              placeholder="请选择文书日期"
              class="replacement-full-width"
            />
          </el-form-item>
          <el-form-item label="文号">
            <el-input v-model="replacementForm.ref_no" placeholder="请输入文号" />
          </el-form-item>
        </div>
        <el-form-item label="标题">
          <el-input v-model="replacementForm.title" placeholder="请输入文书标题" />
        </el-form-item>
        <div class="replacement-grid">
          <el-form-item label="官方期限">
            <el-date-picker
              v-model="replacementForm.official_due_date"
              type="date"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
              placeholder="请选择官方期限"
              class="replacement-full-width"
            />
          </el-form-item>
          <el-form-item label="期限来源">
            <el-select
              v-model="replacementForm.official_due_date_source"
              class="replacement-full-width"
              placeholder="请选择期限来源"
            >
              <el-option label="人工核对官方通知" value="MANUAL_OFFICIAL_NOTICE" />
              <el-option label="导入官方通知" value="IMPORTED_OFFICIAL_NOTICE" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="确认状态">
          <el-tag type="success">已确认</el-tag>
        </el-form-item>
        <el-form-item label="替换原因">
          <el-input
            v-model="replacementForm.reason"
            type="textarea"
            :rows="2"
            placeholder="请输入替换原因"
          />
        </el-form-item>
        <el-form-item label="去重键">
          <el-input v-model="replacementForm.idempotency_key" placeholder="请输入去重键" />
        </el-form-item>
        <el-form-item label="说明（可选）">
          <el-input
            v-model="replacementForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入可选说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :disabled="replacementSubmitting" @click="replacementDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="primary"
          :loading="replacementSubmitting"
          :disabled="!replacementCanSubmit"
          @click="submitReplacementNotice"
        >
          提交更正通知
        </el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  applyGrantFeeBatchInstruction,
  applyGrantFeeTaskAction,
  bindGrantFeeTaskState,
  createGrantFeeTaskReplacementNotice,
  confirmGrantOfficialFees,
  generateGrantFeeDraft,
  generateGrantFeeNoticeDocuments,
  getGrantFeeTaskState,
  getGrantOfficialFeePreview,
  getGrantFeeTasks,
  grantFeeTaskAllowsAction,
  isCurrentGrantFeeTask,
} from '../../../api/grantFees'
import { getDocTemplates, getDocument } from '../../../api/documents'
import type { DocTemplate, Document } from '../../../api/documents.types'
import type {
  GrantFeeTaskBatchInstructionAction,
  GrantFeeTaskClientInstruction,
  GrantFeeTaskLineageStatus,
  GrantFeeTaskListItem,
  GrantFeeTaskListResponse,
  GrantFeeTaskStatus,
  GrantOfficialFeePreview,
} from '../../../api/grantFees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import DocumentLifecycleEvidenceActions from '../../documents/components/DocumentLifecycleEvidenceActions.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { useAuthStore } from '../../../stores/auth'

interface ReplacementForm {
  doc_template_id: string
  doc_date: string
  title: string
  ref_no: string
  official_due_date: string
  official_due_date_source: '' | 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE'
  reason: string
  idempotency_key: string
  description: string
}

const authStore = useAuthStore()
const router = useRouter()
const tasks = ref<GrantFeeTaskListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const generatingTaskId = ref<string | null>(null)
const completingTaskId = ref<string | null>(null)
const waitingTaskId = ref<string | null>(null)
const batchActionLoading = ref<GrantFeeTaskBatchInstructionAction | null>(null)
const batchNoticeLoading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedTaskIds = ref<string[]>([])
const replacementDialogVisible = ref(false)
const replacementTask = ref<GrantFeeTaskListItem | null>(null)
const replacementTemplates = ref<DocTemplate[]>([])
const replacementTemplatesLoading = ref(false)
const replacementTemplateError = ref('')
const replacementSubmitting = ref(false)
const previewLoadingTaskId = ref<string | null>(null)
const officialFeeDialogVisible = ref(false)
const officialFeePreview = ref<GrantOfficialFeePreview | null>(null)
const officialFeeConfirming = ref(false)
const officialFeeIdempotencyKey = ref(crypto.randomUUID())
const grantEvidenceDialogVisible = ref(false)
const grantEvidenceLoading = ref(false)
const grantEvidenceTask = ref<GrantFeeTaskListItem | null>(null)
const grantEvidenceDocument = ref<Document | null>(null)
const replacementForm = reactive<ReplacementForm>(emptyReplacementForm())
const filters = reactive<{
  status: '' | GrantFeeTaskStatus
  client_instruction: '' | GrantFeeTaskClientInstruction
  draft_generated: '' | 'true' | 'false'
  is_overdue: '' | 'true' | 'false'
  case_no: string
  date_range: [string, string] | []
}>({
  status: '',
  client_instruction: '',
  draft_generated: '',
  is_overdue: '',
  case_no: '',
  date_range: [],
})

const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)
const draftGeneratedText = computed({
  get: () => filters.draft_generated,
  set: (value: '' | 'true' | 'false') => {
    filters.draft_generated = value
  },
})
const overdueText = computed({
  get: () => filters.is_overdue,
  set: (value: '' | 'true' | 'false') => {
    filters.is_overdue = value
  },
})
const replacementDisabledReason = computed(() => (
  authStore.hasPermission('DocTemplate.Read')
    ? ''
    : '缺少文书模板读取权限，无法选择更正通知模板'
))
const replacementCanSubmit = computed(() => (
  !replacementSubmitting.value
  && !replacementTemplatesLoading.value
  && !replacementTemplateError.value
  && Boolean(replacementTask.value)
  && Boolean(replacementForm.doc_template_id)
  && Boolean(replacementForm.doc_date)
  && Boolean(replacementForm.title.trim())
  && Boolean(replacementForm.ref_no.trim())
  && Boolean(replacementForm.official_due_date)
  && Boolean(replacementForm.official_due_date_source)
  && Boolean(replacementForm.reason.trim())
  && Boolean(replacementForm.idempotency_key.trim())
))

function emptyReplacementForm(): ReplacementForm {
  return {
    doc_template_id: '',
    doc_date: '',
    title: '',
    ref_no: '',
    official_due_date: '',
    official_due_date_source: '',
    reason: '',
    idempotency_key: crypto.randomUUID(),
    description: '',
  }
}

function formatAmount(input: number | string, currency: string): string {
  const parsed = Number(input || 0)
  const safe = Number.isFinite(parsed) ? parsed : 0
  return `${currency} ${safe.toFixed(2)}`
}

async function openOfficialFeePreview(row: GrantFeeTaskListItem) {
  if (!isCurrentGrantFeeTask(row)) return
  previewLoadingTaskId.value = row.task_id
  error.value = null
  try {
    officialFeePreview.value = await getGrantOfficialFeePreview(row.task_id)
    officialFeeIdempotencyKey.value = crypto.randomUUID()
    officialFeeDialogVisible.value = true
  } catch (err) {
    error.value = err as ApiError
  } finally {
    previewLoadingTaskId.value = null
  }
}

async function confirmOfficialFeePreview() {
  const preview = officialFeePreview.value
  if (!preview || officialFeeConfirming.value) return
  officialFeeConfirming.value = true
  try {
    const result = await confirmGrantOfficialFees(preview.grant_fee_task_id, {
      preview_digest: preview.preview_digest,
      reviewed_evidence_version_id: preview.reviewed_evidence_version_id,
      expected_content_hash: preview.reviewed_evidence_content_hash,
      confirmed_at: new Date().toISOString().slice(0, 19),
      idempotency_key: officialFeeIdempotencyKey.value,
      lines: preview.lines.map(line => ({
        fee_code: line.fee_code,
        quantity: line.quantity,
        confirmed_payable_amount: line.payable_amount,
      })),
    })
    officialFeeDialogVisible.value = false
    ElMessage.success(result.reused ? '已恢复同一官费草单' : '官费草单生成成功')
    await router.push(`/fees/drafts/${result.draft_id}`)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    officialFeeConfirming.value = false
  }
}

function statusText(status: GrantFeeTaskStatus): string {
  const labels: Record<GrantFeeTaskStatus, string> = {
    OPEN: '待处理',
    WAITING_CLIENT: '等待客户',
    READY_TO_DRAFT: '可生成草单',
    DRAFT_GENERATED: '已生成草单',
    DONE: '已完成',
  }
  return labels[status] || '未知状态'
}

function statusTagType(status: GrantFeeTaskStatus): 'info' | 'warning' | 'success' | 'danger' {
  if (status === 'DONE') return 'success'
  if (status === 'READY_TO_DRAFT') return 'warning'
  if (status === 'DRAFT_GENERATED') return 'info'
  return 'warning'
}

function lineageStatusText(status: GrantFeeTaskLineageStatus): string {
  const labels: Record<GrantFeeTaskLineageStatus, string> = {
    CONFIRMED: '来源已确认',
    LEGACY_UNVERIFIED: '历史数据待核验',
    SUPERSEDED: '已被替代',
  }
  return labels[status]
}

function lineageTagType(status: GrantFeeTaskLineageStatus): 'info' | 'warning' | 'success' {
  if (status === 'CONFIRMED') return 'success'
  if (status === 'SUPERSEDED') return 'info'
  return 'warning'
}

function displayLineageValue(input?: string | null): string {
  return input || '未记录'
}

function deadlineSourceText(input?: string | null): string {
  if (!input) return '未记录'
  const labels: Record<string, string> = {
    MANUAL_OFFICIAL_NOTICE: '人工核对官方通知',
    IMPORTED_OFFICIAL_NOTICE: '导入官方通知',
  }
  return labels[input] || input
}

function confirmedAtText(input?: string | null): string {
  return input ? input.replace('T', ' ').replace(/Z$/, '') : '未记录'
}

function clientInstructionText(input: GrantFeeTaskClientInstruction): string {
  const labels: Record<GrantFeeTaskClientInstruction, string> = {
    NONE: '未指示',
    PAY: '支付',
    ABANDON: '放弃',
  }
  return labels[input] || '未知指示'
}

function isUuidLike(input?: string | null): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(String(input || '').trim())
}

function formatCaseDisplay(row: GrantFeeTaskListItem): string {
  return row.case_no || '未命名案件'
}

function formatBillDisplay(row: GrantFeeTaskListItem): string {
  if (row.linked_bill_no && !isUuidLike(row.linked_bill_no)) {
    return row.linked_bill_no
  }
  return row.linked_bill_id ? '已关联账单' : '未生成账单号'
}

function canGenerateDraft(row: GrantFeeTaskListItem): boolean {
  return isCurrentGrantFeeTask(row)
    && row.status === 'READY_TO_DRAFT'
    && !row.draft_generated
    && generatingTaskId.value !== row.task_id
}

function canMarkDone(row: GrantFeeTaskListItem): boolean {
  return isCurrentGrantFeeTask(row)
    && row.status === 'DRAFT_GENERATED'
    && completingTaskId.value !== row.task_id
}

function isOrdinaryMutationSelectable(row: GrantFeeTaskListItem): boolean {
  return grantFeeTaskAllowsAction(row, 'record_pay_instruction')
    || grantFeeTaskAllowsAction(row, 'record_abandon_instruction')
}

function canSeeReplacementAction(row: GrantFeeTaskListItem): boolean {
  return isCurrentGrantFeeTask(row)
    && authStore.hasPermission('GrantFeeTask.Write')
    && authStore.hasPermission('Doc.Create')
}

function isExecutableGrantTemplate(template: DocTemplate): boolean {
  if (!template.input_fields) return false
  try {
    const metadata = JSON.parse(template.input_fields) as Record<string, unknown>
    return metadata.catalog_status === 'EXECUTABLE'
      && metadata.execution_behavior === 'GRANT_NOTICE'
  } catch {
    return false
  }
}

async function loadReplacementTemplates() {
  replacementTemplatesLoading.value = true
  replacementTemplateError.value = ''
  replacementTemplates.value = []
  try {
    const response = await getDocTemplates({ direction: 'IN', enabled: true, page_size: 100 })
    replacementTemplates.value = response.items.filter(isExecutableGrantTemplate)
    if (!replacementTemplates.value.length) {
      replacementTemplateError.value = '未找到可执行的授权通知模板，无法提交'
    }
  } catch {
    replacementTemplateError.value = '更正通知模板加载失败，无法提交'
  } finally {
    replacementTemplatesLoading.value = false
  }
}

function resetReplacementForm() {
  Object.assign(replacementForm, emptyReplacementForm())
  replacementTask.value = null
  replacementTemplates.value = []
  replacementTemplateError.value = ''
  replacementTemplatesLoading.value = false
  replacementSubmitting.value = false
}

function openReplacementDialog(row: GrantFeeTaskListItem) {
  if (!canSeeReplacementAction(row) || replacementDisabledReason.value) return
  Object.assign(replacementForm, emptyReplacementForm())
  replacementTask.value = row
  replacementDialogVisible.value = true
  void loadReplacementTemplates()
}

function replacementErrorMessage(apiError: ApiError | undefined): string {
  if (apiError?.status === 400) return '更正通知内容不符合业务规则，请核对后重试'
  if (apiError?.status === 404) return '授权费任务不存在或已被移除'
  if (apiError?.status === 409) {
    return apiError.code === 'GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT'
      ? '去重键已用于不同内容，请核对后重试'
      : '当前任务无法发起更正通知，请刷新后重试'
  }
  if (apiError?.status === 422) return '更正通知信息校验失败，请检查必填项'
  if (apiError?.status === 401) return '登录状态已失效，请重新登录'
  if (apiError?.status === 403) return '缺少发起更正通知所需权限'
  return '更正通知提交失败，请重试'
}

async function submitReplacementNotice() {
  const task = replacementTask.value
  if (!task || !replacementCanSubmit.value || replacementSubmitting.value) return
  replacementSubmitting.value = true
  try {
    const result = await createGrantFeeTaskReplacementNotice(task.task_id, {
      idempotency_key: replacementForm.idempotency_key.trim(),
      reason: replacementForm.reason.trim(),
      document: {
        doc_template_id: replacementForm.doc_template_id,
        doc_date: replacementForm.doc_date,
        title: replacementForm.title.trim(),
        ref_no: replacementForm.ref_no.trim(),
        official_due_date: replacementForm.official_due_date,
        official_due_date_source: replacementForm.official_due_date_source as 'MANUAL_OFFICIAL_NOTICE' | 'IMPORTED_OFFICIAL_NOTICE',
        official_due_date_status: 'CONFIRMED',
        ...(replacementForm.description.trim()
          ? { description: replacementForm.description.trim() }
          : {}),
      },
    })
    ElMessage.success(result.reused ? '已复用同一更正通知结果' : '更正通知创建成功')
    replacementDialogVisible.value = false
    await fetchTasks()
  } catch (err) {
    ElMessage.error(replacementErrorMessage(err as ApiError | undefined))
  } finally {
    replacementSubmitting.value = false
  }
}

function buildParams() {
  const [date_from, date_to] = filters.date_range
  return {
    status: filters.status || undefined,
    client_instruction: filters.client_instruction || undefined,
    draft_generated: filters.draft_generated === '' ? undefined : filters.draft_generated === 'true',
    is_overdue: filters.is_overdue === '' ? undefined : filters.is_overdue === 'true',
    case_no: filters.case_no.trim() || undefined,
    date_from,
    date_to,
    page: page.value,
    page_size: pageSize.value,
  }
}

async function fetchTasks() {
  loading.value = true
  error.value = null
  try {
    const response: GrantFeeTaskListResponse = await getGrantFeeTasks(buildParams())
    const taskIdCounts = new Map<string, number>()
    for (const task of response.items) {
      taskIdCounts.set(task.task_id, (taskIdCounts.get(task.task_id) || 0) + 1)
    }
    tasks.value = await Promise.all(response.items.map(async (task) => {
      const occurrences = taskIdCounts.get(task.task_id) || 0
      if (occurrences !== 1 || task.lineage_status !== 'CONFIRMED') return task
      try {
        return bindGrantFeeTaskState(task, await getGrantFeeTaskState(task.task_id), occurrences)
      } catch {
        return task
      }
    }))
    total.value = response.total
    selectedTaskIds.value = []
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function handleSelectionChange(rows: GrantFeeTaskListItem[]) {
  selectedTaskIds.value = rows
    .filter((row) => isOrdinaryMutationSelectable(row))
    .map((row) => row.task_id)
}

async function openGrantEvidenceDialog(row: GrantFeeTaskListItem) {
  if (!isCurrentGrantFeeTask(row) || !row.source_document_id) return
  grantEvidenceTask.value = row
  grantEvidenceDocument.value = null
  grantEvidenceDialogVisible.value = true
  grantEvidenceLoading.value = true
  try {
    const document = await getDocument(row.source_document_id)
    if (document.id !== row.source_document_id || document.case_id !== row.case_id) {
      throw new Error('授权通知文书与当前任务不匹配')
    }
    grantEvidenceDocument.value = document
  } catch (err) {
    error.value = err as ApiError
  } finally {
    grantEvidenceLoading.value = false
  }
}

function handleGrantEvidenceError(err: ApiError) {
  error.value = err
}

function handleGrantEvidenceRecorded() {
  grantEvidenceDialogVisible.value = false
  void fetchTasks()
}

async function handleGenerateDraft(row: GrantFeeTaskListItem) {
  if (!canGenerateDraft(row)) {
    ElMessage.warning('当前任务不能生成草单')
    return
  }

  generatingTaskId.value = row.task_id
  try {
    const result = await generateGrantFeeDraft(row.task_id)
    ElMessage.success(result.reused ? '草单已存在，已复用' : '草单生成成功')
    await fetchTasks()
  } catch (err) {
    const apiError = err as ApiError | undefined
    const message = apiError?.message || '草单生成失败，请重试'
    ElMessage.error(message)
  } finally {
    generatingTaskId.value = null
  }
}

async function handleMarkDone(row: GrantFeeTaskListItem) {
  if (!canMarkDone(row)) return
  completingTaskId.value = row.task_id
  error.value = null
  try {
    await applyGrantFeeTaskAction(row.task_id, 'mark_done')
    ElMessage.success('授权费任务已标记完成')
    await fetchTasks()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    completingTaskId.value = null
  }
}

async function handleMarkWaitingClient(row: GrantFeeTaskListItem) {
  if (!grantFeeTaskAllowsAction(row, 'mark_waiting_client')) return
  waitingTaskId.value = row.task_id
  error.value = null
  try {
    await applyGrantFeeTaskAction(row.task_id, 'mark_waiting_client')
    ElMessage.success('授权费任务已标记为等待客户')
    await fetchTasks()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    waitingTaskId.value = null
  }
}

function batchInstructionText(action: GrantFeeTaskBatchInstructionAction): string {
  return action === 'record_pay_instruction' ? '支付' : '放弃'
}

async function handleBatchInstruction(action: GrantFeeTaskBatchInstructionAction) {
  if (!selectedTaskIds.value.length) {
    ElMessage.warning('请先勾选至少一条授权费任务。')
    return
  }

  const actionText = batchInstructionText(action)
  const eligibleTaskIds = tasks.value
    .filter((task) => selectedTaskIds.value.includes(task.task_id))
    .filter((task) => grantFeeTaskAllowsAction(task, action))
    .map((task) => task.task_id)
  if (eligibleTaskIds.length !== selectedTaskIds.value.length) {
    ElMessage.warning('已选任务状态已变化，请刷新后重试。')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认将已选 ${selectedTaskIds.value.length} 条授权费任务批量标记为${actionText}吗？`,
      '确认批量客户指示',
      {
        type: 'warning',
        confirmButtonText: '确认',
        cancelButtonText: '取消',
      },
    )
  } catch {
    return
  }

  batchActionLoading.value = action
  error.value = null
  try {
    const result = await applyGrantFeeBatchInstruction({
      task_ids: eligibleTaskIds,
      action,
    })
    ElMessage.success(`已批量更新 ${result.success_count} 条授权费任务为${actionText}`)
    await fetchTasks()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    batchActionLoading.value = null
  }
}

async function handleBatchNoticeGeneration() {
  if (!selectedTaskIds.value.length) {
    ElMessage.warning('请先勾选至少一条授权费任务。')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认基于已选 ${selectedTaskIds.value.length} 条授权费任务生成真实通知函吗？`,
      '确认批量生成通知函',
      {
        type: 'warning',
        confirmButtonText: '确认生成',
        cancelButtonText: '取消',
      },
    )
  } catch {
    return
  }

  batchNoticeLoading.value = true
  error.value = null
  try {
    const result = await generateGrantFeeNoticeDocuments({
      task_ids: selectedTaskIds.value,
    })
    ElMessage.success(`已生成 ${result.success_count} 份授权费通知函`)
    await fetchTasks()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    batchNoticeLoading.value = false
  }
}

function applyFilters() {
  page.value = 1
  void fetchTasks()
}

function resetFilters() {
  filters.status = ''
  filters.client_instruction = ''
  filters.draft_generated = ''
  filters.is_overdue = ''
  filters.case_no = ''
  filters.date_range = []
  applyFilters()
}

watch([page, pageSize], () => {
  void fetchTasks()
})

onMounted(() => {
  void fetchTasks()
})
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px 28px 32px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.page-header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.page-count {
  color: #6b7280;
  font-size: 14px;
}

.page-note {
  border-radius: 16px;
}

.page-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.summary-card {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.92));
  padding: 18px 20px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
}

.summary-label {
  display: block;
  color: #64748b;
  font-size: 13px;
  margin-bottom: 8px;
}

.summary-value {
  display: block;
  color: #0f172a;
  font-size: 22px;
  font-weight: 700;
}

.summary-note {
  font-size: 16px;
}

.page-error,
.page-empty {
  margin-top: 4px;
}

.preview-source,
.preview-lines {
  margin-top: 16px;
}

.preview-total {
  margin: 16px 0 0;
  text-align: right;
  font-size: 16px;
  font-weight: 700;
}

.page-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.case-link {
  color: #2563eb;
  text-decoration: none;
}

.bill-link {
  color: #2563eb;
  text-decoration: none;
}

.case-link:hover {
  text-decoration: underline;
}

.bill-link:hover {
  text-decoration: underline;
}

.notice-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notice-count {
  color: #64748b;
  font-size: 12px;
  line-height: 1.2;
}

.replacement-unavailable {
  max-width: 180px;
  color: #92400e;
  font-size: 12px;
  line-height: 1.35;
}

.ordinary-mutation-unavailable {
  max-width: 180px;
  color: #b45309;
  font-size: 12px;
  line-height: 1.35;
}

.replacement-alert {
  margin-bottom: 16px;
}

.replacement-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.replacement-full-width {
  width: 100%;
}

.lineage-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  color: #475569;
  font-size: 12px;
  line-height: 1.35;
}

.rule-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  line-height: 1.35;
}

.rule-main {
  color: #111827;
  font-size: 13px;
  font-weight: 600;
}

.rule-sub {
  color: #64748b;
  font-size: 12px;
}

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-summary {
    grid-template-columns: 1fr;
  }
}
</style>
