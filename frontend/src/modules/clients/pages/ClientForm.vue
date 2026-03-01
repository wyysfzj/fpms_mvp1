<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">{{ isEdit ? '编辑客户' : '新建客户' }}</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建客户' }}
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- Form -->
    <div v-else class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="client-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">基础信息</h3>
          
          <el-form-item label="客户名称" prop="name" :error="fieldErrors.get('name')?.join(', ')">
            <el-input v-model="form.name" placeholder="请输入客户名称" />
          </el-form-item>
          
          <el-form-item label="联系人" prop="contact_person" :error="fieldErrors.get('contact_person')?.join(', ')">
            <el-input v-model="form.contact_person" placeholder="请输入联系人姓名" />
          </el-form-item>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">联系方式</h3>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="电话" prop="phone" :error="fieldErrors.get('phone')?.join(', ')">
                <el-input v-model="form.phone" placeholder="请输入电话号码" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱" prop="email" :error="fieldErrors.get('email')?.join(', ')">
                <el-input v-model="form.email" placeholder="请输入邮箱地址" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="地址" prop="address" :error="fieldErrors.get('address')?.join(', ')">
            <el-input 
              v-model="form.address" 
              type="textarea" 
              :rows="3" 
              placeholder="请输入地址" 
            />
          </el-form-item>
        </div>

        <!-- Deactivate Section (Edit mode only) -->
        <div v-if="isEdit && client?.is_active" class="form-section form-section-danger">
          <h3 class="form-section-title">风险操作</h3>
          <div class="danger-action">
            <div class="danger-action-info">
              <strong>停用客户</strong>
              <p>停用后该客户将不可用，但已关联案件会继续保留。</p>
            </div>
            <el-button type="danger" plain :loading="deactivating" @click="handleDeactivate">
              停用
            </el-button>
          </div>
        </div>

        <div v-if="isEdit && !client?.is_active" class="form-section">
          <el-tag type="warning" size="large">该客户已停用</el-tag>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getClient, createClient, updateClient, deactivateClient } from '../../../api/clients'
import type { Client, ClientCreatePayload } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

const route = useRoute()
const router = useRouter()

const clientId = computed(() => {
  const id = route.params.id
  return id ? String(id) : null
})

const isEdit = computed(() => !!clientId.value)

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const deactivating = ref(false)
const error = ref<ApiError | null>(null)
const client = ref<Client | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const form = reactive<ClientCreatePayload>({
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
})

const rules: FormRules = {
  name: [
    { required: true, message: '客户名称为必填项', trigger: 'blur' },
  ],
  email: [
    { type: 'email', message: '请输入有效邮箱地址', trigger: 'blur' },
  ],
}

async function fetchClient() {
  if (!clientId.value) return
  
  loading.value = true
  error.value = null
  try {
    client.value = await getClient(clientId.value)
    // Populate form with existing data
    form.name = client.value.name
    form.contact_person = client.value.contact_person || ''
    form.phone = client.value.phone || ''
    form.email = client.value.email || ''
    form.address = client.value.address || ''
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
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
    if (isEdit.value && clientId.value) {
      await updateClient(clientId.value, form)
      ElMessage.success('客户更新成功')
    } else {
      await createClient(form)
      ElMessage.success('客户创建成功')
    }
    router.push('/clients')
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

async function handleDeactivate() {
  if (!clientId.value) return
  
  try {
    await ElMessageBox.confirm(
      '确定要停用该客户吗？此操作不可撤销。',
      '停用客户',
      {
        confirmButtonText: '确认停用',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
      }
    )
    
    deactivating.value = true
    await deactivateClient(clientId.value)
    ElMessage.success('客户已停用')
    router.push('/clients')
  } catch (err) {
    if (err !== 'cancel') {
      error.value = err as ApiError
    }
  } finally {
    deactivating.value = false
  }
}

function handleCancel() {
  router.push('/clients')
}

onMounted(() => {
  if (isEdit.value) {
    fetchClient()
  }
})
</script>
