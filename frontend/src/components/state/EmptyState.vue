<template>
  <div class="state-empty" role="status" aria-live="polite">
    <p v-if="icon" class="state-empty-icon" aria-hidden="true">{{ icon }}</p>
    <h3 class="state-empty-title">{{ title }}</h3>
    <p class="state-empty-message">{{ message }}</p>
    <div v-if="hasActions" class="state-empty-actions">
      <slot name="actions">
        <router-link v-if="ctaTo && ctaLabel" :to="ctaTo">
          <el-button type="primary">{{ ctaLabel }}</el-button>
        </router-link>
        <el-button v-else-if="ctaLabel" type="primary" @click="emit('cta')">{{ ctaLabel }}</el-button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useSlots } from 'vue'

const props = withDefaults(defineProps<{
  title: string
  message: string
  icon?: string
  ctaLabel?: string
  ctaTo?: string
}>(), {
  icon: '📭',
})

const emit = defineEmits<{
  cta: []
}>()

const slots = useSlots()
const hasActions = computed(() => Boolean(slots.actions || props.ctaLabel))
</script>
