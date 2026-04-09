# DEPTMASTER-PROGRAM-SPEC-01 — freeze department master implementation program

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `planning`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 冻结 department master program 的 authority、runbook 和 task graph，为后续 Module 4 department lane 提供可执行 batch manifest。
- Exact closure slice:
  - add department master program spec/plan
  - define future task graph
- Explicit non-closure:
  - 不做任何 product code
  - 不做 migration/schema implementation
- Remaining follow-up task ids:
  - `DEPTMASTER-DB-01`
  - `DEPTMASTER-BE-01`
  - `DEPTMASTER-FE-01`
  - `EXPSTAT-DEPARTMENT-DB-01`
  - `EXPSTAT-DEPARTMENT-BE-01`
  - `EXPSTAT-DEPARTMENT-FE-01`
  - `EXPSTAT-DEPARTMENT-QA-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-09-department-master-program-design.md`
  - `docs/superpowers/plans/2026-04-09-department-master-program.md`
  - `tasks/postenhancement/backend/DEPTMASTER-PROGRAM-SPEC-01.md`
  - `tasks/postenhancement/backend/DEPTMASTER-QA-PROGRAM-SPEC-01.md`
  - `tasks/postenhancement/backend/DEPTMASTER-DB-01.md`
  - `tasks/postenhancement/backend/DEPTMASTER-BE-01.md`
  - `tasks/postenhancement/frontend/DEPTMASTER-FE-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-DB-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-BE-01.md`
  - `tasks/postenhancement/frontend/EXPSTAT-DEPARTMENT-FE-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-QA-01.md`
- Verification:
  - `./scripts/task_validate.sh DEPTMASTER-PROGRAM-SPEC-01`
