# FEERPT-INCOME-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `semantics freeze before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

### Task 1

- task: `tasks/postenhancement/backend/FEERPT-INCOME-SPEC-01.md`
- owner: `main thread`
- allowlist:
  - `docs/superpowers/specs/2026-04-04-fee-report-agent-income-design.md`
  - `docs/superpowers/plans/2026-04-04-fee-report-agent-income.md`
  - `tasks/postenhancement/backend/FEERPT-INCOME-SPEC-01.md`
- verification:
  - `./scripts/task_validate.sh FEERPT-INCOME-SPEC-01`

### Task 2

- task: `tasks/postenhancement/backend/FEERPT-QA-INCOME-SPEC-01.md`
- owner: `main thread`
- allowlist:
  - `docs/superpowers/specs/2026-04-04-fee-report-agent-income-design.md`
  - `docs/superpowers/plans/2026-04-04-fee-report-agent-income.md`
  - `tasks/postenhancement/backend/FEERPT-QA-INCOME-SPEC-01.md`
- verification:
  - `./scripts/task_validate.sh FEERPT-QA-INCOME-SPEC-01`

## Exact Closure

- freeze `RPT-FEE` agent-attributed service-income semantics only

## Explicit Non-closure

- no product implementation
- no billed / received / unpaid semantics
- no trend reporting
- no closure update
