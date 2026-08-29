<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-left">
        <el-button text @click="goBack">
          <span class="back-icon">←</span> 返回
        </el-button>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="handleEdit">编辑</el-button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="page-error">
      <ApiErrorBanner :error="error" @dismiss="error = null" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="page-loading">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- Content -->
    <template v-else-if="client">
      <el-tabs v-model="activeTab">
        <!-- Tab 1: 基本信息 -->
        <el-tab-pane label="基本信息" name="info">
          <div class="info-hint">
            当前主档仅展示客户基础字段；联系人与地址请分别在“联系人”和“地址”页签中维护。
          </div>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">客户名称</span>
              <span class="info-value">{{ client.name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">客户代码</span>
              <span class="info-value">{{ client.client_code || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">客户类型</span>
              <span class="info-value">{{ client.client_type || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">默认币种</span>
              <span class="info-value">{{ client.default_currency || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">邮箱</span>
              <span class="info-value">{{ client.email || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">状态</span>
              <span class="info-value">
                <el-tag :type="client.is_active ? 'success' : 'info'" size="small">
                  {{ client.is_active ? '启用' : '停用' }}
                </el-tag>
              </span>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 2: 地址 -->
        <el-tab-pane label="地址" name="addresses">
          <AddressTable :client-id="clientId" />
        </el-tab-pane>

        <!-- Tab 3: 联系人 -->
        <el-tab-pane label="联系人" name="contacts">
          <ContactTable :client-id="clientId" />
        </el-tab-pane>

        <!-- Tab 4: 关联案件 -->
        <el-tab-pane label="关联案件" name="cases">
          <el-table
            v-loading="casesLoading"
            :data="relatedCases"
            stripe
            size="small"
            class="compact-table"
          >
            <el-table-column prop="case_no" label="案件编号" width="160" />
            <el-table-column label="案件名称" min-width="200">
              <template #default="{ row }">
                {{ row.title_cn || row.title_en || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.status || '-' }}</el-tag>
              </template>
            </el-table-column>
            <template #empty>
              <span>暂无关联案件</span>
            </template>
          </el-table>
          <div v-if="casesTotal > casesPageSize" style="margin-top: 12px; text-align: right;">
            <el-pagination
              v-model:current-page="casesPage"
              :page-size="casesPageSize"
              :total="casesTotal"
              layout="prev, pager, next"
              small
              @current-change="fetchCases"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- Empty State -->
    <div v-else-if="!loading && !error" class="page-empty">
      <div class="empty-state">
        <h3>未找到客户</h3>
        <p>该客户不存在或已被删除。</p>
        <el-button type="primary" @click="goBack">返回</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getClient } from '../../../api/clients'
import { http } from '../../../api/http'
import type { Client } from '../../../api/clients.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import { usePageContext } from '../../../stores/pageContext'
import AddressTable from '../components/AddressTable.vue'
import ContactTable from '../components/ContactTable.vue'

interface RelatedCase {
    id: string
    case_no: string
    title_cn: string | null
    title_en: string | null
    status: string
}

const route = useRoute()
const router = useRouter()
const pageContext = usePageContext()

const clientId = computed(() => String(route.params.id || ''))

const client = ref<Client | null>(null)
const loading = ref(false)
const error = ref<ApiError | null>(null)
const activeTab = ref('info')

// Related cases state
const relatedCases = ref<RelatedCase[]>([])
const casesLoading = ref(false)
const casesPage = ref(1)
const casesPageSize = 20
const casesTotal = ref(0)

async function fetchClient() {
    const id = clientId.value
    if (!id) return

    loading.value = true
    error.value = null
    try {
        client.value = await getClient(id)
        pageContext.setBreadcrumb(['客户管理', '客户详情', client.value.name || '未命名客户'])
    } catch (err) {
        error.value = err as ApiError
    } finally {
        loading.value = false
    }
}

async function fetchCases() {
    const id = clientId.value
    if (!id) return

    casesLoading.value = true
    try {
        const response = await http.get<{ items: RelatedCase[]; total: number }>('/cases', {
            params: { client_id: id, page: casesPage.value, page_size: casesPageSize }
        })
        relatedCases.value = response.data.items || []
        casesTotal.value = response.data.total || 0
    } catch {
        relatedCases.value = []
    } finally {
        casesLoading.value = false
    }
}

function goBack() {
    router.push('/clients')
}

function handleEdit() {
    router.push(`/clients/${clientId.value}/edit`)
}

onMounted(() => {
    fetchClient()
    fetchCases()
})

onUnmounted(() => {
    pageContext.clear()
})
</script>

<style scoped>
.info-hint {
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: 8px;
  background: var(--bg-subtle, #f8fafc);
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.6;
}
</style>
