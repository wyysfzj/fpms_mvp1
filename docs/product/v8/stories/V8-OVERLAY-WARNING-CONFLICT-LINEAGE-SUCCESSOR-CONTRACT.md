# Story Contract — V8 Overlay Warning and Conflict Lineage Successor

- Risk: `PROTECTED`.
- Trigger: Row275 requires a real unverified fact, legacy conflict and reference-only warning,
  while the accepted overlay currently returns empty warning/conflict tuples and activity
  `conflict_codes` are transient.
- Outcome: persist exact lifecycle activity conflict codes and project source-backed activity,
  conflict and decision-gate warnings through the real lifecycle overlay without changing legal,
  fee, gate or lifecycle state.
- Successor effect: this story is a prerequisite of
  `FPMS-V8-LIVE-FIXTURE-20260712-01`; it does not itself adopt Row275 or Row276.
- Authority: `docs/product/v8/domain-contract.md`, the accepted lifecycle append/overlay contracts,
  the accepted decision-gate join, and
  `docs/product/v8/reviews/V8-FOUNDATION-EXECUTABLE-BOUNDARY-AUDIT-20260809.md`.

## Durable activity conflict carrier

1. Add `t_case_activity_event_conflict` with exact composite primary key
   `(activity_id, code)`, required `case_id`, and a same-case composite foreign key
   `(case_id, activity_id)` to `t_case_activity_event(case_id, id)` with `ON DELETE CASCADE`.
   `code` is a non-empty string of at most 128 characters. No message, legal conclusion or
   mutable case snapshot is stored in this carrier.
2. `append_case_activity` writes the already-validated, sorted, duplicate-free
   `conflict_codes` in the caller-owned transaction. Exact replay compares the stored ordered
   codes with the supplied codes and returns 409/no-write on drift. A failure rolls back the
   activity, evidence and conflict rows together; the service still never commits.
3. The migration is forward-only, follows current head `v8_d27_annuity_reduction_01`, and creates
   no PostgreSQL-only type or function. It backfills only the two already-frozen conflict codes
   for an exact historical importer identity:
   `activity_type=LEGACY_IMPORT`, `confirmation_status=LEGACY_UNVERIFIED`, and
   `idempotency_key='v8-legacy-lifecycle-import:' || case_id`. It does not reconstruct any other
   previously transient conflict.
4. Existing patent-register replay first validates against the stored conflict tuple and then
   independently recomputes the pure rule decision; both tuples must match. No conflict may be
   dropped merely to preserve replay compatibility.

## Exact read-only warning projection

For each accepted overlay page, process milestones in ascending server sequence order.

1. A milestone with `NEEDS_REVIEW` receives one local warning:
   `kind=UNVERIFIED`, `code=LIFECYCLE_ACTIVITY_NEEDS_REVIEW`,
   `message=该生命周期活动尚待复核`.
2. A milestone with `LEGACY_UNVERIFIED` receives one local warning:
   `kind=UNVERIFIED`, `code=LEGACY_ACTIVITY_UNVERIFIED`,
   `message=该历史生命周期活动尚未核验`.
3. Each stored activity conflict code then receives one local warning in ascending code order:
   `kind=CONFLICT`, the exact stored code, and
   `message=生命周期活动存在待核对冲突`.
4. Every activity warning uses `activity_id` equal to the exact event ID,
   `source_object_type=CASE_ACTIVITY_EVENT`, and `source_object_id` equal to that event ID.
   `CONFIRMED` without stored conflicts has no local warning.
5. Top-level warnings first flatten all current-page milestone warnings without deduplication.
   They then append decision-gate warnings in the accepted 29-entry gate order:
   - each `UNRESOLVED` gate yields `kind=CUSTOMER_DECISION_GATE`, exact unresolved-reason code,
     `message=客户决策门禁尚未解析`, no activity ID, source type
     `CUSTOMER_DECISION_GATE`, and source ID equal to its exact composite
     `gate_code:requested_scope_key`;
   - each resolved `HISTORICAL` or `INTERNAL_ONLY` gate yields
     `kind=REFERENCE_ONLY`, `code=DECISION_GATE_REFERENCE_ONLY`,
     `message=该客户决策分类仅供参考，不得激活`, no activity ID, source type
     `CUSTOMER_DECISION_GATE`, and source ID equal to the resolved gate ID.
   `CURRENT_OFFICIAL` creates no reference-only warning and this story exposes no activation
   control.
6. `legacy_conflicts` contains only stored conflict rows whose activity is the exact
   `LEGACY_IMPORT`/`LEGACY_UNVERIFIED` shape. Preserve page activity order then ascending code;
   each item keeps the exact code and activity ID with
   `message=历史生命周期活动存在待核对冲突`. Other activity conflicts remain warnings and are
   not relabelled as legacy conflicts.
7. Missing, duplicate, cross-case or overlong conflict lineage fails closed. Pagination changes
   only the page-local activity part; the full decision-gate warning suffix is rebuilt from each
   complete gate snapshot. The projection performs no write and does not infer center state.

## Exact paths and targeted verification

- `docs/product/v8/domain-contract.md`
- this contract
- `backend/alembic/versions/v8_delta31_overlay_warning_conflict_lineage.py`
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/lifecycle_activity_service.py`
- `backend/app/modules/cases/lifecycle_service.py`
- `backend/app/modules/cases/lifecycle_overlay_service.py`
- `backend/tests/test_v8_overlay_warning_conflict_lineage.py`
- `backend/tests/test_v8_overlay_warning_conflict_migration.py`

Required RED proves the missing carrier and empty overlay projection. GREEN proves atomic append and
exact replay, strict same-case storage, migration upgrade/backfill, exact warning ordering and
provenance, legacy-only conflict projection, 29-gate isolation, page-local aggregation and zero
write behavior. Run the two focused test modules, affected lifecycle append/register replay,
legacy-import and overlay decision-gate regressions, scoped Ruff, migration-head verification and
exact-path diff checks. SQLite-writing checks and migration verification are serialized.

## Non-goals and rollback

No customer decision, legal/lifecycle transition, center-state calculation, fee behavior, gate
activation, API/UI change, Row275 fixture, Row276 E2E, broad historical conflict reconstruction,
payload-key convention, unrelated schema cleanup or repo-wide verification. Rollback reverts the
story before production migration; the migration itself is forward-only. Reverting runtime code
after migration leaves inert conflict rows and returns Row275/276 to authority-blocked.
