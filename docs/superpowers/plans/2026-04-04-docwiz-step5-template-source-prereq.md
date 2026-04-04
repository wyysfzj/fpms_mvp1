# DOCWIZ-STEP5-PREREQ-01 Plan

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `high`
- `be_fe_coupling`: `shared prerequisite freeze before Step 5 final submit integration`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-STEP5-PREREQ-01` | main thread | `docs/superpowers/specs/2026-04-04-docwiz-step5-template-source-prereq-design.md`, `docs/superpowers/plans/2026-04-04-docwiz-step5-template-source-prereq.md`, `tasks/postenhancement/backend/DOCWIZ-STEP5-PREREQ-01.md` | Depends on existing Step 5 preview implementation and evidence of missing template-source mapping | Freeze Step 5 final-submit blocker and prerequisite recommendation only | No product implementation, no schema/API patch |
| `DOCWIZ-QA-STEP5-PREREQ-01` | main thread | `artifacts/DOCWIZ-STEP5-PREREQ-01/**`, `artifacts/DOCWIZ-QA-STEP5-PREREQ-01/**`, `tasks/postenhancement/backend/DOCWIZ-QA-STEP5-PREREQ-01.md` | Runs after prerequisite freeze task artifacts exist | Audit prerequisite-freeze evidence and close summary | No product-code change |

## Verification

- `./scripts/task_validate.sh DOCWIZ-STEP5-PREREQ-01`
- `./scripts/task_validate.sh DOCWIZ-QA-STEP5-PREREQ-01`

## Done Definition

- Blocker is explicitly frozen
- `DOCWIZ-STEP5-FINAL-SUBMIT-01` is marked non-implementable under current carriers
- Next prerequisite recommendation is explicit
- Required artifacts exist and all task gates pass
