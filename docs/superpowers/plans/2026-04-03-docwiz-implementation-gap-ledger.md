# DOCWIZ-IMPL-LEDGER-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `spec-gap ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-IMPL-LEDGER-01` | main thread | `docs/superpowers/specs/2026-04-03-docwiz-implementation-gap-ledger-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-implementation-gap-ledger.md` | Depends on corrected `#8` baseline and existing Step1/2 + Step3/4/5 evidence | Freeze strict spec-gap ledger and implementation-slice mapping for `#8` | No product implementation, no closure update, no dispatch/search/reporting work |
| `DOCWIZ-QA-IMPL-LEDGER-01` | monitor / main thread | `artifacts/DOCWIZ-IMPL-LEDGER-01/**`, `artifacts/DOCWIZ-QA-IMPL-LEDGER-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-IMPL-LEDGER-01.md` | Runs after ledger closure | Audit evidence and close summary for the strict gap ledger | No product-code changes |

## Verification

- `./scripts/task_validate.sh DOCWIZ-IMPL-LEDGER-01`
- `./scripts/task_validate.sh DOCWIZ-QA-IMPL-LEDGER-01`

## Done Definition

- `#8` strict spec-gap ledger exists
- `Implemented / Contract Frozen Only / Missing` classification is explicit
- implementation buckets are mapped without starting code work
- Required artifacts exist and both task gates pass
