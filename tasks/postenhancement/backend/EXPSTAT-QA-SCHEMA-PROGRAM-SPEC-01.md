# EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01 — QA audit for expense statistics schema program

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
- Type: `qa-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `EXPSTAT-SCHEMA-PROGRAM-SPEC-01` planning wave 的 evidence、gate 和 future batch graph。
- Exact closure slice:
  - 审计 planning wave evidence
  - 生成 `artifacts/EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不做第二轮 planning rewrite
- Remaining follow-up task ids:
  - `EXPSTAT-WORKER-DB-01`
  - `EXPSTAT-WORKER-BE-01`
  - `EXPSTAT-WORKER-FE-01`
  - `EXPSTAT-WORKER-QA-01`
  - `EXPSTAT-DEPARTMENT-MASTER-PRE-01`
- Allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01.md`
  - `artifacts/EXPSTAT-SCHEMA-PROGRAM-SPEC-01/**`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-QA-SCHEMA-PROGRAM-SPEC-01`
