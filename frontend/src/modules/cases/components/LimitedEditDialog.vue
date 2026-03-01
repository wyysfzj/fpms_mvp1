<template>
  <el-dialog
    v-model="visible"
    title="快速编辑"
    width="500px"
    :close-on-click-modal="false"
    class="limited-edit-dialog"
    @close="handleClose"
  >
    <!-- Error Banner -->
    <div v-if="error" class="dialog-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <el-form
      ref="formRef"
      :model="form"
      label-position="top"
    >
      <el-form-item label="备注" prop="notes" :error="fieldErrors.get('notes')?.join(', ')">
        <el-input
          v-model="form.notes"
          type="textarea"
          :rows="4"
          placeholder="请输入备注"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { limitedEditCase } from '../../../api/cases'
import type { CaseLimitedEditPayload } from '../../../api/cases.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'

const props = defineProps<{
  modelValue: boolean
  caseId: string | number
  initialNotes?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const visible = ref(props.modelValue)
const formRef = ref<FormInstance>()
const saving = ref(false)
const error = ref<ApiError | null>(null)
const fieldErrors = ref<Map<string, string[]>>(new Map())

const form = reactive<CaseLimitedEditPayload>({
  notes: props.initialNotes || '',
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    // Reset form when dialog opens
    form.notes = props.initialNotes || ''
    error.value = null
    fieldErrors.value = new Map()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

function handleClose() {
  visible.value = false
}

async function handleSave() {
  fieldErrors.value = new Map()
  saving.value = true
  error.value = null

  try {
    await limitedEditCase(props.caseId, form)
    ElMessage.success('案件更新成功')
    visible.value = false
    emit('success')
  } catch (err) {
    const apiError = err as ApiError
    error.value = apiError

    // Map 422 field errors
    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
    // Note: 403 is handled globally by http.ts interceptor
  } finally {
    saving.value = false
  }
}
</script>
