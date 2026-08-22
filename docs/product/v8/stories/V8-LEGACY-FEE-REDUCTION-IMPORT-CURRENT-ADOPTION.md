# Story V8-LEGACY-FEE-REDUCTION-IMPORT-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `b22e5ea`
- Outcome: import only customer-approved legacy fee-reduction truth through one
  deterministic, caller-owned dry-run/apply seam.
- Catalog ID: `FPMS-V8-LEGACY-FEE-REDUCTION-IMPORT-20260712-01` (ordinal `255`,
  profile `TC-MIGRATION`).
- Authority: frozen catalog row `255`, its exact task contract, the accepted D4-12
  provenance carrier, and the fee/source rules in `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

The provenance carrier is current-verified by
`V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-CURRENT-VERIFICATION`.

- `backend/scripts/backfill_v8_fee_reduction.py`
- `backend/tests/test_v8_legacy_fee_reduction_import.py`

## Observable contract

The public importer accepts only an approved, actor-bound manifest and byte-exact legacy
values `0`, `0.7`, or `0.85`. Its dry run is write-free, case-ordered and deterministic,
including all classifications, counts, and input/plan/output hashes. Apply requires the
exact dry-run plan hash and remains wholly inside the caller-owned transaction.

Explicit zero imports without approval. A nonzero value reuses exactly one fully matching
confirmed current-evidence approval and never creates approval authority. Successful apply
updates only the case fee-reduction projection and immutable provenance. Exact replay is
unchanged; changed facts for the same provenance identity fail `409`.

## TDD and verification

The focused RED proved the importer seam was absent. During GREEN, the test exposed and
corrected a real SQLite transaction-ownership defect caused by an internal savepoint.
The final focused run passed `14/14`; scoped Ruff format/check and diff checks passed.

Independent High review inspected the exact two candidate files and their hashes without
repeating SQLite verification. It approved the manifest authority, grammar, deterministic
plan, transaction ownership, approval matching, immutable provenance, replay and
non-closure with P0/P1/P2 all zero.

## Non-goals and rollback

No customer migration was executed. No approval was created, no schema/API/UI/task or old
evidence machinery changed, and no adjacent import abstraction was added. Rollback reverts
only product commit `897eee8`.
