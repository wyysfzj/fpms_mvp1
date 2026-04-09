# DEPTMASTER-QA-PROGRAM-SPEC-01 — audit department master program-spec wave

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `qa-audit`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 审计 `DEPTMASTER-PROGRAM-SPEC-01` 的 evidence、task gate 和 scope compliance。
- Exact closure slice:
  - audit program-spec evidence
  - generate `artifacts/DEPTMASTER-QA-PROGRAM-SPEC-01/**`
- Explicit non-closure:
  - 不做 product code
  - 不改写 program plan
- Remaining follow-up task ids:
  - `DEPTMASTER-DB-01`
  - `DEPTMASTER-BE-01`
  - `DEPTMASTER-FE-01`
  - `EXPSTAT-DEPARTMENT-DB-01`
  - `EXPSTAT-DEPARTMENT-BE-01`
  - `EXPSTAT-DEPARTMENT-FE-01`
  - `EXPSTAT-DEPARTMENT-QA-01`
- Allowlist:
  - task/docs/artifacts only
- Verification:
  - `./scripts/task_validate.sh DEPTMASTER-QA-PROGRAM-SPEC-01`
