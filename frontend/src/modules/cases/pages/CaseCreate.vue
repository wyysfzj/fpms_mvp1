<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">新建案件</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          创建案件
        </el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading Clients -->
    <div v-if="loadingClients" class="page-loading">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- Form -->
    <div v-else class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="case-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">基础信息</h3>
          
          <el-form-item label="案号" prop="case_no" :error="fieldErrors.get('case_no')?.join(', ')">
            <el-input v-model="form.case_no" placeholder="请输入案号（例如：P2024-001）" />
          </el-form-item>
          
          <el-form-item label="标题" prop="title" :error="fieldErrors.get('title')?.join(', ')">
            <el-input v-model="form.title" placeholder="请输入案件标题" />
          </el-form-item>

          <el-form-item label="客户" prop="client_id" :error="fieldErrors.get('client_id')?.join(', ')">
            <el-select
              v-model="form.client_id"
              placeholder="请选择客户"
              :loading="loadingClients"
              filterable
              class="full-width"
            >
              <el-option
                v-for="client in clients"
                :key="client.id"
                :label="client.name"
                :value="client.id"
              />
            </el-select>
            <div v-if="clientsTotal > clients.length" class="field-hint">
              当前显示 {{ clients.length }} / {{ clientsTotal }} 位客户
            </div>
          </el-form-item>
        </div>

        <el-collapse v-model="expandedSections" class="case-extra-sections">
          <el-collapse-item title="公告与授权" name="pub_grant">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="公告日">
                  <el-date-picker v-model="form.pub_date" type="date" placeholder="请选择公告日"
                    format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="公告号">
                  <el-input v-model="form.pub_no" placeholder="请输入公告号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="授权日">
                  <el-date-picker v-model="form.grant_date" type="date" placeholder="请选择授权日"
                    format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="授权号">
                  <el-input v-model="form.grant_no" placeholder="请输入授权号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="专利号">
                  <el-input v-model="form.patent_no" placeholder="请输入专利号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="有效期至">
                  <el-date-picker v-model="form.valid_until" type="date" placeholder="请选择有效期至"
                    format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item title="说明书信息" name="spec">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="说明书页数">
                  <el-input-number v-model="form.spec_pages" :min="0" controls-position="right"
                    placeholder="页数" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="权利要求项数">
                  <el-input-number v-model="form.claim_count" :min="0" controls-position="right"
                    placeholder="项数" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="已提实审请求">
                  <el-switch v-model="form.has_exam_request" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item title="代理人分配" name="agent">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="主办代理人">
                  <el-input v-model="form.primary_agent_id" placeholder="请输入代理人ID" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="辅办代理人">
                  <el-input v-model="form.second_agent_id" placeholder="请输入代理人ID" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="撰写人">
                  <el-input v-model="form.draftor_id" placeholder="请输入撰写人ID" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>

          <el-collapse-item title="控制标记" name="flags">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="费用监控">
                  <el-switch v-model="form.is_fee_monitor" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="减免类型">
                  <el-select v-model="form.fee_reduction" placeholder="请选择" clearable style="width: 100%">
                    <el-option label="不减免" value="NONE" />
                    <el-option label="部分减免" value="PARTIAL" />
                    <el-option label="全额减免" value="FULL" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="申请人类型">
                  <el-select v-model="form.applicant_kind" placeholder="请选择" clearable style="width: 100%">
                    <el-option label="个人" value="INDIVIDUAL" />
                    <el-option label="企业" value="ENTITY" />
                    <el-option label="高校" value="UNIV" />
                    <el-option label="政府" value="GOV" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createCase } from '../../../api/cases'
import { getClients } from '../../../api/clients'
import type { CaseCreatePayload } from '../../../api/cases.types'
import type { Client } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

const router = useRouter()

const formRef = ref<FormInstance>()
const saving = ref(false)
const loadingClients = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const clients = ref<Client[]>([])
const clientsTotal = ref(0)
const expandedSections = ref<string[]>([])

const form = reactive<CaseCreatePayload>({
  case_no: '',
  title: '',
  client_id: '',
})

const rules: FormRules = {
  case_no: [
    { required: true, message: '案号为必填项', trigger: 'blur' },
  ],
  client_id: [
    { required: true, message: '请选择客户', trigger: 'change' },
  ],
}

async function fetchClients() {
  loadingClients.value = true
  try {
    const result = await getClients({ page: 1, page_size: 100 })
    clients.value = result.items
    clientsTotal.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loadingClients.value = false
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
    await createCase(form)
    ElMessage.success('案件创建成功')
    router.push('/cases')
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
  router.push('/cases')
}

onMounted(() => {
  fetchClients()
})
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

.case-form .el-form-item {
  margin-bottom: 20px;
}

.case-form .el-form-item__label {
  font-weight: 500;
  color: var(--text-main);
}
</style>
