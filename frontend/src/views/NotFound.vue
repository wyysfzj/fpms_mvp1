<template>
  <div class="error-page">
    <div class="error-card">
      <div class="error-icon">🔍</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-message">
        您访问的页面不存在或已被移动。
      </p>
      <div class="error-actions">
        <el-button type="primary" @click="goToDashboard">
          返回工作台
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goToDashboard() {
  router.push('/dashboard')
}
</script>
