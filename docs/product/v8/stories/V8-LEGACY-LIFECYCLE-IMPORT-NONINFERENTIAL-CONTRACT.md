# Contract — V8 Legacy Lifecycle Import Without Reverse Inference

- Risk: `PROTECTED`
- Catalog ID: `FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01` (ordinal `253`).
- Outcome: import only the deterministic fact that a legacy case/status exists, without
  reverse-mapping that mixed status into a business stage, official stage or confirmed
  legal status.
- Authority: V8 design §§7.3 and 11.4, the accepted lifecycle activity seam and the current
  legacy-state preflight. The one-way three-axis-to-legacy projection remains one-way.

## Exact public contract

`backend/scripts/backfill_v8_lifecycle.py` exposes frozen keyword-only synchronous
`import_legacy_lifecycle(transaction, actor_id, recorded_at, dry_run,
expected_plan_sha256=None)` and frozen result DTOs. It returns ordered row classifications,
counts and deterministic input/plan/output SHA-256 values. `recorded_at` is an explicit
timezone-naive migration fact; the function never reads the wall clock.

Dry-run performs no write. Apply requires the exact dry-run plan hash, uses one nested
savepoint, performs no commit or outer rollback, and delegates every write to
`append_case_activity`. Caller rollback removes all imports. Exact rerun is unchanged;
source or plan drift fails closed.

## Eligible import and exact projection

An `IMPORT` row requires an exact known `CaseStatus`, exact case ID/status/revision, all four
current lifecycle projection columns null, no pre-existing lifecycle activity and no
conflicting reserved idempotency key. It appends exactly one activity with:

- event/lane/confirmation: `LEGACY_IMPORT / LIFECYCLE / LEGACY_UNVERIFIED`;
- previous projection: all null;
- current projection: business stage null, official stage null,
  `legal_status=UNKNOWN`, `lifecycle_verification_status=LEGACY_UNVERIFIED`;
- unchanged compatibility `Case.status`;
- no evidence, reviewer, source or superseded activity;
- deterministic key `v8-legacy-lifecycle-import:{case_id}`;
- exact canonical payload containing only schema, case ID, original legacy status and
  `reverse_mapping="NONE"`;
- sorted conflict codes `LEGACY_STATUS_UNVERIFIED` and `NO_REVERSE_MAPPING_AUTHORITY`.

This is the sole non-inferential interpretation of the approved migration rule. In
particular, legacy `GRANTED` remains the compatibility string only; legal status becomes
`UNKNOWN`, never `PATENT_IN_FORCE`. The same applies to every other legacy status: no old
string becomes a confirmed legal or official fact.

An exact existing import is `UNCHANGED`. Malformed IDs/status/revision are `INVALID`.
Partial/non-null projections, any prior lifecycle history, reserved-key drift, malformed
stored import or projection/history inconsistency are `CONFLICT`. Only `IMPORT` rows are
written; other rows remain untouched and visible in the report.

## Scope, verification and non-goals

- `backend/scripts/backfill_v8_lifecycle.py`
- `backend/tests/test_v8_legacy_lifecycle_import.py`
- this contract and later adoption/review records

Verification covers the exact public seam, dry-run determinism, all status values including
`GRANTED`, apply/replay/caller rollback, plan drift, partial/current projections, prior
history, malformed carrier state, actor/time validation, deep-writer delegation and no
direct Case/activity writes outside that seam. SQLite verification is serialized.

No reverse mapping table, confirmed lifecycle/legal fact, evidence fabrication, schema,
endpoint/UI, source file edit, existing activity rewrite, bulk commit, customer policy or
adjacent cleanup is included. Rollback reverts only this importer story; imported rows are
forward-only database history and are not deleted by a later migration.
