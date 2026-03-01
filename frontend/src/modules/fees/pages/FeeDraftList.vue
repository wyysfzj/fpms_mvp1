<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">{{ ZH.feeList.title }}</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/fees/drafts/new">
          <el-button type="primary">{{ ZH.feeList.newDraft }}</el-button>
        </router-link>
      </div>
    </div>

    <!-- Filter Bar -->
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-select v-model="filterStatus" placeholder="全部" clearable @change="onFilterChange">
          <el-option label="全部" value="" />
          <el-option label="开放" value="OPEN" />
          <el-option label="已锁定" value="LOCKED" />
        </el-select>
      </el-col>
    </el-row>

    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <LoadingBlock v-if="loading" :rows="8" />

    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        :title="ZH.feeList.emptyTitle"
        :message="ZH.feeList.emptyMsg"
        icon="📝"
        :cta-label="ZH.feeList.newDraft"
        cta-to="/fees/drafts/new"
      />
    </div>

    <div v-else class="page-table">
      <el-table
        :data="drafts"
        stripe
        size="small"
        class="compact-table"
        @row-click="handleRowClick"
      >
        <el-table-column prop="id" :label="ZH.feeList.draftId" min-width="250">
          <template #default="{ row }">
            <span class="id-value">{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.case_" min-width="220">
          <template #default="{ row }">
            <router-link
              class="entity-link"
              :to="`/cases/${row.case_id}`"
              @click.stop
            >
              {{ row.case_id }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.client" min-width="220">
          <template #default="{ row }">
            <router-link
              v-if="row.client_id"
              class="entity-link"
              :to="`/clients/${row.client_id}/edit`"
              @click.stop
            >
              {{ row.client_id }}
            </router-link>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="currency" :label="ZH.feeList.currency" width="120" />
        <el-table-column :label="ZH.feeList.status" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ getFeeDraftStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.amount" width="160">
          <template #default="{ row }">
            <span class="amount">{{ formatAmount(row.amount, row.currency) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="ZH.feeList.actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button text size="small" @click.stop="goToDetail(row.id)">{{ ZH.feeList.view }}</el-button>
          </template>
        </el-table-column>
      </el-table>

      <PaginationBar v-model:page="page" v-model:page-size="pageSize" :total="total" :page-sizes="[20, 50, 100]" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getFeeDrafts } from '../../../api/fees'
import type { FeeDraftListItem, FeeDraftStatus, FeeMoney } from '../../../api/fees.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'
import { ZH } from '../../../constants/labels.zh'
import { getFeeDraftStatusText } from '../../../constants/displayText'

const router = useRouter()

const drafts = ref<FeeDraftListItem[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref<'' | FeeDraftStatus>('')
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

function onFilterChange() {
  page.value = 1
  fetchDrafts()
}

async function fetchDrafts() {
  loading.value = true
  error.value = null
  try {
    const result = await getFeeDrafts({ page: page.value, page_size: pageSize.value, status: filterStatus.value || undefined })
    drafts.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function statusTagType(status: FeeDraftStatus): 'info' | 'warning' {
  return status === 'LOCKED' ? 'warning' : 'info'
}

function formatAmount(amount: FeeMoney, currency?: string): string {
  const curr = currency || 'CNY'
  const numericAmount = typeof amount === 'number' ? amount : Number(amount)
  if (Number.isNaN(numericAmount)) {
    return `${curr} ${amount}`
  }

  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: curr,
  }).format(numericAmount)
}

function goToDetail(draftId: string) {
  router.push(`/fees/drafts/${draftId}`)
}

function handleRowClick(row: FeeDraftListItem) {
  router.push(`/fees/drafts/${row.id}`)
}

watch([page, pageSize], () => {
  fetchDrafts()
})

onMounted(() => {
  fetchDrafts()
})
</script>

<style scoped>
.text-muted {
  color: var(--text-sub);
}

.id-value {
  font-family: var(--font-mono);
  font-size: 12px;
}

.entity-link {
  color: var(--color-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  text-decoration: none;
}

.entity-link:hover {
  text-decoration: underline;
}

.amount {
  font-family: var(--font-mono);
  font-weight: 500;
}
</style>
