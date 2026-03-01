<template>
  <div class="kpi-card">
    <span class="kpi-label">{{ label }}</span>
    <span class="kpi-value">{{ formattedValue }}</span>
    <span v-if="sub" class="kpi-sub">{{ sub }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number | string
  sub?: string
}>()

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString('zh-CN')
  }
  return props.value
})
</script>
