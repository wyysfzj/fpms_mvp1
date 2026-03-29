# CASEBF-DB-01 — 案件递交 submitted_date 承载

- Source: `docs/superpowers/plans/2026-03-30-case-batch-filing-prereq.md`
- Type: `backend db prerequisite`
- Execution mode: Atomic

## Task Definition

- Goal: 为 `Case` 增加 `submitted_date` 结构化字段与 SQLite-safe migration。
- Exact closure slice:
  - `Case.submitted_date`
  - 对应 migration 与模型同步
- Explicit non-closure:
  - 不改批量查询
  - 不改批量动作
  - 不改前端
  - 不改 documents/tasks
- Remaining follow-up task ids:
  - `CASEBF-BE-QUERY-01`
  - `CASEBF-BE-ACT-01`
  - `CASEBF-FE-01`
  - `CASEBF-QA-01`
