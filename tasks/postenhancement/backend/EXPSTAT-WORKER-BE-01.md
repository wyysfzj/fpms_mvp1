# EXPSTAT-WORKER-BE-01 — worker filter and create semantics for expense stats

- Source: `docs/superpowers/plans/2026-04-09-expense-stat-schema-program.md`
- Type: `backend`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- Goal: 为 expenses backend 增加真实 `worker_id` create/list/filter semantics，并补 targeted tests。
- Exact closure slice:
  - `POST /expenses` accept `worker_id`
  - `GET /expenses` support worker filter
  - backend stats path honors worker filter
  - targeted tests
- Explicit non-closure:
  - 不做 frontend path
  - 不做 department lane
- Remaining follow-up task ids:
  - `EXPSTAT-WORKER-FE-01`
  - `EXPSTAT-WORKER-QA-01`
- Allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
  - `backend/tests/test_expense_stats_api.py`
- Verification:
  - task-scoped ruff
  - targeted pytest
