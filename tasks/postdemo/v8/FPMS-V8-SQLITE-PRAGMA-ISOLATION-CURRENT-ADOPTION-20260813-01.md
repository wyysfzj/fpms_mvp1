# FPMS V8 SQLite PRAGMA Isolation Current Adoption

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Exact Closure Slice

Adopt the independently approved SQLite checkout-isolation bytes from exact baseline
`e19d615c84c4c2d2afd10dcc440c4f2683fc2b77` through remediation commit
`9557d1c58ae51d4e9c68b7d435e2873ebb154205`: its exact three paths plus this task, focused
contract and current-adoption story, exactly six fingerprinted paths.

## Explicit Non-Closure

No existing product/test/task byte change; no schema/migration/seed/domain/timeout semantic change;
no Final report/Row283 row/release claim. Row283 remains the sole PENDING catalog row. Production
inputs remain `CONFIG_REQUIRED / PENDING / 409 NO WRITE`; TEST_ONLY remains isolated.

## Allowed Files

- the exact three paths in `git diff --name-only e19d615c84c4c2d2afd10dcc440c4f2683fc2b77..9557d1c58ae51d4e9c68b7d435e2873ebb154205` are fingerprint inputs only and remain unchanged;
- `tasks/postdemo/v8/FPMS-V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION-20260813-01.md`;
- `backend/tests/test_v8_sqlite_pragma_isolation_adoption.py`;
- `docs/product/v8/stories/V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION.md`;
- reviewer-owned `docs/product/v8/reviews/V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION.md`;
- sole later adoption patch `docs/product/v8/coverage-ledger.json`.

## Verification Commands

- `cd backend && .venv/bin/pytest -q tests/test_v8_sqlite_pragma_isolation_adoption.py`
- `cd backend && .venv/bin/ruff check tests/test_v8_sqlite_pragma_isolation_adoption.py`
- `cd backend && .venv/bin/ruff format --check tests/test_v8_sqlite_pragma_isolation_adoption.py`
- `git diff --check e19d615c84c4c2d2afd10dcc440c4f2683fc2b77..<candidate> -- <the six exact candidate paths>`
- `python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha <candidate>` after the exact ledger patch is present.

Independent High review audits the six-path candidate and sole ledger patch, then commits only its
receipt. Controller commits only the reviewed ledger patch.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FINAL-CLOSE-20260712-01`

## Evidence Path

- `artifacts/FPMS-V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION-20260813-01/`
