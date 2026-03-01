<template>
  <div :class="['list-item', { 'finance-highlight': item.highlight }]">
    <div class="finance-row">
      <div class="finance-left">
        <div class="finance-label">{{ item.label }}</div>
        <div v-if="item.date" class="finance-date">{{ item.date }}</div>
      </div>
      <div class="finance-right">
        <span class="money-text">{{ formattedAmount }}</span>
        <span :class="['badge', item.badge_class]">{{ item.badge_text }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface FinanceItem {
  type: 'payment' | 'overdue_bill' | 'pending_bill'
  id: string
  label: string
  amount: number
  currency: string
  badge_text: string
  badge_class: string
  date?: string
  highlight: boolean
}

const props = defineProps<{
  item: FinanceItem
}>()

const formattedAmount = computed(() => {
  const prefix = props.item.currency === 'CNY' ? '¥' : props.item.currency + ' '
  return prefix + props.item.amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
})
</script>
