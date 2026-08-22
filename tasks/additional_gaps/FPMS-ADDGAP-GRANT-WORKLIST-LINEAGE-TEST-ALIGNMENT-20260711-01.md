# FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 41 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the obsolete exact-key assertion in the allowlisted grant-fee worklist test with Task41's four
additive list fields: `lineage_status`, `source_document_id`, `deadline_source`, and
`deadline_confirmed_at`. Preserve all existing permission, pagination, filter, workflow-status,
billing-lineage, and value assertions unchanged.

## Explicit Non-Closure

Do not modify product code, Task41's target test, state-machine tests, spec/plan/manifest, or any
other assertion. Do not weaken exact response-shape coverage or absorb Task42 state-lineage scope.

## Dependencies

- `FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01` acceptance
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_grant_fee_worklist_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/**`

No other source, test, task, plan, manifest, or artifact family is authorized.

## Runtime Contracts

- Test-only; permission, status-code, response-envelope, workflow-state, and product behavior remain unchanged.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_grant_fee_worklist_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_grant_fee_worklist_api.py && .venv/bin/ruff format tests/test_grant_fee_worklist_api.py && .venv/bin/ruff check tests/test_grant_fee_worklist_api.py`
- Scope: `git diff --check -- backend/tests/test_grant_fee_worklist_api.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest. It must pass independent review, evidence
validation, and its task gate before Task41 acceptance; Task47 must record its closure.

## Done Definition

Only the exact expected-key set gains the four Task41 fields; the full worklist test file passes
without deleted or weakened assertions; scoped Ruff/scope, independent review, atomic validation,
and task gate pass. Only then may this task be `PASS`.
