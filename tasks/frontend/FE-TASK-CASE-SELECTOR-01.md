# FE-TASK-CASE-SELECTOR-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Replace the raw `case_id` input in `TaskCreate.vue` with a case selector backed by existing `getCases()`, while preserving the backend payload field as `case_id`.

## Explicit Non-Closure

This task does not change backend behavior, task APIs, worker/assignee selection, task templates, task generation, routing, or other raw-ID fields outside the task case selector.

## Remaining Follow-Up Task IDs

- PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01
- FE-TASK-WORKER-SELECTOR-01
- FE-CASE-RELATED-SELECTORS-01-SPLIT

## Allowed Files

- tasks/frontend/FE-TASK-CASE-SELECTOR-01.md
- frontend/src/modules/tasks/pages/TaskCreate.vue
- artifacts/FE-TASK-CASE-SELECTOR-01/**

## Verification Commands

- cd frontend && npm run typecheck
- cd frontend && npm run build
- rg -n "请选择案件|caseOptions|getCases|case_id" frontend/src/modules/tasks/pages/TaskCreate.vue
- ./scripts/task_validate.sh FE-TASK-CASE-SELECTOR-01

## Evidence Path

- artifacts/FE-TASK-CASE-SELECTOR-01/results.jsonl
- artifacts/FE-TASK-CASE-SELECTOR-01/summary.md
- artifacts/FE-TASK-CASE-SELECTOR-01/git/diff.patch
