# FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 7
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

新增 POST /grant-fee-tasks/{task_id}/replacement-notice，接受 nested document/reason/idempotency key 并返回 composite existing/new 结果。

## Explicit Non-Closure

不修改 replacement service 规则，不新增第二端点，不重接已接 router。

## Dependencies

- 39

## Remaining Follow-Up Task IDs

- 41
- 44

## Allowed Files

- `backend/app/modules/grant_fees/schemas.py`
- `backend/app/modules/grant_fees/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_grant_replacement_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: GrantFeeTask.Write 与 Doc.Create，均以函数参数 Depends 注入。
- Status codes/errors: POST 200；404 old task；400 business shape；409 semantics/lineage/idempotency；422 payload。
- Response envelope: GrantFeeTaskReplacementNoticeOut，明确 existing/new，不发明外层 envelope。
- SQLite: 调用原子 SQLite-safe service。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_replacement_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/schemas.py app/modules/grant_fees/api.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_grant_replacement_api.py && .venv/bin/ruff format app/modules/grant_fees/schemas.py app/modules/grant_fees/api.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_grant_replacement_api.py && .venv/bin/ruff check app/modules/grant_fees/schemas.py app/modules/grant_fees/api.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_grant_replacement_api.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/api.py backend/tests/test_addgap_grant_replacement_api.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
