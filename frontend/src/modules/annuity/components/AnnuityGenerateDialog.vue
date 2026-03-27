<template>
  <el-dialog
    v-model="visible"
    title="生成年费任务"
    width="480px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
    >
      <el-form-item label="案卷" prop="case_id">
        <el-select
          v-model="form.case_id"
          filterable
          remote
          clearable
          :remote-method="searchCases"
          :loading="caseSearchLoading"
          placeholder="请输入案卷编号搜索"
          style="width: 100%"
        >
          <el-option
            v-for="c in caseOptions"
            :key="c.id"
            :label="c.case_no"
            :value="c.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { generateAnnuityTasks } from '../../../api/annuity'
import type { AnnuityTaskGenerateResult } from '../../../api/annuity.types'
import { getCases } from '../../../api/cases'

interface CaseOption {
  id: string
  case_no: string
}

interface GenerateForm {
  case_id: string
}

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: []
}>()

const visible = ref(props.modelValue)
const formRef = ref<FormInstance>()
const saving = ref(false)
const caseSearchLoading = ref(false)
const caseOptions = ref<CaseOption[]>([])

const form = reactive<GenerateForm>({
  case_id: '',
})

const rules: FormRules<GenerateForm> = {
  case_id: [{ required: true, message: '请选择案卷', trigger: 'change' }],
}

watch(
  () => props.modelValue,
  (value) => {
    visible.value = value
    if (value) {
      form.case_id = ''
      caseOptions.value = []
    }
  },
)

watch(visible, (value) => {
  emit('update:modelValue', value)
})

async function searchCases(query: string) {
  if (!query || query.trim().length < 1) {
    caseOptions.value = []
    return
  }
  caseSearchLoading.value = true
  try {
    const result = await getCases({ page: 1, page_size: 20, case_no: query.trim() } as Parameters<typeof getCases>[0])
    caseOptions.value = result.items.map((c) => ({ id: c.id, case_no: c.case_no }))
  } catch {
    caseOptions.value = []
  } finally {
    caseSearchLoading.value = false
  }
}

function handleClose() {
  visible.value = false
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const result: AnnuityTaskGenerateResult = await generateAnnuityTasks({ case_id: form.case_id })
    ElMessage.success(`已生成 ${result.tasks_created} 条年费任务，跳过 ${result.tasks_skipped} 条已存在记录`)
    visible.value = false
    emit('saved')
  } catch (err: unknown) {
    const axiosErr = err as { response?: { data?: { message?: string } } }
    const bizMsg = axiosErr?.response?.data?.message
    if (bizMsg) {
      ElMessage.error(bizMsg)
    } else {
      ElMessage.error('生成失败，请重试')
    }
  } finally {
    saving.value = false
  }
}
</script>
