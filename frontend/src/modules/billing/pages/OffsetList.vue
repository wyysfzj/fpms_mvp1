<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h2>冲销管理</h2>
      </div>
      <div class="page-header-right">
        <el-button @click="fetchData" :loading="loading">刷新</el-button>
      </div>
    </div>

    <el-alert
      class="page-notice"
      title="核销记录与客户回款是不同业务对象"
      type="info"
      :closable="false"
      description="回款记录资金到账；核销记录将回款分配到账单，两者分别保留可追溯事实。"
    />

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <el-alert :title="String(error)" type="error" show-icon closable @close="error = null" />
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar" style="margin-bottom: 16px; display: flex; gap: 12px; align-items: center;">
      <el-select v-model="filterReversed" placeholder="反转状态" clearable style="width: 140px;" @change="handleFilter">
        <el-option label="全部" value="" />
        <el-option label="正常" :value="false" />
        <el-option label="已反转" :value="true" />
      </el-select>
      <el-input
        v-model.trim="filterBillId"
        placeholder="请输入账单编号"
        clearable
        style="width: 220px;"
        @keyup.enter="handleFilter"
        @clear="handleFilter"
      />
      <el-button type="primary" @click="handleFilter">查询</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="items"
      stripe
      size="small"
      class="compact-table"
    >
      <el-table-column label="冲销金额" width="140" align="right">
        <template #default="{ row }">
          <span class="mono-num">{{ formatAmount(row.amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="冲销日期" width="130">
        <template #default="{ row }">
          {{ row.offset_date || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="账单号" width="160">
        <template #default="{ row }">
          <el-link type="primary" @click="goToBill(row.bill_id)">
            {{ getBillDisplay(row.bill_no, row.bill_id) }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.is_reversed" type="danger" size="small">已反转</el-tag>
          <el-tag v-else type="success" size="small">正常</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="反转时间" width="160">
        <template #default="{ row }">
          {{ row.reversed_at || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button
            v-if="!row.is_reversed"
            type="danger"
            size="small"
            text
            @click="handleReverse(row)"
          >
            反转
          </el-button>
          <span v-else class="text-muted">—</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOffsets, reverseOffset } from '../../../api/billing'
import type { OffsetListItem } from '../../../api/billing.types'

const router = useRouter()
const route = useRoute()

const items = ref<OffsetListItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterReversed = ref<boolean | string>('')
const filterBillId = ref((route.query.bill_id as string) || '')

function formatAmount(val: number): string {
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function fetchData() {
  loading.value = true
  error.value = null
  try {
    const params: Record<string, unknown> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filterReversed.value !== '' && filterReversed.value !== null) {
      params.is_reversed = filterReversed.value
    }
    if (filterBillId.value) {
      params.bill_id = filterBillId.value
    }
    const result = await getOffsets(params as Parameters<typeof getOffsets>[0])
    items.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = String(err)
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  page.value = 1
  fetchData()
}

function handleReset() {
  filterReversed.value = ''
  filterBillId.value = ''
  page.value = 1
  fetchData()
}

async function handleReverse(row: OffsetListItem) {
  const billLabel = getBillDisplay(row.bill_no, row.bill_id)
  const amountLabel = formatAmount(row.amount)

  try {
    await ElMessageBox.confirm(
      `冲销金额：¥${amountLabel}\n关联账单：${billLabel}\n\n反转后，账单余额将恢复，付款行可用金额将增加。此操作不可撤销。`,
      '确认反转冲销',
      {
        confirmButtonText: '确认反转',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
    await reverseOffset(row.id)
    ElMessage.success('冲销已反转')
    await fetchData()
  } catch {
    // User cancelled — silently ignore
  }
}

function goToBill(billId: string) {
  router.push({ name: 'bill_detail', params: { id: billId } })
}

function getBillDisplay(billNo?: string, billId?: string): string {
  if (billNo) return billNo
  return billId ? '未生成账单号' : '未关联账单'
}

onMounted(fetchData)
</script>
