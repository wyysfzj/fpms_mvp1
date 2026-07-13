# FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01

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

原子服务按 request key/reason 创建或复用 replacement notice/task，并 supersede 旧 task。

## Explicit Non-Closure

不新增 API/UI，不允许普通文档创建隐式替换，不改变 workflow status 与 lineage_status 的分离。

## Dependencies

- 02, 22, 35–38

## Remaining Follow-Up Task IDs

- 40–44

## Allowed Files

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_grant_replacement_service.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（API 后续同时要求 GrantFeeTask.Write 与 Doc.Create）。
- Status codes/errors: 旧 task 不存在 404；业务 shape 400；语义/lineage/idempotency 冲突 409；成功幂等。
- Response envelope: 返回 composite replacement 所需实体。
- SQLite: 单事务、request key 唯一、flush 取 PK。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_replacement_service.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py app/modules/documents/service.py tests/test_addgap_grant_replacement_service.py && .venv/bin/ruff format app/modules/grant_fees/service.py app/modules/documents/service.py tests/test_addgap_grant_replacement_service.py && .venv/bin/ruff check app/modules/grant_fees/service.py app/modules/documents/service.py tests/test_addgap_grant_replacement_service.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/app/modules/documents/service.py backend/tests/test_addgap_grant_replacement_service.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
