# Story V8-OVERLAY-CENTER-QUERY-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `260` by reading one case and one frozen lifecycle revision into
  the center snapshot and ordered activity milestones without any write.
- Catalog ID: `FPMS-V8-OVERLAY-CENTER-QUERY-20260712-01`.
- Base: `966e081c6628c45819a0cac79d80a8eb1974f137`.

## Public seam and validation

Implement the synchronous keyword-only seam:

```python
read_lifecycle_overlay(
    *,
    case_id: str,
    after_sequence: int,
    limit: int,
    as_of_revision: int | None,
    transaction: Session,
) -> LifecycleOverlay
```

Read the case first. Missing case is the existing 404 `CASE_NOT_FOUND`. Treat a fully
unmanaged legacy case whose revision and four projection carriers are all `NULL` as revision
zero. Otherwise the current revision must be persisted and non-negative. Freeze revision `R`
to that current revision when `as_of_revision is None`; otherwise require the requested
revision to be non-negative and no greater than current. Require
`after_sequence >= 0`, `after_sequence <= R`, and `limit > 0`. Invalid query shape is 400
`LIFECYCLE_OVERLAY_QUERY_INVALID`; corrupt or unreconstructable stored state is 409
`LIFECYCLE_OVERLAY_STATE_CONFLICT`.

Row 260 owns the center read and ordered dataset, not the later row-264 keyset boundary.
Therefore this story selects every activity with `after_sequence < sequence <= R`, ascending,
and returns `has_more=False` and `next_cursor=None`; it validates but does not apply `limit`.
Row 264 will add `limit + 1` pagination without changing the seam.

## Exact center reconstruction

The ledger is authoritative. For the frozen revision range, sequences must be unique,
gap-free `1..R`, and count exactly `R`. Reconstruct the center from the latest `LIFECYCLE`
activity at or before `R`: its `new_business_stage`, `new_official_procedure_stage`, and
`new_legal_status` are the snapshot axes; its confirmation status, effective time, and id are
the snapshot metadata. A later `DOCUMENT` or `FEE` activity cannot erase or replace the
center. Every stored enum value must parse through the accepted lifecycle enums.

For current `R`, the reconstructed axes and confirmation status must equal the five persisted
case carriers and persisted revision. Historical reads do not compare the historical snapshot
to today's case carriers. Revision zero is valid only with no activity and all four projection
carriers `NULL`; its center snapshot is entirely `None`.

For each milestone, only `LIFECYCLE` may change center axes. Its old/new pairs produce a
mapping containing exactly the axes whose values differ. `DOCUMENT` and `FEE` rows must have
all six old/new axis columns `NULL` and expose an empty mapping; any lane/projection violation
fails closed. Evidence links are read in deterministic identity order and projected to the
accepted `EvidenceReference` DTO. All downstream joins remain empty tuples.

Capture one timezone-naive UTC `generated_at` per invocation. The top-level decision gates,
warnings and legacy conflicts remain empty in this story. Perform no add/delete/update,
flush, commit, rollback, or clock-dependent query.

## Verification, non-goals and rollback

The focused test proves revision zero, current and historical reconstruction, mixed-lane
ordering, center changes, evidence ordering, query failures, corrupt/gapped ledgers, current
carrier mismatch, enum/lane corruption, and SQLAlchemy read-only behavior. Run focused pytest,
scoped Ruff, and exact diff check. An independent High reviewer reviews the exact product
commit/range and reruns decisive checks.

No endpoint, UI, schema/migration, document/fee/work-package/task join, decision-gate resolve,
warning aggregation, legacy-conflict projection, keyset pagination, or neighboring cleanup.
Rollback reverts only this service, focused test, and story contract.
