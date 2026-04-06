# Expense Stat Carrier Plan

- date: `2026-04-06`
- target: `SPEC 5.10.2 carrier authority`

## Story Shape Classification

- `shared_file_density`: medium
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- carrier/spec freeze only
- no implementation

## Batch Manifest

### `EXPSTAT-CARRIER-SPEC-01`

- exact closure slice:
  - freeze which `5.10.2` sub-slices are reachable on current carriers
  - reject fake implementations for worker and department statistics
  - define next execution graph
- explicit non-closure:
  - no product implementation
  - no schema/migration
  - no final-audit update
- allowlist:
  - `docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md`
  - `docs/superpowers/plans/2026-04-06-expense-stat-carrier.md`
  - `tasks/postenhancement/backend/EXPSTAT-CARRIER-SPEC-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-CARRIER-SPEC-01.md`
- verification:
  - `./scripts/evidence_run.sh EXPSTAT-CARRIER-SPEC-01 lint test -f docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md -a -f docs/superpowers/plans/2026-04-06-expense-stat-carrier.md -a -f tasks/postenhancement/backend/EXPSTAT-CARRIER-SPEC-01.md -a -f tasks/postenhancement/backend/EXPSTAT-QA-CARRIER-SPEC-01.md`
  - `./scripts/evidence_run.sh EXPSTAT-CARRIER-SPEC-01 test /bin/zsh -lc "rg -n 'created_by is not a faithful substitute|per-client expense totals|EXPSTAT-CASECLIENT-01|EXPSTAT-WORKER-PRE-01|EXPSTAT-DEPARTMENT-PRE-01|EXPSTAT-GROSSPROFIT-SPEC-01' docs/superpowers/specs/2026-04-06-expense-stat-carrier-design.md docs/superpowers/plans/2026-04-06-expense-stat-carrier.md tasks/postenhancement/backend/EXPSTAT-CARRIER-SPEC-01.md"`
  - `./scripts/task_validate.sh EXPSTAT-CARRIER-SPEC-01`
- evidence path:
  - `artifacts/EXPSTAT-CARRIER-SPEC-01/**`
- remaining follow-up task ids:
  - `EXPSTAT-CASECLIENT-01`
  - `EXPSTAT-WORKER-PRE-01`
  - `EXPSTAT-DEPARTMENT-PRE-01`
  - `EXPSTAT-GROSSPROFIT-SPEC-01`

### `EXPSTAT-QA-CARRIER-SPEC-01`

- exact closure slice:
  - audit the carrier-wave evidence and confirm no product behavior was absorbed
- explicit non-closure:
  - no product-code changes
  - no close-decision update
- allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-CARRIER-SPEC-01.md`
  - `artifacts/EXPSTAT-CARRIER-SPEC-01/**`
- verification:
  - `./scripts/evidence_run.sh EXPSTAT-QA-CARRIER-SPEC-01 lint test -f tasks/postenhancement/backend/EXPSTAT-QA-CARRIER-SPEC-01.md -a -f artifacts/EXPSTAT-CARRIER-SPEC-01/summary.md -a -f artifacts/EXPSTAT-CARRIER-SPEC-01/results.jsonl`
  - `./scripts/evidence_run.sh EXPSTAT-QA-CARRIER-SPEC-01 test /bin/zsh -lc "./scripts/task_validate.sh EXPSTAT-CARRIER-SPEC-01 && rg -n 'no product implementation|EXPSTAT-CASECLIENT-01|EXPSTAT-WORKER-PRE-01|EXPSTAT-DEPARTMENT-PRE-01|EXPSTAT-GROSSPROFIT-SPEC-01' artifacts/EXPSTAT-CARRIER-SPEC-01/summary.md"`
  - `./scripts/task_validate.sh EXPSTAT-QA-CARRIER-SPEC-01`
- evidence path:
  - `artifacts/EXPSTAT-QA-CARRIER-SPEC-01/**`
- remaining follow-up task ids:
  - `None`

## Next Natural Follow-up

- `EXPSTAT-CASECLIENT-01`
- reason:
  - this is the only current `5.10.2` statistics slice that is both truthful and schema-safe

