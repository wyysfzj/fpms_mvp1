# FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 2
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

文档创建及其必需的任务/授权副作用在单一事务中全部提交或全部回滚。

## Explicit Non-Closure

不改变副作用业务语义，不新增文档类型，不修复其他事务边界。

## Dependencies

Wave 0 planning gate：`FPMS-ADDGAP-WAVE0-CONTRACT-FREEZE-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_create_atomicity.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 Doc.Create，必须以函数参数 Depends 注入。
- Status codes/errors: 成功沿用 POST 201；业务/配置冲突 409 时不得残留文档或副作用。
- Response envelope: 沿用 DocumentOut 响应包络。
- SQLite: 短事务；不依赖 RETURNING；flush 后取主键。
- Simplified Chinese UI: N/A（不得引入 UI 文本）。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_create_atomicity.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_create_atomicity.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_create_atomicity.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_create_atomicity.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_create_atomicity.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
