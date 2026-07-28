# Story V8-FEE-FOUNDATION-CONTRACTS-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the frozen fee-reduction validator and fee
  obligation public contracts satisfy their exact catalog closures, with all four
  product/test blobs unchanged from archive commit `6b2ef89`.
- Change mode: current verification only; no product, test, ledger or review byte changes.
- Authority: the official-fee, reduction, source and provenance rules in
  `docs/product/v8/domain-contract.md`; the source-precedence and fail-closed decision gates
  in `docs/product/v8/source-decision-registry.md`; and the two frozen catalog task
  contracts.
- Dependencies: the F1-F5 carriers are current-verified through
  `V8-CANARY-SCHEMA-SPINE-CURRENT-VERIFICATION`. Catalog ordinal 93 depends on F5; catalog
  ordinal 102 depends on F1-F5.

## Catalog IDs

1. `FPMS-V8-FEE-REDUCTION-VALIDATOR-20260712-01` (ordinal 93)
2. `FPMS-V8-FO-CONTRACTS-20260712-01` (ordinal 102)

## Exact source and test paths

- `backend/app/modules/fees/fee_reduction.py`
- `backend/tests/test_v8_fee_reduction_validator.py`
- `backend/app/modules/fees/obligation_contracts.py`
- `backend/tests/test_v8_fee_obligation_contracts.py`

## Verification

From this worktree's `backend` directory, run:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_fee_reduction_validator.py tests/test_v8_fee_obligation_contracts.py
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/ruff check app/modules/fees/fee_reduction.py tests/test_v8_fee_reduction_validator.py app/modules/fees/obligation_contracts.py tests/test_v8_fee_obligation_contracts.py
```

Also prove all four source/test blobs are identical to archive commit `6b2ef89`, run exact
diff-check, and have an independent High reviewer rerun the same decisive checks on the
exact story commit.

## Non-goals and rollback

No new fee policy, source activation, persistence adapter, service behavior, endpoint,
seed, schema/migration, UI, old taskctl/evidence mutation or Foundation claim. Rollback
removes only this story record and its later coverage-ledger mapping; the accepted
product/test bytes remain unchanged.
