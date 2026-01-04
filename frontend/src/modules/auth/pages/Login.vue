<template>
  <div style="max-width: 360px; margin: 80px auto;">
    <h2>Login</h2>
    <el-form :model="form" @submit.prevent>
      <el-form-item label="Username">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="Password">
        <el-input v-model="form.password" type="password" />
      </el-form-item>
      <el-button type="primary" @click="onLogin">Login</el-button>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { http } from '../../../api/http'

const router = useRouter()
const form = reactive({ username: '', password: '' })

async function onLogin() {
  const { data } = await http.post('/auth/login', form)
  localStorage.setItem('fpms_token', data.access_token)
  await router.push('/dashboard')
}
</script>
