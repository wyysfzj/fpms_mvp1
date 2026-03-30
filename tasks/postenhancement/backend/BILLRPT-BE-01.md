# BILLRPT-BE-01 — Billing 统计报表后端契约收敛

- Source: `docs/superpowers/plans/2026-03-30-billing-statistics-report.md`
- Type: `backend report endpoint behavior`
- Execution mode: Atomic

## Task Definition

- Goal: 收敛并补齐 `GET /bills` 的 billing statistics report backend contract，使其稳定支撑第一轮 `应收 / 逾期 / 坏账 / 账龄` 报表。
- Exact closure slice:
  - `GET /bills` 的筛选、summary、账龄/逾期/坏账口径、明细列表 contract
- Explicit non-closure:
  - 不做 schema 变更
  - 不改前端页面
  - 不做图表/打印/导出
- Remaining follow-up task ids:
  - `BILLRPT-FE-01`
  - `BILLRPT-QA-01`
