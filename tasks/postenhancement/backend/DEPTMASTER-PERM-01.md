# DEPTMASTER-PERM-01 — seed department master permissions

- Source: `docs/superpowers/plans/2026-04-09-department-master-permission-refresh.md`
- Type: `permission`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 department master 模块新增 truthful permission seed。
- Exact closure slice:
  - add `Department.Read`
  - add `Department.Write`
  - targeted permission tests
- Explicit non-closure:
  - 不做 backend CRUD
  - 不做 frontend path
- Remaining follow-up task ids:
  - `DEPTMASTER-BE-01`
  - `DEPTMASTER-FE-01`
- Allowlist:
  - `backend/app/modules/rbac/service.py`
  - `backend/tests/test_masterdata_prereq_contract.py`
- Verification:
  - task-scoped ruff
  - targeted pytest
