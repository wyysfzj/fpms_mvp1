# GF-RESIDUAL-SPEC-01 Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `residual decomposition after implemented first-round workflow`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `GF-RESIDUAL-SPEC-01` | main thread | `docs/superpowers/specs/2026-04-05-grant-fee-residual-workflow-design.md`, `docs/superpowers/plans/2026-04-05-grant-fee-residual-workflow.md`, `tasks/postenhancement/backend/GF-RESIDUAL-SPEC-01.md` | Depends on `GFPRE-*`, `GFSM-*`, `GFWL-*`, and `GFDRAFT-*` all being PASS and on the current `#15` partially-closed review baseline | Freeze strict residual workflow map for `#15` and recommend the first post-draft story | No product implementation, no close update, no bill/document/detail work |
| `GF-QA-RESIDUAL-SPEC-01` | main thread | `artifacts/GF-RESIDUAL-SPEC-01/**`, `artifacts/GF-QA-RESIDUAL-SPEC-01/**`, `tasks/postenhancement/backend/GF-QA-RESIDUAL-SPEC-01.md` | Runs after residual mapping is complete | Audit evidence and exact close summary for the grant-fee residual-spec wave | No product-code changes |

## Verification

- `./scripts/task_validate.sh GF-RESIDUAL-SPEC-01`
- `./scripts/task_validate.sh GF-QA-RESIDUAL-SPEC-01`

## Done Definition

- `#15` residual workflow map is explicit
- first-round implemented slices are preserved, not reopened
- one first residual follow-up story is recommended explicitly
- required artifacts exist and both task gates pass
