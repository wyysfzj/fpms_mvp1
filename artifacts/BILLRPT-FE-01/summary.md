# BILLRPT-FE-01

- 状态: PASS
- 闭环: 在 BillList.vue 上完成应收/逾期/坏账/账龄的第一轮统计报表前端闭环，包括筛选、summary cards、账龄摘要和明细列表列补齐。
- 非闭环: 未修改 PaymentList.vue，未新增独立 BillingReport.vue，未实现图表、打印、导出或预测型分析。
- 验证:
  - `cd frontend && npm run lint -- src/api/billing.ts src/api/billing.types.ts src/modules/billing/pages/BillList.vue` -> 0
  - `cd frontend && npm run typecheck` -> 0
