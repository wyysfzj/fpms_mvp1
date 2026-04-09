# EXPSTAT-DEPARTMENT-QA-01 — QA close audit for department expense statistics lane

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `qa-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 department master + expense department lane 的 evidence 和 gate，确认 department residual 是否已形成真实闭环。
- Exact closure slice:
  - audit department lane evidence
  - generate `artifacts/EXPSTAT-DEPARTMENT-QA-01/**`
- Explicit non-closure:
  - 不关闭 Module 4 其他 residual
  - 不更新 final audit / close decision
- Remaining follow-up task ids:
  - `EXPSTAT-CLOSE-02`
- Allowlist:
  - task/docs/artifacts only
- Verification:
  - `./scripts/task_validate.sh EXPSTAT-DEPARTMENT-QA-01`
