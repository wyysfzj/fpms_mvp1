<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">{{ ZH.docList.title }}</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/documents/new">
          <el-button type="primary">{{ ZH.docList.newDoc }}</el-button>
        </router-link>
      </div>
    </div>

    <!-- Filter Bar -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-input
          v-model="filterDocName"
          placeholder="按文件名称搜索"
          clearable
          @keyup.enter="onFilterChange"
          @clear="onFilterChange"
        />
      </el-col>
      <el-col :span="6">
        <el-select v-model="filterDirection" placeholder="全部" clearable @change="onFilterChange">
          <el-option label="全部" value="" />
          <el-option label="收文" value="IN" />
          <el-option label="发文" value="OUT" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-input
          v-model="filterCaseNo"
          placeholder="按案件号搜索"
          clearable
          @keyup.enter="onFilterChange"
          @clear="onFilterChange"
        />
      </el-col>
      <el-col :span="6">
        <el-select
          v-model="filterTemplateCode"
          placeholder="全部模板代码"
          clearable
          filterable
          @change="onFilterChange"
        >
          <el-option
            v-for="t in templateOptions"
            :key="t.id"
            :label="`${t.code} — ${t.name}`"
            :value="t.code"
          />
        </el-select>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-select
          v-model="filterDocTypes"
          placeholder="全部文件类型"
          clearable
          multiple
          collapse-tags
          collapse-tags-tooltip
          @change="onFilterChange"
        >
          <el-option
            v-for="option in docTypeOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-date-picker
          v-model="filterDateRange"
          type="daterange"
          start-placeholder="起始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="full-width"
          clearable
          @change="onFilterChange"
        />
      </el-col>
      <el-col :span="6">
        <el-select
          v-model="filterReplyState"
          placeholder="全部回复状态"
          clearable
          @change="onFilterChange"
        >
          <el-option label="全部回复状态" value="" />
          <el-option label="需回复" value="PENDING" />
          <el-option label="已回复" value="DONE" />
          <el-option label="无需回复" value="NONE" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-select
          v-model="filterClientId"
          placeholder="全部客户"
          clearable
          filterable
          @change="onFilterChange"
        >
          <el-option
            v-for="c in clientOptions"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-button @click="resetFilters">重置筛选</el-button>
      </el-col>
    </el-row>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <LoadingBlock v-if="loading" :rows="10" />

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        :title="ZH.docList.emptyTitle"
        :message="ZH.docList.emptyMsg"
        icon="📄"
        :cta-label="ZH.docList.newDoc"
        cta-to="/documents/new"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="documents"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="id" :label="ZH.docList.id" width="70" />
        <el-table-column :label="ZH.docList.direction" width="100">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'IN' ? 'success' : 'warning'" size="small">
              {{ getDocumentDirectionText(row.direction) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" :label="ZH.docList.docTitle" min-width="200" />
        <el-table-column :label="ZH.docList.case_" width="120">
          <template #default="{ row }">
            <router-link v-if="row.case_id" :to="`/cases/${row.case_id}`" class="doc-case-link">
              {{ row.case_no || `#${row.case_id}` }}
            </router-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="模板代码" width="140">
          <template #default="{ row }">
            {{ row.template_code || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="文件类型" width="120">
          <template #default="{ row }">
            {{ getDocumentDocTypeText(row.doc_type) }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.docList.date" width="120">
          <template #default="{ row }">
            <span class="doc-date">{{ formatDate(row.doc_date) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="回复状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.need_reply && !row.reply_date" type="warning" size="small">
              待回复
            </el-tag>
            <el-tag v-else-if="row.need_reply && row.reply_date" type="success" size="small">
              已回复
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.docList.created" width="140">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column :label="ZH.docList.actions" width="90" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click="handleView(row)">
              {{ ZH.docList.view }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { getDocuments, getDocTemplates } from '../../../api/documents'
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import type { DocTemplate, Document } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { getDocumentDirectionText, getDocumentDocTypeText } from '../../../constants/displayText'

const documents = ref<Document[]>([])
const router = useRouter()
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterDocName = ref('')
const filterCaseNo = ref('')
const filterDirection = ref<'' | 'IN' | 'OUT'>('')
const filterClientId = ref('')
const filterTemplateCode = ref('')
const filterDocTypes = ref<Array<'OFFICIAL_IN' | 'OFFICIAL_OUT' | 'CLIENT_IN' | 'CLIENT_OUT'>>([])
const filterDateRange = ref<string[]>([])
const filterReplyState = ref<'' | 'PENDING' | 'DONE' | 'NONE'>('')
const clientOptions = ref<Client[]>([])
const templateOptions = ref<DocTemplate[]>([])
const docTypeOptions = [
  { label: '官方来文', value: 'OFFICIAL_IN' },
  { label: '官方去文', value: 'OFFICIAL_OUT' },
  { label: '客户来文', value: 'CLIENT_IN' },
  { label: '致函客户', value: 'CLIENT_OUT' },
] as const
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function onFilterChange() {
  page.value = 1
  fetchDocuments()
}

async function fetchDocuments() {
  loading.value = true
  error.value = null
  try {
    const [date_from, date_to] = filterDateRange.value
    const need_reply =
      filterReplyState.value === 'NONE' ? false : filterReplyState.value ? true : undefined
    const replied =
      filterReplyState.value === 'PENDING'
        ? false
        : filterReplyState.value === 'DONE'
          ? true
          : undefined
    const result = await getDocuments({
      page: page.value,
      page_size: pageSize.value,
      doc_name: filterDocName.value.trim() || undefined,
      doc_type: filterDocTypes.value.length ? [...filterDocTypes.value] : undefined,
      case_no: filterCaseNo.value.trim() || undefined,
      template_code: filterTemplateCode.value || undefined,
      direction: filterDirection.value || undefined,
      client_id: filterClientId.value || undefined,
      need_reply,
      replied,
      date_from: date_from || undefined,
      date_to: date_to || undefined,
    })
    documents.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

function handleView(row: Document) {
  router.push(`/documents/${row.id}`)
}

watch([page, pageSize], () => {
  fetchDocuments()
})

async function loadClients() {
  try {
    const result = await getClients({ page: 1, page_size: 9999 })
    clientOptions.value = result.items
  } catch {
    // silently ignore
  }
}

async function loadTemplates() {
  try {
    const result = await getDocTemplates({ enabled: true, page_size: 100 })
    templateOptions.value = result.items
  } catch {
    // silently ignore
  }
}

function resetFilters() {
  filterDocName.value = ''
  filterCaseNo.value = ''
  filterDirection.value = ''
  filterClientId.value = ''
  filterTemplateCode.value = ''
  filterDocTypes.value = []
  filterDateRange.value = []
  filterReplyState.value = ''
  onFilterChange()
}

onMounted(() => {
  fetchDocuments()
  loadClients()
  loadTemplates()
})
</script>

<style scoped>
.full-width {
  width: 100%;
}

.doc-case-link {
  color: var(--color-primary);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 12px;
}

.doc-case-link:hover {
  text-decoration: underline;
}

.doc-date {
  font-family: var(--font-mono);
  font-size: 12px;
}
</style>
