<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回清单列表
        </el-button>
        <div>
          <h1 class="page-title">官费清单详情</h1>
          <span class="page-count">{{ payListTitle }}</span>
        </div>
      </div>
      <div class="page-header-right">
        <el-button @click="handleRefresh">刷新</el-button>
        <el-button
          text
          type="primary"
          :disabled="!payList"
          @click="goToFirstRegistrable"
        >
          去登记缴费
        </el-button>
        <el-button
          type="primary"
          :disabled="!canExport"
          :loading="exporting"
          @click="handleExport"
        >
          导出清单
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="10" animated />
    </div>

    <template v-else-if="detail">
      <el-row :gutter="16" class="detail-layout">
        <el-col :xs="24" :lg="16">
          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <span class="form-card-title">清单头信息</span>
              </div>
            </template>

            <el-descriptions :column="2" border>
              <el-descriptions-item label="清单编号">
                {{ formatPayListNo(detail.pay_list) }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="payListStatusTag(detail.pay_list.status)">
                  {{ payListStatusText(detail.pay_list.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="客户">
                {{ formatClientDisplay(detail.pay_list.client_id) }}
              </el-descriptions-item>
              <el-descriptions-item label="币种">
                {{ detail.pay_list.currency }}
              </el-descriptions-item>
              <el-descriptions-item label="计划缴费日期">
                {{ detail.pay_list.planned_pay_date || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="实际缴费日期">
                {{ detail.pay_list.paid_date || '—' }}
              </el-descriptions-item>
              <el-descriptions-item label="清单金额">
                {{ formatMoney(detail.pay_list.total_amount, detail.pay_list.currency) }}
              </el-descriptions-item>
              <el-descriptions-item label="更新时间">
                {{ formatDateTime(detail.pay_list.updated_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="备注" :span="2">
                {{ detail.pay_list.remark || '—' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>

          <el-card shadow="never" class="rows-card">
            <template #header>
              <div class="card-header">
                <span class="form-card-title">内部导出</span>
                <span class="page-count">
                  共 {{ detail.internal_artifacts?.length ?? 0 }} 个
                </span>
              </div>
            </template>

            <el-empty
              v-if="!detail.internal_artifacts?.length"
              description="当前没有内部导出产物"
            />

            <el-table
              v-else
              :data="detail.internal_artifacts"
              stripe
              size="small"
              class="compact-table"
            >
              <el-table-column prop="id" label="产物编号" min-width="180" />
              <el-table-column prop="status" label="产物状态" min-width="150" />
              <el-table-column prop="content_sha256" label="内容摘要" min-width="220" />
              <el-table-column label="生成时间" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.generated_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-card shadow="never" class="rows-card">
            <template #header>
              <div class="card-header">
                <span class="form-card-title">官方工作簿</span>
              </div>
            </template>

            <el-descriptions v-if="detail.official_workbook" :column="2" border>
              <el-descriptions-item label="模板门禁状态">
                {{ detail.official_workbook.official_upload_template_status || '待确认' }}
              </el-descriptions-item>
              <el-descriptions-item label="模板名称">
                {{ detail.official_workbook.official_upload_template_name || '待确认' }}
              </el-descriptions-item>
              <el-descriptions-item label="单批上限">
                {{ detail.official_workbook.official_upload_batch_limit ?? '待确认' }}
              </el-descriptions-item>
              <el-descriptions-item label="边界说明">
                {{ detail.official_workbook.official_pay_list_boundary_note || '—' }}
              </el-descriptions-item>
            </el-descriptions>

            <el-alert
              v-else
              title="官方工作簿门禁尚未开放"
              type="warning"
              :closable="false"
              description="仅显示服务端返回的官方工作簿事实，不依据清单头状态推断。"
            />
          </el-card>

          <el-card shadow="never" class="rows-card">
            <template #header>
              <div class="card-header">
                <span class="form-card-title">支付记录</span>
                <div class="card-header-actions">
                  <span class="page-count">共 {{ detail.payment.length }} 条</span>
                  <el-button
                    v-if="canAddManualRow"
                    size="small"
                    type="primary"
                    plain
                    @click="openManualDialog"
                  >
                    新增历史明细
                  </el-button>
                </div>
              </div>
            </template>

            <el-empty
              v-if="detail.payment.length === 0"
              description="当前清单暂无支付记录"
            />

            <el-table
              v-else
              :data="detail.payment"
              stripe
              size="small"
              class="compact-table"
            >
              <el-table-column label="费用项" min-width="170">
                <template #default="{ row }">
                  {{ formatFeeItemDisplay(row.fee_item_id) }}
                </template>
              </el-table-column>
              <el-table-column prop="case_id" label="案件" min-width="180">
                <template #default="{ row }">
                  {{ formatCaseDisplay(row) }}
                </template>
              </el-table-column>
              <el-table-column label="状态" width="110">
                <template #default="{ row }">
                  <el-tag :type="govPaymentStatusTag(row.status)">
                    {{ govPaymentStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="缴费日期" width="130">
                <template #default="{ row }">
                  {{ row.paid_date || '—' }}
                </template>
              </el-table-column>
              <el-table-column label="缴费金额" min-width="150" align="right">
                <template #default="{ row }">
                  {{ formatMoney(row.paid_amount, row.currency) }}
                </template>
              </el-table-column>
              <el-table-column label="官方收据号" min-width="160">
                <template #default="{ row }">
                  {{ row.official_receipt_no || '—' }}
                </template>
              </el-table-column>
              <el-table-column label="备注" min-width="180">
                <template #default="{ row }">
                  {{ row.remark || '—' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button
                    text
                    type="primary"
                    :disabled="!canRegisterPayment(row)"
                    @click="goToRegister(row)"
                  >
                    登记缴费
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-card shadow="never" class="rows-card">
            <template #header>
              <div class="card-header">
                <span class="form-card-title">官方凭证</span>
                <span class="page-count">
                  共 {{ detail.official_evidence?.length ?? 0 }} 个
                </span>
              </div>
            </template>

            <el-empty
              v-if="!detail.official_evidence?.length"
              description="当前没有官方凭证"
            />

            <el-table
              v-else
              :data="detail.official_evidence"
              stripe
              size="small"
              class="compact-table"
            >
              <el-table-column prop="id" label="产物编号" min-width="180" />
              <el-table-column prop="status" label="凭证状态" min-width="190" />
              <el-table-column
                prop="official_acceptance_evidence_ref"
                label="接受凭证引用"
                min-width="190"
              />
              <el-table-column
                prop="official_acceptance_evidence_hash"
                label="接受凭证摘要"
                min-width="220"
              />
              <el-table-column label="官方接受时间" min-width="160">
                <template #default="{ row }">
                  {{ formatDateTime(row.official_accepted_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :xs="24" :lg="8">
          <FeeLinkagePanel
            v-if="feePackageId && payList"
            class="fee-linkage-side-panel"
            :package-id="feePackageId"
            :focus-id="String(payList.id)"
          />

          <el-card shadow="never">
            <template #header>
              <div class="card-header">
                <span class="form-card-title">操作面板</span>
              </div>
            </template>

            <div class="action-stack">
              <el-alert
                title="缴费登记入口"
                type="info"
                :closable="false"
                description="进入官方缴费登记页，可带入当前官费清单编号。"
              />
              <el-button type="primary" plain @click="goToFirstRegistrable">
                前往官方缴费登记
              </el-button>

              <el-divider />

              <el-alert
                title="清单导出"
                type="warning"
                :closable="false"
                description="只有草稿状态的官费清单允许导出，导出后状态会更新为已导出。"
              />
              <el-button
                type="primary"
                :disabled="!canExport"
                :loading="exporting"
                @click="handleExport"
              >
                导出当前清单
              </el-button>

              <el-divider />

              <el-form
                ref="markPaidFormRef"
                :model="markPaidForm"
                :rules="markPaidRules"
                label-position="top"
              >
                <el-alert
                  title="标记为已缴费"
                  type="success"
                  :closable="false"
                  description="仅已导出且明细已登记缴费的清单可执行。"
                />
                <el-form-item label="实际缴费日期" prop="paid_date">
                  <el-date-picker
                    v-model="markPaidForm.paid_date"
                    type="date"
                    placeholder="请选择日期"
                    value-format="YYYY-MM-DD"
                    format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-button
                  type="success"
                  :disabled="!canMarkPaid"
                  :loading="markingPaid"
                  @click="handleMarkPaid"
                >
                  标记清单已缴费
                </el-button>
              </el-form>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <ManualGovPaymentDialog
      v-model="manualDialogVisible"
      :pay-list-id="payList?.id ?? null"
      :pay-list-title="payListTitle"
      @success="handleManualSuccess"
    />
  </main>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  exportPayList,
  getPayListDetail,
  mapGovPaymentsError,
  markPayListPaid,
} from '../../../api/govPayments'
import type {
  GovPaymentInfo,
  GovPaymentsApiError,
  PayListDetailResult,
} from '../../../api/govPayments.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import ManualGovPaymentDialog from '../components/ManualGovPaymentDialog.vue'
import FeeLinkagePanel from '../../officialWorkflows/components/FeeLinkagePanel.vue'

interface MarkPaidForm {
  paid_date: string
}

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const exporting = ref(false)
const markingPaid = ref(false)
const manualDialogVisible = ref(false)
const error = ref<GovPaymentsApiError | null>(null)
const detail = ref<PayListDetailResult | null>(null)
const markPaidFormRef = ref<FormInstance>()

const markPaidForm = reactive<MarkPaidForm>({
  paid_date: dayjs().format('YYYY-MM-DD'),
})

const markPaidRules: FormRules<MarkPaidForm> = {
  paid_date: [{ required: true, message: '实际缴费日期为必填项', trigger: 'change' }],
}

const payListId = computed(() => {
  const value = Number(route.params.id)
  return Number.isFinite(value) && value > 0 ? value : 0
})
const feePackageId = computed(() => String(route.query.package_id || route.query.packageId || '').trim())

const payList = computed(() => detail.value?.pay_list ?? null)

const payListTitle = computed(() => {
  if (!payList.value) return '读取中'
  return formatPayListNo(payList.value)
})

const canExport = computed(() => (payList.value?.status || '').toUpperCase() === 'DRAFT')
const canMarkPaid = computed(() => (payList.value?.status || '').toUpperCase() === 'EXPORTED')
const canAddManualRow = computed(() => {
  if (!payList.value) return false
  const status = (payList.value.status || '').toUpperCase()
  return status === 'DRAFT' && detail.value?.gov_payments.length === 0
})

const firstRegistrablePayment = computed(() => {
  return detail.value?.gov_payments.find(canRegisterPayment) ?? null
})

function goBack() {
  router.push('/fee-management/pay-lists')
}

function canRegisterPayment(row: GovPaymentInfo): boolean {
  if (!row.fee_item_id) return false
  const status = (row.status || '').toUpperCase()
  return status !== 'PAID' && status !== 'RECORDED'
}

function goToFirstRegistrable() {
  if (!firstRegistrablePayment.value) {
    ElMessage.warning('当前清单没有可登记缴费的费用项。')
    return
  }
  goToRegister(firstRegistrablePayment.value)
}

function goToRegister(row: GovPaymentInfo) {
  if (!payList.value || !row.fee_item_id) return
  router.push({
    path: '/fee-management/gov-payments/new',
    query: {
      pay_list_id: String(payList.value.id),
      fee_item_id: row.fee_item_id,
    },
  })
}

function openManualDialog() {
  if (!canAddManualRow.value) {
    ElMessage.warning('仅空的历史清单可新增手工明细。')
    return
  }
  manualDialogVisible.value = true
}

function payListStatusText(status?: string): string {
  switch ((status || '').toUpperCase()) {
    case 'DRAFT':
      return '草稿'
    case 'EXPORTED':
      return '已导出'
    case 'PAID':
      return '已缴费'
    case 'CANCELLED':
      return '已取消'
    case 'PARTIAL':
      return '部分完成'
    default:
      return '未知状态'
  }
}

function payListStatusTag(status?: string): 'info' | 'warning' | 'success' | 'danger' {
  switch ((status || '').toUpperCase()) {
    case 'EXPORTED':
      return 'warning'
    case 'PAID':
      return 'success'
    case 'CANCELLED':
      return 'danger'
    default:
      return 'info'
  }
}

function govPaymentStatusText(status?: string): string {
  switch ((status || '').toUpperCase()) {
    case 'PLANNED':
      return '已计划'
    case 'RECORDED':
      return '已登记'
    case 'PAID':
      return '已缴费'
    default:
      return '未知状态'
  }
}

function govPaymentStatusTag(status?: string): 'info' | 'warning' | 'success' {
  switch ((status || '').toUpperCase()) {
    case 'PAID':
      return 'success'
    case 'RECORDED':
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

function formatDateTime(dateValue?: string): string {
  if (!dateValue) return '—'
  const parsed = dayjs(dateValue)
  return parsed.isValid() ? parsed.format('YYYY-MM-DD HH:mm') : dateValue
}

function formatPayListNo(target: NonNullable<typeof payList.value>): string {
  return target.pay_list_no || '未生成清单编号'
}

function formatClientDisplay(value?: string | null): string {
  return value ? '已关联客户' : '未关联客户'
}

function formatFeeItemDisplay(value?: string | null): string {
  return value ? '已关联费用项' : '手工补录'
}

function formatCaseDisplay(row: { case_id?: string | null; case_no?: string | null }): string {
  if (row.case_no) return row.case_no
  return row.case_id ? '已关联案件' : '未关联案件'
}

function buildExportFileName(target: NonNullable<typeof payList.value>): string {
  const displayNo = formatPayListNo(target)
  return `官费清单-${displayNo}.xlsx`
}

function downloadBlob(blob: Blob, fileName: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

async function loadDetail() {
  detail.value = null
  if (!payListId.value) {
    error.value = {
      status: 0,
      code: 'INVALID_PAY_LIST_ID',
      message: '官费清单参数无效。',
      category: 'validation',
    }
    return
  }

  loading.value = true
  error.value = null
  try {
    detail.value = await getPayListDetail(payListId.value)
  } catch (err) {
    detail.value = null
    error.value = mapGovPaymentsError(err)
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  await loadDetail()
}

async function handleExport() {
  if (!payList.value || !canExport.value) {
    ElMessage.warning('只有草稿状态的官费清单可以导出。')
    return
  }

  exporting.value = true
  error.value = null
  try {
    const blob = await exportPayList(payList.value.id)
    downloadBlob(blob, buildExportFileName(payList.value))
    ElMessage.success('官费清单已开始导出。')
    await loadDetail()
  } catch (err) {
    error.value = mapGovPaymentsError(err)
  } finally {
    exporting.value = false
  }
}

async function handleMarkPaid() {
  if (!payList.value || !canMarkPaid.value) {
    ElMessage.warning('当前状态不允许标记清单已缴费。')
    return
  }

  const valid = await markPaidFormRef.value?.validate().catch(() => false)
  if (!valid) return

  markingPaid.value = true
  error.value = null
  try {
    await markPayListPaid(payList.value.id, { paid_date: markPaidForm.paid_date })
    ElMessage.success('官费清单已标记为已缴费。')
    await loadDetail()
  } catch (err) {
    error.value = mapGovPaymentsError(err)
  } finally {
    markingPaid.value = false
  }
}

async function handleManualSuccess() {
  await loadDetail()
}

watch(payListId, () => {
  void loadDetail()
}, { immediate: true })
</script>

<style scoped>
.detail-layout {
  margin-top: 8px;
}

.rows-card {
  margin-top: 16px;
}

.fee-linkage-side-panel {
  margin-bottom: 16px;
}

.loading-state {
  padding: 16px 0 8px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.action-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

  .page-header-right {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-header-right :deep(.el-button) {
    flex: 1;
    min-width: 120px;
  }
}
</style>
