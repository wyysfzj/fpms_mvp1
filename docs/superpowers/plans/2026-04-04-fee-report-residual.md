# FEERPT-RESIDUAL-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `residual decomposition after implemented first-round slice`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `FEERPT-RESIDUAL-01` | main thread | `docs/superpowers/specs/2026-04-04-fee-report-residual-design.md`, `docs/superpowers/plans/2026-04-04-fee-report-residual.md`, `tasks/postenhancement/backend/FEERPT-RESIDUAL-01.md`, `tasks/postenhancement/backend/FEERPT-QA-RESIDUAL-01.md` | Depends on current `RPT-FEE` product evidence and existing `FEERPT-*` artifacts | Freeze `RPT-FEE` residual capability map and recommend one next implementation slice | No product implementation, no re-close of first-round fee report, no chart/export/trend implementation |
| `FEERPT-QA-RESIDUAL-01` | monitor / main thread | `artifacts/FEERPT-RESIDUAL-01/**`, `artifacts/FEERPT-QA-RESIDUAL-01/**`, `tasks/postenhancement/backend/FEERPT-QA-RESIDUAL-01.md` | Runs after residual mapping closure | Audit evidence and close summary for the fee-report residual map | No product-code changes |

## First Follow-up Recommendation

- `FEERPT-AGGREGATE-01`
  - grouped `client_amounts + case_type_amounts + country_amounts`
  - no agent income and no billed/received/unpaid semantics in the same slice

## Serialized Shared-file Decisions

- This wave is doc-only; no FE/BE product shared files are touched
- The next implementation slice should serialize:
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/fees/service.py`
  - `backend/app/modules/fees/schemas.py`
  - `frontend/src/api/fees.ts`
  - `frontend/src/api/fees.types.ts`
  - `frontend/src/modules/fees/pages/FeeDraftList.vue`

## Verification

- `./scripts/task_validate.sh FEERPT-RESIDUAL-01`
- `./scripts/task_validate.sh FEERPT-QA-RESIDUAL-01`

## Done Definition

- first-round implemented slice is explicitly separated from residual spec gap
- residual buckets are explicit
- one first residual implementation slice is recommended
- required artifacts exist and both task gates pass
