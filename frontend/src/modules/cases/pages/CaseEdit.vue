<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">编辑案件</h1>
      </div>
      <div class="page-header-right">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存修改
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
        class="case-form"
      >
        <div class="form-section">
          <h3 class="form-section-title">案件信息</h3>

          <el-form-item label="案号">
            <el-input :model-value="caseData?.case_no" disabled />
          </el-form-item>

          <el-form-item label="标题" prop="title" :error="fieldErrors.get('title')?.join(', ')">
            <el-input v-model="form.title" placeholder="请输入案件标题" />
          </el-form-item>

          <el-form-item label="法律状态" prop="status" :error="fieldErrors.get('status')?.join(', ')">
            <el-select v-model="form.status" placeholder="请选择法律状态" clearable>
              <el-option label="未递交" value="NOT_FILED" />
              <el-option label="等待受理" value="WAITING_RECEIPT" />
              <el-option label="初审" value="PRELIM_EXAM" />
              <el-option label="补正中" value="AMENDMENT" />
              <el-option label="初审通过" value="PRELIM_PASS" />
              <el-option label="已公开" value="PUBLISHED" />
              <el-option label="实审中" value="SUB_EXAM" />
              <el-option label="一通阶段" value="OA1" />
              <el-option label="二通阶段" value="OA2" />
              <el-option label="复审中" value="REEXAM" />
              <el-option label="已授权" value="GRANTED" />
              <el-option label="驳回" value="REJECTED" />
              <el-option label="中止/终止" value="TERMINATED" />
              <el-option label="全部无效" value="INVALIDATED" />
              <el-option label="部分无效" value="INVALIDATED_PARTIAL" />
            </el-select>
          </el-form-item>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">日期信息</h3>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="申请日" prop="filing_date" :error="fieldErrors.get('filing_date')?.join(', ')">
                <el-date-picker
                  v-model="form.filing_date"
                  type="date"
                  placeholder="请选择申请日"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="优先权日" prop="app_date" :error="fieldErrors.get('app_date')?.join(', ')">
                <el-date-picker
                  v-model="form.app_date"
                  type="date"
                  placeholder="请选择优先权日"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <h3 class="form-section-title">备注</h3>

          <el-form-item prop="notes" :error="fieldErrors.get('notes')?.join(', ')">
            <el-input
              v-model="form.notes"
              type="textarea"
              :rows="4"
              placeholder="请输入案件备注"
            />
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getCase, updateCase } from '../../../api/cases'
import type { Case, CaseUpdatePayload } from '../../../api/cases.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { mapValidationDetailsToFieldErrors } from '../../../utils/validation'

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const error = ref<ApiError | null>(null)
const caseData = ref<Case | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())
const expandedSections = ref<string[]>([])

const form = reactive<CaseUpdatePayload>({
  title: '',
  status: '',
  filing_date: '',
  app_date: '',
  notes: '',
})

const rules: FormRules = {
  title: [
    { max: 500, message: '标题不能超过 500 个字符', trigger: 'blur' },
  ],
}

async function fetchCase() {
  const id = String(route.params.id || '').trim()
  if (!id) {
    return
  }

  loading.value = true
  error.value = null

  try {
    caseData.value = await getCase(id)
    // Populate form with existing data
    form.title = caseData.value.title || ''
    form.status = caseData.value.status || ''
    form.filing_date = caseData.value.filing_date || ''
    form.app_date = caseData.value.app_date || ''
    form.notes = caseData.value.notes || ''
    // A3 fields
    form.pub_date = caseData.value.pub_date || ''
    form.pub_no = caseData.value.pub_no || ''
    form.grant_date = caseData.value.grant_date || ''
    form.grant_no = caseData.value.grant_no || ''
    form.patent_no = caseData.value.patent_no || ''
    form.valid_until = caseData.value.valid_until || ''
    form.spec_pages = caseData.value.spec_pages ?? undefined
    form.claim_count = caseData.value.claim_count ?? undefined
    form.has_exam_request = caseData.value.has_exam_request ?? undefined
    form.primary_agent_id = caseData.value.primary_agent_id || ''
    form.second_agent_id = caseData.value.second_agent_id || ''
    form.draftor_id = caseData.value.draftor_id || ''
    form.is_fee_monitor = caseData.value.is_fee_monitor ?? undefined
    form.fee_reduction = caseData.value.fee_reduction || ''
    form.applicant_kind = caseData.value.applicant_kind || ''
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  const id = String(route.params.id || '').trim()
  if (!id) return

  // Clear previous field errors
  fieldErrors.value = new Map()

  // Validate form
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  error.value = null

  try {
    await updateCase(id, form)
    ElMessage.success('案件更新成功')
    router.push(`/cases/${id}`)
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
  const id = route.params.id
  router.push(`/cases/${id}`)
}

onMounted(() => {
  fetchCase()
})
</script>
