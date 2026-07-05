<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">年费任务列表</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/reports/annuity-tasks">
          <el-button>年费任务统计</el-button>
        </router-link>
      </div>
    </div>

    <el-form class="filter-form" :inline="true">
      <el-form-item label="客户">
        <el-input
          v-model="filters.client_id"
          class="filter-input"
          clearable
          placeholder="请输入客户配置值"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="案件编号">
        <el-input
          v-model.trim="filters.case_no"
          class="filter-input"
          clearable
          placeholder="请输入案件编号"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="国家">
        <el-input
          v-model="filters.country"
          class="filter-input"
          clearable
          placeholder="例如 CN"
          @keyup.enter="applyFilters"
        />
      </el-form-item>
      <el-form-item label="年度">
        <el-input-number
          v-model="filters.annuity_year"
          class="filter-input"
          :min="1"
          :step="1"
          controls-position="right"
        />
      </el-form-item>
      <el-form-item label="任务状态">
        <el-select
          v-model="filters.task_status"
          class="filter-select"
          clearable
          placeholder="全部任务状态"
        >
          <el-option label="全部" value="" />
          <el-option label="待处理" value="OPEN" />
          <el-option label="已完成" value="DONE" />
          <el-option label="已取消" value="CANCELLED" />
        </el-select>
      </el-form-item>
      <el-form-item label="缴费状态">
        <el-select
          v-model="filters.payment_status"
          class="filter-select"
          clearable
          placeholder="全部缴费状态"
        >
          <el-option label="全部" value="" />
          <el-option label="已缴费" value="PAID" />
          <el-option label="未缴费" value="UNPAID" />
        </el-select>
      </el-form-item>
      <el-form-item label="到期日期">
        <el-date-picker
          v-model="filters.date_range"
          class="filter-range"
          type="daterange"
          range-separator="至"
          start-placeholder="到期开始日期"
          end-placeholder="到期结束日期"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          clearable
        />
      </el-form-item>
      <el-form-item label="处理范围">
        <el-select
          v-model="filters.pending_mode"
          class="filter-select"
          clearable
          placeholder="全部处理范围"
        >
          <el-option label="全部" value="" />
          <el-option label="仅待处理" value="pending" />
          <el-option label="仅已处理" value="processed" />
        </el-select>
      </el-form-item>
      <el-form-item label="通知状态">
        <el-select
          v-model="filters.notice_status"
          class="filter-select"
          clearable
          placeholder="全部通知状态"
        >
          <el-option label="全部" value="" />
          <el-option label="待通知" value="PENDING" />
          <el-option label="已通知" value="SENT" />
          <el-option label="无需通知" value="SKIPPED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="applyFilters">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <div class="batch-action-bar">
      <span class="batch-action-text">已选择 {{ selectedTaskIds.length }} 项</span>
      <el-checkbox v-model="generatePayNextYear">同时生成下一年度</el-checkbox>
      <el-button
        type="primary"
        aria-label="批量生成草单"
        :loading="generatingDrafts"
        :disabled="selectedTaskIds.length === 0"
        @click="handleBatchGenerateDrafts"
      >
        批量生成草单
      </el-button>
      <el-button
        type="primary"
        aria-label="生成年费任务"
        @click="showGenerateDialog = true"
      >
        生成年费任务
      </el-button>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="10" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无年费任务"
        message="请调整筛选条件后重试。"
        icon="📄"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        :data="tasks"
        aria-label="年费任务列表"
        stripe
        size="small"
        class="compact-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column label="案件" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/cases/${row.case_id}`" class="case-link">
              {{ formatCaseDisplay(row) }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="client_id" label="客户" min-width="180">
          <template #default="{ row }">
            {{ formatClientDisplay(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="year_no" label="年度" width="90" />
        <el-table-column label="到期日" width="130">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
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
        <el-table-column label="任务状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ taskStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通知状态" width="120">
          <template #default="{ row }">
            <el-tag :type="noticeTagType(row.notice_status)" size="small">
              {{ noticeStatusText(row.notice_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="客户指示" width="120">
          <template #default="{ row }">
            {{ instructionText(row.client_instruction) }}
          </template>
        </el-table-column>
        <el-table-column label="指示日期" width="130">
          <template #default="{ row }">
            {{ formatDate(row.instruction_date) }}
          </template>
        </el-table-column>
        <el-table-column label="官费预估" width="120" align="right">
          <template #default="{ row }">
            {{ row.gov_fee_amt?.toFixed(2) ?? '—' }}
          </template>
        </el-table-column>
        <el-table-column label="服务费预估" width="120" align="right">
          <template #default="{ row }">
            {{ row.service_fee_amt?.toFixed(2) ?? '—' }}
          </template>
        </el-table-column>
        <el-table-column label="通知次数" width="100" align="center">
          <template #default="{ row }">
            {{ row.notify_count }}
          </template>
        </el-table-column>
        <el-table-column label="草单已生成" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.draft_generated ? 'success' : 'info'" size="small">
              {{ row.draft_generated ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="通知已发" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.notice_sent ? 'success' : 'info'" size="small">
              {{ row.notice_sent ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="是否逾期" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_overdue ? 'danger' : 'info'" size="small">
              {{ row.is_overdue ? '逾期' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openInstructionDialog(row)">
              编辑指示
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
      />
    </div>

    <InstructionDialog
      v-model="instructionDialogVisible"
      :task-id="activeTask?.id ?? null"
      :initial-instruction="activeTask?.client_instruction"
      :initial-instruction-date="activeTask?.instruction_date"
      @success="handleInstructionSaved"
    />

    <AnnuityGenerateDialog
      v-model="showGenerateDialog"
      :initial-case-no="targetCaseNo"
      @saved="handleAnnuityTasksGenerated"
    />

    <el-dialog
      v-model="generateReceiptVisible"
      title="草单生成回执"
      width="900px"
    >
      <template v-if="generateReceipt">
        <el-descriptions :column="3" border style="margin-bottom: 16px">
          <el-descriptions-item label="请求数">{{ generateReceipt.summary.requested }}</el-descriptions-item>
          <el-descriptions-item label="目标数">{{ generateReceipt.summary.targets }}</el-descriptions-item>
          <el-descriptions-item label="成功数">{{ generateReceipt.summary.success }}</el-descriptions-item>
          <el-descriptions-item label="失败数">{{ generateReceipt.summary.failed }}</el-descriptions-item>
          <el-descriptions-item label="下一年度">
            {{ generateReceipt.summary.pay_next_year ? '是' : '否' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="receipt-block">
          <h3 class="receipt-title">成功明细</h3>
          <el-table :data="generateReceipt.success" size="small" border>
            <el-table-column label="来源任务" width="110">
              <template #default="{ row }">
                {{ formatSourceTaskDisplay(row.source_task_id) }}
              </template>
            </el-table-column>
            <el-table-column label="生成任务" width="90">
              <template #default="{ row }">
                {{ formatGeneratedTaskDisplay(row.task_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="year_no" label="年度" width="80" />
            <el-table-column label="草单" min-width="210">
              <template #default="{ row }">
                {{ formatDraftDisplay(row.draft_id) }}
              </template>
            </el-table-column>
            <el-table-column label="金额" width="140" align="right">
              <template #default="{ row }">
                {{ formatMoney(row.amount, row.currency) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="receipt-block" style="margin-top: 16px">
          <h3 class="receipt-title">失败明细</h3>
          <el-table :data="generateReceipt.failed" size="small" border>
            <el-table-column label="来源任务" width="110">
              <template #default="{ row }">
                {{ formatSourceTaskDisplay(row.source_task_id) }}
              </template>
            </el-table-column>
            <el-table-column label="生成任务" width="90">
              <template #default="{ row }">
                {{ formatGeneratedTaskDisplay(row.task_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="year_no" label="年度" width="80" />
            <el-table-column prop="code" label="错误码" width="220" />
            <el-table-column prop="status_code" label="状态码" width="90" />
            <el-table-column label="后端返回" min-width="240">
              <template #default="{ row }">
                {{ formatBackendMessage(row.message) }}
              </template>
            </el-table-column>
            <el-table-column label="失败原因" min-width="220">
              <template #default="{ row }">
                {{ mapDraftFailureMessage(row.code, row.message) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>

      <template #footer>
        <el-button @click="generateReceiptVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { generateAnnuityDrafts, getAnnuityTasks } from '../../../api/annuity'
import type {
  AnnuityGenerateDraftResult,
  AnnuityPendingMode,
  AnnuityTask,
  AnnuityTaskGenerateResult,
} from '../../../api/annuity.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import InstructionDialog from '../components/InstructionDialog.vue'
import AnnuityGenerateDialog from '../components/AnnuityGenerateDialog.vue'

const tasks = ref<AnnuityTask[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<{
  client_id: string
  case_no: string
  country: string
  annuity_year: number | undefined
  task_status: string
  payment_status: string
  pending_mode: AnnuityPendingMode | ''
  notice_status: string
  date_range: string[]
}>({
  client_id: '',
  case_no: '',
  country: '',
  annuity_year: undefined,
  task_status: '',
  payment_status: '',
  pending_mode: '',
  notice_status: '',
  date_range: [],
})
const instructionDialogVisible = ref(false)
const activeTask = ref<AnnuityTask | null>(null)
const selectedTaskIds = ref<number[]>([])
const generatingDrafts = ref(false)
const generatePayNextYear = ref(false)
const generateReceiptVisible = ref(false)
const generateReceipt = ref<AnnuityGenerateDraftResult | null>(null)
const showGenerateDialog = ref(false)

const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)
const targetCaseNo = computed(() => filters.case_no.trim())

function applyFilters() {
  page.value = 1
  fetchTasks()
}

function resetFilters() {
  filters.client_id = ''
  filters.case_no = ''
  filters.country = ''
  filters.annuity_year = undefined
  filters.task_status = ''
  filters.payment_status = ''
  filters.pending_mode = ''
  filters.notice_status = ''
  filters.date_range = []
  applyFilters()
}

async function fetchTasks() {
  loading.value = true
  error.value = null
  try {
    const dueFrom = filters.date_range.length === 2 ? filters.date_range[0] : undefined
    const dueTo = filters.date_range.length === 2 ? filters.date_range[1] : undefined

    const result = await getAnnuityTasks({
      page: page.value,
      page_size: pageSize.value,
      client_id: filters.client_id || undefined,
      case_no: targetCaseNo.value || undefined,
      country: filters.country || undefined,
      annuity_year: filters.annuity_year,
      task_status: filters.task_status || undefined,
      payment_status: filters.payment_status || undefined,
      pending_mode: filters.pending_mode || undefined,
      notice_status: filters.notice_status || undefined,
      date_from: dueFrom,
      date_to: dueTo,
    })
    tasks.value = result.items
    total.value = result.total
    selectedTaskIds.value = []
  } catch (err) {
    error.value = err as ApiError
    tasks.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function formatDate(dateValue?: string): string {
  if (!dateValue) return '—'
  const parsed = dayjs(dateValue)
  return parsed.isValid() ? parsed.format('YYYY-MM-DD') : dateValue
}

function statusTagType(status: string): 'warning' | 'success' | 'info' | 'danger' {
  switch (status?.toUpperCase()) {
    case 'OPEN':
      return 'warning'
    case 'DONE':
      return 'success'
    case 'CANCELLED':
    case 'CANCELED':
      return 'info'
    default:
      return 'danger'
  }
}

function taskStatusText(status: string): string {
  switch (status?.toUpperCase()) {
    case 'OPEN':
      return '待处理'
    case 'DONE':
      return '已完成'
    case 'CANCELLED':
    case 'CANCELED':
      return '已取消'
    default:
      return '未知状态'
  }
}

function noticeTagType(status: string): 'warning' | 'success' | 'info' {
  switch (status?.toUpperCase()) {
    case 'PENDING':
      return 'warning'
    case 'SENT':
      return 'success'
    default:
      return 'info'
  }
}

function noticeStatusText(status: string): string {
  switch (status?.toUpperCase()) {
    case 'PENDING':
      return '待通知'
    case 'SENT':
      return '已通知'
    case 'SKIPPED':
      return '无需通知'
    default:
      return '未知状态'
  }
}

function instructionText(instruction?: string): string {
  switch (instruction?.toUpperCase()) {
    case 'PAY':
      return '缴费'
    case 'DEFER':
      return '延期'
    case 'ABANDON':
      return '放弃'
    default:
      return '未指示'
  }
}

function formatCaseDisplay(row: AnnuityTask): string {
  return row.case_no || '未命名案件'
}

function formatClientDisplay(row: AnnuityTask): string {
  return row.client_id ? '已关联客户' : '未关联客户'
}

function formatSourceTaskDisplay(value?: number | null): string {
  return value ? '已关联任务' : '未关联任务'
}

function formatGeneratedTaskDisplay(value?: number | null): string {
  return value ? '已生成任务' : '未生成任务'
}

function formatDraftDisplay(value?: string | null): string {
  return value ? '已生成草单' : '未生成草单'
}

function openInstructionDialog(task: AnnuityTask) {
  activeTask.value = task
  instructionDialogVisible.value = true
}

function handleInstructionSaved() {
  fetchTasks()
}

function handleAnnuityTasksGenerated(result: AnnuityTaskGenerateResult) {
  const generatedCaseNo = result.case_no?.trim()
  if (generatedCaseNo) {
    filters.case_no = generatedCaseNo
    page.value = 1
  }
  fetchTasks()
}

function handleSelectionChange(rows: AnnuityTask[]) {
  selectedTaskIds.value = rows.map((row) => row.id)
}

function mapGenerateErrorMessage(apiError: ApiError): string {
  switch (apiError.code) {
    case 'ANNUITY_TASK_REQUIRED':
      return '请至少选择一条任务后再生成草单。'
    case 'ANNUITY_STATE_CONFLICT':
      return '存在任务状态冲突，无法生成草单。'
    case 'ANNUITY_TASK_NOT_FOUND':
      return '部分任务不存在或已失效，请刷新后重试。'
    case 'VALIDATION_ERROR':
      return '请求参数校验失败，请检查后重试。'
    default:
      if (apiError.status === 401) return '登录已失效，请重新登录。'
      if (apiError.status === 403) return '无权限执行该操作。'
      if (apiError.status === 409) return '状态冲突，暂时无法生成草单。'
      if (apiError.status === 422) return '输入参数不符合要求，请检查后重试。'
      return '生成草单失败，请稍后重试。'
  }
}

function mapDraftFailureMessage(code: string, backendMessage?: string): string {
  switch (code) {
    case 'ANNUITY_DRAFT_ALREADY_GENERATED':
      return '该任务对应年度草单已生成。'
    case 'ANNUITY_TASK_NOT_FOUND':
      return '未找到对应的年费任务。'
    case 'ANNUITY_STATE_CONFLICT':
      return '任务状态不允许生成草单。'
    case 'FEE_RATE_NOT_FOUND':
      return '缺少年费费率配置，无法生成草单。'
    default:
      return backendMessage
        ? `生成失败（${code}），后端信息：${backendMessage}`
        : `生成失败（${code}）`
  }
}

function formatBackendMessage(message?: string): string {
  return message ? `后端信息：${message}` : '后端信息：无'
}

function formatMoney(amount: number, currency = 'CNY'): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(amount || 0)
}

async function handleBatchGenerateDrafts() {
  if (selectedTaskIds.value.length === 0) {
    ElMessage.warning('请先选择至少一条任务。')
    return
  }

  try {
    await ElMessageBox.confirm(
      `将为选中的 ${selectedTaskIds.value.length} 条任务生成草单，是否继续？`,
      '确认批量生成',
      {
        confirmButtonText: '确认生成',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  generatingDrafts.value = true
  try {
    const result = await generateAnnuityDrafts({
      task_ids: selectedTaskIds.value,
      pay_next_year: generatePayNextYear.value,
      currency: 'CNY',
    })
    generateReceipt.value = result
    generateReceiptVisible.value = true
    ElMessage.success(
      `生成完成：成功 ${result.summary.success} 条，失败 ${result.summary.failed} 条。`,
    )
    fetchTasks()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(mapGenerateErrorMessage(apiError))
  } finally {
    generatingDrafts.value = false
  }
}

watch([page, pageSize], () => {
  fetchTasks()
})

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.case-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.case-link:hover {
  text-decoration: underline;
}

.batch-action-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-form {
  margin-bottom: 16px;
}

.filter-input,
.filter-select {
  width: 180px;
}

.filter-range {
  width: 260px;
}

.batch-action-text {
  color: var(--color-text-secondary);
}

.receipt-title {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
}

.page-error {
  outline: none;
}

.rule-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  line-height: 1.35;
}

.rule-main {
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 600;
}

.rule-sub {
  color: var(--color-text-secondary);
  font-size: 12px;
}

:deep(.el-button:focus-visible),
:deep(.el-input__wrapper:focus-within),
:deep(.el-select__wrapper.is-focused),
:deep(.el-textarea__inner:focus-visible),
:deep(.el-date-editor:focus-within) {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
}
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .page-header-right,
  .filter-actions,
  .action-row,
  .form-actions,
  .batch-action-bar {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-header-right :deep(.el-button),
  .filter-actions :deep(.el-button),
  .action-row :deep(.el-button),
  .form-actions :deep(.el-button),
  .batch-action-bar :deep(.el-button) {
    flex: 1;
    min-width: 120px;
  }
}
</style>
