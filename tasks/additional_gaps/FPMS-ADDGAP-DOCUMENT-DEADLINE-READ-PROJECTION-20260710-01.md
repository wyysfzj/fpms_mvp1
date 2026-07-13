# FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01

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

所有既有 `DocumentOut` 响应投影 structured due/source/read-status/description，同时保留 `extra_data`。

## Explicit Non-Closure

不接受写入、不同步任务、不修改数据库 schema。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01`

## Allowed Files

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_read_projection.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用各 Document.Read/Create/Edit 路由权限。
- Status codes/errors: GET/既有响应状态不变；读取 legacy 不报错并投影 LEGACY_UNVERIFIED。
- Response envelope: 扩展既有 DocumentOut，不新增 envelope。
- SQLite: 纯投影，SQLite-safe。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_read_projection.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_read_projection.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_read_projection.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_read_projection.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_read_projection.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
