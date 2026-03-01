<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">顾问/检索服务费草单生成</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="goBack">返回</el-button>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-card shadow="never" class="form-card">
      <template #header>
        <div class="form-card-title">参数设置</div>
      </template>

      <el-form label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="案件 ID">
              <el-input v-model.trim="form.case_id" placeholder="请输入案件 ID" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="生成模式">
              <el-select v-model="form.mode" placeholder="请选择模式">
                <el-option label="固定模式（FIXED）" value="FIXED" />
                <el-option label="工时模式（HOURLY）" value="HOURLY" />
                <el-option label="混合模式（HYBRID）" value="HYBRID" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="币种">
              <el-input v-model.trim="form.currency" placeholder="默认 CNY（可选）" />
            </el-form-item>
          </el-col>

          <el-col v-if="showFixedFee" :xs="24" :sm="12" :md="8">
            <el-form-item :label="form.mode === 'HYBRID' ? '固定费用（可为 0）' : '固定费用（必须大于 0）'">
              <el-input-number
                v-model="form.fixed_fee"
                :min="0"
                :precision="2"
                :step="100"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div v-if="showHourlyLines" class="line-section">
          <div class="line-section-header">
            <h3 class="line-section-title">工时行</h3>
            <el-button size="small" @click="addHourlyLine">新增工时行</el-button>
          </div>

          <div v-if="form.hourly_lines.length === 0" class="section-empty">
            当前无工时行，请点击“新增工时行”。
          </div>

          <div v-for="(line, index) in form.hourly_lines" :key="line.key" class="line-card">
            <div class="line-card-header">
              <span>工时行 #{{ index + 1 }}</span>
              <el-button text type="danger" @click="removeHourlyLine(index)">删除</el-button>
            </div>
            <el-row :gutter="8">
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="费用代码">
                  <el-input v-model.trim="line.fee_code" placeholder="例如：CONSULT_HOUR" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="费用名称">
                  <el-input v-model.trim="line.fee_name" placeholder="例如：顾问工时费" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="4">
                <el-form-item label="工时">
                  <el-input-number v-model="line.hours" :min="0" :step="0.5" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="4">
                <el-form-item label="小时单价">
                  <el-input-number v-model="line.hourly_rate" :min="0" :step="100" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="4">
                <el-form-item label="追踪键">
                  <el-input v-model.trim="line.trace_key" placeholder="可选" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="备注">
                  <el-input v-model.trim="line.remark" placeholder="可选" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>

        <div class="line-section">
          <div class="line-section-header">
            <h3 class="line-section-title">杂费行（可选）</h3>
            <el-button size="small" @click="addMiscLine">新增杂费行</el-button>
          </div>

          <div v-if="form.misc_lines.length === 0" class="section-empty">
            当前无杂费行。
          </div>

          <div v-for="(line, index) in form.misc_lines" :key="line.key" class="line-card">
            <div class="line-card-header">
              <span>杂费行 #{{ index + 1 }}</span>
              <el-button text type="danger" @click="removeMiscLine(index)">删除</el-button>
            </div>
            <el-row :gutter="8">
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="费用代码">
                  <el-input v-model.trim="line.fee_code" placeholder="例如：SEARCH_MISC" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <el-form-item label="费用名称">
                  <el-input v-model.trim="line.fee_name" placeholder="例如：检索附加费" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="4">
                <el-form-item label="金额">
                  <el-input-number v-model="line.amount" :min="0" :step="100" :precision="2" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="4">
                <el-form-item label="追踪键">
                  <el-input v-model.trim="line.trace_key" placeholder="可选" />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="备注">
                  <el-input v-model.trim="line.remark" placeholder="可选" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </div>

        <div class="action-row">
          <el-button @click="resetForm">重置</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            生成服务费草单
          </el-button>
        </div>
      </el-form>
    </el-card>

    <el-card v-if="result" shadow="never" class="result-card">
      <template #header>
        <div class="form-card-title">生成结果</div>
      </template>

      <el-descriptions :column="4" border>
        <el-descriptions-item label="草单 ID">{{ result.draft_id }}</el-descriptions-item>
        <el-descriptions-item label="草单类型">{{ result.draft_type }}</el-descriptions-item>
        <el-descriptions-item label="模式">{{ result.mode }}</el-descriptions-item>
        <el-descriptions-item label="币种">{{ result.currency }}</el-descriptions-item>
        <el-descriptions-item label="行数">{{ result.created_line_count }}</el-descriptions-item>
        <el-descriptions-item label="服务费合计">
          {{ formatMoney(result.totals.total_service, result.currency) }}
        </el-descriptions-item>
        <el-descriptions-item label="杂费合计">
          {{ formatMoney(result.totals.total_misc, result.currency) }}
        </el-descriptions-item>
        <el-descriptions-item label="总金额">
          {{ formatMoney(result.totals.amount, result.currency) }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="line-section">
        <h3 class="line-section-title">草单明细</h3>
        <el-table :data="result.items" size="small" border>
          <el-table-column prop="item_id" label="费用项 ID" min-width="200" />
          <el-table-column prop="fee_code" label="费用代码" min-width="140" />
          <el-table-column prop="fee_name" label="费用名称" min-width="160" />
          <el-table-column prop="fee_type" label="费用类型" width="100" />
          <el-table-column prop="quantity" label="数量" width="90" />
          <el-table-column prop="unit_price" label="单价" width="120" />
          <el-table-column label="金额" width="140" align="right">
            <template #default="{ row }">
              {{ formatMoney(row.amount, result.currency) }}
            </template>
          </el-table-column>
          <el-table-column prop="trace_key" label="追踪键" min-width="160" />
          <el-table-column prop="remark" label="备注" min-width="180">
            <template #default="{ row }">
              {{ row.remark || '—' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </main>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { http } from '../../../api/http'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

type DraftMode = 'FIXED' | 'HOURLY' | 'HYBRID'

interface HourlyLineForm {
  key: number
  fee_code: string
  fee_name: string
  hours: number
  hourly_rate: number
  remark: string
  trace_key: string
}

interface MiscLineForm {
  key: number
  fee_code: string
  fee_name: string
  amount: number
  remark: string
  trace_key: string
}

interface ConsultingFeeDraftCreatePayload {
  case_id: string
  mode: DraftMode
  currency?: string
  fixed_fee?: number
  hourly_lines?: Array<{
    fee_code: string
    fee_name: string
    hours: number
    hourly_rate: number
    remark?: string
    trace_key?: string
  }>
  misc_lines?: Array<{
    fee_code: string
    fee_name: string
    amount: number
    remark?: string
    trace_key?: string
  }>
}

interface ConsultingFeeDraftResult {
  draft_id: string
  draft_type: 'CONSULT_FEE' | 'SEARCH_FEE'
  mode: DraftMode
  currency: string
  totals: {
    total_gov: number
    total_service: number
    total_misc: number
    amount: number
  }
  items: Array<{
    item_id: string
    fee_code: string | null
    fee_name: string | null
    fee_type: string
    quantity: number | null
    unit_price: number | null
    amount: number
    trace_key: string
    remark: string | null
  }>
  created_line_count: number
}

interface BackendConsultingFeeDraftResult {
  draft_id: string
  draft_type: 'CONSULT_FEE' | 'SEARCH_FEE'
  mode: DraftMode
  currency: string
  totals: {
    total_gov: number | string | null
    total_service: number | string | null
    total_misc: number | string | null
    amount: number | string | null
  }
  items: Array<{
    item_id: string
    fee_code: string | null
    fee_name: string | null
    fee_type: string
    quantity: number | string | null
    unit_price: number | string | null
    amount: number | string | null
    trace_key: string
    remark: string | null
  }>
  created_line_count: number
}

const router = useRouter()
const submitting = ref(false)
const error = ref<ApiError | null>(null)
const result = ref<ConsultingFeeDraftResult | null>(null)
const seed = ref(1)

const form = reactive<{
  case_id: string
  mode: DraftMode
  currency: string
  fixed_fee: number
  hourly_lines: HourlyLineForm[]
  misc_lines: MiscLineForm[]
}>({
  case_id: '',
  mode: 'FIXED',
  currency: 'CNY',
  fixed_fee: 0,
  hourly_lines: [],
  misc_lines: [],
})

const showFixedFee = computed(() => form.mode === 'FIXED' || form.mode === 'HYBRID')
const showHourlyLines = computed(() => form.mode === 'HOURLY' || form.mode === 'HYBRID')

function nextKey(): number {
  seed.value += 1
  return seed.value
}

function addHourlyLine() {
  form.hourly_lines.push({
    key: nextKey(),
    fee_code: '',
    fee_name: '',
    hours: 1,
    hourly_rate: 0,
    remark: '',
    trace_key: '',
  })
}

function removeHourlyLine(index: number) {
  form.hourly_lines.splice(index, 1)
}

function addMiscLine() {
  form.misc_lines.push({
    key: nextKey(),
    fee_code: '',
    fee_name: '',
    amount: 0,
    remark: '',
    trace_key: '',
  })
}

function removeMiscLine(index: number) {
  form.misc_lines.splice(index, 1)
}

function resetForm() {
  form.case_id = ''
  form.mode = 'FIXED'
  form.currency = 'CNY'
  form.fixed_fee = 0
  form.hourly_lines = []
  form.misc_lines = []
  error.value = null
}

function toApiError(errorLike: unknown): ApiError | null {
  if (!errorLike || typeof errorLike !== 'object') return null
  const candidate = errorLike as Partial<ApiError>
  if (typeof candidate.status !== 'number') return null
  if (typeof candidate.code !== 'string') return null
  if (typeof candidate.message !== 'string') return null
  return candidate as ApiError
}

function mapDraftCreateError(errorLike: unknown): string {
  const apiError = toApiError(errorLike)
  if (!apiError || apiError.status === 0) {
    return '网络异常或服务不可用，请稍后重试。'
  }

  if (apiError.status === 400 && apiError.code === 'CONSULTING_FEE_INVALID') {
    return '草单参数不合法，请检查模式与金额/工时配置。'
  }
  if (apiError.status === 404 && apiError.code === 'CASE_NOT_FOUND') {
    return '案件不存在，请确认案件 ID 后重试。'
  }
  if (apiError.status === 409 && apiError.code === 'FEE_DRAFT_CONFLICT') {
    const draftId = apiError.details?.draft_id
    return typeof draftId === 'string'
      ? `当前案件已有开启中的草单（${draftId}），请先处理冲突。`
      : '当前案件已有开启中的草单，请先处理冲突。'
  }
  if (apiError.status === 401) return '登录已失效，请重新登录后重试。'
  if (apiError.status === 403) return '无权限生成顾问/检索服务费草单。'
  if (apiError.status === 422) return '请求参数校验失败，请检查输入格式。'

  return '生成草单失败，请稍后重试。'
}

function mapErrorToBanner(errorLike: unknown, message: string): ApiError {
  const apiError = toApiError(errorLike)
  if (apiError) {
    return {
      ...apiError,
      message,
    }
  }
  return {
    status: 0,
    code: 'UNKNOWN_ERROR',
    message,
  }
}

function validateFormState(): string | null {
  if (!form.case_id.trim()) return '请填写案件 ID。'

  if (form.mode === 'FIXED') {
    if (!(form.fixed_fee > 0)) return '固定模式下固定费用必须大于 0。'
  }

  if (form.mode === 'HOURLY' || form.mode === 'HYBRID') {
    if (form.hourly_lines.length === 0) return '工时模式/混合模式至少需要一条工时行。'

    for (let i = 0; i < form.hourly_lines.length; i += 1) {
      const line = form.hourly_lines[i]
      if (!line.fee_code.trim() || !line.fee_name.trim()) {
        return `工时行 #${i + 1} 的费用代码和费用名称不能为空。`
      }
      if (!(line.hours > 0)) {
        return `工时行 #${i + 1} 的工时必须大于 0。`
      }
      if (line.hourly_rate < 0) {
        return `工时行 #${i + 1} 的小时单价不能为负数。`
      }
    }
  }

  if (form.mode === 'HYBRID' && form.fixed_fee < 0) {
    return '混合模式下固定费用不能小于 0。'
  }

  for (let i = 0; i < form.misc_lines.length; i += 1) {
    const line = form.misc_lines[i]
    if (!line.fee_code.trim() || !line.fee_name.trim()) {
      return `杂费行 #${i + 1} 的费用代码和费用名称不能为空。`
    }
    if (line.amount < 0) {
      return `杂费行 #${i + 1} 的金额不能为负数。`
    }
  }

  if (form.mode === 'HYBRID') {
    const hourlyTotal = form.hourly_lines.reduce(
      (sum, line) => sum + line.hours * line.hourly_rate,
      0,
    )
    const miscTotal = form.misc_lines.reduce((sum, line) => sum + line.amount, 0)
    if (form.fixed_fee + hourlyTotal + miscTotal <= 0) {
      return '混合模式总金额必须大于 0。'
    }
  }

  return null
}

function buildPayload(): ConsultingFeeDraftCreatePayload {
  const payload: ConsultingFeeDraftCreatePayload = {
    case_id: form.case_id.trim(),
    mode: form.mode,
    currency: form.currency.trim() || undefined,
  }

  if (form.mode === 'FIXED' || form.mode === 'HYBRID') {
    payload.fixed_fee = form.fixed_fee
  }

  if (form.mode === 'HOURLY' || form.mode === 'HYBRID') {
    payload.hourly_lines = form.hourly_lines.map((line) => ({
      fee_code: line.fee_code.trim(),
      fee_name: line.fee_name.trim(),
      hours: line.hours,
      hourly_rate: line.hourly_rate,
      remark: line.remark.trim() || undefined,
      trace_key: line.trace_key.trim() || undefined,
    }))
  }

  if (form.misc_lines.length > 0) {
    payload.misc_lines = form.misc_lines.map((line) => ({
      fee_code: line.fee_code.trim(),
      fee_name: line.fee_name.trim(),
      amount: line.amount,
      remark: line.remark.trim() || undefined,
      trace_key: line.trace_key.trim() || undefined,
    }))
  }

  return payload
}

function asNumber(input: number | string | null | undefined): number {
  if (input === null || input === undefined || input === '') return 0
  const parsed = Number(input)
  return Number.isFinite(parsed) ? parsed : 0
}

function mapDraftResult(raw: BackendConsultingFeeDraftResult): ConsultingFeeDraftResult {
  return {
    draft_id: String(raw.draft_id),
    draft_type: raw.draft_type,
    mode: raw.mode,
    currency: raw.currency,
    totals: {
      total_gov: asNumber(raw.totals?.total_gov),
      total_service: asNumber(raw.totals?.total_service),
      total_misc: asNumber(raw.totals?.total_misc),
      amount: asNumber(raw.totals?.amount),
    },
    items: Array.isArray(raw.items)
      ? raw.items.map((item) => ({
        item_id: String(item.item_id),
        fee_code: item.fee_code ?? null,
        fee_name: item.fee_name ?? null,
        fee_type: String(item.fee_type),
        quantity: item.quantity == null ? null : asNumber(item.quantity),
        unit_price: item.unit_price == null ? null : asNumber(item.unit_price),
        amount: asNumber(item.amount),
        trace_key: String(item.trace_key),
        remark: item.remark ?? null,
      }))
      : [],
    created_line_count: Number(raw.created_line_count || 0),
  }
}

function formatMoney(amount: number, currency: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(amount || 0)
}

function goBack() {
  router.back()
}

async function handleSubmit() {
  const validationMessage = validateFormState()
  if (validationMessage) {
    ElMessage.error(validationMessage)
    return
  }

  submitting.value = true
  error.value = null
  try {
    const response = await http.post<BackendConsultingFeeDraftResult>(
      '/consulting/fee-drafts',
      buildPayload(),
    )
    result.value = mapDraftResult(response.data)
    ElMessage.success('服务费草单生成成功。')
  } catch (err) {
    const message = mapDraftCreateError(err)
    error.value = mapErrorToBanner(err, message)
    ElMessage.error(message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-card,
.result-card {
  margin-top: 16px;
}

.form-card-title {
  font-weight: 600;
}

.line-section {
  margin-top: 16px;
}

.line-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.line-section-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.section-empty {
  padding: 12px;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  color: var(--text-sub);
  margin-bottom: 8px;
}

.line-card {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
}

.line-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.action-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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
