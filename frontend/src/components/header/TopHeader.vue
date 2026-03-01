<template>
  <header class="top-header">
    <div class="header-left">
      <div class="header-breadcrumb">
        <template v-if="contextBreadcrumb.length > 0">
          <template v-for="(crumb, i) in contextBreadcrumb" :key="i">
            <span v-if="i > 0" class="breadcrumb-sep"> / </span>
            <span :class="{ current: i === contextBreadcrumb.length - 1 }">{{ crumb }}</span>
          </template>
        </template>
        <template v-else>
          <span>{{ breadcrumb }}</span>
          <span v-if="currentPage" class="current"> / {{ currentPage }}</span>
        </template>
      </div>
    </div>
    <div class="header-right">
      <input type="text" class="search-bar" :placeholder="ZH.header.searchPlaceholder" />
      <el-dropdown @command="handleCommand">
        <div class="user-avatar">
          <span style="font-size: 12px; color: #64748B;">用户</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout">{{ ZH.header.logout }}</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { usePageContext } from '../../stores/pageContext'
import { ZH } from '../../constants/labels.zh'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const pageContext = usePageContext()

const contextBreadcrumb = computed(() => pageContext.breadcrumb)

const breadcrumb = computed(() => {
  const name = route.name as string
  if (!name) return ZH.route.dashboard
  const zhTitle = ZH.route[name as keyof typeof ZH.route]
  if (zhTitle) return zhTitle
  return '页面'
})

const currentPage = computed(() => {
  if (route.params.id) {
    return route.params.id as string
  }
  return null
})

function handleCommand(command: string) {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.breadcrumb-sep {
  color: var(--text-sub, #94A3B8);
  margin: 0 2px;
}
</style>
