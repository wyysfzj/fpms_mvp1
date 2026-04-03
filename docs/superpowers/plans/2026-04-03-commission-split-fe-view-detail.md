# COMMSPLIT-FE-VIEW-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend implementation on top of frozen backend semantics`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `COMMSPLIT-FE-VIEW-01` | frontend worker | `frontend/src/modules/cases/pages/CaseDetail.vue` | Depends on frozen `COMMSPLIT-FE-01` ownership decision | Add read-only `代理人分摊` detail block and promote `agent_splits` as split display carrier | No editing, no settlement exposure, no list exposure, no backend/API/types changes |
| `COMMSPLIT-QA-09` | monitor / main thread | `artifacts/COMMSPLIT-FE-VIEW-01/**`, `artifacts/COMMSPLIT-QA-09/**`, `tasks/postenhancement/frontend/COMMSPLIT-QA-09.md` | Runs after implementation and verification complete | Audit evidence, validate task gate, record close summary | No product-code changes outside audit evidence |

## Execution Steps

1. Update `CaseDetail.vue` only.
2. Add a read-only `代理人分摊` block driven by `caseData.agent_splits`.
3. Keep existing `代理人分配` block intact as context.
4. Run task-scoped frontend verification.
5. Generate required artifacts and run `COMMSPLIT-QA-09`.

## Verification

- `cd frontend && npm run lint -- src/modules/cases/pages/CaseDetail.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh COMMSPLIT-FE-VIEW-01`
- `./scripts/task_validate.sh COMMSPLIT-QA-09`

## Done Definition

- `CaseDetail.vue` shows a Simplified Chinese `代理人分摊` read-only section when `agent_splits` exist.
- Display includes agent, role, and share ratio.
- No edit controls are introduced.
- No shared API/types files are modified.
- Required artifacts exist and both task gates pass.
