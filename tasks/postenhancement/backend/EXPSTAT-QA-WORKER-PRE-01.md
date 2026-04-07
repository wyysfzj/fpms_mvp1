# EXPSTAT-QA-WORKER-PRE-01 — expense statistics worker prerequisite QA audit

- Source: `docs/superpowers/plans/2026-04-07-expense-stat-worker-prereq.md`
- Type: `QA close audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `EXPSTAT-WORKER-PRE-01` 的 evidence、task gate 和 scope compliance。
- Exact closure slice:
  - 校验 `artifacts/EXPSTAT-WORKER-PRE-01/**`
  - 生成 `artifacts/EXPSTAT-QA-WORKER-PRE-01/**`
- Explicit non-closure:
  - 不做任何产品代码修改
  - 不做 department prerequisite
- Remaining follow-up task ids:
  - `None`
- Allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-WORKER-PRE-01.md`
  - `artifacts/EXPSTAT-WORKER-PRE-01/**`
  - `artifacts/EXPSTAT-QA-WORKER-PRE-01/**`
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-QA-WORKER-PRE-01`

## Execution Checklist

- [ ] Confirm no product files were modified
- [ ] Confirm worker semantics were not reinterpreted as audit columns
- [ ] Confirm task gate passes
