# Story V8-LEGACY-FEE-TRUTH-LINK-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `292a1ed`
- Outcome: link legacy draft/payment history to an existing fee obligation only when
  case, source, fee and year authority identify one unambiguous obligation.
- Catalog ID: `FPMS-V8-LEGACY-FEE-TRUTH-LINK-20260712-01`
  (ordinal `256`, profile `TC-MIGRATION`).
- Authority: frozen catalog row `256`, its exact task contract, the current-verified fee
  obligation core/read/payment facts, and the fee/lineage rules in
  `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

- `backend/scripts/backfill_v8_fee_truth.py`
- `backend/tests/test_v8_legacy_fee_truth_link.py`

All catalog dependencies are current-verified. This lane shares no product/test path with
the active legacy document-evidence importer; SQLite verification remains serialized.

## Observable contract

The importer links old draft or payment history only when the same case, source, fee code
and fee year resolve exactly one existing obligation. Missing or ambiguous authority
remains unresolved and fails closed for apply. It never manufactures an obligation.
Dry-run and exact-plan apply are deterministic, and all writes remain caller-owned.

## TDD and verification

The focused RED failed `6/6` because the public importer seam was absent. Independent
review of the initial GREEN found and drove three minimum corrections: whole-plan rejection
when any row is unresolved, canonical multi-payment ordering, and one obligation-line
authority per fee item within a plan. Final focused GREEN passed `9/9`; scoped Ruff/diff
checks passed. Final independent High review approved P0/P1/P2 all zero.

## Non-goals and rollback

No obligation creation, endpoint, UI, schema, migration, adjacent fee rule, second dataset,
customer migration, old task/evidence mutation or unrelated cleanup. Rollback reverts only
product commit `f7ee133` and this story mapping.
