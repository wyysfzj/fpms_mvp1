<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">文件模板管理</h1>
        <span class="page-count">{{ total }} 条</span>
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
      <el-table-column prop="code" label="编码" width="120" />
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column label="方向" width="80">
        <template #default="{ row }">
          <el-tag :type="row.direction === 'IN' ? '' : 'warning'" size="small">
            {{ row.direction === 'IN' ? '收文' : '发文' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态变更" width="120">
        <template #default="{ row }">{{ getStatusEffectLabel(row.status_effect) }}</template>
      </el-table-column>
      <el-table-column label="期限模板" width="140">
        <template #default="{ row }">{{ getDeadlineTemplateLabel(row.deadline_template_code) }}</template>
      </el-table-column>
      <el-table-column label="费用类型" width="120">
        <template #default="{ row }">{{ getFeeDraftTypeLabel(row.fee_draft_type) }}</template>
      </el-table-column>
      <el-table-column label="需回复" width="80">
        <template #default="{ row }">
          <el-tag :type="row.need_reply ? 'warning' : 'info'" size="small">
            {{ row.need_reply ? '是' : '否' }}
          </el-tag>
        </template>
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
        <div class="table-empty">暂无文件模板，点击"新增模板"创建。</div>
      </template>
    </el-table>

    <!-- Pagination -->
    <el-pagination
      v-if="total > pageSize"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end;"
      @current-change="handlePageChange"
    />

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEdit ? '编辑文件模板' : '新增文件模板'"
      width="640px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-position="top"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="编码" prop="code">
              <el-input v-model.trim="form.code" :disabled="isEdit" placeholder="模板编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名称" prop="name">
              <el-input v-model.trim="form.name" placeholder="模板名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="方向">
              <el-select v-model="form.direction" style="width: 100%">
                <el-option label="收文" value="IN" />
                <el-option label="发文" value="OUT" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="isEdit">
            <el-form-item label="启用">
              <el-switch v-model="form.enabled" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态变更">
              <el-input v-model.trim="form.status_effect" placeholder="请输入状态编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态恢复">
              <el-input v-model.trim="form.status_restore" placeholder="请输入恢复状态编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="期限模板">
              <el-select v-model="form.deadline_template_code" placeholder="选择期限模板" clearable style="width: 100%">
                <el-option
                  v-for="t in taskTemplateOptions"
                  :key="t.code"
                  :label="t.name"
                  :value="t.code"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="费用类型">
              <el-input v-model.trim="form.fee_draft_type" placeholder="请输入费用草稿类型编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="需回复">
              <el-switch v-model="form.need_reply" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="回复模板编码">
              <el-input v-model.trim="form.reply_to_template_code" placeholder="回复对应的模板编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="费用项目列表">
          <el-input
            v-model="form.fee_item_list"
            type="textarea"
            :rows="3"
            placeholder="请输入费用项目配置"
          />
        </el-form-item>
        <el-form-item label="输入字段定义">
          <el-input
            v-model="form.input_fields"
            type="textarea"
            :rows="3"
            placeholder="请输入输入字段配置"
          />
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
import { getDocTemplates, createDocTemplate, updateDocTemplate } from '../../../api/documents'
import type { DocTemplate } from '../../../api/documents.types'
import { getTaskTemplates } from '../../../api/tasks'
import type { TaskTemplate } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { getCaseStatusText } from '../../../constants/displayText'

const templates = ref<DocTemplate[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const taskTemplateOptions = ref<TaskTemplate[]>([])

const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref('')
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  code: '',
  name: '',
  direction: 'IN' as 'IN' | 'OUT',
  enabled: true,
  status_effect: '',
  status_restore: '',
  deadline_template_code: '',
  fee_draft_type: '',
  need_reply: false,
  reply_to_template_code: '',
  fee_item_list: '',
  input_fields: '',
})

const formRules: FormRules = {
  code: [{ required: true, message: '编码为必填项', trigger: 'blur' }],
  name: [{ required: true, message: '名称为必填项', trigger: 'blur' }],
}

const FEE_DRAFT_TYPE_TEXT: Record<string, string> = {
  APPLY_FEE: '申请费草稿',
  OA_FEE: '审查意见费草稿',
  GRANT_FEE: '授权费草稿',
  ANNUITY_FEE: '年费草稿',
  INVALIDATION_FEE: '无效费草稿',
  LITIGATION_FEE: '诉讼费草稿',
  CONSULT_FEE: '顾问费草稿',
  SEARCH_FEE: '检索费草稿',
  INTERMEDIATE_FEE: '中间文件费草稿',
}

function getStatusEffectLabel(status?: string | null): string {
  if (!status) return '—'
  return getCaseStatusText(status)
}

function getDeadlineTemplateLabel(code?: string | null): string {
  if (!code) return '—'
  const matched = taskTemplateOptions.value.find((item) => item.code === code)
  return matched?.name || code
}

function getFeeDraftTypeLabel(type?: string | null): string {
  if (!type) return '—'
  return FEE_DRAFT_TYPE_TEXT[type] || type
}

async function fetchTemplates() {
  loading.value = true
  error.value = null
  try {
    const result = await getDocTemplates({ page: currentPage.value, page_size: pageSize.value })
    templates.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function fetchTaskTemplates() {
  try {
    taskTemplateOptions.value = await getTaskTemplates(true)
  } catch {
    // Silently fail — dropdown will be empty
  }
}

function handlePageChange(page: number) {
  currentPage.value = page
  fetchTemplates()
}

function resetForm() {
  form.code = ''
  form.name = ''
  form.direction = 'IN'
  form.enabled = true
  form.status_effect = ''
  form.status_restore = ''
  form.deadline_template_code = ''
  form.fee_draft_type = ''
  form.need_reply = false
  form.reply_to_template_code = ''
  form.fee_item_list = ''
  form.input_fields = ''
}

function openCreate() {
  resetForm()
  isEdit.value = false
  editingId.value = ''
  showDialog.value = true
}

function openEdit(row: DocTemplate) {
  form.code = row.code
  form.name = row.name
  form.direction = row.direction
  form.enabled = row.enabled
  form.status_effect = row.status_effect || ''
  form.status_restore = row.status_restore || ''
  form.deadline_template_code = row.deadline_template_code || ''
  form.fee_draft_type = row.fee_draft_type || ''
  form.need_reply = row.need_reply ?? false
  form.reply_to_template_code = row.reply_to_template_code || ''
  form.fee_item_list = row.fee_item_list || ''
  form.input_fields = row.input_fields || ''
  isEdit.value = true
  editingId.value = row.id
  showDialog.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await updateDocTemplate(editingId.value, {
        name: form.name,
        direction: form.direction,
        enabled: form.enabled,
        status_effect: form.status_effect || null,
        status_restore: form.status_restore || null,
        deadline_template_code: form.deadline_template_code || null,
        fee_draft_type: form.fee_draft_type || null,
        need_reply: form.need_reply,
        reply_to_template_code: form.reply_to_template_code || null,
        fee_item_list: form.fee_item_list || null,
        input_fields: form.input_fields || null,
      })
      ElMessage.success('模板更新成功')
    } else {
      await createDocTemplate({
        code: form.code,
        name: form.name,
        direction: form.direction,
        status_effect: form.status_effect || null,
        status_restore: form.status_restore || null,
        deadline_template_code: form.deadline_template_code || null,
        fee_draft_type: form.fee_draft_type || null,
        need_reply: form.need_reply,
        reply_to_template_code: form.reply_to_template_code || null,
        fee_item_list: form.fee_item_list || null,
        input_fields: form.input_fields || null,
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

async function handleToggleEnabled(row: DocTemplate) {
  try {
    await updateDocTemplate(row.id, { enabled: !row.enabled })
    ElMessage.success(row.enabled ? '已停用' : '已启用')
    fetchTemplates()
  } catch (err) {
    const apiError = err as ApiError
    ElMessage.error(apiError.message || '操作失败')
  }
}

onMounted(() => {
  fetchTemplates()
  fetchTaskTemplates()
})
</script>

<style scoped>
.table-empty {
  padding: 32px 0;
  color: var(--text-sub);
}
</style>
