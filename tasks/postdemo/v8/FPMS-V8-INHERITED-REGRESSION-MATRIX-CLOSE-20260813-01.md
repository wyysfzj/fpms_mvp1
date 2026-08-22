# FPMS V8 Inherited Regression Matrix Close

Status: `IMPLEMENTATION`
Risk: `PROTECTED`
Runbook: `P0-prereq-heavy-story`

## Observable outcome

Execute and bind the exact current Full inherited regression matrix for catalog Row281 after
Row199 and Row278 are current. The matrix is derived from Row281's frozen direct dependencies plus
the independently approved Row278 terminal overlay. Every declared backend, frontend and
Playwright input is accounted for exactly once, and failures produce follow-up work rather than
product changes inside this close.

The result may close Row281 only. It does not activate either production input: payment workbook
and service price remain `CONFIG_REQUIRED`, their registry decisions remain `PENDING`, production
actions remain `409 / NO WRITE`, and TEST_ONLY remains isolated.

## Preconditions

- Row199 is current through `V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION`.
- Row278 is current through `V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION`.
- The unresolved ledger set is exactly Rows281, 282 and 283.
- The frozen catalog remains exactly 283 rows with its recorded SHA-256.

## Exact closure

1. Freeze the ordered 243 effective dependency identities: Row281's 242 frozen dependencies plus
   the reviewed Row278 terminal overlay.
2. Derive the unique declared `primary_tests` and `regression_inputs` from those identities and
   classify them as backend, frontend or Playwright inputs.
3. Replace only the absent historical Row199 primary test with the two reviewed current Full
   successor contract tests; reject every other missing input.
4. Run the exact backend pytest tranche, current Full successor contract tranche, frontend
   typecheck and executable contracts, and exact Playwright tranche under serialized ownership.
5. Record the exact commands, return codes, counts and controlled skips without changing product
   code or weakening assertions.
6. After independent High review, adopt only Row281; leave Rows282 and 283 pending.

## Non-closure

- No product, schema, migration, seed, source-decision registry or runtime-data change.
- No test assertion weakening and no product fix inside this story; each failure becomes a
  separate exact task.
- No Row282 item-to-slice ledger, Row283 Final close, release gate or production activation.
- No historical taskctl/evidence machinery.
- Do not fingerprint the mutable coverage ledger or reviewer-owned review receipt.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-INHERITED-REGRESSION-MATRIX-CLOSE-20260813-01.md`
- `backend/tests/test_v8_inherited_regression_matrix_contract.py`
- `scripts/run_v8_playwright_mock_isolated.py`
- `scripts/run_v8_lifecycle_overlay_live_isolated.py`
- `docs/product/v8/inherited-regression-matrix.json`
- `docs/product/v8/stories/V8-INHERITED-REGRESSION-MATRIX-CLOSE.md`
- `docs/product/v8/reviews/V8-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION.md`
- `docs/product/v8/coverage-ledger.json`

The story fingerprint may bind the frozen Row281 task, catalog, current Full successor tests and
the exact derived read-only test inputs without editing them. `backend/uv.lock` remains unrelated
and untouched.

## Verification and acceptance

The durable matrix file freezes the exact commands after deriving the path sets. Required lanes
are serialized. The task-level gates are:

```text
cd backend && .venv/bin/pytest -q tests/test_v8_inherited_regression_matrix_contract.py
cd backend && .venv/bin/ruff check tests/test_v8_inherited_regression_matrix_contract.py
cd frontend && npm run typecheck
python3 -m pytest -q scripts/tests/test_v8_full_config_required_successor.py scripts/tests/test_v8_full_capability_manifest_close.py
python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha <candidate-sha>
git diff --check -- <exact allowlist>
```

The candidate requires independent High review with P0/P1/P2 `0/0/0`. Rollback reverts only this
story metadata and the Row281 ledger adoption; it never changes production configuration or
business data.
