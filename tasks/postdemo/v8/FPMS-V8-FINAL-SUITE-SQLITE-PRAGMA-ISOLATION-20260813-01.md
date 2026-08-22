# FPMS V8 Final-Suite SQLite PRAGMA Isolation

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Exact Closure Slice

Every checkout from the shared pytest SQLite engine restores the normal 5000 ms lock-wait
budget. A test may still set a shorter `PRAGMA busy_timeout` for its current checked-out
connection, but that value must not leak through the pool into a later test or transaction.

## RED and closure

The Final backend matrix left pooled connections with `busy_timeout` values of 0 or 1 ms. The
later future-annuity concurrency tests then returned before their 100 ms serialization checkpoint,
although both pass in isolation with SQLite's normal 5000 ms wait. Add a deterministic regression
that poisons one checked-out connection and proves the next checkout restores 5000 ms, then make
the minimum shared pytest-engine checkout fix.

## Explicit Non-Closure

No product/API/domain/schema/migration/seed/transaction semantic change; no timeout increase inside
an actively checked-out connection; no concurrency assertion deletion or weakening; no Row283
report, story, ledger, release, or broad-matrix claim.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FINAL-SUITE-SQLITE-PRAGMA-ISOLATION-20260813-01.md`
- `backend/tests/conftest.py`
- `backend/tests/test_v8_sqlite_pragma_isolation.py`

## Verification Commands

- `cd backend && .venv/bin/pytest -q tests/test_v8_sqlite_pragma_isolation.py`
- `cd backend && .venv/bin/pytest -q tests/test_v8_sqlite_pragma_isolation.py tests/test_v8_future_annuity_exception_authority_service.py::test_concurrent_overlapping_publications_serialize_and_fail_closed tests/test_v8_future_annuity_exception_authority_service.py::test_concurrent_gate_revocation_is_revalidated_after_write_lock`
- `cd backend && .venv/bin/ruff check tests/conftest.py tests/test_v8_sqlite_pragma_isolation.py`
- `cd backend && .venv/bin/ruff format --check tests/conftest.py tests/test_v8_sqlite_pragma_isolation.py`
- `git diff --check -- tasks/postdemo/v8/FPMS-V8-FINAL-SUITE-SQLITE-PRAGMA-ISOLATION-20260813-01.md backend/tests/conftest.py backend/tests/test_v8_sqlite_pragma_isolation.py`

Independent High review requires P0/P1/P2 `0/0/0` before any current-byte adoption or Final matrix
resume.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FINAL-CLOSE-20260712-01`

## Evidence Path

- `artifacts/FPMS-V8-FINAL-SUITE-SQLITE-PRAGMA-ISOLATION-20260813-01/`

## Current Verification Result

RED deterministically observed the poisoned pooled connection return `busy_timeout=0` on its next
checkout. GREEN restores 5000 ms on checkout while preserving per-checkout overrides; the focused
regression plus both future-annuity concurrency nodes pass `3 passed`. Scoped Ruff, format-check
and exact diff-check pass. Independent High acceptance remains required.
