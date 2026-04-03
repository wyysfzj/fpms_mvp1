# DOCWIZ-STEP3-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `shared multi-lane residual contract before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP3-SPEC-01` | main thread | `docs/superpowers/specs/2026-04-03-docwiz-step3-deadline-linkage-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-step3-deadline-linkage.md` | Depends on Step1/2 representative slices and current wizard backend carrier inventory | Freeze Step 3 deadline linkage contract only | No Step 4/5, no dispatch/search/reporting, no implementation patch |
| `DOCWIZ-QA-STEP3-01` | monitor / main thread | `artifacts/DOCWIZ-STEP3-SPEC-01/**`, `artifacts/DOCWIZ-QA-STEP3-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP3-01.md` | Runs after spec/plan closure | Audit evidence and close summary for Step 3 contract freeze | No product-code changes |

## Verification

- `./scripts/task_validate.sh DOCWIZ-STEP3-SPEC-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP3-01`

## Done Definition

- Step 3 contract is frozen as a standalone residual slice
- Step 4 and later document capabilities remain explicitly deferred
- Required artifacts exist and both task gates pass
