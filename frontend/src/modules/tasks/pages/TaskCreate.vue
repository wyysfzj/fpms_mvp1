<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">新建任务</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          创建任务
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Form -->
    <div class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="task-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">任务信息</h3>
          
          <el-form-item label="标题" prop="title" :error="fieldErrors.get('title')?.join(', ')">
            <el-input v-model="form.title" placeholder="请输入任务标题" />
          </el-form-item>
          
          <el-form-item label="描述" prop="description" :error="fieldErrors.get('description')?.join(', ')">
            <el-input 
              v-model="form.description" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入任务描述" 
            />
          </el-form-item>

          <el-form-item label="案件编号" prop="case_id" :error="fieldErrors.get('case_id')?.join(', ')">
            <el-input
              v-model.trim="form.case_id"
              placeholder="请输入案件编号"
              class="full-width"
            />
            <div class="field-hint">
              <router-link to="/cases">查看案件列表</router-link> 以获取正确编号
            </div>
          </el-form-item>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">详细设置</h3>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="优先级" prop="priority" :error="fieldErrors.get('priority')?.join(', ')">
                <el-select v-model="form.priority" placeholder="请选择优先级" clearable class="full-width">
                  <el-option label="低" value="low" />
                  <el-option label="中" value="medium" />
                  <el-option label="高" value="high" />
                  <el-option label="紧急" value="urgent" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="截止日期" prop="due_date" :error="fieldErrors.get('due_date')?.join(', ')">
                <el-date-picker
                  v-model="form.due_date"
                  type="date"
                  placeholder="请选择截止日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  class="full-width"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="负责人" prop="assigned_to" :error="fieldErrors.get('assigned_to')?.join(', ')">
            <el-input v-model="form.assigned_to" placeholder="请输入负责人" />
          </el-form-item>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createTask } from '../../../api/tasks'
import type { TaskCreatePayload } from '../../../api/tasks.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const form = reactive<TaskCreatePayload>({
  title: '',
  description: '',
  case_id: '',
  priority: '',
  due_date: '',
  assigned_to: '',
})

const rules: FormRules = {
  title: [
    { required: true, message: '标题为必填项', trigger: 'blur' },
  ],
  case_id: [
    { required: true, message: '案件编号为必填项', trigger: 'blur' },
  ],
  due_date: [
    { required: true, message: '截止日期为必填项', trigger: 'change' },
  ],
}

async function handleSave() {
  // Clear previous field errors
  fieldErrors.value = new Map()
  
  // Validate form
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  error.value = null
  
  try {
    // Build payload, omitting empty optional fields
    const payload: TaskCreatePayload = {
      title: form.title,
      case_id: form.case_id,
      due_date: form.due_date,
    }
    if (form.description) payload.description = form.description
    if (form.priority) payload.priority = form.priority
    if (form.assigned_to) payload.assigned_to = form.assigned_to

    await createTask(payload)
    ElMessage.success('任务创建成功')
    router.push('/tasks')
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError
    
    // Map 422 field errors
    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapValidationDetailsToFieldErrors(apiError.details)
    }
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  router.push('/tasks')
}
</script>

<style scoped>
.full-width {
  width: 100%;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
}

.field-hint a {
  color: var(--color-primary);
}

.task-form .el-form-item {
  margin-bottom: 20px;
}

.task-form .el-form-item__label {
  font-weight: 500;
  color: var(--text-main);
}
</style>
