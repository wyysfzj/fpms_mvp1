<template>
  <section class="case-lifecycle-overlay" data-testid="case-lifecycle-overlay">
    <div v-if="loading" class="overlay-loading">正在加载三线生命周期…</div>
    <ApiErrorBanner v-else-if="error" :error="error" :dismissable="false" />
    <template v-else-if="overlay">
      <header class="overlay-meta">
        <span>快照修订：{{ overlay.lifecycleRevision }}</span>
        <span>生成时间：{{ overlay.generatedAt }}</span>
      </header>
      <div class="overlay-grid">
        <div data-overlay-lane="document">
          <DocumentEvidenceLane :milestones="overlay.milestones" />
        </div>
        <div data-overlay-lane="lifecycle">
          <LifecycleCenterLane
            :snapshot="overlay.centerSnapshot"
            :milestones="overlay.milestones"
          />
        </div>
        <div data-overlay-lane="fee">
          <FeeObligationLane :milestones="overlay.milestones" />
        </div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getLifecycleOverlay } from '../../../api/lifecycleOverlay'
import type { LifecycleOverlay } from '../../../api/lifecycleOverlay.types'
import type { ApiError } from '../../../api/types'
import ApiErrorBanner from '../../../components/errors/ApiErrorBanner.vue'
import DocumentEvidenceLane from './DocumentEvidenceLane.vue'
import FeeObligationLane from './FeeObligationLane.vue'
import LifecycleCenterLane from './LifecycleCenterLane.vue'

const props = defineProps<{
  caseId: string
}>()

const overlay = ref<LifecycleOverlay | null>(null)
const loading = ref(true)
const error = ref<ApiError | null>(null)

async function loadOverlay(): Promise<void> {
  loading.value = true
  error.value = null
  overlay.value = null
  try {
    overlay.value = await getLifecycleOverlay(props.caseId, {
      afterSequence: 0,
      limit: 200,
      asOfRevision: null,
    })
  } catch (caught) {
    error.value = caught as ApiError
  } finally {
    loading.value = false
  }
}

onMounted(loadOverlay)
</script>

<style scoped>
.case-lifecycle-overlay {
  margin: 20px 0;
}

.overlay-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 10px;
  color: var(--text-secondary);
  font-size: 12px;
}

.overlay-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr) minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.overlay-loading {
  padding: 28px;
  text-align: center;
  color: var(--text-secondary);
}

@media (max-width: 1100px) {
  .overlay-grid {
    grid-template-columns: 1fr;
  }
}
</style>
