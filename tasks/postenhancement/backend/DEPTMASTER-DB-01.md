# DEPTMASTER-DB-01 — add department master schema

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 新增 department master 的 ORM model 和 SQLite-safe migration。
- Exact closure slice:
  - add department master model
  - add migration
- Explicit non-closure:
  - 不做 expense `department_id`
  - 不做 backend CRUD
  - 不做 frontend path
- Remaining follow-up task ids:
  - `DEPTMASTER-BE-01`
  - `DEPTMASTER-FE-01`
  - `EXPSTAT-DEPARTMENT-DB-01`
- Allowlist:
  - `backend/app/modules/masterdata/departments/*.py`
  - `backend/alembic/versions/*.py`
  - `backend/app/api/router.py`
- Verification:
  - task-scoped ruff
  - migration smoke
