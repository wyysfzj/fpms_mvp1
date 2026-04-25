<template>
  <div class="case-panel">
    <div class="panel-toolbar">
      <h3 class="panel-heading">费用记录</h3>
      <el-button type="primary" size="small" @click="handleCreate">创建费用草稿</el-button>
    </div>
    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="items.length === 0" class="placeholder-content">
      <p>暂无费用记录</p>
    </div>
    <el-table v-else :data="items" stripe style="width: 100%">
      <el-table-column label="草稿类型" width="120">
        <template #default="{ row }">
          {{ getFeeDraftTypeText(row.draft_type) }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'LOCKED' ? 'danger' : 'success'" size="small">
            {{ getFeeDraftStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="currency" label="币种" width="80" />
      <el-table-column label="总金额" width="140">
        <template #default="{ row }">
          {{ row.amount }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFeeDrafts } from '../../../api/fees'
import type { FeeDraftListItem } from '../../../api/fees.types'
import { getFeeDraftStatusText, getFeeDraftTypeText } from '../../../constants/displayText'

const props = defineProps<{
  caseId: string
}>()

const router = useRouter()
const items = ref<FeeDraftListItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getFeeDrafts({ case_id: props.caseId, page: 1, page_size: 50 })
    items.value = res.items
  } catch {
    // silently fail
  } finally {
    loading.value = false
  }
})

function handleCreate() {
  router.push(`/fees/drafts/new?case_id=${props.caseId}&draft_type=APPLY_FEE`)
}
</script>
