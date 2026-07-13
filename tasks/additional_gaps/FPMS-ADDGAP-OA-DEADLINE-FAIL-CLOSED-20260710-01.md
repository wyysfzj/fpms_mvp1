# FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01

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

- 可执行 OA task generation 必须使用 confirmed explicit due，绝不使用 task-template 天数 fallback。

## Explicit Non-Closure

- 不实现日期录入/UI，不计算第二次 OA 法定期限，不修改其他任务类型。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01`
- `FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`
- Acceptance prerequisite: `FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01` (`PASS`)

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`
- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_addgap_oa_deadline_fail_closed.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用文档创建调用方权限。
- Status codes/errors: 缺失/未确认/冲突 due 返回 409 且文档事务回滚；成功沿用 201。
- Response envelope: 沿用调用端包络。
- SQLite: app-side date handling；无 PG-only SQL。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_deadline_fail_closed.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/tasks/task_generation_service.py tests/test_addgap_oa_deadline_fail_closed.py && .venv/bin/ruff format app/modules/tasks/task_generation_service.py tests/test_addgap_oa_deadline_fail_closed.py && .venv/bin/ruff check app/modules/tasks/task_generation_service.py tests/test_addgap_oa_deadline_fail_closed.py`
- Scope: `git diff --check -- backend/app/modules/tasks/task_generation_service.py backend/tests/test_addgap_oa_deadline_fail_closed.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
