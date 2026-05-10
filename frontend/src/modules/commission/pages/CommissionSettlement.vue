<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">提成结算批次</h1>
        <span class="page-count" aria-live="polite">统计行数：{{ report?.summary.line_count ?? 0 }}</span>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="section-title">创建结算批次</div>
      </template>

      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="代理人编号" prop="agent_id">
              <el-input v-model.trim="createForm.agent_id" placeholder="请输入代理人编号" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="结算币种" prop="currency">
              <el-input v-model.trim="createForm.currency" placeholder="例如：CNY" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="8" :lg="8">
            <el-form-item label="结算期间">
              <el-date-picker
                v-model="createForm.period_range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                class="w-full"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="24">
            <el-form-item label="备注">
              <el-input v-model="createForm.remark" type="textarea" :rows="2" placeholder="可选备注" />
            </el-form-item>
          </el-col>
          <el-col :span="24" class="action-row">
            <el-button type="primary" :loading="creating" @click="handleCreateSettlement">创建批次</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="section-title">生成结算明细</div>
      </template>

      <el-row :gutter="12" class="generate-row">
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-input-number
            v-model="generateForm.settlement_id"
            aria-label="结算批次编号"
            :min="1"
            :controls="false"
            placeholder="结算批次编号"
            class="w-full"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-input
            v-model.trim="generateForm.case_id"
            aria-label="生成目标案件号"
            placeholder="目标案件号"
            clearable
            @keyup.enter="handleGenerateLines"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-button
            type="success"
            aria-label="生成结算明细"
            :loading="generating"
            :disabled="!generateForm.settlement_id"
            @click="handleGenerateLines"
          >
            生成明细
          </el-button>
        </el-col>
      </el-row>
      <div class="generate-guide">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          title="可输入案件号生成目标案件的结算明细；后端会按案件号解析到案件记录，只处理满足可结算条件的提成。"
        />
      </div>

      <div v-if="lastGenerate" class="result-block">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="批次编号">{{ lastGenerate.settlement_id }}</el-descriptions-item>
          <el-descriptions-item label="目标案件号">{{ lastGenerateCaseNumber || '全部' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="settlementStatusTagType(lastGenerate.status)" size="small">
              {{ settlementStatusLabel(lastGenerate.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="明细总数">{{ lastGenerate.line_count }}</el-descriptions-item>
          <el-descriptions-item label="新增明细">{{ lastGenerate.created_count }}</el-descriptions-item>
          <el-descriptions-item label="更新明细">{{ lastGenerate.updated_count }}</el-descriptions-item>
          <el-descriptions-item label="明细总额">{{ formatMoney(lastGenerate.total_amount) }}</el-descriptions-item>
        </el-descriptions>
        <el-alert
          v-if="lastGenerate.status === 'GENERATED'"
          type="success"
          :closable="false"
          show-icon
          title="本次结算明细已生成，相关提成阶段结果已写入，可在提成记录列表查看阶段完成状态。"
          class="result-alert"
        />
      </div>

      <div v-if="recentSettlements.length" class="result-block">
        <div class="sub-title">本页创建的批次</div>
        <el-table :data="recentSettlements" stripe size="small" class="compact-table">
          <el-table-column prop="id" label="编号" width="80" />
          <el-table-column prop="agent_id" label="代理人编号" min-width="140">
            <template #default="{ row }">
              {{ row.agent_id || '—' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="settlementStatusTagType(row.status)" size="small">
                {{ settlementStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="currency" label="币种" width="90" />
          <el-table-column prop="line_count" label="明细数" width="90" />
          <el-table-column label="总额" width="120" align="right">
            <template #default="{ row }">
              <span class="mono-num">{{ formatMoney(row.total_amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button text size="small" @click="useSettlement(row.id)">用于生成</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="section-title">结算报表与统计</div>
      </template>

      <el-row :gutter="12" class="filter-bar">
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-input v-model.trim="reportFilters.agent_id" aria-label="报表代理人筛选" placeholder="代理人编号" clearable @keyup.enter="queryReport" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-input
            v-model.trim="reportFilters.case_id"
            aria-label="报表目标案件号筛选"
            placeholder="目标案件号"
            clearable
            @keyup.enter="queryReport"
          />
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="3">
          <el-input v-model.trim="reportFilters.currency" aria-label="报表币种筛选" placeholder="币种" clearable @keyup.enter="queryReport" />
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="3">
          <el-select v-model="reportFilters.time_field" aria-label="报表时间维度筛选" placeholder="时间维度">
            <el-option label="按明细创建时间" value="line_created_at" />
            <el-option label="按可结算日期" value="settleable_date" />
            <el-option label="按结算期间" value="settlement_period" />
          </el-select>
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="3">
          <el-input v-model.trim="reportFilters.settlement_status" aria-label="报表批次状态筛选" placeholder="批次状态" clearable @keyup.enter="queryReport" />
        </el-col>
        <el-col :xs="12" :sm="8" :md="4" :lg="3">
          <el-input v-model.trim="reportFilters.line_status" aria-label="报表明细状态筛选" placeholder="明细状态" clearable @keyup.enter="queryReport" />
        </el-col>
        <el-col :xs="24" :sm="16" :md="8" :lg="7">
          <el-date-picker
            v-model="reportFilters.date_range"
            aria-label="报表日期范围筛选"
            type="daterange"
            range-separator="至"
            start-placeholder="报表开始日期"
            end-placeholder="报表结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="w-full"
          />
        </el-col>
        <el-col :xs="24" :sm="8" :md="4" :lg="3" class="filter-actions">
          <el-button type="primary" aria-label="查询提成报表" :loading="reportLoading" @click="queryReport">查询报表</el-button>
          <el-button aria-label="导出提成报表" :loading="exporting" @click="handleExportReport">导出报表</el-button>
          <el-button aria-label="重置报表筛选" @click="resetReportFilters">重置</el-button>
        </el-col>
      </el-row>

      <LoadingBlock v-if="reportLoading" :rows="6" />

      <div v-else-if="!report" class="page-empty">
        <EmptyState title="暂无报表数据" message="请先设置条件并查询报表。" icon="📊" />
      </div>

      <div v-else>
        <el-row :gutter="12" class="stat-grid">
          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-card shadow="never" class="stat-card">
              <div class="stat-label">明细总数</div>
              <div class="stat-value">{{ report.summary.line_count }}</div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-card shadow="never" class="stat-card">
              <div class="stat-label">结算批次数</div>
              <div class="stat-value">{{ report.summary.settlement_count }}</div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-card shadow="never" class="stat-card">
              <div class="stat-label">代理人数</div>
              <div class="stat-value">{{ report.summary.agent_count }}</div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-card shadow="never" class="stat-card">
              <div class="stat-label">案件数</div>
              <div class="stat-value">{{ report.summary.case_count }}</div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="8">
            <el-card shadow="never" class="stat-card">
              <div class="stat-label">提成总额</div>
              <div class="stat-value mono-num">{{ formatMoney(report.summary.total_amount) }}</div>
              <div class="stat-hint">时间口径：{{ timeFieldLabel(report.filters.time_field) }}</div>
            </el-card>
          </el-col>
        </el-row>

        <div class="report-hint">
          统计口径仅覆盖已生成的提成记录与结算数据，不包含潜在提成预测或成本占比分析。
        </div>

        <div class="table-section">
          <div class="sub-title">当前筛选摘要</div>
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="代理人">{{ report.filters.agent_id || '全部' }}</el-descriptions-item>
            <el-descriptions-item label="目标案件号">{{ reportTargetCaseNumber || '全部' }}</el-descriptions-item>
            <el-descriptions-item v-if="reportTargetResolvedCaseId" label="解析案件标识">
              {{ reportTargetResolvedCaseId }}
            </el-descriptions-item>
            <el-descriptions-item label="币种">{{ report.filters.currency || '全部' }}</el-descriptions-item>
            <el-descriptions-item label="时间口径">{{ timeFieldLabel(report.filters.time_field) }}</el-descriptions-item>
            <el-descriptions-item label="批次状态">{{ report.filters.settlement_status || '全部' }}</el-descriptions-item>
            <el-descriptions-item label="明细状态">{{ report.filters.line_status || '全部' }}</el-descriptions-item>
            <el-descriptions-item label="开始日期">{{ report.filters.date_from || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="结束日期">{{ report.filters.date_to || '未设置' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="reportTargetCaseNumber" class="table-section">
          <div class="sub-title">目标案件生成引导</div>
          <el-alert
            v-if="settleableReportDetails.length"
            type="success"
            :closable="false"
            show-icon
            :title="`目标案件号 ${reportTargetCaseNumber} 当前有 ${settleableReportDetails.length} 条可结算明细，可用于生成结算批次明细。`"
          />
          <el-alert
            v-else
            type="warning"
            :closable="false"
            show-icon
            :title="`目标案件号 ${reportTargetCaseNumber} 当前没有可结算明细，请先确认收款、阶段完成或提成规则。`"
          />
          <div class="guide-actions">
            <el-button
              type="success"
              :disabled="!settleableReportDetails.length || !generateForm.settlement_id"
              :loading="generating"
              @click="useReportTargetForGeneration"
            >
              按目标案件号生成
            </el-button>
            <span class="guide-note">
              需要先创建或选择一个结算批次；系统仅向接口提交案件号，不需要手工查找隐藏案件 ID。
            </span>
          </div>
        </div>

        <div v-if="!report.by_agent.length && !report.by_case.length && !report.details.length" class="page-empty">
          <EmptyState title="没有匹配的提成统计结果" message="请调整筛选条件后重新查询。" icon="📄" />
        </div>

        <template v-else>
          <div class="table-section">
            <div class="sub-title">按代理人统计</div>
            <el-table :data="report.by_agent" stripe size="small" class="compact-table">
              <el-table-column prop="agent_id" label="代理人编号" min-width="160">
                <template #default="{ row }">
                  {{ row.agent_id || '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="line_count" label="明细数" width="100" />
              <el-table-column label="总额" width="140" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatMoney(row.total_amount) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="table-section">
            <div class="sub-title">按案件统计</div>
            <el-table :data="report.by_case" stripe size="small" class="compact-table">
              <el-table-column prop="case_id" label="案件标识" min-width="180">
                <template #default="{ row }">
                  {{ row.case_id || '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="line_count" label="明细数" width="100" />
              <el-table-column label="总额" width="140" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatMoney(row.total_amount) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="table-section">
            <div class="sub-title">明细列表</div>
            <el-table :data="report.details" stripe size="small" class="compact-table">
              <el-table-column prop="settlement_id" label="批次编号" width="90" />
              <el-table-column prop="commission_id" label="提成编号" width="90" />
              <el-table-column prop="agent_id" label="代理人编号" min-width="140">
                <template #default="{ row }">
                  {{ row.agent_id || '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="case_id" label="案件标识" min-width="150" />
              <el-table-column prop="settlement_status" label="批次状态" width="100">
                <template #default="{ row }">
                  <el-tag
                    v-if="row.settlement_status"
                    :type="settlementStatusTagType(row.settlement_status)"
                    size="small"
                  >
                    {{ settlementStatusLabel(row.settlement_status) }}
                  </el-tag>
                  <span v-else>—</span>
                </template>
              </el-table-column>
              <el-table-column prop="line_status" label="明细状态" width="100">
                <template #default="{ row }">
                  <el-tag
                    v-if="row.line_status"
                    :type="lineStatusTagType(row.line_status)"
                    size="small"
                  >
                    {{ lineStatusLabel(row.line_status) }}
                  </el-tag>
                  <span v-else>—</span>
                </template>
              </el-table-column>
              <el-table-column label="S1 阶段" width="90">
                <template #default="{ row }">
                  <el-tag :type="completionTagType(row.s1_done)" size="small">
                    {{ completionLabel(row.s1_done) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="S2 阶段" width="90">
                <template #default="{ row }">
                  <el-tag :type="completionTagType(row.s2_done)" size="small">
                    {{ completionLabel(row.s2_done) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="可结算" width="90">
                <template #default="{ row }">
                  <el-tag :type="completionTagType(row.is_settleable)" size="small">
                    {{ settleableLabel(row.is_settleable) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="金额" width="120" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatMoney(row.amount) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="settleable_date" label="可结算日期" width="120">
                <template #default="{ row }">
                  {{ row.settleable_date || '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" min-width="170">
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </div>
    </el-card>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import {
  createCommissionSettlement,
  exportCommissionSettlementReport,
  generateCommissionSettlementLines,
  getCommissionSettlementReport,
} from '../../../api/commission'
import type {
  CommissionSettlement,
  CommissionSettlementCreatePayload,
  CommissionSettlementGenerateLinesParams,
  CommissionSettlementGenerateLinesResult,
  CommissionSettlementReportParams,
  CommissionSettlementReportResult,
} from '../../../api/commission.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

const error = ref<ApiError | null>(null)

const createFormRef = ref<FormInstance>()
const creating = ref(false)
const createForm = reactive({
  agent_id: '',
  currency: 'CNY',
  period_range: [] as string[],
  remark: '',
})

const createRules: FormRules = {
  agent_id: [{ required: true, message: '代理人编号为必填项', trigger: 'blur' }],
  currency: [{ required: true, message: '币种为必填项', trigger: 'blur' }],
}

const generateForm = reactive({
  settlement_id: undefined as number | undefined,
  case_id: '',
})
const generating = ref(false)
const lastGenerate = ref<CommissionSettlementGenerateLinesResult | null>(null)
const lastGenerateCaseNumber = ref('')
const recentSettlements = ref<CommissionSettlement[]>([])

const reportLoading = ref(false)
const exporting = ref(false)
const report = ref<CommissionSettlementReportResult | null>(null)
const lastReportCaseNumber = ref('')
const reportFilters = reactive({
  agent_id: '',
  case_id: '',
  currency: '',
  settlement_status: '',
  line_status: '',
  date_range: [] as string[],
  time_field: 'line_created_at' as CommissionSettlementReportParams['time_field'],
})

const reportTargetCaseNumber = computed(() => lastReportCaseNumber.value || report.value?.filters.case_id || '')
const reportTargetResolvedCaseId = computed(() => {
  if (!report.value?.filters.case_id) return ''
  if (report.value.filters.case_id === reportTargetCaseNumber.value) return ''
  return report.value.filters.case_id
})
const settleableReportDetails = computed(() => report.value?.details.filter((detail) => detail.is_settleable) || [])

function toApiError(errorLike: unknown): ApiError | null {
  if (!errorLike || typeof errorLike !== 'object') return null
  const candidate = errorLike as Partial<ApiError>
  if (typeof candidate.status !== 'number') return null
  if (typeof candidate.code !== 'string') return null
  if (typeof candidate.message !== 'string') return null
  return candidate as ApiError
}

function mapCreateSettlementError(errorLike: unknown): string {
  const apiError = toApiError(errorLike)
  if (!apiError || apiError.status === 0) return '网络异常或服务不可用，请稍后重试。'

  if (apiError.status === 400 && apiError.code === 'COMMISSION_SETTLEMENT_INVALID') {
    return '结算批次参数无效，请检查代理人、期间和币种。'
  }
  if (apiError.status === 409 && apiError.code === 'COMMISSION_SETTLEMENT_CONFLICT') {
    return '结算批次冲突：当前条件下已存在进行中的批次。'
  }
  if (apiError.status === 401) return '登录已失效，请重新登录后重试。'
  if (apiError.status === 403) return '无权限创建结算批次。'
  if (apiError.status === 422) return '提交数据校验失败，请检查输入后重试。'

  return '创建结算批次失败，请稍后重试。'
}

function mapGenerateLinesError(errorLike: unknown): string {
  const apiError = toApiError(errorLike)
  if (!apiError || apiError.status === 0) return '网络异常或服务不可用，请稍后重试。'

  if (apiError.status === 404 && apiError.code === 'COMMISSION_SETTLEMENT_NOT_FOUND') {
    return '结算批次不存在，请确认批次编号。'
  }
  if (apiError.status === 400 && apiError.code === 'COMMISSION_SETTLEMENT_INVALID') {
    return '结算批次参数或状态无效，无法生成明细。'
  }
  if (apiError.status === 409 && apiError.code === 'COMMISSION_SETTLEMENT_CONFLICT') {
    return '结算批次冲突：当前状态不允许生成或存在重复明细。'
  }
  if (apiError.status === 401) return '登录已失效，请重新登录后重试。'
  if (apiError.status === 403) return '无权限生成结算明细。'
  if (apiError.status === 422) return '请求参数校验失败，请检查后重试。'

  return '生成结算明细失败，请稍后重试。'
}

function mapReportError(errorLike: unknown): string {
  const apiError = toApiError(errorLike)
  if (!apiError || apiError.status === 0) return '网络异常或服务不可用，请稍后重试。'

  if (apiError.status === 400 && apiError.code === 'COMMISSION_REPORT_INVALID') {
    return '报表查询条件无效，请检查时间范围和筛选项。'
  }
  if (apiError.status === 401) return '登录已失效，请重新登录后重试。'
  if (apiError.status === 403) return '无权限查看结算报表。'
  if (apiError.status === 422) return '报表查询参数校验失败，请检查后重试。'

  return '查询结算报表失败，请稍后重试。'
}

function normalizeOptional(value: string): string | undefined {
  const trimmed = value.trim()
  return trimmed || undefined
}

function formatMoney(value: number): string {
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function timeFieldLabel(value: CommissionSettlementReportParams['time_field'] | undefined): string {
  switch (value) {
    case 'settleable_date':
      return '按可结算日期'
    case 'settlement_period':
      return '按结算期间'
    case 'line_created_at':
    default:
      return '按明细创建时间'
  }
}

function settlementStatusLabel(status: string | undefined): string {
  const map: Record<string, string> = {
    DRAFT: '草稿',
    GENERATED: '已生成',
    CREATED: '已创建',
    PENDING: '待处理',
    SETTLED: '已结算',
    COMPLETE: '已完成',
    CLOSED: '已关闭',
    CANCELLED: '已取消',
    VOID: '已作废',
    OPEN: '进行中',
  }
  return map[status || ''] || status || '—'
}

function settlementStatusTagType(
  status: string | undefined,
): 'success' | 'warning' | 'info' | 'danger' {
  switch (status) {
    case 'GENERATED':
    case 'SETTLED':
    case 'COMPLETE':
    case 'CLOSED':
      return 'success'
    case 'CANCELLED':
    case 'VOID':
      return 'danger'
    case 'DRAFT':
    case 'OPEN':
    case 'CREATED':
    case 'PENDING':
      return 'warning'
    default:
      return 'info'
  }
}

function lineStatusLabel(status: string | undefined): string {
  const map: Record<string, string> = {
    PENDING: '待处理',
    GENERATED: '已生成',
    SETTLED: '已结算',
    COMPLETE: '已完成',
    CLOSED: '已关闭',
    CANCELLED: '已取消',
    VOID: '已作废',
    OPEN: '进行中',
  }
  return map[status || ''] || status || '—'
}

function lineStatusTagType(status: string | undefined): 'success' | 'warning' | 'info' | 'danger' {
  switch (status) {
    case 'SETTLED':
    case 'GENERATED':
    case 'COMPLETE':
    case 'CLOSED':
      return 'success'
    case 'PENDING':
      return 'warning'
    case 'CANCELLED':
    case 'VOID':
      return 'danger'
    default:
      return 'info'
  }
}

function completionLabel(done: boolean | undefined): string {
  return done ? '已完成' : '未完成'
}

function settleableLabel(settleable: boolean | undefined): string {
  return settleable ? '可结算' : '不可结算'
}

function completionTagType(done: boolean | undefined): 'success' | 'info' {
  return done ? 'success' : 'info'
}

function buildCreatePayload(): CommissionSettlementCreatePayload {
  return {
    agent_id: createForm.agent_id.trim(),
    currency: createForm.currency.trim(),
    period_from: createForm.period_range[0] || undefined,
    period_to: createForm.period_range[1] || undefined,
    remark: normalizeOptional(createForm.remark),
  }
}

function buildReportParams(): CommissionSettlementReportParams {
  return {
    agent_id: normalizeOptional(reportFilters.agent_id),
    case_id: normalizeOptional(reportFilters.case_id),
    currency: normalizeOptional(reportFilters.currency),
    settlement_status: normalizeOptional(reportFilters.settlement_status),
    line_status: normalizeOptional(reportFilters.line_status),
    date_from: reportFilters.date_range[0] || undefined,
    date_to: reportFilters.date_range[1] || undefined,
    time_field: reportFilters.time_field,
  }
}

function buildGenerateParams(): CommissionSettlementGenerateLinesParams {
  return {
    case_id: normalizeOptional(generateForm.case_id),
  }
}

function downloadBlob(blob: Blob, fileName: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

function useSettlement(id: number) {
  generateForm.settlement_id = id
}

function useReportTargetForGeneration() {
  generateForm.case_id = reportTargetCaseNumber.value
  handleGenerateLines()
}

async function handleCreateSettlement() {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return

  creating.value = true
  error.value = null
  try {
    const settlement = await createCommissionSettlement(buildCreatePayload())
    recentSettlements.value = [settlement, ...recentSettlements.value.filter((s) => s.id !== settlement.id)]
    generateForm.settlement_id = settlement.id
    ElMessage.success(`批次创建成功（编号: ${settlement.id}）`)
  } catch (err) {
    error.value = toApiError(err)
    ElMessage.error(mapCreateSettlementError(err))
  } finally {
    creating.value = false
  }
}

async function handleGenerateLines() {
  if (!generateForm.settlement_id) {
    ElMessage.warning('请先输入结算批次编号')
    return
  }

  generating.value = true
  error.value = null
  try {
    const targetCaseNumber = normalizeOptional(generateForm.case_id) || ''
    const result = await generateCommissionSettlementLines(generateForm.settlement_id, buildGenerateParams())
    lastGenerate.value = result
    lastGenerateCaseNumber.value = targetCaseNumber

    const index = recentSettlements.value.findIndex((s) => s.id === result.settlement_id)
    if (index >= 0) {
      recentSettlements.value[index] = {
        ...recentSettlements.value[index],
        line_count: result.line_count,
        total_amount: result.total_amount,
        status: result.status,
      }
    }

    ElMessage.success(targetCaseNumber ? `目标案件号 ${targetCaseNumber} 的明细生成成功` : '明细生成成功')
  } catch (err) {
    error.value = toApiError(err)
    ElMessage.error(mapGenerateLinesError(err))
  } finally {
    generating.value = false
  }
}

async function queryReport() {
  reportLoading.value = true
  error.value = null
  const targetCaseNumber = normalizeOptional(reportFilters.case_id) || ''
  try {
    report.value = await getCommissionSettlementReport(buildReportParams())
    lastReportCaseNumber.value = targetCaseNumber
    if (targetCaseNumber && !generateForm.case_id) {
      generateForm.case_id = targetCaseNumber
    }
  } catch (err) {
    error.value = toApiError(err)
    ElMessage.error(mapReportError(err))
  } finally {
    reportLoading.value = false
  }
}

async function handleExportReport() {
  exporting.value = true
  try {
    const blob = await exportCommissionSettlementReport(buildReportParams())
    downloadBlob(blob, '提成结算报表.xlsx')
    ElMessage.success('提成结算报表已开始导出。')
  } catch (err) {
    error.value = toApiError(err)
    ElMessage.error(mapReportError(err))
  } finally {
    exporting.value = false
  }
}

function resetReportFilters() {
  reportFilters.agent_id = ''
  reportFilters.case_id = ''
  reportFilters.currency = ''
  reportFilters.settlement_status = ''
  reportFilters.line_status = ''
  reportFilters.date_range = []
  reportFilters.time_field = 'line_created_at'
  lastReportCaseNumber.value = ''
  queryReport()
}

onMounted(() => {
  queryReport()
})
</script>

<style scoped>
.section-card {
  margin-top: 16px;
}

.section-title {
  font-weight: 600;
}

.action-row {
  display: flex;
  justify-content: flex-end;
}

.generate-row {
  align-items: center;
}

.generate-guide {
  margin-top: 12px;
}

.result-block {
  margin-top: 16px;
}

.result-alert {
  margin-top: 12px;
}

.sub-title {
  margin-bottom: 8px;
  font-weight: 600;
}

.filter-bar {
  margin-bottom: 16px;
}

.guide-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
}

.guide-note {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.stat-grid {
  margin-bottom: 16px;
}

.stat-card {
  min-height: 96px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-sub);
}

.stat-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 700;
}

.stat-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-sub);
}

.report-hint {
  margin-bottom: 16px;
  color: var(--text-sub);
}

.table-section {
  margin-top: 16px;
}

.mono-num {
  font-family: var(--font-mono);
}

.w-full {
  width: 100%;
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
