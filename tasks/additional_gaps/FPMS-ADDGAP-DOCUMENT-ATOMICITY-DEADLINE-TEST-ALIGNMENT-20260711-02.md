# FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental final-close prerequisite
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the grant-notice document atomicity test fixture with the confirmed explicit official-deadline
precondition so the test still reaches and verifies forced side-effect rollback.

## Explicit Non-Closure

Do not modify product code or rollback assertions; do not weaken grant deadline fail-closed behavior.

## Dependencies

- Tasks24, 35, and 37 are PASS.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_addgap_document_create_atomicity.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Runtime Contracts

- Test-only; preserve 409 rollback semantics and every persistence assertion.
- SQLite pytest is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_create_atomicity.py`
- Ruff: scoped check/format/check for the allowlisted test.
- Scope: `git diff --check -- backend/tests/test_addgap_document_create_atomicity.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Supplemental Close Contract

Outside the frozen manifest; independent review/evidence/gate required and Task47 must append it.

## Done Definition

Only fixture lineage changes; prior rollback assertions remain; RED/GREEN, Ruff, scope, independent
review, atomic evidence validation, and task gate pass.
