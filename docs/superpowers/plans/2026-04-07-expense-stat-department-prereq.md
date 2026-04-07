# Expense Stat Department Prerequisite Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `low`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-prereq-heavy-story`

## Result Shape

- `spec/prerequisite freeze only`
- no product implementation

## Batch Manifest

### `EXPSTAT-DEPARTMENT-PRE-01`

- exact closure slice:
  - freeze truthful prerequisite authority for the department residual under `SPEC 5.10.2`
- explicit non-closure:
  - no product implementation
  - no schema/migration
  - no final-audit update
  - no worker residual handling
- allowlist:
  - `docs/superpowers/specs/2026-04-07-expense-stat-department-prereq-design.md`
  - `docs/superpowers/plans/2026-04-07-expense-stat-department-prereq.md`
  - `tasks/postenhancement/backend/EXPSTAT-DEPARTMENT-PRE-01.md`
  - `tasks/postenhancement/backend/EXPSTAT-QA-DEPARTMENT-PRE-01.md`
- verification:
  - `./scripts/task_validate.sh EXPSTAT-DEPARTMENT-PRE-01`
- evidence path:
  - `artifacts/EXPSTAT-DEPARTMENT-PRE-01`
- remaining follow-up task ids:
  - `EXPSTAT-QA-DEPARTMENT-PRE-01`

### `EXPSTAT-QA-DEPARTMENT-PRE-01`

- exact closure slice:
  - audit evidence and gate outcome for the department prerequisite freeze
- explicit non-closure:
  - no product implementation
  - no second prerequisite wave
- allowlist:
  - `tasks/postenhancement/backend/EXPSTAT-QA-DEPARTMENT-PRE-01.md`
  - `artifacts/EXPSTAT-DEPARTMENT-PRE-01/**`
  - `artifacts/EXPSTAT-QA-DEPARTMENT-PRE-01/**`
- verification:
  - `./scripts/task_validate.sh EXPSTAT-QA-DEPARTMENT-PRE-01`
- evidence path:
  - `artifacts/EXPSTAT-QA-DEPARTMENT-PRE-01`
- remaining follow-up task ids:
  - `None`

## Serialized Shared-file Decisions

- This wave owns only doc/task files.
- No product shared files are touched.

## Next Natural Follow-up

- no truthful department implementation story exists until a carrier decision is made
