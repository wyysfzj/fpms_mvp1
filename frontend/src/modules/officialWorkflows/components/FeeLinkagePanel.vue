<template>
  <section class="case-panel fee-linkage-panel">
    <div class="panel-toolbar">
      <div>
        <h3 class="panel-heading">费用联动核对</h3>
        <p class="linkage-subtitle">区分内部费用草单、pay-list边界和官方缴费Excel模板准备状态。</p>
      </div>
      <div class="panel-actions">
        <el-tag :type="overallTagType" size="small">{{ overallStatusText }}</el-tag>
        <el-button size="small" :loading="loading" @click="fetchLinkage">刷新联动</el-button>
      </div>
    </div>

    <el-alert
      v-if="!packageId"
      type="info"
      :closable="false"
      title="请选择费用工作包"
      description="请从官方工作包入口进入，或在地址中带入 package_id。"
      show-icon
    />

    <div v-else-if="error" class="inline-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div v-else-if="loading" class="panel-loading">
      <el-skeleton :rows="6" animated />
    </div>

    <template v-else-if="linkage">
      <el-alert
        v-if="!linkage.official_excel_template_ready"
        type="warning"
        :closable="false"
        title="官方费率 / 费减清单来源待确认"
        description="内部 pay-list 和 GovPayment 只表示系统内缴费计划；在客户提供可读费率清单和官方模板样例前，不应把它视为官方上传 Excel。"
        show-icon
      />

      <div class="summary-grid">
        <div class="summary-card">
          <span>缴费执行模式</span>
          <strong>{{ getPaymentExecutionModeText(linkage.payment_execution_mode) }}</strong>
        </div>
        <div class="summary-card">
          <span>官方缴费Excel模板</span>
          <strong>{{ linkage.official_excel_template_ready ? '已确认' : '待确认' }}</strong>
        </div>
        <div class="summary-card">
          <span>Excel生成权限</span>
          <strong>{{ linkage.official_excel_generation_allowed ? '允许生成' : '未开放' }}</strong>
        </div>
        <div class="summary-card">
          <span>客户确认阻止项</span>
          <strong>{{ linkage.customer_confirmation_blockers.length }} 项</strong>
        </div>
      </div>

      <h4 class="subsection-title">内部费用草单</h4>
      <el-table :data="feeDraftRows" size="small" class="linkage-table">
        <el-table-column label="草单" min-width="150">
          <template #default="{ row }">
            <router-link class="entity-link" :to="`/fees/drafts/${row.id}?package_id=${packageId}`">
              {{ row.id }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" min-width="140" align="right">
          <template #default="{ row }">{{ formatMoney(row.amount, row.currency) }}</template>
        </el-table-column>
        <el-table-column label="客户减免比例" min-width="130">
          <template #default="{ row }">{{ row.customer_fee_reduction_ratio ?? '待确认' }}</template>
        </el-table-column>
        <el-table-column label="系统应缴比例" min-width="130">
          <template #default="{ row }">{{ row.payable_fee_ratio ?? '待确认' }}</template>
        </el-table-column>
        <el-table-column label="费减转换" min-width="150">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.fee_reduction_conversion_status)" size="small">
              {{ getStatusText(row.fee_reduction_conversion_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="费减说明" min-width="260">
          <template #default="{ row }">
            {{ row.fee_reduction_conversion_note || row.official_fee_reduction_note || '按客户答复规则核对费减比例。' }}
          </template>
        </el-table-column>
        <el-table-column label="模板状态" min-width="180">
          <template #default="{ row }">
            {{ getTemplateStatusText(row.official_template_status) }}
            <span v-if="row.official_template_version"> / {{ row.official_template_version }}</span>
          </template>
        </el-table-column>
        <el-table-column label="说明" min-width="220">
          <template #default="{ row }">{{ row.official_template_note || '按系统费用草单核对，不代表官方模板可用。' }}</template>
        </el-table-column>
      </el-table>

      <h4 class="subsection-title">pay-list边界</h4>
      <el-table :data="payListRows" size="small" class="linkage-table">
        <el-table-column label="内部清单" min-width="150">
          <template #default="{ row }">
            <router-link class="entity-link" :to="`/fee-management/pay-lists/${row.id}?package_id=${packageId}`">
              {{ row.pay_list_no || row.id }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" min-width="140" align="right">
          <template #default="{ row }">{{ formatMoney(row.total_amount, row.currency) }}</template>
        </el-table-column>
        <el-table-column label="官方模板" min-width="200">
          <template #default="{ row }">
            {{ getTemplateStatusText(row.official_upload_template_status) }}
            <span v-if="row.official_upload_template_name"> / {{ row.official_upload_template_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="批量上限" width="110">
          <template #default="{ row }">{{ row.official_upload_batch_limit || '待确认' }}</template>
        </el-table-column>
        <el-table-column label="边界说明" min-width="260">
          <template #default="{ row }">
            {{ row.official_pay_list_boundary_note || '内部 pay-list 不是官方上传 Excel；需另行确认官方模板。' }}
          </template>
        </el-table-column>
      </el-table>

      <h4 class="subsection-title">费用核对清单</h4>
      <el-table :data="linkage.checklist" size="small" class="linkage-table">
        <el-table-column prop="checklist_label" label="核对项" min-width="180" />
        <el-table-column label="要求" width="90">
          <template #default="{ row }">
            <el-tag :type="row.required ? 'danger' : 'info'" size="small">
              {{ row.required ? '必做' : '可选' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="阻止原因" min-width="220">
          <template #default="{ row }">{{ row.blocker_reason || '无' }}</template>
        </el-table-column>
      </el-table>

      <h4 class="subsection-title">客户确认阻止项</h4>
      <div v-if="linkage.customer_confirmation_blockers.length" class="blocker-list">
        <div
          v-for="blocker in linkage.customer_confirmation_blockers"
          :key="`${blocker.blocker_code}-${blocker.source_id || ''}`"
          class="blocker-item"
        >
          <div>
            <strong>{{ blocker.blocker_label }}</strong>
            <span>{{ blocker.message }}</span>
          </div>
          <el-tag :type="getStatusTagType(blocker.status)" size="small">{{ getStatusText(blocker.status) }}</el-tag>
        </div>
      </div>
      <el-empty v-else description="暂无客户确认阻止项" :image-size="72" />
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getOfficialFeeLinkage } from '../../../api/officialWorkflows'
import type {
  OfficialFeeLinkage,
  OfficialMoney,
} from '../../../api/officialWorkflows.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const props = withDefaults(defineProps<{
  packageId?: string
  focusId?: string
}>(), {
  packageId: '',
  focusId: '',
})

const linkage = ref<OfficialFeeLinkage | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)

const packageId = computed(() => String(props.packageId || '').trim())

const feeDraftRows = computed(() => prioritizeRows(linkage.value?.fee_drafts || []))
const payListRows = computed(() => prioritizeRows(linkage.value?.pay_lists || []))

const overallTagType = computed((): 'success' | 'warning' | 'danger' | 'info' => {
  if (!linkage.value) return 'info'
  if (linkage.value.customer_confirmation_blockers.length) return 'danger'
  if (!linkage.value.official_excel_template_ready) return 'warning'
  return 'success'
})

const overallStatusText = computed(() => {
  if (!linkage.value) return '待读取'
  if (linkage.value.customer_confirmation_blockers.length) return '存在阻止项'
  if (!linkage.value.official_excel_template_ready) return '模板待确认'
  return '已可核对'
})

watch(packageId, () => {
  void fetchLinkage()
})

onMounted(() => {
  void fetchLinkage()
})

async function fetchLinkage() {
  if (!packageId.value) {
    linkage.value = null
    return
  }

  loading.value = true
  error.value = null
  try {
    linkage.value = await getOfficialFeeLinkage(packageId.value)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function prioritizeRows<T extends { id: string | number }>(rows: T[]): T[] {
  if (!props.focusId) return rows
  const currentId = String(props.focusId)
  return [...rows].sort((left, right) => {
    const leftMatch = String(left.id) === currentId ? 0 : 1
    const rightMatch = String(right.id) === currentId ? 0 : 1
    return leftMatch - rightMatch
  })
}

function formatMoney(amount: OfficialMoney, currency: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(Number(amount || 0))
}

function getPaymentExecutionModeText(value?: string | null): string {
  const normalized = normalize(value)
  if (normalized === 'INTERNAL_PLAN_ONLY') return '仅内部计划'
  if (normalized === 'MANUAL_OFFICIAL_PAYMENT') return '人工官方缴费'
  if (normalized === 'OFFICIAL_TEMPLATE_READY') return '官方模板已确认'
  return value || '待确认'
}

function getTemplateStatusText(value?: string | null): string {
  const normalized = normalize(value)
  if (normalized === 'READY') return '已确认'
  if (normalized === 'MISSING') return '缺失'
  if (normalized === 'BLOCKED') return '阻止'
  if (normalized === 'PENDING' || normalized === 'NEEDS_CONFIRMATION') return '待确认'
  return value || '待确认'
}

function getStatusText(value?: string | null): string {
  const normalized = normalize(value)
  if (normalized === 'OPEN' || normalized === 'DRAFT') return '草稿'
  if (normalized === 'LOCKED') return '已锁定'
  if (normalized === 'EXPORTED') return '已导出'
  if (normalized === 'PAID') return '已缴费'
  if (normalized === 'READY' || normalized === 'DONE' || normalized === 'PASS' || normalized === 'CONFIRMED') return '已满足'
  if (normalized === 'MISSING' || normalized === 'NEEDS_MAINTENANCE') return '需维护'
  if (normalized === 'BLOCKED' || normalized === 'EXCEPTION') return '阻止'
  if (normalized === 'PENDING' || normalized === 'NEEDS_CONFIRMATION') return '待确认'
  return value || '待核对'
}

function getStatusTagType(value?: string | null): 'success' | 'warning' | 'danger' | 'info' {
  const normalized = normalize(value)
  if (normalized === 'READY' || normalized === 'DONE' || normalized === 'PASS' || normalized === 'PAID' || normalized === 'CONFIRMED') return 'success'
  if (normalized === 'MISSING' || normalized === 'NEEDS_MAINTENANCE' || normalized === 'BLOCKED' || normalized === 'EXCEPTION') return 'danger'
  if (normalized === 'PENDING' || normalized === 'NEEDS_CONFIRMATION' || normalized === 'EXPORTED') return 'warning'
  return 'info'
}

function normalize(value?: string | null): string {
  return String(value || '').trim().toUpperCase()
}
</script>

<style scoped>
.fee-linkage-panel {
  display: grid;
  gap: 16px;
}

.linkage-subtitle {
  margin: -6px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.panel-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.inline-error,
.panel-loading {
  min-height: 80px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  display: grid;
  gap: 6px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.summary-card span {
  color: var(--text-sub);
  font-size: 12px;
}

.summary-card strong {
  color: var(--text-main);
  font-size: 14px;
  overflow-wrap: anywhere;
}

.subsection-title {
  margin: 2px 0 0;
  color: var(--text-main);
  font-size: 15px;
}

.linkage-table {
  width: 100%;
}

.entity-link {
  color: var(--color-primary);
  font-family: var(--font-mono);
  text-decoration: none;
}

.blocker-list {
  display: grid;
  gap: 10px;
}

.blocker-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  background: #f8fafc;
}

.blocker-item div {
  display: grid;
  gap: 4px;
}

.blocker-item span {
  color: var(--text-sub);
  font-size: 12px;
}

@media (max-width: 1180px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .panel-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
