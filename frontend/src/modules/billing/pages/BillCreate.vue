<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回
        </el-button>
      </div>
    </div>

    <div class="page-error" v-if="error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div class="form-card">
      <h2 class="form-card-title">创建账单</h2>

      <el-tabs v-model="activeTab" class="create-tabs">
        <!-- From Drafts Tab -->
        <el-tab-pane label="从费用草稿生成" name="drafts">
          <el-form
            ref="draftsFormRef"
            :model="draftsForm"
            label-position="top"
            class="bill-form"
          >
            <div class="form-section">
              <h3 class="form-section-title">选择费用草稿</h3>
              <p class="form-section-desc">
                请选择已锁定且已有费用明细的草稿，系统会根据所选草稿生成账单。
              </p>

              <el-form-item
                label="费用草稿"
                prop="draft_ids"
                :error="fieldErrors.get('draft_ids')?.join(', ')"
              >
                <el-select
                  v-model="draftsForm.draft_ids"
                  multiple
                  filterable
                  collapse-tags
                  collapse-tags-tooltip
                  clearable
                  :loading="draftOptionsLoading"
                  :no-data-text="draftOptionsLoading ? '正在加载可开票草稿…' : '暂无可用于开票的锁定草稿'"
                  placeholder="请选择已锁定且可开票的费用草稿"
                  class="full-width"
                >
                  <el-option
                    v-for="option in availableDraftOptions"
                    :key="option.id"
                    :label="option.displayLabel"
                    :value="option.id"
                  >
                    <div class="draft-option">
                      <div class="draft-option-main">
                        <span class="draft-option-id">{{ option.displayId }}</span>
                        <span class="draft-option-case">{{ option.caseDisplay }}</span>
                      </div>
                      <div class="draft-option-sub">
                        <span>{{ option.clientDisplay }}</span>
                        <span>{{ option.amountDisplay }}</span>
                      </div>
                    </div>
                  </el-option>
                </el-select>
                <div class="field-hint">
                  仅展示“已锁定”且金额大于 0 的草稿。
                  <router-link to="/fees/drafts">查看费用草稿列表</router-link>
                </div>
              </el-form-item>

              <el-form-item
                label="币种"
                prop="currency"
                :error="fieldErrors.get('currency')?.join(', ')"
              >
                <el-select v-model="draftsForm.currency" placeholder="请选择币种" class="full-width">
                  <el-option label="CNY" value="CNY" />
                  <el-option label="USD" value="USD" />
                  <el-option label="EUR" value="EUR" />
                </el-select>
              </el-form-item>

              <el-form-item label="备注" prop="notes">
                <el-input
                  v-model="draftsForm.notes"
                  type="textarea"
                  :rows="3"
                  placeholder="账单备注（可选）"
                />
              </el-form-item>
            </div>

            <div class="form-actions">
              <el-button @click="goBack">取消</el-button>
              <el-button
                type="primary"
                :loading="saving"
                :disabled="draftsForm.draft_ids.length === 0"
                @click="handleCreateFromDrafts"
              >
                创建账单
              </el-button>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- Manual Tab -->
        <el-tab-pane label="手工录入" name="manual">
          <el-form
            ref="manualFormRef"
            :model="manualForm"
            :rules="manualRules"
            label-position="top"
            class="bill-form"
          >
            <div class="form-section">
              <h3 class="form-section-title">账单信息</h3>

              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item
                    label="客户编号"
                    prop="client_id"
                    :error="fieldErrors.get('client_id')?.join(', ')"
                  >
                    <el-select
                      v-model="manualForm.client_id"
                      filterable
                      clearable
                      :loading="clientOptionsLoading"
                      class="full-width"
                      placeholder="请选择客户"
                    >
                      <el-option
                        v-for="client in clientOptions"
                        :key="client.id"
                        :label="formatClientOption(client)"
                        :value="client.id"
                      />
                    </el-select>
                    <div class="field-hint">
                      <router-link to="/clients">查看客户列表</router-link>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item
                    label="案件编号（可选）"
                    prop="case_id"
                    :error="fieldErrors.get('case_id')?.join(', ')"
                  >
                    <el-select
                      v-model="manualForm.case_id"
                      filterable
                      clearable
                      :disabled="!manualForm.client_id"
                      :loading="caseOptionsLoading"
                      class="full-width"
                      placeholder="请选择案件（可选）"
                    >
                      <el-option
                        v-for="caseItem in caseOptions"
                        :key="caseItem.id"
                        :label="formatCaseOption(caseItem)"
                        :value="caseItem.id"
                      />
                    </el-select>
                    <div class="field-hint">
                      <router-link to="/cases">查看案件列表</router-link>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item
                    label="币种"
                    prop="currency"
                    :error="fieldErrors.get('currency')?.join(', ')"
                  >
                    <el-select v-model="manualForm.currency" placeholder="请选择币种" class="full-width">
                      <el-option label="CNY" value="CNY" />
                      <el-option label="USD" value="USD" />
                      <el-option label="EUR" value="EUR" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item
                    label="账单方向"
                    prop="direction"
                    :error="fieldErrors.get('direction')?.join(', ')"
                  >
                    <el-select v-model="manualForm.direction" placeholder="请选择账单方向" class="full-width">
                      <el-option
                        v-for="option in directionOptions"
                        :key="option.value"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                    <div class="field-hint">
                      应收账单用于向客户收款，应付账单用于记录需对外支付的款项。
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>
            </div>

            <div class="form-section">
              <h3 class="form-section-title">账单明细</h3>

              <el-table :data="manualForm.items" stripe size="small" class="items-table">
                <el-table-column label="描述" min-width="200">
                  <template #default="{ row, $index }">
                    <el-input
                      v-model="row.description"
                      placeholder="明细描述"
                      size="small"
                      :class="{ 'is-error': getItemError($index, 'description') }"
                    />
                  </template>
                </el-table-column>
                <el-table-column label="数量" width="100">
                  <template #default="{ row }">
                    <el-input-number
                      v-model="row.quantity"
                      :min="1"
                      :precision="0"
                      size="small"
                      controls-position="right"
                    />
                  </template>
                </el-table-column>
                <el-table-column label="单价" width="140">
                  <template #default="{ row }">
                    <el-input-number
                      v-model="row.unit_price"
                      :min="0"
                      :precision="2"
                      size="small"
                      controls-position="right"
                    />
                  </template>
                </el-table-column>
                <el-table-column label="金额" width="120" align="right">
                  <template #default="{ row }">
                    <span class="mono-num">{{ formatAmount(row.quantity * row.unit_price) }}</span>
                  </template>
                </el-table-column>
                <el-table-column width="60" align="center">
                  <template #default="{ $index }">
                    <el-button
                      v-if="manualForm.items.length > 1"
                      type="danger"
                      text
                      size="small"
                      @click="removeItem($index)"
                    >
                      ×
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <div class="items-footer">
                <el-button size="small" @click="addItem">+ 添加明细</el-button>
                <div class="items-total">
                  <span class="total-label">合计：</span>
                  <span class="total-value mono-num">{{ formatAmount(totalAmount) }}</span>
                </div>
              </div>
            </div>

            <div class="form-section">
              <el-form-item label="备注" prop="notes">
                <el-input
                  v-model="manualForm.notes"
                  type="textarea"
                  :rows="3"
                  placeholder="账单备注（可选）"
                />
              </el-form-item>
            </div>

            <div class="form-actions">
              <el-button @click="goBack">取消</el-button>
              <el-button
                type="primary"
                :loading="saving"
                :disabled="manualForm.items.length === 0 || !manualForm.client_id"
                @click="handleCreateManual"
              >
                创建账单
              </el-button>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { createBillFromDrafts, createManualBill } from '../../../api/billing'
import type { BillFromDraftsPayload, BillManualPayload, BillManualItem, BillDirection } from '../../../api/billing.types'
import { getFeeDrafts } from '../../../api/fees'
import type { FeeDraftListItem } from '../../../api/fees.types'
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import { getCases } from '../../../api/cases'
import type { Case } from '../../../api/cases.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const router = useRouter()

const activeTab = ref('drafts')
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const draftOptionsLoading = ref(false)
const availableDrafts = ref<FeeDraftListItem[]>([])
const clientOptionsLoading = ref(false)
const caseOptionsLoading = ref(false)
const clientOptions = ref<Client[]>([])
const caseOptions = ref<Case[]>([])

const draftsFormRef = ref<FormInstance>()
const manualFormRef = ref<FormInstance>()

// Form for creating from drafts
const draftsForm = reactive({
  draft_ids: [] as string[],
  currency: 'CNY',
  notes: '',
})

// Form for manual creation
const manualForm = reactive({
  client_id: '',
  case_id: '',
  currency: 'CNY',
  direction: 'AR' as BillDirection,
  items: [{ description: '', quantity: 1, unit_price: 0, fee_type: '', year_no: undefined }] as BillManualItem[],
  notes: '',
})

const directionOptions = [
  { label: '应收账单', value: 'AR' as BillDirection },
  { label: '应付账单', value: 'AP' as BillDirection },
]

const manualRules: FormRules = {
  client_id: [
    { required: true, message: '请选择客户', trigger: 'change' },
  ],
  currency: [
    { required: true, message: '币种为必填项', trigger: 'change' },
  ],
  direction: [
    { required: true, message: '请确认账单方向', trigger: 'change' },
  ],
}

const totalAmount = computed(() => {
  return manualForm.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
})

function asNumericAmount(amount: number | string | undefined): number {
  if (amount === undefined || amount === null || amount === '') return 0
  const parsed = Number(amount)
  return Number.isFinite(parsed) ? parsed : 0
}

function formatDraftAmount(amount: number | string | undefined, currency: string): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency || 'CNY',
  }).format(asNumericAmount(amount))
}

const availableDraftOptions = computed(() => {
  return availableDrafts.value.map((draft) => {
    const readableDraftId = '费用草稿'
    const caseDisplay = draft.case_no || '未命名案件'
    const clientDisplay = draft.client_name || '未关联客户'
    const amountDisplay = formatDraftAmount(draft.amount, draft.currency)
    return {
      id: draft.id,
      displayId: readableDraftId,
      caseDisplay,
      clientDisplay,
      amountDisplay,
      displayLabel: `${readableDraftId} · ${caseDisplay} · ${clientDisplay} · ${amountDisplay}`,
    }
  })
})

function formatClientOption(client: Client): string {
  const code = client.client_code ? `${client.client_code} · ` : ''
  return `${code}${client.name || '未命名客户'}`
}

function formatCaseOption(caseItem: Case): string {
  const title = caseItem.title ? ` · ${caseItem.title}` : ''
  return `${caseItem.case_no}${title}`
}

async function fetchAvailableDrafts() {
  draftOptionsLoading.value = true
  try {
    const result = await getFeeDrafts({ page: 1, page_size: 100, status: 'LOCKED' })
    availableDrafts.value = result.items.filter((draft) => asNumericAmount(draft.amount) > 0)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    draftOptionsLoading.value = false
  }
}

async function fetchClientOptions() {
  clientOptionsLoading.value = true
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clientOptions.value = result.items
  } catch (err) {
    error.value = err as ApiError
  } finally {
    clientOptionsLoading.value = false
  }
}

async function fetchCaseOptions() {
  if (!manualForm.client_id) {
    caseOptions.value = []
    return
  }

  caseOptionsLoading.value = true
  try {
    const result = await getCases({
      page: 1,
      page_size: 100,
      client_id: manualForm.client_id,
    })
    caseOptions.value = result.items
  } catch (err) {
    error.value = err as ApiError
  } finally {
    caseOptionsLoading.value = false
  }
}

function formatAmount(amount: number): string {
  const curr = manualForm.currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(amount)
}

function addItem() {
  manualForm.items.push({ description: '', quantity: 1, unit_price: 0 })
}

function removeItem(index: number) {
  manualForm.items.splice(index, 1)
}

function getItemError(index: number, field: string): boolean {
  return fieldErrors.value.has(`items.${index}.${field}`)
}

function goBack() {
  router.push('/billing/bills')
}

async function handleCreateFromDrafts() {
  fieldErrors.value = new Map()

  if (draftsForm.draft_ids.length === 0) {
    ElMessage.warning('请至少选择一个草稿')
    return
  }

  saving.value = true
  error.value = null

  try {
    const payload: BillFromDraftsPayload = {
      draft_ids: draftsForm.draft_ids,
      currency: draftsForm.currency,
      notes: draftsForm.notes || undefined,
    }

    const bill = await createBillFromDrafts(payload)
    ElMessage.success('账单创建成功')
    router.push(`/billing/bills/${bill.id}`)
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    saving.value = false
  }
}

async function handleCreateManual() {
  fieldErrors.value = new Map()

  const valid = await manualFormRef.value?.validate().catch(() => false)
  if (!valid) return

  // Validate items
  const validItems = manualForm.items.filter(item => item.description.trim())
  if (validItems.length === 0) {
    ElMessage.warning('请至少添加一条含描述的明细')
    return
  }

  saving.value = true
  error.value = null

  try {
    const payload: BillManualPayload = {
      client_id: manualForm.client_id,
      case_id: manualForm.case_id || undefined,
      currency: manualForm.currency,
      direction: manualForm.direction,
      items: validItems,
      notes: manualForm.notes || undefined,
    }

    const bill = await createManualBill(payload)
    ElMessage.success('账单创建成功')
    router.push(`/billing/bills/${bill.id}`)
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    saving.value = false
  }
}

watch(
  () => manualForm.client_id,
  () => {
    manualForm.case_id = ''
    void fetchCaseOptions()
  }
)

onMounted(() => {
  fetchAvailableDrafts()
  fetchClientOptions()
})
</script>

<style scoped>
.form-card-title {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
}

.create-tabs {
  margin-top: 16px;
}

.bill-form {
  max-width: 800px;
}

.full-width {
  width: 100%;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 6px;
}

.field-hint a {
  color: var(--color-primary);
  text-decoration: none;
}

.field-hint a:hover {
  text-decoration: underline;
}

.draft-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 2px 0;
}

.draft-option-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.draft-option-id {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--text-main);
}

.draft-option-case {
  color: var(--text-main);
}

.draft-option-sub {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--text-sub);
  font-size: 12px;
}

.items-table {
  width: 100%;
  margin-bottom: 12px;
}

.items-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.items-total {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-label {
  font-weight: 500;
  color: var(--text-sub);
}

.total-value {
  font-size: 18px;
  font-weight: 600;
}

.mono-num {
  font-family: var(--font-mono);
}

.is-error :deep(.el-input__inner) {
  border-color: var(--el-color-danger);
}
</style>
