# Expense Stat Residual Plan

- date: `2026-04-06`
- target residual: `SPEC 5.10.2 查询与统计`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: high
- `be_fe_coupling`: medium
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- prerequisite/spec freeze only
- no implementation

## Batch Manifest

### `EXPSTAT-SPEC-01`

- exact closure slice:
  - freeze the prerequisite judgment for Module 4 expense statistics residual
  - record why current carrier/state is insufficient for direct implementation
  - define the next follow-up task graph
- explicit non-closure:
  - no backend/frontend product implementation
  - no schema/migration
  - no final-audit update
- allowlist:
  - `docs/superpowers/specs/2026-04-06-expense-stat-gap-design.md`
  - `docs/superpowers/plans/2026-04-06-expense-stat-gap.md`
  - `tasks/postenhancement/backend/EXPSTAT-SPEC-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-PLAN-01.md`
- verification:
  - `./scripts/evidence_run.sh EXPSTAT-SPEC-01 lint test -f docs/superpowers/specs/2026-04-06-expense-stat-gap-design.md -a -f docs/superpowers/plans/2026-04-06-expense-stat-gap.md -a -f tasks/postenhancement/backend/EXPSTAT-SPEC-01.md -a -f tasks/postenhancement/backend/EXPSTAT-QA-PLAN-01.md`
  - `./scripts/evidence_run.sh EXPSTAT-SPEC-01 test /bin/zsh -lc "rg -n 'P0-prereq-heavy-story|WorkerID|per-department|gross-profit|not ready for direct implementation' docs/superpowers/specs/2026-04-06-expense-stat-gap-design.md docs/superpowers/plans/2026-04-06-expense-stat-gap.md tasks/postenhancement/backend/EXPSTAT-SPEC-01.md"`
  - `./scripts/task_validate.sh EXPSTAT-SPEC-01`
- evidence path:
  - `artifacts/EXPSTAT-SPEC-01/**`
- remaining follow-up task ids:
  - `EXPSTAT-CARRIER-SPEC-01`
  - `EXPSTAT-GROSSPROFIT-SPEC-01`

### `EXPSTAT-QA-PLAN-01`

- exact closure slice:
  - audit the planning-wave evidence and confirm no product implementation was absorbed
- explicit non-closure:
  - no product-code changes
  - no audit/close update
- allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-PLAN-01.md`
  - `artifacts/EXPSTAT-SPEC-01/**`
- verification:
  - `./scripts/evidence_run.sh EXPSTAT-QA-PLAN-01 lint test -f tasks/postenhancement/backend/EXPSTAT-QA-PLAN-01.md -a -f artifacts/EXPSTAT-SPEC-01/summary.md -a -f artifacts/EXPSTAT-SPEC-01/results.jsonl`
  - `./scripts/evidence_run.sh EXPSTAT-QA-PLAN-01 test /bin/zsh -lc "./scripts/task_validate.sh EXPSTAT-SPEC-01 && rg -n 'no backend/frontend product implementation|EXPSTAT-CARRIER-SPEC-01|EXPSTAT-GROSSPROFIT-SPEC-01' artifacts/EXPSTAT-SPEC-01/summary.md"`
  - `./scripts/task_validate.sh EXPSTAT-QA-PLAN-01`
- evidence path:
  - `artifacts/EXPSTAT-QA-PLAN-01/**`
- remaining follow-up task ids:
  - `None`

## Serialized Shared-file Decisions

- this planning wave touches only docs/task files
- any future product execution must serialize:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
  - `frontend/src/api/expenses.ts`
  - `frontend/src/api/expenses.types.ts`
  - `frontend/src/modules/expenses/pages/ExpenseList.vue`

## Next Natural Follow-up

- `EXPSTAT-CARRIER-SPEC-01`
- reason:
  - current product cannot honestly implement worker/department/gross-profit statistics without freezing carrier authority first

