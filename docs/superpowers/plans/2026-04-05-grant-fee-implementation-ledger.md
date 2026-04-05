# GF-LEDGER-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `workflow ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `GF-LEDGER-01` | main thread | `docs/superpowers/specs/2026-04-05-grant-fee-implementation-ledger-design.md`, `docs/superpowers/plans/2026-04-05-grant-fee-implementation-ledger.md`, `tasks/postenhancement/backend/GF-LEDGER-01.md`, `tasks/postenhancement/backend/GF-QA-LEDGER-01.md` | Depends on current `#15` refresh baseline, mitigation ledger entry, SPEC 5.7 evidence, and observed grant-fee workflow product evidence | Freeze strict grant-fee workflow implementation ledger and first implementation priority for `#15` | No product implementation, no close update, no bill/document generation, no settlement work |
| `GF-QA-LEDGER-01` | monitor / main thread | `artifacts/GF-LEDGER-01/**`, `artifacts/GF-QA-LEDGER-01/**`, `tasks/postenhancement/backend/GF-QA-LEDGER-01.md` | Runs after ledger closure | Audit evidence and close summary for the strict grant-fee workflow ledger | No product-code changes |

## Workflow Execution Recommendation

- Grant-fee workflow ledger only:
  - `GF-LEDGER-01`
- First residual slice eligible for implementation after ledger:
  - `GF-BATCH-INSTRUCTION-01`
- Explicitly deferred slices for this planning wave:
  - `GF-DOC-GEN`
  - `GF-DETAIL`
  - `GF-BILL-GEN`
  - `GF-SETTLEMENT`
  - any reminder/task generation

## Serialized Shared-file Decisions

- This wave is doc-only; no FE/BE product shared files are touched
- Future residual implementation must serialize shared ownership for:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## Verification

- `./scripts/task_validate.sh GF-LEDGER-01`
- `./scripts/task_validate.sh GF-QA-LEDGER-01`

## Done Definition

- `#15` strict workflow ledger exists
- slice-by-slice classification is explicit:
  - `Implemented`
  - `Partially Implemented`
  - `Contract/Plan Only`
  - `Missing`
- first implementation slice recommendation is explicit
- required artifacts exist and both task gates pass
