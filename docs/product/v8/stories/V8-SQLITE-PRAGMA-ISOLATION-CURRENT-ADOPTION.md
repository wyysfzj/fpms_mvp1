# Story V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION

- Status: `CURRENT_VERIFIED` candidate pending independent adoption review.
- Risk: `PROTECTED`.
- Purpose: adopt the exact independently accepted Final-suite SQLite PRAGMA isolation bytes,
  without adding behavior or claiming release.

## Exact cumulative boundary

- accepted ledger baseline: `e19d615c84c4c2d2afd10dcc440c4f2683fc2b77`;
- independently approved remediation: `9557d1c58ae51d4e9c68b7d435e2873ebb154205`;
- exact remediation paths: three;
- candidate fingerprint paths: those three exact paths plus this story, its task card and focused
  adoption contract, exactly six unique paths.

## Accepted remediation

- the shared pytest SQLite engine restores `PRAGMA busy_timeout=5000` at checkout;
- an actively checked-out connection may still set a shorter timeout for its own controlled test;
- deterministic RED proved a pooled connection retained zero without the fix;
- GREEN focused isolation plus the two unchanged future-annuity concurrency nodes passed
  `3 passed`;
- scoped Ruff, format-check and exact diff-check passed;
- independent High review approved the remediation with `P0/P1/P2 = 0/0/0`.

## Residual

- Row283 remains the sole PENDING catalog row;
- production inputs remain `CONFIG_REQUIRED / PENDING / 409 NO WRITE`;
- TEST_ONLY remains isolated and production activation is not claimed;
- independent High adoption review, receipt-only commit and sole ledger adoption remain required.
