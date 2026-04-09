# DEPTMASTER-PERM-REFRESH-01 — refresh department master program for permission seed

- Source: `docs/superpowers/plans/2026-04-09-department-master-permission-refresh.md`
- Type: `planning`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 补齐 permission seed prerequisite，避免 `DEPTMASTER-BE-01` 越权触碰 shared RBAC 文件。
- Exact closure slice:
  - add permission refresh design/plan
  - define `DEPTMASTER-PERM-01`
- Explicit non-closure:
  - 不做 permission seed implementation
  - 不做 backend CRUD
- Remaining follow-up task ids:
  - `DEPTMASTER-PERM-01`
  - `DEPTMASTER-BE-01`
- Allowlist:
  - `docs/superpowers/specs/2026-04-09-department-master-permission-refresh-design.md`
  - `docs/superpowers/plans/2026-04-09-department-master-permission-refresh.md`
  - `tasks/postenhancement/backend/DEPTMASTER-PERM-REFRESH-01.md`
  - `tasks/postenhancement/backend/DEPTMASTER-QA-PERM-REFRESH-01.md`
  - `tasks/postenhancement/backend/DEPTMASTER-PERM-01.md`
- Verification:
  - `./scripts/task_validate.sh DEPTMASTER-PERM-REFRESH-01`
