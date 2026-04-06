# EXPSTAT-GROSSPROFIT-FE-01

- status: PASS
- exact closure slice:
  - render case-level gross-profit grouped summary cards on `ExpenseList.vue`
  - adapt frontend expense stats contract for `gross_profit_amounts`
- explicit non-closure respected:
  - no backend changes
  - no client/department/worker gross-profit UI
  - no `SPEC 5.11` UI
- verification:
  - `cd frontend && npm run lint -- src/api/expenses.ts src/api/expenses.types.ts src/modules/expenses/pages/ExpenseList.vue`
  - `cd frontend && npm run typecheck`
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-FE-01`
