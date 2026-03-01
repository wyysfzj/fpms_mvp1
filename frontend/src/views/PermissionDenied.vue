<template>
  <div class="error-page">
    <div class="error-card">
      <div class="error-icon">🚫</div>
      <h1 class="error-title">无权限访问</h1>
      <p class="error-message">
        您没有访问该资源的权限。
      </p>
      <div v-if="requiredPerm" class="error-detail">
        <span class="detail-label">所需权限：</span>
        <code class="detail-value">{{ requiredPerm }}</code>
      </div>
      <div v-if="requestId" class="error-detail">
        <span class="detail-label">请求 ID：</span>
        <code class="detail-value">{{ requestId }}</code>
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goToDashboard">
          返回工作台
        </el-button>
        <el-button @click="handleLogout">
          退出登录
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const requiredPerm = computed(() => route.query.perm as string | undefined)
const requestId = computed(() => route.query.rid as string | undefined)

function goToDashboard() {
  router.push('/dashboard')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
