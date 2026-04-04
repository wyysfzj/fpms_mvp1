# ANNRPT-AMOUNT-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `semantics freeze before grouped amount implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

### Task 1

- task: `tasks/postenhancement/backend/ANNRPT-AMOUNT-SPEC-01.md`
- owner: `main thread`
- allowlist:
  - `docs/superpowers/specs/2026-04-05-annuity-report-amount-semantics-design.md`
  - `docs/superpowers/plans/2026-04-05-annuity-report-amount-semantics.md`
  - `tasks/postenhancement/backend/ANNRPT-AMOUNT-SPEC-01.md`
- verification:
  - `./scripts/task_validate.sh ANNRPT-AMOUNT-SPEC-01`

### Task 2

- task: `tasks/postenhancement/backend/ANNRPT-QA-AMOUNT-SPEC-01.md`
- owner: `main thread`
- allowlist:
  - `docs/superpowers/specs/2026-04-05-annuity-report-amount-semantics-design.md`
  - `docs/superpowers/plans/2026-04-05-annuity-report-amount-semantics.md`
  - `tasks/postenhancement/backend/ANNRPT-QA-AMOUNT-SPEC-01.md`
- verification:
  - `./scripts/task_validate.sh ANNRPT-QA-AMOUNT-SPEC-01`

## Exact Closure

- freeze `RPT-ANN` payable / official-paid / client-received grouped amount semantics only

## Explicit Non-closure

- no product implementation
- no success-rate semantics
- no chart / export
- no closure update
