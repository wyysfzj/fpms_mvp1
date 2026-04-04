# ANNRPT-SUCCESS-FE-01

- status: PASS
- closure slice: 在 `AnnuityTaskList.vue` 展示年费监视成功率指标
- non-closure: 未实现按客户/国别/年度拆分成功率、图表、导出
- verification:
  - `cd frontend && npm run lint -- src/api/annuity.ts src/api/annuity.types.ts src/modules/annuity/pages/AnnuityTaskList.vue`
  - `cd frontend && npm run typecheck`
- notes:
  - `success_rate = null` 时显示 `暂无`
  - 所有新增用户可见文案均为简体中文

