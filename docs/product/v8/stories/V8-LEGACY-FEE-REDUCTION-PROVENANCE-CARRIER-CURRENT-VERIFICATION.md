# Story V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Integration parent: `7ac790f`
- Outcome: prove on the current lean tree that the already-integrated D4-12 legacy
  fee-reduction provenance carrier satisfies its frozen schema, migration and append-only
  audit contract.
- Task ID: `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01`.
- Change mode: current verification only; no migration, model, schema, test or product byte
  changes.
- Authority: the frozen D4-12 task, Delta-4 contract, fee-reduction/source fail-closed
  rules, and current migration graph.

## Dependency and exact paths

The migration consumes exact parent `v8_d4_annuity_lineage_01`; the current graph then
continues through `v8_d4_legacy_fee_provenance_01` to the later accepted
`v8_d4_evidence_kind_capacity_01` head.

- `backend/app/modules/fees/models.py`
- `backend/alembic/versions/v8_delta4_legacy_fee_reduction_provenance.py`
- `backend/tests/test_v8_legacy_fee_reduction_provenance_carrier.py`

Current blobs are byte-identical to their introducing commit `83d014f` and the preserved
archive comparison source `6b2ef89`; those historical commits are provenance inputs, not
current acceptance.

## Verification

The exact focused SQLite-writing schema test passed `4/4`. It proves the frozen table
shape, application UUID identity, exact legacy-value grammar, approval nullability
invariant, unique case/manifest identity, restricted foreign keys, explicit naive
confirmation audit and immutable carrier behavior.

Scoped Ruff, task-contract check and exact-path diff check pass. An independent High
reviewer must inspect this exact story-card commit, the current product fingerprints and
migration graph, then independently rerun the focused test under the serialized SQLite
lane.

## Non-goals and rollback

No importer/backfill, approval creation or inference, customer decision, fee entitlement,
source activation, API/UI/seed change, migration rewrite, old task/evidence mutation,
coverage row or milestone claim. Rollback reverts only this story-card commit; existing
product/test bytes remain unchanged.
