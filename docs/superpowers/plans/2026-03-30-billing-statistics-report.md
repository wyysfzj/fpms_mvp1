# RPT-BILL — Billing Statistics Report Plan

- Story Shape Classification:
  - `shared_file_density`: `medium`
  - `prereq_dependency_density`: `low`
  - `be_fe_coupling`: `chained (BE -> FE)`
  - `evidence_cost`: `medium`
- `chosen_runbook`: `P0-frontend-heavy-story`

## Batch Manifest

1. `BILLRPT-BE-01`
- exact closure slice: `GET /bills` 的 billing report/list contract，覆盖筛选、summary、账龄/逾期/坏账口径与明细字段
- explicit non-closure: 不改 schema，不改前端，不做图表/导出

2. `BILLRPT-FE-01`
- exact closure slice: `BillList.vue` 的报表前端闭环，覆盖筛选、summary cards、明细列表
- explicit non-closure: 不改 `PaymentList.vue`，不建独立报表页，不做图表/导出

3. `BILLRPT-QA-01`
- exact closure slice: task gate 审计、evidence 审计、story close summary
- explicit non-closure: 不改产品代码

## Wave Order

- Wave 1 `BILLRPT-BE-01`
- Wave 2 `BILLRPT-FE-01`
- Wave 3 `BILLRPT-QA-01`
