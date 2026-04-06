# EXPSTAT-GROSSPROFIT-BE-01

- status: PASS
- exact closure slice:
  - add case-level `gross_profit_amounts` to `GET /expenses?include_stats=true`
  - compute rows from `CaseReceipt.received_amt - Expense.amount`
  - group by `(case_id, currency)`
  - cover semantics with targeted backend tests
- explicit non-closure respected:
  - no frontend changes
  - no client/department/worker gross-profit
  - no FX conversion
  - no `SPEC 5.11`
- verification:
  - `python3 -m ruff check backend/app/modules/expenses/api.py backend/app/modules/expenses/service.py backend/tests/test_expense_stats_api.py`
  - `cd backend && pytest -q tests/test_expense_stats_api.py`
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-BE-01`
