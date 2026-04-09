# DEPTMASTER-BE-01 — department master backend contract

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `backend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 department master 增加真实 backend list/create/update/deactivate contract。
- Exact closure slice:
  - backend list/create/update/deactivate endpoints
  - targeted tests
- Explicit non-closure:
  - 不做 expense department stats
  - 不做 frontend path
- Remaining follow-up task ids:
  - `DEPTMASTER-FE-01`
  - `EXPSTAT-DEPARTMENT-DB-01`
- Allowlist:
  - `backend/app/modules/masterdata/departments/*.py`
  - `backend/tests/test_department_master_api.py`
- Verification:
  - task-scoped ruff
  - targeted pytest
