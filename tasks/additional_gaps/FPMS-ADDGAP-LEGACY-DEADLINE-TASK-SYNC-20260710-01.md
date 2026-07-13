# FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 6
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

确认同一 legacy/missing 日期时，重算恰好一个 matching OA task 的 due/internal/reminders 并记录证据。

## Explicit Non-Closure

不支持改变已确认日期，不触碰 grant task，不在零/多任务时猜测。

## Dependencies

- `FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_addgap_legacy_deadline_task_sync.py`
- `tasks/additional_gaps/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01.md`
- `artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 Doc.Edit。
- Status codes/errors: 零/多 matching OA task 或冲突返回 409 且零写入；成功 200。
- Response envelope: 沿用 DocumentOut。
- SQLite: 精确选择并在单事务同步；SQLite-safe date math。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_legacy_deadline_task_sync.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/tasks/task_generation_service.py tests/test_addgap_legacy_deadline_task_sync.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/tasks/task_generation_service.py tests/test_addgap_legacy_deadline_task_sync.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/tasks/task_generation_service.py tests/test_addgap_legacy_deadline_task_sync.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_addgap_legacy_deadline_task_sync.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
