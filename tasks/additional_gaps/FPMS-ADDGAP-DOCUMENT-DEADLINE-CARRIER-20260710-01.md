# FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01

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

提供 canonical extra_data parser/merger，保留未知 JSON 和 legacy text，并只读投影 LEGACY_UNVERIFIED。

## Explicit Non-Closure

不修改 API/schema/UI，不生成任务，不覆盖未知键。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01`
- `FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01`
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01`
- `FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`
- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`
- `FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`
- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`

## Allowed Files

- `backend/app/modules/documents/extra_data.py`
- `backend/tests/test_addgap_document_deadline_carrier.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（纯内部组件）。
- Status codes/errors: 畸形 shape 由调用方映射 422，cross-field 业务错误映射 400。
- Response envelope: N/A。
- SQLite: 数据仍以现有 TEXT/JSON 兼容格式保存；不引入 JSONB。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_carrier.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/extra_data.py tests/test_addgap_document_deadline_carrier.py && .venv/bin/ruff format app/modules/documents/extra_data.py tests/test_addgap_document_deadline_carrier.py && .venv/bin/ruff check app/modules/documents/extra_data.py tests/test_addgap_document_deadline_carrier.py`
- Scope: `git diff --check -- backend/app/modules/documents/extra_data.py backend/tests/test_addgap_document_deadline_carrier.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
