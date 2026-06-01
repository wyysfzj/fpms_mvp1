<template>
  <main class="page-container official-workflow-placeholder">
    <div class="page-header">
      <div>
        <h1>{{ title }}</h1>
        <p class="placeholder-subtitle">{{ description }}</p>
      </div>
    </div>
    <el-alert
      type="info"
      :closable="false"
      title="官方工作包入口"
      description="请从案件、往来文件或费用记录进入具体工作包。"
      show-icon
    />
  </main>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title?: string
  description?: string
}>(), {
  title: '官方工作包',
  description: '请选择具体工作包。',
})
</script>

<style scoped>
.official-workflow-placeholder {
  display: grid;
  gap: 18px;
}

.placeholder-subtitle {
  margin: 6px 0 0;
  color: var(--text-sub);
  font-size: 14px;
}
</style>
