# EXPSTAT-QA-DEPARTMENT-PRE-01 — expense statistics department prerequisite QA audit

- Source: `docs/superpowers/plans/2026-04-07-expense-stat-department-prereq.md`
- Type: `QA close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `EXPSTAT-DEPARTMENT-PRE-01` 的 evidence、task gate 和 scope compliance。
- Exact closure slice:
  - 校验 `artifacts/EXPSTAT-DEPARTMENT-PRE-01/**`
  - 生成 `artifacts/EXPSTAT-QA-DEPARTMENT-PRE-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不做 worker prerequisite work
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-DEPARTMENT-PRE-01.md`
  - `artifacts/EXPSTAT-DEPARTMENT-PRE-01/**`
  - `artifacts/EXPSTAT-QA-DEPARTMENT-PRE-01/**`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-QA-DEPARTMENT-PRE-01`

## Execution Checklist

- [ ] Confirm no product files were modified
- [ ] Confirm department semantics were not faked from unrelated fields
- [ ] Confirm task gate passes
