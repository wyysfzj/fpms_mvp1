# COMRPT-FE-01 — 提成统计报表前端闭环

- Source: `docs/superpowers/plans/2026-03-30-commission-statistics-report.md`
- Type: `frontend page capability`
- Execution mode: Atomic

## Task Definition

- Goal: 在现有 `CommissionSettlement.vue` 上收敛提成统计报表的第一轮最小闭环。
- Exact closure slice:
  - 筛选
  - summary cards
  - 按代理人统计
  - 按案件统计
  - 明细列表
- Explicit non-closure:
  - 不新建独立报表页
  - 不改批次创建/明细生成逻辑
  - 不做图表/打印/导出
  - 不做成本占比分析
- Remaining follow-up task ids:
  - `COMRPT-QA-01`
