<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">邮寄信息登记</h1>
        <span class="page-count">{{ total }} 条候选去文</span>
      </div>
      <div class="page-header-right">
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          批量登记
        </el-button>
      </div>
    </div>

    <el-card class="filter-panel" shadow="never">
      <el-form :model="filters" label-position="top">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="标题 / 文号">
              <el-input
                v-model.trim="filters.q"
                placeholder="按标题或文号搜索"
                clearable
                @keyup.enter="fetchCandidates"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="客户">
              <el-select v-model="filters.client_id" clearable filterable class="full-width" placeholder="全部客户">
                <el-option
                  v-for="client in clients"
                  :key="client.id"
                  :label="client.name"
                  :value="client.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="模板">
              <el-select
                v-model="filters.doc_template_id"
                clearable
                filterable
                class="full-width"
                placeholder="全部模板"
              >
                <el-option
                  v-for="template in templates"
                  :key="template.id"
                  :label="`${template.code} — ${template.name}`"
                  :value="template.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="文档日期范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                class="full-width"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8" class="filter-actions">
            <el-button type="primary" :loading="loading" @click="fetchCandidates">查询去文</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="action-panel" shadow="never">
      <div class="action-panel-header">
        <h3>登记参数</h3>
        <div class="selection-summary">已选 {{ selectedIds.length }} 份去文</div>
      </div>
      <el-form :model="actionForm" inline>
        <el-form-item label="寄出编号" required>
          <el-input v-model.trim="actionForm.outgoing_reg_no" placeholder="请输入寄出编号" />
        </el-form-item>
        <el-form-item label="转寄日期">
          <el-date-picker
            v-model="actionForm.forward_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>
      <el-alert
        title="当前只关闭邮寄信息登记，不在本页生成交接单或信封。"
        type="info"
        :closable="false"
        show-icon
      />
    </el-card>

    <el-card class="action-panel" shadow="never">
      <div class="action-panel-header">
        <h3>文件交接单</h3>
        <div class="selection-summary">用于生成交接单的去文 {{ selectedIds.length }} 份</div>
      </div>
      <el-form :model="dispatchForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="客户" required>
              <el-select
                v-model="dispatchForm.client_id"
                clearable
                filterable
                class="full-width"
                placeholder="请先选择客户"
              >
                <el-option
                  v-for="client in clients"
                  :key="client.id"
                  :label="client.name"
                  :value="client.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="交接日期" required>
              <el-date-picker
                v-model="dispatchForm.dispatch_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="请选择交接日期"
                class="full-width"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注">
              <el-input v-model.trim="dispatchForm.remark" placeholder="可选备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div class="dispatch-actions">
        <el-button type="primary" :loading="creatingDispatch" @click="handleCreateDispatch">
          生成交接单
        </el-button>
        <el-button :disabled="!currentDispatchId" @click="handleReloadDispatch">
          重新加载详情
        </el-button>
        <span v-if="currentDispatchId" class="dispatch-meta">当前交接单编号：{{ currentDispatchId }}</span>
      </div>
    </el-card>

    <el-card v-if="dispatchDetail" class="action-panel" shadow="never">
      <div class="action-panel-header">
        <h3>交接单详情</h3>
        <div class="selection-summary">
          {{ dispatchDetail.client_name || dispatchDetail.client_id }} · {{ dispatchDetail.dispatch_date }}
        </div>
      </div>
      <div class="dispatch-detail-meta">
        <span>交接单编号：{{ dispatchDetail.id }}</span>
        <span>明细数量：{{ dispatchDetail.lines.length }}</span>
        <span>备注：{{ dispatchDetail.remark || '无' }}</span>
      </div>
      <el-table :data="dispatchDetail.lines" stripe size="small">
        <el-table-column prop="case_no" label="案号" width="180" />
        <el-table-column prop="doc_name" label="文件名称" min-width="220" />
        <el-table-column prop="outgoing_reg_no" label="寄出编号" min-width="160" />
      </el-table>
    </el-card>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <div v-else class="page-table">
      <el-table :data="documents" stripe size="small" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="case_no" label="案号" width="170" />
        <el-table-column prop="title" label="标题" min-width="220" />
        <el-table-column label="方向" width="100">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'OUT' ? 'warning' : 'success'" size="small">
              {{ row.direction === 'OUT' ? '发文' : '收文' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="doc_date" label="文档日期" width="120" />
        <el-table-column prop="ref_no" label="文号" min-width="160" />
        <el-table-column label="当前寄出编号" min-width="180">
          <template #default="{ row }">
            {{ row.outgoing_reg_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="当前转寄日期" width="130">
          <template #default="{ row }">
            {{ row.forward_date || '-' }}
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar
        v-model:page="page"
        v-model:page-size="pageSize"
        :total="total"
        @change="fetchCandidates"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { getClients } from '../../../api/clients'
import {
  batchRegisterDocumentMailing,
  createDocumentDispatch,
  getDocTemplates,
  getDocumentDispatch,
  getDocumentDispatchMailingCandidates,
} from '../../../api/documents'
import type { Client } from '../../../api/clients.types'
import type {
  DocTemplate,
  Document,
  DocumentDispatchOut,
  DocumentDispatchMailingListParams,
} from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const documents = ref<Document[]>([])
const clients = ref<Client[]>([])
const templates = ref<DocTemplate[]>([])
const loading = ref(false)
const submitting = ref(false)
const error = ref<ApiError | null>(null)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedIds = ref<string[]>([])
const creatingDispatch = ref(false)
const dispatchDetail = ref<DocumentDispatchOut | null>(null)
const currentDispatchId = ref('')

const filters = reactive<DocumentDispatchMailingListParams>({
  q: '',
  client_id: '',
  doc_template_id: '',
  date_from: '',
  date_to: '',
})

const actionForm = reactive({
  outgoing_reg_no: '',
  forward_date: '',
})

const dispatchForm = reactive({
  client_id: '',
  dispatch_date: '',
  remark: '',
})

const dateRange = computed({
  get: () => {
    if (filters.date_from && filters.date_to) {
      return [filters.date_from, filters.date_to]
    }
    return []
  },
  set: (value: string[] | undefined) => {
    filters.date_from = value?.[0] || ''
    filters.date_to = value?.[1] || ''
  },
})

async function fetchReferenceData() {
  const [clientResult, templateResult] = await Promise.all([
    getClients({ page: 1, page_size: 200 }),
    getDocTemplates({ enabled: true, page_size: 100 }),
  ])
  clients.value = clientResult.items
  templates.value = templateResult.items.filter((item) => item.direction === 'OUT')
}

async function fetchCandidates() {
  loading.value = true
  error.value = null
  try {
    const response = await getDocumentDispatchMailingCandidates({
      ...filters,
      page: page.value,
      page_size: pageSize.value,
    })
    documents.value = response.items
    total.value = response.total
    selectedIds.value = []
    dispatchDetail.value = null
    currentDispatchId.value = ''
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.q = ''
  filters.client_id = ''
  filters.doc_template_id = ''
  filters.date_from = ''
  filters.date_to = ''
  dispatchForm.client_id = ''
  page.value = 1
  fetchCandidates()
}

function handleSelectionChange(rows: Document[]) {
  selectedIds.value = rows.map((row) => row.id)
}

async function handleSubmit() {
  if (!selectedIds.value.length) {
    ElMessage.error('请先勾选至少一份去文。')
    return
  }
  if (!actionForm.outgoing_reg_no.trim()) {
    ElMessage.error('请输入寄出编号。')
    return
  }

  submitting.value = true
  error.value = null
  try {
    const result = await batchRegisterDocumentMailing({
      selected_document_ids: selectedIds.value,
      outgoing_reg_no: actionForm.outgoing_reg_no.trim(),
      forward_date: actionForm.forward_date || null,
    })
    ElMessage.success(`登记完成：成功更新 ${result.success_count} 份去文。`)
    await fetchCandidates()
  } catch (err) {
    error.value = err as ApiError
  } finally {
    submitting.value = false
  }
}

async function handleCreateDispatch() {
  if (!selectedIds.value.length) {
    ElMessage.error('请先勾选至少一份去文。')
    return
  }
  if (!dispatchForm.client_id) {
    ElMessage.error('请先选择交接单客户。')
    return
  }
  if (!dispatchForm.dispatch_date) {
    ElMessage.error('请选择交接日期。')
    return
  }

  creatingDispatch.value = true
  error.value = null
  try {
    const created = await createDocumentDispatch({
      client_id: dispatchForm.client_id,
      dispatch_date: dispatchForm.dispatch_date,
      selected_document_ids: selectedIds.value,
      remark: dispatchForm.remark.trim() || null,
    })
    currentDispatchId.value = created.id
    dispatchDetail.value = await getDocumentDispatch(created.id)
    ElMessage.success(`交接单已生成，共 ${dispatchDetail.value.lines.length} 条明细。`)
  } catch (err) {
    error.value = err as ApiError
  } finally {
    creatingDispatch.value = false
  }
}

async function handleReloadDispatch() {
  if (!currentDispatchId.value) {
    return
  }
  creatingDispatch.value = true
  error.value = null
  try {
    dispatchDetail.value = await getDocumentDispatch(currentDispatchId.value)
    ElMessage.success('交接单详情已刷新。')
  } catch (err) {
    error.value = err as ApiError
  } finally {
    creatingDispatch.value = false
  }
}

onMounted(async () => {
  await fetchReferenceData()
  if (filters.client_id) {
    dispatchForm.client_id = filters.client_id
  }
  await fetchCandidates()
})
</script>

<style scoped>
.filter-panel,
.action-panel {
  margin-bottom: 16px;
}

.filter-actions {
  display: flex;
  align-items: end;
}

.full-width {
  width: 100%;
}

.action-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.selection-summary {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.dispatch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dispatch-meta,
.dispatch-detail-meta {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.dispatch-detail-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
</style>
