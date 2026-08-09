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
2. Add the nullable parent-event attestation triple `conflict_lineage_version`,
   `conflict_code_count`, and `conflict_codes_sha256`. The only complete shape is exact version
   `V1`, a non-negative integer count, and the lowercase SHA-256 of the canonical JSON array of
   the ascending stored codes; the only other valid shape is all three fields `NULL`. Partial,
   unknown-version, count/hash-mismatched or malformed attestations fail closed. This triple is
   what distinguishes a verified empty tuple from missing pre-carrier lineage.
3. `append_case_activity` writes the already-validated, sorted, duplicate-free
   `conflict_codes`, their child rows and the exact attestation in the caller-owned transaction.
   Exact replay validates the attestation against the stored ordered rows, compares that tuple
   with the supplied codes, and returns 409/no-write on drift. A failure rolls back the activity,
   evidence, conflict rows and attestation together; the service still never commits.
4. The migration is forward-only, follows current head `v8_d27_annuity_reduction_01`, and creates
   no PostgreSQL-only type or function. Repository search establishes that the accepted
   pre-carrier production paths supplied non-empty conflicts only for `LEGACY_IMPORT` and
   `PATENT_REGISTER_STATUS_CONFIRMED`; all other pre-carrier event types receive an attested empty
   tuple. An exact legacy import receives the literal ascending codes
   `LEGACY_STATUS_UNVERIFIED` and `NO_REVERSE_MAPPING_AUTHORITY` only when all of these hold:
   lifecycle lane; legacy-unverified confirmation; reserved idempotency key; source,
   supersession and reviewer are null; old axes are null; new business/official axes are null;
   new legal status is `UNKNOWN`; occurred/effective timestamps match; payload is the exact
   canonical `FPMS_V8_LEGACY_LIFECYCLE_IMPORT_V1` object for the same case and a `legacy_status`
   in the exact accepted importer set (`NOT_FILED`, `PENDING`, `GRANTED`, `REJECTED`, `WITHDRAWN`,
   `ABANDONED`, `EXPIRED`, `WAITING_RECEIPT`, `PRELIM_EXAM`, `PRELIM_PASS`, `AMENDMENT`,
   `PUBLISHED`, `SUB_EXAM`, `OA1`, `OA2`, `REEXAM`, `ACCEPTED`, `GRANT_PENDING`, `TERMINATED`,
   `INVALIDATED`); and no evidence row exists. The import must be the first lifecycle-lane event.
   Its case ledger must have contiguous sequences `1..Case.lifecycle_revision`, every event's old
   axes must equal the preceding event's new axes, and the final event's new axes must equal the
   current Case axes. Current `Case.status` must also remain inside the same accepted importer set,
   but need not equal the initial payload status; current projection and revision likewise need
   not remain at the initial imported values, because accepted later events may have advanced
   them. A near-miss `LEGACY_IMPORT` receives no child or attestation. Migration tests include an
   exact import with later valid events plus unknown payload status, known payload/unknown current
   Case status, and broken-ledger near misses.
5. Pre-carrier `PATENT_REGISTER_STATUS_CONFIRMED` rows receive no inferred child or attestation.
   Reading or replaying one returns exact 409 code `LIFECYCLE_CONFLICT_LINEAGE_MISSING` without a
   write, because the previously transient tuple cannot be reconstructed safely. New
   patent-register replay validates the stored attestation/tuple first and then independently
   recomputes the pure rule decision; both tuples must match. No conflict may be dropped merely
   to preserve replay compatibility. Migration tests cover exact backfill, each material legacy
   near-miss, attested empty rows, and the pre-carrier patent-register 409.

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
     `CUSTOMER_DECISION_GATE`, and source ID equal to the exact composite
     `gate_code:requested_scope_key:resolved_gate_id`, so distinct requested form scopes remain
     distinguishable even when they resolve through the same `ALL-22` carrier.
   `CURRENT_OFFICIAL` creates no reference-only warning and this story exposes no activation
   control.
6. `legacy_conflicts` contains only stored conflict rows whose activity is the exact
   `LEGACY_IMPORT`/`LEGACY_UNVERIFIED` shape. Preserve page activity order then ascending code;
   each item keeps the exact code and activity ID with
   `message=历史生命周期活动存在待核对冲突`. Other activity conflicts remain warnings and are
   not relabelled as legacy conflicts.
7. Missing, partial, hash/count-mismatched, duplicate, cross-case or overlong conflict lineage
   fails closed. Pagination changes
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
- affected lifecycle append/register replay, legacy-import and overlay regression modules may
  receive only the mechanical fixture attestation fields or assertions required by this carrier;
  they may not change their pre-existing product expectations.

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
