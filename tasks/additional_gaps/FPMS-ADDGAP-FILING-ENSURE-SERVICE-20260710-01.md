# FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01

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

按案件 resolve/create 一个初始化 filing package：先复用，仅 NOT_FILED 可新建，唯一键竞争后重读胜者。

## Explicit Non-Closure

不新增 API 或页面入口，不创建 OA package，不更改 filing checklist 业务项。

## Dependencies

`FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01`

## Allowed Files

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_filing_ensure_service.py`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（服务由 API 注入 OfficialWorkflow.Update）。
- Status codes/errors: 缺资源 404、状态不允许/身份冲突 409；成功返回既有 package。
- Response envelope: 返回既有 filing package schema 所需实体。
- SQLite: 依赖 DB 唯一键处理竞争；短事务，不依赖 RETURNING。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_filing_ensure_service.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_filing_ensure_service.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_filing_ensure_service.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_filing_ensure_service.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_filing_ensure_service.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
