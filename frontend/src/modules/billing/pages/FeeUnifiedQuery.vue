<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">费用情况查询一览</h1>
        <span class="page-count" aria-live="polite">
          上半表 {{ upperTotal }} 条，下半表 {{ lowerTotal }} 条
        </span>
      </div>
    </div>

    <div v-if="!hasAnyOverviewPerm" class="page-empty">
      <EmptyState
        title="暂无访问权限"
        message="需要具备官费清单读取或个案收款读取权限后才能使用费用情况查询一览。"
        icon="🔐"
      />
    </div>

    <template v-else>
      <section class="overview-section">
        <div class="section-header">
          <div>
            <h2 class="section-title">上半表：官费缴费情况一览</h2>
            <p class="section-desc">按官费缴费记录查看案卷缴费情况。</p>
          </div>
          <el-tag type="info" size="small">数据源：T_GovPayment</el-tag>
        </div>

        <div v-if="!hasGovPaymentPerm" class="page-empty section-empty">
          <EmptyState
            title="暂无上半表权限"
            message="需要具备官费清单读取权限后才能查看官费缴费情况。"
            icon="🔐"
          />
        </div>

        <template v-else>
          <el-form class="filter-form" :inline="true">
            <el-form-item label="案卷号">
              <el-input
                v-model.trim="upperFilters.case_no"
                class="filter-input"
                clearable
                placeholder="请输入案卷号"
                @keyup.enter="applyUpperFilters"
              />
            </el-form-item>
            <el-form-item label="申请号">
              <el-input
                v-model.trim="upperFilters.app_no"
                class="filter-input"
                clearable
                placeholder="请输入申请号"
                @keyup.enter="applyUpperFilters"
              />
            </el-form-item>
            <el-form-item label="专利号">
              <el-input
                v-model.trim="upperFilters.patent_no"
                class="filter-input"
                clearable
                placeholder="请输入专利号"
                @keyup.enter="applyUpperFilters"
              />
            </el-form-item>
            <el-form-item label="客户编号">
              <el-input
                v-model.trim="upperFilters.client_id"
                class="filter-input"
                clearable
                placeholder="请输入客户编号"
                @keyup.enter="applyUpperFilters"
              />
            </el-form-item>
            <el-form-item label="申请人">
              <el-input
                v-model.trim="upperFilters.applicant_name"
                class="filter-input"
                clearable
                placeholder="请输入申请人"
                @keyup.enter="applyUpperFilters"
              />
            </el-form-item>
            <el-form-item label="缴费日期">
              <el-date-picker
                v-model="upperFilters.paid_date_range"
                class="filter-range"
                clearable
                end-placeholder="结束日期"
                range-separator="至"
                start-placeholder="开始日期"
                type="daterange"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="upperLoading" @click="applyUpperFilters">查询</el-button>
              <el-button :disabled="upperLoading" @click="resetUpperFilters">重置</el-button>
            </el-form-item>
          </el-form>

          <div v-if="upperError" class="page-error">
            <ApiErrorBanner :error="upperError" @dismiss="upperError = null" />
          </div>

          <LoadingBlock v-else-if="upperLoading" :rows="6" />

          <div v-else-if="upperTotal === 0" class="page-empty section-empty">
            <EmptyState
              title="暂无官费缴费记录"
              message="请调整上半表筛选条件后重试。"
              icon="📑"
            />
          </div>

          <div v-else class="page-table">
            <el-table :data="upperItems" stripe size="small" class="compact-table">
              <el-table-column label="案卷号" min-width="150" show-overflow-tooltip>
                <template #default="{ row }">{{ row.case_no || '—' }}</template>
              </el-table-column>
              <el-table-column label="申请号" min-width="160" show-overflow-tooltip>
                <template #default="{ row }">{{ row.app_no || '—' }}</template>
              </el-table-column>
              <el-table-column label="费用代码" width="140" show-overflow-tooltip>
                <template #default="{ row }">{{ row.fee_code || '—' }}</template>
              </el-table-column>
              <el-table-column label="费用名称" min-width="160" show-overflow-tooltip>
                <template #default="{ row }">{{ row.fee_name || '—' }}</template>
              </el-table-column>
              <el-table-column label="年度" width="90" align="center">
                <template #default="{ row }">{{ row.year_no ?? '—' }}</template>
              </el-table-column>
              <el-table-column label="应缴金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatAmount(row.planned_amt, row.currency) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="实缴金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatAmount(row.paid_amt, row.currency) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="清单编号" width="130" show-overflow-tooltip>
                <template #default="{ row }">{{ row.list_no || '—' }}</template>
              </el-table-column>
              <el-table-column label="凭证号" width="140" show-overflow-tooltip>
                <template #default="{ row }">{{ row.voucher_no || '—' }}</template>
              </el-table-column>
              <el-table-column label="发票号" width="140" show-overflow-tooltip>
                <template #default="{ row }">{{ row.invoice_no || '—' }}</template>
              </el-table-column>
              <el-table-column label="计划缴费日" width="120">
                <template #default="{ row }">{{ formatDate(row.planned_pay_date) }}</template>
              </el-table-column>
              <el-table-column label="实际缴费日" width="120">
                <template #default="{ row }">{{ formatDate(row.paid_date) }}</template>
              </el-table-column>
            </el-table>

            <PaginationBar
              v-model:page="upperPage"
              v-model:page-size="upperPageSize"
              :total="upperTotal"
              :page-sizes="[10, 20, 50]"
            />
          </div>
        </template>
      </section>

      <section class="overview-section">
        <div class="section-header">
          <div>
            <h2 class="section-title">下半表：个案收款情况一览</h2>
            <p class="section-desc">按个案收款记录查看应收、实收与欠款情况。</p>
          </div>
          <el-tag type="warning" size="small">数据源：T_CaseReceipt</el-tag>
        </div>

        <div v-if="!hasCaseReceiptPerm" class="page-empty section-empty">
          <EmptyState
            title="暂无下半表权限"
            message="需要具备个案收款读取权限后才能查看个案收款情况。"
            icon="🔐"
          />
        </div>

        <template v-else>
          <el-form class="filter-form" :inline="true">
            <el-form-item label="案卷号">
              <el-input
                v-model.trim="lowerFilters.case_no"
                class="filter-input"
                clearable
                placeholder="请输入案卷号"
                @keyup.enter="applyLowerFilters"
              />
            </el-form-item>
            <el-form-item label="申请号">
              <el-input
                v-model.trim="lowerFilters.app_no"
                class="filter-input"
                clearable
                placeholder="请输入申请号"
                @keyup.enter="applyLowerFilters"
              />
            </el-form-item>
            <el-form-item label="专利号">
              <el-input
                v-model.trim="lowerFilters.patent_no"
                class="filter-input"
                clearable
                placeholder="请输入专利号"
                @keyup.enter="applyLowerFilters"
              />
            </el-form-item>
            <el-form-item label="客户编号">
              <el-input
                v-model.trim="lowerFilters.client_id"
                class="filter-input"
                clearable
                placeholder="请输入客户编号"
                @keyup.enter="applyLowerFilters"
              />
            </el-form-item>
            <el-form-item label="申请人">
              <el-input
                v-model.trim="lowerFilters.applicant_name"
                class="filter-input"
                clearable
                placeholder="请输入申请人"
                @keyup.enter="applyLowerFilters"
              />
            </el-form-item>
            <el-form-item label="费用类型">
              <el-select
                v-model="lowerFilters.fee_type"
                clearable
                class="filter-input"
                placeholder="全部费用类型"
              >
                <el-option label="官费" value="GOV" />
                <el-option label="服务费" value="SERVICE" />
                <el-option label="杂费" value="MISC" />
              </el-select>
            </el-form-item>
            <el-form-item label="收款日期">
              <el-date-picker
                v-model="lowerFilters.receipt_date_range"
                class="filter-range"
                clearable
                end-placeholder="结束日期"
                range-separator="至"
                start-placeholder="开始日期"
                type="daterange"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="lowerLoading" @click="applyLowerFilters">查询</el-button>
              <el-button :disabled="lowerLoading" @click="resetLowerFilters">重置</el-button>
            </el-form-item>
          </el-form>

          <div v-if="lowerError" class="page-error">
            <ApiErrorBanner :error="lowerError" @dismiss="lowerError = null" />
          </div>

          <LoadingBlock v-else-if="lowerLoading" :rows="6" />

          <div v-else-if="lowerTotal === 0" class="page-empty section-empty">
            <EmptyState
              title="暂无个案收款记录"
              message="请调整下半表筛选条件后重试。"
              icon="📋"
            />
          </div>

          <div v-else class="page-table">
            <el-table :data="lowerItems" stripe size="small" class="compact-table">
              <el-table-column label="案卷号" min-width="150" show-overflow-tooltip>
                <template #default="{ row }">{{ row.case_no || '—' }}</template>
              </el-table-column>
              <el-table-column label="费用代码" width="140" show-overflow-tooltip>
                <template #default="{ row }">{{ row.fee_code || '—' }}</template>
              </el-table-column>
              <el-table-column label="费用名称" min-width="160" show-overflow-tooltip>
                <template #default="{ row }">{{ row.fee_name || '—' }}</template>
              </el-table-column>
              <el-table-column label="年度" width="90" align="center">
                <template #default="{ row }">{{ row.year_no ?? '—' }}</template>
              </el-table-column>
              <el-table-column label="费用类型" width="110" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="feeTypeTagType(row.fee_type)">{{ row.fee_type || '—' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="应收金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatAmount(row.receivable_amt, row.currency) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="实收金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatAmount(row.received_amt, row.currency) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="欠款标记" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="booleanTagType(row.is_arrears)">
                    {{ booleanText(row.is_arrears) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="是否预收" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="booleanTagType(row.is_prepayment)">
                    {{ booleanText(row.is_prepayment) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="可提成" width="100" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="booleanTagType(row.is_commissionable)">
                    {{ booleanText(row.is_commissionable) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="收款日期" width="120">
                <template #default="{ row }">{{ formatDate(row.receipt_date) }}</template>
              </el-table-column>
              <el-table-column label="缴费期限" width="120">
                <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
              </el-table-column>
              <el-table-column label="发票号" width="140" show-overflow-tooltip>
                <template #default="{ row }">{{ row.invoice_no || '—' }}</template>
              </el-table-column>
            </el-table>

            <PaginationBar
              v-model:page="lowerPage"
              v-model:page-size="lowerPageSize"
              :total="lowerTotal"
              :page-sizes="[10, 20, 50]"
            />
          </div>
        </template>
      </section>
    </template>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import {
  getFeeOverviewCaseReceipts,
  getFeeOverviewGovPayments,
} from '../../../api/billing'
import type {
  FeeOverviewCaseReceiptItem,
  FeeOverviewCaseReceiptResponse,
  FeeOverviewGovPaymentItem,
  FeeOverviewGovPaymentResponse,
} from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { useAuthStore } from '../../../stores/auth'

const authStore = useAuthStore()

const upperItems = ref<FeeOverviewGovPaymentItem[]>([])
const upperLoading = ref(false)
const upperError = ref<ApiError | null>(null)
const upperPage = ref(1)
const upperPageSize = ref(20)
const upperTotal = ref(0)

const lowerItems = ref<FeeOverviewCaseReceiptItem[]>([])
const lowerLoading = ref(false)
const lowerError = ref<ApiError | null>(null)
const lowerPage = ref(1)
const lowerPageSize = ref(20)
const lowerTotal = ref(0)

const upperFilters = reactive({
  case_no: '',
  app_no: '',
  patent_no: '',
  client_id: '',
  applicant_name: '',
  paid_date_range: [] as [string, string] | [],
})

const lowerFilters = reactive({
  case_no: '',
  app_no: '',
  patent_no: '',
  client_id: '',
  applicant_name: '',
  fee_type: '',
  receipt_date_range: [] as [string, string] | [],
})

const hasGovPaymentPerm = computed(() => authStore.hasPermission('PayList.Read'))
const hasCaseReceiptPerm = computed(() => authStore.hasPermission('CaseReceipt.Read'))
const hasAnyOverviewPerm = computed(() => hasGovPaymentPerm.value || hasCaseReceiptPerm.value)

function formatAmount(value: number, currency: string): string {
  const safeValue = Number.isFinite(value) ? value : 0
  return `${currency || 'CNY'} ${safeValue.toFixed(2)}`
}

function formatDate(value?: string | null): string {
  return value ? value.slice(0, 10) : '—'
}

function feeTypeTagType(feeType?: string | null): 'info' | 'success' | 'warning' {
  const normalized = (feeType || '').toUpperCase()
  if (normalized === 'GOV') return 'warning'
  if (normalized === 'SERVICE') return 'success'
  return 'info'
}

function booleanTagType(value?: boolean | null): 'success' | 'info' {
  return value ? 'success' : 'info'
}

function booleanText(value?: boolean | null): string {
  return value ? '是' : '否'
}

function buildUpperParams() {
  return {
    page: upperPage.value,
    page_size: upperPageSize.value,
    case_no: upperFilters.case_no || undefined,
    app_no: upperFilters.app_no || undefined,
    patent_no: upperFilters.patent_no || undefined,
    client_id: upperFilters.client_id || undefined,
    applicant_name: upperFilters.applicant_name || undefined,
    paid_date_range: upperFilters.paid_date_range,
  }
}

function buildLowerParams() {
  return {
    page: lowerPage.value,
    page_size: lowerPageSize.value,
    case_no: lowerFilters.case_no || undefined,
    app_no: lowerFilters.app_no || undefined,
    patent_no: lowerFilters.patent_no || undefined,
    client_id: lowerFilters.client_id || undefined,
    applicant_name: lowerFilters.applicant_name || undefined,
    fee_type: lowerFilters.fee_type || undefined,
    receipt_date_range: lowerFilters.receipt_date_range,
  }
}

async function fetchUpperRecords() {
  if (!hasGovPaymentPerm.value) {
    upperItems.value = []
    upperTotal.value = 0
    upperLoading.value = false
    return
  }

  upperLoading.value = true
  upperError.value = null

  try {
    const result: FeeOverviewGovPaymentResponse = await getFeeOverviewGovPayments(buildUpperParams())
    upperItems.value = result.items
    upperTotal.value = result.total
  } catch (err) {
    upperError.value = err as ApiError
  } finally {
    upperLoading.value = false
  }
}

async function fetchLowerRecords() {
  if (!hasCaseReceiptPerm.value) {
    lowerItems.value = []
    lowerTotal.value = 0
    lowerLoading.value = false
    return
  }

  lowerLoading.value = true
  lowerError.value = null

  try {
    const result: FeeOverviewCaseReceiptResponse = await getFeeOverviewCaseReceipts(buildLowerParams())
    lowerItems.value = result.items
    lowerTotal.value = result.total
  } catch (err) {
    lowerError.value = err as ApiError
  } finally {
    lowerLoading.value = false
  }
}

function applyUpperFilters() {
  if (upperPage.value === 1) {
    fetchUpperRecords()
    return
  }
  upperPage.value = 1
}

function resetUpperFilters() {
  upperFilters.case_no = ''
  upperFilters.app_no = ''
  upperFilters.patent_no = ''
  upperFilters.client_id = ''
  upperFilters.applicant_name = ''
  upperFilters.paid_date_range = []
  upperError.value = null
  if (upperPage.value === 1) {
    fetchUpperRecords()
    return
  }
  upperPage.value = 1
}

function applyLowerFilters() {
  if (lowerPage.value === 1) {
    fetchLowerRecords()
    return
  }
  lowerPage.value = 1
}

function resetLowerFilters() {
  lowerFilters.case_no = ''
  lowerFilters.app_no = ''
  lowerFilters.patent_no = ''
  lowerFilters.client_id = ''
  lowerFilters.applicant_name = ''
  lowerFilters.fee_type = ''
  lowerFilters.receipt_date_range = []
  lowerError.value = null
  if (lowerPage.value === 1) {
    fetchLowerRecords()
    return
  }
  lowerPage.value = 1
}

watch([upperPage, upperPageSize], () => {
  fetchUpperRecords()
})

watch([lowerPage, lowerPageSize], () => {
  fetchLowerRecords()
})

onMounted(() => {
  fetchUpperRecords()
  fetchLowerRecords()
})
</script>

<style scoped>
.overview-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 28px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.section-title {
  margin: 0;
  font-size: 18px;
}

.section-desc {
  margin: 6px 0 0;
  color: var(--text-sub, #64748b);
  font-size: 13px;
}

.section-empty {
  padding: 12px 0;
}

.mono-num {
  font-family: var(--font-mono, monospace);
}

@media (max-width: 960px) {
  .section-header {
    flex-direction: column;
  }
}
</style>
