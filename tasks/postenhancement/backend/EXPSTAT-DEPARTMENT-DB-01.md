# EXPSTAT-DEPARTMENT-DB-01 — add expense department carrier

- Source: `docs/superpowers/plans/2026-04-09-department-master-program.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 在 department master 存在后，为 `T_Expense` 新增真实 `department_id` carrier。
- Exact closure slice:
  - add `department_id` to expense ORM model
  - add SQLite-safe migration
- Explicit non-closure:
  - 不做 backend aggregation semantics
  - 不做 frontend path
- Remaining follow-up task ids:
  - `EXPSTAT-DEPARTMENT-BE-01`
  - `EXPSTAT-DEPARTMENT-FE-01`
  - `EXPSTAT-DEPARTMENT-QA-01`
- Allowlist:
  - `backend/app/modules/expenses/models.py`
  - `backend/alembic/versions/*.py`
- Verification:
  - task-scoped ruff
  - migration smoke
