# FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02

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

Align the OA document fixture local to the need-reply deadline-edit test with confirmed explicit
official deadline input while preserving all edit, cancel, log, and due-date assertions.

## Explicit Non-Closure

Do not modify shared helpers, product code, or expected update/cancel behavior; do not weaken OA
deadline fail-closed rules.

## Dependencies

- Task27 is PASS.

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_b_need_reply_deadline_edit_rule.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02.md`
- `artifacts/FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Runtime Contracts

- Test-only; existing 200/400 behavior and error codes stay unchanged.
- SQLite pytest is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_b_need_reply_deadline_edit_rule.py`
- Ruff: scoped check/format/check for the allowlisted test.
- Scope: `git diff --check -- backend/tests/test_b_need_reply_deadline_edit_rule.py`

## Evidence Path

- `artifacts/FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02/**`

## Supplemental Close Contract

Outside the frozen manifest; independent review/evidence/gate required and Task47 must append it.

## Done Definition

Only local fixture deadline input changes; all behavioral assertions remain; RED/GREEN, Ruff, scope,
independent review, atomic evidence validation, and task gate pass.
