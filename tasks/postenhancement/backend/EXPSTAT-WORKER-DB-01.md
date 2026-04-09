# EXPSTAT-WORKER-DB-01 — add worker carrier to expense schema

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
- Type: `schema`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 `T_Expense` 新增真实 `worker_id` carrier，并保持 SQLite-safe migration。
- Exact closure slice:
  - add `worker_id` to expense ORM model
  - add migration
- Explicit non-closure:
  - 不处理 department carrier
  - 不做 backend filter semantics
  - 不做 frontend path
- Remaining follow-up task ids:
  - `EXPSTAT-WORKER-BE-01`
  - `EXPSTAT-WORKER-FE-01`
  - `EXPSTAT-WORKER-QA-01`
- Allowlist:
  - `backend/app/modules/expenses/models.py`
  - `backend/alembic/versions/*.py`
- Verification:
  - task-scoped ruff
  - migration smoke if applicable
