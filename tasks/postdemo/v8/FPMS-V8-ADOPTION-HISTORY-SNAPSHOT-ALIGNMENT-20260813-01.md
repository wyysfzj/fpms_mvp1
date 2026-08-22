# FPMS V8 Adoption History Snapshot Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Exact Closure Slice

Make the SQLite PRAGMA and Final governance snapshot adoption contracts verify their exact
historical ledger-only adoption commits while preserving those adopted stories as immutable current
prefix members after later append-only adoptions.

## Explicit Non-Closure

No product/domain/schema/migration/seed/ledger/report/Row283/release change; no skip/xfail/assertion
deletion; no mutation or reordering of any adopted row/story.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-ADOPTION-HISTORY-SNAPSHOT-ALIGNMENT-20260813-01.md`
- `backend/tests/test_v8_sqlite_pragma_isolation_adoption.py`
- `backend/tests/test_v8_final_governance_snapshot_adoption.py`

## Verification Commands

- `cd backend && .venv/bin/pytest -q tests/test_v8_sqlite_pragma_isolation_adoption.py::test_ledger_adoption_is_append_only_when_materialized tests/test_v8_final_governance_snapshot_adoption.py::test_ledger_adoption_is_append_only_when_materialized`
- scoped Ruff, format-check and exact diff-check over the two tests and task.

Independent High review requires P0/P1/P2 `0/0/0` before current-byte adoption or Final resume.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FINAL-CLOSE-20260712-01`

## Evidence Path

- `artifacts/FPMS-V8-ADOPTION-HISTORY-SNAPSHOT-ALIGNMENT-20260813-01/`

## Current Verification Result

The full backend lane reached `6155 passed` before failing only the stale SQLite adoption last-story
assumption. Both affected historical adoption contracts now bind their exact ledger-only commits,
prove the original sole append there, and require those exact adopted ledgers as immutable current
prefixes. Focused GREEN passes `2 passed`; scoped Ruff, format and exact diff checks pass.
