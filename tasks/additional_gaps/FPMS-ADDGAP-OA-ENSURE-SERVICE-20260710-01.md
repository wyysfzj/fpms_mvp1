# FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01

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

每个可执行 IN 源文档 resolve/create 唯一 OA package，创建状态必须与 resolver 的 OA1/OA2 匹配。

## Explicit Non-Closure

不新增 API/UI，不处理收据，不完成 OA 任务。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`
- `FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-OA-RESOLVE-API-20260710-01`
- `FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`

## Allowed Files

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_oa_ensure_service.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（服务由 API 注入 OfficialWorkflow.Update）。
- Status codes/errors: 404 文档不存在；400 方向错误；409 状态/语义/身份冲突。
- Response envelope: 返回 OaReplyPackageOut 所需实体。
- SQLite: 使用 resolve_key 唯一性；竞争后重读；短事务。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_ensure_service.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_oa_ensure_service.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_oa_ensure_service.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_oa_ensure_service.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_oa_ensure_service.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
