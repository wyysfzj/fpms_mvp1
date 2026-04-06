# Expense Gross-Profit Semantics Plan

- date: `2026-04-06`
- target: `SPEC 5.10.2 gross-profit semantics`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- semantics/spec freeze only
- no implementation

## Batch Manifest

### `EXPSTAT-GROSSPROFIT-SPEC-01`

- exact closure slice:
  - freeze receipt-side authority and first-round aggregation rules for `SPEC 5.10.2` gross-profit analysis
  - separate this slice from `SPEC 5.11`
  - define the next truthful implementation graph
- explicit non-closure:
  - no product implementation
  - no schema/migration
  - no `5.11` implementation
  - no final-audit update
- allowlist:
  - `docs/superpowers/specs/2026-04-06-expense-stat-grossprofit-design.md`
  - `docs/superpowers/plans/2026-04-06-expense-stat-grossprofit.md`
  - `tasks/postenhancement/backend/EXPSTAT-GROSSPROFIT-SPEC-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-GROSSPROFIT-SPEC-01.md`
- verification:
  - `./scripts/evidence_run.sh EXPSTAT-GROSSPROFIT-SPEC-01 lint test -f docs/superpowers/specs/2026-04-06-expense-stat-grossprofit-design.md -a -f docs/superpowers/plans/2026-04-06-expense-stat-grossprofit.md -a -f tasks/postenhancement/backend/EXPSTAT-GROSSPROFIT-SPEC-01.md -a -f tasks/postenhancement/backend/EXPSTAT-QA-GROSSPROFIT-SPEC-01.md`
  - `./scripts/evidence_run.sh EXPSTAT-GROSSPROFIT-SPEC-01 test /bin/zsh -lc "rg -n 'CaseReceipt\\.received_amt|case-level aggregation only|same currency bucket|not a substitute for `5\\.11`|EXPSTAT-GROSSPROFIT-BE-01|FEOVERVIEW-SPEC-01' docs/superpowers/specs/2026-04-06-expense-stat-grossprofit-design.md docs/superpowers/plans/2026-04-06-expense-stat-grossprofit.md tasks/postenhancement/backend/EXPSTAT-GROSSPROFIT-SPEC-01.md"`
  - `./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-SPEC-01`
- evidence path:
  - `artifacts/EXPSTAT-GROSSPROFIT-SPEC-01/**`
- remaining follow-up task ids:
  - `EXPSTAT-GROSSPROFIT-BE-01`
  - `EXPSTAT-GROSSPROFIT-FE-01`
  - `EXPSTAT-GROSSPROFIT-QA-01`
  - `FEOVERVIEW-SPEC-01`

### `EXPSTAT-QA-GROSSPROFIT-SPEC-01`

- exact closure slice:
  - audit the gross-profit semantics-wave evidence and confirm no product behavior was absorbed
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-GROSSPROFIT-SPEC-01.md`
  - `artifacts/EXPSTAT-GROSSPROFIT-SPEC-01/**`
- verification:
  - `./scripts/evidence_run.sh EXPSTAT-QA-GROSSPROFIT-SPEC-01 lint test -f tasks/postenhancement/backend/EXPSTAT-QA-GROSSPROFIT-SPEC-01.md -a -f artifacts/EXPSTAT-GROSSPROFIT-SPEC-01/summary.md -a -f artifacts/EXPSTAT-GROSSPROFIT-SPEC-01/results.jsonl`
  - `./scripts/evidence_run.sh EXPSTAT-QA-GROSSPROFIT-SPEC-01 test /bin/zsh -lc "./scripts/task_validate.sh EXPSTAT-GROSSPROFIT-SPEC-01 && rg -n 'no product implementation|CaseReceipt\\.received_amt|same currency bucket|FEOVERVIEW-SPEC-01' artifacts/EXPSTAT-GROSSPROFIT-SPEC-01/summary.md"`
  - `./scripts/task_validate.sh EXPSTAT-QA-GROSSPROFIT-SPEC-01`
- evidence path:
  - `artifacts/EXPSTAT-QA-GROSSPROFIT-SPEC-01/**`
- remaining follow-up task ids:
  - `None`

## Next Natural Follow-up

- `EXPSTAT-GROSSPROFIT-BE-01`
- reason:
  - after this freeze, the first truthful implementation slice is a case-level gross-profit summary on the existing expense statistics endpoint
