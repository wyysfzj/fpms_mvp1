# COMRPT-BE-01 — 提成统计报表后端契约收敛

- Source: `docs/superpowers/plans/2026-03-30-commission-statistics-report.md`
- Type: `backend report endpoint behavior`
- Execution mode: Atomic

## Task Definition

- Goal: 收敛并补齐 commission settlement report backend contract，使其稳定支撑第一轮提成统计报表。
- Exact closure slice:
  - `GET /commission/reports/settlement` 的筛选、summary、按代理人统计、按案件统计、明细列表 contract
- Explicit non-closure:
  - 不做 schema 变更
  - 不做成本占比分析
  - 不做图表/打印/导出
  - 不改前端页面
- Remaining follow-up task ids:
  - `COMRPT-FE-01`
  - `COMRPT-QA-01`
