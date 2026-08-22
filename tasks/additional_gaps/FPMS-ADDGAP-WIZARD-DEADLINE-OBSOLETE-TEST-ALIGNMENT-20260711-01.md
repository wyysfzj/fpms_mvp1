# FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 29 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the single obsolete malformed-raw-`OfficialDueDate` wizard assertion in
`test_b_official_due_date_task_generation.py` with the approved Task22/Task29 shape contract:
malformed raw extra-data returns HTTP 422 `DOCUMENT_EXTRA_DATA_INVALID`. Preserve every other test
and assertion in the file unchanged.

## Explicit Non-Closure

Do not modify product or any other test/spec/plan/manifest. Do not weaken 400 cross-field, 409
missing-confirmation/configuration, or confirmed explicit due behavior. Do not absorb Task29
implementation or acceptance.

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01` (`PASS`)
- `FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01` acceptance
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_b_official_due_date_task_generation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other file or artifact family is authorized.

## Runtime Contracts

- Status: malformed raw extra-data is 422 with `DOCUMENT_EXTRA_DATA_INVALID`.
- Permission/envelope: unchanged; test-only alignment.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_b_official_due_date_task_generation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_b_official_due_date_task_generation.py && .venv/bin/ruff format tests/test_b_official_due_date_task_generation.py && .venv/bin/ruff check tests/test_b_official_due_date_task_generation.py`
- Scope: `git diff --check -- backend/tests/test_b_official_due_date_task_generation.py tasks/additional_gaps/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest. It must independently pass review/evidence/gate
before Task29 acceptance, and Task47 must record its closure.

## Done Definition

Only the one obsolete status/code assertion changes; full target passes, all other test bodies remain
unchanged, Ruff/scope/secret/evidence/gate pass, and non-closure is respected. Only then may this
task be `PASS`.
