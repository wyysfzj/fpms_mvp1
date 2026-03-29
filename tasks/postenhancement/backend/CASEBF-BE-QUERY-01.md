# CASEBF-BE-QUERY-01 — 批件递交查询 contract

- Source: `docs/superpowers/plans/2026-03-30-case-batch-filing-prereq.md`
- Type: `backend api`
- Execution mode: Atomic

## Task Definition

- Goal: 提供批件递交页面专用的最小筛选查询与列表 contract。
- Exact closure slice:
  - 按最小筛选集检索 `NOT_FILED` 候选案件
  - 返回批件递交所需最小列表字段
- Explicit non-closure:
  - 不执行状态迁移
  - 不更新 `submitted_date`
  - 不改前端
  - 不改 documents/tasks
- Remaining follow-up task ids:
  - `CASEBF-BE-ACT-01`
  - `CASEBF-FE-01`
  - `CASEBF-QA-01`
