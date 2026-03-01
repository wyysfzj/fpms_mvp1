<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">信头管理</h1>
        <span class="page-count">{{ letterheads.length }} 条</span>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="openCreateDialog">
          新增信头
        </el-button>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <LoadingBlock v-if="loading" :rows="8" />

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无信头配置"
        message="新增信头后可用于文档生成。"
        icon="📄"
        cta-label="新增信头"
        @cta="openCreateDialog"
      />
    </div>

    <!-- List -->
    <div v-else class="letterhead-list">
      <div
        v-for="letterhead in letterheads"
        :key="letterhead.id"
        class="letterhead-card"
        :class="{ 'is-default': letterhead.is_default }"
      >
        <div class="letterhead-header">
          <div class="letterhead-name">
            {{ letterhead.name }}
            <el-tag v-if="letterhead.is_default" type="success" size="small">默认</el-tag>
          </div>
          <div class="letterhead-actions">
            <el-tag type="info" size="small">只读</el-tag>
          </div>
        </div>
        <div class="letterhead-content">
          <div v-if="letterhead.header_text" class="letterhead-section">
            <span class="section-label">页眉：</span>
            <span class="section-value">{{ letterhead.header_text }}</span>
          </div>
          <div v-if="letterhead.footer_text" class="letterhead-section">
            <span class="section-label">页脚：</span>
            <span class="section-value">{{ letterhead.footer_text }}</span>
          </div>
          <div v-if="!letterhead.header_text && !letterhead.footer_text" class="letterhead-empty">
            暂未配置页眉或页脚内容。
          </div>
        </div>
        <div class="letterhead-meta">
          <span>创建时间：{{ formatDate(letterhead.created_at) }}</span>
          <span>更新时间：{{ formatDate(letterhead.updated_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Create Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="新增信头"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      @open="handleCreateDialogOpen"
      @close="resetCreateForm"
      @closed="restoreCreateTriggerFocus"
    >
      <div v-if="createError" class="dialog-error">
        <ApiErrorBanner :error="createError" @dismiss="createError = null" />
      </div>

      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-position="top"
      >
        <el-form-item
          label="名称"
          prop="name"
          :error="fieldErrors.get('name')?.join(', ')"
        >
          <el-input
            ref="createNameInputRef"
            v-model.trim="createForm.name"
            placeholder="例如：总部信头"
          />
        </el-form-item>

        <el-form-item prop="is_default">
          <el-checkbox v-model="createForm.is_default">
            设为默认信头
          </el-checkbox>
        </el-form-item>

        <el-form-item
          label="页眉文本"
          prop="header_text"
          :error="fieldErrors.get('header_text')?.join(', ')"
        >
          <el-input
            v-model="createForm.header_text"
            type="textarea"
            :rows="3"
            placeholder="请输入显示在文档页眉的文本"
          />
        </el-form-item>

        <el-form-item
          label="页脚文本"
          prop="footer_text"
          :error="fieldErrors.get('footer_text')?.join(', ')"
        >
          <el-input
            v-model="createForm.footer_text"
            type="textarea"
            :rows="3"
            placeholder="请输入显示在文档页脚的文本"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules, InputInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getLetterheads, createLetterhead } from '../../../api/system'
import type { LetterheadListItem } from '../../../api/system.types'
import type { ApiError } from '../../../api/types'
import { mapFieldErrors } from '../../../api/errors'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'

const letterheads = ref<LetterheadListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const isEmpty = computed(() => !loading.value && !error.value && letterheads.value.length === 0)

// Create dialog state
const showCreateDialog = ref(false)
const creating = ref(false)
const createError = ref<ApiError | null>(null)
const createFormRef = ref<FormInstance>()
const createNameInputRef = ref<InputInstance>()
const fieldErrors = ref<Map<string, string[]>>(new Map())
const lastFocusedElement = ref<HTMLElement | null>(null)

const createForm = reactive({
  name: '',
  is_default: false,
  header_text: '',
  footer_text: '',
})

const createRules: FormRules = {
  name: [
    { required: true, message: '名称为必填项', trigger: 'blur' },
  ],
}

async function fetchLetterheads() {
  loading.value = true
  error.value = null
  try {
    letterheads.value = await getLetterheads()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

function resetCreateForm() {
  createForm.name = ''
  createForm.is_default = false
  createForm.header_text = ''
  createForm.footer_text = ''
  createError.value = null
  fieldErrors.value = new Map()
}

function openCreateDialog() {
  lastFocusedElement.value = document.activeElement instanceof HTMLElement
    ? document.activeElement
    : null
  showCreateDialog.value = true
}

async function handleCreateDialogOpen() {
  await nextTick()
  createNameInputRef.value?.focus?.()
}

function restoreCreateTriggerFocus() {
  lastFocusedElement.value?.focus()
  lastFocusedElement.value = null
}

async function handleCreate() {
  fieldErrors.value = new Map()

  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return

  creating.value = true
  createError.value = null

  try {
    await createLetterhead({
      name: createForm.name,
      is_default: createForm.is_default,
      header_text: createForm.header_text || undefined,
      footer_text: createForm.footer_text || undefined,
    })

    ElMessage.success('信头创建成功')
    showCreateDialog.value = false
    resetCreateForm()
    fetchLetterheads()
  } catch (err) {
    const apiError = err as ApiError
    createError.value = apiError

    if (apiError.status === 422 && apiError.details) {
      fieldErrors.value = mapFieldErrors(apiError.details)
    }
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  fetchLetterheads()
})
</script>

<style scoped>
.letterhead-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.letterhead-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 16px;
  transition: border-color 0.2s;
}

.letterhead-card.is-default {
  border-color: var(--color-success);
}

.letterhead-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.letterhead-name {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.letterhead-content {
  margin-bottom: 12px;
}

.letterhead-section {
  margin-bottom: 8px;
}

.section-label {
  font-size: 12px;
  color: var(--text-sub);
  margin-right: 8px;
}

.section-value {
  font-size: 14px;
  color: var(--text-main);
}

.letterhead-empty {
  color: var(--text-sub);
  font-style: italic;
  font-size: 13px;
}

.letterhead-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
}

.dialog-error {
  margin-bottom: 16px;
}
</style>
