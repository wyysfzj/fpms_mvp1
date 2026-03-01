<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">官费清单</h1>
        <span class="page-count">生成与状态查询</span>
      </div>
      <div class="page-header-right">
        <el-button @click="goToGovPaymentCreate()">去登记缴费</el-button>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div class="form-card">
      <h2 class="form-card-title">清单生成条件</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="pay-list-form">
        <el-form-item
          label="费用项编号"
          prop="fee_item_ids"
          :error="fieldErrors.get('fee_item_ids')?.join('，')"
        >
          <el-input
            v-model="form.fee_item_ids"
            type="textarea"
            :rows="4"
            placeholder="请输入费用项编号，支持逗号、空格或换行分隔"
          />
          <div class="field-hint">示例：`fee-item-001, fee-item-002`</div>
        </el-form-item>

        <el-row :gutter="12">
          <el-col :xs="24" :sm="12">
            <el-form-item label="计划缴费日期" prop="planned_pay_date">
              <el-date-picker
                v-model="form.planned_pay_date"
                type="date"
                placeholder="请选择日期（可选）"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="备注" prop="remark">
              <el-input
                v-model.trim="form.remark"
                placeholder="可填写本次清单说明（可选）"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-actions">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :loading="generating" @click="handleGenerate">
            生成官费清单
          </el-button>
        </div>
      </el-form>
    </div>

    <div v-if="result" class="result-card">
      <h2 class="form-card-title">生成回执</h2>

      <el-descriptions :column="4" border>
        <el-descriptions-item label="请求数量">{{ result.summary.requested }}</el-descriptions-item>
        <el-descriptions-item label="成功数量">{{ result.summary.success }}</el-descriptions-item>
        <el-descriptions-item label="失败数量">{{ result.summary.failed }}</el-descriptions-item>
        <el-descriptions-item label="已生成清单">
          {{ result.summary.pay_list_created ? '是' : '否' }}
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="result.pay_list" class="pay-list-info">
        <h3 class="section-title">清单状态</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="清单编号">
            {{ result.pay_list.pay_list_no || `#${result.pay_list.id}` }}
          </el-descriptions-item>
          <el-descriptions-item label="客户ID">{{ result.pay_list.client_id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="payListStatusTag(result.pay_list.status)">
              {{ payListStatusText(result.pay_list.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="币种">{{ result.pay_list.currency }}</el-descriptions-item>
          <el-descriptions-item label="计划缴费日期">
            {{ result.pay_list.planned_pay_date || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="清单金额">
            {{ formatMoney(result.pay_list.total_amount, result.pay_list.currency) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-if="result.success.length > 0" class="receipt-section">
        <h3 class="section-title">成功明细</h3>
        <el-table :data="result.success" size="small" border>
          <el-table-column prop="fee_item_id" label="费用项ID" min-width="200" />
          <el-table-column prop="case_id" label="案件ID" min-width="180" />
          <el-table-column label="金额" width="150" align="right">
            <template #default="{ row }">
              {{ formatMoney(row.amount, row.currency) }}
            </template>
          </el-table-column>
          <el-table-column prop="pay_list_id" label="清单ID" width="100" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button text type="primary" @click="goToGovPaymentCreate(row.fee_item_id, row.pay_list_id)">
                登记缴费
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="result.failed.length > 0" class="receipt-section">
        <h3 class="section-title">失败明细</h3>
        <el-table :data="result.failed" size="small" border>
          <el-table-column prop="fee_item_id" label="费用项ID" min-width="200" />
          <el-table-column prop="code" label="错误码" min-width="180" />
          <el-table-column prop="status_code" label="状态码" width="100" />
          <el-table-column label="失败说明" min-width="240">
            <template #default="{ row }">
              {{ formatFailedMessage(row.message) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { createPayListFromFeeItems, mapGovPaymentsError } from '../../../api/govPayments'
import type { GovPaymentsApiError, PayListCreateResult } from '../../../api/govPayments.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

interface PayListForm {
  fee_item_ids: string
  planned_pay_date: string
  remark: string
}

const router = useRouter()

const formRef = ref<FormInstance>()
const generating = ref(false)
const error = ref<GovPaymentsApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const result = ref<PayListCreateResult | null>(null)

const form = reactive<PayListForm>({
  fee_item_ids: '',
  planned_pay_date: '',
  remark: '',
})

const rules: FormRules<PayListForm> = {
  fee_item_ids: [
    { required: true, message: '费用项编号为必填项', trigger: 'blur' },
  ],
}

function normalizeFeeItemIds(raw: string): string[] {
  const values = raw
    .split(/[\s,，;；\n]+/g)
    .map((item) => item.trim())
    .filter(Boolean)
  return Array.from(new Set(values))
}

function payListStatusText(status: string): string {
  switch (status?.toUpperCase()) {
    case 'DRAFT':
      return '草稿'
    case 'PARTIAL':
      return '部分完成'
    case 'PAID':
      return '已完成'
    default:
      return status || '未知'
  }
}

function payListStatusTag(status: string): 'info' | 'warning' | 'success' {
  switch (status?.toUpperCase()) {
    case 'PAID':
      return 'success'
    case 'PARTIAL':
      return 'warning'
    default:
      return 'info'
  }
}

function formatMoney(amount: number, currency: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(amount || 0)
}

function formatFailedMessage(message?: string): string {
  return message ? `后端信息：${message}` : '后端信息：无'
}

function goToGovPaymentCreate(feeItemId?: string, payListId?: number) {
  router.push({
    path: '/annuity/gov-payments/new',
    query: {
      ...(payListId ? { pay_list_id: String(payListId) } : {}),
      ...(feeItemId ? { fee_item_id: feeItemId } : {}),
    },
  })
}

function resetForm() {
  form.fee_item_ids = ''
  form.planned_pay_date = ''
  form.remark = ''
  fieldErrors.value = new Map()
  error.value = null
}

async function handleGenerate() {
  fieldErrors.value = new Map()
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  const feeItemIds = normalizeFeeItemIds(form.fee_item_ids)
  if (feeItemIds.length === 0) {
    ElMessage.warning('请至少输入一个费用项编号。')
    return
  }

  generating.value = true
  error.value = null
  try {
    const response = await createPayListFromFeeItems({
      fee_item_ids: feeItemIds,
      planned_pay_date: form.planned_pay_date || undefined,
      remark: form.remark || undefined,
    })
    result.value = response

    if (response.summary.success > 0 && response.summary.failed > 0) {
      ElMessage.warning(`处理完成：成功 ${response.summary.success} 条，失败 ${response.summary.failed} 条。`)
    } else if (response.summary.success > 0) {
      ElMessage.success(`清单生成成功，共 ${response.summary.success} 条。`)
    } else {
      ElMessage.info('处理完成，未生成可用清单。')
    }
  } catch (err) {
    const mapped = mapGovPaymentsError(err)
    error.value = mapped
    if (mapped.field_errors && mapped.field_errors.size > 0) {
      fieldErrors.value = mapped.field_errors
    }
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.pay-list-form {
  max-width: 920px;
}

.field-hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-sub);
}

.result-card {
  margin-top: 20px;
}

.section-title {
  margin: 14px 0 8px;
  font-size: 14px;
  font-weight: 600;
}

.pay-list-info {
  margin-top: 14px;
}

.receipt-section {
  margin-top: 16px;
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
