# FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01

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

- Exact closure slice: grant list response 增加独立 lineage fields，不改变 workflow state/status。
- Explicit non-closure: 不改变 state action 可用性、不实现 UI、不合并 lineage_status 与 workflow status。
- Dependencies: 35–40
- Remaining follow-up task IDs: 42, 43

## Exact allowlist

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/tests/test_addgap_grant_list_lineage_projection.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 GrantFeeTask.Read。
- Status codes/errors: GET 200；GET 无 body。
- Response envelope: 扩展既有 grant list item/model。
- SQLite: 只读 SQLite-safe projection。
- Simplified Chinese UI: N/A。

## TDD and verification

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_list_lineage_projection.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_list_lineage_projection.py && .venv/bin/ruff format app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_list_lineage_projection.py && .venv/bin/ruff check app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_list_lineage_projection.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_addgap_grant_list_lineage_projection.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
