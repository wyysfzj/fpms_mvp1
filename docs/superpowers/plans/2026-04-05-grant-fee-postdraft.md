# GF-POSTDRAFT-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend wiring on top of existing backend state action`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `GF-POSTDRAFT-FE-01` | main thread | `frontend/src/api/grantFees.ts`, `frontend/src/api/grantFees.types.ts`, `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`, `docs/superpowers/specs/2026-04-05-grant-fee-postdraft-design.md`, `docs/superpowers/plans/2026-04-05-grant-fee-postdraft.md`, `tasks/postenhancement/frontend/GF-POSTDRAFT-FE-01.md` | Depends on existing backend `mark_done` authority and `GF-RESIDUAL-SPEC-01` being PASS | Make post-draft `mark_done` reachable from the current grant-fee worklist page | No backend changes, no bill/document/detail workflow |
| `GF-POSTDRAFT-QA-01` | main thread | `artifacts/GF-POSTDRAFT-FE-01/**`, `artifacts/GF-POSTDRAFT-QA-01/**`, `tasks/postenhancement/backend/GF-POSTDRAFT-QA-01.md` | Runs after FE wiring is complete | Audit evidence and exact close summary for the post-draft FE wave | No product-code changes |

## Verification

- `cd frontend && npm run lint -- src/api/grantFees.ts src/api/grantFees.types.ts src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh GF-POSTDRAFT-FE-01`
- `./scripts/task_validate.sh GF-POSTDRAFT-QA-01`

## Done Definition

- `DRAFT_GENERATED` rows expose a real `标记完成` action
- completion success refreshes the current worklist state
- no backend code is changed
- required artifacts exist and both task gates pass
