<template>
  <div class="bad-debt-panel">
    <div class="panel-header">
      <div>
        <h3 class="panel-heading">坏账信息</h3>
        <p class="panel-description">查看坏账状态、主凭证和回收记录。</p>
      </div>
      <div class="panel-actions">
        <el-button
          v-if="canMark && bill.status !== 'BAD_DEBT'"
          size="small"
          type="danger"
          :loading="marking"
          @click="openMarkDialog('MARK')"
        >
          标记坏账
        </el-button>
        <el-button
          v-if="canMark && bill.status !== 'BAD_DEBT'"
          size="small"
          type="warning"
          :loading="marking"
          @click="openMarkDialog('TRANSFER')"
        >
          剩余转坏账
        </el-button>
        <el-button
          v-if="canRecover && hasBadDebtVoucher && remainingAmount > 0"
          size="small"
          type="success"
          :loading="recovering"
          @click="openRecoverDialog"
        >
          回收坏账
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="!canMark && !canRecover"
      title="当前账号没有坏账操作权限。"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    />

    <div class="summary-grid">
      <div class="summary-card">
        <span class="summary-label">坏账状态</span>
        <el-tag :type="badDebtStatusTagType" size="small">{{ badDebtStatusText }}</el-tag>
      </div>
      <div class="summary-card">
        <span class="summary-label">坏账子状态</span>
        <el-tag v-if="badDebtSubstatusText !== '—'" type="info" size="small">
          {{ badDebtSubstatusText }}
        </el-tag>
        <span v-else class="summary-value">—</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">累计回收</span>
        <span class="summary-value mono-num">{{ formatAmount(totalRecovered) }}</span>
      </div>
      <div class="summary-card">
        <span class="summary-label">剩余坏账金额</span>
        <span class="summary-value mono-num" :class="{ 'summary-value-danger': remainingAmount > 0 }">
          {{ formatAmount(remainingAmount) }}
        </span>
      </div>
    </div>

    <div class="content-grid">
      <section class="content-card">
        <div class="content-title">坏账主凭证</div>
        <template v-if="badDebtVoucher">
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">凭证编号</span>
              <span class="info-value mono-num">{{ badDebtVoucher.id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">凭证状态</span>
              <el-tag :type="badDebtVoucherTagType" size="small">
                {{ badDebtVoucherStatusText }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">坏账金额</span>
              <span class="info-value mono-num">{{ formatAmount(badDebtVoucher.bad_debt_amount) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">已回收金额</span>
              <span class="info-value mono-num">{{ formatAmount(badDebtVoucher.recovered_amount) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">坏账日期</span>
              <span class="info-value">{{ formatDate(badDebtVoucher.bad_debt_date) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">备注</span>
              <span class="info-value">{{ badDebtVoucher.remark || '—' }}</span>
            </div>
          </div>
        </template>
        <div v-else class="empty-state">暂无坏账主凭证。</div>
      </section>

      <section class="content-card">
        <div class="content-title">回收记录</div>
        <template v-if="recoveries.length">
          <el-table :data="recoveries" stripe size="small" class="compact-table">
            <el-table-column label="回收日期" width="130">
              <template #default="{ row }">
                {{ formatDate(row.recovery_date) }}
              </template>
            </el-table-column>
            <el-table-column label="回收金额" width="140" align="right">
              <template #default="{ row }">
                <span class="mono-num">{{ formatAmount(row.recovery_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="备注" min-width="180">
              <template #default="{ row }">
                {{ row.remark || '—' }}
              </template>
            </el-table-column>
          </el-table>
        </template>
        <div v-else class="empty-state">暂无回收记录。</div>
      </section>
    </div>

    <el-dialog
      v-model="markDialogVisible"
      :title="markDialogTitle"
      width="520px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form :model="markForm" label-position="top">
        <el-form-item label="坏账日期">
          <el-date-picker
            v-model="markForm.bad_debt_date"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="请选择坏账日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model.trim="markForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="markDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="marking" @click="submitMarkBadDebt">
          确认
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="recoverDialogVisible"
      title="回收坏账"
      width="520px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form ref="recoverFormRef" :model="recoverForm" :rules="recoverRules" label-position="top">
        <el-form-item label="回收金额" prop="recovery_amount">
          <el-input-number
            v-model="recoverForm.recovery_amount"
            :min="0"
            :precision="2"
            controls-position="right"
            placeholder="请输入回收金额"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="回收日期">
          <el-date-picker
            v-model="recoverForm.recovery_date"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="请选择回收日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model.trim="recoverForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recoverDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="recovering" @click="submitRecoverBadDebt">
          确认
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { markBillBadDebt, recoverBillBadDebt } from '../../../api/billing'
import type {
  BillBadDebtActionPayload,
  BillBadDebtRecoveryPayload,
  BillDetail,
} from '../../../api/billing.types'

type MarkMode = BillBadDebtActionPayload['mode']

const props = defineProps<{
  bill: BillDetail
  canMark: boolean
  canRecover: boolean
}>()

const emit = defineEmits<{
  changed: []
}>()

const markDialogVisible = ref(false)
const recoverDialogVisible = ref(false)
const marking = ref(false)
const recovering = ref(false)
const markMode = ref<MarkMode>('MARK')
const recoverFormRef = ref<FormInstance>()

const markForm = reactive<BillBadDebtActionPayload>({
  mode: 'MARK',
  bad_debt_date: '',
  remark: '',
})

const recoverForm = reactive<BillBadDebtRecoveryPayload & { recovery_date: string | '' }>({
  recovery_amount: 0,
  recovery_date: '',
  remark: '',
})

const recoverRules: FormRules = {
  recovery_amount: [
    { required: true, message: '请输入回收金额', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (typeof value !== 'number' || value <= 0) {
          callback(new Error('回收金额必须大于 0'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

const badDebtVoucher = computed(() => props.bill.bad_debt_voucher || null)
const recoveries = computed(() => props.bill.bad_debt_recoveries || [])
const totalRecovered = computed(() => props.bill.bad_debt_total_recovered || 0)
const remainingAmount = computed(() => props.bill.bad_debt_remaining_amount || 0)
const badDebtStatus = computed(() => (props.bill.bad_debt_status || 'NONE').toUpperCase())
const badDebtSubstatus = computed(() => (props.bill.bad_debt_substatus || '').toUpperCase())
const hasBadDebtVoucher = computed(() => !!badDebtVoucher.value)

const badDebtStatusText = computed(() => {
  switch (badDebtStatus.value) {
    case 'OPEN':
      return '坏账处理中'
    case 'CLOSED':
      return '已结清'
    case 'NONE':
    default:
      return '未坏账'
  }
})

const badDebtSubstatusText = computed(() => {
  switch (badDebtSubstatus.value) {
    case 'MANUAL_MARK':
      return '手工标记'
    case 'PARTIAL_TRANSFER':
      return '剩余转坏账'
    case 'PARTIAL_RECOVERY':
      return '部分回收'
    case 'FULLY_RECOVERED':
      return '全部回收'
    default:
      return '—'
  }
})

const badDebtStatusTagType = computed<'info' | 'warning' | 'success'>(() => {
  switch (badDebtStatus.value) {
    case 'OPEN':
      return 'warning'
    case 'CLOSED':
      return 'success'
    default:
      return 'info'
  }
})

const badDebtVoucherStatusText = computed(() => {
  const status = (badDebtVoucher.value?.status || 'OPEN').toUpperCase()
  if (status === 'CLOSED') return '已结清'
  if (status === 'OPEN') return '处理中'
  return status
})

const badDebtVoucherTagType = computed<'info' | 'warning' | 'success'>(() => {
  const status = (badDebtVoucher.value?.status || 'OPEN').toUpperCase()
  if (status === 'CLOSED') return 'success'
  if (status === 'OPEN') return 'warning'
  return 'info'
})

const markDialogTitle = computed(() => (markMode.value === 'TRANSFER' ? '剩余转坏账' : '标记坏账'))

function todayValue(): string {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatAmount(value: number): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: props.bill.currency || 'CNY',
  }).format(value || 0)
}

function formatDate(value?: string | null): string {
  if (!value) return '—'
  try {
    return new Date(value).toLocaleDateString('zh-CN')
  } catch {
    return value
  }
}

function openMarkDialog(mode: MarkMode) {
  markMode.value = mode
  markForm.mode = mode
  markForm.bad_debt_date = todayValue()
  markForm.remark = ''
  markDialogVisible.value = true
}

function openRecoverDialog() {
  recoverForm.recovery_amount = remainingAmount.value
  recoverForm.recovery_date = todayValue()
  recoverForm.remark = ''
  recoverDialogVisible.value = true
}

async function submitMarkBadDebt() {
  if (marking.value) return
  marking.value = true
  try {
    await markBillBadDebt(props.bill.id, {
      mode: markForm.mode,
      bad_debt_date: markForm.bad_debt_date || undefined,
      remark: markForm.remark || undefined,
    })
    ElMessage.success(markForm.mode === 'TRANSFER' ? '剩余部分已转坏账' : '账单已标记为坏账')
    markDialogVisible.value = false
    emit('changed')
  } catch (err) {
    ElMessage.error(resolveActionErrorMessage(err))
  } finally {
    marking.value = false
  }
}

async function submitRecoverBadDebt() {
  if (recovering.value) return
  const form = recoverFormRef.value
  if (form) {
    const valid = await form.validate().catch(() => false)
    if (!valid) return
  }

  recovering.value = true
  try {
    await recoverBillBadDebt(props.bill.id, {
      recovery_amount: Number(recoverForm.recovery_amount),
      recovery_date: recoverForm.recovery_date || undefined,
      remark: recoverForm.remark || undefined,
    })
    ElMessage.success('坏账已回收')
    recoverDialogVisible.value = false
    emit('changed')
  } catch (err) {
    ElMessage.error(resolveActionErrorMessage(err))
  } finally {
    recovering.value = false
  }
}

function resolveActionErrorMessage(error: unknown): string {
  const candidate = error as { status?: number; code?: string }
  if (candidate?.status === 401) return '登录已失效，请重新登录'
  if (candidate?.status === 403) return '无权限执行该操作'
  if (candidate?.status === 404) return '未找到目标账单'
  if (candidate?.status === 400) {
    switch (candidate.code) {
      case 'BAD_DEBT_NOT_ALLOWED':
        return '当前账单不满足坏账操作条件'
      case 'BAD_DEBT_VOUCHER_NOT_FOUND':
        return '未找到坏账凭证，请先标记坏账'
      case 'BAD_DEBT_RECOVERY_NOT_ALLOWED':
        return '当前账单不支持回收坏账'
      case 'BAD_DEBT_RECOVERY_EXCEEDS_REMAINING':
        return '回收金额不能超过剩余坏账金额'
      default:
        return '坏账操作失败，请稍后重试'
    }
  }
  if (candidate?.status === 409) return '账单状态冲突，请刷新后重试'
  if (candidate?.status === 422) return '参数校验失败，请检查后重试'
  return '坏账操作失败，请稍后重试'
}
</script>

<style scoped>
.bad-debt-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.panel-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.panel-description {
  margin: 6px 0 0;
  color: var(--text-sub);
  font-size: 13px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-card,
.content-card {
  border: 1px solid var(--border-light);
  border-radius: 12px;
  background: var(--bg-card);
}

.summary-card {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-label {
  font-size: 13px;
  color: var(--text-sub);
}

.summary-value {
  font-size: 16px;
  font-weight: 600;
}

.summary-value-danger {
  color: var(--color-danger);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.content-card {
  padding: 16px;
}

.content-title {
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 13px;
  color: var(--text-sub);
}

.info-value {
  color: var(--text-main);
}

.empty-state {
  padding: 12px 0 4px;
  color: var(--text-sub);
}

.mono-num {
  font-family: var(--font-mono);
}

@media (max-width: 960px) {
  .summary-grid,
  .info-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .panel-header {
    flex-direction: column;
  }

  .panel-actions {
    justify-content: flex-start;
  }

  .summary-grid,
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
