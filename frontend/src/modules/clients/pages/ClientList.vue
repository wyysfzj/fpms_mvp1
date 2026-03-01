<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">客户列表</h1>
        <span class="page-count">{{ total }} 条</span>
      </div>
      <div class="page-header-right">
        <router-link to="/clients/new">
          <el-button type="primary">新建客户</el-button>
        </router-link>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading State -->
    <LoadingBlock v-if="loading" :rows="10" />

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="page-empty">
      <EmptyState
        title="暂无客户"
        message="创建首个客户后可在此查看。"
        icon="📋"
        cta-label="新建客户"
        cta-to="/clients/new"
      />
    </div>

    <!-- Table -->
    <div v-else class="page-table">
      <el-table
        :data="clients"
        stripe
        size="small"
        class="compact-table"
      >
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="contact_person" label="联系人" min-width="140" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click">
              <el-button
                text
                size="small"
                class="row-actions-trigger"
                :aria-label="`打开客户操作：${row.name || row.id}`"
              >
                <span>操作</span>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleView(row)">查看</el-dropdown-item>
                  <el-dropdown-item @click="handleEdit(row)">编辑</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
import { getClients } from '../../../api/clients'
import type { Client } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import EmptyState from '../../../components/state/EmptyState.vue'
import LoadingBlock from '../../../components/state/LoadingBlock.vue'
import PaginationBar from '../../../components/state/PaginationBar.vue'

const router = useRouter()

const clients = ref<Client[]>([])
const loading = ref(false)
const error = ref<ApiError | null>(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const isEmpty = computed(() => !loading.value && !error.value && total.value === 0)

async function fetchClients() {
  loading.value = true
  error.value = null
  try {
    const result = await getClients({ page: page.value, page_size: pageSize.value })
    clients.value = result.items
    total.value = result.total
  } catch (err) {
    error.value = err as ApiError
  } finally {
    loading.value = false
  }
}

function handleView(row: Client) {
  router.push(`/clients/${row.id}/edit`)
}

function handleEdit(row: Client) {
  router.push(`/clients/${row.id}/edit`)
}

// Watch for pagination changes
watch([page, pageSize], () => {
  fetchClients()
})

onMounted(() => {
  fetchClients()
})
</script>
