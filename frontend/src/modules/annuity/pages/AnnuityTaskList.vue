<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">年费任务列表</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
    </div>

    <el-row :gutter="12" style="margin-bottom: 16px">
      <el-col :xs="24" :sm="12" :md="6">
        <el-select
          v-model="filterStatus"
          aria-label="任务状态筛选"
          placeholder="任务状态"
          clearable
          @change="onFilterChange"
        >
          <el-option label="全部状态" value="" />
          <el-option label="待处理" value="OPEN" />
          <el-option label="已完成" value="DONE" />
          <el-option label="已取消" value="CANCELLED" />
        </el-select>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-select
          v-model="filterPendingMode"
          aria-label="处理范围筛选"
          placeholder="处理范围"
          clearable
          @change="onFilterChange"
        >
          <el-option label="全部范围" value="" />
          <el-option label="仅待处理" value="pending" />
          <el-option label="仅已处理" value="processed" />
        </el-select>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-select
          v-model="filterNoticeStatus"
          aria-label="通知状态筛选"
          placeholder="通知状态"
          clearable
          @change="onFilterChange"
        >
          <el-option label="全部通知状态" value="" />
          <el-option label="待通知" value="PENDING" />
          <el-option label="已通知" value="SENT" />
          <el-option label="无需通知" value="SKIPPED" />
        </el-select>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-date-picker
          v-model="filterDueRange"
          aria-label="到期日期范围筛选"
          type="daterange"
          range-separator="至"
          start-placeholder="到期开始日期"
          end-placeholder="到期结束日期"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
          clearable
          @change="onFilterChange"
        />
      </el-col>
    </el-row>

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
        <el-table-column prop="id" label="任务ID" width="90" />
        <el-table-column label="案件" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/cases/${row.case_id}`" class="case-link">
              {{ row.case_id }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="client_id" label="客户ID" min-width="180" />
        <el-table-column prop="year_no" label="年度" width="90" />
        <el-table-column label="到期日" width="130">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
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
            <el-table-column prop="source_task_id" label="来源任务ID" width="110" />
            <el-table-column prop="task_id" label="任务ID" width="90" />
            <el-table-column prop="year_no" label="年度" width="80" />
            <el-table-column prop="draft_id" label="草单ID" min-width="210" />
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
            <el-table-column prop="source_task_id" label="来源任务ID" width="110" />
            <el-table-column prop="task_id" label="任务ID" width="90">
              <template #default="{ row }">
                {{ row.task_id ?? '—' }}
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
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { generateAnnuityDrafts, getAnnuityTasks } from '../../../api/annuity'
import type { AnnuityGenerateDraftResult, AnnuityPendingMode, AnnuityTask } from '../../../api/annuity.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import InstructionDialog from '../components/InstructionDialog.vue'

const tasks = ref<AnnuityTask[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filterStatus = ref('')
const filterPendingMode = ref<AnnuityPendingMode | ''>('')
const filterNoticeStatus = ref('')
const filterDueRange = ref<string[]>([])
const instructionDialogVisible = ref(false)
const activeTask = ref<AnnuityTask | null>(null)
const selectedTaskIds = ref<number[]>([])
const generatingDrafts = ref(false)
const generatePayNextYear = ref(false)
const generateReceiptVisible = ref(false)
const generateReceipt = ref<AnnuityGenerateDraftResult | null>(null)

const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function onFilterChange() {
  page.value = 1
  fetchTasks()
}

async function fetchTasks() {
  loading.value = true
  error.value = null
  try {
    const dueFrom = filterDueRange.value.length === 2 ? filterDueRange.value[0] : undefined
    const dueTo = filterDueRange.value.length === 2 ? filterDueRange.value[1] : undefined

    const result = await getAnnuityTasks({
      page: page.value,
      page_size: pageSize.value,
      status: filterStatus.value || undefined,
      pending_mode: filterPendingMode.value || undefined,
      notice_status: filterNoticeStatus.value || undefined,
      due_from: dueFrom,
      due_to: dueTo,
    })
    tasks.value = result.items
    total.value = result.total
    selectedTaskIds.value = []
  } catch (err) {
    error.value = err as ApiError
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
      return status || '未知'
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
      return status || '未知'
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

function openInstructionDialog(task: AnnuityTask) {
  activeTask.value = task
  instructionDialogVisible.value = true
}

function handleInstructionSaved() {
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

function formatMoney(amount: number, currency: string): string {
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
