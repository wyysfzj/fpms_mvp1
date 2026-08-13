# V8 SQLite PRAGMA Isolation Current Adoption Review

Verdict: APPROVED

P0: 0
P1: 0
P2: 0

- Review class: Independent High / PROTECTED
- Base SHA: `e19d615c84c4c2d2afd10dcc440c4f2683fc2b77`
- Remediation SHA: `9557d1c58ae51d4e9c68b7d435e2873ebb154205`
- Candidate SHA: `c6a449f134764f57d36ecc5429cc51ba13539040`
- Candidate range:
  `e19d615c84c4c2d2afd10dcc440c4f2683fc2b77..c6a449f134764f57d36ecc5429cc51ba13539040`
- Exact six-path tree fingerprint:
  `534a81069575c59f91bc6a5862e1fb6316c763d5dd526a935a8fd1c9abf76192`
- Reviewed sole-ledger patch SHA-256:
  `edc68f9de61788a4fb23c27185a6e458a78f34dce194740b97352ed65b6d74f3`

## Remediation and scope audit

The candidate contains exactly the three independently approved remediation paths plus the
current-adoption task, focused contract and story. The resulting six paths are unique, ordered
exactly as the ledger story records them and match the reviewed tree fingerprint.

The remediation changes only the shared pytest SQLite fixture: each pooled DBAPI connection
checkout restores `PRAGMA busy_timeout=5000`. The focused regression proves an actively checked
out connection may still set and observe a shorter timeout, while the next checkout restores the
normal value. The two unchanged future-annuity concurrency nodes continue to exercise lock-wait
serialization and write-lock revalidation. There is no product, domain, schema, migration, seed,
concurrency-assertion or release behavior change. The remediation received a separate independent
High review with `P0/P1/P2 = 0/0/0`.

## Ledger and production boundary

The reviewed uncommitted ledger patch leaves every catalog row and every preceding story
byte-equivalent to the candidate, then appends exactly one
`V8-SQLITE-PRAGMA-ISOLATION-CURRENT-ADOPTION` story. Row283 remains the sole `PENDING` row and
retains `FINAL_CLOSE_PENDING`; this review does not close Row283 or run release.

Both production inputs remain `CONFIG_REQUIRED`, their source decisions remain `PENDING`, and
production failure remains `409 / NO WRITE`. TEST_ONLY remains isolated and
`production_activation_claimed` is false. No customer input or production activation is inferred.

## Fresh independent verification

- Exact candidate range: `6` unique paths; ledger path order matched.
- Candidate tree fingerprint: matched.
- Focused adoption contract: `2 passed, 2 warnings in 1.21s`.
- Scoped Ruff and format-check: passed.
- Coverage-ledger JSON parse and exact candidate/ledger diff checks: passed.
- Sole-ledger patch hash: matched; rows and prior stories unchanged; only Row283 pending.
- `python3 scripts/v8_lean_coverage_check.py --repo-root . --integration-sha
  c6a449f134764f57d36ecc5429cc51ba13539040 --milestone inventory`: passed.

This approval is limited to the exact candidate and reviewed sole-ledger patch. The implementer
did not approve its own work. This reviewer receipt must be committed alone before the controller
commits the ledger-only adoption.
