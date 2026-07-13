# FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02

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

Align OA creation fixtures in the document-specific-search test file with confirmed explicit official
deadline input while preserving every search/filter/persistence assertion.

## Explicit Non-Closure

Do not modify product search behavior, non-OA fixtures, filters, or expected result sets; do not
weaken OA deadline fail-closed rules.

## Dependencies

- Task27 is PASS.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_document_specific_search_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Runtime Contracts

- Test-only; API status, envelope, permission, and search semantics unchanged.
- SQLite pytest is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_document_specific_search_api.py`
- Ruff: scoped check/format/check for the allowlisted test.
- Scope: `git diff --check -- backend/tests/test_document_specific_search_api.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Supplemental Close Contract

Outside the frozen manifest; independent review/evidence/gate required and Task47 must append it.

## Done Definition

Only OA fixture deadline input changes; all search assertions remain; RED/GREEN, Ruff, scope,
independent review, atomic evidence validation, and task gate pass.
