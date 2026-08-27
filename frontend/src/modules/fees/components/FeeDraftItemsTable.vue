<template>
  <div class="items-section">
    <!-- Error Banner -->
    <div v-if="error" class="items-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Header with Add Button -->
    <div class="items-header">
      <h3 class="panel-heading">费用明细</h3>
      <div class="items-actions">
        <el-button
          size="small"
          type="success"
          :disabled="selectedGovItems.length === 0"
          @click="openPayListDialog"
        >
          生成官费清单
        </el-button>
        <el-button v-if="canUseGenericEditing" size="small" type="primary" @click="openAddDialog">
          + 添加明细
        </el-button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="items-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="items-empty">
      <p>暂无明细，请点击“添加明细”开始。</p>
    </div>

    <!-- Items Table -->
    <template v-else>
      <el-table
        :data="items"
        stripe
        size="small"
        class="compact-table items-table"
        show-summary
        :summary-method="getSummaries"
      >
        <el-table-column label="选择" width="64" align="center">
          <template #default="{ row }">
            <el-checkbox
              :model-value="isItemSelected(row)"
              :disabled="!isGovItem(row)"
              :aria-label="selectionLabel(row)"
              @change="handleGovItemToggle(row, $event)"
              @click.stop
            />
          </template>
        </el-table-column>
        <el-table-column label="费用类型" width="100">
          <template #default="{ row }">
            <el-tag :type="isGovItem(row) ? 'success' : 'info'" size="small">
              {{ feeTypeText(row.fee_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="费用项目" min-width="160">
          <template #default="{ row }">
            {{ row.fee_name || row.description || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="数量" width="80" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ resolveAdjustmentQuantity(row, sourceFacts) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="单价" width="120" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ formatAmount(row.unit_price) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="140" align="right">
          <template #default="{ row }">
            <span class="mono-num amount-cell">{{ formatAmount(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="showActionColumn" label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-button
              v-if="canAdjustItem(row)"
              text
              size="small"
              type="primary"
              @click="openAdjustmentDialog(row)"
            >
              调整数量
            </el-button>
            <template v-else-if="canUseGenericEditing">
              <el-button text size="small" @click="openEditDialog(row)">编辑</el-button>
              <el-button text size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
            </template>
            <span v-else class="field-hint">只读</span>
          </template>
        </el-table-column>
      </el-table>
    </template>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingItem ? '编辑明细' : '添加明细'"
      width="480px"
      @close="resetDialog"
    >
      <div v-if="dialogError" class="dialog-error">
        <ApiErrorBanner :error="dialogError" @dismiss="dialogError = null" />
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="描述" prop="description" :error="fieldErrors.get('description')?.join(', ')">
          <el-input v-model="form.description" placeholder="请输入明细描述" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity" :error="fieldErrors.get('quantity')?.join(', ')">
              <el-input-number
                v-model="form.quantity"
                :min="1"
                :precision="0"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价" prop="unit_price" :error="fieldErrors.get('unit_price')?.join(', ')">
              <el-input-number
                v-model="form.unit_price"
                :min="0"
                :precision="2"
                :step="100"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">
          {{ editingItem ? '保存修改' : '添加明细' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="adjustmentDialogVisible" title="调整服务费数量" width="480px">
      <el-alert
        title="本操作会生成可追溯的替代记录，每份服务费草单只允许调整一次。"
        type="warning"
        :closable="false"
        show-icon
      />
      <el-form label-position="top" class="adjustment-form">
        <el-form-item label="费用项目">
          <el-input :model-value="adjustingItem?.fee_name || adjustingItem?.description || '—'" disabled />
        </el-form-item>
        <el-form-item label="当前数量">
          <el-input :model-value="String(adjustmentForm.expected_quantity)" disabled />
        </el-form-item>
        <el-form-item label="调整后数量">
          <el-input-number v-model="adjustmentForm.new_quantity" :min="1" :precision="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="调整原因（须包含中文）">
          <el-input v-model="adjustmentForm.reason" type="textarea" :rows="3" maxlength="256" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustmentDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="adjusting" @click="submitAdjustment">确认调整</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="payListDialogVisible"
      title="生成官费清单"
      width="480px"
    >
      <div v-if="payListError" class="dialog-error">
        <ApiErrorBanner :error="payListError" @dismiss="payListError = null" />
      </div>
      <el-form label-position="top">
        <el-form-item label="已选官费明细">
          <div class="field-hint">共 {{ selectedGovItems.length }} 条，合计 {{ formatAmount(selectedGovTotal) }}</div>
        </el-form-item>
        <el-form-item label="计划缴费日期">
          <el-date-picker
            v-model="payListForm.planned_pay_date"
            type="date"
            placeholder="请选择计划缴费日期"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="payListForm.remark" placeholder="可填写说明（可选）" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="payListDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creatingPayList" @click="handleCreatePayList">
          创建官费清单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  adjustDemoServiceDraft,
  getFeeDraftItems,
  createFeeItem,
  updateFeeItem,
  deleteFeeItem,
} from '../../../api/fees'
import { createPayListFromFeeItems, mapGovPaymentsError } from '../../../api/govPayments'
import type { DemoV6DraftSourceFacts, FeeItem, FeeItemCreatePayload } from '../../../api/fees.types'
import type { GovPaymentsApiError } from '../../../api/govPayments.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const props = defineProps<{
  draftId: string
  currency?: string
  readonly?: boolean
  sourceFacts?: DemoV6DraftSourceFacts | null
  sourceFactsResolved?: boolean
}>()

const router = useRouter()

const emit = defineEmits<{
  change: []
}>()

const items = ref<FeeItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)

// Dialog state
const dialogVisible = ref(false)
const editingItem = ref<FeeItem | null>(null)
const formRef = ref<FormInstance>()
const saving = ref(false)
const dialogError = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const selectedItems = ref<FeeItem[]>([])
const payListDialogVisible = ref(false)
const creatingPayList = ref(false)
const payListError = ref<GovPaymentsApiError | null>(null)
const adjustmentDialogVisible = ref(false)
const adjustingItem = ref<FeeItem | null>(null)
const adjusting = ref(false)

const adjustmentForm = reactive({
  expected_quantity: 1,
  new_quantity: 1,
  reason: '',
  idempotency_key: crypto.randomUUID(),
})

const form = reactive<FeeItemCreatePayload>({
  description: '',
  quantity: 1,
  unit_price: 0,
})

const payListForm = reactive({
  planned_pay_date: '',
  remark: '',
})

const rules: FormRules = {
  description: [
    { required: true, message: '描述为必填项', trigger: 'blur' },
  ],
  quantity: [
    { required: true, message: '数量为必填项', trigger: 'blur' },
  ],
  unit_price: [
    { required: true, message: '单价为必填项', trigger: 'blur' },
  ],
}

const totalAmount = computed(() => {
  return items.value.reduce((sum, item) => sum + Number(item.amount), 0)
})

const selectedGovItems = computed(() => selectedItems.value.filter(isGovItem))
const canUseGenericEditing = computed(() => (
  !props.readonly
  && props.sourceFactsResolved === true
  && !props.sourceFacts
))
const showActionColumn = computed(() => (
  canUseGenericEditing.value
  || Boolean(props.sourceFacts?.fee_domain === 'SERVICE' && !props.readonly)
))
const selectedGovTotal = computed(() => {
  return selectedGovItems.value.reduce((sum, item) => sum + Number(item.amount || 0), 0)
})

async function fetchItems() {
  loading.value = true
  error.value = null

  try {
    items.value = await getFeeDraftItems(props.draftId)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatAmount(value: number): string {
  const curr = props.currency || 'CNY'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(value)
}

function feeTypeText(feeType?: string | null): string {
  switch ((feeType || '').toUpperCase()) {
    case 'GOV':
      return '官费'
    case 'SERVICE':
      return '服务费'
    case 'MISC':
      return '杂费'
    default:
      return feeType || '未知'
  }
}

function isGovItem(item: FeeItem): boolean {
  return (item.fee_type || '').toUpperCase() === 'GOV'
}

function sourceFactFor(item: FeeItem) {
  return props.sourceFacts?.lines.find(line => line.current_item_id === item.id)
}

function resolveAdjustmentQuantity(
  item: Pick<FeeItem, 'id' | 'quantity'>,
  sourceFacts: DemoV6DraftSourceFacts | null | undefined,
): number {
  if (sourceFacts?.fee_domain !== 'SERVICE') return item.quantity
  const quantity = sourceFacts.lines.find(line => line.current_item_id === item.id)?.quantity
  return Number.isInteger(quantity) && Number(quantity) > 0 ? Number(quantity) : item.quantity
}

function canAdjustItem(item: FeeItem): boolean {
  const fact = sourceFactFor(item)
  const quantity = resolveAdjustmentQuantity(item, props.sourceFacts)
  return Boolean(
    !props.readonly
    && props.sourceFacts?.fee_domain === 'SERVICE'
    && fact?.adjustable
    && !fact.adjustment_activity_id
    && Number.isInteger(quantity)
    && quantity > 0,
  )
}

function openAdjustmentDialog(item: FeeItem) {
  if (!canAdjustItem(item)) return
  const currentQuantity = resolveAdjustmentQuantity(item, props.sourceFacts)
  adjustingItem.value = item
  adjustmentForm.expected_quantity = currentQuantity
  adjustmentForm.new_quantity = currentQuantity
  adjustmentForm.reason = ''
  adjustmentForm.idempotency_key = crypto.randomUUID()
  adjustmentDialogVisible.value = true
}

async function submitAdjustment() {
  const item = adjustingItem.value
  const reason = adjustmentForm.reason.trim()
  if (!item || !canAdjustItem(item)) return
  if (!reason || !/[\u4e00-\u9fff]/.test(reason)) {
    ElMessage.warning('请输入包含中文的调整原因。')
    return
  }
  if (adjustmentForm.new_quantity === adjustmentForm.expected_quantity) {
    ElMessage.warning('调整后数量必须与当前数量不同。')
    return
  }
  adjusting.value = true
  try {
    await adjustDemoServiceDraft(props.draftId, {
      item_id: item.id,
      expected_quantity: adjustmentForm.expected_quantity,
      new_quantity: adjustmentForm.new_quantity,
      reason,
      idempotency_key: adjustmentForm.idempotency_key,
    })
    adjustmentDialogVisible.value = false
    await fetchItems()
    emit('change')
    ElMessage.success('服务费数量调整成功，来源与调整记录已更新。')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    adjusting.value = false
  }
}

function isItemSelected(item: FeeItem): boolean {
  return selectedItems.value.some(selected => selected.id === item.id)
}

function selectionLabel(item: FeeItem): string {
  const rowName = item.description || `#${item.id}`
  if (!isGovItem(item)) {
    return `该费用明细不可选择：${rowName}`
  }
  return `选择官费明细：${rowName}`
}

function handleGovItemToggle(item: FeeItem, checked: boolean | string | number) {
  if (!isGovItem(item)) return

  if (checked === true) {
    if (!isItemSelected(item)) {
      selectedItems.value = [...selectedItems.value, item]
    }
    return
  }

  selectedItems.value = selectedItems.value.filter(selected => selected.id !== item.id)
}

function openPayListDialog() {
  if (selectedGovItems.value.length === 0) {
    ElMessage.warning('请先选择官费明细。')
    return
  }
  payListError.value = null
  payListDialogVisible.value = true
}

async function handleCreatePayList() {
  if (selectedGovItems.value.length === 0) {
    ElMessage.warning('请先选择官费明细。')
    return
  }
  creatingPayList.value = true
  payListError.value = null
  try {
    const response = await createPayListFromFeeItems({
      fee_item_ids: selectedGovItems.value.map(item => item.id),
      planned_pay_date: payListForm.planned_pay_date || undefined,
      remark: payListForm.remark || undefined,
    })
    if (!response.pay_list) {
      ElMessage.warning('未创建官费清单，请检查失败明细。')
      return
    }
    ElMessage.success('官费清单创建成功')
    payListDialogVisible.value = false
    router.push(`/fee-management/pay-lists/${response.pay_list.id}`)
  } catch (err) {
    payListError.value = mapGovPaymentsError(err)
  } finally {
    creatingPayList.value = false
  }
}

function getSummaries({ columns }: { columns: { property?: string; label?: string }[] }): string[] {
  return columns.map((column, index) => {
    if (index === 0) return '合计'
    if (column.property === 'amount' || column.label === '金额') {
      return formatAmount(totalAmount.value)
    }
    return ''
  })
}

function openAddDialog() {
  editingItem.value = null
  form.description = ''
  form.quantity = 1
  form.unit_price = 0
  dialogError.value = null
  fieldErrors.value = new Map()
  dialogVisible.value = true
}

function openEditDialog(item: FeeItem) {
  editingItem.value = item
  form.description = item.description
  form.quantity = item.quantity
  form.unit_price = item.unit_price
  dialogError.value = null
  fieldErrors.value = new Map()
  dialogVisible.value = true
}

function resetDialog() {
  editingItem.value = null
  fieldErrors.value = new Map()
  dialogError.value = null
}

async function handleSubmit() {
  fieldErrors.value = new Map()

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  dialogError.value = null

  try {
    if (editingItem.value) {
      await updateFeeItem(props.draftId, editingItem.value.id, {
        description: form.description,
        quantity: form.quantity,
        unit_price: form.unit_price,
      })
      ElMessage.success('明细更新成功')
    } else {
      await createFeeItem(props.draftId, {
        description: form.description,
        quantity: form.quantity,
        unit_price: form.unit_price,
      })
      ElMessage.success('明细添加成功')
    }

    dialogVisible.value = false
    await fetchItems()
    emit('change')
  } catch (err) {
    const apiError = err as ApiError
    dialogError.value = apiError

    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    saving.value = false
  }
}

async function confirmDelete(item: FeeItem) {
  try {
    await ElMessageBox.confirm(
      `确认删除明细“${item.description}”吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await deleteFeeItem(item.id)
    ElMessage.success('明细删除成功')
    await fetchItems()
    emit('change')
  } catch (err) {
    if (err !== 'cancel') {
      error.value = err as ApiError
    }
  }
}

onMounted(() => {
  fetchItems()
})

defineExpose({
  refresh: fetchItems
})
</script>

<style scoped>
.items-section {
  padding: 0;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.items-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.items-header .panel-heading {
  margin: 0;
}

.items-loading {
  padding: 16px 0;
}

.items-empty {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-sub);
}

.items-error {
  margin-bottom: 16px;
}

.items-table {
  width: 100%;
}

.mono-num {
  font-family: var(--font-mono);
}

.amount-cell {
  font-weight: 500;
}

.dialog-error {
  margin-bottom: 16px;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
}

.adjustment-form {
  margin-top: 16px;
}
</style>
