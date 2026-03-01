<template>
  <div class="case-panel">
    <div class="panel-toolbar">
      <h3 class="panel-heading">公文记录</h3>
      <el-button type="primary" size="small" @click="handleCreate">登记公文</el-button>
    </div>
    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="items.length === 0" class="placeholder-content">
      <p>暂无公文记录</p>
    </div>
    <el-table v-else :data="items" stripe style="width: 100%">
      <el-table-column label="方向" width="90">
        <template #default="{ row }">
          <el-tag :type="row.direction === 'IN' ? 'success' : 'warning'" size="small">
            {{ row.direction === 'IN' ? '收文' : '发文' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="doc_date" label="公文日期" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="160" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDocuments } from '../../../api/documents'
import type { Document } from '../../../api/documents.types'

const props = defineProps<{
  caseId: string
}>()

const router = useRouter()
const items = ref<Document[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getDocuments({ case_id: props.caseId, page: 1, page_size: 50 })
    items.value = res.items
  } catch {
    // silently fail
  } finally {
    loading.value = false
  }
})

function handleCreate() {
  router.push(`/documents/new?case_id=${props.caseId}`)
}
</script>
