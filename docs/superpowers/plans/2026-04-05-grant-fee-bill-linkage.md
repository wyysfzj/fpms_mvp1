# GF-BILL-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `semantics freeze before linkage implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `GF-BILL-SPEC-01` | main thread | `docs/superpowers/specs/2026-04-05-grant-fee-bill-linkage-design.md`, `docs/superpowers/plans/2026-04-05-grant-fee-bill-linkage.md`, `tasks/postenhancement/backend/GF-BILL-SPEC-01.md` | Depends on `GF-RESIDUAL-SPEC-01` and current generic billing carriers being present | Freeze grant-fee bill linkage authority and recommend one minimal follow-up story | No product implementation, no state-machine expansion, no receipt/payment semantics |
| `GF-QA-BILL-SPEC-01` | main thread | `artifacts/GF-BILL-SPEC-01/**`, `artifacts/GF-QA-BILL-SPEC-01/**`, `tasks/postenhancement/backend/GF-QA-BILL-SPEC-01.md` | Runs after semantics freeze is complete | Audit evidence and exact close summary for the grant-fee bill-linkage semantics wave | No product-code changes |

## Verification

- `./scripts/task_validate.sh GF-BILL-SPEC-01`
- `./scripts/task_validate.sh GF-QA-BILL-SPEC-01`

## Done Definition

- bill-linkage source-of-truth is explicit
- task-state non-expansion is explicit
- one first bill-linkage follow-up story is recommended
- required artifacts exist and both task gates pass
