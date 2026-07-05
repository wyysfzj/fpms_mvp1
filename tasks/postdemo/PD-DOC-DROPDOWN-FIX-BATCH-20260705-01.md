# PD-DOC-DROPDOWN-FIX-BATCH-20260705-01 — 上传/文书下拉不齐收口 batch

## Story Shape Classification

- shared_file_density: Medium. Task A and Task B both touch documents module, so execution must be serialized.
- prereq_dependency_density: Low. Existing `DocTemplate` and `DocAttachment` carriers already exist.
- be_fe_coupling: Medium. Task A is backend/catalog only; Task B couples backend upload API and frontend upload UI.
- evidence_cost: Medium. Requires backend targeted tests, frontend typecheck, and per-task gates.
- chosen_runbook: `P0-prereq-heavy-story`

## Closure

Coordinate the exact atomic tasks needed to close the demo feedback “上传文件下拉列表不齐”:

1. `tasks/postdemo/PD-DOC-OFFICIAL-NOTICE-CATALOG-20260705-01.md`
2. `tasks/postdemo/PD-DOC-ATTACHMENT-UPLOAD-ROLE-SELECT-20260705-01.md`
3. `tasks/postdemo/PD-DOC-DROPDOWN-FIX-FINAL-REGRESSION-20260705-01.md`

## Non-Closure

No CPC/OA direct submit, no RPA, no automatic signing, no automatic upload to official systems, no schema migration, and no broad document/workflow refactor.

## Execution Order

Wave 1:
- Task A: official notice/catalog seed and search.

Wave 2:
- Task B: attachment upload role and historical alias selection.

Wave 3:
- Task C: final batch close audit and regression evidence.

## Shared File Decisions

- `backend/app/modules/documents/service.py` is serialized because Task A may touch template search while Task B may rely on attachment metadata behavior.
- `frontend/src/api/documents.ts` is owned only by Task B.
- No two tasks run concurrently.

## Done Definition

- Each task has `artifacts/<TASK-ID>/results.jsonl`, `summary.md`, and `git/diff.patch`.
- Dirty baseline artifacts exist where required.
- Each task passes `./scripts/task_validate.sh <TASK-ID>`.
- Final audit maps customer feedback to task evidence and explicitly confirms that official notice catalog is not mixed into attachment role enum.

