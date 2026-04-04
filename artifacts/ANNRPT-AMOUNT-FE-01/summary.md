# ANNRPT-AMOUNT-FE-01

- status: PASS
- closure slice: 在 `AnnuityTaskList.vue` 展示按客户 / 国家 / 年度金额汇总
- non-closure: 未实现 success-rate、图表、导出、新页面
- verification:
  - `cd frontend && npm run lint -- src/api/annuity.ts src/api/annuity.types.ts src/modules/annuity/pages/AnnuityTaskList.vue`
  - `cd frontend && npm run typecheck`
- notes:
  - 所有新增用户可见文案均为简体中文
  - 仅扩展现有 summary 展示，不改筛选和列表交互

