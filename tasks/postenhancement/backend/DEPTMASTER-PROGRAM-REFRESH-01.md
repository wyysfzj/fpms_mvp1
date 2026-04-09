# DEPTMASTER-PROGRAM-REFRESH-01 — refresh department master program for router ownership

- Source: `docs/superpowers/plans/2026-04-09-department-master-router-refresh.md`
- Type: `planning`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在首次进入 department module 后，补齐 router ownership refresh，避免 `DEPTMASTER-BE-01` 越权触碰 shared router 文件。
- Exact closure slice:
  - add router refresh design/plan
  - define `DEPTMASTER-ROUTER-01`
- Explicit non-closure:
  - 不做 router wiring
  - 不做 backend CRUD
- Remaining follow-up task ids:
  - `DEPTMASTER-ROUTER-01`
  - `DEPTMASTER-BE-01`
  - `DEPTMASTER-FE-01`
  - `EXPSTAT-DEPARTMENT-DB-01`
  - `EXPSTAT-DEPARTMENT-BE-01`
  - `EXPSTAT-DEPARTMENT-FE-01`
  - `EXPSTAT-DEPARTMENT-QA-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-09-department-master-router-refresh-design.md`
  - `docs/superpowers/plans/2026-04-09-department-master-router-refresh.md`
  - `tasks/postenhancement/backend/DEPTMASTER-PROGRAM-REFRESH-01.md`
  - `tasks/postenhancement/backend/DEPTMASTER-QA-PROGRAM-REFRESH-01.md`
  - `tasks/postenhancement/backend/DEPTMASTER-ROUTER-01.md`
- Verification:
  - `./scripts/task_validate.sh DEPTMASTER-PROGRAM-REFRESH-01`
