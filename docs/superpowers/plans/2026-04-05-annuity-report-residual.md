# ANNRPT-RESIDUAL-01 Plan

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
| `ANNRPT-RESIDUAL-01` | main thread | `docs/superpowers/specs/2026-04-05-annuity-report-residual-design.md`, `docs/superpowers/plans/2026-04-05-annuity-report-residual.md`, `tasks/postenhancement/backend/ANNRPT-RESIDUAL-01.md`, `tasks/postenhancement/backend/ANNRPT-QA-RESIDUAL-01.md` | Depends on current `RPT-ANN` product evidence and existing `ANNRPT-*` artifacts | Freeze `RPT-ANN` residual capability map and recommend one next implementation/prerequisite slice | No product implementation, no re-close of first-round annuity report, no chart/export/success-rate implementation |
| `ANNRPT-QA-RESIDUAL-01` | main thread | `artifacts/ANNRPT-RESIDUAL-01/**`, `artifacts/ANNRPT-QA-RESIDUAL-01/**`, `tasks/postenhancement/backend/ANNRPT-QA-RESIDUAL-01.md` | Runs after residual mapping closure | Audit evidence and close summary for the annuity-report residual map | No product-code changes |

## First Follow-up Recommendation

- `ANNRPT-AMOUNT-SPEC-01`
  - freeze grouped client/country/year payable / official-paid / client-received semantics
  - no success-rate semantics in the same slice

## Serialized Shared-file Decisions

- This wave is doc-only; no FE/BE product shared files are touched
- The next implementation/prerequisite slice should serialize:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
  - `backend/app/modules/annuity/schemas.py`
  - `frontend/src/api/annuity.ts`
  - `frontend/src/api/annuity.types.ts`
  - `frontend/src/modules/annuity/pages/AnnuityTaskList.vue`

## Verification

- `./scripts/task_validate.sh ANNRPT-RESIDUAL-01`
- `./scripts/task_validate.sh ANNRPT-QA-RESIDUAL-01`

## Done Definition

- first-round implemented slice is explicitly separated from residual spec gap
- residual buckets are explicit
- one first residual prerequisite/implementation slice is recommended
- required artifacts exist and both task gates pass
