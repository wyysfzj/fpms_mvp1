<template>
  <div class="app-shell">
    <SidebarNav />
    <div class="main-container">
      <TopHeader />
      <main class="content-scroll">
        <router-view />
      </main>
    </div>
    <ModeToggle v-if="showModeToggle" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import SidebarNav from '../components/nav/SidebarNav.vue'
import TopHeader from '../components/header/TopHeader.vue'
import ModeToggle from '../components/layout/ModeToggle.vue'

const route = useRoute()

// Show mode toggle only on routes that support focus mode
const showModeToggle = computed(() => {
  return route.matched.some(record => record.meta.supportsFocusMode === true)
})
</script>
