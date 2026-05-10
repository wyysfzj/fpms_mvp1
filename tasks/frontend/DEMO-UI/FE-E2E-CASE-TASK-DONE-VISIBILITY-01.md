# FE-E2E-CASE-TASK-DONE-VISIBILITY-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: medium
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Make the case detail task tab visibly show generated OA reply tasks and their completed/write-off state using Simplified Chinese labels.

## Explicit Non-Closure

- Do not change backend task generation.
- Do not add new task mutation actions.
- Do not modify shared frontend API clients unless required by existing type mismatch.
- Do not change Skeleton Pack assets.

## Allowed Files

- `frontend/src/modules/cases/components/CaseTasksTab.vue`
- `tasks/frontend/DEMO-UI/FE-E2E-CASE-TASK-DONE-VISIBILITY-01.md`
- `artifacts/FE-E2E-CASE-TASK-DONE-VISIBILITY-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh FE-E2E-CASE-TASK-DONE-VISIBILITY-01 test /bin/zsh -lc 'cd frontend && npm run typecheck'
```

```bash
./scripts/evidence_run.sh FE-E2E-CASE-TASK-DONE-VISIBILITY-01 lint /bin/zsh -lc 'cd frontend && npm run lint -- src/modules/cases/components/CaseTasksTab.vue'
```

```bash
./scripts/evidence_run.sh FE-E2E-CASE-TASK-DONE-VISIBILITY-01 task_gate ./scripts/task_validate.sh FE-E2E-CASE-TASK-DONE-VISIBILITY-01
```

## Evidence Path

- `artifacts/FE-E2E-CASE-TASK-DONE-VISIBILITY-01/results.jsonl`
- `artifacts/FE-E2E-CASE-TASK-DONE-VISIBILITY-01/summary.md`
- `artifacts/FE-E2E-CASE-TASK-DONE-VISIBILITY-01/git/diff.patch`

## Remaining Follow-Up Task IDs

- None

