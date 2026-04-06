# TASKLIST-EXPORTPRINT-SPEC-01

## Story Shape Classification

- shared_file_density: high
- prereq_dependency_density: low
- be_fe_coupling: high
- evidence_cost: high

## chosen_runbook

- P0-prereq-heavy-story

## Problem Statement

`docs/FPMS_SPEC2_Final_Audit_Excluding_Document_Generation_20260406.md` freezes one residual family for Module 3: `4.9 / FR-DL-09` still lacks list-level export/print closure for:

- 我的任务列表
- 监督任务列表
- 专项检索结果

Current product behavior provides:

- real `GET /tasks` list filtering
- real `GET /tasks/special/search` special-search filtering
- real single-task `GET /tasks/{task_id}/print`

Current product behavior does **not** provide:

- list-level export endpoint
- list-level print endpoint / printable payload
- frontend export/print user path on `TaskList.vue`
- frontend export/print user path on `TaskSpecialSearch.vue`

This is therefore a residual family requiring decomposition, not a single implementation slice.

## Assumptions

- no schema or migration prerequisite is required
- existing task list carriers already hold the fields needed for first-round list export/print
- single-task print does not satisfy `FR-DL-09`
- real closure requires backend contract + frontend user path + targeted tests
- this batch excludes document-generation-only scope; first-round print may use printable HTML instead of docx generation if that is the smallest truthful product path

## Scope

- freeze `FR-DL-09` residual-family decomposition
- define exact closure slices for list-level export/print
- define shared-file serialization rules
- define first implementation sequence

## Non-scope

- no task CRUD changes
- no task template changes
- no dashboard reminder changes
- no single-task detail print rewrite
- no other Module 3 residuals
- no review / mitigation close-decision update in this spec wave

## Current Implementation Inventory

### Implemented

- `GET /tasks`
  - file: `backend/app/modules/tasks/api.py`
  - service: `backend/app/modules/tasks/service.py::list_tasks`
- `GET /tasks/special/search`
  - file: `backend/app/modules/tasks/api.py`
  - service: `backend/app/modules/tasks/service.py::list_special_search_tasks`
- FE task list page
  - file: `frontend/src/modules/tasks/pages/TaskList.vue`
- FE special-search page
  - file: `frontend/src/modules/tasks/pages/TaskSpecialSearch.vue`
- FE task api contracts
  - file: `frontend/src/api/tasks.ts`
  - file: `frontend/src/api/tasks.types.ts`
- single-task print only
  - file: `backend/app/modules/tasks/api.py`
  - path: `GET /tasks/{task_id}/print`
  - helper: `TaskSheetContextBuilder`
  - helper: `DocxRenderer`

### Missing

- list-level export contract for `GET /tasks` result set
- list-level print contract for `GET /tasks` result set
- frontend export/print controls for task list page
- list-level export/print contract for special-search result set
- frontend export/print controls for special-search page
- targeted tests for list-level export/print

## Decomposition Recommendation

Recommended atomic slices:

1. `TASKLIST-EXPORTPRINT-SPEC-01`
   - exact closure slice: freeze decomposition authority for Module 3 list-level export/print residual family
   - explicit non-closure: no product-code changes
2. `TASKLIST-EXPORT-BE-01`
   - exact closure slice: add list-level export contract for `GET /tasks` filtered result set
   - explicit non-closure: no print, no special-search, no FE changes
3. `TASKLIST-PRINT-BE-01`
   - exact closure slice: add list-level printable payload / print contract for `GET /tasks` filtered result set
   - explicit non-closure: no export, no special-search, no FE changes
4. `TASKLIST-FE-01`
   - exact closure slice: connect task-list export/print user paths for 我的任务 / 监督任务 based on existing filters
   - explicit non-closure: no special-search page changes
5. `TASKSPECIAL-EXPORTPRINT-BE-01`
   - exact closure slice: add export/print contract for `GET /tasks/special/search` result set
   - explicit non-closure: no task-list FE path, no task CRUD changes
6. `TASKSPECIAL-FE-01`
   - exact closure slice: connect special-search export/print user paths
   - explicit non-closure: no task-list page changes
7. `TASKLIST-EXPORTPRINT-QA-01`
   - exact closure slice: audit evidence, scope, task gates, and item-to-slice ledger for the residual family
   - explicit non-closure: no product-code changes

## Backend Export/Print Semantics

First-round authority:

- export should be a real downloadable file response
- print should be a real printable user path, not a placeholder button
- first-round export may use CSV if Excel generation is not already reusable in the tasks module and if the chosen task explicitly states the exact scope
- first-round print may use printable HTML if that is the smallest truthful list-level print path

Required behavioral rule:

- backend export/print must honor the same filters already supported by the source list
- task list view must preserve `status`, `client_id`, `as=worker|supervisor`, paging-independent full-result export/print semantics
- special-search view must preserve current special-search filters

## Frontend User-path Semantics

- `TaskList.vue` must expose real export and print actions for the current filtered view
- `TaskSpecialSearch.vue` must expose real export and print actions for the current filtered view
- all user-facing text must remain Simplified Chinese
- disabled or placeholder controls do not count toward closure

## Shared-file / Ownership Analysis

Serialized shared files:

- `backend/app/modules/tasks/api.py`
- `backend/app/modules/tasks/service.py`
- `backend/app/modules/tasks/schemas.py`
- `frontend/src/api/tasks.ts`
- `frontend/src/api/tasks.types.ts`
- `frontend/src/modules/tasks/pages/TaskList.vue`
- `frontend/src/modules/tasks/pages/TaskSpecialSearch.vue`
- `backend/tests/test_task_special_search_api.py`
- `backend/tests/test_tasks_api.py` if touched
- any shared helper extracted from existing single-task print chain

## API / Service Impact

Expected contract growth:

- task-list export endpoint
- task-list print endpoint
- special-search export endpoint
- special-search print endpoint

Service impact should prefer:

- reuse of existing list query carriers
- output-specific helper functions instead of schema changes

## Test Plan

- targeted backend tests for export response status, content type, and filtered dataset
- targeted backend tests for print response status and filtered dataset
- permission tests for export/print endpoints
- FE lint/typecheck
- QA gate validation for all task ids

## SQLite / Phase Compatibility

- SQLite compatible
- no schema / migration changes
- no new persistence carrier required

## Risks / Blockers

- scope drift into task CRUD / dashboard / template maintenance
- treating single-task print as representative closure
- mixing export and print semantics into one oversized task
- touching shared FE/BE task files concurrently

## Exact Non-closure Boundary

- no task CRUD
- no task template
- no dashboard reminder
- no single-task print rewrite
- no close-decision update in this wave
- no other Module 3 residuals

## First Implementation Recommendation

After this spec wave, the most natural implementation entry is:

- `TASKLIST-EXPORT-BE-01`

Reason:

- task-list export is the narrowest real list-level closure slice
- it reuses the already mature `GET /tasks` filter carrier
- it avoids immediately coupling into print renderer decisions
