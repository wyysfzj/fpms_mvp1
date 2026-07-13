# FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01

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

仅在 lineage/due/draft gates 完成后激活“授权通知书-电子”并绑定冻结 grant 语义。

## Explicit Non-Closure

不激活其他授权别名、办登/年费/PCT/复审目录，不改变 deadline 规则。

## Dependencies

- 35–37
- `FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01`
- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`

## Remaining Follow-Up Task IDs

- Task55 supplemental alignment for Task33's superseded six-row `seed_dev` assertion
- 39
- 46

## Allowed Files

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_addgap_notice_grant_activation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime Contracts

- Permission: N/A（幂等 seed/catalog）。
- Status codes/errors: 缺 confirmed due 的创建由 gate 409；合法创建沿用 201。
- Response envelope: 目录输出沿用既有 schema。
- SQLite: seed 幂等、bootstrap-safe。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_grant_activation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_grant_activation.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_grant_activation.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_grant_activation.py`
- Scope: `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/scripts/seed_dev.py backend/tests/test_addgap_notice_grant_activation.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
