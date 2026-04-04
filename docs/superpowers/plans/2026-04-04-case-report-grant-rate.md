# CASERPT-RATE-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `semantics freeze before report metric implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `CASERPT-RATE-SPEC-01` | main thread | `docs/superpowers/specs/2026-04-04-case-report-grant-rate-design.md`, `docs/superpowers/plans/2026-04-04-case-report-grant-rate.md`, `tasks/postenhancement/backend/CASERPT-RATE-SPEC-01.md`, `tasks/postenhancement/backend/CASERPT-QA-RATE-SPEC-01.md` | Depends on existing `RPT-CASE` residual map, current `Case.status` carrier, and trend prerequisite conclusion | Freeze grant-rate numerator/denominator semantics and decide whether rate metrics are implementation-ready | No product implementation, no trend work, no close update |
| `CASERPT-QA-RATE-SPEC-01` | monitor / main thread | `artifacts/CASERPT-RATE-SPEC-01/**`, `artifacts/CASERPT-QA-RATE-SPEC-01/**`, `tasks/postenhancement/backend/CASERPT-QA-RATE-SPEC-01.md` | Runs after semantics-freeze closure | Audit evidence and close summary for the grant-rate semantics wave | No product-code changes |

## Follow-up Recommendation

- `CASERPT-RATE-01`
  - add `granted_count`
  - add `grant_rate`
  - add `terminated_count`
  - add `invalidated_count`
  - add `in_prosecution_count`
  - no trend reporting in the same slice

## Serialized Shared-file Decisions

- This wave is doc-only; no FE/BE product shared files are touched
- The follow-up implementation slice should serialize:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/modules/cases/pages/CaseList.vue`

## Verification

- `./scripts/task_validate.sh CASERPT-RATE-SPEC-01`
- `./scripts/task_validate.sh CASERPT-QA-RATE-SPEC-01`

## Done Definition

- grant-rate numerator semantics are explicit
- denominator set and excluded statuses are explicit
- implementation readiness is decided without hand-waving
- required artifacts exist and both task gates pass
