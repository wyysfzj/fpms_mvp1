# FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 34 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align obsolete executable-OA source creation fixtures in the two allowlisted reply-chain tests with
Task24/Task27 confirmed explicit due requirements. Preserve every reply-date, open-task,
no-auto-writeoff, status/template/default, list-filter, and lifecycle assertion unchanged.

## Explicit Non-Closure

Do not modify product or any other test/spec/plan/manifest. Do not alter reply validation, task
write-off, case-state, or Task34 implementation/acceptance. Do not delete coverage.

## Dependencies

- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01` (`PASS`)
- `FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01` acceptance
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_addgap_oa_out_keeps_task_open.py`
- `backend/tests/test_b2_reply_chain.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other file or artifact family is authorized.

## Runtime Contracts

- Test-only; permission/status/envelope unchanged.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py && .venv/bin/ruff format tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py && .venv/bin/ruff check tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py`
- Scope: `git diff --check -- backend/tests/test_addgap_oa_out_keeps_task_open.py backend/tests/test_b2_reply_chain.py tasks/additional_gaps/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest. It must pass independent review/evidence/gate
before Task34 acceptance; Task47 must record its closure.

## Done Definition

Only executable-OA fixture payloads gain confirmed due tuples; full two-file suite passes with all
non-deadline assertions preserved; Ruff/scope/secret-safe RED/GREEN, independent review, atomic
validation, and task gate pass. Only then may this task be `PASS`.
