# FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: medium
- be_fe_coupling: low
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Exact Closure Slice

Align `DocumentWizard.vue` user-facing copy and actions with `PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01`:

- preview steps are described as non-writing;
- Step 2 submit is clearly scoped as document-only registration;
- final Step 5 submit remains the primary full wizard write action.

## Explicit Non-Closure

This task does not change backend behavior, API wrappers, route definitions, menu configuration, raw-ID selectors, document rendering, task generation, fee generation, or attachment storage.

## Remaining Follow-Up Task IDs

- BE-FE-COMMISSION-QUERY-READINESS-01
- FE-COMMISSION-CASE-NO-FILTER-01
- FE-CASE-RELATED-SELECTORS-01-SPLIT

## Allowed Files

- tasks/frontend/FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01.md
- frontend/src/modules/documents/pages/DocumentWizard.vue
- artifacts/FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01/**

## Verification Commands

- cd frontend && npm run typecheck
- cd frontend && npm run build
- rg -n "仅登记文书|完成向导并提交|预览阶段不会写入|不会写入后续任务、费用或附件" frontend/src/modules/documents/pages/DocumentWizard.vue
- ./scripts/task_validate.sh FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01

## Evidence Path

- artifacts/FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01/results.jsonl
- artifacts/FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01/summary.md
- artifacts/FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01/git/diff.patch
