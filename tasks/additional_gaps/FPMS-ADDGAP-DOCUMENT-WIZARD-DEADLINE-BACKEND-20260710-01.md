# FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01

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

wizard schemas/service 接受并逐行保存 structured due/source/write-status。

## Explicit Non-Closure

不实现前端字段，不改变模板列表分页，不允许 LEGACY_UNVERIFIED 写入。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01`

## Allowed Files

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_document_wizard_deadline_backend.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 Doc.Create。
- Status codes/errors: 成功沿用 wizard 201/既有合同；shape 422；业务 400；缺确认/配置 409 且原子回滚。
- Response envelope: 沿用 wizard 结果包络。
- SQLite: 逐行保存仍在受控事务内，不依赖 RETURNING。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_wizard_deadline_backend.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/service.py tests/test_addgap_document_wizard_deadline_backend.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/service.py tests/test_addgap_document_wizard_deadline_backend.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/service.py tests/test_addgap_document_wizard_deadline_backend.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_addgap_document_wizard_deadline_backend.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
