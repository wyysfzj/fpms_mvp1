# V8 Inherited Regression Matrix — Current Adoption Review

Verdict: APPROVED

P0: 0
P1: 0
P2: 0

Review class: Independent High / PROTECTED
Candidate SHA: `2e32394ad356c7a743b010e75306a7b1ceba0ce1`
Candidate range: `52f1790^..2e32394ad356c7a743b010e75306a7b1ceba0ce1`
Candidate tree fingerprint:
`60fdc71fd57a665870d9fe3b170f8f4e02c6b6f96d8e97ae18ac6de25c0e261a`
Reviewed ledger diff SHA-256:
`b81f6f64af394beac9b02b9d436b61cf10c970aba75b6bc1abbd7ec35e21340d`

## Scope and matrix closure

- The reviewed story binds exactly 63 unique paths. Every one exists at the candidate SHA, all 62
  paths changed by the cumulative Row281 range are owned, and the sole unchanged owned path is the
  frozen original Row281 task.
- The matrix derives exactly 243 effective dependencies, 244 unique primary inputs and 62 unique
  regression inputs, for 306 unique declared paths. The sole missing historical Row199 test is
  replaced by the two reviewed current Full-successor contracts.
- All 21 declared primary Playwright paths are accounted for exactly once: 20 mocked paths passed
  52 tests and the official-workbook live path passed one test.
- The Tasks01–70 Playwright set is partitioned into 11 mocked paths that passed 22 tests and one
  isolated lifecycle-live path that passed one test. All seven declared Playwright regressions are
  contained in the mocked Tasks01–70 tranche.
- All 12 result lanes record exact replayable commands. Their SHA-256 values match the focused
  contract constants; no placeholder or prose-only command remains.
- The cumulative candidate contains no product, schema, migration, seed, registry or runtime-data
  change. The reviewed alignment changes add no skip or xfail and preserve the asserted permission,
  mutation, lineage, state and error boundaries.

## Ledger and configuration boundary

- The reviewed ledger patch changes only Row281 and adds only
  `V8-FULL-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION`.
- Row281 becomes `CURRENT_VERIFIED`. Rows282 and 283 are byte-identical to the candidate ledger,
  remain `PENDING`, and the post-adoption unresolved set is exactly `[282, 283]`.
- `DG-PAYMENT-WORKBOOK:GLOBAL` and `DG-SERVICE-RATE-VERSION:GLOBAL` both remain
  `CONFIG_REQUIRED`; their registry decisions remain `PENDING`.
- Missing or invalid production input remains `409 / NO WRITE`, `TEST_ONLY` remains isolated, and
  `production_activation_claimed` is false. This review makes no production, Final or Release
  activation claim.

## Fresh verification

- `cd backend && .venv/bin/pytest -q tests/test_v8_inherited_regression_matrix_contract.py` —
  5 passed.
- `cd backend && .venv/bin/ruff check tests/test_v8_inherited_regression_matrix_contract.py ../scripts/run_v8_playwright_mock_isolated.py ../scripts/run_v8_lifecycle_overlay_live_isolated.py`
  — passed.
- `python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha 2e32394ad356c7a743b010e75306a7b1ceba0ce1`
  — passed.
- Exact candidate, ledger, command-hash, tree-fingerprint, scope and diff checks — passed.

This approval is limited to the reviewed Row281 matrix capability and ledger-adoption boundary.
Rows282 and 283 retain their own independent closure requirements.
