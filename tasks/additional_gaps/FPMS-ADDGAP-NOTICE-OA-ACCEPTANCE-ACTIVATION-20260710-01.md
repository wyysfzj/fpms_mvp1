# FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: 6B
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

只激活受理通知、精确首 OA、二/三/四/五次 OA 目录行，并绑定冻结语义。

## Explicit Non-Closure

UM/design OA、补正、复审、驳回、年费、PCT、授权及其他目录仍 reference-only。

## Dependencies

- 18–29

## Remaining Follow-Up Task IDs

- 34
- 46

## Allowed Files

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_addgap_notice_oa_acceptance_activation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime Contracts

- Permission: N/A（幂等 seed/catalog）。
- Status codes/errors: 无 confirmed due 的可执行 OA 创建由既有 gate 返回 409。
- Response envelope: 目录输出沿用现有 schema。
- SQLite: seed 幂等、bootstrap-safe。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_oa_acceptance_activation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_oa_acceptance_activation.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_oa_acceptance_activation.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_oa_acceptance_activation.py`
- Scope: `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/scripts/seed_dev.py backend/tests/test_addgap_notice_oa_acceptance_activation.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/**`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
