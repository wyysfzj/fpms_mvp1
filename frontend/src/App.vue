<template>
  <router-view />
  <DemoBoundaryBanner v-if="showDemoBoundary" />
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import DemoBoundaryBanner from './components/demo/DemoBoundaryBanner.vue'
import { installHttpDemoObserver } from './api/http'
import {
  DEMO_UI_SESSION_CHANGE_EVENT,
  handleDemoUiRoute,
  hasStoredDemoUiSession,
  installDemoUiDomObserver,
  isDemoUiSessionActive,
  prepareDemoUiSessionObserver,
  restoreDemoUiSession,
  stopDemoUiSession,
} from './modules/demo/demoUiSession'

const route = useRoute()
const demoSessionActive = ref(isDemoUiSessionActive())
const showDemoBoundary = computed(() => demoSessionActive.value && !['/login', '/demo/abc'].includes(route.path))
let disposeHttpObserver: () => void = () => undefined
let disposeDomObserver: () => void = () => undefined

function syncDemoSession(): void {
  demoSessionActive.value = isDemoUiSessionActive()
}

onMounted(async () => {
  window.addEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
  if (route.path === '/demo/abc') {
    await handleDemoUiRoute(route.path)
    syncDemoSession()
    return
  }
  if (route.path === '/login') return
  disposeHttpObserver = installHttpDemoObserver()
  disposeDomObserver = installDemoUiDomObserver()
  if (!prepareDemoUiSessionObserver()) return
  if (!hasStoredDemoUiSession()) {
    const navigation = performance.getEntriesByType('navigation')[0] as
      | PerformanceNavigationTiming
      | undefined
    if (navigation?.type === 'reload') stopDemoUiSession('SESSION_TUPLE_MISSING')
    return
  }
  try {
    await restoreDemoUiSession()
  } catch {
    stopDemoUiSession('SESSION_REVALIDATION_FAILED')
  }
})

watch(() => route.path, (path) => { void handleDemoUiRoute(path) })

onBeforeUnmount(() => {
  window.removeEventListener(DEMO_UI_SESSION_CHANGE_EVENT, syncDemoSession)
  disposeDomObserver()
  disposeHttpObserver()
})
</script>
