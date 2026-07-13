# FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01

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

POST document 接受 write-status、due、source 字段并持久化 canonical structured deadline。

## Explicit Non-Closure

不实现普通更新/影响预览/wizard/UI，不允许写入 LEGACY_UNVERIFIED。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`
- `FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01`

## Allowed Files

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_create_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: Doc.Create，函数参数 Depends 注入。
- Status codes/errors: POST 201；shape 422；cross-field 400；缺确认/配置或冲突 409。
- Response envelope: 既有 DocumentOut，含新增 read projection。
- SQLite: 与 Task 02 同一事务；不依赖 RETURNING。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_create_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_create_api.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_create_api.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_create_api.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_create_api.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
