# BILLRPT-FE-01 — Billing 统计报表前端闭环

- Source: `docs/superpowers/plans/2026-03-30-billing-statistics-report.md`
- Type: `frontend page capability`
- Execution mode: Atomic

## Task Definition

- Goal: 在现有 `BillList.vue` 上收敛 billing 统计报表第一轮最小闭环。
- Exact closure slice:
  - 筛选
  - summary cards
  - 明细列表
- Explicit non-closure:
  - 不改 `PaymentList.vue`
  - 不建独立报表页
  - 不做图表/打印/导出
- Remaining follow-up task ids:
  - `BILLRPT-QA-01`
