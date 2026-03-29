<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">任务模板管理</h1>
        <span class="page-count">{{ templates.length }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="openCreate">新增模板</el-button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="templates"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="code" label="编码" width="150" />
      <el-table-column prop="name" label="名称" min-width="180" />
      <el-table-column label="加天数" width="100">
        <template #default="{ row }">{{ row.add_days ?? '—' }}</template>
      </el-table-column>
      <el-table-column label="加月数" width="100">
        <template #default="{ row }">{{ row.add_months ?? '—' }}</template>
      </el-table-column>
      <el-table-column label="内部偏移天数" width="120">
        <template #default="{ row }">{{ row.inner_offset_days ?? '—' }}</template>
      </el-table-column>
      <el-table-column label="期限基准" width="120">
        <template #default="{ row }">{{ getDeadlineBaseLabel(row.deadline_base) }}</template>
      </el-table-column>
      <el-table-column label="提醒基准" width="120">
        <template #default="{ row }">{{ getRemindBaseLabel(row.remind_base) }}</template>
      </el-table-column>
      <el-table-column label="提醒偏移" width="180">
        <template #default="{ row }">{{ formatRemindOffsets(row) }}</template>
      </el-table-column>
      <el-table-column label="每日提醒" width="100">
        <template #default="{ row }">
          <el-tag :type="row.daily_remind ? 'warning' : 'info'">
            {{ row.daily_remind ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="默认监督人ID" width="140">
        <template #default="{ row }">{{ row.default_supervisor_id || '—' }}</template>
      </el-table-column>
      <el-table-column label="默认角色" width="120">
        <template #default="{ row }">{{ row.default_worker_role || '—' }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'">
            {{ row.enabled ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button
            size="small"
            :type="row.enabled ? 'warning' : 'success'"
            @click="handleToggleEnabled(row)"
          >
            {{ row.enabled ? '停用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
      <template #empty>
        <div class="table-empty">暂无任务模板，点击"新增模板"创建。</div>
      </template>
    </el-table>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEdit ? '编辑任务模板' : '新增任务模板'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-position="top"
      >
        <el-form-item label="编码" prop="code">
          <el-input v-model.trim="form.code" :disabled="isEdit" maxlength="64" placeholder="模板编码" show-word-limit />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model.trim="form.name" maxlength="256" placeholder="模板名称" show-word-limit />
        </el-form-item>
        <el-form-item label="加天数" prop="add_days">
          <el-input-number v-model="form.add_days" :min="0" :precision="0" placeholder="天数" />
        </el-form-item>
        <el-form-item label="加月数" prop="add_months">
          <el-input-number v-model="form.add_months" :min="0" :precision="0" placeholder="月数" />
        </el-form-item>
        <el-form-item label="内部偏移天数" prop="inner_offset_days">
          <el-input-number v-model="form.inner_offset_days" :min="0" :precision="0" placeholder="天数" />
        </el-form-item>
        <el-form-item label="期限基准" prop="deadline_base">
          <el-select v-model="form.deadline_base" clearable style="width: 100%" placeholder="请选择期限基准">
            <el-option v-for="option in deadlineBaseOptions" :key="option.value || 'none'" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="提醒基准" prop="remind_base">
          <el-select v-model="form.remind_base" clearable style="width: 100%" placeholder="请选择提醒基准">
            <el-option v-for="option in remindBaseOptions" :key="option.value || 'none'" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="提醒1偏移天数" prop="remind_1_offset_days">
          <el-input-number v-model="form.remind_1_offset_days" :min="0" :precision="0" placeholder="填写非负整数天数" />
        </el-form-item>
        <el-form-item label="提醒2偏移天数" prop="remind_2_offset_days">
          <el-input-number v-model="form.remind_2_offset_days" :min="0" :precision="0" placeholder="填写非负整数天数" />
        </el-form-item>
        <el-form-item label="提醒3偏移天数" prop="remind_3_offset_days">
          <el-input-number v-model="form.remind_3_offset_days" :min="0" :precision="0" placeholder="填写非负整数天数" />
        </el-form-item>
        <el-form-item label="每日提醒" prop="daily_remind">
          <el-switch v-model="form.daily_remind" />
        </el-form-item>
        <el-form-item label="默认监督人ID" prop="default_supervisor_id">
          <el-input
            v-model.trim="form.default_supervisor_id"
            placeholder="可留空，直接填写用户ID"
          />
        </el-form-item>
        <el-form-item label="默认角色" prop="default_worker_role">
          <el-input v-model.trim="form.default_worker_role" maxlength="32" placeholder="例如：审查员" show-word-limit />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="模板描述" />
        </el-form-item>
        <el-form-item v-if="isEdit" label="启用" prop="enabled">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getTaskTemplates, createTaskTemplate, updateTaskTemplate } from '../../../api/tasks'
import type { TaskDeadlineBase, TaskRemindBase, TaskTemplate } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const deadlineBaseOptions: Array<{ label: string; value: TaskDeadlineBase | '' }> = [
  { label: '未设置', value: '' },
  { label: '递交日', value: 'FILING_DATE' },
  { label: '接收日', value: 'RECEIVE_DATE' },
  { label: '送达日', value: 'DISPATCH_DATE' },
  { label: '公布日', value: 'PUB_DATE' },
  { label: '授权日', value: 'GRANT_DATE' },
  { label: '案件事件', value: 'CASE_EVENT' },
  { label: '自定义', value: 'CUSTOM' },
]

const remindBaseOptions: Array<{ label: string; value: TaskRemindBase | '' }> = [
  { label: '未设置', value: '' },
  { label: '内部期限', value: 'INNER' },
  { label: '到期日', value: 'DEADLINE' },
]

const templates = ref<TaskTemplate[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)

const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  code: '',
  name: '',
  add_days: undefined as number | undefined,
  add_months: undefined as number | undefined,
  inner_offset_days: undefined as number | undefined,
  deadline_base: '' as TaskDeadlineBase | '',
  remind_base: '' as TaskRemindBase | '',
  remind_1_offset_days: undefined as number | undefined,
  remind_2_offset_days: undefined as number | undefined,
  remind_3_offset_days: undefined as number | undefined,
  daily_remind: false,
  default_supervisor_id: '',
  default_worker_role: '',
  description: '',
  enabled: true,
})

const formRules: FormRules = {
  code: [{ required: true, message: '编码为必填项', trigger: 'blur' }],
  name: [{ required: true, message: '名称为必填项', trigger: 'blur' }],
  default_supervisor_id: [
    {
      validator: (_rule, value: string, callback) => {
        if (!value) {
          callback()
          return
        }
        const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
        if (!uuidPattern.test(value)) {
          callback(new Error('默认监督人ID必须是有效的UUID'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  default_worker_role: [{ max: 32, message: '默认角色不能超过32个字符', trigger: 'blur' }],
}

async function fetchTemplates() {
  loading.value = true
  error.value = null
  try {
    templates.value = await getTaskTemplates()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.code = ''
  form.name = ''
  form.add_days = undefined
  form.add_months = undefined
  form.inner_offset_days = undefined
  form.deadline_base = ''
  form.remind_base = ''
  form.remind_1_offset_days = undefined
  form.remind_2_offset_days = undefined
  form.remind_3_offset_days = undefined
  form.daily_remind = false
  form.default_supervisor_id = ''
  form.default_worker_role = ''
  form.description = ''
  form.enabled = true
}

function openCreate() {
  resetForm()
  isEdit.value = false
  editingId.value = ''
  showDialog.value = true
}

function openEdit(row: TaskTemplate) {
  form.code = row.code
  form.name = row.name
  form.add_days = row.add_days ?? undefined
  form.add_months = row.add_months ?? undefined
  form.inner_offset_days = row.inner_offset_days ?? undefined
  form.deadline_base = row.deadline_base ?? ''
  form.remind_base = row.remind_base ?? ''
  form.remind_1_offset_days = row.remind_1_offset_days ?? undefined
  form.remind_2_offset_days = row.remind_2_offset_days ?? undefined
  form.remind_3_offset_days = row.remind_3_offset_days ?? undefined
  form.daily_remind = row.daily_remind
  form.default_supervisor_id = row.default_supervisor_id ?? ''
  form.default_worker_role = row.default_worker_role ?? ''
  form.description = row.description ?? ''
  form.enabled = row.enabled
  isEdit.value = true
  editingId.value = row.id
  showDialog.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  const addDaysValue = form.add_days ?? 0
  const addMonthsValue = form.add_months ?? 0
  if (addDaysValue === 0 && addMonthsValue === 0) {
    ElMessage.error('加天数和加月数不能同时为空或为0')
    return
  }

  if (form.remind_base === 'INNER' && form.inner_offset_days == null) {
    ElMessage.error('提醒基准为内部期限时，必须填写内部偏移天数')
    return
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await updateTaskTemplate(editingId.value, {
        name: form.name,
        deadline_base: form.deadline_base || null,
        add_days: form.add_days ?? null,
        add_months: form.add_months ?? null,
        inner_offset_days: form.inner_offset_days ?? null,
        remind_base: form.remind_base || null,
        remind_1_offset_days: form.remind_1_offset_days ?? null,
        remind_2_offset_days: form.remind_2_offset_days ?? null,
        remind_3_offset_days: form.remind_3_offset_days ?? null,
        daily_remind: form.daily_remind,
        default_supervisor_id: form.default_supervisor_id || null,
        default_worker_role: form.default_worker_role || null,
        description: form.description || null,
        enabled: form.enabled,
      })
      ElMessage.success('模板更新成功')
    } else {
      await createTaskTemplate({
        code: form.code,
        name: form.name,
        deadline_base: form.deadline_base || null,
        add_days: form.add_days ?? null,
        add_months: form.add_months ?? null,
        inner_offset_days: form.inner_offset_days ?? null,
        remind_base: form.remind_base || null,
        remind_1_offset_days: form.remind_1_offset_days ?? null,
        remind_2_offset_days: form.remind_2_offset_days ?? null,
        remind_3_offset_days: form.remind_3_offset_days ?? null,
        daily_remind: form.daily_remind,
        default_supervisor_id: form.default_supervisor_id || null,
        default_worker_role: form.default_worker_role || null,
        description: form.description || null,
      })
      ElMessage.success('模板创建成功')
    }
    showDialog.value = false
    resetForm()
    fetchTemplates()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(apiError.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleToggleEnabled(row: TaskTemplate) {
  try {
    await updateTaskTemplate(row.id, { enabled: !row.enabled })
    ElMessage.success(row.enabled ? '已停用' : '已启用')
    fetchTemplates()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(apiError.message || '操作失败')
  }
}

onMounted(() => {
  fetchTemplates()
})

function getDeadlineBaseLabel(value?: TaskDeadlineBase | null): string {
  switch (value) {
    case 'FILING_DATE':
      return '递交日'
    case 'RECEIVE_DATE':
      return '接收日'
    case 'DISPATCH_DATE':
      return '送达日'
    case 'PUB_DATE':
      return '公布日'
    case 'GRANT_DATE':
      return '授权日'
    case 'CASE_EVENT':
      return '案件事件'
    case 'CUSTOM':
      return '自定义'
    default:
      return '—'
  }
}

function getRemindBaseLabel(value?: TaskRemindBase | null): string {
  switch (value) {
    case 'INNER':
      return '内部期限'
    case 'DEADLINE':
      return '到期日'
    default:
      return '—'
  }
}

function formatRemindOffsets(row: TaskTemplate): string {
  const remind1 = row.remind_1_offset_days ?? '—'
  const remind2 = row.remind_2_offset_days ?? '—'
  const remind3 = row.remind_3_offset_days ?? '—'
  return `1: ${remind1} / 2: ${remind2} / 3: ${remind3}`
}
</script>

<style scoped>
.table-empty {
  padding: 32px 0;
  color: var(--text-sub);
}
</style>
