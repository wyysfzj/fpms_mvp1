<template>
  <div class="receipts-summary">
    <!-- Error -->
    <div v-if="error" class="receipts-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="receipts-loading">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- Content -->
    <template v-else-if="receipts">
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="summary-card">
          <div class="card-label">累计开票</div>
          <div class="card-value mono-num">{{ formatAmount(receipts.total_billed) }}</div>
        </div>
        <div class="summary-card">
          <div class="card-label">累计回款</div>
          <div class="card-value mono-num text-success">{{ formatAmount(receipts.total_paid) }}</div>
        </div>
        <div class="summary-card">
          <div class="card-label">未结清</div>
          <div class="card-value mono-num" :class="{ 'text-warning': receipts.total_outstanding > 0 }">
            {{ formatAmount(receipts.total_outstanding) }}
          </div>
        </div>
      </div>

      <!-- Enriched Receipt Info (B5) -->
      <div v-if="hasEnrichedFields" class="enriched-info">
        <div class="info-grid">
          <div v-if="receipts.fee_code" class="info-item">
            <span class="info-label">费用代码</span>
            <span class="info-value mono-num">{{ receipts.fee_code }}</span>
          </div>
          <div v-if="receipts.fee_type" class="info-item">
            <span class="info-label">费用类型</span>
            <span class="info-value">{{ receipts.fee_type }}</span>
          </div>
          <div v-if="receipts.year_no != null" class="info-item">
            <span class="info-label">年度</span>
            <span class="info-value">{{ receipts.year_no }}</span>
          </div>
          <div v-if="receipts.invoice_no" class="info-item">
            <span class="info-label">发票号</span>
            <span class="info-value mono-num">{{ receipts.invoice_no }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">欠费状态</span>
            <el-tag v-if="receipts.is_arrears" type="danger" size="small">欠费</el-tag>
            <span v-else class="info-value">正常</span>
          </div>
          <div v-if="receipts.is_commissionable != null" class="info-item">
            <span class="info-label">可提成</span>
            <span class="info-value">{{ receipts.is_commissionable ? '是' : '否' }}</span>
          </div>
        </div>
      </div>

      <!-- Bills Table -->
      <div v-if="receipts.bills.length > 0" class="bills-section">
        <h4 class="section-title">账单</h4>
        <el-table
          :data="receipts.bills"
          stripe
          size="small"
          class="compact-table"
          @row-click="handleBillClick"
        >
          <el-table-column prop="bill_no" label="账单号" width="140">
            <template #default="{ row }">
              <span class="bill-no">{{ row.bill_no }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">
                {{ getBillStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="130" align="right">
            <template #default="{ row }">
              <span class="mono-num">{{ formatAmount(row.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="余额" width="130" align="right">
            <template #default="{ row }">
              <span class="mono-num" :class="{ 'text-success': row.balance === 0 }">
                {{ formatAmount(row.balance) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="issue_date" label="开票日" width="120">
            <template #default="{ row }">
              {{ row.issue_date ? formatDate(row.issue_date) : '—' }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Empty State -->
      <div v-else class="no-bills">
        <p>该案件暂无账单。</p>
      </div>
    </template>

    <!-- No Data -->
    <div v-else-if="!loading && !error" class="no-data">
      <p>暂无账务信息。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getCaseReceipts } from '../../../api/billing'
import type { CaseReceiptsSummary, BillStatus } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { getBillStatusText } from '../../../constants/displayText'

const props = defineProps<{
  caseId: number | string
}>()

const router = useRouter()

const receipts = ref<CaseReceiptsSummary | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)

const hasEnrichedFields = computed(() => {
  if (!receipts.value) return false
  return !!(
    receipts.value.fee_code ||
    receipts.value.fee_type ||
    receipts.value.year_no != null ||
    receipts.value.invoice_no ||
    receipts.value.is_arrears != null ||
    receipts.value.is_commissionable != null
  )
})

async function fetchReceipts() {
  if (!props.caseId) return

  loading.value = true
  error.value = null

  try {
    receipts.value = await getCaseReceipts(props.caseId)
  } catch (err) {
    const apiError = err as ApiError
    // 404 is expected when no receipts exist
    if (apiError.status === 404) {
      receipts.value = null
    } else {
      error.value = apiError
    }
  } finally {
    loading.value = false
  }
}

function formatAmount(amount: number): string {
  const curr = receipts.value?.currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(amount)
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

function statusTagType(status: BillStatus): 'info' | 'warning' | 'success' | 'danger' {
  switch (status) {
    case 'PAID': return 'success'
    case 'ISSUED': return 'warning'
    case 'VOID': return 'danger'
    default: return 'info'
  }
}

function handleBillClick(row: { id: string }) {
  router.push(`/billing/bills/${row.id}`)
}

watch(() => props.caseId, () => {
  fetchReceipts()
})

onMounted(() => {
  fetchReceipts()
})
</script>

<style scoped>
.receipts-summary {
  padding: 16px 0;
}

.receipts-error {
  margin-bottom: 16px;
}

.receipts-loading {
  padding: 16px 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.card-label {
  font-size: 12px;
  color: var(--text-sub);
  margin-bottom: 8px;
}

.card-value {
  font-size: 20px;
  font-weight: 600;
}

.mono-num {
  font-family: var(--font-mono);
}

.text-success {
  color: var(--color-success);
}

.text-warning {
  color: var(--color-warning);
}

.bills-section {
  margin-top: 24px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.bill-no {
  font-family: var(--font-mono);
  font-weight: 500;
  color: var(--color-primary);
  cursor: pointer;
}

.bill-no:hover {
  text-decoration: underline;
}

.no-bills,
.no-data {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-sub);
}

.compact-table :deep(.el-table__row) {
  cursor: pointer;
}

.enriched-info {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--text-sub);
}

.info-value {
  font-size: 14px;
  color: var(--text-main);
}
</style>
