# FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01

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

新增无 body 的 filing resolve POST，返回 existing-or-created package 的既有响应包络。

## Explicit Non-Closure

不修改 service 规则，不新增 GET body，不增加路由重复 wiring。

## Dependencies

`FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01` 已 PASS。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`

## Allowed Files

- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/tests/test_addgap_filing_resolve_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: OfficialWorkflow.Update，必须作为函数参数 Depends 注入。
- Status codes/errors: POST 200；404 案件不存在；409 状态/身份冲突；422 路径校验。
- Response envelope: 沿用 filing package 输出模型，不发明新 envelope。
- SQLite: N/A（调用 SQLite-safe service）。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_filing_resolve_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_filing_resolve_api.py && .venv/bin/ruff format app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_filing_resolve_api.py && .venv/bin/ruff check app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_filing_resolve_api.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/api.py backend/app/modules/official_workflows/schemas.py backend/tests/test_addgap_filing_resolve_api.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
