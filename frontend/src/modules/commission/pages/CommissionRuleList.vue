<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">提成规则管理</h1>
        <span class="page-count" aria-live="polite">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" aria-label="新增提成规则" @click="openCreate">新增规则</el-button>
      </div>
    </div>

    <el-row :gutter="12" class="filter-bar">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-input
          v-model.trim="filters.q"
          aria-label="规则关键词筛选"
          placeholder="按规则名称或备注搜索"
          clearable
          @keyup.enter="onFilterChange"
        />
      </el-col>
      <el-col :xs="12" :sm="6" :md="4" :lg="3">
        <el-select v-model="filters.enabled" aria-label="规则状态筛选" placeholder="状态" clearable>
          <el-option label="全部状态" value="" />
          <el-option label="启用" value="true" />
          <el-option label="停用" value="false" />
        </el-select>
      </el-col>
      <el-col :xs="12" :sm="6" :md="4" :lg="3">
        <el-input v-model.trim="filters.case_type" aria-label="案件类型筛选" placeholder="案件类型" clearable @keyup.enter="onFilterChange" />
      </el-col>
      <el-col :xs="12" :sm="6" :md="4" :lg="3">
        <el-input v-model.trim="filters.fee_type" aria-label="费用类型筛选" placeholder="费用类型" clearable @keyup.enter="onFilterChange" />
      </el-col>
      <el-col :xs="24" :sm="12" :md="4" :lg="3" class="filter-actions">
        <el-button type="primary" aria-label="查询提成规则" @click="onFilterChange">查询</el-button>
        <el-button aria-label="重置提成规则筛选" @click="resetFilters">重置</el-button>
      </el-col>
    </el-row>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="10" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无提成规则"
        message="可点击“新增规则”创建第一条提成规则。"
        icon="📘"
        cta-label="新增规则"
        @cta="openCreate"
      />
    </div>

    <div v-else class="page-table">
      <el-table :data="rules" aria-label="提成规则列表" stripe size="small" class="compact-table">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="rule_name" label="规则名称" min-width="180" />
        <el-table-column prop="case_type" label="案件类型" min-width="120">
          <template #default="{ row }">
            {{ getCaseTypeText(row.case_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="fee_type" label="费用类型" min-width="120">
          <template #default="{ row }">
            {{ getFeeTypeText(row.fee_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="s1_rate" label="S1 比例" width="110" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatPercent(row.s1_rate) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="s2_rate" label="S2 比例" width="110" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatPercent(row.s2_rate) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="wait_pay" label="待回款" width="100">
          <template #default="{ row }">
            <el-tag :type="row.wait_pay ? 'warning' : 'info'" size="small">
              {{ row.wait_pay ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="force_settle" label="强制结算" width="100">
          <template #default="{ row }">
            <el-tag :type="row.force_settle ? 'success' : 'info'" size="small">
              {{ row.force_settle ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生效区间" min-width="190">
          <template #default="{ row }">
            <span v-if="row.effective_from || row.effective_to">
              {{ row.effective_from || '—' }} ~ {{ row.effective_to || '—' }}
            </span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click="openEdit(row)">编辑</el-button>
            <el-button
              text
              size="small"
              :loading="togglingRuleId === row.id"
              :type="row.enabled ? 'warning' : 'success'"
              @click="toggleEnabled(row)"
            >
              {{ row.enabled ? '停用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑提成规则' : '新增提成规则'"
      width="760px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="规则名称" prop="rule_name">
              <el-input v-model.trim="form.rule_name" placeholder="请输入规则名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch v-model="form.enabled" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="案件类型">
              <el-input v-model.trim="form.case_type" placeholder="例如：NORMAL" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="费用类型">
              <el-input v-model.trim="form.fee_type" placeholder="例如：SERVICE" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="流程方向">
              <el-input v-model.trim="form.flow_dir" placeholder="例如：INBOUND" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="专利类别">
              <el-input v-model.trim="form.patent_category" placeholder="例如：INV" />
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="S1 比例" prop="s1_rate">
              <el-input-number v-model="form.s1_rate" :min="0" :precision="4" :step="0.01" controls-position="right" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="S2 比例" prop="s2_rate">
              <el-input-number v-model="form.s2_rate" :min="0" :precision="4" :step="0.01" controls-position="right" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="S1 固定金额">
              <el-input-number v-model="form.s1_fixed_amount" :min="0" :precision="2" :step="10" controls-position="right" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="S2 固定金额">
              <el-input-number v-model="form.s2_fixed_amount" :min="0" :precision="2" :step="10" controls-position="right" class="w-full" />
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="待回款">
              <el-switch v-model="form.wait_pay" active-text="是" inactive-text="否" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="强制结算">
              <el-switch v-model="form.force_settle" active-text="是" inactive-text="否" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="生效开始">
              <el-date-picker
                v-model="form.effective_from"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                class="w-full"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="生效结束">
              <el-date-picker
                v-model="form.effective_to"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                class="w-full"
              />
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="可选备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import {
  createCommissionRule,
  getCommissionRules,
  updateCommissionRule,
} from '../../../api/commission'
import type {
  CommissionRule,
  CommissionRuleCreatePayload,
  CommissionRuleUpdatePayload,
} from '../../../api/commission.types'
import type { ApiError } from '../../../api/types'
import { getCaseTypeText, getFeeTypeText } from '../../../constants/displayText'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const rules = ref<CommissionRule[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

const filters = reactive({
  q: '',
  enabled: '',
  case_type: '',
  fee_type: '',
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingRuleId = ref<number | null>(null)
const togglingRuleId = ref<number | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  rule_name: '',
  case_type: '',
  fee_type: '',
  flow_dir: '',
  patent_category: '',
  s1_rate: 0,
  s2_rate: 0,
  s1_fixed_amount: 0,
  s2_fixed_amount: 0,
  wait_pay: false,
  force_settle: false,
  enabled: true,
  effective_from: '',
  effective_to: '',
  remark: '',
})

const formRules: FormRules = {
  rule_name: [{ required: true, message: '规则名称为必填项', trigger: 'blur' }],
  s1_rate: [{ required: true, message: 'S1 比例为必填项', trigger: 'blur' }],
  s2_rate: [{ required: true, message: 'S2 比例为必填项', trigger: 'blur' }],
}

function normalizeOptional(value: string): string | undefined {
  const trimmed = value.trim()
  return trimmed || undefined
}

function buildFilterParams() {
  return {
    q: normalizeOptional(filters.q),
    case_type: normalizeOptional(filters.case_type),
    fee_type: normalizeOptional(filters.fee_type),
    enabled: filters.enabled === '' ? undefined : filters.enabled === 'true',
    page: page.value,
    page_size: pageSize.value,
  }
}

async function fetchRules() {
  loading.value = true
  error.value = null
  try {
    const result = await getCommissionRules(buildFilterParams())
    rules.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  fetchRules()
}

function resetFilters() {
  filters.q = ''
  filters.enabled = ''
  filters.case_type = ''
  filters.fee_type = ''
  onFilterChange()
}

function resetForm() {
  form.rule_name = ''
  form.case_type = ''
  form.fee_type = ''
  form.flow_dir = ''
  form.patent_category = ''
  form.s1_rate = 0
  form.s2_rate = 0
  form.s1_fixed_amount = 0
  form.s2_fixed_amount = 0
  form.wait_pay = false
  form.force_settle = false
  form.enabled = true
  form.effective_from = ''
  form.effective_to = ''
  form.remark = ''
}

function openCreate() {
  resetForm()
  isEdit.value = false
  editingRuleId.value = null
  dialogVisible.value = true
}

function openEdit(rule: CommissionRule) {
  form.rule_name = rule.rule_name
  form.case_type = rule.case_type || ''
  form.fee_type = rule.fee_type || ''
  form.flow_dir = rule.flow_dir || ''
  form.patent_category = rule.patent_category || ''
  form.s1_rate = rule.s1_rate
  form.s2_rate = rule.s2_rate
  form.s1_fixed_amount = rule.s1_fixed_amount
  form.s2_fixed_amount = rule.s2_fixed_amount
  form.wait_pay = rule.wait_pay
  form.force_settle = rule.force_settle
  form.enabled = rule.enabled
  form.effective_from = rule.effective_from || ''
  form.effective_to = rule.effective_to || ''
  form.remark = rule.remark || ''
  isEdit.value = true
  editingRuleId.value = rule.id
  dialogVisible.value = true
}

function buildCreatePayload(): CommissionRuleCreatePayload {
  return {
    rule_name: form.rule_name.trim(),
    case_type: normalizeOptional(form.case_type),
    fee_type: normalizeOptional(form.fee_type),
    flow_dir: normalizeOptional(form.flow_dir),
    patent_category: normalizeOptional(form.patent_category),
    s1_rate: form.s1_rate,
    s2_rate: form.s2_rate,
    s1_fixed_amount: form.s1_fixed_amount,
    s2_fixed_amount: form.s2_fixed_amount,
    wait_pay: form.wait_pay,
    force_settle: form.force_settle,
    enabled: form.enabled,
    effective_from: normalizeOptional(form.effective_from),
    effective_to: normalizeOptional(form.effective_to),
    remark: normalizeOptional(form.remark),
  }
}

function buildUpdatePayload(): CommissionRuleUpdatePayload {
  return {
    rule_name: form.rule_name.trim(),
    case_type: normalizeOptional(form.case_type),
    fee_type: normalizeOptional(form.fee_type),
    flow_dir: normalizeOptional(form.flow_dir),
    patent_category: normalizeOptional(form.patent_category),
    s1_rate: form.s1_rate,
    s2_rate: form.s2_rate,
    s1_fixed_amount: form.s1_fixed_amount,
    s2_fixed_amount: form.s2_fixed_amount,
    wait_pay: form.wait_pay,
    force_settle: form.force_settle,
    enabled: form.enabled,
    effective_from: normalizeOptional(form.effective_from),
    effective_to: normalizeOptional(form.effective_to),
    remark: normalizeOptional(form.remark),
  }
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value && editingRuleId.value !== null) {
      await updateCommissionRule(editingRuleId.value, buildUpdatePayload())
      ElMessage.success('规则更新成功')
    } else {
      await createCommissionRule(buildCreatePayload())
      ElMessage.success('规则创建成功')
    }

    dialogVisible.value = false
    await fetchRules()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(apiError.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function toggleEnabled(rule: CommissionRule) {
  togglingRuleId.value = rule.id
  try {
    await updateCommissionRule(rule.id, { enabled: !rule.enabled })
    ElMessage.success(rule.enabled ? '规则已停用' : '规则已启用')
    await fetchRules()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(apiError.message || '状态更新失败')
  } finally {
    togglingRuleId.value = null
  }
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`
}

watch([page, pageSize], () => {
  fetchRules()
})

onMounted(() => {
  fetchRules()
})
</script>

<style scoped>
.filter-bar {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  gap: 8px;
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
