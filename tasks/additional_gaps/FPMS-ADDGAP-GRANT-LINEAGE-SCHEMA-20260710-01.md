# FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01

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

Phase 0-EXT 为 grant task 增加 source/deadline/supersede/request-key carriers，并在重复扫描通过后创建唯一索引。

## Explicit Non-Closure

不创建 grant task，不激活授权目录，不修改用户现有 migration，不更改 workflow status。

## Dependencies

`FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`；执行前重新确认当前 Alembic head。

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`
- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`
- `FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`
- `FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01`
- `FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01`

## Allowed Files

- `backend/alembic/versions/addgap_grant_lineage.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_addgap_grant_lineage_schema.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: N/A（schema）。
- Status codes/errors: N/A；重复/不可回填数据 fail-closed。
- Response envelope: N/A。
- SQLite: SQLite-safe 类型、CURRENT_TIMESTAMP、唯一索引；clean upgrade head。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_lineage_schema.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix alembic/versions/addgap_grant_lineage.py app/modules/fees/models.py tests/test_addgap_grant_lineage_schema.py && .venv/bin/ruff format alembic/versions/addgap_grant_lineage.py app/modules/fees/models.py tests/test_addgap_grant_lineage_schema.py && .venv/bin/ruff check alembic/versions/addgap_grant_lineage.py app/modules/fees/models.py tests/test_addgap_grant_lineage_schema.py`
- Migration gate: `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head` on a clean temporary SQLite database.
- Scope: `git diff --check -- backend/alembic/versions/addgap_grant_lineage.py backend/app/modules/fees/models.py backend/tests/test_addgap_grant_lineage_schema.py`

## Evidence Path

Initialize/finalize under `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/**`, preserve RED/GREEN and clean-migration evidence, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`.

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
