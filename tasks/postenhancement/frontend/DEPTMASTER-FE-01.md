# DEPTMASTER-FE-01 — department master management path

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `frontend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 接入 department master 的真实管理页面和 API 用户路径。
- Exact closure slice:
  - frontend department list/create/update/deactivate path
  - frontend API/types wiring
- Explicit non-closure:
  - 不做 expense department stats
  - 不做 close audit
- Remaining follow-up task ids:
  - `EXPSTAT-DEPARTMENT-DB-01`
  - `EXPSTAT-DEPARTMENT-BE-01`
  - `EXPSTAT-DEPARTMENT-FE-01`
- Allowlist:
  - `frontend/src/api/departments*.ts`
  - `frontend/src/modules/masterdata/departments/**/*.vue`
  - `frontend/src/constants/menu.ts`
  - frontend route wiring files if needed
- Verification:
  - frontend lint
  - typecheck
