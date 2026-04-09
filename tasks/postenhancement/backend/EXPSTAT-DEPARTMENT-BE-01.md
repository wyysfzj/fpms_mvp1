# EXPSTAT-DEPARTMENT-BE-01 — department filter and grouped stats semantics

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `backend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 expenses backend 增加真实 `department_id` create/list/filter/group semantics，并补 targeted tests。
- Exact closure slice:
  - `POST /expenses` accept `department_id`
  - `GET /expenses` support department filter
  - stats path returns department-grouped totals
  - targeted tests
- Explicit non-closure:
  - 不做 frontend path
  - 不做 Module 4 final close
- Remaining follow-up task ids:
  - `EXPSTAT-DEPARTMENT-FE-01`
  - `EXPSTAT-DEPARTMENT-QA-01`
- Allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
  - `backend/tests/test_expense_stats_api.py`
- Verification:
  - task-scoped ruff
  - targeted pytest
