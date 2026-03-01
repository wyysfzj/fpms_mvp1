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
                输入已锁定费用草稿的编号，用于生成本账单。
              </p>

              <el-form-item
                label="草稿编号"
                prop="draft_ids"
                :error="fieldErrors.get('draft_ids')?.join(', ')"
              >
                <el-select
                  v-model="draftsForm.draft_ids"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  placeholder="输入草稿编号（可粘贴或输入）"
                  class="full-width"
                >
                </el-select>
                <div class="field-hint">
                  <router-link to="/fees/drafts">查看费用草稿</router-link> 以获取草稿编号
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
                    <el-input
                      v-model.trim="manualForm.client_id"
                      placeholder="请输入客户编号"
                    />
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
                    <el-input
                      v-model.trim="manualForm.case_id"
                      placeholder="可选案件编号"
                    />
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
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { createBillFromDrafts, createManualBill } from '../../../api/billing'
import type { BillFromDraftsPayload, BillManualPayload, BillManualItem } from '../../../api/billing.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const router = useRouter()

const activeTab = ref('drafts')
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

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
  items: [{ description: '', quantity: 1, unit_price: 0 }] as BillManualItem[],
  notes: '',
})

const manualRules: FormRules = {
  client_id: [
    { required: true, message: '客户编号为必填项', trigger: 'blur' },
  ],
  currency: [
    { required: true, message: '币种为必填项', trigger: 'change' },
  ],
}

const totalAmount = computed(() => {
  return manualForm.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
})

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
