# V8 Input Activation Capabilities — Current Adoption Review

Verdict: APPROVED

P0: 0
P1: 0
P2: 0

Review class: Independent High / PROTECTED
Candidate SHA: `11b0161541eb3811dd033e73caed442d31278cb8`
Reviewed scope: the exact input-capability ledger-adoption candidate through the candidate SHA,
plus the sole metadata diff in `docs/product/v8/coverage-ledger.json`.

## Scope and identity

- Exactly catalog rows 175, 176, 214–229 and 278 resolve to
  `V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION`; the adopted set contains 19 rows.
- Row199 and terminal Rows281, 282 and 283 remain outside this adoption.
- The story contains 63 unique paths and binds candidate tree fingerprint
  `866a7d1dd1b8315922eede284b810da7d46591d5ff040c7559e141ab003b4bfc`.
- The fingerprint covers every path changed by accepted commits `090b4b7`, `d2810c3`,
  `2280839`, `6a17a18`, `97771c2`, `a8219b7` and the reviewed checker/adoption range.
- Integrated-owner validation excludes only the mutable coverage-ledger metadata path; product,
  successor-task and terminal-task drift remains fail closed.

## Capability and configuration boundary

The adopted implementation is `CAPABILITY_READY`, while production remains
`CONFIG_REQUIRED` for both `DG-PAYMENT-WORKBOOK:GLOBAL` and
`DG-SERVICE-RATE-VERSION:GLOBAL`. Both source-decision registry gates remain `PENDING`.
Missing or invalid production input remains `409 / NO WRITE`, and `TEST_ONLY` inputs remain
isolated from production. This review makes no production activation claim.

## Fresh verification

- `python3 -m pytest -q scripts/tests/test_v8_lean_coverage_check.py scripts/tests/test_v8_input_activation_capability_ledger_adoption.py` — 37 passed.
- `python3 -m ruff check scripts/v8_lean_coverage_check.py scripts/tests/test_v8_lean_coverage_check.py scripts/tests/test_v8_input_activation_capability_ledger_adoption.py` — passed.
- `python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha 11b0161541eb3811dd033e73caed442d31278cb8` — passed.
- Exact receipt, ledger and candidate diff checks — passed.

The independent review found no unresolved P0, P1 or P2 issue. It approves only the reviewed
capability and ledger metadata boundary, not a real production input, positive production gate,
Full, Final or Release.
