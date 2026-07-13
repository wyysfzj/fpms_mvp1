# FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01

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

## Atomic contract

- Exact closure slice: grant state response 暴露 lineage，并对 legacy/superseded task 移除状态变更 actions。
- Explicit non-closure: 不更改 workflow state 值、不实现 UI、不自动迁移 legacy task。
- Dependencies: 41
- Remaining follow-up task IDs: 43, 44

## Exact allowlist

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/tests/test_addgap_grant_state_lineage_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 GrantFeeTask.Read/Write。
- Status codes/errors: GET 200；被 gate 的写动作保持明确 409。
- Response envelope: 扩展既有 state response。
- SQLite: 只读 lineage 判断，SQLite-safe。
- Simplified Chinese UI: N/A。

## TDD and verification

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_state_lineage_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_state_lineage_gate.py && .venv/bin/ruff format app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_state_lineage_gate.py && .venv/bin/ruff check app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_state_lineage_gate.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_addgap_grant_state_lineage_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
