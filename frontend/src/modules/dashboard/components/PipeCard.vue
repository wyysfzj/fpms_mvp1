<template>
  <div
    class="pipe-card"
    role="button"
    tabindex="0"
    :aria-label="label + ' ' + formattedValue"
    @click="$emit('click')"
    @keydown.enter="$emit('click')"
  >
    <div class="pipe-bar" :style="{ background: barColor }"></div>
    <div class="pipe-header">
      <span>{{ label }}</span>
      <span v-if="badge" :class="['badge', badge.class]">{{ badge.text }}</span>
    </div>
    <div class="pipe-num">{{ formattedValue }}</div>
    <div v-if="hint" class="pipe-hint">{{ hint }}</div>
    <div v-else class="pipe-label">{{ sublabel }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  barColor: string
  value: string | number
  label: string
  sublabel?: string
  hint?: string
  badge?: { text: string; class: string }
}>()

defineEmits<{
  click: []
}>()

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString('zh-CN')
  }
  return props.value
})
</script>
