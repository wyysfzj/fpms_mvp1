<template>
  <div v-if="hasAnyLink" class="relation-chain-card">
    <span class="chain-label">关系链</span>
    <div class="chain-items">
      <template v-for="(item, idx) in chainItems" :key="item.type">
        <span v-if="idx > 0" class="chain-arrow">&rarr;</span>
        <router-link v-if="item.id" :to="item.route" class="chain-link">
          {{ item.icon }} {{ item.display }}
        </router-link>
        <span v-else class="chain-muted">
          {{ item.icon }} 未关联
        </span>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface EntityRef {
  id: string
  name?: string
  no?: string
  title?: string
  refNo?: string
  label?: string
}

const props = defineProps<{
  client?: EntityRef
  caseRef?: EntityRef
  document?: EntityRef
  feeDraft?: EntityRef
  bill?: EntityRef
}>()

interface ChainItem {
  type: string
  icon: string
  id: string | undefined
  route: string
  display: string
}

const chainItems = computed<ChainItem[]>(() => {
  const items: ChainItem[] = []

  if (props.client !== undefined) {
    items.push({
      type: 'client',
      icon: '👥',
      id: props.client?.id,
      route: props.client?.id ? `/clients/${props.client.id}/edit` : '',
      display: props.client?.name || truncateId(props.client?.id),
    })
  }

  if (props.caseRef !== undefined) {
    items.push({
      type: 'case',
      icon: '📂',
      id: props.caseRef?.id,
      route: props.caseRef?.id ? `/cases/${props.caseRef.id}` : '',
      display: props.caseRef?.no || props.caseRef?.title || truncateId(props.caseRef?.id),
    })
  }

  if (props.document !== undefined) {
    items.push({
      type: 'document',
      icon: '📄',
      id: props.document?.id,
      route: props.document?.id ? `/documents/${props.document.id}` : '',
      display: props.document?.refNo || truncateId(props.document?.id),
    })
  }

  if (props.feeDraft !== undefined) {
    items.push({
      type: 'feeDraft',
      icon: '💰',
      id: props.feeDraft?.id,
      route: props.feeDraft?.id ? `/fees/drafts/${props.feeDraft.id}` : '',
      display: props.feeDraft?.label || truncateId(props.feeDraft?.id),
    })
  }

  if (props.bill !== undefined) {
    items.push({
      type: 'bill',
      icon: '🧾',
      id: props.bill?.id,
      route: props.bill?.id ? `/billing/bills/${props.bill.id}` : '',
      display: props.bill?.no || truncateId(props.bill?.id),
    })
  }

  return items
})

const hasAnyLink = computed(() => chainItems.value.some(item => item.id))

function truncateId(id?: string): string {
  if (!id) return '未关联'
  return id.length > 8 ? id.slice(0, 8) + '...' : id
}
</script>
