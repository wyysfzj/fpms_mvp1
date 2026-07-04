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
          @change="handleCaseChange"
        >
          <el-option
            v-for="c in caseOptions"
            :key="c.id"
            :label="c.case_no"
            :value="c.id"
          />
        </el-select>
      </el-form-item>
      <el-alert
        v-if="targetCaseNo"
        class="target-alert"
        type="warning"
        :closable="false"
        show-icon
      >
        <template #title>
          将为案件编号 {{ targetCaseNo }} 生成年费任务
        </template>
      </el-alert>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
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
  initialCaseNo?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: [result: AnnuityTaskGenerateResult]
}>()

const visible = ref(props.modelValue)
const formRef = ref<FormInstance>()
const saving = ref(false)
const caseSearchLoading = ref(false)
const caseOptions = ref<CaseOption[]>([])
const selectedCaseNo = ref('')
const caseSearchKeyword = ref('')

const form = reactive<GenerateForm>({
  case_id: '',
})

const targetCaseNo = computed(() => selectedCaseNo.value || caseSearchKeyword.value.trim() || form.case_id.trim())

const rules: FormRules<GenerateForm> = {
  case_id: [{ required: true, message: '请选择案卷', trigger: 'change' }],
}

watch(
  () => props.modelValue,
  (value) => {
    visible.value = value
    if (value) {
      resetFormFromInitialCase()
    }
  },
)

watch(visible, (value) => {
  emit('update:modelValue', value)
})

async function searchCases(query: string) {
  caseSearchKeyword.value = query.trim()
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

async function resolveCaseSelection(): Promise<boolean> {
  const rawValue = form.case_id.trim() || caseSearchKeyword.value.trim() || selectedCaseNo.value.trim()
  if (!rawValue) return false

  const matched = caseOptions.value.find((item) => item.id === rawValue || item.case_no === rawValue)
  if (matched) {
    form.case_id = matched.id
    selectedCaseNo.value = matched.case_no
    return true
  }

  caseSearchLoading.value = true
  try {
    const result = await getCases({ page: 1, page_size: 5, case_no: rawValue } as Parameters<typeof getCases>[0])
    const exact = result.items.find((item) => item.case_no === rawValue) || result.items[0]
    if (!exact) return false
    const resolved = { id: exact.id, case_no: exact.case_no }
    caseOptions.value = [resolved]
    form.case_id = resolved.id
    selectedCaseNo.value = resolved.case_no
    return true
  } finally {
    caseSearchLoading.value = false
  }
}

function resetFormFromInitialCase() {
  const initialCaseNo = props.initialCaseNo?.trim() || ''
  form.case_id = initialCaseNo
  selectedCaseNo.value = initialCaseNo
  caseSearchKeyword.value = initialCaseNo
  caseOptions.value = initialCaseNo ? [{ id: initialCaseNo, case_no: initialCaseNo }] : []
}

function handleCaseChange(value: string) {
  const matchedCase = caseOptions.value.find((item) => item.id === value)
  selectedCaseNo.value = matchedCase?.case_no || value
  caseSearchKeyword.value = selectedCaseNo.value
}

function handleClose() {
  visible.value = false
}

async function handleSubmit() {
  const resolved = await resolveCaseSelection()
  if (!resolved) {
    ElMessage.error('请先选择有效案卷')
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  const confirmedCaseNo = targetCaseNo.value
  try {
    await ElMessageBox.confirm(
      `确认仅为案件编号 ${confirmedCaseNo} 生成年费任务？`,
      '确认生成年费任务',
      {
        confirmButtonText: '确认生成',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  saving.value = true
  try {
    const result: AnnuityTaskGenerateResult = await generateAnnuityTasks({ case_id: form.case_id })
    ElMessage.success(`已生成 ${result.tasks_created} 条年费任务，跳过 ${result.tasks_skipped} 条已存在记录`)
    visible.value = false
    emit('saved', result)
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

<style scoped>
.target-alert {
  margin-bottom: 16px;
}
</style>
