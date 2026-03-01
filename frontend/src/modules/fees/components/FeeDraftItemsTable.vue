<template>
  <div class="items-section">
    <!-- Error Banner -->
    <div v-if="error" class="items-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Header with Add Button -->
    <div class="items-header">
      <h3 class="panel-heading">费用明细</h3>
      <el-button v-if="!readonly" size="small" type="primary" @click="openAddDialog">
        + 添加明细
      </el-button>
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
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="数量" width="80" align="right">
          <template #default="{ row }">
            <span class="mono-num">{{ row.quantity }}</span>
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
        <el-table-column v-if="!readonly" label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button text size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button text size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getFeeDraftItems, createFeeItem, updateFeeItem, deleteFeeItem } from '../../../api/fees'
import type { FeeItem, FeeItemCreatePayload } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const props = defineProps<{
  draftId: string
  currency?: string
  readonly?: boolean
}>()

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

const form = reactive<FeeItemCreatePayload>({
  description: '',
  quantity: 1,
  unit_price: 0,
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
</style>
