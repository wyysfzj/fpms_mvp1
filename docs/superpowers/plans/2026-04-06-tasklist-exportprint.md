# TASKLIST-EXPORTPRINT-SPEC-01 Plan

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: low
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

- P0-prereq-heavy-story

## Result Shape

- spec/decomposition freeze only
- no implementation in this task

## Batch Manifest

### Wave 1

- task id: `TASKLIST-EXPORTPRINT-SPEC-01`
  - owner: main thread
  - task file: `tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-SPEC-01.md`
  - exact closure slice: freeze decomposition authority, runbook choice, and first implementation sequence for `FR-DL-09` list-level export/print residual family
  - explicit non-closure: no product-code changes, no close update
  - allowlist:
    - `docs/superpowers/specs/2026-04-06-tasklist-exportprint-design.md`
    - `docs/superpowers/plans/2026-04-06-tasklist-exportprint.md`
    - `tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-SPEC-01.md`
    - `tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-QA-PLAN-01.md`
  - verification:
    - `./scripts/evidence_run.sh TASKLIST-EXPORTPRINT-SPEC-01 lint test -f docs/superpowers/specs/2026-04-06-tasklist-exportprint-design.md -a -f docs/superpowers/plans/2026-04-06-tasklist-exportprint.md -a -f tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-SPEC-01.md -a -f tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-QA-PLAN-01.md`
    - `./scripts/task_validate.sh TASKLIST-EXPORTPRINT-SPEC-01`
  - evidence path:
    - `artifacts/TASKLIST-EXPORTPRINT-SPEC-01/**`
  - remaining follow-up task ids:
    - `TASKLIST-EXPORT-BE-01`
    - `TASKLIST-PRINT-BE-01`
    - `TASKLIST-FE-01`
    - `TASKSPECIAL-EXPORTPRINT-BE-01`
    - `TASKSPECIAL-FE-01`
    - `TASKLIST-EXPORTPRINT-QA-01`

- task id: `TASKLIST-EXPORTPRINT-QA-PLAN-01`
  - owner: main thread
  - task file: `tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-QA-PLAN-01.md`
  - exact closure slice: audit the spec/decomposition wave evidence and task gate
  - explicit non-closure: no product-code changes, no close update
  - allowlist:
    - `tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-QA-PLAN-01.md`
    - `artifacts/TASKLIST-EXPORTPRINT-SPEC-01/**`
    - `artifacts/TASKLIST-EXPORTPRINT-QA-PLAN-01/**`
  - verification:
    - `./scripts/evidence_run.sh TASKLIST-EXPORTPRINT-QA-PLAN-01 lint test -f tasks/postenhancement/backend/TASKLIST-EXPORTPRINT-QA-PLAN-01.md -a -f artifacts/TASKLIST-EXPORTPRINT-SPEC-01/summary.md -a -f artifacts/TASKLIST-EXPORTPRINT-SPEC-01/results.jsonl`
    - `./scripts/task_validate.sh TASKLIST-EXPORTPRINT-QA-PLAN-01`
  - evidence path:
    - `artifacts/TASKLIST-EXPORTPRINT-QA-PLAN-01/**`
  - remaining follow-up task ids:
    - `TASKLIST-EXPORT-BE-01`
    - `TASKLIST-PRINT-BE-01`
    - `TASKLIST-FE-01`
    - `TASKSPECIAL-EXPORTPRINT-BE-01`
    - `TASKSPECIAL-FE-01`
    - `TASKLIST-EXPORTPRINT-QA-01`

## Shared-file Serialization Decisions

- no product shared files are touched in this spec wave
- future implementation waves must serialize:
  - `backend/app/modules/tasks/api.py`
  - `backend/app/modules/tasks/service.py`
  - `backend/app/modules/tasks/schemas.py`
  - `frontend/src/api/tasks.ts`
  - `frontend/src/api/tasks.types.ts`
  - `frontend/src/modules/tasks/pages/TaskList.vue`
  - `frontend/src/modules/tasks/pages/TaskSpecialSearch.vue`
  - `backend/tests/test_task_special_search_api.py`

## Future Execution Order Recommendation

Recommended serialized implementation order:

1. `TASKLIST-EXPORT-BE-01`
2. `TASKLIST-FE-01`
3. `TASKLIST-PRINT-BE-01`
4. `TASKSPECIAL-EXPORTPRINT-BE-01`
5. `TASKSPECIAL-FE-01`
6. `TASKLIST-EXPORTPRINT-QA-01`

Reasoning:

- task-list export is the smallest truthful first slice
- task-list FE should only attach after the export contract is real
- print semantics should be frozen against the post-export shape
- special-search BE/FE should follow after task-list patterns are proven
- final QA should close the item-to-slice ledger only after all implementation slices pass
