# FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 5
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Seed `OA_REPLY_SUBSEQUENT` 作为二次及以后 OA 的 task identity，且不提供可计算期限 fallback。

## Explicit Non-Closure

不激活中文目录、不改变首 OA 任务、不从模板天数生成期限。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01`
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`
- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`

## Allowed Files

- `backend/scripts/seed_dev.py`
- `backend/tests/test_addgap_oa_subsequent_task_identity.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（幂等 seed）。
- Status codes/errors: N/A；缺显式截止日时后续消费者必须 409。
- Response envelope: N/A。
- SQLite: seed 幂等、bootstrap-safe。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_subsequent_task_identity.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix scripts/seed_dev.py tests/test_addgap_oa_subsequent_task_identity.py && .venv/bin/ruff format scripts/seed_dev.py tests/test_addgap_oa_subsequent_task_identity.py && .venv/bin/ruff check scripts/seed_dev.py tests/test_addgap_oa_subsequent_task_identity.py`
- Scope: `git diff --check -- backend/scripts/seed_dev.py backend/tests/test_addgap_oa_subsequent_task_identity.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/**`, preserve RED/GREEN command evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
