<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">授权费任务看板</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-space wrap>
          <el-button disabled type="primary">状态操作（预留）</el-button>
          <el-button disabled>账单与文书联动（预留）</el-button>
        </el-space>
      </div>
    </div>

    <el-alert
      class="page-note"
      title="当前页面支持查看、筛选、单行生成草单和草单后完成，其他联动暂未开放。"
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
          v-model="filters.case_id"
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
        <span class="summary-value summary-note">查看、筛选、单行生成</span>
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
      <el-table :data="tasks" aria-label="授权费任务列表" stripe size="small" class="compact-table">
        <el-table-column prop="task_id" label="任务编号" min-width="180" />
        <el-table-column label="案件" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/cases/${row.case_id}`" class="case-link">
              {{ row.case_id }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="140">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="到期日" width="130">
          <template #default="{ row }">
            {{ row.due_date }}
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
            <el-tag :type="row.notice_sent ? 'success' : 'warning'" size="small">
              {{ row.notice_sent ? '已通知' : '待通知' }}
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
        <el-table-column label="动作入口" min-width="180" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
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
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[20, 50, 100]" />
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { applyGrantFeeTaskAction, generateGrantFeeDraft, getGrantFeeTasks } from '../../../api/grantFees'
import type {
  GrantFeeTaskClientInstruction,
  GrantFeeTaskListItem,
  GrantFeeTaskListResponse,
  GrantFeeTaskStatus,
} from '../../../api/grantFees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const tasks = ref<GrantFeeTaskListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const generatingTaskId = ref<string | null>(null)
const completingTaskId = ref<string | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<{
  status: '' | GrantFeeTaskStatus
  client_instruction: '' | GrantFeeTaskClientInstruction
  draft_generated: '' | 'true' | 'false'
  is_overdue: '' | 'true' | 'false'
  case_id: string
  date_range: [string, string] | []
}>({
  status: '',
  client_instruction: '',
  draft_generated: '',
  is_overdue: '',
  case_id: '',
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

function formatAmount(input: number | string, currency: string): string {
  const parsed = Number(input || 0)
  const safe = Number.isFinite(parsed) ? parsed : 0
  return `${currency} ${safe.toFixed(2)}`
}

function statusText(status: GrantFeeTaskStatus): string {
  const labels: Record<GrantFeeTaskStatus, string> = {
    OPEN: '待处理',
    WAITING_CLIENT: '等待客户',
    READY_TO_DRAFT: '可生成草单',
    DRAFT_GENERATED: '已生成草单',
    DONE: '已完成',
  }
  return labels[status] || status
}

function statusTagType(status: GrantFeeTaskStatus): 'info' | 'warning' | 'success' | 'danger' {
  if (status === 'DONE') return 'success'
  if (status === 'READY_TO_DRAFT') return 'warning'
  if (status === 'DRAFT_GENERATED') return 'info'
  return 'warning'
}

function clientInstructionText(input: GrantFeeTaskClientInstruction): string {
  const labels: Record<GrantFeeTaskClientInstruction, string> = {
    NONE: '未指示',
    PAY: '支付',
    ABANDON: '放弃',
  }
  return labels[input] || input
}

function canGenerateDraft(row: GrantFeeTaskListItem): boolean {
  return row.status === 'READY_TO_DRAFT' && !row.draft_generated && generatingTaskId.value !== row.task_id
}

function canMarkDone(row: GrantFeeTaskListItem): boolean {
  return row.status === 'DRAFT_GENERATED' && completingTaskId.value !== row.task_id
}

function buildParams() {
  const [date_from, date_to] = filters.date_range
  return {
    status: filters.status || undefined,
    client_instruction: filters.client_instruction || undefined,
    draft_generated: filters.draft_generated === '' ? undefined : filters.draft_generated === 'true',
    is_overdue: filters.is_overdue === '' ? undefined : filters.is_overdue === 'true',
    case_id: filters.case_id || undefined,
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
    tasks.value = response.items
    total.value = response.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
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

function applyFilters() {
  page.value = 1
  void fetchTasks()
}

function resetFilters() {
  filters.status = ''
  filters.client_instruction = ''
  filters.draft_generated = ''
  filters.is_overdue = ''
  filters.case_id = ''
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

.page-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.case-link {
  color: #2563eb;
  text-decoration: none;
}

.case-link:hover {
  text-decoration: underline;
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
