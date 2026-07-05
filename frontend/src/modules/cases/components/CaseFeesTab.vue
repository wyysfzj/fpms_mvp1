<template>
  <div class="case-panel official-fee-node-panel">
    <div class="panel-toolbar official-fee-node-header">
      <div>
        <h3 class="panel-heading">官费节点线</h3>
        <p class="official-fee-node-hint">
          根据案件字段和费率参数预览受理/新申请阶段官费候选，预览不会写入草稿或官费清单。
        </p>
      </div>
      <el-tag :type="nodeTagType" size="small">{{ nodeStatusText }}</el-tag>
    </div>

    <div v-if="previewLoading" class="muted">官费节点加载中...</div>
    <el-alert
      v-else-if="previewError"
      :title="previewErrorTitle"
      :description="previewErrorDescription"
      type="warning"
      show-icon
      :closable="false"
      class="official-fee-node-alert"
    />
    <div v-else-if="preview" class="official-fee-node-body">
      <div class="official-fee-node-summary">
        <div class="official-fee-node-summary-item">
          <span class="official-fee-node-label">节点</span>
          <strong>申请/受理官费候选</strong>
        </div>
        <div class="official-fee-node-summary-item">
          <span class="official-fee-node-label">候选官费合计</span>
          <strong>{{ formatMoney(preview.total_gov, preview.currency) }}</strong>
        </div>
        <div class="official-fee-node-summary-item">
          <span class="official-fee-node-label">费用草稿状态</span>
          <strong>{{ draftStatusSummary }}</strong>
        </div>
        <div class="official-fee-node-summary-item official-fee-node-wide">
          <span class="official-fee-node-label">去重键</span>
          <span class="official-fee-node-mono">{{ preview.idempotency_key }}</span>
        </div>
      </div>

      <el-table
        v-if="preview.candidates.length"
        :data="preview.candidates"
        size="small"
        stripe
        class="official-fee-node-table"
      >
        <el-table-column label="官费项目" min-width="180">
          <template #default="{ row }">
            <div class="official-fee-item-name">{{ row.fee_name || row.fee_code }}</div>
            <div class="official-fee-item-code">{{ row.fee_code }}</div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="90">
          <template #default="{ row }">{{ getFeeTypeText(row.fee_type) }}</template>
        </el-table-column>
        <el-table-column label="数量" width="90">
          <template #default="{ row }">{{ row.quantity }}</template>
        </el-table-column>
        <el-table-column label="单价" width="120">
          <template #default="{ row }">{{ formatMoney(row.unit_price, preview?.currency) }}</template>
        </el-table-column>
        <el-table-column label="金额" width="120">
          <template #default="{ row }">{{ formatMoney(row.amount, preview?.currency) }}</template>
        </el-table-column>
        <el-table-column label="计算依据" min-width="210">
          <template #default="{ row }">{{ formatCalculationNote(row.calculation_note) }}</template>
        </el-table-column>
        <el-table-column label="来源" min-width="190">
          <template #default="{ row }">
            <div>{{ row.source_doc || '费率参数表' }}</div>
            <div class="official-fee-source-status">{{ formatSourceStatus(row.source_status) }}</div>
          </template>
        </el-table-column>
      </el-table>
      <div v-else class="placeholder-content">
        <p>当前节点暂无可预览的官费候选。</p>
      </div>
    </div>
  </div>

  <div class="case-panel">
    <div class="panel-toolbar">
      <h3 class="panel-heading">费用记录</h3>
      <el-button type="primary" size="small" @click="handleCreate">创建费用草稿</el-button>
    </div>
    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="items.length === 0" class="placeholder-content">
      <p>暂无费用记录</p>
    </div>
    <el-table v-else :data="items" stripe style="width: 100%">
      <el-table-column label="草稿类型" width="120">
        <template #default="{ row }">
          {{ formatDraftType(row.draft_type) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'LOCKED' ? 'danger' : 'success'" size="small">
            {{ getFeeDraftStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="currency" label="币种" width="80" />
      <el-table-column label="总金额" width="140">
        <template #default="{ row }">
          {{ row.amount }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFeeDrafts, previewOfficialFeeCandidates } from '../../../api/fees'
import type { FeeDraftListItem, OfficialFeePreview } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import { getFeeDraftStatusText, getFeeDraftTypeText, getFeeTypeText } from '../../../constants/displayText'
import { formatMoney } from '../../../utils/money'

const props = defineProps<{
  caseId: string
}>()

const router = useRouter()
const items = ref<FeeDraftListItem[]>([])
const loading = ref(true)
const preview = ref<OfficialFeePreview | null>(null)
const previewLoading = ref(true)
const previewError = ref<ApiError | null>(null)

onMounted(async () => {
  await Promise.all([loadOfficialFeePreview(), loadFeeDrafts()])
})

const draftStatusSummary = computed(() => {
  if (loading.value) return '草稿加载中'
  if (!items.value.length) return '尚未生成草稿'
  const statusTexts = Array.from(new Set(items.value.map((item) => getFeeDraftStatusText(item.status))))
  return `已有 ${items.value.length} 个费用草稿（${statusTexts.join('、')}）`
})

const nodeStatusText = computed(() => {
  if (previewLoading.value || loading.value) return '加载中'
  if (items.value.length) return '已有费用草稿'
  if (preview.value?.candidates.length) return '候选待确认'
  if (previewError.value?.status === 409) return '缺少费率'
  if (previewError.value) return '待确认'
  return '暂无候选'
})

const nodeTagType = computed(() => {
  if (previewLoading.value || loading.value) return 'info'
  if (items.value.length) return 'success'
  if (preview.value?.candidates.length) return 'warning'
  if (previewError.value) return 'danger'
  return 'info'
})

const previewErrorTitle = computed(() => {
  if (previewError.value?.status === 409) return '官费节点缺少费率配置'
  if (previewError.value?.code === 'APPLY_FEE_UNSUPPORTED_CASE') return '当前案件暂不支持自动预览'
  if (previewError.value?.code === 'OFFICIAL_FEE_PREVIEW_TRIGGER_UNSUPPORTED') return '当前触发节点暂未启用'
  return '官费节点待确认'
})

const previewErrorDescription = computed(() => {
  const error = previewError.value
  if (!error) return ''
  if (error.status === 409) {
    const missing = Array.isArray(error.details?.missing_fee_codes)
      ? error.details?.missing_fee_codes.join('、')
      : '必要官费项目'
    return `请先在费率参数表维护并启用：${missing}。`
  }
  if (error.code === 'APPLY_FEE_UNSUPPORTED_CASE') {
    return '本轮仅对国内普通申请的申请/受理官费提供候选预览，其他场景需要客户确认后再启用。'
  }
  return '请确认案件字段、触发节点和费率来源后再生成费用草稿。'
})

async function loadFeeDrafts() {
  try {
    const res = await getFeeDrafts({ case_id: props.caseId, page: 1, page_size: 50 })
    items.value = res.items
  } catch {
    // silently fail
  } finally {
    loading.value = false
  }
}

async function loadOfficialFeePreview() {
  previewLoading.value = true
  previewError.value = null
  try {
    preview.value = await previewOfficialFeeCandidates({
      case_id: props.caseId,
      trigger_event: 'FILING_ACCEPTED',
      currency: 'CNY',
    })
  } catch (error) {
    preview.value = null
    previewError.value = error as ApiError
  } finally {
    previewLoading.value = false
  }
}

function handleCreate() {
  router.push(`/fees/drafts/new?case_id=${props.caseId}&draft_type=APPLY_FEE`)
}

function formatDraftType(type?: string | null): string {
  return type ? getFeeDraftTypeText(type) : '费用草稿'
}

function formatCalculationNote(note?: string | null): string {
  const normalized = note || ''
  const notes: Record<string, string> = {
    'application official fee': '申请费，按案件专利类型和费减比例计算',
    'excess claim official fee': '权利要求超过 10 项后按项计算',
    'publication printing official fee': '发明公布印刷费',
    'substantive exam official fee': '发明实质审查费，按是否同时请求实审计算',
  }
  return notes[normalized] || normalized || '按官费参数表计算'
}

function formatSourceStatus(status?: string | null): string {
  const normalized = (status || '').toUpperCase()
  if (normalized === 'CONFIRMED') return '来源状态：已确认'
  if (normalized === 'PENDING') return '来源状态：待确认'
  if (normalized === 'DISABLED') return '来源状态：未启用'
  return '来源状态：未标记'
}
</script>

<style scoped>
.official-fee-node-panel {
  margin-bottom: 16px;
}

.official-fee-node-header {
  align-items: flex-start;
}

.official-fee-node-hint {
  margin: 4px 0 0;
  color: var(--text-sub, #64748b);
  font-size: 13px;
  line-height: 1.5;
}

.official-fee-node-alert {
  margin-top: 12px;
}

.official-fee-node-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.official-fee-node-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.official-fee-node-summary-item {
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  padding: 12px;
  background: var(--color-bg-body, #f8fafc);
}

.official-fee-node-wide {
  grid-column: 1 / -1;
}

.official-fee-node-label {
  display: block;
  margin-bottom: 4px;
  color: var(--text-sub, #64748b);
  font-size: 12px;
}

.official-fee-node-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  word-break: break-all;
}

.official-fee-node-table {
  width: 100%;
}

.official-fee-item-name {
  font-weight: 600;
}

.official-fee-item-code,
.official-fee-source-status {
  margin-top: 2px;
  color: var(--text-sub, #64748b);
  font-size: 12px;
}

@media (max-width: 900px) {
  .official-fee-node-summary {
    grid-template-columns: 1fr;
  }
}
</style>
