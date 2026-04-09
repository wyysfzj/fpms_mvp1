# EXPSTAT-WORKER-QA-01 — QA close audit for worker expense statistics lane

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
- Type: `qa-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 worker lane 的 DB/BE/FE evidence 和 gate，确认 worker residual 是否已形成真实闭环。
- Exact closure slice:
  - 审计 worker lane evidence
  - 生成 `artifacts/EXPSTAT-WORKER-QA-01/**`
- Explicit non-closure:
  - 不关闭 department residual
  - 不更新 Module 4 final close decision
- Remaining follow-up task ids:
  - `EXPSTAT-DEPARTMENT-MASTER-PRE-01`
  - `EXPSTAT-CLOSE-02`
- Allowlist:
  - task/docs/artifacts only
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-WORKER-QA-01`
