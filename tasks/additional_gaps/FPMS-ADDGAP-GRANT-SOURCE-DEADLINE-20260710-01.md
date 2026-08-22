# FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01

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

首个可执行授权通知按 source key 创建/复用一个 grant task，必须使用 confirmed explicit due，并移除 +60 推算。

## Explicit Non-Closure

不激活授权目录、不生成 FeeDraft、不处理 replacement、不修改 UI。

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`
- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`
- `FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`
- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`

## Allowed Files

- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_addgap_grant_source_deadline.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用调用方权限。
- Status codes/errors: 缺失/未确认 due 或不同 active source 409；同 source 幂等复用。
- Response envelope: 沿用 grant task 输出模型。
- SQLite: source unique 约束；不依赖 RETURNING。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_source_deadline.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_addgap_grant_source_deadline.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_addgap_grant_source_deadline.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_addgap_grant_source_deadline.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_addgap_grant_source_deadline.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/**`, preserve RED/GREEN evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
