# GF-NOTICE-DOC-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `cross-module FE/BE document-generation prerequisite freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `GF-NOTICE-DOC-SPEC-01` | main thread | `docs/superpowers/specs/2026-04-05-grant-fee-notice-generation-design.md`, `docs/superpowers/plans/2026-04-05-grant-fee-notice-generation.md`, `tasks/postenhancement/backend/GF-NOTICE-DOC-SPEC-01.md`, `tasks/postenhancement/backend/GF-QA-NOTICE-DOC-SPEC-01.md` | Depends on `GF-BATCH-INSTRUCTION-01` and existing documents/template render capabilities; must not stretch into real implementation | Freeze authority for real grant-fee notice document generation and the first implementation-ready minimal path | No product implementation, no reminder generation, no close update |
| `GF-QA-NOTICE-DOC-SPEC-01` | main thread | `artifacts/GF-NOTICE-DOC-SPEC-01/**`, `artifacts/GF-QA-NOTICE-DOC-SPEC-01/**`, `tasks/postenhancement/backend/GF-QA-NOTICE-DOC-SPEC-01.md` | Runs after spec closure | Audit evidence and close summary for the notice-generation authority freeze | No product-code changes |

## Execution Recommendation

- Notice-generation authority freeze only:
  - `GF-NOTICE-DOC-SPEC-01`
- First implementation slice after freeze:
  - `GF-NOTICE-DOC-01`
- Explicitly deferred in this wave:
  - reminder task generation
  - dispatch / envelope
  - bill / settlement semantics
  - detail/edit page

## Serialized Shared-file Decisions

- This wave is doc-only; no FE/BE product shared files are touched
- Future implementation must serialize ownership for:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/documents/service.py`
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Verification

- `./scripts/task_validate.sh GF-NOTICE-DOC-SPEC-01`
- `./scripts/task_validate.sh GF-QA-NOTICE-DOC-SPEC-01`

## Done Definition

- real grant-fee notice-generation authority is frozen
- first implementation slice recommendation is explicit
- write-back, template, lineage, and non-closure boundaries are explicit
- required artifacts exist and both task gates pass
