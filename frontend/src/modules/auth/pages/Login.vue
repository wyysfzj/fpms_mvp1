<template>
  <div style="max-width: 360px; margin: 80px auto;">
    <h2>{{ ZH.login.title }}</h2>
    <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" style="margin-bottom: 16px;">
      <template v-if="errorRequestId">
        <small>请求 ID：{{ errorRequestId }}</small>
      </template>
    </el-alert>
    <el-form :model="form" @submit.prevent="onLogin">
      <el-form-item :label="ZH.login.username">
        <el-input v-model="form.username" :disabled="loading" />
      </el-form-item>
      <el-form-item :label="ZH.login.password">
        <el-input v-model="form.password" type="password" :disabled="loading" />
      </el-form-item>
      <el-button type="primary" :loading="loading" @click="onLogin">{{ ZH.login.submit }}</el-button>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../../stores/auth'
import type { ApiError } from '../../../api/types'
import { ZH } from '../../../constants/labels.zh'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({ username: '', password: '' })
const loading = ref(false)
const errorMessage = ref<string | null>(null)
const errorRequestId = ref<string | null>(null)

async function onLogin() {
  loading.value = true
  errorMessage.value = null
  errorRequestId.value = null

  try {
    await authStore.login(form.username, form.password)
    const redirect = route.query.redirect as string | undefined
    await router.push(redirect || '/dashboard')
  } catch (err) {
    const apiError = err as ApiError
    errorMessage.value = apiError.message || ZH.login.error
    errorRequestId.value = apiError.requestId || null
  } finally {
    loading.value = false
  }
}
</script>
