<template>
  <div class="demo-boundary-banner" role="status" data-testid="demo-v6-boundary-banner">
    <span>合成演示数据｜仅用于技术展示，非客户、生产或官方事实</span>
    <button
      v-if="nextStage"
      type="button"
      data-testid="demo-v6-capture-stage"
      :disabled="capturing"
      @click="captureStage"
    >
      {{ capturing ? '正在记录阶段截图…' : `记录阶段 ${String(nextStage).padStart(2, '0')} 截图` }}
    </button>
    <span v-else>11 个阶段截图已齐全</span>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { captureDemoStageScreenshot, getNextDemoScreenshotStage } from '../../modules/demo/demoUiSession'

const nextStage = ref<number | null>(null)
const capturing = ref(false)

async function refreshStage(): Promise<void> {
  nextStage.value = await getNextDemoScreenshotStage()
}

async function captureStage(): Promise<void> {
  if (!nextStage.value || capturing.value) return
  capturing.value = true
  try {
    await captureDemoStageScreenshot(nextStage.value)
    await refreshStage()
  } catch (error) {
    window.alert(error instanceof Error ? error.message : '阶段截图记录失败')
  } finally {
    capturing.value = false
  }
}

onMounted(refreshStage)
</script>

<style scoped>
.demo-boundary-banner {
  display: grid;
  gap: 8px;
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 3000;
  max-width: calc(100vw - 36px);
  padding: 10px 16px;
  border: 1px solid var(--el-color-warning);
  border-radius: 8px;
  background: var(--el-color-warning-light-9);
  color: var(--el-color-warning-dark-2);
  font-size: 13px;
  font-weight: 700;
  box-shadow: var(--el-box-shadow-light);
}

.demo-boundary-banner button {
  padding: 6px 10px;
  border: 1px solid currentColor;
  border-radius: 6px;
  background: white;
  color: inherit;
  cursor: pointer;
  font: inherit;
}
</style>
