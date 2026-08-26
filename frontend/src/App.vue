<template>
  <router-view />
  <DemoBoundaryBanner v-if="showDemoBoundary" />
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import DemoBoundaryBanner from './components/demo/DemoBoundaryBanner.vue'
import { readDemoPreflight } from './modules/demo/demo.api'
import {
  DEMO_UI_SESSION_CHANGE_EVENT,
  hasStoredDemoUiSession,
  isDemoUiSessionActive,
  prepareDemoUiSessionObserver,
  restoreDemoUiSession,
  stopDemoUiSession,
} from './modules/demo/demoUiSession'

const route = useRoute()
const demoSessionActive = ref(isDemoUiSessionActive())
const showDemoBoundary = computed(() => demoSessionActive.value && route.path !== '/login')

function syncDemoSession(): void {
  demoSessionActive.value = isDemoUiSessionActive()
}

onMounted(async () => {
  window.addEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
  if (!prepareDemoUiSessionObserver()) return
  if (!hasStoredDemoUiSession()) {
    const navigation = performance.getEntriesByType('navigation')[0] as
      | PerformanceNavigationTiming
      | undefined
    if (navigation?.type === 'reload') stopDemoUiSession('SESSION_TUPLE_MISSING')
    return
  }
  try {
    restoreDemoUiSession(await readDemoPreflight())
  } catch {
    stopDemoUiSession('PREFLIGHT_FAILED')
  }
})

onBeforeUnmount(() => {
  window.removeEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
})
</script>
