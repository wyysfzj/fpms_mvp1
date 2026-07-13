# FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01

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

OA_OUT reply validation 接受 resolver 标识的可执行 OA semantic aliases，而非仅 literal OA_IN。

## Explicit Non-Closure

不接受 reference-only alias，不改变 OA_OUT 不关 task 的规则。

## Dependencies

- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

## Allowed Files

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_oa_alias_reply_validation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/**`

No other source, test, task, or shared ownership file is authorized. Shared files must follow the serial order frozen in the approved implementation plan.

## Runtime contracts

- Permission: 沿用 Doc.Create。
- Status codes/errors: 有效 alias 成功 201；reference-only/方向/语义冲突 400/409。
- Response envelope: 沿用 DocumentOut。
- SQLite: SQLite-safe 查询。
- Simplified Chinese UI: N/A。

## Verification Commands

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_alias_reply_validation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_oa_alias_reply_validation.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_oa_alias_reply_validation.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_oa_alias_reply_validation.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_oa_alias_reply_validation.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01`.

## Evidence Path

- `artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/`

## Done definition

The RED test is preserved, the minimum allowlisted implementation makes it GREEN, scoped checks pass, dirty-baseline artifacts and required evidence exist under `artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/`, the task gate passes, the exact closure is complete, and the non-closure boundary remains untouched. Only then may this task be reported PASS.
