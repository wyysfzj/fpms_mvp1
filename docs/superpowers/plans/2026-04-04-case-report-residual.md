# CASERPT-RESIDUAL-01 Plan

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
| `CASERPT-RESIDUAL-01` | main thread | `docs/superpowers/specs/2026-04-04-case-report-residual-design.md`, `docs/superpowers/plans/2026-04-04-case-report-residual.md`, `tasks/postenhancement/backend/CASERPT-RESIDUAL-01.md`, `tasks/postenhancement/backend/CASERPT-QA-RESIDUAL-01.md` | Depends on current `RPT-CASE` product evidence and existing `CASERPT-*` artifacts | Freeze `RPT-CASE` residual capability map and recommend one next implementation slice | No product implementation, no re-close of first-round case report, no chart/export/trend implementation |
| `CASERPT-QA-RESIDUAL-01` | monitor / main thread | `artifacts/CASERPT-RESIDUAL-01/**`, `artifacts/CASERPT-QA-RESIDUAL-01/**`, `tasks/postenhancement/backend/CASERPT-QA-RESIDUAL-01.md` | Runs after residual mapping closure | Audit evidence and close summary for the case-report residual map | No product-code changes |

## First Follow-up Recommendation

- `CASERPT-AGGREGATE-01`
  - grouped `country_counts` + `agent_counts`
  - no grant-rate and no trend reporting in the same slice

## Serialized Shared-file Decisions

- This wave is doc-only; no FE/BE product shared files are touched
- The next implementation slice should serialize:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseList.vue`

## Verification

- `./scripts/task_validate.sh CASERPT-RESIDUAL-01`
- `./scripts/task_validate.sh CASERPT-QA-RESIDUAL-01`

## Done Definition

- first-round implemented slice is explicitly separated from residual spec gap
- residual buckets are explicit
- one first residual implementation slice is recommended
- required artifacts exist and both task gates pass
