<template>
  <article
    class="lifecycle-summary-card"
    :class="{ 'lifecycle-summary-card--emphasis': props.emphasis }"
    :data-testid="props.testId"
  >
    <header class="summary-card-header">
      <div>
        <p class="summary-kicker">{{ props.kicker }}</p>
        <h2>{{ props.title }}</h2>
      </div>
      <span class="summary-status">{{ props.statusLabel }}</span>
    </header>

    <section class="summary-section">
      <p class="summary-question">现在是什么状态</p>
      <p v-for="line in props.currentLines" :key="line" class="summary-answer">{{ line }}</p>
    </section>
    <section class="summary-section">
      <p class="summary-question">最近发生了什么</p>
      <p class="summary-answer">{{ props.latestText }}</p>
      <p v-if="props.latestAt" class="summary-time">{{ props.latestAt }}</p>
    </section>
    <section class="summary-section">
      <p class="summary-question">下一步是什么</p>
      <p class="summary-answer">{{ props.nextText }}</p>
      <p v-if="props.nextAt" class="summary-time">{{ props.nextAt }}</p>
    </section>
    <p v-if="props.footnote" class="summary-footnote">{{ props.footnote }}</p>
  </article>
</template>

<script setup lang="ts">
const props = defineProps<{
  testId: string
  kicker: string
  title: string
  statusLabel: string
  currentLines: readonly string[]
  latestText: string
  latestAt: string | null
  nextText: string
  nextAt: string | null
  footnote?: string
  emphasis?: boolean
}>()
</script>

<style scoped>
.lifecycle-summary-card {
  min-width: 0;
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--bg-card);
}

.lifecycle-summary-card--emphasis {
  border-top: 2px solid var(--el-color-primary);
}

.summary-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.summary-card-header h2,
.summary-card-header p,
.summary-section p,
.summary-footnote {
  margin: 0;
}

.summary-card-header h2 {
  font-size: 16px;
  font-weight: 600;
}

.summary-kicker,
.summary-question,
.summary-time,
.summary-footnote {
  color: var(--text-secondary);
  font-size: 12px;
}

.summary-kicker {
  margin-bottom: 4px !important;
}

.summary-status {
  flex: 0 0 auto;
  padding: 4px 8px;
  border-radius: 999px;
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-size: 12px;
  font-weight: 600;
}

.summary-section {
  display: grid;
  gap: 5px;
  margin-top: 16px;
}

.summary-answer {
  overflow-wrap: anywhere;
  font-size: 14px;
}

.summary-time {
  margin-top: 3px !important;
}

.summary-footnote {
  margin-top: 16px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}
</style>
