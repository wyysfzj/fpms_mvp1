<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">案件批件递交</h1>
        <span class="page-count">{{ total }} 条候选案件</span>
      </div>
      <div class="page-header-right">
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          执行递交
        </el-button>
      </div>
    </div>

    <el-card class="filter-panel" shadow="never">
      <el-form :model="filters" label-position="top">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="案件类型">
              <el-select v-model="filters.case_type" clearable class="full-width" placeholder="全部">
                <el-option label="普通申请" value="NORMAL" />
                <el-option label="PCT国际" value="PCT_INTL" />
                <el-option label="PCT国内" value="PCT_NATL" />
                <el-option label="优先权" value="PRIORITY" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="流程方向">
              <el-select v-model="filters.flow_dir" clearable class="full-width" placeholder="全部">
                <el-option label="国内" value="CN_DOMESTIC" />
                <el-option label="出境" value="CN_OUTBOUND" />
                <el-option label="入境" value="FOREIGN_INBOUND" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="法律状态">
              <el-select v-model="filters.status" class="full-width" placeholder="未递交">
                <el-option label="未递交" value="NOT_FILED" />
                <el-option label="待受理" value="WAITING_RECEIPT" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="专利类别">
              <el-select v-model="filters.patent_category" clearable class="full-width" placeholder="全部">
                <el-option label="发明" value="INV" />
                <el-option label="实用新型" value="UM" />
                <el-option label="外观设计" value="DES" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="收文日范围">
              <el-date-picker
                v-model="recvDateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                class="full-width"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="客户">
              <el-select v-model="filters.client_id" clearable filterable class="full-width" placeholder="全部客户">
                <el-option
                  v-for="client in clients"
                  :key="client.id"
                  :label="client.name"
                  :value="client.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="主办代理人">
              <el-input v-model.trim="filters.primary_agent_id" placeholder="请输入代理人ID" />
            </el-form-item>
          </el-col>
          <el-col :span="6" class="filter-actions">
            <el-button type="primary" :loading="loading" @click="fetchCandidates">查询案件</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="action-panel" shadow="never">
      <div class="action-panel-header">
        <h3>批处理参数</h3>
        <div class="selection-summary">已选 {{ selectedIds.length }} 件</div>
      </div>
      <el-form :model="actionForm" inline>
        <el-form-item label="递交日" required>
          <el-date-picker
            v-model="actionForm.submitted_date"
            type="date"
            placeholder="请选择递交日"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="立即提实审">
          <el-switch v-model="actionForm.apply_exam_now" />
        </el-form-item>
      </el-form>
      <el-alert
        title="第一版不生成递交清单文档，也不自动生成申请费时限任务。"
        type="info"
        :closable="false"
        show-icon
      />
      <div class="final-material-gate-strip">
        <div>
          <span class="gate-strip-label">最终材料门禁</span>
          <strong>递交前检查最终稿、签章件和客户确认记录</strong>
        </div>
        <div class="gate-strip-tags">
          <el-tag :type="hardBlockCount ? 'danger' : 'success'" size="small">
            硬阻止：{{ hardBlockCount }} 件
          </el-tag>
          <el-tag :type="afterfillAuditCount ? 'warning' : 'info'" size="small">
            后补审计：{{ afterfillAuditCount }} 件
          </el-tag>
        </div>
      </div>
    </el-card>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <div v-else class="page-table">
      <el-table :data="candidates" stripe size="small" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" :selectable="isCandidateSelectable" />
        <el-table-column prop="case_no" label="案号" width="160" />
        <el-table-column prop="title_cn" label="标题" min-width="220" />
        <el-table-column prop="client_name" label="客户" min-width="180" />
        <el-table-column prop="case_type" label="案件类型" width="120" />
        <el-table-column prop="patent_category" label="专利类别" width="100" />
        <el-table-column prop="flow_dir" label="流程方向" width="130" />
        <el-table-column prop="recv_date" label="收文日" width="120" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column label="最终材料" width="100">
          <template #default="{ row }">
            {{ getFinalMaterialGate(row).count }}
          </template>
        </el-table-column>
        <el-table-column label="缺失项" min-width="130">
          <template #default="{ row }">
            {{ getFinalMaterialGate(row).missing }}
          </template>
        </el-table-column>
        <el-table-column label="门禁结论" width="120">
          <template #default="{ row }">
            <el-tag :type="getFinalMaterialGate(row).tagType" size="small">
              {{ getFinalMaterialGate(row).conclusion }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理" width="120">
          <template #default="{ row }">
            {{ getFinalMaterialGate(row).action }}
          </template>
        </el-table-column>
        <el-table-column label="已提实审" width="100">
          <template #default="{ row }">
            {{ row.has_exam_request ? '是' : '否' }}
          </template>
        </el-table-column>
      </el-table>

      <el-alert
        v-if="hardBlockCount"
        class="final-material-hard-block"
        title="硬阻止"
        :description="hardBlockDescription"
        type="error"
        :closable="false"
        show-icon
      />

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        @change="fetchCandidates"
      />
    </div>

    <div class="batch-gate-preview-grid">
      <el-card shadow="never">
        <template #header>
          <span>后补审计</span>
        </template>
        <el-empty v-if="!afterfillAuditRows.length" description="当前没有后补审计项" :image-size="72" />
        <el-table v-else :data="afterfillAuditRows" size="small">
          <el-table-column prop="case_no" label="案号" min-width="130" />
          <el-table-column prop="items" label="后补项" min-width="160" />
          <el-table-column prop="conclusion" label="门禁结论" min-width="110" />
        </el-table>
      </el-card>

      <el-card shadow="never">
        <template #header>
          <span>执行预览</span>
        </template>
        <el-empty v-if="!executionPreviewItems.length" description="暂无执行预览" :image-size="72" />
        <ul v-else class="execution-preview-list">
          <li
            v-for="item in executionPreviewItems"
            :key="`${item.case_no}-${item.kind}-${item.label}`"
            :class="{ 'execution-preview-danger': !item.enabled }"
          >
            {{ item.case_no }}：{{ item.label }}{{ item.detail ? `，${item.detail}` : '' }}
          </li>
        </ul>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { getBatchFilingCandidates, submitBatchFiling } from '../../../api/cases'
import { getClients } from '../../../api/clients'
import type {
  CaseBatchFilingCandidate,
  CaseBatchFilingQueryParams,
} from '../../../api/cases.types'
import type { Client } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const candidates = ref<CaseBatchFilingCandidate[]>([])
const clients = ref<Client[]>([])
const loading = ref(false)
const submitting = ref(false)
const error = ref<ApiError | null>(null)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedIds = ref<string[]>([])

type GateTagType = 'success' | 'warning' | 'danger' | 'info'

const filters = reactive<CaseBatchFilingQueryParams>({
  case_type: '',
  flow_dir: '',
  status: 'NOT_FILED',
  recv_date_from: '',
  recv_date_to: '',
  client_id: '',
  primary_agent_id: '',
  patent_category: '',
})

const actionForm = reactive({
  submitted_date: '',
  apply_exam_now: false,
})

const recvDateRange = computed({
  get: () => {
    if (filters.recv_date_from && filters.recv_date_to) {
      return [filters.recv_date_from, filters.recv_date_to]
    }
    return []
  },
  set: (value: string[] | undefined) => {
    filters.recv_date_from = value?.[0] || ''
    filters.recv_date_to = value?.[1] || ''
  },
})

const selectedCandidates = computed(() => {
  const selected = new Set(selectedIds.value)
  return candidates.value.filter((candidate) => selected.has(candidate.id))
})
const previewCandidates = computed(() => selectedCandidates.value.length ? selectedCandidates.value : candidates.value)
const hardBlockCount = computed(() =>
  candidates.value.filter((candidate) => candidate.final_material_gate?.hard_block).length
)
const afterfillAuditCount = computed(() =>
  candidates.value.filter((candidate) => candidate.final_material_gate?.afterfill_audit_required).length
)
const hardBlockDescription = computed(() => {
  const blockedRows = candidates.value.filter((candidate) => candidate.final_material_gate?.hard_block)
  const caseNos = blockedRows.map((candidate) => candidate.case_no).join('、')
  const missingItems = Array.from(new Set(
    blockedRows.flatMap((candidate) =>
      candidate.final_material_gate?.missing_items
        .filter((item) => item.blocks_submission)
        .map((item) => item.requirement_name) || []
    )
  )).join('、')
  return `以下案件不会进入本次递交事务：${caseNos || '无'}；硬性缺失项：${missingItems || '无'}。`
})
const afterfillAuditRows = computed(() =>
  previewCandidates.value
    .filter((candidate) => candidate.final_material_gate?.afterfill_audit_required)
    .map((candidate) => ({
      case_no: candidate.case_no,
      items: getMissingMaterialText(candidate, true),
      conclusion: getConclusionText(candidate.final_material_gate?.conclusion),
    }))
)
const executionPreviewItems = computed(() =>
  previewCandidates.value.flatMap((candidate) =>
    (candidate.final_material_gate?.execution_preview || []).map((item) => ({
      case_no: candidate.case_no,
      kind: item.kind,
      label: item.label,
      enabled: item.enabled,
      detail: item.detail,
    }))
  )
)

function getFinalMaterialGate(row: CaseBatchFilingCandidate) {
  const gate = row.final_material_gate
  if (!gate) {
    return {
      count: '-',
      missing: '暂无门禁数据',
      conclusion: '未核验',
      tagType: 'info' as GateTagType,
      action: '等待核验',
    } as const
  }

  return {
    count: `${gate.material_count} 项`,
    missing: getMissingMaterialText(row),
    conclusion: getConclusionText(gate.conclusion, gate.hard_block),
    tagType: getConclusionTagType(gate.conclusion, gate.hard_block),
    action: getGateAction(row),
  } as const
}

function getMissingMaterialText(row: CaseBatchFilingCandidate, afterfillOnly = false) {
  const items = row.final_material_gate?.missing_items || []
  const filtered = afterfillOnly ? items.filter((item) => item.afterfill_allowed) : items
  return filtered.length ? filtered.map((item) => item.requirement_name).join('、') : '无'
}

function getConclusionText(conclusion?: string, hardBlock = false) {
  if (hardBlock || conclusion === 'BLOCKED') return '硬阻止'
  if (conclusion === 'WARNING') return '允许后补'
  if (conclusion === 'PASS') return '可递交'
  return '未核验'
}

function getConclusionTagType(conclusion?: string, hardBlock = false): GateTagType {
  if (hardBlock || conclusion === 'BLOCKED') return 'danger'
  if (conclusion === 'WARNING') return 'warning'
  if (conclusion === 'PASS') return 'success'
  return 'info'
}

function getGateAction(row: CaseBatchFilingCandidate) {
  const gate = row.final_material_gate
  if (!gate) return '等待核验'
  if (gate.hard_block) return '补齐材料'
  if (gate.afterfill_audit_required) return '填写后补审计'
  return '查看材料'
}

function isCandidateSelectable(row: CaseBatchFilingCandidate) {
  return Boolean(row.final_material_gate && !row.final_material_gate.hard_block)
}

function normalizeSubmitError(apiError: ApiError) {
  if (apiError.code === 'CASE_BATCH_FILING_MATERIAL_GATE_BLOCKED') {
    const caseNos = Array.isArray(apiError.details?.case_nos)
      ? apiError.details.case_nos.map((item) => String(item)).join('、')
      : ''
    return caseNos
      ? `存在硬阻止案件，后端已拒绝递交：${caseNos}。`
      : '存在硬阻止案件，后端已拒绝递交。'
  }
  return apiError.message || '递交失败，请稍后重试。'
}

async function fetchClients() {
  const response = await getClients({ page: 1, page_size: 200 })
  clients.value = response.items
}

async function fetchCandidates() {
  loading.value = true
  error.value = null
  try {
    const response = await getBatchFilingCandidates({
      ...filters,
      page: page.value,
      page_size: pageSize.value,
    })
    candidates.value = response.items
    total.value = response.total
    selectedIds.value = []
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.case_type = ''
  filters.flow_dir = ''
  filters.status = 'NOT_FILED'
  filters.recv_date_from = ''
  filters.recv_date_to = ''
  filters.client_id = ''
  filters.primary_agent_id = ''
  filters.patent_category = ''
  page.value = 1
  fetchCandidates()
}

function handleSelectionChange(rows: CaseBatchFilingCandidate[]) {
  selectedIds.value = rows.filter(isCandidateSelectable).map((row) => row.id)
}

async function handleSubmit() {
  if (!selectedIds.value.length) {
    ElMessage.error('请先勾选至少一件案件。')
    return
  }
  if (!actionForm.submitted_date) {
    ElMessage.error('请选择递交日。')
    return
  }
  const blockedRows = selectedCandidates.value.filter((candidate) => candidate.final_material_gate?.hard_block)
  if (blockedRows.length) {
    ElMessage.error(`存在硬阻止案件，请先补齐材料：${blockedRows.map((row) => row.case_no).join('、')}。`)
    return
  }

  submitting.value = true
  error.value = null
  try {
    const result = await submitBatchFiling({
      selected_case_ids: selectedIds.value,
      submitted_date: actionForm.submitted_date,
      apply_exam_now: actionForm.apply_exam_now,
      generate_list: false,
    })
    ElMessage.success(`递交完成：成功更新 ${result.success_count} 件案件。`)
    await fetchCandidates()
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError
    ElMessage.error(normalizeSubmitError(apiError))
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await fetchClients()
  await fetchCandidates()
})
</script>

<style scoped>
.filter-panel,
.action-panel {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  align-items: end;
}

.full-width {
  width: 100%;
}

.action-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.selection-summary {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.final-material-gate-strip {
  align-items: center;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 14px;
  padding: 12px 14px;
}

.final-material-gate-strip div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.gate-strip-label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.gate-strip-tags {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.final-material-hard-block {
  margin-top: 14px;
}

.batch-gate-preview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.execution-preview-list {
  color: var(--el-text-color-regular);
  display: flex;
  flex-direction: column;
  gap: 8px;
  line-height: 1.6;
  margin: 0;
  padding-left: 18px;
}

.execution-preview-danger {
  color: var(--el-color-danger);
  font-weight: 600;
}

@media (max-width: 1100px) {
  .final-material-gate-strip {
    align-items: flex-start;
    flex-direction: column;
  }

  .gate-strip-tags {
    justify-content: flex-start;
  }

  .batch-gate-preview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
