# FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02

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

Align the OA wizard task-preview success request with confirmed explicit official deadline input and
assert that the preview uses that date, while preserving non-deadline-template behavior.

## Explicit Non-Closure

Do not restore template-offset derivation, modify product code, or weaken the 409 missing-deadline
contract owned by Task27.

## Dependencies

- Task27 is PASS.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_document_wizard_task_preview.py`
- `tasks/additional_gaps/FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02.md`
- `artifacts/FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Runtime Contracts

- Test-only; preview status/envelope and non-deadline empty result remain unchanged.
- SQLite pytest is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_document_wizard_task_preview.py`
- Ruff: scoped check/format/check for the allowlisted test.
- Scope: `git diff --check -- backend/tests/test_document_wizard_task_preview.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Supplemental Close Contract

Outside the frozen manifest; independent review/evidence/gate required and Task47 must append it.

## Done Definition

Explicit confirmed input replaces obsolete offset expectation; non-deadline behavior remains; RED/
GREEN, Ruff, scope, independent review, atomic evidence validation, and task gate pass.
