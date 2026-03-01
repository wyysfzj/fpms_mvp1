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
        <el-select v-model="filterDirection" placeholder="全部" clearable @change="onFilterChange">
          <el-option label="全部" value="" />
          <el-option label="收文" value="IN" />
          <el-option label="发文" value="OUT" />
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
        <el-table-column prop="doc_type" :label="ZH.docList.type" width="120">
          <template #default="{ row }">
            {{ row.doc_type || '-' }}
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
import { getDocuments } from '../../../api/documents'
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import type { Document } from '../../../api/documents.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { getDocumentDirectionText } from '../../../constants/displayText'

const documents = ref<Document[]>([])
const router = useRouter()
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterDirection = ref<'' | 'IN' | 'OUT'>('')
const filterClientId = ref('')
const clientOptions = ref<Client[]>([])
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function onFilterChange() {
  page.value = 1
  fetchDocuments()
}

async function fetchDocuments() {
  loading.value = true
  error.value = null
  try {
    const result = await getDocuments({ page: page.value, page_size: pageSize.value, direction: filterDirection.value || undefined, client_id: filterClientId.value || undefined })
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

onMounted(() => {
  fetchDocuments()
  loadClients()
})
</script>

<style scoped>
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
