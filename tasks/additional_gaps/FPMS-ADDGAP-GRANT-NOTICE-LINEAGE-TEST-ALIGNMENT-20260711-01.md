# FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 59 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the allowlisted grant notice-document test's ordinary notice-generation fixtures with
Task59's confirmed-lineage precondition by creating a real same-case incoming source document and
complete deadline lineage tuple. Preserve all rendering, attachment, permission, client-instruction
400, and missing-template 409 assertions unchanged.

## Explicit Non-Closure

Do not modify product code, Task59 target tests, draft/state tests, or any existing behavioral
expectation. Do not add legacy/superseded coverage already owned by Task59.

## Dependencies

- `FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01` acceptance
- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_grant_fee_notice_document_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/**`

No other file or artifact family is authorized.

## Runtime Contracts

- Test-only; product, permission, status, envelope, rendering, and workflow semantics remain unchanged.
- Every ordinary fixture uses a real same-case IN document plus nonblank deadline source and confirmation time.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_grant_fee_notice_document_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_grant_fee_notice_document_api.py && .venv/bin/ruff format tests/test_grant_fee_notice_document_api.py && .venv/bin/ruff check tests/test_grant_fee_notice_document_api.py`
- Scope: `git diff --check -- backend/tests/test_grant_fee_notice_document_api.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest and must pass review/evidence/gate independently.
Task47 must record it in the supplemental appendix.

## Done Definition

Only fixture lineage setup changes; the full file passes with every prior assertion preserved; Ruff,
scope, independent review, evidence validation, and task gate pass. Only then may this task be PASS.
