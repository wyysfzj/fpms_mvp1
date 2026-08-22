# FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before final full-suite close
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align `test_grant_fee_notice_task_creation.py` with the approved Task24/Task36 explicit grant
deadline and source-lineage contract: created and imported grant notices carry a confirmed explicit
official due date, repeated same-source behavior remains idempotent, and assertions use that exact
due date rather than the obsolete document-date-plus-60 fallback. Preserve attachment, case-state,
fee-prefill, and all other original coverage.

## Explicit Non-Closure

Do not modify product, seed, migration, schema, service, API, manifest, specification, plan, or any
other test file. Do not change grant auto-draft, replacement, catalog activation, UI, or E2E behavior.
Do not delete or weaken existing attachment/state/fee assertions.

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01` (`PASS`)
- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01` (`PASS`)

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_grant_fee_notice_task_creation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other source, test, task, manifest, specification, plan, shared ownership file, or artifact family
is authorized.

## Runtime Contracts

- Permission/status/envelope: unchanged; test-only alignment preserves existing public contracts.
- SQLite: every pytest invocation is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.
- Simplified Chinese UI: N/A.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_grant_fee_notice_task_creation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_grant_fee_notice_task_creation.py && .venv/bin/ruff format tests/test_grant_fee_notice_task_creation.py && .venv/bin/ruff check tests/test_grant_fee_notice_task_creation.py`
- Scope: `git diff --check -- backend/tests/test_grant_fee_notice_task_creation.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Execution and Close-Audit Contract

This supplemental task must not modify the frozen 47-entry manifest/spec/plan. Task47 must record
its ID, evidence, gate result, and closure decision before final full-suite acceptance.

## Done Definition

The exact target file passes with confirmed source deadlines while preserving all original
non-deadline assertions; scoped Ruff/scope, credential-safe RED/GREEN evidence, independent review,
atomic validation, and task gate pass; exact closure and non-closure are respected. Only then may
this task be `PASS`.
