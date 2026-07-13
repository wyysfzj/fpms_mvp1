# FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02

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

Align the original grant-fee prerequisite schema test's exact expected column set with the lineage,
deadline, supersede, and request-key carriers added by Task35, for both ORM and clean migration paths.

## Explicit Non-Closure

Do not modify models/migrations, relax exact schema equality, or change defaults/FK assertions.

## Dependencies

- Task35 is PASS.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_grant_fee_prereq_schema.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02.md`
- `artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/**`

## Runtime Contracts

- Test-only; exact schema equality, SQLite clean-upgrade, FK, and defaults remain enforced.
- SQLite pytest is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_grant_fee_prereq_schema.py`
- Ruff: scoped check/format/check for the allowlisted test.
- Scope: `git diff --check -- backend/tests/test_grant_fee_prereq_schema.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/**`

## Supplemental Close Contract

Outside the frozen manifest; independent review/evidence/gate required and Task47 must append it.

## Done Definition

Expected columns exactly match Task35 carriers in ORM and clean migration; RED/GREEN, Ruff, scope,
independent review, atomic evidence validation, and task gate pass.
