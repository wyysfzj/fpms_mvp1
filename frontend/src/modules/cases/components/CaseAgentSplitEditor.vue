<template>
  <div class="agent-split-editor">
    <div class="section-toolbar">
      <div class="field-hint">支持新增多行分摊记录。请填写代理人、角色和分摊比例，删除最后一行即可清空记录。</div>
      <el-button text type="primary" @click="handleAddRow">新增分摊行</el-button>
    </div>

    <div v-if="rows.length === 0" class="empty-state">
      当前没有分摊记录，点击“新增分摊行”后开始维护。
    </div>

    <div v-for="(row, index) in rows" :key="row.uiKey" class="agent-split-card">
      <div class="agent-split-card-header">
        <span>分摊 {{ index + 1 }}</span>
        <el-button text type="danger" @click="handleRemoveRow(index)">删除</el-button>
      </div>

      <el-row :gutter="16">
        <el-col :span="10">
          <el-form-item label="代理人">
            <el-input
              :model-value="row.agent_id"
              placeholder="请输入代理人"
              clearable
              @update:model-value="(value: unknown) => handleAgentIdChange(index, value)"
            />
          </el-form-item>
        </el-col>
        <el-col :span="7">
          <el-form-item label="角色">
            <el-select
              :model-value="row.role"
              class="full-width"
              placeholder="请选择角色"
              clearable
              @update:model-value="(value: unknown) => handleRoleChange(index, value)"
            >
              <el-option label="代理人" value="Agent" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="7">
          <el-form-item label="分摊比例">
            <el-input-number
              :model-value="row.share_ratio"
              class="full-width"
              :min="0.0001"
              :max="100"
              :precision="4"
              :step="0.0001"
              controls-position="right"
              placeholder="请输入比例"
              @update:model-value="(value: unknown) => handleRatioChange(index, value)"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <div v-if="normalizedRowErrors[index]?.length" class="row-error">
        <div class="row-error-title">本行问题</div>
        <ul class="validation-summary-list">
          <li v-for="message in normalizedRowErrors[index]" :key="message">{{ message }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { CaseAgentSplit } from '../../../api/cases.types'

interface SplitRow extends CaseAgentSplit {
  uiKey: string
}

const props = defineProps<{
  modelValue?: CaseAgentSplit[] | null
  rowErrors?: string[][]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: CaseAgentSplit[]]
}>()

const rows = ref<SplitRow[]>([])
const normalizedRowErrors = computed(() => props.rowErrors ?? [])
let nextKey = 0

function createEmptyAgentSplit(): CaseAgentSplit {
  return {
    agent_id: '',
    role: '',
    share_ratio: null,
  }
}

function createRowKey() {
  nextKey += 1
  return `agent-split-${nextKey}`
}

function toModelRows(nextRows: SplitRow[]): CaseAgentSplit[] {
  return nextRows.map((row) => {
    const { uiKey, ...modelRow } = row
    void uiKey
    return modelRow
  })
}

function emitRows(nextRows: SplitRow[]) {
  emit('update:modelValue', toModelRows(nextRows))
}

function syncRows(value?: CaseAgentSplit[] | null) {
  const incoming = value ?? []
  const previousRows = rows.value
  rows.value = incoming.map((row, index) => ({
    ...row,
    uiKey: previousRows[index]?.uiKey ?? createRowKey(),
  }))
}

watch(() => props.modelValue, (value) => {
  syncRows(value)
}, { immediate: true, deep: true })

function handleAddRow() {
  const nextRows = [...rows.value, { ...createEmptyAgentSplit(), uiKey: createRowKey() }]
  rows.value = nextRows
  emitRows(nextRows)
}

function handleRemoveRow(index: number) {
  const nextRows = [...rows.value]
  nextRows.splice(index, 1)
  rows.value = nextRows
  emitRows(nextRows)
}

function handleAgentIdChange(index: number, value: unknown) {
  updateRow(index, { agent_id: String(value ?? '') })
}

function handleRoleChange(index: number, value: unknown) {
  updateRow(index, { role: String(value ?? '') })
}

function handleRatioChange(index: number, value: unknown) {
  updateRow(index, { share_ratio: typeof value === 'number' ? value : null })
}

function updateRow(index: number, patch: Partial<CaseAgentSplit>) {
  const nextRows = [...rows.value]
  nextRows[index] = {
    ...(nextRows[index] || createEmptyAgentSplit()),
    uiKey: nextRows[index]?.uiKey ?? createRowKey(),
    ...patch,
  }
  rows.value = nextRows
  emitRows(nextRows)
}
</script>

<style scoped>
.agent-split-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.field-hint {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
}

.agent-split-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 10px;
  padding: 16px;
  background: var(--el-bg-color);
}

.agent-split-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
}

.empty-state {
  padding: 16px;
  border-radius: 10px;
  border: 1px dashed var(--el-border-color);
  color: var(--text-sub);
  background: var(--el-fill-color-lighter);
}

.row-error {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  background: var(--el-color-danger-light-9);
  border: 1px solid var(--el-color-danger-light-7);
}

.row-error-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-color-danger);
}

.validation-summary-list {
  margin: 6px 0 0;
  padding-left: 18px;
}

.full-width {
  width: 100%;
}
</style>
