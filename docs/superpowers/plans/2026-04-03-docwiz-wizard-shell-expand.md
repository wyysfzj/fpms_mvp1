# DOCWIZ-WIZARD-SHELL-EXPAND-01 Plan

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `frontend shell implementation before step-specific logic`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-frontend-heavy-story`

## Batch Manifest

| Task ID | Owner | Allowlist | Dependency Notes | Exact Closure Slice | Explicit Non-closure |
|---|---|---|---|---|---|
| `DOCWIZ-WIZARD-SHELL-EXPAND-01` | main thread | `frontend/src/modules/documents/pages/DocumentWizard.vue`, `docs/superpowers/specs/2026-04-03-docwiz-wizard-shell-expand-design.md`, `docs/superpowers/plans/2026-04-03-docwiz-wizard-shell-expand.md` | Must serialize ownership of `DocumentWizard.vue` before any Step3/4/5 implementation story starts | Expand the 2-step wizard shell into a 5-step frontend shell with placeholders | No Step 3/4/5 business logic, no backend patch, no API/types change |
| `DOCWIZ-QA-WIZARD-SHELL-01` | monitor / main thread | `artifacts/DOCWIZ-WIZARD-SHELL-EXPAND-01/**`, `artifacts/DOCWIZ-QA-WIZARD-SHELL-01/**`, `tasks/postenhancement/frontend/DOCWIZ-QA-WIZARD-SHELL-01.md` | Runs after shell expansion implementation | Audit evidence and close summary for wizard shell expansion | No product behavior outside the shell slice |

## Verification

- `cd frontend && npm run lint -- src/modules/documents/pages/DocumentWizard.vue`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCWIZ-WIZARD-SHELL-EXPAND-01`
- `./scripts/task_validate.sh DOCWIZ-QA-WIZARD-SHELL-01`

## Done Definition

- Wizard shell shows 5 steps
- Step 3/4/5 placeholder panels exist
- Step 1/2 current behavior is preserved
- Required artifacts exist and both task gates pass
