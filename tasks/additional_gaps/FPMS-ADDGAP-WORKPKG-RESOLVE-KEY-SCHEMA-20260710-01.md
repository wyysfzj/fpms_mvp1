# FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01

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

Phase 0-EXT 增加并回填 OfficialWorkPackage.resolve_key，重复预检通过后建立唯一约束。

## Explicit Non-Closure

不修改用户现有 migration，不创建 work package 服务/API/UI，不更改其他表。

## Dependencies

Wave 0 已 PASS；执行前已重新确认唯一 Alembic head 为用户 migration `frfe04_block_struct_cols_01`。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01`
- `FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01`
- `FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`
- `FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`

## Allowed Files

- `backend/alembic/versions/addgap_workpkg_resolve_key.py`
- `backend/app/modules/official_workflows/models.py`
- `backend/tests/test_addgap_workpkg_resolve_key_schema.py`
- `tasks/additional_gaps/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01.md`
- `artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（schema）。
- Status codes/errors: N/A；migration 重复数据必须 fail-closed 并给出明确错误。
- Response envelope: N/A。
- SQLite: Integer/FK 对齐、CURRENT_TIMESTAMP、无 PG-only SQL；clean SQLite upgrade head。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_workpkg_resolve_key_schema.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix alembic/versions/addgap_workpkg_resolve_key.py app/modules/official_workflows/models.py tests/test_addgap_workpkg_resolve_key_schema.py && .venv/bin/ruff format alembic/versions/addgap_workpkg_resolve_key.py app/modules/official_workflows/models.py tests/test_addgap_workpkg_resolve_key_schema.py && .venv/bin/ruff check alembic/versions/addgap_workpkg_resolve_key.py app/modules/official_workflows/models.py tests/test_addgap_workpkg_resolve_key_schema.py`
- Migration gate: `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head` on a clean temporary SQLite database.
- Scope: `git diff --check -- backend/alembic/versions/addgap_workpkg_resolve_key.py backend/app/modules/official_workflows/models.py backend/tests/test_addgap_workpkg_resolve_key_schema.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/**`, preserve RED/GREEN and clean-migration evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
