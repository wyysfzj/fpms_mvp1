<template>
  <div class="error-banner" :class="bannerClass">
    <div class="error-banner-content">
      <span class="error-banner-icon">{{ icon }}</span>
      <div class="error-banner-text">
        <p class="error-banner-message">{{ message }}</p>
        <p v-if="requiredPerm" class="error-banner-detail">
          所需权限：<code>{{ requiredPerm }}</code>
        </p>
        <p v-if="requestId" class="error-banner-detail">
          请求 ID：<code>{{ requestId }}</code>
        </p>
      </div>
    </div>
    <el-button v-if="dismissable" text @click="emit('dismiss')">
      ✕
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ApiError } from '../../api/types'

const props = withDefaults(defineProps<{
  error: ApiError
  dismissable?: boolean
}>(), {
  dismissable: true,
})

const emit = defineEmits<{
  dismiss: []
}>()

const message = computed(() => props.error.message)
const requestId = computed(() => props.error.requestId)
const requiredPerm = computed(() => {
  const details = props.error.details
  if (details && typeof details.required_perm === 'string') {
    return details.required_perm
  }
  if (details && typeof details.requiredPerm === 'string') {
    return details.requiredPerm
  }
  return null
})

const bannerClass = computed(() => {
  const status = props.error.status
  if (status === 403) return 'error-banner--forbidden'
  if (status === 409) return 'error-banner--conflict'
  if (status === 422) return 'error-banner--validation'
  return 'error-banner--error'
})

const icon = computed(() => {
  const status = props.error.status
  if (status === 403) return '🚫'
  if (status === 409) return '⚠️'
  if (status === 422) return '📝'
  return '❌'
})
</script>
