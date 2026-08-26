<template>
  <div class="demo-boundary-banner" role="status" data-testid="demo-v6-boundary-banner">
    合成演示数据｜仅用于技术展示，非客户、生产或官方事实
  </div>
</template>

<style scoped>
.demo-boundary-banner {
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
</style>
