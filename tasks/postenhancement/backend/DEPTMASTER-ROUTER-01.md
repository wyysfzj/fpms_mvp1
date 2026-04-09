# DEPTMASTER-ROUTER-01 — wire department master router

- Source: `docs/superpowers/plans/2026-04-09-department-master-router-refresh.md`
- Type: `router`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 首次进入 department module 时完成 one-time router wiring。
- Exact closure slice:
  - add department router import
  - add `include_router(...)`
- Explicit non-closure:
  - 不做 backend CRUD
  - 不做 frontend path
  - 不做 expense department stats
- Remaining follow-up task ids:
  - `DEPTMASTER-BE-01`
  - `DEPTMASTER-FE-01`
  - `EXPSTAT-DEPARTMENT-DB-01`
- Allowlist:
  - `backend/app/api/router.py`
  - `backend/app/modules/masterdata/departments/api.py`
- Verification:
  - task-scoped ruff
