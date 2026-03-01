<template>
  <div class="state-loading-block" :class="{ 'state-loading-block--panel': panel }" role="status" aria-live="polite" aria-busy="true">
    <el-skeleton :rows="rows" animated />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  rows?: number
  panel?: boolean
}>(), {
  rows: 8,
  panel: false,
})
</script>
