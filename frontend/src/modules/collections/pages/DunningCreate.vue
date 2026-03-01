<template>
  <main class="page-container" role="main">
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回
        </el-button>
      </div>
    </div>

    <div v-if="error" class="page-error" role="alert" aria-live="assertive">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <div class="form-card">
      <h2 class="form-card-title">创建催款批次</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="dunning-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">批次条件</h3>

          <el-form-item
            label="截止日期"
            prop="to_date"
            :error="fieldErrors.get('to_date')?.join('，')"
          >
            <el-date-picker
              v-model="form.to_date"
              type="date"
              placeholder="请选择截止日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              class="full-width"
            />
          </el-form-item>

          <el-form-item label="冲突策略">
            <el-switch
              v-model="form.strict_conflict"
              active-text="严格冲突校验"
              inactive-text="允许复用既有批次"
            />
            <div class="field-hint">开启后，若存在冲突将由后端返回冲突错误。</div>
          </el-form-item>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">客户过滤</h3>

          <el-form-item label="客户范围">
            <el-radio-group v-model="form.customer_scope">
              <el-radio value="all">全部客户</el-radio>
              <el-radio value="selected">指定客户</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item
            v-if="form.customer_scope === 'selected'"
            label="选择客户"
            prop="client_ids"
            :error="fieldErrors.get('client_ids')?.join('，')"
          >
            <el-select
              v-model="form.client_ids"
              multiple
              filterable
              allow-create
              default-first-option
              clearable
              collapse-tags
              collapse-tags-tooltip
              :loading="clientsLoading"
              placeholder="请输入或选择客户编号"
              class="full-width"
            >
              <el-option
                v-for="client in clientOptions"
                :key="client.id"
                :label="formatClientLabel(client)"
                :value="client.id"
              />
            </el-select>
            <div class="field-hint">可直接输入客户编号；不指定时表示全部客户。</div>
            <div v-if="clientsError" class="field-hint warning-text">{{ clientsError }}</div>
          </el-form-item>
        </div>

        <div class="form-actions">
          <el-button @click="goBack">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSubmit">
            生成催款批次
          </el-button>
        </div>
      </el-form>
    </div>
  </main>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { generateDunning, mapCollectionsError } from '../../../api/collections'
import { getClients } from '../../../api/clients'
import type { CollectionsApiError, DunningGenerateBatch, DunningGeneratePayload } from '../../../api/collections.types'
import type { Client } from '../../../api/clients.types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

interface DunningCreateForm {
  to_date: string
  strict_conflict: boolean
  customer_scope: 'all' | 'selected'
  client_ids: string[]
}

const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<CollectionsApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const clientsLoading = ref(false)
const clientsError = ref('')
const clientOptions = ref<Client[]>([])

const form = reactive<DunningCreateForm>({
  to_date: new Date().toISOString().split('T')[0],
  strict_conflict: false,
  customer_scope: 'all',
  client_ids: [],
})

const rules: FormRules<DunningCreateForm> = {
  to_date: [{ required: true, message: '截止日期为必填项', trigger: 'change' }],
  client_ids: [
    {
      validator: (_rule, value: unknown, callback) => {
        if (form.customer_scope === 'selected' && (!Array.isArray(value) || value.length === 0)) {
          callback(new Error('请至少选择一个客户'))
          return
        }
        callback()
      },
      trigger: 'change',
    },
  ],
}

function formatClientLabel(client: Client): string {
  if (client.name) {
    return `${client.name}（${client.id}）`
  }
  return `客户 ${client.id}`
}

function normalizeClientIds(input: string[]): string[] {
  const normalized = input.map((id) => id.trim()).filter(Boolean)
  return Array.from(new Set(normalized))
}

async function loadClients() {
  clientsLoading.value = true
  clientsError.value = ''

  try {
    const result = await getClients({ page: 1, page_size: 200 })
    clientOptions.value = result.items.filter((client) => client.is_active)
  } catch {
    clientOptions.value = []
    clientsError.value = '客户列表加载失败，可手动输入客户编号。'
  } finally {
    clientsLoading.value = false
  }
}

function goBack() {
  router.push('/collections/dunning')
}

async function navigateAfterSuccess(batches: DunningGenerateBatch[]) {
  if (batches.length === 1) {
    await router.push(`/collections/dunning/${batches[0].id}`)
    return
  }
  await router.push('/collections/dunning')
}

async function handleSubmit() {
  fieldErrors.value = new Map()
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    const payload: DunningGeneratePayload = {
      to_date: form.to_date,
      strict_conflict: form.strict_conflict,
    }

    if (form.customer_scope === 'selected') {
      const ids = normalizeClientIds(form.client_ids)
      if (ids.length > 0) {
        payload.client_ids = ids
      }
    }

    const result = await generateDunning(payload)

    if (result.summary.batches > 0) {
      ElMessage.success(`催款批次生成成功，共 ${result.summary.batches} 个`)
    } else {
      ElMessage.success('处理完成，未生成新批次')
    }

    await navigateAfterSuccess(result.batches)
  } catch (err) {
    const mappedError = mapCollectionsError(err)
    error.value = mappedError
    if (mappedError.field_errors && mappedError.field_errors.size > 0) {
      fieldErrors.value = mappedError.field_errors
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadClients()
})
</script>

<style scoped>
.form-card-title {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
}

.dunning-form {
  max-width: 640px;
}

.full-width {
  width: 100%;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 6px;
}

.warning-text {
  color: var(--color-warning);
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
