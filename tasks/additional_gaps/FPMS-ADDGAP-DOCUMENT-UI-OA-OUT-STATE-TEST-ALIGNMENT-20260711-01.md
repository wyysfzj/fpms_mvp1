# FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental final-close prerequisite S2b
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the single obsolete OA_OUT assertion in the document UI deadline integration test with
Task43's accepted contract: creating an OA reply document does not close the open OA task; the task
remains `OPEN` until the official receipt closure path completes.

## Explicit Non-Closure

Do not change product code, OA receipt closure behavior, incoming deadline fixture fields, task
creation assertions, or any other test. Do not make OA_OUT auto-close the task.

## Dependencies

- `FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01` is PASS.
- Task67 has applied only its separate confirmed-deadline fixture edit and stopped before changing
  the state assertion.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02` re-verification
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_document_ui_deadline_generation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/**`

No other file is authorized. Ownership of the shared test file is serialized after Task67.

## Runtime Contracts

- Test-only; Task43's OA_OUT keep-open semantics remain authoritative.
- Existing 201/200 response checks, task identity, and incoming task creation assertions stay intact.
- SQLite pytest is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_document_ui_deadline_generation.py`
- Contract cross-check: targeted Task43 test for OA_OUT keeps task open.
- Ruff: scoped check/format/check for the allowlisted test.
- Scope: `git diff --check -- backend/tests/test_document_ui_deadline_generation.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Close Contract

Outside the frozen manifest; independent review/evidence/gate required and Task47 must append it.

## Done Definition

Only the obsolete OA_OUT state expectation/name is aligned; all other assertions remain; RED/GREEN,
Task43 cross-check, Ruff, scope, independent review, atomic evidence validation, and task gate pass.
