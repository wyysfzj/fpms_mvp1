# FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02

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

Align the incoming OA fixture in the document UI deadline-generation integration test with confirmed
explicit official deadline input while preserving task creation and reply write-off assertions.

## Explicit Non-Closure

Do not modify product/UI code or change the OA_OUT reply behavior; do not weaken fail-closed rules.

## Dependencies

- Task27 is PASS.
- `FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01` is independently PASS and owns
  only the separate test-name and OA_OUT `DONE` to `OPEN` assertion alignment.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_document_ui_deadline_generation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Runtime Contracts

- Test-only; existing 201/200 behavior and task state assertions stay unchanged.
- SQLite pytest is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_document_ui_deadline_generation.py`
- Ruff: scoped check/format/check for the allowlisted test.
- Scope: `git diff --check -- backend/tests/test_document_ui_deadline_generation.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Supplemental Close Contract

Outside the frozen manifest; independent review/evidence/gate required and Task47 must append it.

## Done Definition

Only incoming fixture deadline input changes; all lifecycle assertions remain; RED/GREEN, Ruff,
scope, independent review, atomic evidence validation, and task gate pass.
