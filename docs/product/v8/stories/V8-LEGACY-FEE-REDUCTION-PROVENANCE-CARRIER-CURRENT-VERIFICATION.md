# Story V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Integration parent: `7ac790f`
- Outcome: prove on the current lean tree that the already-integrated D4-12 legacy
  fee-reduction provenance carrier satisfies its frozen schema, migration and append-only
  audit contract.
- Task ID: `FPMS-V8-LEGACY-FEE-REDUCTION-PROVENANCE-CARRIER-20260715-01`.
- Change mode: current verification followed by the minimum independently found database
  no-coercion correction; no importer or adjacent schema change.
- Authority: the frozen D4-12 task, Delta-4 contract, fee-reduction/source fail-closed
  rules, and current migration graph.

## Dependency and exact paths

The migration consumes exact parent `v8_d4_annuity_lineage_01`; the current graph then
continues through `v8_d4_legacy_fee_provenance_01` to the later accepted
`v8_d4_evidence_kind_capacity_01` head.

- `backend/app/modules/fees/models.py`
- `backend/alembic/versions/v8_delta4_legacy_fee_reduction_provenance.py`
- `backend/tests/test_v8_legacy_fee_reduction_provenance_carrier.py`

Before the P1 correction, all three product/test blobs were byte-identical to their
introducing commit `83d014f` and preserved archive comparison source `6b2ef89`. Those old
blobs remain pre-correction provenance inputs, not current acceptance. Correction commit
`5d60e88` intentionally changes the model, migration and focused test; their corrected Git
blob IDs are respectively `25428b6`, `f5e3554` and `5922dc3`.

## Verification

The first independent review found one P1: SQLite TEXT affinity converted raw numeric
inputs to text before the existing value check, so the test proved ORM rejection but not
the frozen database-boundary no-coercion rule. The correction RED failed exactly on
`VARCHAR` storage and an accepted raw numeric insert.

The minimum correction keeps the ORM surface a Python/SQLAlchemy string while compiling
only `legacy_value` with SQLite BLOB/no-coercion affinity, and requires both
`typeof(legacy_value) = 'text'` and the exact `0/0.7/0.85` grammar in ORM and migration
DDL. The focused SQLite-writing schema test then passed `4/4`, including raw numeric
rejection and persisted string identity. It also proves the frozen table shape,
application UUID identity, approval nullability invariant, unique case/manifest identity,
restricted foreign keys, explicit naive confirmation audit and immutable carrier
behavior.

Scoped Ruff, task-contract check and exact-path diff check pass. An independent High
reviewer must inspect the exact corrected commit/range, current product fingerprints and
migration graph, then independently rerun the focused test under the serialized SQLite
lane.

## Non-goals and rollback

No importer/backfill, approval creation or inference, customer decision, fee entitlement,
source activation, API/UI/seed change, unrelated migration rewrite, old task/evidence
mutation, coverage row or milestone claim. Rollback reverts the exact correction commit's
four paths: model, D4-12 migration, focused test and this story card.
