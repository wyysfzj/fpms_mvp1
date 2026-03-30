<template>
  <section class="placeholder-page">
    <p class="eyebrow">设置 / 主数据 / 申请人</p>
    <h1>申请人主数据（预留）</h1>
    <p>
      这个入口保留给申请人主数据的后续列表与维护能力。当前阶段仅提供稳定路由，暂不开放对象级 CRUD、案件联动或导入导出。
    </p>
    <ul>
      <li>未来承载申请人列表与筛选</li>
      <li>未来承载申请人新增、编辑与启停用</li>
      <li>当前仅用于占位和导航落点</li>
    </ul>
  </section>
</template>

<style scoped>
.placeholder-page {
  display: grid;
  gap: 12px;
  padding: 24px;
  max-width: 760px;
}

.eyebrow {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

h1 {
  margin: 0;
  font-size: 28px;
}

p,
li {
  color: #4b5563;
  line-height: 1.75;
}

ul {
  margin: 0;
  padding-left: 20px;
}
</style>
