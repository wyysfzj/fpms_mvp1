<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> {{ ZH.common.back }}
        </el-button>
      </div>
      <div class="page-header-right">
        <el-button @click="handlePrint" :loading="printing" :disabled="!bill">
          {{ ZH.billDetail.printBill }}
        </el-button>
        <el-button @click="fetchBill" :loading="loading">{{ ZH.billDetail.refresh }}</el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- Content -->
    <template v-else-if="bill">
      <!-- Relation Chain -->
      <RelationChainCard
        :client="bill.client_id ? { id: bill.client_id, name: clientDisplay } : undefined"
        :case-ref="bill.case_id ? { id: bill.case_id, no: caseDisplay } : undefined"
        :fee-draft="feeDraftRelation"
        :bill="{ id: bill.id, no: billDisplayNo }"
      />

      <!-- Bill Header -->
      <div class="case-header">
        <div class="case-header-main">
          <div class="case-meta">
            <el-tag :type="statusTagType" size="small">{{ getBillStatusDisplay(bill.status) }}</el-tag>
            <span class="meta-divider">|</span>
            <span class="bill-no">{{ billDisplayNo }}</span>
            <span class="meta-divider">|</span>
            <span>{{ billDirectionText(bill.direction) }}</span>
            <span class="meta-divider">|</span>
            <span>{{ billCurrencyDisplay }}</span>
          </div>
          <div class="case-title">
            <h1>{{ ZH.billDetail.billNo }} {{ billDisplayNo }}</h1>
            <p class="meta-subtitle">
              {{ clientDisplay }}
            </p>
          </div>
        </div>
      </div>

      <el-alert
        :title="`账单结清状态：${settlementStatusText(bill.status)}`"
        :type="bill.status === 'SETTLED' ? 'success' : 'warning'"
        :closable="false"
      >
        <template #default>
          账单余额为 {{ formatAmount(bill.balance) }}；余额大于零时为未结清或部分结清，余额归零后为已结清。
        </template>
      </el-alert>

      <el-tabs v-model="activeTab" class="case-tabs">
        <el-tab-pane :label="ZH.billDetail.items" name="items">
          <div class="case-panel">
            <h3 class="panel-heading">{{ ZH.billDetail.billItems }}</h3>

            <div v-if="bill.items.length === 0" class="items-empty">
              <p>{{ ZH.billDetail.noItems }}</p>
            </div>

            <el-table
              v-else
              :data="bill.items"
              stripe
              size="small"
              class="compact-table items-table"
              show-summary
              :summary-method="getSummaries"
            >
              <el-table-column prop="description" :label="ZH.billDetail.description" min-width="200" />
              <el-table-column :label="ZH.billDetail.qty" width="80" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ row.quantity }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="ZH.billDetail.unitPrice" width="120" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatAmount(row.unit_price) }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="ZH.billDetail.amount" width="140" align="right">
                <template #default="{ row }">
                  <span class="mono-num amount-cell">{{ formatAmount(row.amount) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="ZH.billDetail.overview" name="overview">
          <div class="case-content-grid">
            <div class="case-main-panel">
              <div class="case-panel">
                <h3 class="panel-heading">{{ ZH.billDetail.billInfo }}</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">{{ ZH.billDetail.billNo }}</span>
                    <span class="info-value bill-no">{{ billDisplayNo }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.billDetail.status }}</span>
                    <span class="info-value">{{ getBillStatusDisplay(bill.status) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">账单方向</span>
                    <span class="info-value">{{ billDirectionText(bill.direction) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.billDetail.client }}</span>
                    <router-link
                      v-if="bill.client_id"
                      class="entity-link info-value"
                      :to="`/clients/${bill.client_id}`"
                    >
                      {{ clientDisplay }}
                    </router-link>
                    <span v-else class="info-value">—</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.billDetail.case_ }}</span>
                    <router-link
                      v-if="bill.case_id"
                      class="entity-link info-value"
                      :to="`/cases/${bill.case_id}`"
                    >
                      {{ caseDisplay }}
                    </router-link>
                    <span v-else class="info-value">—</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">费用草稿</span>
                    <router-link
                      v-if="feeDraftRelation"
                      class="entity-link info-value"
                      :to="`/fees/drafts/${feeDraftRelation.id}`"
                    >
                      {{ feeDraftDisplay }}
                    </router-link>
                    <span v-else class="info-value">—</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.billDetail.currency }}</span>
                    <span class="info-value">{{ billCurrencyDisplay }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.billDetail.issueDate }}</span>
                    <span class="info-value">{{ bill.issue_date ? formatDate(bill.issue_date) : '—' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">{{ ZH.billDetail.dueDate }}</span>
                    <span class="info-value">{{ bill.due_date ? formatDate(bill.due_date) : '—' }}</span>
                  </div>
                </div>
              </div>

              <div v-if="bill.notes" class="case-panel">
                <h3 class="panel-heading">{{ ZH.billDetail.notes }}</h3>
                <p class="notes-content">{{ bill.notes }}</p>
              </div>

              <BadDebtPanel
                :bill="bill"
                :can-mark="canMarkBadDebt"
                :can-recover="canRecoverBadDebt"
                @changed="fetchBill"
              />
            </div>

            <div class="case-side-panel">
              <div class="case-panel side-widget">
                <div class="widget-title">{{ ZH.billDetail.amounts }}</div>
                <div class="amounts-summary">
                  <div class="amount-row">
                    <span class="amount-label">{{ ZH.billDetail.total }}</span>
                    <span class="amount-value mono-num">{{ formatAmount(bill.amount) }}</span>
                  </div>
                  <div class="amount-row">
                    <span class="amount-label">{{ ZH.billDetail.balance }}</span>
                    <span class="amount-value mono-num" :class="{ 'balance-zero': bill.balance === 0 }">
                      {{ formatAmount(bill.balance) }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="case-panel side-widget">
                <div class="widget-title">{{ ZH.billDetail.quickActions }}</div>
                <div class="quick-actions">
                  <router-link v-if="bill.case_id" :to="`/cases/${bill.case_id}`">
                    <el-button size="small">{{ ZH.billDetail.openCase }}</el-button>
                  </router-link>
                  <router-link v-if="bill.client_id" :to="`/clients/${bill.client_id}`">
                    <el-button size="small">{{ ZH.billDetail.viewClient }}</el-button>
                  </router-link>
                  <router-link v-if="feeDraftRelation" :to="`/fees/drafts/${feeDraftRelation.id}`">
                    <el-button size="small">查看费用草稿</el-button>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="抵扣记录" name="offsets">
          <div class="case-panel">
            <h3 class="panel-heading">抵扣记录</h3>

            <div v-if="offsetsLoading" class="items-empty">
              <el-skeleton :rows="3" animated />
            </div>

            <div v-else-if="offsets.length === 0" class="items-empty">
              <p>暂无抵扣记录。</p>
            </div>

            <el-table
              v-else
              :data="offsets"
              stripe
              size="small"
              class="compact-table"
            >
              <el-table-column label="抵扣日期" width="130">
                <template #default="{ row }">
                  {{ row.offset_date ? formatDate(row.offset_date) : '—' }}
                </template>
              </el-table-column>
              <el-table-column label="抵扣金额" width="140" align="right">
                <template #default="{ row }">
                  <span class="mono-num">{{ formatAmount(row.amount) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="120">
                <template #default="{ row }">
                  <el-tag v-if="row.is_reversed" type="danger" size="small">已撤销</el-tag>
                  <el-tag v-else type="success" size="small">有效</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-popconfirm
                    v-if="!row.is_reversed"
                    title="确定撤销此抵扣？"
                    confirm-button-text="确定"
                    cancel-button-text="取消"
                    @confirm="handleReverseOffset(row.id)"
                  >
                    <template #reference>
                      <el-button type="danger" size="small" text>撤销</el-button>
                    </template>
                  </el-popconfirm>
                  <span v-else class="text-muted">—</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- Empty State -->
    <div v-else-if="!loading && !error" class="page-empty">
      <div class="empty-state">
        <span class="empty-icon">🧾</span>
        <h3 class="empty-title">{{ ZH.billDetail.notFound }}</h3>
        <p class="empty-message">{{ ZH.billDetail.notFoundMsg }}</p>
        <el-button type="primary" @click="goBack">{{ ZH.common.back }}</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getBill,
  getOffsets,
  printBill,
  reverseOffset,
  settlementStatusText,
} from '../../../api/billing'
import type { BillDetail, OffsetListItem } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import BadDebtPanel from '../components/BadDebtPanel.vue'
import RelationChainCard from '../../../components/relations/RelationChainCard.vue'
import { usePageContext } from '../../../stores/pageContext'
import { useAuthStore } from '../../../stores/auth'
import { ZH } from '../../../constants/labels.zh'
import { getBillDirectionText, getBillStatusText } from '../../../constants/displayText'
import { formatMoney, normalizeCurrencyCode } from '../../../utils/money'

const BAD_DEBT_MARK_PERMISSION = 'Billing.BadDebtMark'
const BAD_DEBT_RECOVER_PERMISSION = 'Billing.BadDebtRecover'

const route = useRoute()
const router = useRouter()
const pageContext = usePageContext()
const authStore = useAuthStore()

const bill = ref<BillDetail | null>(null)
const loading = ref(false)
const printing = ref(false)
const error = ref<ApiError | null>(null)
const activeTab = ref('items')

const offsets = ref<OffsetListItem[]>([])
const offsetsLoading = ref(false)

const billId = computed(() => String(route.params.id || ''))
const canMarkBadDebt = computed(() => authStore.hasPermission(BAD_DEBT_MARK_PERMISSION))
const canRecoverBadDebt = computed(() => authStore.hasPermission(BAD_DEBT_RECOVER_PERMISSION))
const billDisplayNo = computed(() => {
  if (!bill.value?.id) return '—'
  return bill.value.bill_no || '未生成账单号'
})
const clientDisplay = computed(() => {
  if (!bill.value?.client_id) return '未关联客户'
  return bill.value.client_name || '未命名客户'
})
const caseDisplay = computed(() => {
  if (!bill.value?.case_id) return '—'
  return bill.value.case_no || '未命名案件'
})
const feeDraftDisplay = computed(() => {
  if (!bill.value) return '—'
  if (bill.value.primary_draft_label) return bill.value.primary_draft_label
  const labels = bill.value.source_draft_labels || []
  if (labels.length === 1) return labels[0]
  if (labels.length > 1) return `${labels[0]} 等 ${labels.length} 个草稿`
  return bill.value.primary_draft_id ? '费用草稿' : '—'
})
const feeDraftRelation = computed(() => {
  if (!bill.value?.primary_draft_id) return undefined
  return {
    id: bill.value.primary_draft_id,
    label: feeDraftDisplay.value,
  }
})
const billCurrencyDisplay = computed(() => normalizeCurrencyCode(bill.value?.currency))

const statusTagType = computed<'info' | 'warning' | 'success' | 'danger'>(() => {
  switch (bill.value?.status) {
    case 'PAID': return 'success'
    case 'ISSUED': return 'warning'
    case 'BAD_DEBT': return 'danger'
    case 'VOID': return 'danger'
    default: return 'info'
  }
})

async function fetchBill() {
  if (!billId.value) return

  loading.value = true
  error.value = null

  try {
    bill.value = await getBill(billId.value)
    pageContext.setBreadcrumb(['账单管理', '账单详情', billDisplayNo.value])
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatAmount(value: number): string {
  return formatMoney(value, bill.value?.currency)
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

function getBillStatusDisplay(status?: string): string {
  if (status === 'BAD_DEBT') return '坏账'
  return getBillStatusText(status)
}

function billDirectionText(direction?: string): string {
  return getBillDirectionText(direction)
}

function getSummaries({ columns }: { columns: { property?: string; label?: string }[] }): string[] {
  return columns.map((column, index) => {
    if (index === 0) return ZH.billDetail.total
    if (column.property === 'amount' || column.label === ZH.billDetail.amount) {
      return formatAmount(bill.value?.amount || 0)
    }
    return ''
  })
}

function goBack() {
  router.push('/billing/bills')
}

async function handlePrint() {
  if (!billId.value || !bill.value) return

  printing.value = true
  error.value = null

  try {
    const blob = await printBill(billId.value)

    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `bill-${billDisplayNo.value}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success(ZH.billDetail.downloadSuccess)
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    // Special handling for 409 (template not configured)
    if (apiError.status === 409) {
      ElMessage.error(ZH.billDetail.templateNotConfigured)
    }
  } finally {
    printing.value = false
  }
}

async function fetchOffsets() {
  if (!billId.value) return
  offsetsLoading.value = true
  try {
    const result = await getOffsets({ bill_id: billId.value })
    offsets.value = result.items
  } catch {
    // Silent fail — offsets are supplementary
  } finally {
    offsetsLoading.value = false
  }
}

async function handleReverseOffset(offsetId: string) {
  try {
    await reverseOffset(offsetId)
    ElMessage.success('抵扣已撤销')
    await Promise.all([fetchBill(), fetchOffsets()])
  } catch (err) {
    error.value = err as ApiError
  }
}

onMounted(() => {
  fetchBill()
  fetchOffsets()
})

onBeforeUnmount(() => {
  pageContext.clear()
})
</script>

<style scoped>
.bill-no {
  font-family: var(--font-mono);
  font-weight: 500;
}

.meta-subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: var(--text-sub);
}

.entity-link {
  color: var(--color-primary);
  font-family: var(--font-mono);
  text-decoration: none;
}

.entity-link:hover {
  text-decoration: underline;
}

.mono-num {
  font-family: var(--font-mono);
}

.amount-cell {
  font-weight: 500;
}

.items-empty {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-sub);
}

.items-table {
  width: 100%;
}

.notes-content {
  margin: 0;
  line-height: 1.6;
  color: var(--text-main);
  white-space: pre-wrap;
}

.amounts-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.amount-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.amount-label {
  font-size: 13px;
  color: var(--text-sub);
}

.amount-value {
  font-size: 16px;
  font-weight: 600;
}

.balance-zero {
  color: var(--color-success);
}

.text-muted {
  color: var(--text-sub);
  font-size: 13px;
}
</style>
