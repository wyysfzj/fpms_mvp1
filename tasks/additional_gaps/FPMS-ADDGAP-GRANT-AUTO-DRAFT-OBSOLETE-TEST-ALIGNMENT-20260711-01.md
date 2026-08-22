# FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 38 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the three obsolete grant-specific assertions in `test_b3_fee_linking.py` with the approved
Task24/Task36/Task37 contracts: grant document creation supplies a confirmed explicit official due
date, returns 201, and creates no generic zero-value `FeeDraft` or auto-draft response header before
client instruction. Preserve the file's remaining B3 non-grant coverage unchanged.

## Explicit Non-Closure

Do not modify product, seed, migration, schema, service, API, manifest, specification, or plan files.
Do not delete tests, weaken confirmed-due or no-auto-draft behavior, implement client instruction,
or absorb Task38 activation or Task47 final-close work.

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01` (`PASS`)
- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01` (`PASS`)
- `FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01` (`PASS`)

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_b3_fee_linking.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other source, test, task, manifest, specification, plan, shared ownership file, or artifact family
is authorized.

## Runtime Contracts

- Permission: unchanged; test-only alignment.
- Status codes/errors: grant document creation uses a confirmed explicit due and remains 201; no
  generic fee draft/header exists before client instruction.
- Response envelope: unchanged.
- SQLite: serialize every pytest invocation through `/tmp/fpms_addgap_sqlite_test.lock`.
- Simplified Chinese UI: N/A.

## Verification Commands

- RED characterization, then GREEN: `cd backend && .venv/bin/pytest -q tests/test_b3_fee_linking.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_b3_fee_linking.py && .venv/bin/ruff format tests/test_b3_fee_linking.py && .venv/bin/ruff check tests/test_b3_fee_linking.py`
- Scope: `git diff --check -- backend/tests/test_b3_fee_linking.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Execution and Close-Audit Contract

This task is supplemental to the frozen 47-entry manifest and must not modify that manifest, its
approved specification, or plan. It must pass its own evidence and task gate before Task38
acceptance. Task47 must record this task ID, evidence, gate result, and closure decision.

## Done Definition

The three obsolete grant assertions preserve their original registration/no-unrelated-effect intent
while using confirmed structured due fields and asserting no generic auto draft; all eight B3 tests
pass under the SQLite lock; scoped Ruff/scope, evidence validation, independent review, and task
gate pass; the exact closure is complete and explicit non-closure is respected. Only then may this
supplemental task be `PASS`.
