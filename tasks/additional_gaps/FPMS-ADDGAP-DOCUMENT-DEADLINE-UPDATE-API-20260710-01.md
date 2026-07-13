# FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01

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

PUT document 可确认 missing/legacy 的同一日期，但普通编辑拒绝改变或清除已确认 due。

## Explicit Non-Closure

不提供正式 deadline override workflow，不实现 UI，不同步其他任务类型。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`

## Allowed Files

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_update_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: Doc.Edit，函数参数 Depends 注入。
- Status codes/errors: 成功 200；shape 422；cross-field 400；已确认 due 变更/清除 409。
- Response envelope: 既有 DocumentOut。
- SQLite: 单短事务，保留未知 extra_data。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_update_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_update_api.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_update_api.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_update_api.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_update_api.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
